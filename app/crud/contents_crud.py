''' Place to define all Database CRUD operations for content tables
bible, commentary, infographic, biblevideo, dictionary etc'''

import json
import sqlalchemy
from sqlalchemy.orm import Session, defer, joinedload

import db_models
from custom_exceptions import NotAvailableException, TypeException, AlreadyExistsException

def get_commentaries(db_:Session, source_name, book_code=None, chapter=None, #pylint: disable=too-many-arguments
    verse=None, last_verse=None, active=True, skip=0, limit=100):
    '''Fetches rows of commentries from the table specified by source_name'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('commentary'):
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
    return query.offset(skip).limit(limit).all()

def upload_commentaries(db_: Session, source_name, commentaries, user_id=None):
    '''Adds rows to the commentary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'commentary':
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in commentaries:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
        if item.verseStart is not None and item.verseEnd is None:
            item.verseEnd = item.verseStart
        row = model_cls(
            book_id = book.bookId,
            chapter = item.chapter,
            verseStart = item.verseStart,
            verseEnd = item.verseEnd,
            commentary = item.commentary,
            active=item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_commentaries(db_: Session, source_name, commentaries, user_id=None):
    '''Update rows, that matches book, chapter and verse range fields in the commentary table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'commentary':
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    prev_book_code = None
    for item in commentaries:
        if item.bookCode != prev_book_code:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
            prev_book_code = item.bookCode
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database')
        row = db_.query(model_cls).filter(
            model_cls.book_id == book.bookId,
            model_cls.chapter == item.chapter,
            model_cls.verseStart == item.verseStart,
            model_cls.verseEnd == item.verseEnd).first()
        if not row:
            raise NotAvailableException("Commentary row with bookCode:%s, chapter:%s, \
                verseStart:%s, verseEnd:%s, not found for %s"%(
                    item.bookCode, item.chapter, item.verseStart, item.verseEnd, source_name))
        if item.commentary:
            row.commentary = item.commentary
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def get_dictionary_words(db_:Session, source_name, search_word = None, details = None,  #pylint: disable=too-many-arguments
    exact_match=False, word_list_only=False, active=True, skip=0, limit=100):
    '''Fetches rows of dictionary from the table specified by source_name'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('dictionary'):
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    if word_list_only:
        query = db_.query(model_cls.word)
    else:
        query = db_.query(model_cls)
    if search_word and exact_match:
        query = query.filter(model_cls.word == search_word)
    elif search_word:
        query = query.filter(model_cls.word.like(search_word+"%"))
    if details:
        det = json.loads(details)
        for key in det:
            query = query.filter(model_cls.details.op('->>')(key) == det[key])
    query = query.filter(model_cls.active == active)
    res = query.offset(skip).limit(limit).all()
    return res

def upload_dictionary_words(db_: Session, source_name, dictionary_words, user_id=None):
    '''Adds rows to the dictionary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'dictionary':
        raise TypeException('The operation is supported only on dictionaries')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in dictionary_words:
        row = model_cls(
            word = item.word,
            details = item.details,
            active = item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_dictionary_words(db_: Session, source_name, dictionary_words, user_id=None):
    '''Update rows, that matches the word field in the dictionary table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'dictionary':
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
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def get_infographics(db_:Session, source_name, book_code=None, title=None, #pylint: disable=too-many-arguments
    active=True, skip=0, limit=100):
    '''Fetches rows of infographics from the table specified by source_name'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('infographic'):
        raise TypeException('The operation is supported only on infographics')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if title:
        query = query.filter(model_cls.title == title.strip())
    query = query.filter(model_cls.active == active)
    return query.offset(skip).limit(limit).all()

def upload_infographics(db_: Session, source_name, infographics, user_id=None):
    '''Adds rows to the infographics table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'infographic':
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
            title = item.title.strip(),
            infographicLink = item.infographicLink,
            active=item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_infographics(db_: Session, source_name, infographics, user_id=None):
    '''Update rows, that matches book, and title in the infographic table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'infographic':
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
            model_cls.title == item.title.strip()).first()
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
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def get_bible_videos(db_:Session, source_name, book_code=None, title=None, theme=None, active=True, #pylint: disable=too-many-arguments
    skip=0, limit=100):
    '''fetches rows of bible videos as per provided source_name and filters'''
    if source_name not in db_models.dynamicTables:
        raise NotAvailableException('%s not found in database.'%source_name)
    if not source_name.endswith('biblevideo'):
        raise TypeException('The operation is supported only on biblevideo')
    model_cls = db_models.dynamicTables[source_name]
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.books.any(book_code.lower()))
    if title:
        query = query.filter(model_cls.title == title.strip())
    if theme:
        query = query.filter(model_cls.theme == theme.strip())
    query = query.filter(model_cls.active == active)
    return query.offset(skip).limit(limit).all()



def upload_bible_videos(db_: Session, source_name, videos, user_id=None):
    '''Adds rows to the bible videos table specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'biblevideo':
        raise TypeException('The operation is supported only on biblevideo')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in videos:
        for book_code in item.books:
            # verifying if the book codes are valid as we dont use FK for this field
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == book_code.lower() ).first()
            if not book:
                raise NotAvailableException('Bible Book code, %s, not found in database'%book_code)
        row = model_cls(
            title = item.title.strip(),
            theme = item.theme.strip(),
            description = item.description.strip(),
            active = item.active,
            books = item.books,
            videoLink = item.videoLink)
        db_content.append(row)
    db_.add_all(db_content)
    db_.commit()
    db_.expire_all()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content


