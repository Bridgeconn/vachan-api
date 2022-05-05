''' Defines SQL Alchemy models for each Database Table'''

from enum import Enum
from sqlalchemy import Column, Integer, String, JSON, ARRAY, Float, text
from sqlalchemy import Boolean, ForeignKey, DateTime
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property

from database import Base
from custom_exceptions import GenericException

dynamicTables = {}

class ContentTypeName(Enum):
    '''The string literals used as value of ContentType field in ContentType
    and also used to as the ending of respective database table names'''
    BIBLE = "bible"
    COMMENTARY = "commentary"
    INFOGRAPHIC = "infographic"
    BIBLEVIDEO = "biblevideo"
    DICTIONARY = "dictionary"
    GITLABREPO = "gitlabrepo"

class TranslationDocumentType(Enum):
    '''Currently supports bible USFM only. Can be extended to
    CSV(for commentary or notes), doc(stories, other passages) etc.'''
    USFM = 'Bible USFM'

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
    metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())


class License(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table licenses in vachan DB(postgres)'''
    __tablename__ = 'licenses'

    licenseId = Column('license_id', Integer, primary_key=True)
    code = Column('license_code', String, unique=True, index=True)
    name = Column('license_name', String)
    license = Column('license_text', String)
    permissions = Column('permissions', ARRAY(String))
    active = Column('active', Boolean)
    # metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class Version(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table versions in vachan DB(postgres)'''
    __tablename__ = 'versions'

    versionId = Column('version_id', Integer, primary_key=True)
    versionAbbreviation = Column('version_code', String, unique=True, index=True)
    versionName = Column('version_description', String)
    revision = Column('revision', Integer)
    metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class Source(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table sources in vachan DB(postgres)'''
    __tablename__ = 'sources'

    sourceId = Column('source_id', Integer, primary_key=True)
    sourceName = Column('source_name', String, unique=True)
    tableName = Column('source_table', String, unique=True)
    year = Column('year', Integer)
    licenseId = Column('license_id', Integer, ForeignKey('licenses.license_id'))
    license = relationship(License)
    contentId = Column('content_id', Integer, ForeignKey('content_types.content_type_id'))
    contentType = relationship('ContentType')
    languageId = Column('language_id', Integer, ForeignKey('languages.language_id'))
    language = relationship('Language')
    versionId = Column('version_id', Integer, ForeignKey('versions.version_id'))
    version = relationship('Version')
    active = Column('active', Boolean)
    metaData = Column('metadata', JSONB)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class BibleBook(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table bible_books_look_up in vachan DB(postgres)'''
    __tablename__ = 'bible_books_look_up'

    bookId = Column('book_id', Integer, primary_key=True)
    bookName = Column('book_name', String)
    bookCode = Column('book_code', String)

class Commentary(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created commentary tables in vachan Db(postgres)'''
    commentaryId = Column('commentary_id', Integer,
        Sequence('commentary_id_seq', start=100001, increment=1), primary_key=True)
    @declared_attr
    def book_id(cls): # pylint: disable=E0213
        '''For modelling the bookId field in derived classes'''
        return Column('book_id', Integer, ForeignKey('bible_books_look_up.book_id'))
    @declared_attr
    def book(cls): # pylint: disable=E0213
        '''For modelling the book field in derived classes'''
        return relationship(BibleBook)
    @hybrid_property
    def ref_string(self):
        '''To compose surrogate id'''
        return f'{self.book.bookCode} {self.chapter}:{self.verseStart}-{self.verseEnd}'
    @ref_string.expression
    def ref_string(cls): # pylint: disable=E0213
        '''To compose surrogate id'''
        return func.concat(BibleBook.bookCode," ",cls.chapter,":",cls.verseStart,"-",cls.verseEnd)
    chapter = Column('chapter', Integer)
    verseStart = Column('verse_start', Integer)
    verseEnd = Column('verse_end', Integer)
    commentary = Column('commentary', String)
    active = Column('active', Boolean)
    # __table_args__ = (
    #     UniqueConstraint('book_id', 'chapter', 'verse_start', 'verse_end'),
    #     {'extend_existing': True}
    #                  )

class Dictionary(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created dictionary tables in vachan Db(postgres)'''
    wordId = Column('word_id', Integer,
        Sequence('word_id_seq', start=100001, increment=1), primary_key=True)
    word = Column('word', String, unique=True)
    details = Column('details', JSONB)
    active = Column('active', Boolean)

    __table_args__ = (
        {'extend_existing': True},
                     )

class Infographic(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created infographics tables in vachan Db(postgres)'''
    infographicId = Column('infographic_id', Integer,
        Sequence('infographic_id_seq', start=100001, increment=1), primary_key=True)
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
    bibleVideoId  = Column('biblevideo_id', Integer,
        Sequence('biblevideo_id_seq', start=100001, increment=1), primary_key=True)
    refIds  = Column('ref_ids', ARRAY(Integer))
    title = Column('title', String, unique=True)
    series = Column('series', String)
    description = Column('description', String)
    videoLink = Column('video_link', String)
    active = Column('active', Boolean)
    __table_args__ = {'extend_existing': True}

class BibleAudio(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible_audio tables in vachan Db(postgres)'''
    audioId  = Column('bible_audio_id', Integer,
        Sequence('bible_audio_id_seq', start=100001, increment=1), primary_key=True)
    name = Column('name', String)
    @declared_attr
    def book_id(self):
        '''FK column referncing bible contents'''
        table_name = self.__tablename__.replace("_audio", "") #pylint: disable=E1101
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
        refering_table = self.__tablename__+"_audio" #pylint: disable=E1101
        # return relationship(dynamicTables[refering_table], uselist=False)
        return relationship(refering_table, uselist=False)
    active = Column('active', Boolean, default=True)
    __table_args__ = {'extend_existing': True}

def create_ref_id(context):
    '''generate refid value'''
    bbb = str(context.get_current_parameters()['book_id']).zfill(3)
    ccc = str(context.get_current_parameters()['chapter']).zfill(3)
    vvv = str(context.get_current_parameters()['verse_number']).zfill(3)
    return bbb + ccc + vvv

class BibleContentCleaned(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible_cleaned tables in vachan Db(postgres)'''
    refId  = Column('ref_id', Integer, primary_key=True, default=create_ref_id)
    @declared_attr
    def book_id(cls): # pylint: disable=E0213
        '''For modelling the bookId field in bible content classes'''
        return Column('book_id', Integer, ForeignKey('bible_books_look_up.book_id'))
    @declared_attr
    def book(cls): # pylint: disable=E0213
        '''For modelling the book field in bible content classes'''
        return relationship(BibleBook)
    @hybrid_property
    def ref_string(self):
        '''To compose surrogate id'''
        return f'{self.book.bookCode} {self.chapter}:{self.verseNumber}'

    @ref_string.expression
    def ref_string(cls): # pylint: disable=E0213
        '''To compose surrogate id'''
        return func.concat(BibleBook.bookCode," ",cls.chapter,":",cls.verseNumber)
    chapter = Column('chapter', Integer)
    verseNumber = Column('verse_number', Integer)
    verseText = Column('verse_text', String)
    # footNote = Column('footnote', String)
    # crossReference = Column('cross_reference')
    active = Column('active', Boolean, default=True)
    metaData = Column('metadata', JSONB)
    __table_args__ = (
        UniqueConstraint('book_id', 'chapter', 'verse_number'),
        {'extend_existing': True}
                     )

def create_dynamic_table(source_name, table_name, content_type):
    '''To map or create one dynamic table based on the content Type'''
    if content_type == ContentTypeName.BIBLE.value:
        dynamicTables[source_name+'_audio'] = type(
            table_name+'_audio',(BibleAudio, Base,),
            {"__tablename__": table_name+'_audio'})
        dynamicTables[source_name] = type(
            table_name,(BibleContent, Base,),
            {"__tablename__": table_name})
        dynamicTables[source_name+'_cleaned'] = type(
            table_name+'_cleaned',(BibleContentCleaned, Base,),
            {"__tablename__": table_name+'_cleaned'})
    elif content_type == ContentTypeName.COMMENTARY.value:
        dynamicTables[source_name] = type(
            table_name,(Commentary, Base,),{"__tablename__": table_name})
    elif content_type == ContentTypeName.DICTIONARY.value:
        dynamicTables[source_name] = type(
            table_name,(Dictionary, Base,),{"__tablename__": table_name})
        new_index = Index(table_name+'_word_details_ix',  # pylint: disable=W0612
            text("to_tsvector('simple', word || ' ' ||"+\
            "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"),
            postgresql_using="gin",
            )
    elif content_type == ContentTypeName.INFOGRAPHIC.value:
        dynamicTables[source_name] = type(
            table_name,(Infographic, Base,),{"__tablename__": table_name})
    elif content_type == ContentTypeName.BIBLEVIDEO.value:
        dynamicTables[source_name] = type(
            table_name,(BibleVideo, Base,),{"__tablename__": table_name})
    elif content_type == ContentTypeName.GITLABREPO.value:
        pass
    else:
        raise GenericException("Table structure not defined for this content type:%s"
            %content_type)


def map_all_dynamic_tables(db_: Session):
    '''Fetches list of dynamic tables from sources table
    and maps them according to their content types'''

    all_src = db_.query(Source).all()
    for src in all_src:
        create_dynamic_table(src.sourceName, src.tableName, src.contentType.contentType)


############ Translation Tables ##########

class TranslationProject(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table translation_projects in vachan DB used by Autographa MT mode'''
    __tablename__ = 'translation_projects'

    projectId = Column('project_id', Integer, primary_key=True, autoincrement=True)
    projectName = Column('project_name', String, index=True)
    @declared_attr
    def source_lang_id(cls): # pylint: disable=E0213
        '''For modelling the sourceLanguage field in this class'''
        return Column('source_lang_id', Integer, ForeignKey('languages.language_id'))
    @declared_attr
    def sourceLanguage(cls): # pylint: disable=E0213, disable=C0103
        '''For modelling the sourceLanguage field in this class'''
        return relationship(Language, foreign_keys=cls.source_lang_id, uselist=False)
    @declared_attr
    def target_lang_id(cls): # pylint: disable=E0213
        '''For modelling the targetLanguage field in this class'''
        return Column('target_lang_id', Integer, ForeignKey('languages.language_id'))
    @declared_attr
    def targetLanguage(cls): # pylint: disable=E0213, disable=C0103
        '''For modelling the targetLanguage field in this class'''
        return relationship(Language, foreign_keys=cls.target_lang_id, uselist=False)
    @declared_attr
    def users(cls):# pylint: disable=E0213
        '''For modelling project users from translation_project_users'''
        return relationship('TranslationProjectUser', uselist=True,
            back_populates='project')
    documentFormat = Column('source_document_format', String)
    metaData = Column('metadata', JSON)
    active = Column('active', Boolean, default=True)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class TranslationDraft(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table translation_drafts in vachan DB used by Autographa MT mode'''
    __tablename__ = 'translation_sentences'

    draftId = Column('draft_id', Integer, primary_key=True, autoincrement=True)
    @declared_attr
    def project_id(cls): # pylint: disable=E0213
        '''For modelling the targetLanguage field in this class'''
        return Column('project_id', Integer, ForeignKey('translation_projects.project_id'))
    @declared_attr
    def project(cls): # pylint: disable=E0213
        '''For modelling the project field in this class'''
        return relationship(TranslationProject, uselist=False)
    sentenceId = Column('sentence_id', Integer)
    surrogateId = Column('surrogate_id', String)
    sentence = Column('sentence', String)
    draft = Column('draft', String)
    draftMeta = Column('draft_metadata', JSON)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class TranslationMemory(Base):  # pylint: disable=too-few-public-methods
    '''Corresponds to table translation_memory in vachan DB used by Autographa MT mode'''
    __tablename__ = 'translation_memory'

    tokenId = Column('token_id', Integer, primary_key=True, autoincrement=True)
    @declared_attr
    def source_lang_id(cls): # pylint: disable=E0213
        '''For modelling the sourceLanguage field in this class'''
        return Column('source_lang_id', Integer, ForeignKey('languages.language_id'))
    @declared_attr
    def source_language(cls): # pylint: disable=E0213
        '''For modelling the sourceLanguage field in this class'''
        return relationship(Language, foreign_keys=cls.source_lang_id, uselist=False)
    @declared_attr
    def target_lang_id(cls): # pylint: disable=E0213
        '''For modelling the targetLanguage field in this class'''
        return Column('target_lang_id', Integer, ForeignKey('languages.language_id'))
    @declared_attr
    def target_language(cls): # pylint: disable=E0213
        '''For modelling the targetLanguage field in this class'''
        return relationship(Language, foreign_keys=cls.target_lang_id, uselist=False)
    token = Column('source_token', String)
    tokenRom = Column('source_token_romanized', String)
    translation = Column('translation', String)
    translationRom = Column('translation_romanized', String)
    frequency = Column('frequency', Integer)
    metaData = Column('source_token_metadata', JSON)

class TranslationProjectUser(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table translation_users in vachan DB used by Autographa MT mode'''
    __tablename__ = 'translation_project_users'

    projectUserId = Column('project_user_id', Integer, primary_key=True, autoincrement=True)
    @declared_attr
    def project_id(cls): # pylint: disable=E0213
        '''For modelling the targetLanguage field in this class'''
        return Column('project_id', Integer, ForeignKey('translation_projects.project_id'))
    @declared_attr
    def project(cls): # pylint: disable=E0213
        '''For modelling the targetLanguage field in this class'''
        return relationship(TranslationProject, foreign_keys=cls.project_id, uselist=False,
            back_populates="users")
    userId = Column('user_id', String, index=True)
    userRole = Column('user_role', String)
    metaData = Column('metadata', JSON)
    active = Column('active', Boolean)

class StopWords(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table stopwords_look_up in vachan DB '''
    __tablename__ = 'stopwords_look_up'

    swId = Column('sw_id', Integer, primary_key=True, autoincrement=True)
    languageId = Column('language_id', Integer)
    stopWord = Column('stopword', String)
    confidence = Column('confidence', Float)
    metaData = Column('metadata', JSON)
    active = Column('active', Boolean, default=True)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=func.now())

class Jobs(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table jobs in vachan DB '''
    __tablename__ = 'jobs'

    jobId = Column('job_id', Integer, primary_key=True, autoincrement=True)
    userId = Column('user_id', String)
    status = Column('status', String)
    output = Column('output', JSON)
    startTime = Column('start_time', DateTime)
    endTime = Column('end_time', DateTime)
