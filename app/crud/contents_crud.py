''' Place to define all Database CRUD operations for content tables
bible, commentary, infographic, biblevideo, dictionary etc'''
import json
import re
from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import Session, defer, joinedload
from sqlalchemy.sql import text
import db_models
from crud import utils
from crud.nlp_sw_crud import update_job
from schema import schemas_nlp
from custom_exceptions import NotAvailableException, TypeException, AlreadyExistsException

def get_commentaries(db_:Session, *args,**kwargs):
    '''Fetches rows of commentries from the table specified by source_name'''
    source_name = args[0]
    book_code = args[1]
    chapter = args[2]
    verse = args[3]
    last_verse = args[4]
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith(db_models.ContentTypeName.COMMENTARY.value):
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if chapter is not None:
        query = query.filter(model_cls.chapter == chapter)
    if verse is not None:
        if last_verse is None:
            last_verse = verse
        query = query.filter(model_cls.verseStart <= verse, model_cls.verseEnd >= last_verse)
    query = query.filter(model_cls.active == active)
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    response = {
        'db_content':query.offset(skip).limit(limit).all(),
        'source_content':source_db_content}
    return response

def upload_commentaries(db_: Session, source_name, commentaries, job_id, user_id=None):#pylint: disable=too-many-locals,R1710
    '''Adds rows to the commentary table specified by source_name'''
    update_args = {
                    "status" : schemas_nlp.JobStatus.STARTED.value,
                    "startTime": datetime.now()}
    update_job(db_, job_id, user_id, update_args)

    update_args = {
                    "status" : schemas_nlp.JobStatus.ERROR.value,
                    "endTime": datetime.now(),
                    "output": {}}

    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if source_db_content.contentType.contentType != db_models.ContentTypeName.COMMENTARY.value:
        update_args["output"]= {
                "message": 'The operation is supported only on commentaries',
                "source_name": source_name,"data": None}
        update_job(db_, job_id, user_id, update_args)
        return None
        # raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    db_content_out = []
    prev_book_code = None
    for item in commentaries:
        if item.verseStart is not None and item.verseEnd is None:
            item.verseEnd = item.verseStart
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                update_args["output"]= {
                "message": 'Bible Book code, %s, not found in database'%prev_book_code,
                "source_name": source_name,"data": None}
                update_job(db_, job_id, user_id, update_args)
                return None
                # raise NotAvailableException('Bible Book code, %s, not found in database')
            exist_check = db_.query(model_cls).filter(
                model_cls.book_id == book.bookId, model_cls.chapter == item.chapter,
                model_cls.verseStart == item.verseStart, model_cls.verseEnd == item.verseEnd,
            ).first()
            if exist_check:
                update_args["output"]= {
                "message": 'Already exist commentary with same values for reference range',
                "book_id": book.bookId, "chapter":item.chapter, "verseStart" : item.verseStart,
                "verseEnd" : item.verseEnd, "data": None}
                update_job(db_, job_id, user_id, update_args)
                return None

        row = model_cls(
            book_id = book.bookId,
            chapter = item.chapter,
            verseStart = item.verseStart,
            verseEnd = item.verseEnd,
            commentary = utils.normalize_unicode(item.commentary),
            active=item.active)
        row_out = {
            "book" : {
                "bookId": book.bookId,
                "bookName": book.bookName,
                "bookCode": book.bookCode,},
            "chapter" :  item.chapter,
            "verseStart" :  item.verseStart,
            "verseEnd" :  item.verseEnd,
            "commentary" :  utils.normalize_unicode(item.commentary),
            "active": item.active}
        db_content.append(row)
        db_content_out.append(row_out)
    db_.add_all(db_content)
    db_.expire_all()
    source_db_content.updatedUser = user_id
    update_args = {
        "status" : schemas_nlp.JobStatus.FINISHED.value,
        "endTime": datetime.now(),
        "output": {"message": "Commentaries added successfully","data": db_content_out}}
    update_job(db_, job_id, user_id, update_args)

