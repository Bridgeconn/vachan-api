from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, constr, AnyUrl

class NormalResponse(BaseModel):
	message : str

class ErrorResponse(BaseModel):
	error: str
	details: str


class ContentType(BaseModel):
	contentId : int
	contentType : str

class ContentTypeUpdateResponse(BaseModel):
	message: str
	data: ContentType = None



langCodePattern =constr(regex="^\w\w\w$")
class Direction(str, Enum):
	left_to_right = 'left-to-right'
	right_to_left = 'right-to-left'

class Language(BaseModel):
	language : str 
	code : langCodePattern 
	localScriptName : str = None
	script : str = None
	scriptDirection : Direction = None

class LanguageResponse(BaseModel):
	languageId : int
	language : str 
	code : langCodePattern 
	localScriptName : str = None
	script : str = None
	scriptDirection : Direction = None

class LanguageUpdateResponse(BaseModel):
	message: str
	data: LanguageResponse = None

class LanguageEdit (BaseModel):
	languageId: int
	language : str = None
	code : langCodePattern = None
	localScriptName : str = None
	script : str = None
	scriptDirection : Direction = None	



versionPattern = constr(regex="^[A-Z]+$")
class Version(BaseModel):
	versionAbbreviation : versionPattern
	versionName : str
	revision : str = "1"
	metadata : dict = None

class VersionResponse(BaseModel):
	versionId : int
	versionAbbreviation : versionPattern
	versionName : str
	revision : str 
	metadata : dict = None

class VersionUpdateResponse(BaseModel):
	message: str
	data: VersionResponse = None

class VersionEdit(BaseModel):
	versionId: int
	versionAbbreviation : versionPattern = None
	versionName : str = None
	revision : str = None
	metadata : dict = None


tableNamePattern = constr(regex="^\w\w\w_[A-Z]+_\w+_[a-z]+$")

class Source(BaseModel):
	sourceName : tableNamePattern
	contentType : str
	language : langCodePattern
	version : versionPattern
	revision: str = "1"
	year: int
	license: str = "ISC"
	metadata: dict = None
	active: bool = True

class SourceUpdateResponse(BaseModel):
	message: str
	data: Source = None

class SourceEdit(BaseModel):
	sourceName : int
	contentType : str = None
	language : langCodePattern = None
	version : versionPattern = None
	revision: str = None
	year: int = None
	license: str = None
	metadata: dict = None
	active: bool = None

BookCodePattern = constr(regex="^[a-z1-9][a-z][a-z]$")

class BibleBook(BaseModel):
	bookId : int
	bookName : str
	bookCode : BookCodePattern

class AudioBible(BaseModel):
	audioId: int
	name: str
	url: AnyUrl
	books: dict
	format: str
	status: bool

class AudioBibleUpdateResponse(BaseModel):
	message: str
	data: List[AudioBible] = None

class AudioBibleUpload(BaseModel):
	name: str
	url: AnyUrl
	books: dict
	format: str
	status: bool


class AudioBibleEdit(BaseModel):
	audioId: int
	name: str = None
	url: str = None
	books: dict = None
	format: str = None
	status: bool = None

class BibleBookContent(BaseModel):
	bookCode : BookCodePattern
	versification : dict = None
	USFM: str = None
	JSON: dict = None
	audio: AudioBible = None

class BibleBookUpdateResponse(BaseModel):
	message: str
	data: BibleBookContent = None

class BibleBookUpload(BaseModel):
	USFM: str 
	JSON: dict

class Reference(BaseModel):
	# bible : Source = None
	bookId: int = None
	bookcode: BookCodePattern
	chapter: int
	verseNumber: int
	verseNumberEnd: int = None

class BibleVerse(BaseModel):
	reference : Reference
	verseText: str
	footNote : str = None
	crossReference : str = None

class BookContentType(str, Enum):
	USFM = 'usfm'
	JSON = 'json'
	audio = 'audio'
	all = 'all'

class Commentary(BaseModel):
	bookCode : BookCodePattern
	chapter: int
	verseNumber: int
	commentary: str

class CommentaryUpdateResponse(BaseModel):
	message: str
	data: List[Commentary] = None

letterPattern = constr(regex='^\w$')
class DictionaryWord(BaseModel):
	word: str
	details: dict = None

class DictionaryUpdateResponse(BaseModel):
	message: str
	data: List[DictionaryWord] = None

class Infographic(BaseModel):
	bookCode : BookCodePattern
	infographicsLink : AnyUrl

class InfographicUpdateResponse(BaseModel):
	message: str
	data: List[Infographic] = None


class BibleVideo(BaseModel):
	bibleVideoId: int
	books: dict
	videoLink: AnyUrl
	title: str
	description: str
	theme: str
	status: bool

class BibleVideoUpdateResponse(BaseModel):
	message: str
	data: List[BibleVideo] = None

class BibleVideoUpload(BaseModel):
	books: dict
	videoLink: AnyUrl
	title: str
	description: str
	theme: str
	status: bool


class BibleVideoEdit(BaseModel):
	bibleVideoId: int
	books: dict  = None
	videoLink: AnyUrl  = None
	title: str  = None
	description: str  = None
	theme: str  = None
	status: bool  = None
