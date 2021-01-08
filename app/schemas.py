'''Defines all input and output classes for API endpoints'''

from typing import List
from enum import Enum
from pydantic import BaseModel, constr, AnyUrl, validator, root_validator

class NormalResponse(BaseModel):
    '''Response with only a message'''
    message : str

class ErrorResponse(BaseModel):
    '''common error response object'''
    error: str
    details: str

class ContentTypeCreate(BaseModel):
    '''Input object to ceate a new content type'''
    contentType : constr(regex=r"^[^0-9\s]+$")

class ContentType(BaseModel):
    '''output object for content types'''
    contentId : int
    contentType : str
    class Config: # pylint: disable=too-few-public-methods
        '''For SQL Alchemy'''
        orm_mode = True

class ContentTypeUpdateResponse(BaseModel):
    '''Object usedtTo update content type'''
    message: str
    data: ContentType = None

LangCodePattern =constr(regex=r"^[a-zA-Z][a-zA-Z][a-zA-Z]$")
class Direction(str, Enum):
    '''To specify direction of script'''
    left_to_right = 'left-to-right'
    right_to_left = 'right-to-left'

class LanguageCreate(BaseModel):
    '''To create new language'''
    language : str
    code : LangCodePattern
    scriptDirection : Direction = None

class LanguageResponse(BaseModel):
    '''Return object of languages'''
    languageId : int
    language : str
    code : LangCodePattern
    scriptDirection : Direction = None
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class LanguageUpdateResponse(BaseModel):
    '''Return object of language update'''
    message: str
    data: LanguageResponse = None

class LanguageEdit (BaseModel):
    '''Input object of language update'''
    languageId: int
    language : str = None
    code : LangCodePattern = None
    scriptDirection : Direction = None

MetaDataPattern = constr(
    regex=r"^\{\s*[\"\'][^\"]+[\"\']\s*:\s*[\"\'][^\"]+[\"\']\s*" +
        r"(,\s*[\"\'][^\"]+[\"\']\s*:\s*[\"\'][^\"]+[\"\']\s*)*")

VersionPattern = constr(regex=r"^[A-Z]+$")
class VersionCreate(BaseModel):
    '''input object of version'''
    versionAbbreviation : VersionPattern
    versionName : str
    revision : int = 1
    metaData : dict = None

class VersionResponse(BaseModel):
    '''Return object of version'''
    versionId : int
    versionAbbreviation : VersionPattern
    versionName : str
    revision : int
    metaData : dict = None
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class VersionUpdateResponse(BaseModel):
    '''Return object of version update'''
    message: str
    data: VersionResponse = None

class VersionEdit(BaseModel):
    '''input object of version update'''
    versionId: int
    versionAbbreviation : VersionPattern = None
    versionName : str = None
    revision : int = None
    metaData : dict = None


TableNamePattern = constr(regex=r"^\w\w\w_[A-Z]+_\w+_[a-z]+$")

class SourceCreate(BaseModel):
    '''Input object of sources'''
    contentType : str
    language : LangCodePattern
    version : VersionPattern
    revision: str = "1"
    year: int
    license: str = "ISC"
    metaData: dict = None

class SourceResponse(BaseModel):
    '''Output object of sources'''
    sourceName : TableNamePattern
    contentType : ContentType = None
    language : LanguageResponse = None
    version : VersionResponse = None
    # revision: str = "1"
    year: int
    license: str = "ISC"
    metaData: dict = None
    active: bool = True
    class Config: # pylint: disable=too-few-public-methods
        '''For Pydantic'''
        orm_mode = True

class SourceUpdateResponse(BaseModel):
    '''response object of sources update'''
    message: str
    data: SourceResponse = None

class SourceEdit(BaseModel):
    '''Input object of source update'''
    sourceName : TableNamePattern
    language : LangCodePattern = None
    version : VersionPattern = None
    revision: str = None
    year: int = None
    license: str = None
    metaData: dict = None
    active: bool = None

BookCodePattern = constr(regex=r"^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")

