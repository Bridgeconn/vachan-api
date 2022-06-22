''' Place to define all data processing and operations
related to gitlab media operations'''
import os
import re
import mimetypes
import gitlab
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import db_models
from crud import utils
from crud.contents_crud import ref_to_bcv, bcv_to_ref
from custom_exceptions import NotAvailableException, TypeException

access_token = os.environ.get("VACHAN_GITLAB_TOKEN")
BYTES_PER_RESPONSE = 100000

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
    stream = kwargs.get("stream", None)#pylint: disable=W0612

    # asked = request.headers.get("Range")
    # print("comes in router func once with range:", asked)

    # asked = None

    if permanent_link is None or permanent_link == '':
        url = f"{repo}/-/raw/{tag}/{file_path}"
    else:
        url = permanent_link

    content_type = mimetypes.guess_type(url.split("/")[-1], strict=True)
    if content_type is None:
        raise Exception("Unsupported media format!")

    if "video" not in content_type[0] and "audio" not in content_type[0]:
        raise HTTPException(status_code=406,
            detail="Currently api supports only video and audio streams")

    if "Range" in request.headers:
        asked = request.headers.get("Range")
        # print("comes in router func once with range:", asked)
    else:
        raise HTTPException(status_code=406,
            detail="This is a Streaming api , Call it from supported players")

    if stream is None:
        # # Currently, it is not possible to fetch LFS-tracked files from the API at all.
        # # https://gitlab.com/gitlab-org/gitlab-foss/-/issues/41843
        # project_name_with_namespace = repo # "namespace/project_name"
        # project = gl.projects.get(project_name_with_namespace)
        # file_obj = project.files.get(file_path=file_path, ref=tag)
        # file_raw = project.files.raw(file_path=file_path, ref=file_obj.commit_id)
        # stream = file_raw
        # stream = gl.http_get(url).content
        stream = gl.http_get(url).content

    total_size = len(stream)

    start_byte_requested = int(asked.split("=")[-1][:-1])
    end_byte_planned = min(start_byte_requested + BYTES_PER_RESPONSE, total_size)

    return StreamingResponse(
        media_streamer(stream, chunk_size=BYTES_PER_RESPONSE,
                        start=start_byte_requested, size=total_size),
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start_byte_requested}-{end_byte_planned}/{total_size}",
            "Content-Type": content_type[0]
        },
        status_code=206)

def get_gitlab_download(repo, tag, permanent_link, file_path):
    """get downlaodable content from gtilab"""

    if permanent_link is None or permanent_link == '':
        url = f"{repo}/-/raw/{tag}/{file_path}"
    else:
        url = permanent_link
    stream = gl.http_get(url).content

    return stream

def find_media_source(repo, db_):
    """find source of requested gitlab media"""
    query = db_.query(db_models.Source)
    query = query.filter(db_models.Source.metaData.contains({"repo":repo})).first()
    return query

# bible Video
def get_bible_videos(db_:Session, source_name, book_code=None, title=None, series=None,**kwargs):#pylint: disable=too-many-locals
    '''fetches rows of bible videos as per provided source_name and filters'''
    search_word = kwargs.get("search_word",None)
    chapter = kwargs.get("chapter",None)
    active = kwargs.get("active",True)
    verse = kwargs.get("verse",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith(db_models.ContentTypeName.BIBLEVIDEO.value):
        raise TypeException('The operation is supported only on biblevideo')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if title:
        query = query.filter(model_cls.title == utils.normalize_unicode(title.strip()))
    if series:
        query = query.filter(model_cls.series == utils.normalize_unicode(series.strip()))
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', title || ' ' ||"+\
            " series || ' ' || description || ' ')"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    if book_code:
        book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == book_code.lower() ).first()
        if book_code and chapter and verse:
            bcv = ref_to_bcv(book.bookId,chapter,verse)
            fullbook = int(str(book.bookId)+'000000')
            book_chapter = book.bookId * 1000000 + chapter*1000
            query = query.filter(sqlalchemy.or_(model_cls.refIds.any(int(bcv)),
                model_cls.refIds.any(fullbook),model_cls.refIds.any(book_chapter)))
        elif book_code and chapter:
            book_chapter = book.bookId * 1000000 + chapter*1000
            fullbook = int(str(book.bookId)+'000000')
            raw_sql = f'''SELECT * FROM {model_cls.__tablename__}
                WHERE EXISTS (SELECT 1 FROM unnest(
                {model_cls.__tablename__}.ref_ids) AS ele WHERE
                ele BETWEEN {book_chapter} and {book_chapter+1000} OR ele={fullbook})'''
            result = db_.execute(raw_sql)
            id_list = [row[0] for row in result]
            query = query.filter(model_cls.bibleVideoId.in_(id_list))
        elif book_code:
            code = int(str(book.bookId) + "000000")
            raw_sql = f'''SELECT * FROM {model_cls.__tablename__}
             WHERE EXISTS (SELECT 1 FROM unnest(
                {model_cls.__tablename__}.ref_ids) AS ele
                WHERE ele >= {code} AND ele < {code+1000000})'''
            result = db_.execute(raw_sql)
            id_list = [row[0] for row in result]
            query = query.filter(model_cls.bibleVideoId.in_(id_list))

    query = query.filter(model_cls.active == active)
    db_content = query.offset(skip).limit(limit).all()
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    db_content_dict = [item.__dict__ for item in db_content]
    for content in db_content_dict:
        content['references'] = []
        for ref in content['refIds']:
            content['references'].append(bcv_to_ref(ref,db_))
    response = {
        'db_content':db_content_dict,
        'source_content':source_db_content
        }
    return response