def update_bible_videos(db_: Session, source_name, videos, user_id=None):
    '''Update rows, that matches title in the bible videos table
    specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'biblevideo':
        raise TypeException('The operation is supported only on biblevideo')
    model_cls = db_models.dynamicTables[source_name]
    db_content = []
    for item in videos:
        row = db_.query(model_cls).filter(model_cls.title == item.title.strip()).first()
        if not row:
            raise NotAvailableException("Bible Video row with title:%s, \
                not found for %s"%(
                    item.title, source_name))
        if item.books:
            for book_code in item.books:
                # verifying if the book codes are valid as we dont use FK for this field
                book = db_.query(db_models.BibleBook).filter(
                    db_models.BibleBook.bookCode == book_code.lower() ).first()
                if not book:
                    raise NotAvailableException('Bible Book code, %s, not found in database'
                        %book_code )
            row.books = item.books
        if item.theme:
            row.theme = item.theme.strip()
        if item.description:
            row.description = item.description.strip()
        if item.active is not None:
            row.active = item.active
        if item.videoLink:
            row.videoLink = item.videoLink
        db_.flush()
        db_content.append(row)
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    db_.refresh(source_db_content)
    return db_content

def upload_bible_books(db_: Session, source_name, books, user_id=None): #pylint: disable=too-many-branches, disable=too-many-locals
    '''Adds rows to the bible table and corresponding bible_cleaned specified by source_name'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[source_name]
    model_cls_2 = db_models.dynamicTables[source_name+'_cleaned']
    db_content = []
    db_content2 = []
    for item in books:
        try:
            book_code = item.JSON['book']['bookCode']
        except Exception as exe:
            raise TypeException("JSON is not of the required format."+\
                " book.bookCode should be present") from exe
        book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == book_code.lower() ).first()
        if not book:
            raise NotAvailableException('Bible Book code, %s, not found in database'
                %book_code)
        row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
        if row:
            if row.USFM:
                raise AlreadyExistsException("Bible book, %s, already present in DB"%book.bookCode)
            row.USFM = item.USFM
            row.JSON = item.JSON
            row.active = True
        else:
            row = model_cls(
                book_id=book.bookId,
                USFM=item.USFM,
                JSON=item.JSON,
                active=True)
        db_.flush()
        db_content.append(row)
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
                    row_other = model_cls_2(
                        book_id = book.bookId,
                        chapter = chapter_number,
                        verseNumber = content['verseNumber'],
                        verseText = content['verseText'].strip())
                    db_content2.append(row_other)
    db_.add_all(db_content)
    db_.add_all(db_content2)
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

