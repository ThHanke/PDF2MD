# app.py
import os
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

#from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, HTTPException, FastAPI
from fastapi.responses import StreamingResponse


from typing import Optional, Any, Union
from pydantic import BaseModel, AnyUrl, Field, FileUrl

from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import PROV, RDF, RDFS, XSD
from rdflib.util import guess_format

import settings
setting = settings.Setting()

from enum import Enum

from pdfextract import PDFExtract

class ReturnType(str, Enum):
    jsonld="json-ld"
    n3="n3"
    #nquads="nquads" #only makes sense for context-aware stores
    nt="nt"
    hext="hext"
    #prettyxml="pretty-xml" #only makes sense for context-aware stores
    trig="trig"
    #trix="trix" #only makes sense for context-aware stores
    turtle="turtle"
    longturtle="longturtle"
    xml="xml"

def path2url(path):
    
    return urlparse(path,scheme='file').geturl()

def get_media_type(format: str) -> str:
    """ Returns a mime type for a Response of serialized rdf
    Args:
        format (str): format as one of ["json-ld","n3","nt","hext","trig","turtle","longturtle","xml"]

    Returns:
        str: mime type, for example "application/xml"
    """
    if format==ReturnType.jsonld:
        media_type='application/json'
    elif format==ReturnType.xml:
        media_type='application/xml'
    elif format in [ReturnType.turtle, ReturnType.longturtle]:
        media_type='text/turtle'
    else:
        media_type='text/utf-8'
    return media_type

def parse_graph(url: AnyUrl, graph: Graph = Graph(), format: str = '') -> Graph:
    """Parse a Graph from web url to rdflib graph object

    Args:
        url (AnyUrl): Url to an web ressource
        graph (Graph): Existing Rdflib Graph object to parse data to.
        format (str):  rdf format as one of ["json-ld","n3","nt","hext","trig","turtle","longturtle","xml"]

    Returns:
        Graph: Rdflib graph Object
    """
    parsed_url=urlparse(url)
    if not format:
        format=guess_format(parsed_url.path)
    print(parsed_url.path, format)
    if parsed_url.scheme in ['https', 'http']:
        graph.parse(urlopen(parsed_url.geturl()).read(), format=format)

    elif parsed_url.scheme in ['file','']:
        graph.parse(parsed_url.path, format=format)
    return graph

def add_prov(graph: Graph, api_url: str, data_url: str) -> Graph:
    """ Add prov-o information to output graph

    Args:
        graph (Graph): Graph to add prov information to
        api_url (str): the api url 
        data_url (str): the url to the rdf file that was used

    Returns:
        Graph: Input Graph with prov metadata of the api call 
    """
    graph.bind('prov',PROV)
    
    root=BNode()
    api_node=URIRef(api_url)
    graph.add((root,PROV.wasGeneratedBy,api_node))
    graph.add((api_node,RDF.type,PROV.Activity))
    software_node=URIRef(setting.source+"/releases/tag/"+setting.version)
    graph.add((api_node,PROV.wasAssociatedWith,software_node))
    graph.add((software_node,RDF.type,PROV.SoftwareAgent))
    graph.add((software_node,RDFS.label,Literal( setting.name+setting.version)))
    graph.add((software_node,PROV.hadPrimarySource,URIRef(setting.source)))
    graph.add((root,PROV.generatedAtTime,Literal(str(datetime.now().isoformat()),datatype=XSD.dateTime)))
    entity=URIRef(str(data_url))
    graph.add((entity,RDF.type,PROV.Entity))
    derivation=BNode()
    graph.add((derivation,RDF.type,PROV.Derivation))
    graph.add((derivation,PROV.entity,entity))
    graph.add((derivation,PROV.hadActivity,api_node))
    graph.add((root,PROV.qualifiedDerivation,derivation))
    graph.add((root,PROV.wasDerivedFrom,entity))
    
    return graph

