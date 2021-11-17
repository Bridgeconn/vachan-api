'''Input and Ourput object definitions for graphQL'''
import graphene
from graphene.types import Scalar

#Data clases have few public methods methods
class Metadata(Scalar):
    '''metadata representing JSON'''
    @staticmethod
    def serialize(dt_):
        '''process the response'''
        return dt_

class ContentType(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''output object for content types'''
    contentId = graphene.ID()
    contentType = graphene.String(description="Use values bible, commentary, dictionary etc")

class Language(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''output object for Language'''
    languageId = graphene.Int()
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = Metadata()

class LicensePermission(graphene.Enum):
    '''available choices for permission'''
    commercial = "Commercial_use"
    modification = "Modification"
    distribution = "Distribution"
    patent = "Patent_use"
    private = "Private_use"


class License(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Return object of licenses'''
    name = graphene.String()
    code = graphene.String()
    license = graphene.String()
    permissions = graphene.List(LicensePermission)
    active = graphene.Boolean()

class Version(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Return object of version'''
    versionId = graphene.ID()
    versionAbbreviation = graphene.String()
    versionName = graphene.String()
    revision = graphene.Int()
    metaData = Metadata()

class Source(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Return object of source'''
    sourceName = graphene.String()
    contentType = graphene.Field(ContentType)
    language = graphene.Field(Language)
    version = graphene.Field(Version)
    year = graphene.Int()
    license = graphene.Field(License)
    metaData = Metadata()
    active = graphene.Boolean()


class BibleBook(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''response object of Bible book'''
    bookId = graphene.ID()
    bookName = graphene.String()
    bookCode = graphene.String()

class AudioBible(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''output object for AudioBible'''
    name = graphene.String()
    url = graphene.String()
    book = graphene.Field(BibleBook)
    format = graphene.String()
    active = graphene.Boolean()

class BibleContent(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''output object for Biblecontent'''
    book = graphene.Field(BibleBook)
    USFM = graphene.String()
    JSON = Metadata()
    audio = graphene.Field(AudioBible)
    active = graphene.Boolean()

class Versification(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Format of versification response'''
    maxVerses = Metadata()
    mappedVerses = Metadata()
    excludedVerses = Metadata()
    partialVerses = Metadata()

class Reference(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response object of bible refernce'''
    bible = graphene.String()
    book = graphene.String()
    chapter = graphene.Int()
    verseNumber = graphene.Int()
    verseNumberEnd = graphene.Int()

class BibleVerse(graphene.ObjectType):
    '''output object for a verse'''
    refId = graphene.ID()
    refString = graphene.String()
    reference = graphene.Field(Reference)
    verseText = graphene.String()
    # footNotes = graphene.List(graphene.String)
    # crossReferences  = graphene.List(graphene.String)

    #pylint: disable=E1136
    def resolve_refobject(parent, _): #pylint: disable=E0213
        '''resolver'''
        return parent['reference']

    def resolve_refstring(parent, _):  #pylint: disable=E0213
        '''resolver'''
        if ('verseNumberEnd' in parent['reference'] and
            parent['reference']['verseNumberEnd'] is not None):
            return '%s %s:%s-%s'%(parent['reference']['book'], parent['reference']['chapter'],
                parent['reference']['verseNumber'], parent['reference']['verseNumberEnd'])
        return '%s %s:%s'%(parent['reference']['book'], parent['reference']['chapter'],
            parent['reference']['verseNumber'])

class Commentary(graphene.ObjectType):
    '''Response for Commentary'''
    refString =  graphene.String()
    book = graphene.Field(BibleBook)
    chapter = graphene.Int()
    verseStart = graphene.Int()
    verseEnd = graphene.Int()
    commentary = graphene.String()
    active = graphene.Boolean()

    #pylint: disable=E1101
    def resolve_refstring(parent, _):#pylint: disable=E0213
        '''resolver'''
        if parent.chapter == 0:
            return '%s introduction'%(parent.book.bookCode)
        if parent.chapter == -1:
            return '%s epilogue'%(parent.book.bookCode)
        if parent.verseStart == 0:
            return '%s %s introduction'%(parent.book.bookCode, parent.chapter)
        if parent.verseStart == -1:
            return '%s %s epilogue'%(parent.book.bookCode, parent.chapter)
        if parent.verseEnd is None or parent.verseEnd == 0:
            return '%s %s:%s'%(parent.book.bookCode, parent.chapter, parent.verseStart)
        return '%s %s:%s-%s'%(parent.book.bookCode, parent.chapter, parent.verseStart,
            parent.verseEnd)
    def resolve_book(parent, _):#pylint: disable=E0213
        '''resolver'''
        return parent.book

class DictionaryWord(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response object for dictionary word'''
    word = graphene.String()
    details = Metadata()
    active = graphene.Boolean()

class Infographic(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response for Infographics'''
    book = graphene.Field(BibleBook)
    title = graphene.String()
    infographicLink = graphene.String()
    active = graphene.Boolean()

class BibleVideo(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response for BibleVideo'''
    title = graphene.String()
    books = graphene.List(graphene.String)
    videoLink = graphene.String()
    description = graphene.String()
    theme = graphene.String()
    active = graphene.Boolean()

class TranslationDocumentType(graphene.Enum):
    '''Currently supports bible USFM only. Can be extended to
    CSV(for commentary or notes), doc(stories, other passages) etc.'''
    USFM = 'usfm'
    TEXT = 'text'
    CSV = 'csv'
    JSON = 'alignment-json'

class ProjectUser(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Input object for AgMT user update'''
    project_id = graphene.ID()
    userId = graphene.Int()
    userRole = graphene.String()
    metaData = Metadata()
    active = graphene.Boolean()

class TranslationProject(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Output object for project creation'''
    projectId = graphene.ID()
    projectName = graphene.String()
    sourceLanguage = graphene.Field(Language)
    targetLanguage = graphene.Field(Language)
    documentFormat = TranslationDocumentType()
    users = graphene.List(ProjectUser)
    metaData = Metadata()
    active = graphene.Boolean()

class TokenOccurence(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Object for token occurence'''
    sentenceId = graphene.ID()
    offset = graphene.List(graphene.Int)

class Token(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response object for token'''
    token = graphene.String()
    occurrences = graphene.List(TokenOccurence)
    translations = Metadata(name="translationSuggestions")
    metaData = Metadata()

class TokenTranslation(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''For translation/draft of a specific token'''
    token = graphene.String()
    translation = graphene.String()
    occurrence = graphene.Field(TokenOccurence)
    status = graphene.String()

class Sentence(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response object for sentences and plain-text draft'''
    sentenceId = graphene.ID()
    sentence = graphene.String()
    draft = graphene.String()
    draftMeta = Metadata()

class Progress(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response object for AgMT project progress'''
    confirmed = graphene.Float()
    suggestion = graphene.Float()
    untranslated = graphene.Float()

class Gloss(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Output object for translation memory or gloss'''
    token = graphene.String()
    translations = Metadata()
    metaData = Metadata()

class Suggestion(graphene.ObjectType):#pylint: disable=too-few-public-methods
    '''Response object for suggestion'''
    suggestion = graphene.String()
    score = graphene.Float()

###################### Input Types ###############################

class SentenceInput(graphene.InputObjectType):
    '''Input sentences for tokenization'''
    sentenceId = graphene.ID(required=True)
    sentence = graphene.String(required=True)
    draft = graphene.String(default_value="")
    draftMeta = graphene.JSONString(default_value=None,
        description="The draftMeta JSON in response object(Sentence)"+\
        " should be provided here as a JSON-String")

class Stopwords(graphene.InputObjectType):
    '''Input object for stopwords'''
    prepositions = graphene.List(graphene.String,
        description='example=["कोई", "यह", "इस","इसे", "उस", "कई","इसी", "अभी", "जैसे"]')
    postpositions= graphene.List(graphene.String,
        description='example=["के", "का", "में", "की", "है", "और", "से", "हैं", "को", "पर"]')

class IndexPair(graphene.InputObjectType):
    '''Index pair showing alignment of soure token and target Token'''
    sourceTokenIndex = graphene.Int(required=True)
    targetTokenIndex = graphene.Int(required=True)

class Alignment(graphene.InputObjectType):
    '''Import object of alignment data for learning'''
    sourceTokenList = graphene.List(graphene.String, required=True,
        description='example=["This", "is", "an", "apple"]')
    targetTokenList = graphene.List(graphene.String, required=True,
        description='example=["यह","एक","सेब","है"]')
    alignedTokens = graphene.List(IndexPair, required=True, description=''' example=[
        {"sourceTokenIndex": 0, "targetTokenIndex": 0},
        {"sourceTokenIndex": 1, "targetTokenIndex": 3},
        {"sourceTokenIndex": 2, "targetTokenIndex": 1},
        {"sourceTokenIndex": 3, "targetTokenIndex": 2} ]''')

class GlossInput(graphene.InputObjectType):
    '''Import object for glossary(dictionary) data for learning'''
    token = graphene.String(description='example="love"', required=True)
    translations = graphene.List(graphene.String,
        description="example=['प्यार', 'प्रेम', 'प्रेम करना']")
    tokenMetaData = graphene.JSONString(description='example={"word-class":["noun", "verb"]}')

class TokenOccurenceInput(graphene.InputObjectType):
    '''Object for token occurence'''
    sentenceId = graphene.ID()
    offset = graphene.List(graphene.Int)

class TokenUpdate(graphene.InputObjectType):
    '''Input object for applying token translation'''
    token = graphene.String(required=True)
    occurrences = graphene.List(TokenOccurenceInput, required=True)
    translation = graphene.String(required=True)

class DraftInput(graphene.InputObjectType):
    '''Input sentences for translation'''
    sentenceId = graphene.ID()
    sentence = graphene.String(required=True,
        description='example="इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है"')
    draft = graphene.String(required=True,
        description='example="അബ്രാഹാം के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है"')
    draftMeta = graphene.JSONString()

class SugggestTranslationInput(graphene.InputObjectType):
    """Body content for transaltion"""
    sentence_list = graphene.List(SentenceInput,\
        required=True)
    stopwords = graphene.Field(Stopwords)
    punctuations = graphene.List(graphene.String,\
        description="""List [ ",", "\"", "!", ".", ":", ";", "\n""]""")

################### Graphql mutation types ###########################
class InputAddLang(graphene.InputObjectType):
    """ADD Language Input"""
    language = graphene.String(required=True)
    code = graphene.String(required=True,\
    description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString(description="Expecting a dictionary Type")

class InputUpdateLang(graphene.InputObjectType):
    """ update Language Input """
    languageId = graphene.Int(required=True)
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString(description="Expecting a dictionary Type")

class InputContentType(graphene.InputObjectType):
    """ update Language Input """
    contentType = graphene.String(required=True,\
        description="Input object to ceate a new content type : pattern: ^[a-z]+$ :\
        example: commentary")

class InputAddLicense(graphene.InputObjectType):
    """Add license Input"""
    name = graphene.String(required=True)
    code = graphene.String(required=True,\
        description="pattern: '^[a-zA-Z0-9\\.\\_\\-]+$'")
    license = graphene.String(required=True)
    permissions = graphene.List(LicensePermission, \
        default_value =["Private_use"],\
        description="Expecting a list \
        [ Commercial_use, Modification, Distribution, Patent_use, Private_use ]")

class InputEditLicense(graphene.InputObjectType):
    """Edit license Input"""
    name = graphene.String()
    code = graphene.String(required=True,description=\
        "pattern: ^[a-zA-Z0-9\\.\\_\\-]+$")
    license = graphene.String()
    permissions = graphene.List(LicensePermission, default_value =\
        ["Private_use"],\
        description="Expecting a list\
        [ Commercial_use, Modification, Distribution, Patent_use, Private_use ]")
    active = graphene.Boolean()

class InputAddVersion(graphene.InputObjectType):
    """Input for Edit versions"""
    versionAbbreviation = graphene.String(required=True,\
        description="pattern: ^[A-Z]+$")
    versionName = graphene.String(required=True)
    revision = graphene.Int(default_value = 1)
    metaData = graphene.JSONString(default_value = None,\
    description="Expecting a dictionary Type JSON String")

class InputEditVersion(graphene.InputObjectType):
    """Input for Edit versions"""
    versionId = graphene.ID(required=True)
    versionAbbreviation = graphene.String(\
        description="pattern: ^[A-Z]+$")
    versionName = graphene.String()
    revision = graphene.Int()
    metaData = graphene.JSONString(description="Expecting a dictionary Type JSON String")

class InputAddSource(graphene.InputObjectType):
    """Add Source Input"""
    contentType  = graphene.String(required=True)
    language = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    version = graphene.String(required=True,\
        description="pattern:^[A-Z]+$")
    revision = graphene.String(default_value = 1,\
        description="default: 1")
    year = graphene.Int(required=True)
    license = graphene.String(default_value = "CC-BY-SA",\
        description="pattern: ^[a-zA-Z0-9\\.\\_\\-]+$")
    metaData = graphene.JSONString(description="Expecting a dictionary Type JSON String")

class InputEditSource(graphene.InputObjectType):
    """Edit Source Input"""
    sourceName = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    contentType  = graphene.String()
    language = graphene.String(description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    version = graphene.String(description="pattern:^[A-Z]+$")
    revision = graphene.String(description="default: 1")
    year = graphene.Int()
    license = graphene.String(description="pattern: ^[a-zA-Z0-9\\.\\_\\-]+$")
    metaData = graphene.JSONString(description="Expecting a dictionary Type JSON String")
    active = graphene.Boolean()

class InputBibleDict(graphene.InputObjectType):
    """Add Bible Dict"""
    USFM = graphene.String()
    JSON = graphene.JSONString(description="Provide JSON structure\
         obtained from USFM-Grammar or one like that")

class BibleEditDict(graphene.InputObjectType):
    """bible books inputs"""
    book_code = graphene.String(
        description="pattern:^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")
    USFM = graphene.String(description="USFM Data")
    JSON = graphene.JSONString(description="Provide JSON structure obtained\
        from USFM-Grammar or one like that")
    active = graphene.Boolean(default_value = True)

class AudioAdddict(graphene.InputObjectType):
    """audio input"""
    name = graphene.String(required=True)
    url = graphene.String(required=True)
    books = graphene.List(graphene.String,required=True)
    format = graphene.String(required=True)
    active = graphene.Boolean(default_value = True)

class AudioEditdict(graphene.InputObjectType):
    """audio input"""
    name = graphene.String()
    url = graphene.String()
    books = graphene.List(graphene.String,required=True)
    format = graphene.String()
    active = graphene.Boolean(default_value = True)

class CommentaryDict(graphene.InputObjectType):
    """commentary input"""
    bookCode = graphene.String(required=True)
    chapter = graphene.Int(required=True)
    verseStart = graphene.Int()
    verseEnd = graphene.Int()
    commentary = graphene.String(required=True)
    active = graphene.Boolean(default_value = True)

class CommentaryEditDict(graphene.InputObjectType):
    """commentary Edit input"""
    bookCode = graphene.String(required=True)
    chapter = graphene.Int(required=True)
    verseStart = graphene.Int()
    verseEnd = graphene.Int()
    commentary = graphene.String()
    active = graphene.Boolean(default_value = True)

class InputCreateAGMTProject(graphene.InputObjectType):
    """CreateAGMTProject Input"""
    projectName = graphene.String(required=True,\
        description="example: Hindi Malayalam Gospels")
    sourceLanguageCode = graphene.String(required=True,\
        description="pattern:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    targetLanguageCode = graphene.String(required=True,\
        description="pattern:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    documentFormat = graphene.Field(TranslationDocumentType)
    useDataForLearning = graphene.Boolean()
    stopwords = graphene.Field(Stopwords)
    punctuations = graphene.List(graphene.String,\
        description="""List [ ",", "\"", "!", ".", ":", ";", "\n""]""")
    active = graphene.Boolean(default_value=True)

class InputSeclectedBooks(graphene.InputObjectType):
    """List of selected books from an existing bible in the server"""
    bible = graphene.String(required=True,\
        description = "pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$\
        example: hi_IRV_1_bible")
    books = graphene.List(graphene.String,required=True,\
        description = "pattern: ^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$\
        example: [ 'luk', 'jhn' ]")

class InputEditAGMTProject(graphene.InputObjectType):
    """CreateAGMTProject Input"""
    projectId = graphene.Int(required=True)
    projectName = graphene.String(\
        description="example: Hindi Malayalam Gospels")
    selectedBooks = graphene.Field(InputSeclectedBooks)
    uploadedUSFMs = graphene.List(graphene.String)
    useDataForLearning = graphene.Boolean()
    stopwords = graphene.Field(Stopwords)
    punctuations = graphene.List(graphene.String,\
        description="""List [ ",", "\"", "!", ".", ":", ";", "\n""]""")
    active = graphene.Boolean(default_value=True)

class AGMTUserCreateInput(graphene.InputObjectType):
    """input of AGMT user create"""
    project_id = graphene.Int(required=True)
    user_id = graphene.Int(required=True)

class AGMTUserEditInput(graphene.InputObjectType):
    """input of AGMT user Edit"""
    project_id = graphene.Int(required=True)
    userId = graphene.Int(required=True)
    userRole = graphene.String()
    metaData = graphene.JSONString()
    active = graphene.Boolean()

class BibleVideoDict(graphene.InputObjectType):
    """BibleVideo input"""
    title = graphene.String(required=True)
    books = graphene.List(graphene.String,required=True,\
        description="provide book codes")
    videoLink = graphene.String(required=True)
    description = graphene.String(required=True)
    theme = graphene.String(required=True)
    active = graphene.Boolean(default_value = True)

class InputAddBibleVideo(graphene.InputObjectType):
    """Add BibleVideo Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    video_data = graphene.List(BibleVideoDict)

class BibleVideoEditDict(graphene.InputObjectType):
    """BibleVideo Edit input"""
    title = graphene.String(required=True)
    books = graphene.List(graphene.String)
    videoLink = graphene.String()
    description = graphene.String()
    theme = graphene.String()
    active = graphene.Boolean(default_value = True)

class InputEditBibleVideo(graphene.InputObjectType):
    """Edit BibleVideo Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    video_data = graphene.List(BibleVideoEditDict)

class DictionaryDict(graphene.InputObjectType):
    """Dictionary input"""
    word = graphene.String(required=True)
    details = graphene.JSONString(description="Expecting a dictionary Type")
    active = graphene.Boolean(default_value = True)

class InputAddDictionary(graphene.InputObjectType):
    """Add Dictionary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    word_list = graphene.List(DictionaryDict)

class DictionaryEditDict(graphene.InputObjectType):
    """Dictionary input"""
    word = graphene.String(required=True)
    details = graphene.JSONString(description="Expecting a dictionary Type")
    active = graphene.Boolean(default_value = True)

class InputEditDictionary(graphene.InputObjectType):
    """Add Dictionary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    word_list = graphene.List(DictionaryEditDict)

class InfographicDict(graphene.InputObjectType):
    """Infographic input"""
    bookCode = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")
    title = graphene.String(required=True)
    infographicLink = graphene.String(required=True,\
        description="Provide valid URL")
    active = graphene.Boolean(default_value = True)

class InputAddInfographic(graphene.InputObjectType):
    """Add Infographic Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    data = graphene.List(InfographicDict)

class InfographicEditDict(graphene.InputObjectType):
    """Infographic Edit input"""
    bookCode = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z1-9][a-zA-Z][a-zA-Z]$")
    title = graphene.String(required=True)
    infographicLink = graphene.String(\
        description="Provide valid URL")
    active = graphene.Boolean(default_value = True)

class InputEditInfographic(graphene.InputObjectType):
    """Edit Infographic Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    data = graphene.List(InfographicEditDict)

class InputApplyToken(graphene.InputObjectType):
    """Inputs for Aplly Token"""
    project_id = graphene.Int(required=True)
    return_drafts = graphene.Boolean(default_value = True)
    token = graphene.List(TokenUpdate)

class InputAutoTranslation(graphene.InputObjectType):
    """Auto Translation Suggestion input"""
    project_id  = graphene.Int(required=True)
    books = graphene.List(graphene.String)
    sentence_id_list = graphene.List(graphene.Int,\
        description="List of sentance id BCV")
    sentence_id_range = graphene.List(graphene.Int,\
        description="List of sentance range BCV , 2 values in list")
    confirm_all = graphene.Boolean(default_value = False)

class InputAddGloss(graphene.InputObjectType):
    """Add Gloss input"""
    source_language = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    target_language  = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    data = graphene.List(GlossInput,required=True)

class InputAddAlignment(graphene.InputObjectType):
    """Add Alignement input"""
    source_language = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    target_language  = graphene.String(required=True,\
        description="patten:^[a-zA-Z]+(-[a-zA-Z0-9]+)*$")
    data = graphene.List(Alignment,required=True)

class InputAddBible(graphene.InputObjectType):
    """Add Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    books = graphene.List(InputBibleDict,required=True,\
        description="Must Provide One of the Two USFM or JSON")

class InputEditBible(graphene.InputObjectType):
    """Edit Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    books = graphene.List(BibleEditDict,\
        description="Either JSON or USFM should provide")

class InputAddAudioBible(graphene.InputObjectType):
    """Add Audio Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    audio_data = graphene.List(AudioAdddict)

class InputEditAudioBible(graphene.InputObjectType):
    """Edit Audio Bible Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    audio_data = graphene.List(AudioEditdict)

class InputAddCommentary(graphene.InputObjectType):
    """Add commentary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    commentary_data = graphene.List(CommentaryDict)

class InputEditCommentary(graphene.InputObjectType):
    """Edit commentary Input"""
    source_name = graphene.String(required=True,\
        description="pattern: ^[a-zA-Z]+(-[a-zA-Z0-9]+)*_[A-Z]+_\\w+_[a-z]+$")
    commentary_data = graphene.List(CommentaryEditDict)
