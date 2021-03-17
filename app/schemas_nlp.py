'''Defines all input and output classes for translation Apps related API endpoints'''

from typing import List, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from schemas import LangCodePattern, BookCodePattern


class TranslationDocumentType(Enum):
    '''Currently supports bible USFM only. Can be extended to
    CSV(for commentary or notes), doc(stories, other passages) etc.'''
    USFM = 'Bible USFM'

class TranslationProjectCreate(BaseModel):
    '''Input object for project creation'''
    projectName: str = Field(..., example="Hindi Malayalam Gospels")
    sourceLanguageCode : LangCodePattern =Field(...,example='hin')
    targetLanguageCode : LangCodePattern =Field(...,example='mal')
    documentFormat: TranslationDocumentType = TranslationDocumentType.USFM
    books: List[BookCodePattern] = Field(None, example=['mat', 'mrk'])
    active: bool = True

class TranslationProject(BaseModel):
    '''Output object for project creation'''
    projectId: int= Field(..., example=100001)
    projectName: str= Field(..., example="Hindi Malayalam Gospels")
    sourceLanguageCode : LangCodePattern = Field(..., example='hin')
    targetLanguageCode : LangCodePattern = Field(..., example='mal')
    documentFormat: TranslationDocumentType
    books: List[BookCodePattern] = Field(..., example=['mat', 'mrk', 'luk', 'jhn'])
    active: bool
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class TranslationProjectEdit(BaseModel):
    '''Input object for project updation'''
    projectId: int = Field(..., example=100001)
    # targetLanguageCode : LangCodePattern = None
    books: List[BookCodePattern] = Field(None, example=['luk', 'jhn'])
    active: bool = None

class TranslationProjectUpdateResponse(BaseModel):
    '''Response for post and put'''
    message:str = Field(...,example="Project created/updated successfully")
    data: TranslationProject = None

class TokenOccurence(BaseModel):
    '''Object for token occurence'''
    sentenceId: int = Field(..., example=41001001)
    offset: List[int] = Field(..., min_items=2, max_items=2, example=(0,8))

class Token(BaseModel):
    '''Response object for token'''
    token: str = Field(..., example='इब्राहीम')
    occurences: List[TokenOccurence]
    translations: List[str] = Field(..., example=['അബ്രാഹാമിന്റെ', 'അബ്രാഹാം'])
    metaData: dict = Field(None, example={"translationWord": "Abraham",
    	"link": "https://git.door43.org/unfoldingWord/en_tw/src/branch/master/bible/names/abraham.md"})
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class TokenUpdate(BaseModel):
    '''Input object for applying token translation'''
    token: str = Field(..., example="इब्राहीम")
    occurences: List[TokenOccurence]
    translation: str = Field(..., example="അബ്രാഹാമിന്റെ")

class Draft(BaseModel):
    '''Response object for plain-text draft'''
    sentenceId: int
    sentence: str
    draft: str
    draftMeta: List[Tuple[Tuple[int, int], Tuple[int,int],'str']]
    class Config: # pylint: disable=too-few-public-methods
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class DraftInput(BaseModel):
    '''Input sentences for translation'''
    sentenceId: int = Field(..., example=41001001)
    sentence: str = Field(...,
    	example="इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है")
    draft: str = None
    draftMeta: List[Tuple[Tuple[int, int], Tuple[int,int],'str']] = None

class DraftFormats(Enum):
    '''Specify various export,view,download formats for project/draft'''
    TEXT = 'plain-text'
    USFM = 'Bible USFM'
    JSON = 'Export JSON'

class Suggestion(BaseModel):
    '''Response object for suggestion'''
    suggestion:str
    score: float

class Stopwords(BaseModel):
    '''Input object for stopwords'''
    prepositions: List[str]
    postpositions: List[str]
