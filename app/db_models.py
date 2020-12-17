''' Defines SQL Alchemy models for each Database Table'''

from sqlalchemy import Column, Integer, String, JSON
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
    __table_args__ = (
        UniqueConstraint('book_id', 'chapter', 'verse_start', 'verse_end',
            name='unique_reference_range'),
                     )
    __table_args__ = {'extend_existing': True}

dynamicTables = {}
def create_dynamic_table(source_name, content_type):
    '''To map or create one dynamic table based on the content Type'''
    if content_type == 'commentary':
        dynamicTables[source_name] = type(
            source_name,(Commentary, Base,),{"__tablename__": source_name})
    else:
        raise GenericException("Table structure not defined for this content type")


def map_all_dynamic_tables(db_: Session):
    '''Fetches list of dynamic tables from sources table
    and maps them according to their content types'''

    all_src = db_.query(Source).all()
    for src in all_src:
        create_dynamic_table(src.sourceName, src.contentType.contentType)
