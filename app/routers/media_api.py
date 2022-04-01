from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, Request
from crud import media_crud
from dependencies import log

router = APIRouter()

@router.get("/v2/media/gitlab/stream", status_code=200, tags=["Media"])
async def stream_media(request: Request, #pylint: disable=unused-argument
    repo: str = Query(None,example="kavitha.raju/trial-media-project"),
    tag: str = Query("main"),
    file_path: str=Query(None,example="token videos/Apostle.MOV"),
    permanent_link: str=Query(None,example=
        "https://gitlab.bridgeconn.com/kavitha.raju/trial-media-project/-/raw/main/token videos/Apostle.MOV"),
    start_time: Optional[datetime] =Query(None),
    end_time: Optional[datetime] =Query(None)):
    '''Access the file from gitlab and pass it on to clients.
    tag can be a commit-hash, branch-name or release-tag.
    * to access a content provide either (repo + tag+ file_path) or permanent_link
    * permanent link will be considered if its given
    * start and end time are optional in format of H:M:S.000
    '''
    log.info('In get_stream_media')
    log.debug('repo:%s, tag %s, file_path: %s, permanent_link: %s, start_time: %s, end_time: %s',
        repo, tag, file_path, permanent_link, start_time, end_time)
    return media_crud.get_gitlab_stream(request, repo, tag, file_path,
        permanent_link, start_time=start_time, end_time=end_time)

    
