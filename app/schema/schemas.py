'''Defines all input and output classes for API endpoints'''
#pylint: disable=too-many-lines
from typing import List
from enum import Enum
from pydantic import BaseModel, constr, Field


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

class SourcePermissions(str, Enum):
    '''To specify source access permisions'''
    CONTENT = "content"
    OPENACCESS = "open-access"
    PUBLISHABLE = "publishable"
    DOWNLOADABLE = "downloadable"
    DERIVABLE = "derivable"
    RESEARCHUSE = "research-use"

LicenseCodePattern =constr(regex=r"^[a-zA-Z0-9\.\_\-]+$")

# class LicensePermisssion(str, Enum):
#     '''To specify direction of script'''
#     COMMERCIAL = "Commercial_use"
#     MODIFICATION = "Modification"
#     DISTRIBUTION = "Distribution"
#     PATENT = "Patent_use"
#     PRIVATE = "Private_use"

class LicenseCreate(BaseModel):
    '''To create and upload new license'''
    name: str
    code : LicenseCodePattern
    license : str
    permissions : List[SourcePermissions] = [SourcePermissions.OPENACCESS]
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "GNU Public License version 3",
                "code": "GPL-3",
                "license": "...actual license text here...",
                "permissions":
                    ["content", "open-access", "publishable",
                    "downloadable", "derivable", "research-use"]
            }
        }

class LicenseShortResponse(BaseModel):
    '''Return object of licenses without the full text'''
    name : str
    code : LicenseCodePattern
    permissions : List[SourcePermissions]
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
                    ["content", "open-access", "publishable",
                    "downloadable", "derivable", "research-use"]
            }
        }


class LicenseResponse(BaseModel):
    '''Return object of licenses'''
    name : str
    code : LicenseCodePattern
    license : str
    permissions : List[SourcePermissions]
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
                    ["content", "open-access", "publishable",
                    "downloadable", "derivable", "research-use"]
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
    permissions : List[SourcePermissions] = [SourcePermissions.OPENACCESS]
    active: bool = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "name": "GNU Public License version 3",
                "code": "GPL-3",
                "license": "...actual license text here...",
                "permissions":
                    ["content", "open-access", "publishable",
                    "downloadable", "derivable", "research-use"]
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

TableNamePattern = constr(regex=r"^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\w+_[a-z,-]+$")

class SourceCreate(BaseModel):
    '''Input object of sources'''
    contentType : str
    language : LangCodePattern
    version : VersionPattern
    revision: str = "1"
    year: int
    license: LicenseCodePattern = "CC-BY-SA"
    accessPermissions : List[SourcePermissions] = [SourcePermissions.CONTENT]
    metaData: dict = {}
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
    accessPermissions : List[SourcePermissions] = [SourcePermissions.CONTENT]
    metaData: dict = {}
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
