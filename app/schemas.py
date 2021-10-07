'''Defines all input and output classes for API endpoints'''

from typing import List
from enum import Enum
from pydantic import BaseModel, constr, AnyUrl, validator, root_validator, Field

from crud import utils

#pylint: disable=too-few-public-methods
class NormalResponse(BaseModel):
    '''Response with only a message'''
    message : str = Field(...,example="App is up and running")

class ErrorResponse(BaseModel):
    '''common error response object'''
    error: str
    details: str
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "error": "Error Name",
                "details":"More details about the error"
            }
        }

class ContentTypeCreate(BaseModel):
    '''Input object to ceate a new content type'''
    contentType : constr(regex=r"^[a-z]+$") = Field(...,example="commentary")

class ContentType(BaseModel):
    '''output object for content types'''
    contentId : int
    contentType : str
    class Config:
        '''For SQL Alchemy'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "contentId": 1,
                "contentType": "commentary"
            }
        }

class ContentTypeUpdateResponse(BaseModel):
    '''Object usedtTo update content type'''
    message: str = Field(...,example="Content type created successfully")
    data: ContentType = None

LangCodePattern =constr(regex=r"^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
class Direction(str, Enum):
    '''To specify direction of script'''
    LEFTTORIGHT = 'left-to-right'
    RIGHTTOLEFT = 'right-to-left'

class LanguageCreate(BaseModel):
    '''To create new language'''
    language : str
    code : LangCodePattern
    scriptDirection : Direction = None
    metaData: dict = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "language": "Hindi",
                "code": "hi",
                "scriptDirection": "left-to-right",
                "metaData": {"region": "India, Asia",
                    "alternate-names": ["Khadi Boli", "Khari Boli", "Dakhini", "Khariboli"],
                    "suppress-script": "Deva", "is-gateway-language": True}
            }
        }

class LanguageResponse(BaseModel):
    '''Return object of languages'''
    languageId : int
    language : str
    code : LangCodePattern
    scriptDirection : Direction = None
    metaData: dict = None
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "languageId": 100057,
                "language": "Hindi",
                "code": "hi",
                "scriptDirection": "left-to-right",
                "metaData": {"region": "India, Asia",
                    "alternate-names": ["Khadi Boli", "Khari Boli", "Dakhini", "Khariboli"],
                    "suppress-script": "Deva", "is-gateway-language": True}

            }
        }

class LanguageCreateResponse(BaseModel):
    '''Return object of language update'''
    message: str = Field(..., example="Language created successfully")
    data: LanguageResponse = None

class LanguageUpdateResponse(BaseModel):
    '''Return object of language update'''
    message: str = Field(..., example="Language edited successfully")
    data: LanguageResponse = None

class LanguageEdit (BaseModel):
    '''Input object of language update'''
    languageId: int
    language : str = None
    code : LangCodePattern = None
    scriptDirection : Direction = None
    metaData: dict = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "languageId": 100057,
                "language": "Hindi",
                "code": "hi",
                "scriptDirection":"left-to-right",
                "metaData": {"region": "India, Asia",
                    "alternate-names": ["Khadi Boli", "Khari Boli", "Dakhini", "Khariboli"],
                    "suppress-script": "Deva", "is-gateway-language": True}

            }
        }

LicenseCodePattern =constr(regex=r"^[a-zA-Z0-9\.\_\-]+$")
class LicensePermisssion(str, Enum):
    '''To specify direction of script'''
    COMMERCIAL = "Commercial_use"
    MODIFICATION = "Modification"
    DISTRIBUTION = "Distribution"
    PATENT = "Patent_use"
    PRIVATE = "Private_use"

class LicenseCreate(BaseModel):
    '''To create and upload new license'''
    name: str
    code : LicenseCodePattern
    license : str
    permissions : List[LicensePermisssion] = ['Private_use']
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "GNU Public License version 3",
                "code": "GPL-3",
                "license": "...actual license text here...",
                "permissions":
                    ["Commercial_use", "Modification", "Distribution", "Patent_use", "Private_use"]
            }
        }

class LicenseShortResponse(BaseModel):
    '''Return object of licenses without the full text'''
    name : str
    code : LicenseCodePattern
    permissions : List[LicensePermisssion]
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "GNU Public License version 3",
                "code": "GPL-3",
                "permissions":
                    ["Commercial_use", "Modification", "Distribution", "Patent_use", "Private_use"]
            }
        }


class LicenseResponse(BaseModel):
    '''Return object of licenses'''
    name : str
    code : LicenseCodePattern
    license : str
    permissions : List[LicensePermisssion]
    active: bool
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "GNU Public License version 3",
                "code": "GPL-3",
                "license": "...actual license text here...",
                "permissions":
                    ["Commercial_use", "Modification", "Distribution", "Patent_use", "Private_use"]
            }
        }

class LicenseCreateResponse(BaseModel):
    '''Return object of language update'''
    message: str = Field(..., example="License uploaded successfully")
    data: LicenseResponse = None

class LicenseUpdateResponse(BaseModel):
    '''Return object of language update'''
    message: str = Field(..., example="License edited successfully")
    data: LicenseResponse = None

class LicenseEdit (BaseModel):
    '''Input object of language update'''
    code: LicenseCodePattern
    name : str = None
    license : str = None
    permissions : List[LicensePermisssion] = None
    active: bool = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "GNU Public License version 3",
                "code": "GPL-3",
                "license": "...actual license text here...",
                "permissions":
                    ["Commercial_use", "Modification", "Distribution", "Patent_use", "Private_use"]
            }
        }

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
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "versionAbbreviation": "KJV",
                "versionName": "King James Version",
                "revision": 1,
                "metaData": {"publishedIn": "1611"}
            }
        }

class VersionResponse(BaseModel):
    '''Return object of version'''
    versionId : int
    versionAbbreviation : VersionPattern
    versionName : str
    revision : int
    metaData : dict = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "versionId": 1,
                "versionAbbreviation": "KJV",
                "versionName": "King James Version",
                "revision": 1,
                "metaData": {"publishedIn": "1611"}
            }
        }

class VersionCreateResponse(BaseModel):
    '''Return object of version update'''
    message: str = Field(..., example="Version created successfully")
    data: VersionResponse = None

class VersionUpdateResponse(BaseModel):
    '''Return object of version update'''
    message: str = Field(..., example="Version edited successfully")
    data: VersionResponse = None

class VersionEdit(BaseModel):
    '''input object of version update'''
    versionId: int
    versionAbbreviation : VersionPattern = None
    versionName : str = None
    revision : int = None
    metaData : dict = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "versionId": 1,
                "versionAbbreviation": "KJV",
                "versionName": "King James Version",
                "revision": 1,
                "metaData": {"publishedIn": "1611"}
            }
        }

class SourcePermisions(str, Enum):
    '''To specify source access permisions'''
    CONTENT = "content"
    OPENACCESS = "open-access"
    PUBLISHABLE = "publishable"
    DOWNLOADABLE = "downloadable"
    DERIVABLE = "derivable"

TableNamePattern = constr(regex=r"^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\w+_[a-z]+$")

class SourceCreate(BaseModel):
    '''Input object of sources'''
    contentType : str
    language : LangCodePattern
    version : VersionPattern
    revision: str = "1"
    year: int
    license: LicenseCodePattern = "CC-BY-SA"
    accessPermissions : List[SourcePermisions] = [SourcePermisions.CONTENT]
    metaData: dict = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "contentType": "commentary",
                "language": "en",
                "version": "KJV",
                "revision": 1,
                "year": 2020,
                "license": "ISC",
                "accessPermissions" : ["content"],
                "metaData": {"otherName": "KJBC, King James Bible Commentaries"}
            }
        }

class SourceResponse(BaseModel):
    '''Output object of sources'''
    sourceName : TableNamePattern
    contentType : ContentType = None
    language : LanguageResponse = None
    version : VersionResponse = None
    # revision: str = "1"
    year: int
    license: LicenseShortResponse
    metaData: dict = None
    active: bool = True
    class Config:
        '''For Pydantic'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "sourceName": "en_KJV_1_commentary",
                "contentType": {},
                "language": {},
                "version": {},
                "revision": 1,
                "year": 2020,
                "license": {},
                "metaData": {"otherName": "KJBC, King James Bible Commentaries"},
                "active": True
            }
        }