def update_bible_books(db_: Session, source_name, books, user_id=None): #pylint: disable=too-many-locals, disable=too-many-branches
    '''change values of bible books already uploaded'''
    source_db_content = db_.query(db_models.Source).filter(
        db_models.Source.sourceName == source_name).first()
    if not source_db_content:
        raise NotAvailableException('Source %s, not found in database'%source_name)
    if source_db_content.contentType.contentType != 'bible':
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
            row.USFM = item.USFM
            row.JSON = item.JSON
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    # update bible cleaned table
    db_content2 = []
    model_cls_2 = db_models.dynamicTables[source_name+'_cleaned']
    for item in books:
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        if item.USFM: # delete all verses and add them again
            db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).delete()
            for chapter in item.JSON["chapters"]:
                chapter_number = int(chapter['chapterNumber'])
                for content in chapter['contents']:
                    if 'verseNumber' in content:
                        row_other = model_cls_2(
                            book_id = book.bookId,
                            chapter = chapter_number,
                            verseNumber = content['verseNumber'],
                            verseText = content['verseText'].strip())
                        db_content2.append(row_other)
            db_.add_all(db_content2)
            db_.flush()
        if item.active is not None: # set all the verse rows' active flag accordingly
            rows = db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).all()
            for row in rows:
                row.active = item.active
    db_.commit()
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content


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
                name=item.name.strip(),
                url=item.url.strip(),
                book_id=book.bookId,
                format=item.format.strip(),
                active=item.active)
            db_content.append(row)
    db_.add_all(db_content)
    db_.add_all(db_content2)
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content

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
                row.name = item.name.strip()
            if item.url:
                row.url = item.url.strip()
            if item.format:
                row.format = item.format.strip()
            if item.active is not None:
                row.active = item.active
            db_content.append(row)
    source_db_content.updatedUser = user_id
    db_.commit()
    return db_content



def get_bible_versification(db_, source_name, book_code, active=True):
    '''select the reference list from bible_cleaned table'''
    model_cls = db_models.dynamicTables[source_name+"_cleaned"]
    query = db_.query(model_cls).prefix_with(
        "'"+source_name+"' as bible, ")
    query = query.options(defer(model_cls.verseText))
    query = query.filter(model_cls.book.has(bookCode = book_code.lower()),
        model_cls.active == active )
    res_list = []
    for res in query.all():
        res = res.__dict__
        res['bible'] = source_name
        res['book'] = book_code
        res_list.append(res)
    return res_list


def get_available_bible_books(db_, source_name, book_code=None, content_type=None, #pylint: disable=too-many-arguments, disable=too-many-locals
    versification=False, active=True, skip=0, limit=100):
    '''fetches the contents of .._bible table based of provided source_name and other options'''
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
    if versification:
        added_results = []
        for res in results:
            ref_list = get_bible_versification(db_, source_name, res["book"].bookCode, active)
            added_res = res
            added_res['versification'] = ref_list
            added_results.append(added_res)
        return added_results
    return results


def get_bible_verses(db_:Session, source_name, book_code=None, chapter=None, verse=None, #pylint: disable=too-many-locals, disable=too-many-arguments
    last_verse=None, search_phrase=None, active=True, skip=0, limit=100):
    '''queries the bible cleaned table for verses'''
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
        query = query.filter(model_cls.verseText.like('%'+search_phrase.strip()+"%"))
    results = query.filter(model_cls.active == active).offset(skip).limit(limit).all()
    ref_combined_results = []
    for res in results:
        ref_combined = {}
        ref_combined['verseText'] = res.verseText
        ref = { "bible": source_name,
                "book": res.book.bookCode,
                "chapter": res.chapter,
                "verseNumber":res.verseNumber}
        ref_combined['reference'] = ref
        ref_combined_results.append(ref_combined)
    return ref_combined_results