def bible_video_db_content_generate(item,db_):
    """db content for post and put for bible video"""
    ref_id_list = set()
    for buk in item.references:
        # verifying if the book codes are valid as we dont use FK for this field
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == buk.bookCode.lower() ).first()
        if not book:
            raise NotAvailableException\
                ('Bible Book code, %s, not found in database'%buk.bookCode)
        #generate refid value in BCV
        if buk.verseEnd is None:
            buk.verseStart = 0 if buk.verseStart is None else buk.verseStart
            bcvcode = ref_to_bcv(book.bookId,buk.chapter,buk.verseStart)
            ref_id_list.add(int(bcvcode))
        else:
            for count in range(buk.verseStart,buk.verseEnd+1):
                current_verse = count
                bcvcode = ref_to_bcv(book.bookId,buk.chapter,current_verse)
                ref_id_list.add(int(bcvcode))
    return list(ref_id_list)

def upload_bible_videos(db_: Session, source_name, videos, user_id=None):
    '''Adds rows to the bible videos table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.BIBLEVIDEO.value:
        raise TypeException('The operation is supported only on biblevideo')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in videos:
        ref_id_list = bible_video_db_content_generate(item,db_)
        row = model_cls(
            title = utils.normalize_unicode(item.title.strip()),
            series = utils.normalize_unicode(item.series.strip()),
            description = utils.normalize_unicode(item.description.strip()),
            active = item.active,
            refIds = ref_id_list,
            videoLink = item.videoLink)
        db_content.append(row)
    db_content_dict = [item.__dict__ for item in db_content]
    for content in db_content_dict:
        content['references'] = []
        for ref in content['refIds']:
            content['references'].append(bcv_to_ref(ref,db_))
    db_.add_all(db_content)
    db_.expire_all()
    source_db_content.updatedUser = user_id
    response = {
        'db_content':db_content_dict,
        'source_content':source_db_content
        }
    return response

def update_bible_videos(db_: Session, source_name, videos, user_id=None):
    '''Update rows, that matches title in the bible videos table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.BIBLEVIDEO.value:
        raise TypeException('The operation is supported only on biblevideo')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in videos:
        row = db_.query(model_cls).filter(
            model_cls.title == utils.normalize_unicode(item.title.strip())).first()
        if not row:
            raise NotAvailableException("Bible Video row with title:%s, \
                not found for %s"%(
                    item.title, source_name))
        if item.references:
            row.refIds = bible_video_db_content_generate(item,db_)
        if item.series:
            row.series = utils.normalize_unicode(item.series.strip())
        if item.description:
            row.description = utils.normalize_unicode(item.description.strip())
        if item.active is not None:
            row.active = item.active
        if item.videoLink:
            row.videoLink = item.videoLink
        db_.flush()
        db_content.append(row)
    source_db_content.updatedUser = user_id
    db_content_dict = [item.__dict__ for item in db_content]
    for content in db_content_dict:
        content['references'] = []
        for ref in content['refIds']:
            content['references'].append(bcv_to_ref(ref,db_))
    response = {
        'db_content':db_content_dict,
        'source_content':source_db_content
        }
    return response
