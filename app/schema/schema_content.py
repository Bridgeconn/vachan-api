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
    audioId: int
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
    '''Response object of parascript reference'''
    bible : TableNamePattern = None
    book: BookCodePattern = None
    chapter: int = None
    verseNumber: int = None
    bookEnd: BookCodePattern = None
    chapterEnd: int = None
    verseEnd: int = None

    @validator('chapter', 'chapterEnd')
    def check_chapter(cls, val): # pylint:  disable=E0213
        '''chapter fields should be greater than or equal to -1'''
        if val is not None and val < -1:
            raise ValueError('chapter field should be greater than or equal to -1')
        return val

    @validator('verseNumber', 'verseEnd')
    def check_verses(cls, val, values): # pylint:  disable=E0213
        '''verse fields should be greater than or equal to -1'''
        if 'chapter' in values and values['chapter'] in [-1, 0]:
            if val not in [-1, 0, None]:
                raise ValueError('verse fields should be 0 for book introductions and epilogues')
            val = 0
        if val is not None and  val < -1:
            raise ValueError('verse fields should be greater than or equal to -1')
        return val
    @validator('chapterEnd')
    def check_chapter_range(cls, val, values): # pylint:  disable=E0213
        '''chapter start should be less than or equal to chapter end'''
        if 'chapter' in values and val < values['chapter']:
            raise ValueError('chapter start should be less than or equal to chapter end')
        return val
    def check_verse_range(cls, val, values): # pylint:  disable=E0213
        '''verse start should be less than or equal to verse end'''
        if 'verseNumber' in values and val < values['verseNumber']:
            raise ValueError('verse start should be less than or equal to verse end')
        return val
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "book": "mat",
                "chapter": 1,
                "verseNumber": 12,
                "bookEnd": "luk",
                "chapterEnd": 10,
                "verseEnd": 20
            }
        }
class BibleBookContent(BaseModel):
    '''Response object of Bible book contents'''
    bookContentId : int = None
    audioId : int = None
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
                "bookContentId": 1,
                "audioId": 100000,
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
    def check_for_usfm_json(cls, values): # pylint: disable=E0213
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
    def check_for_usfm_json(cls, values): # pylint:  disable=E0213
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
    def check_verses(cls, val, values): # pylint:  disable=E0213
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
    def check_range(cls, val, values): # pylint: disable=E0213
        '''verse start should be less than or equal to verse end'''
        if 'verseStart' in values and val < values['verseStart']:
            raise ValueError('verse start should be less than or equal to verse end')
        return val

    @validator('chapter')
    def check_chapter(cls, val): # pylint:  disable=E0213
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
    def check_verses(cls, val, values): # pylint: disable=E0213
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
    def check_range(cls, val, values): # pylint:  disable=E0213
        '''verse start should be less than or equal to verse end'''
        if 'verseStart' in values and val < values['verseStart']:
            raise ValueError('verse start should be less than or equal to verse end')
        return val

    @validator('chapter')
    def check_chapter(cls, val): # pylint:  disable=E0213
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
    commentaryId: int
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
                "commentaryId":100000,
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
class VocabularyWordCreate(BaseModel):
    '''Upload object of vocabulary word'''
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

class VocabularyWordEdit(BaseModel):
    '''Upload object of vocabulary word'''
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

class VocabularyWordResponse(BaseModel):
    '''Response object of vocabulary word'''
    wordId: int = None
    word: str
    details: dict = None
    active: bool = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "wordId": 100000,
                "word": "Adam",
                "details": {"type": "person",
                    "definition": "The first man God created."},
                "active": True
            }
        }

class VocabularyCreateResponse(BaseModel):
    '''Response object of vocabulary word update'''
    message: str = Field(..., example="Vocabulary words added successfully")
    data: List[VocabularyWordResponse] = None

class VocabularyUpdateResponse(BaseModel):
    '''Response object of vocabulary word update'''
    message: str = Field(..., example="Vocabulary words updated successfully")
    data: List[VocabularyWordResponse] = None

class ParascriptResponse(BaseModel):
    '''Response object of parascripturals'''
    parascriptId : int
    category: str
    title: str
    description: str = None
    content: str = None
    reference: Reference = None
    link: AnyUrl = None
    metaData: dict = None
    active: bool = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "parascriptId": 100000,
                "category": "Bible project video",
                "title": "Bible Video of Genesis",
                "description": "Day's theme or some sub title if available",
                "content": "some detailed content",
                "reference": {"book":"MAT", "chapter":2, "verseNumber":3,
                               "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
                "link": "http://someplace.com/resoucesid",
                "metaData": {"key": "value"},
                "active": True
            }
        }
