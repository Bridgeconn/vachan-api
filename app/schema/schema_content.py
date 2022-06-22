'''Defines all input and output classes for Content related API endpoints
like Bible,Audio,Video etc.'''

from typing import List
from enum import Enum
from pydantic import BaseModel, constr, AnyUrl, validator, root_validator, Field
from schema.schemas import TableNamePattern, BookCodePattern
from crud import utils

#pylint: disable=too-few-public-methods
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
    metaData : dict = None
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

# class CommentaryCreateResponse(BaseModel):
#     '''Response object for commentary update'''
#     message: str = Field(..., example="Commentaries added successfully")
#     data: List[CommentaryResponse] = None

# Again added to avoid circulat import error for job
class Job(BaseModel):
    '''Response objects of Job'''
    jobId: int = Field(..., example=100000)
    status: str = Field(..., example="job created")
    output: dict = Field(None, example={
        'data': []
        })

class CommentaryCreateResponse(BaseModel):
    '''Response object for commentary update'''
    message: str = Field(..., example="Uploading Commentaries in background")
    data: Job

# class CommentaryUpdateResponse(BaseModel):
#     '''Response object for commentary update'''
#     message: str = Field(..., example="Commentaries updated successfully")
#     data: List[CommentaryResponse] = None

class CommentaryUpdateResponse(BaseModel):
    '''Response object for commentary update'''
    message: str = Field(..., example="Commentaries updated successfully")
    data: Job

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

class BibleVideoRefObj(BaseModel):
    """Reference Object of BibleVideo"""
    bookCode : BookCodePattern = None
    chapter: int
    verseStart: int = None
    verseEnd: int = None

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

class BibleVideo(BaseModel):
    '''Response object of Bible Vedios'''
    title: str
    references: List[Reference] = []
    videoLink: AnyUrl
    description: str
    series: str
    active: bool
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Overview: song of songs",
                "references": [{
                    "book": "sng",
                    "chapter": 1,
                    "verseNumber": 12
                }],
                "videoLink": "https://someplace.com/resoucesid",
                "description": "Watch our overview video on the book of Song of Songs,"+\
                    "which breaks down the literary design of the book and "+\
                    "its flow of thought.",
                "series": "Old Testament, Poetic Book",
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
    references: List[BibleVideoRefObj] = []
    videoLink: AnyUrl
    description: str
    series: str
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Overview: song of songs",
                "references": [{
                    "bookCode": "sng",
                    "chapter": 10,
                    "verseStart": 1,
                    "verseEnd": 7
                }],
                "videoLink": "https://someplace.com/resoucesid",
                "description": "Watch our overview video on the book of Song of Songs,"+\
                    "which breaks down the literary design of the book and "+\
                    "its flow of thought.",
                "series": "Old Testament",
                "active": True

            }
        }

class BibleVideoEdit(BaseModel):
    '''Input object of Bible Video update'''
    title: str
    references: List[BibleVideoRefObj]  = None
    videoLink: AnyUrl  = None
    description: str  = None
    series: str  = None
    active: bool  = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Overview: song of songs",
                "references": [{
                    "bookCode": "sng",
                    "chapter": 10,
                    "verseStart": 1,
                    "verseEnd": 7
                }],
                "videoLink": "https://anotherplace.com/resoucesid",
                "description": "Watch our overview video on the book of Song of Songs,"+\
                    "which breaks down the literary design of the book and "+\
                    "its flow of thought.",
                "series": "Old Testament, Poetic Book",
                "active": True
            }
        }
