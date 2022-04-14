"""API endpoints related to media"""
import re
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, Request, Depends
from starlette.datastructures import URL
from sqlalchemy.orm import Session
from schema import schemas
from routers.utils import get_source_and_permission_check
from crud import media_crud
from custom_exceptions import NotAvailableException, UnprocessableException
from dependencies import log, get_db
from auth.authentication import get_auth_access_check_decorator ,\
    get_user_or_none

router = APIRouter()

@router.get("/v2/media/gitlab/stream",
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},403:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Media"])
@get_auth_access_check_decorator
async def stream_media(request: Request, #pylint: disable=unused-argument,too-many-arguments
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query(None,example="main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/"+
            "trial-media-project/-/raw/main/token videos/Apostle.MOV"),
    start_time: Optional[datetime] =Query(None),
    end_time: Optional[datetime] =Query(None),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''Access the file from gitlab and pass it on to clients.
    * tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    * start and end time are optional in format of H:M:S.000
    '''
    log.info('In get_stream_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s, start_time: %s, end_time: %s',
        repo, tag, file_path, permanent_link, start_time, end_time)
    if not permanent_link:
        if not repo or not file_path:
            raise UnprocessableException("Either Permanent Link or repo + file_path is"+
                "mandatory to identify the media")
        repo = "https://gitlab.bridgeconn.com/" + repo
    else:
        repo = permanent_link.split("/-/")[0]
        part2 = permanent_link.split("/-/")[1]
        tag =  re.search(r'[^raw/]\w+',part2)[0]
        file_path = re.search(f'[^raw/{tag}].+',part2)[0]

    # find source
    db_source = media_crud.find_media_source(repo, db_)
    if db_source is None:
        raise NotAvailableException(f"No source is available for {repo}")
    source_name = db_source.sourceName
    request.scope['path'] = "/v2/sources"
    request._url = URL("/v2/sources")#pylint: disable=W0212

    tables = await get_source_and_permission_check(source_name, request, user_details, db_)
    if len(tables) == 0:
        raise NotAvailableException("No sources available for the requested name or language")
    if tag is None:
        if not "defaultBranch" in tables[0].metaData:
            raise NotAvailableException("Default Branch is Not in source metadata")
        tag = tables[0].metaData["defaultBranch"]
    return media_crud.get_gitlab_stream(request, repo, tag, file_path,
        permanent_link, start_time=start_time, end_time=end_time)


@router.get("/v2/media/gitlab/download",
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},403:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Media"])
# @get_auth_access_check_decorator
async def download_media(request: Request, #pylint: disable=too-many-arguments
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query(None,example="main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/"+
            "trial-media-project/-/raw/main/token videos/Apostle.MOV"),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''Access the file from gitlab and pass it on to clients.
    tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    '''
    log.info('In get_download_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s',
        repo, tag, file_path, permanent_link)
    if not permanent_link:
        if not repo or not file_path:
            raise UnprocessableException("Either Permanent Link or repo + file_path is\
                 mandatory to identify the media")
        repo = "https://gitlab.bridgeconn.com/" + repo
    else:
        repo = permanent_link.split("/-/")[0]
        part2 = permanent_link.split("/-/")[1]
        tag =  re.search(r'[^raw/]\w+',part2)[0]
        file_path = re.search(f'[^raw/{tag}].+',part2)[0]

    # find source
    db_source = media_crud.find_media_source(repo, db_)
    if db_source is None:
        raise NotAvailableException(f"No source is available for {repo}")
    source_name = db_source.sourceName

    # request.scope['path'] = "/v2/sources"
    # request._url = URL("/v2/sources")#pylint: disable=W0212

    tables = await get_source_and_permission_check(source_name, request, user_details, db_)

    if len(tables) == 0:
        raise NotAvailableException("No sources available for the requested name or language")
    if tag is None:
        if not "defaultBranch" in tables[0].metaData:
            raise NotAvailableException("Default Branch is Not in source metadata")
        tag = tables[0].metaData["defaultBranch"]
    return media_crud.get_gitlab_download(repo, tag, permanent_link, file_path)