class SourceCreateResponse(BaseModel):
    '''response object of sources update'''
    message: str = Field(..., example="Source created successfully")
    data: SourceResponse = None

class SourceUpdateResponse(BaseModel):
    '''response object of sources update'''
    message: str = Field(..., example="Source edited successfully")
    data: SourceResponse = None


class SourceEdit(BaseModel):
    '''Input object of source update'''
    sourceName : TableNamePattern
    language : LangCodePattern = None
    version : VersionPattern = None
    revision: str = None
    year: int = None
    license: LicenseCodePattern = None
    accessPermissions : List[SourcePermisions] = [SourcePermisions.CONTENT]
    metaData: dict = None
    active: bool = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "sourceName": "en_KJV_1_commentary",
                "language": "en",
                "version": "KJV",
                "revision": 1,
                "year": 2020,
                "license": "ISC",
                "accessPermissions" : ["content"],
                "metaData": {"otherName": "KJBC, King James Bible Commentaries"},
                "active": False
            }
        }

BookCodePattern = constr(regex=r"^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")

class BibleBook(BaseModel):
    '''response object of Bible book'''
    bookId : int
    bookName : str
    bookCode : BookCodePattern
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookId": 41,
                "bookName": "Matthew",
                "bookCode": "mat"
            }
        }