def update_commentaries(db_: Session, source_name, commentaries,job_id, user_id=None):#pylint: disable=R1710
    '''Update rows, that matches book, chapter and verse range fields in the commentary table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    update_args = {"status" : schemas_nlp.JobStatus.STARTED.value,
                    "startTime": datetime.now()}
    update_job(db_, job_id, user_id, update_args)
    update_args = {"status" : schemas_nlp.JobStatus.ERROR.value,
                    "endTime": datetime.now(),"output": {}}
    if source_db_content.contentType.contentType != db_models.ContentTypeName.COMMENTARY.value:
        update_args["output"]= {"message": 'The operation is supported only on commentaries',
                "source_name": source_name,"data": None}
        update_job(db_, job_id, user_id, update_args)
        return None
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    db_content_out = []
    prev_book_code = None
    for item in commentaries:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                update_args["output"]= {
                "message": 'Bible Book code, %s, not found in database'%prev_book_code,
                "source_name": source_name,"data": None}
                update_job(db_, job_id, user_id, update_args)
                return None
        row = db_.query(model_cls).filter(
            model_cls.book_id == book.bookId,
            model_cls.chapter == item.chapter,
            model_cls.verseStart == item.verseStart,
            model_cls.verseEnd == item.verseEnd).first()
        if not row:
            update_args["output"]= {
                "message" : "Commentary row with bookCode:"+
                    f"{item.bookCode},chapter:{item.chapter},verseStart:{item.verseStart},"+
                    f"verseEnd:{item.verseEnd}, not found for {source_name}",
                "source_name": source_name,"data": None}
            update_job(db_, job_id, user_id, update_args)
            return None
        if item.commentary:
            row.commentary = utils.normalize_unicode(item.commentary)
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
        row_out = {
            "book" : {
                "bookId": book.bookId,
                "bookName": book.bookName,
                "bookCode": book.bookCode,},
            "chapter" :  row.chapter,
            "verseStart" :  row.verseStart,
            "verseEnd" :  row.verseEnd,
            "commentary" :  row.commentary,
            "active": row.active}
        db_content_out.append(row_out)
    source_db_content.updatedUser = user_id
    update_args = {
        "status" : schemas_nlp.JobStatus.FINISHED.value,
        "endTime": datetime.now(),
        "output": {"message": "Commentaries updated successfully","data": db_content_out}}
    update_job(db_, job_id, user_id, update_args)

def get_dictionary_words(db_:Session, source_name,search_word =None, **kwargs):#pylint: disable=too-many-locals
    '''Fetches rows of dictionary from the table specified by source_name'''
    details = kwargs.get("details",None)
    exact_match = kwargs.get("exact_match",False)
    word_list_only = kwargs.get("word_list_only",False)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith(db_models.ContentTypeName.DICTIONARY.value):
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    if word_list_only:
        query = db_.query(model_cls.word)
    else:
        query = db_.query(model_cls)
    if search_word and exact_match:
        query = query.filter(model_cls.word == utils.normalize_unicode(search_word))
    elif search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', word || ' ' ||"+\
            "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    if details:
        det = json.loads(details)
        for key in det:
            query = query.filter(model_cls.details.op('->>')(key) == det[key])
    query = query.filter(model_cls.active == active)
    res = query.offset(skip).limit(limit).all()
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    response = {
        'db_content':res,
        'source_content':source_db_content }
    return response

def upload_dictionary_words(db_: Session, source_name, dictionary_words, user_id=None):
    '''Adds rows to the dictionary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.DICTIONARY.value:
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in dictionary_words:
        row = model_cls(
            word = utils.normalize_unicode(item.word),
            details = item.details,
            active = item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.expire_all()
    source_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'source_content':source_db_content
        }
    return response

