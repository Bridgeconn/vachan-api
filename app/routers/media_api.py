from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, Request, Depends
from starlette.datastructures import URL
from sqlalchemy.orm import Session
from crud import media_crud
from schema import schemas, schema_auth
from custom_exceptions import NotAvailableException
from routers.content_apis import get_source
from dependencies import log, get_db
from auth.authentication import get_auth_access_check_decorator ,\
    get_user_or_none

router = APIRouter()

@router.get("/v2/media/gitlab/stream", status_code=200, tags=["Media"])
@get_auth_access_check_decorator
async def stream_media(request: Request, #pylint: disable=unused-argument
    source_name:schemas.TableNamePattern=Query(None,example="en_TBP_1_bible"),
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query("main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/trial-media-project/-/raw/main/token videos/Apostle.MOV"),
    start_time: Optional[datetime] =Query(None),
    end_time: Optional[datetime] =Query(None),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):
    '''Access the file from gitlab and pass it on to clients.
    tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    * start and end time are optional in format of H:M:S.000
    '''
    log.info('In get_stream_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s, start_time: %s, end_time: %s',
        repo, tag, file_path, permanent_link, start_time, end_time)

    # check getting source
    if source_name:
        parts = source_name.split('_')
        language_code = parts[0]
        version_abbreviation = parts[1]
        revision = parts[2]
        content_type = parts[3]
    request.scope['path'] = "/v2/sources"
    request._url = URL("/v2/sources")
    # print("request----->",request.scope['path'])
    # print("request url path----->",request.url.path)
    try:
        tables = await get_source(request=request, content_type=content_type,
            version_abbreviation=version_abbreviation,
            revision=revision,
            language_code=language_code,
            license_code=None, metadata=None,
            access_tag = None,
            active= True, latest_revision= True,
            skip=0, limit=1000,
            user_details=user_details, db_=db_,
            operates_on=schema_auth.ResourceType.CONTENT.value,
            filtering_required=True)
    except Exception:
        log.error("Error in getting sources list")
        raise
    if len(tables) == 0:
        raise NotAvailableException("No sources available for the requested name or language")
    return media_crud.get_gitlab_stream(request, repo, tag, file_path,
        permanent_link, start_time=start_time, end_time=end_time)

@router.get("/v2/media/gitlab/download", status_code=200, tags=["Media"])
async def download_media(request: Request, #pylint: disable=unused-argument
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query("main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/trial-media-project/-/raw/main/token videos/Apostle.MOV")):
    '''Access the file from gitlab and pass it on to clients.
    tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    '''
    log.info('In get_download_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s',
        repo, tag, file_path, permanent_link)
    return media_crud.get_gitlab_download(request, repo, tag, file_path,permanent_link)
    