class BibleBook(BaseModel):
    '''response object of Bible book'''
    bookId : int
    bookName : str
    bookCode : BookCodePattern
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class AudioBible(BaseModel):
    '''Response object of Audio Bible'''
    # audioId: int
    name: str
    url: AnyUrl
    books:  List[BookCodePattern]
    format: str
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class AudioBibleUpdateResponse(BaseModel):
    '''Response object of auido bible update'''
    message: str
    data: List[AudioBible] = None

class AudioBibleUpload(BaseModel):
    '''Input object of Audio Bible'''
    name: str
    url: AnyUrl
    books:  List[BookCodePattern]
    format: str
    active: bool = True

class AudioBibleEdit(BaseModel):
    ''' Input object of Auido Bible'''
    name: str
    url: str = None
    books: List[BookCodePattern] = None
    format: str = None
    active: bool = None

class BibleBookContent(BaseModel):
    '''Response object of Bible book contents'''
    book : BibleBook
    bookName: str = None
    versification : dict = None
    USFM: str = None
    JSON: dict = None
    audio: AudioBible = None
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class BibleBookUpdateResponse(BaseModel):
    '''Input object of Bible book update'''
    message: str
    data: List[BibleBookContent] = None

class BibleBookUpload(BaseModel):
    '''Input object of bible book'''
    USFM: str
    JSON: dict

class BibleBookEdit(BaseModel):
    '''Input object of bible book'''
    bookCode: BookCodePattern = None
    USFM: str = None
    JSON: dict = None
    active: bool = None

    @root_validator
    def check_for_usfm_json(cls, values): # pylint: disable=R0201 disable=E0213
        '''USFM and JSON should be updated together. If they are absent, bookCode is required'''
        print(">>>>>>>>>>>>>>>>>>>>>>>>")
        print(values)
        if (values['USFM'] is not None and values['JSON'] is None) or (
            values['USFM'] is not None and values['JSON'] is None):
            raise ValueError(
                'USFM and JSON are inter-dependant. So both should be updated together')
        if "bookCode" not in values or values['bookCode'] is None:
            if "JSON" in values:
                print(values['JSON'])
                values["bookCode"] = values['JSON']['book']['bookCode'].lower()
            else:
                raise ValueError('"bookCode" is required to identiy the row to be updated')
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<")
        print(values)
        return values

class Reference(BaseModel):
    '''Response object of bible refernce'''
    bible : TableNamePattern = None
    book: BibleBook
    chapter: int
    verseNumber: int
    verseNumberEnd: int = None

class BibleVerse(BaseModel):
    '''Response object of Bible Verse'''
    reference : Reference
    verseText: str
    footNote : str = None
    crossReference : str = None

class BookContentType(str, Enum):
    '''choices for bible content types'''
    USFM = 'usfm'
    JSON = 'json'
    audio = 'audio'
    all = 'all'

class CommentaryCreate(BaseModel):
    '''Response object for commentaries'''
    bookCode : BookCodePattern
    chapter: int
    verseStart: int = None
    verseEnd: int = None
    commentary: str
    active: bool = True

    @validator('verseStart', 'verseEnd')
    def check_verses(cls, val, values): # pylint: disable=R0201 disable=E0213
        '''verse fields should be greater than or equal to -1'''
        if 'chapter' in values and values['chapter'] in [-1, 0]:
            if val not in [-1, 0, None]:
                raise ValueError('verse fields should be 0, for book introductions and epilogues')
            val = 0
        if val is None:
            raise ValueError('verse fields must have a value, '+
                'except for book introduction and epilogue')
        if val < -1:
            raise ValueError('verse fields should be greater than or equal to -1')
        return val

    @validator('verseEnd')
    def check_range(cls, val, values): # pylint: disable=R0201 disable=E0213
        '''verse start should be less than or equal to verse end'''
        if 'verseStart' in values and val < values['verseStart']:
            raise ValueError('verse start should be less than or equal to verse end')
        return val

    @validator('chapter')
    def check_chapter(cls, val): # pylint: disable=R0201 disable=E0213
        '''chapter fields should be greater than or equal to -1'''
        if val < -1:
            raise ValueError('chapter field should be greater than or equal to -1')
        return val