def update_dictionary_words(db_: Session, source_name, dictionary_words, user_id=None):
    '''Update rows, that matches the word field in the dictionary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.DICTIONARY.value:
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in dictionary_words:
        row = db_.query(model_cls).filter(model_cls.word == item.word).first()
        if not row:
            raise NotAvailableException("Dictionary row with word:%s, not found for %s"%(
                    item.word, source_name))
        if item.details:
            row.details = item.details
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    source_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'source_content':source_db_content
        }
    return response

def get_infographics(db_:Session, source_name, book_code=None, title=None,**kwargs):
    '''Fetches rows of infographics from the table specified by source_name'''
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith(db_models.ContentTypeName.INFOGRAPHIC.value):
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if title:
        query = query.filter(model_cls.title == utils.normalize_unicode(title.strip()))
    query = query.filter(model_cls.active == active)
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    response = {
        'db_content':query.offset(skip).limit(limit).all(),
        'source_content':source_db_content
        }
    return response

def upload_infographics(db_: Session, source_name, infographics, user_id=None):
    '''Adds rows to the infographics table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.INFOGRAPHIC.value:
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in infographics:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database'
                    %item.bookCode)
        row = model_cls(
            book_id = book.bookId,
            title = utils.normalize_unicode(item.title.strip()),
            infographicLink = item.infographicLink,
            active=item.active)
        db_content.append(row)
    db_.add_all(db_content)
    # db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    # db_.commit()
    # return db_content
    response = {
        'db_content':db_content,
        'source_content':source_db_content
        }
    return response

