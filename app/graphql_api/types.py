'''Input and Ourput object definitions for graphQL'''
import json
import graphene
from graphene.types import Scalar
from graphql.language import ast


#pylint: disable=too-few-public-methods

class Metadata(Scalar):
    '''metadata representing JSON'''
    @staticmethod
    def serialize(dt_):
        '''process the response'''
        return dt_

class ContentType(graphene.ObjectType):
    '''output object for content types'''
    contentId = graphene.ID()
    contentType = graphene.String(description="Use values bible, commentary, dictionary etc")

class Language(graphene.ObjectType):
    '''output object for Language'''
    # language_id = graphene.String()
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


class License(graphene.ObjectType):
    '''Return object of licenses'''
    name = graphene.String()
    code = graphene.String()
    license = graphene.String()
    permissions = graphene.List(LicensePermission)
    active = graphene.Boolean()

class Version(graphene.ObjectType):
    '''Return object of version'''
    versionId = graphene.ID()
    versionAbbreviation = graphene.String()
    versionName = graphene.String()
    revision = graphene.Int()
    metaData = Metadata()

class Source(graphene.ObjectType):
    '''Return object of source'''
    sourceName = graphene.String()
    contentType = graphene.Field(ContentType)
    language = graphene.Field(Language)
    version = graphene.Field(Version)
    year = graphene.Int()
    license = graphene.Field(License)
    metaData = Metadata()
    active = graphene.Boolean()


class BibleBook(graphene.ObjectType):
    '''response object of Bible book'''
    bookId = graphene.ID()
    bookName = graphene.String()
    bookCode = graphene.String()

class AudioBible(graphene.ObjectType):
    '''output object for AudioBible'''
    name = graphene.String()
    url = graphene.String()
    book = graphene.Field(BibleBook)
    format = graphene.String()
    active = graphene.Boolean()

class BibleContent(graphene.ObjectType):
    '''output object for Biblecontent'''
    book = graphene.Field(BibleBook)
    USFM = graphene.String()
    JSON = Metadata()
    audio = graphene.Field(AudioBible)
    active = graphene.Boolean()

class Versification(graphene.ObjectType):
    '''Format of versification response'''
    maxVerses = Metadata()
    mappedVerses = Metadata()
    excludedVerses = Metadata()
    partialVerses = Metadata()

class Reference(graphene.ObjectType):
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
    refObject = graphene.Field(Reference)
    verseText = graphene.String()
    # footNotes = graphene.List(graphene.String)
    # crossReferences  = graphene.List(graphene.String)

    #pylint: disable=E1136

    def resolve_refObject(parent, _): #pylint: disable=E0213, C0103
        '''resolver'''
        return parent['reference']

    def resolve_refString(parent, _):  #pylint: disable=E0213, C0103
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
    def resolve_refString(parent, _):#pylint: disable=E0213, C0103
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
    def resolve_book(parent, _):#pylint: disable=E0213, C0103
        '''resolver'''
        return parent.book

class DictionaryWord(graphene.ObjectType):
    '''Response object for dictionary word'''
    word = graphene.String()
    details = Metadata()
    active = graphene.Boolean()

class Infographic(graphene.ObjectType):
    '''Response for Infographics'''
    book = graphene.Field(BibleBook)
    title = graphene.String()
    infographicLink = graphene.String()
    active = graphene.Boolean()

class BibleVideo(graphene.ObjectType):
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

class ProjectUser(graphene.ObjectType):
    '''Input object for AgMT user update'''
    project_id = graphene.ID()
    userId = graphene.Int()
    userRole = graphene.String()
    metaData = Metadata()
    active = graphene.Boolean()

class TranslationProject(graphene.ObjectType):
    '''Output object for project creation'''
    projectId = graphene.ID()
    projectName = graphene.String()
    sourceLanguage = graphene.Field(Language)
    targetLanguage = graphene.Field(Language)
    documentFormat = TranslationDocumentType()
    users = graphene.List(ProjectUser)
    metaData = Metadata()
    active = graphene.Boolean()

class TokenOccurence(graphene.ObjectType):
    '''Object for token occurence'''
    sentenceId = graphene.ID()
    offset = graphene.List(graphene.Int)

class Token(graphene.ObjectType):
    '''Response object for token'''
    token = graphene.String()
    occurrences = graphene.List(TokenOccurence)
    translations = Metadata(name="translationSuggestions")
    metaData = Metadata()   

class TokenTranslation(graphene.ObjectType):
    '''For translation/draft of a specific token'''
    token = graphene.String()
    translation = graphene.String()
    occurrence = graphene.Field(TokenOccurence)
    status = graphene.String()

class Sentence(graphene.ObjectType):
    '''Response object for sentences and plain-text draft'''
    sentenceId = graphene.ID()
    sentence = graphene.String()
    draft = graphene.String()
    draftMeta = Metadata()

class Progress(graphene.ObjectType):
    '''Response object for AgMT project progress'''
    confirmed = graphene.Float()
    suggestion = graphene.Float()
    untranslated = graphene.Float()

class Gloss(graphene.ObjectType):
    '''Output object for translation memory or gloss'''
    token = graphene.String()
    translations = Metadata()
    metaData = Metadata()

class Suggestion(graphene.ObjectType):
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
    tokenMetaData = Metadata(description='example={"word-class":["noun", "verb"]}')

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
