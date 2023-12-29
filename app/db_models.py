''' Defines SQL Alchemy models for each Database Table'''

from enum import Enum
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, JSON, Float, text
from sqlalchemy import Boolean, ForeignKey, DateTime
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Sequence
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from pytz import timezone
from database import Base  # pylint: disable=import-error
from custom_exceptions import GenericException # pylint: disable=import-error

ist_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

dynamicTables = {}

class ResourceTypeName(Enum):
    '''The string literals used as value of ResourceType field in ResourceType
    and also used to as the ending of respective database table names'''
    BIBLE = "bible"
    COMMENTARY = "commentary"
    PARASCRIPTURAL = "parascriptural"
    VOCABULARY = "vocabulary"
    GITLABREPO = "gitlabrepo"
    AUDIOBIBLE = "audiobible"
    SIGNBIBLEVIDEO = "signbiblevideo"

class TranslationDocumentType(Enum):
    '''Currently supports bible USFM only. Can be extended to
    CSV(for commentary or notes), doc(stories, other passages) etc.'''
    USFM = 'Bible USFM'

class ResourceType(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table resource_types in vachan DB(postgres)'''
    __tablename__ = "resource_types"

    resourcetypeId = Column('resource_type_id', Integer, primary_key=True)
    resourceType = Column('resource_type', String, unique=True)
    createdUser = Column('created_user', String)

class Language(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table languages in vachan DB(postgres)'''
    __tablename__ = 'languages'

    languageId = Column('language_id', Integer, primary_key=True)
    code = Column('language_code', String, unique=True, index=True)
    language = Column('language_name', String)
    scriptDirection = Column('script_direction', String)
    localScriptName = Column('localscript_name',String)
    metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    createTime = Column('created_at',DateTime,default=ist_time)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)

class License(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table licenses in vachan DB(postgres)'''
    __tablename__ = 'licenses'

    licenseId = Column('license_id', Integer, primary_key=True)
    code = Column('license_code', String, unique=True, index=True)
    name = Column('license_name', String)
    license = Column('license_text', String)
    permissions = Column('permissions', ARRAY(String))
    active = Column('active', Boolean,default=True)
    # metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    createTime = Column('created_at',DateTime,default=ist_time)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)

class Version(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table versions in vachan DB(postgres)'''
    __tablename__ = 'versions'

    versionId = Column('version_id', Integer, primary_key=True)
    versionAbbreviation = Column('version_short_name', String, unique=True, index=True)
    versionName = Column('version_name', String)
    versionTag = Column('version_tag', ARRAY(String))
    metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    createTime = Column('created_at',DateTime,default=ist_time)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)