def update_infographics(db_: Session, source_name, infographics, user_id=None):
    '''Update rows, that matches book, and title in the infographic table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.INFOGRAPHIC.value:
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in infographics:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database'
                    %item.bookCode)
        row = db_.query(model_cls).filter(
            model_cls.book_id == book.bookId,
            model_cls.title == utils.normalize_unicode(item.title.strip())).first()
        if not row:
            raise NotAvailableException("Infographics row with bookCode:%s, title:%s, \
                not found for %s"%(
                    item.bookCode, item.title, source_name))
        if item.infographicLink:
            row.infographicLink = item.infographicLink
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    source_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'source_content':source_db_content
        }
    return response

def ref_to_bcv(book,chapter,verse):
    '''convert reference to BCV format'''
    bbb = str(book).zfill(3)
    ccc = str(chapter).zfill(3)
    vvv = str(verse).zfill(3)
    return bbb + ccc + vvv

def bcv_to_ref(bcvref,db_):
    '''convert bcv to reference'''
    bbb = str(bcvref)[0:-6]
    book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookId == int(bbb)).first()
    ref = {
        "book": book.bookCode,
        "chapter": str(bcvref)[-6:-3],
        "verseNumber": str(bcvref)[-3:]
      }
    return ref

def bible_split_verse_completion(db_content2,split_indexs):
    """create split verse entry in db object"""
    post_script_list = []
    for indx in split_indexs:
        for char in db_content2[indx].metaData["tempcontent"]:
            post_script_list.append(char)
        post_script_list.sort()
        for char in post_script_list:
            db_content2[indx].verseText = \
                    db_content2[indx].verseText + ' '+ db_content2[indx].metaData\
                        ["tempcontent"][char]["verseText"]
            db_content2[indx].verseText=db_content2[indx].verseText.strip()
        db_content2[indx].metaData.pop("tempcontent")
        post_script_list = []
    return db_content2

def bible_verse_type_check(content, model_cls_2, book, db_content2, chapter_number,*args):#pylint: disable=too-many-locals
    """manage upload bible books verses based on verse type normal, merged
    verse or split verse"""
    split_indexs = args[0]
    normal_verse_pattern = re.compile(r'\d+$')
    split_verse_pattern = re.compile(r'(\d+)(\w+)$')
    merged_verse_pattern = re.compile(r'(\d+)-(\d+)$')
    metadata_field = {"publishedVersification":[]}
    #NormalVerseNumber Pattern
    if normal_verse_pattern.match(str(content['verseNumber'])):
        row_other = model_cls_2(
        book_id = book.bookId,
        chapter = chapter_number,
        verseNumber = content['verseNumber'],
        verseText = utils.normalize_unicode(content['verseText'].strip()))
        db_content2.append(row_other)
    #splitVerseNumber Pattern
    # combine split verses and use the whole number verseNumber
    elif split_verse_pattern.match(str(content['verseNumber'])):
        match_obj = split_verse_pattern.match(content['verseNumber'])
        post_script = match_obj.group(2)
        verse_number = match_obj.group(1)

        if not len(db_content2)==0 and book.bookId == db_content2[-1].book_id and\
            chapter_number == db_content2[-1].chapter\
            and verse_number == db_content2[-1].verseNumber:
            metadata_field['publishedVersification'].append(
                {"verseNumber": content["verseNumber"], "verseText":content["verseText"]})
            db_content2[-1].metaData['publishedVersification'].append(
                metadata_field['publishedVersification'][0])
            db_content2[-1].metaData['tempcontent'][post_script] = \
                {"verseText":utils.normalize_unicode(content['verseText'].strip()),
                "verseNumber":verse_number}
        else:
            #first time split verse
            split_indexs.append(len(db_content2)) if len(split_indexs) != 0\
                else split_indexs.append(0)#pylint: disable=expression-not-assigned
            metadata_field["tempcontent"] = {
                post_script:{"verseText":utils.normalize_unicode(content['verseText'].strip()),
                "verseNumber":verse_number}}
            metadata_field['publishedVersification'].append(
                {"verseNumber": content["verseNumber"], "verseText":content["verseText"]})
            row_other = model_cls_2(
            book_id = book.bookId,
            chapter = chapter_number,
            verseNumber = verse_number,
            verseText = '',
            metaData = metadata_field)
            db_content2.append(row_other)
    #mergedVerseNumber Pattern
    #keep the whole text in first verseNumber of merged verses
    elif merged_verse_pattern.match(str(content['verseNumber'])):
        match_obj = merged_verse_pattern.match(content['verseNumber'])
        verse_number = match_obj.group(1)
        verse_number_end = match_obj.group(2)
        metadata_field['publishedVersification'].append({"verseNumber":content['verseNumber'],
            "verseText":content['verseText']})
        row_other = model_cls_2(
            book_id = book.bookId,
            chapter = chapter_number,
            verseNumber = verse_number,
            verseText = utils.normalize_unicode(content['verseText'].strip()),
            metaData = metadata_field)
        db_content2.append(row_other)
        ## add empty text in the rest of the verseNumber range
        for versenum in range(int(verse_number)+1, int(verse_number_end)+1):
            row_other = model_cls_2(
                book_id = book.bookId,
                chapter = chapter_number,
                verseNumber = versenum,
                verseText = "",
                metaData = metadata_field)
            db_content2.append(row_other)
    else:
        raise TypeException(#pylint: disable=raising-format-tuple,too-many-function-args
            "Unrecognized pattern in %s chapter %s verse %s",
            book.bookName, chapter_number, content['verseNumber'])
    return db_content2, split_indexs

def upload_bible_books(db_: Session, source_name, books, user_id=None):#pylint: disable=too-many-locals
    '''Adds rows to the bible table and corresponding bible_cleaned specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.BIBLE.value:
        raise TypeException('The operation is supported only on bible')
    model_cls_2 = db_models.dynamicTables[source_name+'_cleaned']
    db_content = []
    db_content2 = []
    split_indexs = []
    for item in books:
        #checks for uploaded books
        book = upload_bible_books_checks(db_, item, source_name, db_content)
        if "chapters" not in item.JSON:
            raise TypeException("JSON is not of the required format")
        for chapter in item.JSON["chapters"]:
            if "chapterNumber" not in chapter or "contents" not in chapter:
                raise TypeException("JSON is not of the required format."+\
                    " Chapters should have chapterNumber and contents")
            try:
                chapter_number = int(chapter['chapterNumber'])
            except Exception as exe:
                raise TypeException("JSON is not of the required format."+\
                    " chapterNumber should be an interger") from exe
            for content in chapter['contents']:
                if 'verseNumber' in content:
                    if "verseText" not in content:
                        raise TypeException(
                            "JSON is not of the required format. verseText not found")
                    db_content2, split_indexs = \
                        bible_verse_type_check(content, model_cls_2,
                            book, db_content2, chapter_number,split_indexs)
    if len(split_indexs) > 0:
        db_content2 = bible_split_verse_completion(db_content2, split_indexs)

    db_.add_all(db_content)
    db_.add_all(db_content2)
    source_db_content.updatedUser = user_id
    # db_.commit()
    response = {
        'db_content':db_content,
        'source_content':source_db_content
    }
    return response