class ParascriptEdit(BaseModel):
    '''Input object of parascriptuals update'''
    category: str
    title: str
    description: str = None
    content: str = None
    reference: Reference = None
    link: AnyUrl = None
    active: bool = None
    metaData: dict = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "category": "Bible project video",
                "title": "Bible Video of Genesis",
                "description": "updated description",
                "content": "updated content",
                "reference": {"book":"MRK", "chapter":11, "verseNumber":12,
                               "bookEnd":"LUK", "chapterEnd":14, "verseEnd":15 },
                "link": "http://someplace.com/newresoucesid",
                "metaData": {"newkey": "newvalue"},
                "active": True
            }
        }
class ParascriptUpdateResponse(BaseModel):
    '''Response object of parascripturals update'''
    message: str = Field(..., example="Parascripturals updated successfully")
    data: List[ParascriptResponse] = None

class ParascriptCreateResponse(BaseModel):
    '''Response object of parascripturals update'''
    message: str = Field(..., example="Parascripturals added successfully")
    data: List[ParascriptResponse] = None

class ParascripturalCreate(BaseModel):
    '''Input object for parascripturals'''
    category: str
    title: str
    description: str = None
    content: str = None
    reference: Reference = None
    link: AnyUrl = None
    metaData: dict = None
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "category": "Bible project video",
                "title": "Bible Video of Genesis",
                "description": "Day's theme or some sub title if available",
                "content": "some detailed content",
                "reference": {"book":"MAT", "chapter":2, "verseNumber":3,
                               "bookEnd":"JHN", "chapterEnd":5, "verseEnd":6 },
                "link": "http://someplace.com/resoucesid",
                "metaData": {"key": "value"},
                "active": True
            }
        }

class SignVideoResponse(BaseModel):
    '''Response object of sign bible videos'''
    signVideoId : int
    title: str = None
    description: str = None
    reference: Reference = None
    link: AnyUrl = None
    metaData: dict = None
    active: bool = None
    class Config:
        ''' telling Pydantic that "it's OK if I pass a non-dict value'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "signVideoId": 100000,
                "title": "Sign Bible Video of Genesis",
                "description": "Day's theme or some sub title if available",
                "reference": {"book":"GEN", "chapter":1, "verseNumber":1,
                               "bookEnd":"GEN", "chapterEnd":10, "verseEnd":10 },
                "link": "http://someplace.com/resoucesid",
                "metaData": {"key": "value"},
                "active": True
            }
        }
class SignVideoEdit(BaseModel):
    '''Input object of sign bible videos update'''
    signVideoId: int
    title: str = None
    description: str = None
    reference: Reference = None
    link: AnyUrl = None
    active: bool = None
    metaData: dict = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "signVideoId":100000,
                "title": "Sign Bible Video of Mathewss",
                "description": "updated description",
                "reference": {"book":"MAT", "chapter":2, "verseNumber":10,
                               "bookEnd":"MAT", "chapterEnd":12, "verseEnd":15 },
                "link": "http://someplace.com/newresoucesid",
                "metaData": {"newkey": "newvalue"},
                "active": True
            }
        }
class SignVideoUpdateResponse(BaseModel):
    '''Response object of sign bible videos update'''
    message: str = Field(..., example="Sign Bible Video updated successfully")
    data: List[SignVideoResponse] = None

class SignVideoCreateResponse(BaseModel):
    '''Response object of sign bible videos update'''
    message: str = Field(..., example="Sign Bible Video added successfully")
    data: List[SignVideoResponse] = None

class SignVideoCreate(BaseModel):
    '''Input object for sign bible video'''
    title: str
    description: str = None
    reference: Reference = None
    link: AnyUrl = None
    metaData: dict = None
    active: bool = True
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "title": "Sign Bible Video of Genesis",
                "description": "Day's theme or some sub title if available",
                "reference": {"book":"GEN", "chapter":1, "verseNumber":1,
                               "bookEnd":"GEN", "chapterEnd":10, "verseEnd":10 },
                "link": "http://someplace.com/resoucesid",
                "metaData": {"key": "value"},
                "active": True
            }
        }

class UploadedUsfm(BaseModel):
    '''Input object to upload a usfm string'''
    USFM :str
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "USFM": "\\id MAT\n\\c 1\n\\p\n\\v 1 इब्राहीम की सन्‍तान, दाऊद की ...",
            }
        }