class AudioBible(BaseModel):
    '''Response object of Audio Bible'''
    # audioId: int
    name: str = None
    url: AnyUrl = None
    # book:  BibleBook
    format: str = None
    active: bool = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "XXX audio bible: Gospel series",
                "url": "http://someplace.come/resoucesid",
                "format": "mp3",
                "active": True
            }
        }

class AudioBibleCreateResponse(BaseModel):
    '''Response object of auido bible update'''
    message: str = Field(..., example="Bible audios details uploaded successfully")
    data: List[AudioBible] = None

class AudioBibleUpdateResponse(BaseModel):
    '''Response object of auido bible update'''
    message: str = Field(..., example="Bible audios details updated successfully")
    data: List[AudioBible] = None

class AudioBibleUpload(BaseModel):
    '''Input object of Audio Bible'''
    name: str
    url: AnyUrl
    books:  List[BookCodePattern]
    format: str
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "XXX audio bible: Gospel series",
                "books": ["mat"],
                "url": "http://someplace.come/resoucesid",
                "format": "mp3",
                "active": True
            }
        }

class AudioBibleEdit(BaseModel):
    ''' Input object of Auido Bible'''
    name: str = None
    url: AnyUrl = None
    books: List[BookCodePattern]
    format: str = None
    active: bool = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "books": ["mat", "mrk", "luk", "jhn"],
                "name": "XXX audio bible: Gospel series",
                "url": "http://someplace.come/resoucesid",
                "format": "mp3",
                "active": True
            }
        }

class Reference(BaseModel):
    '''Response object of bible refernce'''
    bible : TableNamePattern = None
    book: BookCodePattern = None
    chapter: int
    verseNumber: int
    verseNumberEnd: int = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bible": "hi_IRV_5_bible",
                "book": "mat",
                "chapter": 1,
                "verseNumber": 12,
                "verseNumberEnd": 17
            }
        }

class BibleBookContent(BaseModel):
    '''Response object of Bible book contents'''
    book : BibleBook
    bookName: str = None
    USFM: str = None
    JSON: dict = None
    audio: AudioBible = None
    active: bool
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "book": { "bookId": 41, "bookCode": "mat", "bookName": "Matthew"},
                "USFM": "\\id MAT\n\\c 1\n\\p\n\\v 1 इब्राहीम की सन्‍तान, दाऊद की ...",
                "JSON": { "book": { "bookCode": "MAT" },
                      "chapters": [
                            {"chapterNumber": "1",
                             "contents": [ {
                                "verseNumber": "1",
                                "verseText": "इब्राहीम की सन्‍तान, दाऊद की ..."}]}
                        ]
                    },
                "AudioBible": {
                    "name": "XXX audio bible: Gospel series",
                    "url": "http://someplace.come/resoucesid",
                    "format": "mp3",
                    "active": True
                },
                "active": True
            }
        }

class BibleBookCreateResponse(BaseModel):
    '''Input object of Bible book update'''
    message: str = Field(..., example="Bible books uploaded and processed successfully")
    data: List[BibleBookContent] = None

class BibleBookUpdateResponse(BaseModel):
    '''Input object of Bible book update'''
    message: str = Field(..., example="Bible books updated successfully")
    data: List[BibleBookContent] = None