def upload_bible_books_checks(db_, item, source_name, db_content):
    """checks for uploaded bible books"""
    model_cls = db_models.dynamicTables[source_name]
    book_code = None
    if item.JSON is None:
        try:
            item.JSON = utils.parse_usfm(item.USFM)
        except Exception as exe:
            raise TypeException("USFM is not of the required format.") from exe
    elif item.USFM is None:
        try:
            item.USFM = utils.form_usfm(item.JSON)
        except Exception as exe:
            raise TypeException("Input JSON is not of the required format.") from exe
    try:
        book_code = item.JSON['book']['bookCode']
    except Exception as exe:
        raise TypeException("Input JSON is not of the required format.") from exe

    book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == book_code.lower() ).first()
    if not book:
        raise NotAvailableException('Bible Book code, %s, not found in database'
            %book_code)
    row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
    if row:
        if row.USFM:
            raise AlreadyExistsException("Bible book, %s, already present in DB"%book.bookCode)
        row.USFM = utils.normalize_unicode(item.USFM)
        row.JSON = item.JSON
        row.active = True
    else:
        row = model_cls(
            book_id=book.bookId,
            USFM=utils.normalize_unicode(item.USFM),
            JSON=item.JSON,
            active=True)
    db_.flush()
    db_content.append(row)
    return book

def update_bible_books(db_: Session, source_name, books, user_id=None):
    '''change values of bible books already uploaded'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != db_models.ContentTypeName.BIBLE.value:
        raise TypeException('The operation is supported only on bible')
    # update the bible table
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in books:
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
        if not row:
            raise NotAvailableException("Bible book, %s, not found in Database"%item.bookCode)
        if item.USFM:
            item.JSON = utils.parse_usfm(item.USFM)
            row.USFM = utils.normalize_unicode(item.USFM)
            row.JSON = item.JSON
        if item.JSON:
            item.USFM = utils.form_usfm(item.JSON)
            row.USFM = utils.normalize_unicode(item.USFM)
            row.JSON = item.JSON
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
        source_db_content = update_bible_books_cleaned\
            (db_,source_name,books,source_db_content,user_id)
        response = {
        'db_content':db_content,
        'source_content':source_db_content
        }
        # return db_content
        return response

def update_bible_books_cleaned(db_,source_name,books,source_db_content,user_id):
    """update bible cleaned table"""
    db_content2 = []
    split_indexs = []
    model_cls_2 = db_models.dynamicTables[source_name+'_cleaned']
    for item in books:
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        if item.USFM: # delete all verses and add them again
            db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).delete()
            for chapter in item.JSON['chapters']:
                chapter_number = int(chapter['chapterNumber'])
                for content in chapter['contents']:
                    if 'verseNumber' in content:
                        db_content2, split_indexs = \
                        bible_verse_type_check(content, model_cls_2,
                            book, db_content2, chapter_number,split_indexs)

        if item.active is not None: # set all the verse rows' active flag accordingly
            rows = db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).all()
            for row in rows:
                row.active = item.active
    if len(split_indexs) > 0:
        db_content2 = bible_split_verse_completion(db_content2, split_indexs)
    db_.add_all(db_content2)
    db_.flush()
    # db_.commit()
    # source_db_content.updatedUser = user_id
    source_db_content.updatedUser = user_id
    return source_db_content
    # db_.commit()

def upload_bible_audios(db_:Session, source_name, audios, user_id=None):
    '''Add audio bible related contents to _bible_audio table'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    model_cls_audio = db_models.dynamicTables[source_name+'_audio']
    model_cls_bible = db_models.dynamicTables[source_name]
    db_content = []
    db_content2 = []
    for item in audios:
        for buk in item.books:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == buk.strip().lower()).first()
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
            bible_table_row = db_.query(model_cls_bible).filter(
                model_cls_bible.book_id == book.bookId).first()
            if not bible_table_row:
                bible_table_row = model_cls_bible(
                    book_id=book.bookId
                    )
                db_content2.append(bible_table_row)
            row = model_cls_audio(
                name=utils.normalize_unicode(item.name.strip()),
                url=item.url.strip(),
                book_id=book.bookId,
                format=item.format.strip(),
                active=item.active)
            db_content.append(row)
    db_.add_all(db_content)
    db_.add_all(db_content2)
    source_db_content.updatedUser = user_id
    # db_.commit()
    response = {
        'db_content':db_content,
        'source_content':source_db_content
    }
    # return db_content
    return response

