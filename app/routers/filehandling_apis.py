'''API endpoints related to file format handling. Uses usfm-grammar'''
from fastapi import APIRouter, Request, Path, Query, Depends, Body
from sqlalchemy.orm import Session
import usfm_grammar
from dependencies import get_db, log
from routers import content_apis
from schema import schemas, schema_content
from crud import files_crud
from auth.authentication import get_auth_access_check_decorator ,\
    get_user_or_none
from custom_exceptions import NotAvailableException, GenericException

router = APIRouter()
#pylint: disable=too-many-arguments,unused-argument

#################### USFM Grammar ####################

@router.get('/v2/resources/bibles/{resource_name}/books/{book_code}/export/{output_format}',
    responses={404: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ErrorResponse}},
    status_code=200, tags=['File Handling', 'Bibles'])
@get_auth_access_check_decorator
async def usfm_parse_resource_bible(request: Request,
    resource_name: schemas.TableNamePattern = Path(..., examples="hi_IRV_1_bible"),
    book_code: schemas.BookCodePattern=Path(..., examples="mat"),
    output_format: usfm_grammar.Format = Path(..., examples="usx"),
    content_filter_str: str = Query("PARAGRAPHS"),  # Use a string parameter
    chapter: int=Query(None, examples=1),
    active: bool=True,
    user_details = Depends(get_user_or_none),
    db_: Session = Depends(get_db)):
    '''Selects a bible from servers and converts it to required format using usfm-grammar'''
    log.info("In usfm_parse_resource_bible router function")
    log.debug('resource_name: %s, format: %s, filter: %s', resource_name,
              output_format, content_filter_str)
              
    # Set a default value for content_filter
    content_filter = None
    
    if content_filter_str:
        # Convert the string to the enum within the function
        content_filter = usfm_grammar.Filter[content_filter_str]
    
    src_response = await content_apis.get_available_bible_book(
        request=request,
        resource_name=resource_name,
        book_code=book_code,
        content_type=schema_content.BookContentType.USFM,
        active=active,
        skip=0, limit=100,
        user_details=user_details,
        db_=db_
    )
    if "error" in src_response:
        raise GenericException(src_response['error'])
    if len(src_response) == 0:
        raise NotAvailableException(f"Book, {book_code}, is not available in {resource_name}")
    input_usfm = src_response[0]['USFM']
    log.debug("Obtained usfm from resource bible, %s", input_usfm[:50])
    
    # Parse the USFM content and convert it to JSON
    usfm_parser = usfm_grammar.USFMParser(input_usfm)
    output_content = usfm_parser.to_usj(content_filter)
    
    return output_content


@router.put('/v2/files/usfm/to/{output_format}',
    responses={422: {"model": schemas.ErrorResponse}, 500: {"model": schemas.ErrorResponse}},
    status_code=200, tags=['File Handling'])
@get_auth_access_check_decorator
async def parse_uploaded_usfm(request:Request,
    output_format: usfm_grammar.Format = Path(..., examples="usx"),
    content_filter_str: str = Query("PARAGRAPHS"), 
    input_usfm: schema_content.UploadedUsfm = Body(...),
    chapter: int=Query(None, examples=1),
    user_details=Depends(get_user_or_none)):
    '''Allows to upload a USFM file to be converted to another format. uses usfm-grammar'''
    log.info("In parse_uploaded_usfm router function")
    log.debug("output_format: %s, content_filter: %s", output_format, content_filter_str)
    
    # Set a default value for content_filter
    content_filter = None
    
    if content_filter_str:
        # Convert the string to the enum within the function
        content_filter = usfm_grammar.Filter[content_filter_str]
    
    return files_crud.parse_with_usfm_grammar(
        input_usfm.USFM, output_format, content_filter, chapter)