''' Place to define all data processing and operations
related to gitlab media operations'''
import os
from datetime import datetime
from fastapi.responses import StreamingResponse, Response
import gitlab
import db_models

access_token = os.environ.get("VACHAN_GITLAB_TOKEN")
BYTES_PER_RESPONSE = 100000
CACHEDMEDIA = []
cached_media_download = []
MEDIA_CACHE_LIMIT = 3

gl = gitlab.Gitlab(url="https://gitlab.bridgeconn.com", private_token=access_token)

def media_streamer(stream, chunk_size, start, size):
    '''chunk up the object and return in pieces'''
    # print("comes in streamer once with start:", start)

    bytes_to_read = min(start+chunk_size, size)
    yield stream[start: start+bytes_to_read]

def get_gitlab_stream(request, repo, tag, file_path,permanent_link,**kwargs):#pylint: disable=too-many-locals
    """get stream from gtilab"""
    start_time = kwargs.get("start_time", None)#pylint: disable=W0612
    end_time = kwargs.get("end_time", None)#pylint: disable=W0612

    global CACHEDMEDIA #pylint: disable=W0603
    asked = request.headers.get("Range")
    # print("comes in router func once with range:", asked)

    if permanent_link is None or permanent_link == '':
        url = f"{repo}/-/raw/{tag}/{file_path}"
    else:
        url = permanent_link

    if url.endswith("mp4"):
        content_type =  "video/mp4"
    elif url.endswith("mov") or url.endswith("MOV"):
        content_type =  "video/quicktime"
    else:
        raise Exception("Unsupported video format!")

    stream = None
    for med in CACHEDMEDIA:
        if url == med['url']:
            stream = med['stream']
            med['last_access'] = datetime.now()
    if stream is None:
        # # Currently, it is not possible to fetch LFS-tracked files from the API at all.
        # # https://gitlab.com/gitlab-org/gitlab-foss/-/issues/41843
        # project_name_with_namespace = repo # "namespace/project_name"
        # project = gl.projects.get(project_name_with_namespace)
        # file_obj = project.files.get(file_path=file_path, ref=tag)
        # file_raw = project.files.raw(file_path=file_path, ref=file_obj.commit_id)
        # stream = file_raw
        stream = gl.http_get(url).content
        if len(CACHEDMEDIA) == MEDIA_CACHE_LIMIT:
            CACHEDMEDIA = sorted(CACHEDMEDIA, key=lambda x: x['last_access'], reverse=False)
            CACHEDMEDIA.pop(0)
        CACHEDMEDIA.append({"url":url, "stream":stream, "last_access":datetime.now()})

    total_size = len(stream)
    # print("file size with len:", total_size)

    start_byte_requested = int(asked.split("=")[-1][:-1])
    end_byte_planned = min(start_byte_requested + BYTES_PER_RESPONSE, total_size)

    return StreamingResponse(
        media_streamer(stream, chunk_size=BYTES_PER_RESPONSE,
                        start=start_byte_requested, size=total_size),
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte_requested}-{end_byte_planned}/{total_size}",
            "Content-Type": content_type
        },
        status_code=206)

def get_gitlab_download(repo, tag, permanent_link, file_path):
    """get downlaodable content from gtilab"""

    if permanent_link is None or permanent_link == '':
        url = f"{repo}/-/raw/{tag}/{file_path}"
    else:
        url = permanent_link

    stream = gl.http_get(url).content
    response = Response(stream)

    response.headers["Content-Disposition"] = "attachment; filename=stream.mp4"
    response.headers["Content-Type"] = "application/force-download"
    response.headers["Content-Transfer-Encoding"] = "Binary"
    response.headers["Content-Type"] = "application/octet-stream"
    return response


def find_media_source(repo, db_):
    """find source of requested gitlab media"""
    query = db_.query(db_models.Source)
    query = query.filter(db_models.Source.metaData.contains({"repo":repo})).first()
    return query