def update_bible_audios(db_: Session, source_name, audios, user_id=None):
    '''Update any details of a bible Auido row.
    Use name as row-identifier, which cannot be changed'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name+'_audio']
    db_content = []
    for item in audios:
        for buk in item.books:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == buk.strip().lower()).first()
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
            row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
            if not row:
                raise NotAvailableException("Bible audio for, %s, not found in database"%item.name)
            if item.name:
                row.name = utils.normalize_unicode(item.name.strip())
            if item.url:
                row.url = item.url.strip()
            if item.format:
                row.format = item.format.strip()
            if item.active is not None:
                row.active = item.active
            db_content.append(row)
    source_db_content.updatedUser = user_id
    # db_.commit()
    # return db_content
    response = {
        'db_content':db_content,
        'source_content':source_db_content
        }
    return response

def get_bible_versification(db_, source_name):
    '''select the reference list from bible_cleaned table'''
    model_cls = db_models.dynamicTables[source_name+"_cleaned"]
    query = db_.query(model_cls).prefix_with(
        "'"+source_name+"' as bible, ")
    query = query.options(defer(model_cls.verseText))
    query = query.order_by(model_cls.refId)
    versification = {"maxVerses":{}, "mappedVerses":{}, "excludedVerses":[], "partialVerses":{}}
    prev_book_code = None
    prev_chapter = 0
    prev_verse = 0
    for row in query.all():
        if row.book.bookCode != prev_book_code:
            if prev_book_code is not None:
                versification['maxVerses'][prev_book_code].append(prev_verse)
            versification['maxVerses'][row.book.bookCode] = []
            prev_book_code = row.book.bookCode
            prev_chapter = row.chapter
        elif row.chapter != prev_chapter:
            versification['maxVerses'][row.book.bookCode].append(prev_verse)
            if prev_chapter+1 != row.chapter:
                for chap in range(prev_chapter+1, row.chapter): #pylint: disable=unused-variable
                    versification['maxVerses'][row.book.bookCode].append(0)
            prev_chapter = row.chapter
        elif row.verseNumber != prev_verse + 1:
            for i in range(prev_verse+1, row.verseNumber):
                versification['excludedVerses'].append('%s %s:%s'%(prev_book_code, row.chapter, i))
        prev_verse = row.verseNumber
    if prev_book_code is not None:
        versification['maxVerses'][prev_book_code].append(prev_verse)
    # return versification
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    response = {
        'db_content':versification,
        'source_content':source_db_content
        }
    return response


def get_available_bible_books(db_, source_name, book_code=None, content_type=None,
    **kwargs):
    '''fetches the contents of .._bible table based of provided source_name and other options'''
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('_bible'):
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name]
    # model_cls_audio = db_models.dynamicTables[source_name+"_audio"]
    query = db_.query(model_cls).options(joinedload(model_cls.book))
    fetched = None
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if content_type == "usfm":
        query = query.options(defer(model_cls.JSON))
    elif content_type == "json":
        query = query.options(defer(model_cls.USFM))
    elif content_type == "all":
        query = query.options(joinedload(model_cls.audio)).filter(
            sqlalchemy.or_(model_cls.active == active, model_cls.audio.has(active=active)))
        fetched = query.offset(skip).limit(limit).all()
    elif content_type == "audio":
        query = query.options(joinedload(model_cls.audio),
            defer(model_cls.JSON), defer(model_cls.USFM)).filter(
            model_cls.audio.has(active=active))
        fetched = query.offset(skip).limit(limit).all()
    elif content_type is None:
        query = query.options(defer(model_cls.JSON), defer(model_cls.USFM))
    if not fetched:
        fetched = query.filter(model_cls.active == active).offset(skip).limit(limit).all()
    results = [res.__dict__ for res in fetched]
    # return results
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    response = {
        'db_content':results,
        'source_content':source_db_content
        }
    return response

def get_bible_verses(db_:Session, source_name, book_code=None, chapter=None, verse=None,#pylint: disable=too-many-locals
    **kwargs):
    '''queries the bible cleaned table for verses'''
    last_verse = kwargs.get("last_verse",None)
    search_phrase = kwargs.get("search_phrase",None)
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('_bible'):
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name+'_cleaned']
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if chapter:
        query = query.filter(model_cls.chapter == chapter)
    if verse:
        if not last_verse:
            last_verse = verse
        query = query.filter(model_cls.verseNumber >= verse, model_cls.verseNumber <= last_verse)
    if search_phrase:
        query = query.filter(model_cls.verseText.like(
            '%'+utils.normalize_unicode(search_phrase.strip())+"%"))
    results = query.filter(model_cls.active ==
        kwargs.get("active",True)).offset(kwargs.get("skip",0)).limit(kwargs.get("limit",100)).all()
    ref_combined_results = []
    for res in results:
        ref_combined = {}
        ref_combined['verseText'] = res.verseText
        ref_combined['metaData'] = res.metaData
        ref = { "bible": source_name,
                "book": res.book.bookCode,
                "chapter": res.chapter,
                "verseNumber":res.verseNumber}
        ref_combined['reference'] = ref
        ref_combined_results.append(ref_combined)
    # return ref_combined_results
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    response = {
        'db_content':ref_combined_results,
        'source_content':source_db_content
        }
    return response

def extract_text(db_:Session, tables, books, skip=0, limit=100):
    '''get all text field contents from the list of tables provided.
    The text column would be determined based on the table type'''
    sentence_list = []
    for table in tables:
        if table.contentType.contentType == db_models.ContentTypeName.BIBLE.value:
            model_cls = db_models.dynamicTables[table.sourceName+'_cleaned']
            query = db_.query(model_cls.refId.label('sentenceId'),
                model_cls.ref_string.label('surrogateId'),
                model_cls.verseText.label('sentence')).join(model_cls.book)
        elif table.contentType.contentType == db_models.ContentTypeName.COMMENTARY.value:
            model_cls = db_models.dynamicTables[table.sourceName]
            query = db_.query(model_cls.commentaryId.label('sentenceId'),
                model_cls.ref_string.label('surrogateId'),
                model_cls.commentary.label('sentence')).join(model_cls.book)
        else:
            continue
        if books is not None:
            query = query.filter(
                db_models.BibleBook.bookCode.in_([buk.lower() for buk in books]))
        sentence_list += query.offset(skip).limit(limit).all()
        if len(sentence_list) >= limit:
            sentence_list = sentence_list[:limit]
            break
    return sentence_list
