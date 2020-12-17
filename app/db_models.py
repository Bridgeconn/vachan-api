''' Defines SQL Alchemy models for each Database Table'''

from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


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
    UpdatedUser = Column('last_updated_user', Integer)

class BibleBook(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table bible_books_look_up in vachan DB(postgres)'''
    __tablename__ = 'bible_books_look_up'

    bookId = Column('book_id', Integer, primary_key=True)
    bookName = Column('book_name', String)
    bookCode = Column('book_code', String)