class BibleBookUpload(BaseModel):
    '''Input object of bible book'''
    USFM: str = None
    JSON: dict = None
    @root_validator
    def check_for_usfm_json(cls, values): # pylint: disable=R0201 disable=E0213
        '''Either USFM and JSON should be present'''
        if "USFM" not in values and "JSON" not in values:
            raise ValueError("Either USFM and JSON should be provided")
        return values

    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "USFM": "\\id MAT\n\\c 1\n\\p\n\\v 1 इब्राहीम की सन्‍तान, दाऊद की ...",
            }
        }

class BibleBookEdit(BaseModel):
    '''Input object of bible book'''
    bookCode: BookCodePattern = None
    USFM: str = None
    JSON: dict = None
    active: bool = None

    @root_validator
    def check_for_usfm_json(cls, values): # pylint: disable=R0201 disable=E0213
        '''USFM and JSON should be updated together. If they are absent, bookCode is required'''
        if "bookCode" not in values or values['bookCode'] is None:
            if "JSON" in values and values['JSON'] is not None:
                values["bookCode"] = values["JSON"]['book']['bookCode'].lower()
            elif "USFM" in values:
                usfm_json = utils.parse_usfm(values['USFM'])
                values["bookCode"] = usfm_json['book']['bookCode'].lower()
                values["JSON"] = usfm_json
            else:
                raise ValueError('"bookCode" is required to identiy the row to be updated')
        return values

    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookCode": "mat",
                "USFM": "\\id MAT\n\\c 1\n\\p\n\\v 1 इब्राहीम की सन्‍तान, दाऊद की सन्‍तान,"+\
                    "यीशु मसीह की वंशावली ।",
                "active": True
            }
        }

class Versification(BaseModel):
    '''Response object for bible versification'''
    maxVerses: dict
    mappedVerses: dict
    excludedVerses: list
    partialVerses: dict
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "maxVerses": {
                    "GEN":["31", "25", "24", "26", "32", "22"],
                    "EXO": ["22", "25", "22", "31", "23", "30", "29", "28", "35", "29", "10", "51"]
                },
                "mappedVerses":{},
                "excludedVerses": ['MAT 17:21'],
                "partialVerses": {}
            }
        }

class BibleVerse(BaseModel):
    '''Response object of Bible Verse'''
    reference : Reference
    verseText: str
    # footNote : str = None
    # crossReference : str = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "reference": {
                    "bible": "hi_IRV_5_bible",
                    "book": "mat",
                    "chapter": 1,
                    "verseNumber": 12
                },
                "verseText": "बन्‍दी होकर बाबुल पहुंचाए जाने के बाद..."
            }
        }

class BookContentType(str, Enum):
    '''choices for bible content types'''
    USFM = 'usfm'
    JSON = 'json'
    AUDIO = 'audio'
    ALL = 'all'

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
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookCode": "1ki",
                "chapter": 10,
                "verseStart": 1,
                "verseEnd": 7,
                "commentary": "It was customary at the time ...",
                "active": True
            }
        }


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
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookCode": "1ki",
                "chapter": 10,
                "verseStart": 1,
                "verseEnd": 7,
                "commentary": "One of the practices of that time was ...",
                "active": False
            }
        }

class CommentaryResponse(BaseModel):
    '''Response object for commentaries'''
    book : BibleBook
    chapter: int
    verseStart: int = None
    verseEnd: int = None
    commentary: str
    active: bool
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookCode": "1ki",
                "chapter": 10,
                "verseStart": 1,
                "verseEnd": 7,
                "commentary": "It was customary at the time ...",
                "active": True
            }
        }

class CommentaryCreateResponse(BaseModel):
    '''Response object for commentary update'''
    message: str = Field(..., example="Commentaries added successfully")
    data: List[CommentaryResponse] = None

class CommentaryUpdateResponse(BaseModel):
    '''Response object for commentary update'''
    message: str = Field(..., example="Commentaries updated successfully")
    data: List[CommentaryResponse] = None

LetterPattern = constr(regex=r'^\w$')
class DictionaryWordCreate(BaseModel):
    '''Upload object of dictionary word'''
    word: str
    details: dict = None
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "word": "Adam",
                "details": {"type": "person",
                    "definition": "The first man God created"},
                "active": True
            }
        }