class CommentaryEdit(BaseModel):
    '''Response object for commentaries'''
    bookCode : BookCodePattern
    chapter: int
    verseStart: int = None
    verseEnd: int = None
    commentary: str = None
    active: bool = None

    @validator('verseStart', 'verseEnd')
    def check_verses(cls, val, values): # pylint: disable=R0201 disable=E0213
        '''verse fields should be greater than or equal to -1'''
        if 'chapter' in values and values['chapter'] in [-1, 0]:
            if val not in [-1, 0, None]:
                raise ValueError('verse fields should be 0, for book introductions and epilogues')
            val = 0
        if val is None:
            raise ValueError('verse fields must have a value, '+
                'except for book introduction and epilogue')
        if val < -1:
            raise ValueError('verse fields should be greater than or equal to -1')
        return val

    @validator('verseEnd')
    def check_range(cls, val, values): # pylint: disable=R0201 disable=E0213
        '''verse start should be less than or equal to verse end'''
        if 'verseStart' in values and val < values['verseStart']:
            raise ValueError('verse start should be less than or equal to verse end')
        return val

    @validator('chapter')
    def check_chapter(cls, val): # pylint: disable=R0201 disable=E0213
        '''chapter fields should be greater than or equal to -1'''
        if val < -1:
            raise ValueError('chapter field should be greater than or equal to -1')
        return val

class CommentaryResponse(BaseModel):
    '''Response object for commentaries'''
    book : BibleBook
    chapter: int
    verseStart: int = None
    verseEnd: int = None
    commentary: str
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class CommentaryUpdateResponse(BaseModel):
    '''Response object for commentary update'''
    message: str
    data: List[CommentaryResponse] = None

LetterPattern = constr(regex=r'^\w$')
class DictionaryWordCreate(BaseModel):
    '''Upload object of dictionary word'''
    word: str
    details: dict = None
    active: bool = True

class DictionaryWordEdit(BaseModel):
    '''Upload object of dictionary word'''
    word: str
    details: dict = None
    active: bool = None

class DictionaryWordResponse(BaseModel):
    '''Response object of dictionary word'''
    word: str
    details: dict = None
    active: bool = None
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class DictionaryUpdateResponse(BaseModel):
    '''Response object of dictionary word update'''
    message: str
    data: List[DictionaryWordResponse] = None

class InfographicCreate(BaseModel):
    '''Input object of infographics'''
    bookCode : BookCodePattern
    title: str
    infographicLink : AnyUrl
    active: bool = True

class InfographicEdit(BaseModel):
    '''Input object of infographics Update'''
    bookCode : BookCodePattern
    title: str
    infographicLink : AnyUrl = None
    active: bool = None

class InfographicResponse(BaseModel):
    '''Response object of infographics'''
    book : BibleBook
    title: str
    infographicLink : AnyUrl
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class InfographicUpdateResponse(BaseModel):
    '''Response object of infographics update'''
    message: str
    data: List[InfographicResponse] = None


class BibleVideo(BaseModel):
    '''Response object of Bible Vedios'''
    title: str
    books: List[BookCodePattern]
    videoLink: AnyUrl
    description: str
    theme: str
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class BibleVideoUpdateResponse(BaseModel):
    '''Response object of Bible Video update'''
    message: str
    data: List[BibleVideo] = None

class BibleVideoUpload(BaseModel):
    '''Input Object of bible Videos'''
    title: str
    books: List[BookCodePattern]
    videoLink: AnyUrl
    description: str
    theme: str
    active: bool = True


class BibleVideoEdit(BaseModel):
    '''Input object of Bible Video update'''
    title: str
    books: List[BookCodePattern]  = None
    videoLink: AnyUrl  = None
    description: str  = None
    theme: str  = None
    active: bool  = None
