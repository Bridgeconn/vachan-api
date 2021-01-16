''' Defines SQL Alchemy models for each Database Table'''

from sqlalchemy import Column, Integer, String, JSON, ARRAY
from sqlalchemy import Boolean, ForeignKey, DateTime
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declared_attr

from database import Base
from custom_exceptions import GenericException

class ContentType(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table content_types in vachan DB(postgres)'''
    __tablename__ = "content_types"

    contentId = Column('content_type_id', Integer, primary_key=True)
    contentType = Column('content_type', String, unique=True)

class Language(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table languages in vachan DB(postgres)'''
    __tablename__ = 'languages'

    languageId = Column('language_id', Integer, primary_key=True)
    code = Column('language_code', String, unique=True, index=True)
    language = Column('language_name', String)
    scriptDirection = Column('script_direction', String)

class Version(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table versions in vachan DB(postgres)'''
    __tablename__ = 'versions'

    versionId = Column('version_id', Integer, primary_key=True)
    versionAbbreviation = Column('version_code', String, unique=True, index=True)
    versionName = Column('version_description', String)
    revision = Column('revision', Integer)
    metaData = Column('metadata', JSON)

class Source(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table sources in vachan DB(postgres)'''
    __tablename__ = 'sources'

    sourceId = Column('source_id', Integer, primary_key=True)
    sourceName = Column('table_name', String, unique=True)
    year = Column('year', Integer)
    license = Column('license', String)
    contentId = Column('content_id', Integer, ForeignKey('content_types.content_type_id'))
    contentType = relationship('ContentType')
    languageId = Column('language_id', Integer, ForeignKey('languages.language_id'))
    language = relationship('Language')
    versionId = Column('version_id', Integer, ForeignKey('versions.version_id'))
    version = relationship('Version')
    active = Column('active', Boolean)
    metaData = Column('metadata', JSON)
    createdUser = Column('created_user', Integer)
    updatedUser = Column('last_updated_user', Integer)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class BibleBook(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table bible_books_look_up in vachan DB(postgres)'''
    __tablename__ = 'bible_books_look_up'

    bookId = Column('book_id', Integer, primary_key=True)
    bookName = Column('book_name', String)
    bookCode = Column('book_code', String)

class Commentary(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created commentary tables in vachan Db(postgres)'''
    commentaryId = Column('commentary_id', Integer, primary_key=True, autoincrement=True)
    @declared_attr
    def book_id(cls): # pylint: disable=E0213
        '''For modelling the bookId field in derived classes'''
        return Column('book_id', Integer, ForeignKey('bible_books_look_up.book_id'))
    @declared_attr
    def book(cls): # pylint: disable=E0213
        '''For modelling the book field in derived classes'''
        return relationship(BibleBook)
    chapter = Column('chapter', Integer)
    verseStart = Column('verse_start', Integer)
    verseEnd = Column('verse_end', Integer)
    commentary = Column('commentary', String)
    active = Column('active', Boolean)
    __table_args__ = (
        UniqueConstraint('book_id', 'chapter', 'verse_start', 'verse_end'),
        {'extend_existing': True}
                     )

class Dictionary(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created dictionary tables in vachan Db(postgres)'''
    wordId = Column('word_id', Integer, primary_key=True, autoincrement=True)
    word = Column('word', String, unique=True)
    details = Column('details', JSON)
    active = Column('active', Boolean)
    __table_args__ = {'extend_existing': True}

class Infographic(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created infographics tables in vachan Db(postgres)'''
    infographicId = Column('infographic_id', Integer, primary_key=True, autoincrement=True)
    @declared_attr
    def book_id(cls): # pylint: disable=E0213
        '''For modelling the bookId field in derived classes'''
        return Column('book_id', Integer, ForeignKey('bible_books_look_up.book_id'))
    @declared_attr
    def book(cls): # pylint: disable=E0213
        '''For modelling the book field in derived classes'''
        return relationship(BibleBook)
    title = Column('title', String)
    infographicLink = Column('infographic_url', String)
    active = Column('active', Boolean)
    __table_args__ = (
        UniqueConstraint('book_id', 'title'),
        {'extend_existing': True}
                     )

class BibleVideo(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible videos tables in vachan Db(postgres)'''
    bibleVideoId  = Column('bible_video_id', Integer, primary_key=True, autoincrement=True)
    title = Column('title', String, unique=True)
    theme = Column('theme', String)
    description = Column('description', String)
    videoLink = Column('video_link', String)
    active = Column('active', Boolean)
    books = Column('books', ARRAY(String))
    __table_args__ = {'extend_existing': True}

class BibleAudio(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible_audio tables in vachan Db(postgres)'''
    audioId  = Column('bible_audio_id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    @declared_attr
    def book_id(self):
        table_name = self.__tablename__.replace("_audio", "")
        return Column('book_id', Integer, ForeignKey(table_name+'.book_id'), unique=True)
    url = Column('audio_link', String)
    format = Column('audio_format', String)
    active = Column('active', Boolean, default=True)
    __table_args__ = {'extend_existing': True}

class BibleContent(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible tables in vachan Db(postgres)'''
    bookContentId  = Column('bible_content_id', Integer, primary_key=True, autoincrement=True)
    @declared_attr
    def book_id(cls): # pylint: disable=E0213
        '''For modelling the bookId field in bible content classes'''
        return Column('book_id', Integer, ForeignKey('bible_books_look_up.book_id'), unique=True)
    @declared_attr
    def book(cls): # pylint: disable=E0213
        '''For modelling the book field in bible content classes'''
        return relationship(BibleBook, uselist=False)
    USFM = Column('usfm', String)
    JSON = Column('json_object', JSON)
    @declared_attr
    def audio(self): # pylint: disable=E0213
        '''For modelling the audio field in bible content classes'''
        refering_table = self.__tablename__+"_audio"
        return relationship(dynamicTables[refering_table], uselist=False)
    active = Column('active', Boolean, default=True)
    __table_args__ = {'extend_existing': True}

def createRefId(context):
    bbb = str(context.get_current_parameters()['book_id']).zfill(3)
    ccc = str(context.get_current_parameters()['chapter']).zfill(3)
    vvv = str(context.get_current_parameters()['verse_number']).zfill(3)
    return bbb + ccc + vvv

class BibleContentCleaned(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible_cleaned tables in vachan Db(postgres)'''
    refId  = Column('ref_id', Integer, primary_key=True, default=createRefId)
    @declared_attr
    def book_id(cls): # pylint: disable=E0213
        '''For modelling the bookId field in bible content classes'''
        return Column('book_id', Integer, ForeignKey('bible_books_look_up.book_id'))
    @declared_attr
    def book(cls): # pylint: disable=E0213
        '''For modelling the book field in bible content classes'''
        return relationship(BibleBook)
    chapter = Column('chapter', Integer)
    verseNumber = Column('verse_number', Integer)
    verseText = Column('verse_text', String)
    # footNote = Column('footnote', String)
    # crossReference = Column('cross_reference')
    active = Column('active', Boolean, default=True)
    __table_args__ = (
        UniqueConstraint('book_id', 'chapter', 'verse_number'),
        {'extend_existing': True}
                     )

dynamicTables = {}
def create_dynamic_table(source_name, content_type):
    '''To map or create one dynamic table based on the content Type'''
    if content_type == 'bible':
        dynamicTables[source_name+'_audio'] = type(
            source_name+'_audio',(BibleAudio, Base,),
            {"__tablename__": source_name+'_audio'})
        dynamicTables[source_name] = type(
            source_name,(BibleContent, Base,),
            {"__tablename__": source_name})
        dynamicTables[source_name+'_cleaned'] = type(
            source_name+'_cleaned',(BibleContentCleaned, Base,),
            {"__tablename__": source_name+'_cleaned'})
    elif content_type == 'commentary':
        dynamicTables[source_name] = type(
            source_name,(Commentary, Base,),{"__tablename__": source_name})
    elif content_type == 'dictionary':
        dynamicTables[source_name] = type(
            source_name,(Dictionary, Base,),{"__tablename__": source_name})
    elif content_type == 'infographics':
        dynamicTables[source_name] = type(
            source_name,(Infographic, Base,),{"__tablename__": source_name})
    elif content_type == 'bible_video':
        dynamicTables[source_name] = type(
            source_name,(BibleVideo, Base,),{"__tablename__": source_name})
    else:
        raise GenericException("Table structure not defined for this content type:%s"
            %content_type)


def map_all_dynamic_tables(db_: Session):
    '''Fetches list of dynamic tables from sources table
    and maps them according to their content types'''

    all_src = db_.query(Source).all()
    for src in all_src:
        create_dynamic_table(src.sourceName, src.contentType.contentType)
