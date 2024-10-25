# app.py
import os, re
import base64
from urllib.parse import urlparse
from urllib.request import urlopen

from datetime import datetime
import logging
from io import BytesIO

import uvicorn

from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
from wtforms import URLField, SelectField, FileField

# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException, FastAPI
from fastapi.responses import StreamingResponse
from fastapi import UploadFile, File


from typing import Optional, Any, Union
from pydantic import BaseModel, AnyUrl, Field, FileUrl

from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import PROV, RDF, RDFS, XSD
from rdflib.util import guess_format

import settings

setting = settings.Setting()

from enum import Enum

from pdfextract import PDFExtract
from pathlib import Path

default_extract_dir = Path.cwd() / "extract"


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
)


app.mount("/static/", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals["get_flashed_messages"] = get_flashed_messages

logging.basicConfig(level=logging.DEBUG)


class StartFormUri(StarletteForm):
    data_url = URLField(
        "URL PDF File",
        # validators=[DataRequired()],
        description="Paste a URL to a pdf file.",
        # validators=[DataRequired(message='Either URL to data file or file upload is required.')],
        render_kw={
            "class": "form-control",
            "placeholder": "https://css4.pub/2015/textbook/somatosensory.pdf",
        },
    )
    file = FileField(
        "Upload File",
        description="Upload your PDF File here.",
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
    with urlopen(url) as response:
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


import tempfile


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
async def extract(request: Request, file: UploadFile = File(...)) -> StreamingResponse:
    """Converts a rdf file on the web to the specified serializatio format.

    Args:
        request (Request): general request

    Raises:
        HTTPException: Error description

    Returns:
        StreamingResponse: RDF Output File as Streaming Response
    """
    doc_path = default_extract_dir / file.filename
    with open(default_extract_dir / file.filename, "wb") as f:
        f.write(await file.read())
    extractor = PDFExtract(doc_path=doc_path)
    extractor.extract_text()
    zip_file_buffer = extractor.zip_results()
    zip_name = extractor.outname
    del extractor
    headers = {
        "Content-Disposition": "attachment; filename={}".format(zip_name + ".zip"),
        "Access-Control-Expose-Headers": "Content-Disposition",
    }
    media_type = "application/zip"
    response = StreamingResponse(
        iter([zip_file_buffer.getvalue()]), media_type=media_type, headers=headers
    )

    return response


@app.get("/info", response_model=settings.Setting)
async def info() -> dict:
    """App Information

    Returns:
        dict: Provinance information of the App.
    """
    return setting


# time http calls
from time import time


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app_mode = os.environ.get("APP_MODE") or "production"
    if app_mode == "development":
        reload = True
        access_log = True
    else:
        reload = False
        access_log = False
        "--workers", "6", "--proxy-headers"
    uvicorn.run(
        "app:app", host="0.0.0.0", port=port, reload=reload, access_log=access_log
    )