class Resource(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table resources in vachan DB(postgres)'''
    __tablename__ = 'resources'

    resourceId = Column('resource_id', Integer, primary_key=True)
    resourceName = Column('version', String, unique=True)
    tableName = Column('resource_table', String, unique=True)
    year = Column('year', Integer)
    labels = Column('labels', ARRAY(String))
    licenseId = Column('license_id', Integer, ForeignKey('licenses.license_id'))
    license = relationship(License)
    resourcetypeId = Column('resourcetype_id',
                            Integer, ForeignKey('resource_types.resource_type_id'))
    resourceType = relationship('ResourceType')
    languageId = Column('language_id', Integer, ForeignKey('languages.language_id'))
    language = relationship('Language')
    versionId = Column('version_id', Integer, ForeignKey('versions.version_id'))
    version = relationship('Version')
    active = Column('active', Boolean)
    metaData = Column('metadata', JSONB)
    createdUser = Column('created_user', String)
    createTime = Column('created_at',DateTime,default=ist_time)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)

class BibleBook(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table bible_books_look_up in vachan DB(postgres)'''
    __tablename__ = 'bible_books_look_up'

    bookId = Column('book_id', Integer, primary_key=True)
    bookName = Column('book_name', String)
    bookCode = Column('book_code', String)

class Commentary(): # pylint: disable=too-few-public-methods # pylint: disable=unsubscriptable-object
    '''Corresponds to the dynamically created commentary tables in vachan Db(postgres)'''
    commentaryId = Column('commentary_id', Integer,
        Sequence('commentary_id_seq', start=100001, increment=1), primary_key=True)
    @hybrid_property
    def reference(self):
        '''To store reference information as JSONB'''
        return self._reference

    @reference.setter
    def reference(self, value):
        '''To set reference information from JSONB'''
        self._reference = value

    _reference = Column('reference', JSONB)

    @hybrid_property
    def ref_string(self):
        '''To compose surrogate id'''
        return f'{self.reference["book"]} {self.reference["chapter"]}:\
            {self.reference["verseNumber"]}-{self.reference["verseEnd"]}'

    @ref_string.expression
    def ref_string(cls):# pylint: disable=E0213
        '''To compose surrogate id(SQL expression)'''
        return func.concat(cls.reference['book'], " ", cls.reference['chapter'],\
             ":", cls.reference['verseNumber'], "-", cls.reference['verseEnd'])
    refStart = Column('ref_start', Integer)
    refEnd = Column('ref_end', Integer)
    commentary = Column('commentary', String)
    sectionType = Column('section_type', ARRAY(String))
    active = Column('active', Boolean)
    __table_args__ = (
        {'extend_existing': True}
                     )

class Vocabulary(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created vocabulary tables in vachan Db(postgres)'''
    wordId = Column('word_id', Integer,
        Sequence('word_id_seq', start=100001, increment=1), primary_key=True)
    word = Column('word', String, unique=True)
    details = Column('details', JSONB)
    active = Column('active', Boolean)
    # createdUser = Column('created_user',String)

    __table_args__ = (
        {'extend_existing': True},
                     )

class Parascriptural():# pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created parascripturals tables in vachan Db(postgres)'''
    parascriptId = Column('parascript_id', Integer,
        Sequence('parascriptural_id_seq', start=100001, increment=1), primary_key=True)
    category = Column('category',String)
    title = Column('title', String)
    description = Column('description', String)
    content = Column('content', String)
    reference = Column('reference', JSONB)
    refStart = Column('ref_start', Integer)
    refEnd = Column('ref_end', Integer)
    link = Column('link', String)
    metaData = Column('metadata', JSONB)
    active = Column('active', Boolean)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    createTime = Column('created_at', DateTime, default=ist_time)
    updateTime = Column('last_updated_at', DateTime, onupdate= ist_time,default=ist_time)
    __table_args__ = (
        {'extend_existing': True}
                     )
class SignBibleVideo():# pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created sign bible videos tables in vachan Db(postgres)'''
    signVideoId = Column('signvideo_id', Integer,
        Sequence('signvideo_id_seq', start=100001, increment=1), primary_key=True)
    title = Column('title', String)
    description = Column('description', String)
    reference = Column('reference', JSONB)
    refStart = Column('ref_start', Integer)
    refEnd = Column('ref_end', Integer)
    link = Column('link', String)
    metaData = Column('metadata', JSONB)
    active = Column('active', Boolean)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    createTime = Column('created_at', DateTime, default=ist_time)
    updateTime = Column('last_updated_at', DateTime, onupdate= ist_time,default=ist_time)
    __table_args__ = (
        {'extend_existing': True}
                     )
class AudioBible(): # pylint: disable=too-few-public-methods
    '''Corresponds to the dynamically created bible_audio tables in vachan Db(postgres)'''
    audioId  = Column('audio_id', Integer,
        Sequence('audio_id_seq', start=100001, increment=1), primary_key=True)
    name = Column('name', String)
    reference = Column('reference', JSONB)
    refStart = Column('ref_start', Integer)
    refEnd = Column('ref_end', Integer)
    link = Column('link', String)
    audioFormat = Column('audio_format', String)
    metaData = Column('metadata', JSONB)
    active = Column('active', Boolean)
    createdUser = Column('created_user', String)
    updatedUser = Column('last_updated_user', String)
    createTime = Column('created_at', DateTime, default=ist_time)
    updateTime = Column('last_updated_at', DateTime, onupdate= ist_time,default=ist_time)
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

def create_dynamic_table(resource_name, table_name, resource_type):
    '''To map or create one dynamic table based on the content Type'''
    if resource_type == ResourceTypeName.BIBLE.value:
        dynamicTables[resource_name] = type(
            table_name,(BibleContent, Base,),
            {"__tablename__": table_name})
        dynamicTables[resource_name+'_cleaned'] = type(
            table_name+'_cleaned',(BibleContentCleaned, Base,),
            {"__tablename__": table_name+'_cleaned'})
    elif resource_type == ResourceTypeName.COMMENTARY.value:
        dynamicTables[resource_name] = type(
            table_name,(Commentary, Base,),{"__tablename__": table_name})
    elif resource_type == ResourceTypeName.VOCABULARY.value:
        dynamicTables[resource_name] = type(
            table_name,(Vocabulary, Base,),{"__tablename__": table_name})
        new_index = Index(table_name+'_word_details_ix',  # pylint: disable=W0612
            text("to_tsvector('simple', word || ' ' ||"+\
            "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"),
            postgresql_using="gin",
            )
    elif resource_type == ResourceTypeName.PARASCRIPTURAL.value:
        dynamicTables[resource_name] = type(
            table_name,(Parascriptural, Base,),{"__tablename__": table_name})
    elif resource_type == ResourceTypeName.AUDIOBIBLE.value:
        dynamicTables[resource_name] = type(
            table_name,(AudioBible, Base,),{"__tablename__": table_name})
    elif resource_type == ResourceTypeName.SIGNBIBLEVIDEO.value:
        dynamicTables[resource_name] = type(
            table_name,(SignBibleVideo, Base,),{"__tablename__": table_name})
    elif resource_type == ResourceTypeName.GITLABREPO.value:
        pass
    else:
        raise GenericException("Table structure not defined for this content type:{resource_type}")


def map_all_dynamic_tables(db_: Session):
    '''Fetches list of dynamic tables from resources table
    and maps them according to their content types'''

    all_src = db_.query(Resource).all()
    for src in all_src:
        create_dynamic_table(src.resourceName, src.tableName, src.resourceType.resourceType)

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
    createTime = Column('created_at', DateTime, default=ist_time)
    updateTime = Column('last_updated_at', DateTime, onupdate= ist_time,default=ist_time)
    compatibleWith = Column('compatible_with', ARRAY(String))

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
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)

class TranslationMemory(Base):  # pylint: disable=too-few-public-methods
    '''Corresponds to table translation_memory in vachan DB used by Autographa MT mode'''
    __tablename__ = 'translation_memory'

    tmID = Column('token_id', Integer, primary_key=True, autoincrement=True)
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
    createTime = Column('created_at',DateTime,default=ist_time)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)

class Jobs(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table jobs in vachan DB '''
    __tablename__ = 'jobs'

    jobId = Column('job_id', Integer, primary_key=True, autoincrement=True)
    userId = Column('user_id', String)
    status = Column('status', String)
    output = Column('output', JSON)
    startTime = Column('start_time', DateTime)
    endTime = Column('end_time', DateTime)

class DeletedItem(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table deleted_items in vachan DB '''
    __tablename__ = 'deleted_items'

    itemId = Column('item_id', Integer, primary_key=True,autoincrement=True)
    deletedData = Column('deleted_data', JSON)
    createdUser = Column('deleted_user', String)
    deletedTime = Column('deleted_time', DateTime, default=ist_time)
    deletedFrom = Column('deleted_from', String)
    