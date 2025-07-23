# app.py
import base64
import logging
import multiprocessing
import os
import re
import ssl
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO, StringIO
from pathlib import Path
import json
from cross_ref import build_full_record
# time http calls
from time import time
from typing import Any, Optional
from urllib.request import urlopen
import unicodedata

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile, Query, HTTPException

# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import PROV, RDF, RDFS, XSD
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
from starlette_wtf import CSRFProtectMiddleware, StarletteForm, csrf_protect
from wtforms import FileField, URLField

import settings
from pdfextract import PDFExtract, load_models

setting = settings.Setting()

default_extract_dir = Path.cwd() / "extract"

# Global variable to cache the resource
cached_models = {}


def add_prov(graph: Graph, api_url: str, data_url: str) -> Graph:
    """Add prov-o information to output graph

    Args:
        graph (Graph): Graph to add prov information to
        api_url (str): the api url
        data_url (str): the url to the rdf file that was used

    Returns:
        Graph: Input Graph with prov metadata of the api call
    """
    graph.bind("prov", PROV)

    root = BNode()
    api_node = URIRef(api_url)
    graph.add((root, PROV.wasGeneratedBy, api_node))
    graph.add((api_node, RDF.type, PROV.Activity))
    software_node = URIRef(setting.source + "/releases/tag/" + setting.version)
    graph.add((api_node, PROV.wasAssociatedWith, software_node))
    graph.add((software_node, RDF.type, PROV.SoftwareAgent))
    graph.add((software_node, RDFS.label, Literal(setting.name + setting.version)))
    graph.add((software_node, PROV.hadPrimarySource, URIRef(setting.source)))
    graph.add(
        (
            root,
            PROV.generatedAtTime,
            Literal(str(datetime.now().isoformat()), datatype=XSD.dateTime),
        )
    )
    entity = URIRef(str(data_url))
    graph.add((entity, RDF.type, PROV.Entity))
    derivation = BNode()
    graph.add((derivation, RDF.type, PROV.Derivation))
    graph.add((derivation, PROV.entity, entity))
    graph.add((derivation, PROV.hadActivity, api_node))
    graph.add((root, PROV.qualifiedDerivation, derivation))
    graph.add((root, PROV.wasDerivedFrom, entity))

    return graph


# flash integration flike flask flash
def flash(request: Request, message: Any, category: str = "info") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})


def get_flashed_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []


middleware = [
    Middleware(
        SessionMiddleware, secret_key=os.environ.get("APP_SECRET", "changemeNOW")
    ),
    Middleware(
        CSRFProtectMiddleware, csrf_secret=os.environ.get("APP_SECRET", "changemeNOW")
    ),
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    ),
    Middleware(
        uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware, trusted_hosts="*"
    ),
]

