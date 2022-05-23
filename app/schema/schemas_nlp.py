'''Defines all input and output classes for translation Apps related API endpoints'''
from typing import List, Tuple
from enum import Enum
from pydantic import BaseModel, Field, constr, root_validator

from schema.schemas import LangCodePattern, TableNamePattern, LanguageResponse
from schema.schema_content import BookCodePattern, Job

#pylint: disable=too-few-public-methods
class TranslationDocumentType(Enum):
    '''Currently supports bible USFM only. Can be extended to
    CSV(for commentary or notes), doc(stories, other passages) etc.'''
    USFM = 'usfm'
    TEXT = 'text'
    CSV = 'csv'
    JSON = 'alignment-json'

class Stopwords(BaseModel):
    '''Input object for stopwords'''
    prepositions: List[str] = Field(...,
        example=["कोई", "यह", "इस","इसे", "उस", "कई","इसी", "अभी", "जैसे"])
    postpositions: List[str] = Field(...,
        example=["के", "का", "में", "की", "है", "और", "से", "हैं", "को", "पर"])

class ProjectUser(BaseModel):
    '''Input object for AgMT user update'''
    project_id: int
    userId: str
    userRole: str = Field(None, example='projectOwner')
    metaData: dict = Field(None, example={
        "lastProject":100002, "lastFilter":{"book":"mat","chapter":28}})
    active: bool =None
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class UserUpdateResponse(BaseModel):
    '''Response for user addition and updation on AgMT project'''
    message: str = Field(..., example='User added to/updated in project successfully')
    data: ProjectUser

class TranslationProjectCreate(BaseModel):
    '''Input object for project creation'''
    projectName: str = Field(..., example="Hindi Malayalam Gospels")
    sourceLanguageCode : LangCodePattern =Field(...,example='hi')
    targetLanguageCode : LangCodePattern =Field(...,example='ml')
    documentFormat: TranslationDocumentType = TranslationDocumentType.USFM
    useDataForLearning: bool = True
    stopwords: Stopwords = None
    punctuations: List[constr(max_length=1)] = Field(None,
        example=[',', '"', '!', '.', ':', ';', '\n', '\\','“','”',
        '“','*','।','?',';',"'","’","(",")","‘","—"])
    active: bool = True

class TranslationProject(BaseModel):
    '''Output object for project creation'''
    projectId: int= Field(..., example=100001)
    projectName: str= Field(..., example="Hindi Malayalam Gospels")
    sourceLanguage : LanguageResponse = Field(...)
    targetLanguage : LanguageResponse = Field(...)
    documentFormat: TranslationDocumentType
    users: List[ProjectUser] = None
    metaData: dict = Field(None, example={"books":['mat', 'mrk', 'luk', 'jhn'],
        "useDataForLearning":True})
    active: bool
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class SelectedBooks(BaseModel):
    '''List of selected books from an existing bible in the server'''
    bible: TableNamePattern = Field(..., example='hi_IRV_1_bible')
    books: List[BookCodePattern]= Field(..., example=['luk', 'jhn'])

class SentenceInput(BaseModel):
    '''Input sentences for tokenization'''
    sentenceId: str = Field(..., example=41001001)
    surrogateId: str= Field(None, example="MAT 1:1")
    sentence: str = Field(...,
        example="इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है")
    @root_validator
    def set_surrogate_id(cls, values): # pylint: disable=R0201 disable=E0213
        '''Set surrogate id value, if not provided and make id int'''
        if values['surrogateId'] is None:
            values['surrogateId'] = values['sentenceId']
        values['sentenceId'] = int(values['sentenceId'])
        return values

class TranslationProjectEdit(BaseModel):
    '''New books to be added or active flag change'''
    projectId: int
    projectName: str = None
    active: bool = None
    selectedBooks: SelectedBooks = None
    uploadedUSFMs: List[str] = None
    sentenceList: List[SentenceInput] = None
    useDataForLearning: bool = None
    stopwords: Stopwords = None
    punctuations: List[constr(max_length=1)] = None

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
    occurrences: List[TokenOccurence]
    translations: dict = Field(...,
        example={'അബ്രാഹാമിന്റെ':{"frequency":10}, 'അബ്രാഹാം':{"frequency":24}})
    metaData: dict = Field(None, example={"translationWord": "Abraham",
    	"link": "https://git.door43.org/unfoldingWord/en_tw/src/branch/master/bible/names/abraham.md"})
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class TokenUpdate(BaseModel):
    '''Input object for applying token translation'''
    token: str = Field(..., example="इब्राहीम")
    occurrences: List[TokenOccurence]
    translation: str = Field(..., example="അബ്രാഹാം")

class Sentence(BaseModel):
    '''Response object for sentences and plain-text draft'''
    sentenceId: int
    surrogateId: str
    sentence: str
    draft: str = None
    draftMeta: List[Tuple[Tuple[int, int], Tuple[int,int],'str']] = Field(None,
        example=[[[0,8], [0,8],"confirmed"],
            [[8,64],[8,64],"untranslated"]])
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class TranslateResponse(BaseModel):
    '''response object after applying token translations'''
    message: str = Field(..., example="Token translations saved")
    data:List[Sentence] = None

