"""API endpoints related to media"""
import re
from datetime import datetime
from typing import  Optional
from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from schema import schemas,schema_auth
from routers.content_apis import get_source
from crud import media_crud
from custom_exceptions import NotAvailableException, UnprocessableException
from dependencies import log, get_db
from auth.authentication import get_auth_access_check_decorator ,\
    get_current_user_data
from redis_db.utils import  get_routes_from_cache, set_routes_to_cache

router = APIRouter()

async def get_and_accesscheck_for_repo(repo, file_path, tag, permanent_link, db_,*args):
    """find repo and check access for source"""
    request = args[0]
    user_details = args[1]
    if not permanent_link:
        if not repo or not file_path:
            raise UnprocessableException("Either Permanent Link or repo + file_path is"+
                 " mandatory to identify the media")
        repo = "https://gitlab.bridgeconn.com/" + repo
        permanent_link = f"{repo}/-/raw/{tag}/{file_path}"
    else:
        repo = permanent_link.split("/-/")[0]
        tag =  re.search(r'/-/[^/]+/[^/]+',permanent_link)[0].split("/")[-1]
        file_path = re.findall(r'(/-/[^/]+/[^/]+/)(.+)',permanent_link)[0][-1]

        permanent_link =  re.sub(r'/-/[^/]+',"/-/raw",permanent_link)
    # find source
    db_source = media_crud.find_media_source(repo, db_)
    # print("permanent link ======", db_source)
    if db_source is None:
        raise NotAvailableException(f"No source is available for {repo}")
    source_name = db_source.sourceName

    try:
        tables = await get_source(request=request,source_name=source_name,
        content_type=None, version_abbreviation=None,
        revision=None,language_code=None,license_code=None,
        metadata=None,access_tag = None, active= True, latest_revision= True,
        limit=1000, skip=0, db_=db_, user_details=user_details,
        filtering_required=True,
        operates_on=schema_auth.ResourceType.CONTENT.value)
    except Exception:
        log.error("Error in getting sources list")
        raise

    if len(tables) == 0:
        raise NotAvailableException("No sources available for the requested repo, \
accessible to the user")
    if tag is None:
        if not "defaultBranch" in tables[0].metaData:
            raise NotAvailableException("Default Branch is Not in source metadata")
        tag = tables[0].metaData["defaultBranch"]

    return repo, tag, permanent_link, file_path

@router.get("/v2/media/gitlab/stream",
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},403:{"model": schemas.ErrorResponse},
    406:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Media"])
@get_auth_access_check_decorator
async def stream_media(request: Request, #pylint: disable=unused-argument,too-many-arguments
    access_token: str = Query(None),
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query(None,example="main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/"+
            "trial-media-project/-/raw/main/token videos/Apostle.MOV"),
    start_time: Optional[datetime] =Query(None),
    end_time: Optional[datetime] =Query(None),
    db_: Session = Depends(get_db)):
    '''Access the file from gitlab and pass it on to clients.
    * Support Medias - Video , Audio, Image
    * tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    * start and end time are optional in format of H:M:S.000
    '''
    log.info('In get_stream_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s, start_time: %s, end_time: %s',
        repo, tag, file_path, permanent_link, start_time, end_time)

    user_details = get_current_user_data(access_token)

    repo, tag, permanent_link, file_path = await get_and_accesscheck_for_repo(repo, file_path,
        tag, permanent_link, db_, request, user_details)

    # redis cache part
    stream = get_routes_from_cache(key= permanent_link)
    # print("stream type from cache --------------->",type(stream))
    if stream is None:
        stream = media_crud.get_gitlab_download(repo, tag, permanent_link, file_path)
        # print("stream type direct gitlab --------------->",type(stream))
        set_routes_to_cache(key=permanent_link, value=stream)

    return media_crud.get_gitlab_stream(request, repo, tag, file_path,
        permanent_link, start_time=start_time, end_time=end_time, stream = stream)


@router.get("/v2/media/gitlab/download",
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},403:{"model": schemas.ErrorResponse}},
    status_code=200, tags=["Media"])
@get_auth_access_check_decorator
async def download_media(request: Request, #pylint: disable=too-many-arguments
    access_token: str = Query(None),
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query(None,example="main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/"+
            "trial-media-project/-/raw/main/token videos/Apostle.MOV"),
    db_: Session = Depends(get_db)):
    '''Access the file from gitlab and pass it on to clients.
    tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    '''
    log.info('In get_download_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s',
        repo, tag, file_path, permanent_link)

    user_details = get_current_user_data(access_token)

    repo, tag, permanent_link, file_path = await get_and_accesscheck_for_repo(repo, file_path,
        tag, permanent_link, db_, request, user_details)

    # redis cache part
    data = get_routes_from_cache(key= permanent_link)
    # print("stream type from cache --------------->",type(data))
    if data is None:
        data = media_crud.get_gitlab_download(repo, tag, permanent_link, file_path)
        # print("stream type direct gitlab --------------->",type(data))
        set_routes_to_cache(key=permanent_link, value=data)

    response =  Response(data)
    response.headers["Content-Disposition"] = "attachment; filename=stream.mp4"
    response.headers["Content-Type"] = "application/force-download"
    response.headers["Content-Transfer-Encoding"] = "Binary"
    response.headers["Content-Type"] = "application/octet-stream"
    return response
