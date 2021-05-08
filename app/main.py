'''Defines all API endpoints for the web server app'''

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from custom_exceptions import GenericException
from custom_exceptions import NotAvailableException, AlreadyExistsException, TypeException
import db_models
from database import engine
from dependencies import get_db, log
from schemas import NormalResponse

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
from routers import content_apis, translation_apis

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    log.exception("%s: %s","Already Exists", exc.__dict__)
    return JSONResponse(
        status_code=409,
        content={"error": "Already Exists", "details" : str(exc.orig).replace("DETAIL","")},
    )
######################################################

db_models.map_all_dynamic_tables(db_= next(get_db()))
db_models.Base.metadata.create_all(bind=engine)

@app.get('/', response_model=NormalResponse, status_code=200)
def test(db_: Session = Depends(get_db)):
    '''tests if app is running and the DB connection is active'''
    db_.query(db_models.Language).first()
    return {"message": "App is up and running"}

app.include_router(content_apis.router)
app.include_router(translation_apis.router)