class DictionaryWordEdit(BaseModel):
    '''Upload object of dictionary word'''
    word: str
    details: dict = None
    active: bool = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "word": "Adam",
                "details": {"type": "person name",
                    "definition": 'The first man God created.'+\
                    'The word adam is also used in the Bible as a pronoun, individually as '+\
                    '"a human" and in a collective sense as "mankind".'},
                "active": True
            }
        }

class DictionaryWordResponse(BaseModel):
    '''Response object of dictionary word'''
    word: str
    details: dict = None
    active: bool = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "word": "Adam",
                "details": {"type": "person",
                    "definition": "The first man God created."},
                "active": True
            }
        }

class DictionaryCreateResponse(BaseModel):
    '''Response object of dictionary word update'''
    message: str = Field(..., example="Dictionary words added successfully")
    data: List[DictionaryWordResponse] = None

class DictionaryUpdateResponse(BaseModel):
    '''Response object of dictionary word update'''
    message: str = Field(..., example="Dictionary words updated successfully")
    data: List[DictionaryWordResponse] = None

class InfographicCreate(BaseModel):
    '''Input object of infographics'''
    bookCode : BookCodePattern
    title: str
    infographicLink : AnyUrl
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookCode": "exo",
                "title": "Ark of Covenant",
                "infographicLink": "http://someplace.com/resoucesid",
                "active": True
            }
        }

class InfographicEdit(BaseModel):
    '''Input object of infographics Update'''
    bookCode : BookCodePattern
    title: str
    infographicLink : AnyUrl = None
    active: bool = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "bookCode": "exo",
                "title": "Ark of Covenant",
                "infographicLink": "http://someOtherPlace.com/resoucesid",
                "active": False
            }
        }

class InfographicResponse(BaseModel):
    '''Response object of infographics'''
    book : BibleBook
    title: str
    infographicLink : AnyUrl
    active: bool
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "book": {"bookId":2, "bookCode":"exo", "bookName":"exodus"},
                "title": "Ark of Covenant",
                "infographicLink": "http://someplace.com/resoucesid",
                "active": True
            }
        }

class InfographicCreateResponse(BaseModel):
    '''Response object of infographics update'''
    message: str = Field(..., example="Infographics added successfully")
    data: List[InfographicResponse] = None

class InfographicUpdateResponse(BaseModel):
    '''Response object of infographics update'''
    message: str = Field(..., example="Infographics updated successfully")
    data: List[InfographicResponse] = None

class BibleVideo(BaseModel):
    '''Response object of Bible Vedios'''
    title: str
    books: List[BookCodePattern]
    videoLink: AnyUrl
    description: str
    theme: str
    active: bool
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Overview: song of songs",
                "books": ["sng"],
                "videoLink": "https://someplace.com/resoucesid",
                "description": "Watch our overview video on the book of Song of Songs,"+\
                    "which breaks down the literary design of the book and "+\
                    "its flow of thought.",
                "theme": "Old Testament, Poetic Book",
                "active": True
            }
        }

class BibleVideoCreateResponse(BaseModel):
    '''Response object of Bible Video update'''
    message: str = Field(...,example="Bible videos added successfully")
    data: List[BibleVideo] = None

class BibleVideoUpdateResponse(BaseModel):
    '''Response object of Bible Video update'''
    message: str = Field(...,example="Bible videos updated successfully")
    data: List[BibleVideo] = None

class BibleVideoUpload(BaseModel):
    '''Input Object of bible Videos'''
    title: str
    books: List[BookCodePattern]
    videoLink: AnyUrl
    description: str
    theme: str
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Overview: song of songs",
                "books": ["sng"],
                "videoLink": "https://someplace.com/resoucesid",
                "description": "Watch our overview video on the book of Song of Songs,"+\
                    "which breaks down the literary design of the book and "+\
                    "its flow of thought.",
                "theme": "Old Testament",
                "active": True

            }
        }


class BibleVideoEdit(BaseModel):
    '''Input object of Bible Video update'''
    title: str
    books: List[BookCodePattern]  = None
    videoLink: AnyUrl  = None
    description: str  = None
    theme: str  = None
    active: bool  = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Overview: song of songs",
                "books": ["sng"],
                "videoLink": "https://anotherplace.com/resoucesid",
                "description": "Watch our overview video on the book of Song of Songs,"+\
                    "which breaks down the literary design of the book and "+\
                    "its flow of thought.",
                "theme": "Old Testament, Poetic Book",
                "active": True
            }
        }
