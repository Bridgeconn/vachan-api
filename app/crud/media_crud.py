''' Place to define all data processing and operations
related to gitlab media operations'''
import os
from datetime import datetime
from fastapi.responses import StreamingResponse, FileResponse
import gitlab

access_token = os.environ.get("VACHAN_GITLAB_TOKEN")
BYTES_PER_RESPONSE = 100000
cached_media = []
cached_media_download = []
MEDIA_CACHE_LIMIT = 3

gl = gitlab.Gitlab(url="https://gitlab.bridgeconn.com", private_token=access_token)

def media_streamer(stream, chunk_size, start, size):
    '''chunk up the object and return in pieces'''
    print("comes in streamer once with start:", start)

    bytes_to_read = min(start+chunk_size, size)
    yield stream[start: start+bytes_to_read]

def get_gitlab_stream(request, repo, tag, file_path, permanent_link,**kwargs):
    """get stream from gtilab"""
    start_time = kwargs.get("start_time", None)
    end_time = kwargs.get("end_time", None)

    global cached_media
    asked = request.headers.get("Range")
    print("comes in router func once with range:", asked)

    if permanent_link is None or permanent_link == '':
        url = f"https://gitlab.bridgeconn.com/{repo}/-/raw/{tag}/{file_path}"
    else:
        url = permanent_link

    if url.endswith("mp4"):
        content_type =  "video/mp4"
    elif url.endswith("mov"):
        content_type =  "video/quicktime"
    else:
        raise Exception("Unsupported video format!")
    
    stream = None
    for med in cached_media:
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
        # print("get stream data----->",stream)
        if len(cached_media) == MEDIA_CACHE_LIMIT:
            cached_media = sorted(cached_media, key=lambda x: x['last_access'], reverse=False)
            cached_media.pop(0)
        cached_media.append({"url":url, "stream":stream, "last_access":datetime.now()})
    
    total_size = len(stream)
    print("file size with len:", total_size)

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

def get_gitlab_download(request, repo, tag, file_path,permanent_link):
    """get downlaodable content from gtilab"""
    if permanent_link is None or permanent_link == '':
        url = f"https://gitlab.bridgeconn.com/{repo}/-/raw/{tag}/{file_path}"
    else:
        url = permanent_link
   
    stream = gl.http_get(url).content

    print("name---->",url.split("/")[-1])
    filename = url.split("/")[-1]
    fn=url.split("/")[-1]
    with open(fn, 'wb') as file:
        file.write(stream)
    filepath = os.path.join(os.getcwd(),url.split("/")[-1])
    print("current cwd------------------->",filepath)
    # response = FileResponse(filepath, media_type="application/octet-stream", filename=fn)
    response = FileResponse(filepath)

    # memfile = BytesIO(stream)
    # response = StreamingResponse(memfile, media_type="")
    # response.headers["Content-Disposition"] = f"inline; filename={filename}"
    
    return FileResponse(stream)
    # return response