tags_metadata = [
    {
        "name": "transform",
        "description": "transforms data to other format",
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    """
    try:
        print("Preloading models during lifespan startup...")
        cached_models.update(load_models())
        print("Lifespan startup complete: models loaded!")
        yield  # Keep the app running until shutdown
    except Exception as e:
        print(f"Error during lifespan startup: {e}")
        raise  # Re-raise exception to prevent silent failures
    finally:
        print("Lifespan shutdown: cleaning up resources...")


app = FastAPI(
    title=setting.name,
    description=setting.desc,
    version=setting.version,
    contact={
        "name": setting.contact_name,
        "url": setting.org_site,
        "email": setting.admin_email,
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_url=setting.openapi_url,
    openapi_tags=tags_metadata,
    docs_url=setting.docs_url,
    redoc_url=None,
    swagger_ui_parameters={"syntaxHighlight": False},
    # swagger_favicon_url="/static/resources/favicon.svg",
    middleware=middleware,
    lifespan=lifespan,
)


app.mount("/static/", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals["get_flashed_messages"] = get_flashed_messages

logging.basicConfig(level=logging.DEBUG)


def replace_non_latin1(s: str) -> str:
    # Normalize and remove characters not supported by Latin-1
    normalized = unicodedata.normalize("NFKD", s)
    ascii_string = normalized.encode("latin-1", "ignore").decode("latin-1")
    return ascii_string

def sanitize_headers(headers: dict) -> dict:
    sanitized = {}
    for k, v in headers.items():
        try:
            # Ensure keys and values are strings
            k_str = str(k)
            v_str = str(v)

            # Replace non-latin-1 characters
            clean_k = replace_non_latin1(k_str)
            clean_v = replace_non_latin1(v_str)

            sanitized[clean_k] = clean_v
        except Exception as e:
            logging.debug(f"Skipping header due to error: {k}: {v} ({e})")
    return sanitized

class StartFormUri(StarletteForm):
    data_url = URLField(
        "URL Document File",
        # validators=[DataRequired()],
        description="Paste a URL to a document file.",
        # validators=[DataRequired(message='Either URL to data file or file upload is required.')],
        render_kw={
            "class": "form-control",
            "placeholder": "https://css4.pub/2015/textbook/somatosensory.pdf",
        },
    )
    file = FileField(
        "Upload File",
        description="Upload your Document File here.",
        render_kw={"class": "form-control", "placeholder": "Your File"},
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@csrf_protect
async def get_index(request: Request):
    """GET /: form handler"""
    template = "index.html"
    form = await StartFormUri.from_formdata(request)
    return templates.TemplateResponse(
        template, {"request": request, "form": form, "result": "", "setting": setting}
    )


def download_file(url: str) -> UploadFile:
    ctx = ssl.create_default_context()
    app_mode = os.environ.get("APP_MODE") or "production"
    if app_mode == "development":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    with urlopen(url, context=ctx) as response:
        file_bytes = BytesIO(response.read())
        if "Content-Disposition" in response.headers:
            header = response.getheader("Content-Disposition")
            match = re.search("filename=([^;\n]+)", header)
            filename = match.group(1) if match else None
        else:
            filename = url.rsplit("/", 1)[-1]
        if not filename:
            filename = "file.pdf"
    return filename, file_bytes


@app.post("/", response_class=HTMLResponse, include_in_schema=False)
@csrf_protect
async def post_index(request: Request):
    """POST /: form handler"""
    template = "index.html"
    form = await StartFormUri.from_formdata(request)
    result = ""
    filename = ""
    payload = ""
    if not (form.data_url.data or form.file.data.filename):
        msg = "URL Data File empty: using placeholder value for demonstration."
        logging.debug("URL Data File empty: using placeholder value for demonstration.")
        form.data_url.data = form.data_url.render_kw["placeholder"]
        flash(request, msg, "info")
    if await form.validate_on_submit():
        if form.file.data.filename:
            upload_file = UploadFile(
                filename=form.file.data.filename, file=form.file.data.file
            )
            result = await extract(request=request, file=upload_file)
        elif form.data_url.data:
            data_url = form.data_url.data
            filename, file_bytes = download_file(data_url)
            prefix, suffix = filename.rsplit(".", 1)
            with tempfile.NamedTemporaryFile(
                prefix=prefix, suffix="." + suffix
            ) as temp_file:
                temp_file.write(file_bytes.getvalue())
                temp_file.seek(0)
                upload_file = UploadFile(filename=filename, file=temp_file)
                result = await extract(request=request, file=upload_file)

        # Create a BytesIO object to hold the contents of the response
        file_buffer = BytesIO()
        async for chunk in result.body_iterator:
            file_buffer.write(chunk)
        file_buffer.seek(0)
        b64 = base64.b64encode(file_buffer.getvalue())
        payload = b64.decode()
        header = result.headers.get("Content-Disposition")
        match = re.search("filename=([^;\n]+)", header)
        filename = match.group(1) if match else "file.zip"
    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "form": form,
            "result": result,
            "filename": filename,
            "payload": payload,
            "setting": setting,
        },
    )


@app.post("/api/extract", tags=["extract transform"])
async def extract(
    request: Request,
    file: UploadFile = File(...),
) -> StreamingResponse:
    """Converts a document file on the web to the specified serializatio format.

    Args:
        request (Request): general request

    Raises:
        HTTPException: Error description

    Returns:
        StreamingResponse: Zip Output File as Streaming Response
    """
    # models = get_cached_models()  # Directly call the caching function
    doc_path = default_extract_dir / file.filename
    with open(default_extract_dir / file.filename, "wb") as f:
        f.write(await file.read())
    global loaded_models
    extractor = PDFExtract(doc_path=doc_path, models=cached_models)
    extractor.extract_text()
    app_mode = os.environ.get("APP_MODE") or "production"
    if app_mode == "development":
        delete_files = False
    else:
        delete_files = True
    zip_file_buffer = extractor.zip_results(delete_files=delete_files)
    zip_name = extractor.outname
    del extractor
    headers = {
        "Content-Disposition": "attachment; filename={}".format(zip_name + ".zip"),
        "Access-Control-Expose-Headers": "Content-Disposition",
    }
    media_type = "application/zip"
    response = StreamingResponse(
        iter([zip_file_buffer.getvalue()]),
        media_type=media_type,
        headers=sanitize_headers(headers)
    )

    return response

@app.post("/api/extract", tags=["extract transform"])
async def extract(
    request: Request,
    file: UploadFile = File(...),
) -> StreamingResponse:
    """Converts a document file on the web to the specified serializatio format.

    Args:
        request (Request): general request

    Raises:
        HTTPException: Error description

    Returns:
        StreamingResponse: Zip Output File as Streaming Response
    """
    # models = get_cached_models()  # Directly call the caching function
    doc_path = default_extract_dir / file.filename
    with open(default_extract_dir / file.filename, "wb") as f:
        f.write(await file.read())
    global loaded_models
    extractor = PDFExtract(doc_path=doc_path, models=cached_models)
    extractor.extract_text()
    app_mode = os.environ.get("APP_MODE") or "production"
    if app_mode == "development":
        delete_files = False
    else:
        delete_files = True
    zip_file_buffer = extractor.zip_results(delete_files=delete_files)
    zip_name = extractor.outname
    del extractor
    headers = {
        "Content-Disposition": "attachment; filename={}".format(zip_name + ".zip"),
        "Access-Control-Expose-Headers": "Content-Disposition",
    }
    media_type = "application/json"
    response = StreamingResponse(
        iter([zip_file_buffer.getvalue()]), media_type=media_type, headers=headers
    )

    return response

@app.get("/api/crossref")
async def get_crossref(
    query: Optional[str] = Query(None, description="A string query parameter."),
    doi_url: Optional[str] = Query(None, description="An DOI URL."),
    max_depth: Optional[int] = Query(0, description="The recursive depth of citations to follow")
):
    """
    Get crossref metadata for a string to query (best use title) or a doi link.

    - **query**: A required string parameter used for processing.
    - **doi_url**: An optional DOI URL for additional context (if provided).
    
    Returns a streamed JSON response.
    """
    if not query and not doi_url:
        raise HTTPException(status_code=400, detail="Either 'query' or 'doi_url' must be set.")
    if doi_url:
        final_data_of_paper = build_full_record(doi=doi_url, max_depth=max_depth)
    else:
        final_data_of_paper = build_full_record(query=query, max_depth=max_depth)
    response_data = json.dumps(final_data_of_paper, indent=4)
    
    # Create a stream from the response data
    response_stream = StringIO(response_data)
    
    return StreamingResponse(response_stream, media_type="application/json")

@app.get("/info", response_model=settings.Setting)
async def info() -> dict:
    """App Information

    Returns:
        dict: Provinance information of the App.
    """
    return setting


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    print("Preloading models in the main process...")
    cached_models.update(load_models())
    print("Models preloaded successfully!")
    port = int(os.environ.get("PORT", 5000))
    app_mode = os.environ.get("APP_MODE") or "production"
    if app_mode == "development":
        log_level = "debug"
        reload = True
        access_log = True
        host = "0.0.0.0"
    else:
        log_level = "info"
        reload = False
        access_log = False
        host = None
        # "--workers", "1", "--proxy-headers"
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        access_log=access_log,
        log_level=log_level,
    )
