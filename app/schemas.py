'''Defines all input and output classes for API endpoints'''

from typing import List
from enum import Enum
from pydantic import BaseModel, constr, AnyUrl

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

VersionPattern = constr(regex=r"^[A-Z]+$")
class Version(BaseModel):
    '''input object of version'''
    versionAbbreviation : VersionPattern
    versionName : str
    revision : str = "1"
    metadata : dict = None

class VersionResponse(BaseModel):
    '''Return object of version'''
    versionId : int
    versionAbbreviation : VersionPattern
    versionName : str
    revision : str
    metadata : dict = None

class VersionUpdateResponse(BaseModel):
    '''Return object of version update'''
    message: str
    data: VersionResponse = None

class VersionEdit(BaseModel):
    '''input object of version update'''
    versionId: int
    versionAbbreviation : VersionPattern = None
    versionName : str = None
    revision : str = None
    metadata : dict = None


TableNamePattern = constr(regex=r"^\w\w\w_[A-Z]+_\w+_[a-z]+$")

class Source(BaseModel):
    '''Input object of sources'''
    sourceName : TableNamePattern
    contentType : str
    language : LangCodePattern
    version : VersionPattern
    revision: str = "1"
    year: int
    license: str = "ISC"
    metadata: dict = None
    active: bool = True

class SourceUpdateResponse(BaseModel):
    '''response object of sources'''
    message: str
    data: Source = None

class SourceEdit(BaseModel):
    '''Input object of source update'''
    sourceName : int
    contentType : str = None
    language : LangCodePattern = None
    version : VersionPattern = None
    revision: str = None
    year: int = None
    license: str = None
    metadata: dict = None
    active: bool = None

BookCodePattern = constr(regex=r"^[a-z1-9][a-z][a-z]$")

class BibleBook(BaseModel):
    '''response object of Bible book'''
    bookId : int
    bookName : str
    bookCode : BookCodePattern

class AudioBible(BaseModel):
    '''Response object of Audio Bible'''
    audioId: int
    name: str
    url: AnyUrl
    books: dict
    format: str
    status: bool

class AudioBibleUpdateResponse(BaseModel):
    '''Response object of auido bible update'''
    message: str
    data: List[AudioBible] = None

class AudioBibleUpload(BaseModel):
    '''Input object of Audio Bible'''
    name: str
    url: AnyUrl
    books: dict
    format: str
    status: bool


class AudioBibleEdit(BaseModel):
    ''' Input object of Auido Bible'''
    audioId: int
    name: str = None
    url: str = None
    books: dict = None
    format: str = None
    status: bool = None

class BibleBookContent(BaseModel):
    '''Response object of Bible book contents'''
    bookCode : BookCodePattern
    versification : dict = None
    USFM: str = None
    JSON: dict = None
    audio: AudioBible = None

class BibleBookUpdateResponse(BaseModel):
    '''Input object of Bible book update'''
    message: str
    data: BibleBookContent = None

class BibleBookUpload(BaseModel):
    '''Input object of bible book'''
    USFM: str
    JSON: dict

class Reference(BaseModel):
    '''Response object of bible refernce'''
    # bible : Source = None
    bookId: int = None
    bookcode: BookCodePattern
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

class Commentary(BaseModel):
    '''Response object for commentaries'''
    bookCode : BookCodePattern
    chapter: int
    verseNumber: int
    commentary: str

class CommentaryUpdateResponse(BaseModel):
    '''Response object for commentary update'''
    message: str
    data: List[Commentary] = None

LetterPattern = constr(regex=r'^\w$')
class DictionaryWord(BaseModel):
    '''Response object of dictionary word'''
    word: str
    details: dict = None

class DictionaryUpdateResponse(BaseModel):
    '''Response object of dictionary word update'''
    message: str
    data: List[DictionaryWord] = None

class Infographic(BaseModel):
    '''Response object of infographics'''
    bookCode : BookCodePattern
    infographicsLink : AnyUrl

class InfographicUpdateResponse(BaseModel):
    '''Response object of infographics update'''
    message: str
    data: List[Infographic] = None


class BibleVideo(BaseModel):
    '''Response object of Bible Vedios'''
    bibleVideoId: int
    books: dict
    videoLink: AnyUrl
    title: str
    description: str
    theme: str
    status: bool

class BibleVideoUpdateResponse(BaseModel):
    '''Response object of Bible Video update'''
    message: str
    data: List[BibleVideo] = None

class BibleVideoUpload(BaseModel):
    '''Input Object of bible Videos'''
    books: dict
    videoLink: AnyUrl
    title: str
    description: str
    theme: str
    status: bool


class BibleVideoEdit(BaseModel):
    '''Input object of Bible Video update'''
    bibleVideoId: int
    books: dict  = None
    videoLink: AnyUrl  = None
    title: str  = None
    description: str  = None
    theme: str  = None
    status: bool  = None