#flash integration flike flask flash
def flash(request: Request, message: Any, category: str = "info") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

def get_flashed_messages(request: Request):
    return request.session.pop("_messages") if "_messages" in request.session else []

middleware = [
    Middleware(SessionMiddleware, secret_key=os.environ.get('APP_SECRET','changemeNOW')),
    Middleware(CSRFProtectMiddleware, csrf_secret=os.environ.get('APP_SECRET','changemeNOW')),
    Middleware(CORSMiddleware, 
            allow_origins=["*"], # Allows all origins
            allow_methods=["*"], # Allows all methods
            allow_headers=["*"] # Allows all headers
            ),
    Middleware(uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware, trusted_hosts="*")
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
    contact={"name": setting.contact_name, "url": setting.org_site, "email": setting.admin_email},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_url=setting.openapi_url,
    openapi_tags=tags_metadata,
    docs_url=setting.docs_url,
    redoc_url=None,
    swagger_ui_parameters= {'syntaxHighlight': False},
    #swagger_favicon_url="/static/resources/favicon.svg",
    middleware=middleware
)


app.mount("/static/", StaticFiles(directory='static', html=True), name="static")
templates= Jinja2Templates(directory="templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages

logging.basicConfig(level=logging.DEBUG)

class ConvertRequest(BaseModel):
    data_url: Union[AnyUrl, FileUrl] = Field('', title='Raw Data Url', description='Url to raw data')
    format: Optional[ReturnType] = Field(ReturnType.jsonld, title='Serialization Format', description='The format to use to serialize the rdf.')
    
    class Config:
        json_schema_extra = {
            "example": {
                "data_url": "https://github.com/Mat-O-Lab/CSVToCSVW/raw/main/examples/example-metadata.json",
                "format": "json-ld"
            }
        }

class ExampleResponse(BaseModel):
    filename:  str = Field('example.ttl', title='Resulting File Name', description='Suggested filename of the generated rdf.')
    filedata: str = Field( title='Generated RDF', description='The generated rdf for the given meta data file as string in utf-8.')

class StartFormUri(StarletteForm):
    data_url = URLField(
        'URL Data File',
        #validators=[DataRequired()],
        description='Paste URL to a data file, e.g. csv, TRA',
        #validators=[DataRequired(message='Either URL to data file or file upload is required.')],
        render_kw={"class":"form-control", "placeholder": "https://github.com/Mat-O-Lab/CSVToCSVW/raw/main/examples/example-metadata.json"},
    )
    file=FileField(
        'Upload File',
        description='Upload your File here.',
        render_kw={"class":"form-control", "placeholder": "Your File"},
    )


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
@csrf_protect
async def get_index(request: Request):
    """GET /: form handler
    """
    template="index.html"
    form = await StartFormUri.from_formdata(request)
    return templates.TemplateResponse(template, {"request": request,
        "form": form,
        "result": '',
        "setting": setting
        }
    )


@app.post('/', response_class=HTMLResponse, include_in_schema=False)
@csrf_protect
async def post_index(request: Request):
    """POST /: form handler
    """
    template="index.html"
    form = await StartFormUri.from_formdata(request)
    result = ''
    filename = ''
    payload= ''
    if not (form.data_url.data or form.file.data.filename):
        msg='URL Data File empty: using placeholder value for demonstration.'
        logging.debug('URL Data File empty: using placeholder value for demonstration.')
        form.data_url.data=form.data_url.render_kw['placeholder']
        flash(request,msg,'info')
    if await form.validate_on_submit():
        if form.file.data.filename:
            with open(form.file.data.filename, mode="wb") as f:
                f.write(await form.file.data.read())
                file_path=os.path.realpath(f.name)
                data_url=path2url(file_path)
        elif form.data_url.data:
            data_url=form.data_url.data
        filename=data_url.rsplit('/',1)[-1].rsplit('.',1)[0]
        try:
            graph= parse_graph(data_url)
        except Exception as e:
            flash(request,e, category="error")
        else:    
            #add prov-o annotations
            graph=add_prov(graph,request.url._url,data_url)
            #serialize
            result=graph.serialize(format='json-ld')
            filename=filename+'json'
            b64 = base64.b64encode(result.encode())
            payload = b64.decode()
            #remove temp file
        if form.file.data.filename:
            os.remove(file_path)
    # return response
    return templates.TemplateResponse(template, {"request": request,
        "form": form,
        "result": result,
        "filename": filename,
        "payload": payload,
        "setting": setting
        }
    )

@app.post("/api/convert", tags=["transform"])
async def convert(request: Request, convert_request: ConvertRequest) -> StreamingResponse:
    """Converts a rdf file on the web to the specified serializatio format.

    Args:
        request (Request): general request
        convert_request (ConvertRequest): convert informatation

    Raises:
        HTTPException: Error description

    Returns:
        StreamingResponse: RDF Output File as Streaming Response
    """
    data_url=str(convert_request.data_url)
    try:
        graph= parse_graph(data_url)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    #add prov-o annotations
    graph=add_prov(graph,request.url._url,data_url)
    result=graph.serialize(format=convert_request.format.value)
    
    filename=data_url.rsplit('/',1)[-1].rsplit('.',1)[0]
    if convert_request.format.value in ['turtle','longturtle']:
        filename+='.ttl'
    elif convert_request.format.value=='json-ld':
        filename+='.json'
    else:
        filename+='.'+convert_request.format.value 
    data_bytes=BytesIO(result.encode())
    headers = {
        'Content-Disposition': 'attachment; filename={}'.format(filename),
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    media_type=get_media_type(convert_request.format)
    return StreamingResponse(content=data_bytes, media_type=media_type, headers=headers)

from pathlib import Path
default_test_dir=Path.cwd() / "test"

@app.post("/api/extract", tags=["extract transform"])
async def convert(request: Request, convert_request: ConvertRequest) -> StreamingResponse:
    """Converts a rdf file on the web to the specified serializatio format.

    Args:
        request (Request): general request
        convert_request (ConvertRequest): convert informatation

    Raises:
        HTTPException: Error description

    Returns:
        StreamingResponse: RDF Output File as Streaming Response
    """
    data_url=str(convert_request.data_url)
    # try:
    #     graph= parse_graph(data_url)
    # except Exception as e:
    #     raise HTTPException(status_code=404, detail=str(e))
    # #add prov-o annotations
    # graph=add_prov(graph,request.url._url,data_url)
    #result=graph.serialize(format=convert_request.format.value)
    PDFExtract(default_test_dir / "science_article2.pdf")
    
    filename=data_url.rsplit('/',1)[-1].rsplit('.',1)[0]
    if convert_request.format.value in ['turtle','longturtle']:
        filename+='.ttl'
    elif convert_request.format.value=='json-ld':
        filename+='.json'
    else:
        filename+='.'+convert_request.format.value 
    data_bytes=BytesIO(result.encode())
    headers = {
        'Content-Disposition': 'attachment; filename={}'.format(filename),
        'Access-Control-Expose-Headers': 'Content-Disposition'
    }
    media_type=get_media_type(convert_request.format)
    return StreamingResponse(content=data_bytes, media_type=media_type, headers=headers)

@app.get("/info", response_model=settings.Setting)
async def info() -> dict:
    """App Information

    Returns:
        dict: Provinance information of the App.
    """
    return setting

#time http calls
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
    app_mode=os.environ.get("APP_MODE") or 'production'
    if app_mode=='development':
        reload=True
        access_log=True
    else:
        reload=False
        access_log=False
        "--workers", "6","--proxy-headers"
    uvicorn.run("app:app",host="0.0.0.0",port=port, reload=reload, access_log=access_log)


    
