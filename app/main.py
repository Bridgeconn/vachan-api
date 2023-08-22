'''Defines all API endpoints for the web server app'''
import os
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
# pylint: disable=E0401
from custom_exceptions import GenericException,TypeException , PermissionException,\
    UnprocessableException,NotAvailableException, AlreadyExistsException,\
        UnAuthorizedException, GitlabException
import db_models
from database import engine
from dependencies import get_db, log
from routers import content_apis, translation_apis, auth_api, media_api, filehandling_apis
from auth.authentication import create_super_user
# pylint: enable=E0401

# from auth.api_permission_map import initialize_apipermissions

#create super user
if os.environ.get("VACHAN_TEST_MODE", "False") != 'True':

    create_super_user()

app = FastAPI(title="Vachan-API", version="2.0.0-beta.10",
    description="The server application that provides APIs to interact \
with the underlying Databases and modules in Vachan-Engine.")
template = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#read JSON and api permissions on startup
# initialize_accessrules()
# initialize_apipermissions()

######### Error Handling ##############
@app.exception_handler(Exception)
async def any_exception_handler(request, exc: Exception):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",'Error', str(exc))
    if hasattr(exc, "status_code"):
        status_code=exc.status_code
    else:
        status_code = 500
    return JSONResponse(
        status_code =status_code,
        content={"error": 'Error', "details" : str(exc)},
    )

@app.exception_handler(GenericException)
async def generic_exception_handler(request, exc: GenericException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request, exc: SQLAlchemyError):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    if hasattr(exc, 'orig'):
        detail = str(exc.orig).replace('DETAIL:','')
    else:
        detail = str(exc)
    log.exception("%s: %s","Database Error", detail)
    return JSONResponse(
        status_code=502,
        content={"error": "Database Error", "details" : detail},
    )

@app.exception_handler(NotAvailableException)
async def na_exception_handler(request, exc: NotAvailableException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(AlreadyExistsException)
async def exists_exception_handler(request, exc: AlreadyExistsException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(TypeException)
async def type_exception_handler(request, exc: TypeException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(PermissionException)
async def permision_exception_handler(request, exc: PermissionException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(UnAuthorizedException)
async def unauthorized_exception_handler(request, exc: UnAuthorizedException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(UnprocessableException)
async def unprocessable_exception_handler(request, exc: UnprocessableException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s",exc.name, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details" : exc.detail},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    '''logs and returns error details'''
    log.error("Request URL:%s %s, from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("Http Error: %s", exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "details": str(exc.detail)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    '''logs and returns error details'''
    log.error("Request URL:%s %s, from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("Input Validation Error: %s", str(exc))
    return JSONResponse(
        status_code=422,
        content={"error": "Input Validation Error" ,"details": str(exc).replace("\n", ". ")}
    )

@app.exception_handler(IntegrityError)
async def unique_violation_exception_handler(request, exc: IntegrityError):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s","Already Exists/Conflict", exc.__dict__)

    if "unique constraint" in str(exc.orig):
        return JSONResponse(
        status_code=409,
        content={"error": "Already Exists", "details" : str(exc.orig).replace("DETAIL","")},
        )
    if "foreign key constraint" in str(exc.orig):
        return JSONResponse(
        status_code=409,
        content={"error": "Conflict", "details" : str(exc.orig).replace("DETAIL","")},
        )

@app.exception_handler(GitlabException)
async def gitlab_exception_handler(request, exc: GitlabException):
    '''logs and returns error details'''
    log.error("Request URL:%s %s,  from : %s",
        request.method ,request.url.path, request.client.host)
    log.exception("%s: %s","Gitlab Error", exc.__dict__)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.name, "details": str(exc.detail)}
    )
######################################################
db_models.map_all_dynamic_tables(db_= next(get_db()))
db_models.Base.metadata.create_all(bind=engine)


@app.get('/', response_class=HTMLResponse, status_code=200)
def test(request: Request,db_: Session = Depends(get_db)):
    '''Tests if app is running and the DB connection is active
    * Also displays API documentation page upon successful connection on root endpoint'''
    db_.query(db_models.Language).first()
    root_url = os.getenv("VACHAN_DOMAIN")
    if root_url is not None and not root_url.startswith("http://"):
        root_url = "http://" + root_url
    return template.TemplateResponse(
        "landing_page.html",
        {
            "request": request,
            "root_url": root_url
        }
    )

app.include_router(auth_api.router)
app.include_router(content_apis.router)
app.include_router(translation_apis.router)
app.include_router(media_api.router)
app.include_router(filehandling_apis.router)

beta_endpoints = [
    "/graphql",  # Specify the paths of the beta endpoints
    "/v2/resources/bibles/{resource_name}/versification",
    "/v2/resources/bibles/{resource_name}/books/{book_code}/export/{output_format}",
    "/v2/text/translate/token-based/project/versification",
    "/v2/media/gitlab/stream",
    "/v2/media/gitlab/download",
    "/v2/files/usfm/to/{output_format}"
]

def custom_openapi():
    '''Modify the auto generated openapi schema for API docs'''
    openapi_schema = get_openapi(title="Vachan-API", version="2.0.0-beta.10",
        description="The server application that provides APIs to interact \
        with the underlying Databases and modules in Vachan-Engine.",
        routes=app.routes)

    # Add version information to specific endpoints
    for path, path_data in openapi_schema["paths"].items():
        for _, method_data in path_data.items():
            if path in beta_endpoints:
                # Set endpoints as experimental in the API-docs
                method_data.setdefault("x-experimental", True)

    return openapi_schema

app.openapi = custom_openapi