class DraftInput(BaseModel):
    '''Input sentences for translation'''
    sentenceId: str = Field(..., example=41001001)
    surrogateId: str= Field(None, example="MAT 1:1")
    sentence: str = Field(...,
    	example="इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है")
    draft: str = Field(None,
        example="അബ്രാഹാം के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है")
    draftMeta: List[Tuple[Tuple[int, int], Tuple[int,int],'str']] = Field(None,
        example=[[[0,8], [0,8],"confirmed"],
            [[8,64],[8,64],"untranslated"]])
    @root_validator
    def set_surrogate_id(cls, values): # pylint: disable=R0201 disable=E0213
        '''Set surrogate id value, if not provided and make id int'''
        if values['surrogateId'] is None:
            values['surrogateId'] = values['sentenceId']
        values['sentenceId'] = int(values['sentenceId'])
        return values


class DraftFormats(Enum):
    '''Specify various export,view,download formats for project/draft'''
    USFM = 'usfm'
    JSON = 'alignment-json'
    PRINT = 'print-json'

class Suggestion(BaseModel):
    '''Response object for suggestion'''
    suggestion:str
    score: float
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class Progress(BaseModel):
    '''Response object for AgMT project progress'''
    confirmed: float
    suggestion: float
    untranslated: float

class IndexPair(BaseModel):
    '''Index pair showing alignment of soure token and target Token'''
    sourceTokenIndex: int
    targetTokenIndex: int

class Alignment(BaseModel):
    '''Import object of alignment data for learning'''
    sourceTokenList: List[str] = Field(..., example=["This", "is", "an", "apple"])
    targetTokenList: List[str] = Field(..., example=["यह","एक","सेब","है"])
    alignedTokens: List[IndexPair] = Field(..., example=[
        {"sourceTokenIndex": 0, "targetTokenIndex": 0},
        {"sourceTokenIndex": 1, "targetTokenIndex": 3},
        {"sourceTokenIndex": 2, "targetTokenIndex": 1},
        {"sourceTokenIndex": 3, "targetTokenIndex": 2} ])

class GlossInput(BaseModel):
    '''Import object for glossary(dictionary) data for learning'''
    token: str = Field(..., example="love")
    translations: List[str] = Field(None, example=['प्यार', "प्रेम", "प्रेम करना"])
    tokenMetaData: dict = Field(None, example={"word-class":["noun", "verb"]})

class GlossOutput(BaseModel):
    '''Output object for translation memory or gloss'''
    token: str = Field(..., example="love")
    translations: dict = Field(None, example={'प्यार':3, "प्रेम":1.2,
        "प्रेम करना":0})
    metaData: dict = Field(None, example={"word-class":["noun", "verb"]})
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True

class GlossUpdateResponse(BaseModel):
    '''Response object for learn/gloss and learn/alignments'''
    message: str = Field(..., example="Added to glossary/Alignments used for learning")
    data: List[GlossOutput]

class Translation(BaseModel):
    '''Response of what is the current translation of a specific token in agmt'''
    token: str = Field(..., example="duck")
    translation: str = Field(..., example="താറാവ്")
    occurrence: TokenOccurence
    status: str = Field(..., example="confirmed")

class StopWordsType(Enum):
    '''Types of stop-words based on how they are generated'''
    SYSTEM = 'system defined'
    USER = 'user defined'
    AUTO = 'auto generated'

class StopWords(BaseModel):
    '''Response object for stop words'''
    stopWord: str = Field(..., example="और")
    stopwordType: StopWordsType = Field(None, example="Auto generated")
    confidence: float = Field(None, example=0.8)
    active : bool = Field(..., example=True)
    metaData: dict = Field(None, example={
        "type":'postposition'})
    @root_validator
    def set_stopword_type(cls, values): # pylint: disable=R0201 disable=E0213
        '''Set stopword type based on confidence score'''
        if values['stopwordType'] is None:
            if values['confidence'] == 2:
                values['stopwordType'] = StopWordsType.SYSTEM.value
            elif values['confidence'] == 1:
                values['stopwordType'] = StopWordsType.USER.value
            else:
                values['stopwordType'] = StopWordsType.AUTO.value
            if values['confidence'] in [1, 2]:
                values['confidence'] = None
        return values

class StopWordUpdate(BaseModel):
    '''Import object for updating stopword info'''
    stopWord: str = Field(..., example="और")
    active : bool = Field(None, example=True)
    metaData: dict = Field(None, example={
        "type":'postposition'})

class StopWordUpdateResponse(BaseModel):
    '''Response object after updating metadata or active status'''
    message: str = Field(..., example="Stopword info updated successfully")
    data: StopWords

class StopWordsAddResponse(BaseModel):
    '''Response object after adding new stopwords in db'''
    message: str = Field(..., example="3 stopwords added successfully")
    data:List[StopWords] = None

# class Job(BaseModel):
#     '''Response objects of Job'''
#     jobId: int = Field(..., example=100000)
#     status: str = Field(..., example="job created")
#     output: dict = Field(None, example={
#         'language':'hi',
#         'data': [{"stopWord": "और",
#                   "stopwordType": "auto generated",
#                   "confidence": 0.8,
#                   "active": True,
#                   "metaData": {
#                          "type": "postposition"
#                    }
#                 }]
#         })

class StopWordsGenerateResponse(BaseModel):
    '''Response object of auto-generate stopword API'''
    message: str = Field(..., example="Generating stop words in background")
    data: Job

class JobStatus(Enum):
    '''Types of job status'''
    CREATED = 'job created'
    STARTED = 'job started'
    IN_PROGRESS = 'job in progress'
    PENDING = 'job pending'
    ERROR = 'job error'
    FINISHED = 'job finished'

class JobCreateResponse(BaseModel):
    '''Response object of job create api'''
    message: str = Field(..., example="Job created successfully")
    data: Job

class JobStatusResponse(BaseModel):
    '''Response object for job'''
    message: str = Field(..., example="Automatically generated stopwords for the given language")
    data: Job
