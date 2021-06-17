import graphene
from graphene.types import Scalar

from crud import structurals_crud
from dependencies import get_db, log

class Metadata(Scalar):
    '''metadata representing JSON'''
    @staticmethod
    def serialize(dt):
        return dt

class ContentType(graphene.ObjectType):
    '''output object for content types'''
    contentId = graphene.ID()
    contentType = graphene.String()

class Language(graphene.ObjectType):
    # language_id = graphene.String()
    language = graphene.String()
    code = graphene.String()
    scriptDirection = graphene.String()
    metaData = Metadata()

class LicensePermission(graphene.Enum):
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
    name = graphene.String()
    url = graphene.String()
    book = graphene.Field(BibleBook)
    format = graphene.String()
    active = graphene.Boolean()

class BibleContent(graphene.ObjectType):
    book = graphene.Field(BibleBook)
    USFM = graphene.String()
    JSON = Metadata()
    audio = graphene.Field(AudioBible)
    active = graphene.Boolean()

class Versification(graphene.ObjectType):
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
    refId = graphene.ID()
    refString = graphene.String()
    refObject = graphene.Field(Reference)
    verseText = graphene.String()
    # footNotes = graphene.List(graphene.String)
    # crossReferences  = graphene.List(graphene.String)

    def resolve_refObject(parent, info):
        return parent['reference']

    def resolve_refString(parent, info):
        if 'verseNumberEnd' in parent['reference'] and parent['reference']['verseNumberEnd'] is not None:
            return '%s %s:%s-%s'%(parent['reference']['book'], parent['reference']['chapter'],
                parent['reference']['verseNumber'], parent['reference']['verseNumberEnd'])
        return '%s %s:%s'%(parent['reference']['book'], parent['reference']['chapter'],
            parent['reference']['verseNumber'])

class Commentary(graphene.ObjectType):
    refString =  graphene.String()
    book = graphene.Field(BibleBook)
    chapter = graphene.Int()
    verseStart = graphene.Int()
    verseEnd = graphene.Int()
    commentary = graphene.String()
    active = graphene.Boolean()

    def resolve_refString(parent, info):
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
    def resolve_book(parent, info):
        return parent.book

class DictionaryWord(graphene.ObjectType):
    word = graphene.String()
    details = Metadata()
    active = graphene.Boolean()

class Infographic(graphene.ObjectType):
    book = graphene.Field(BibleBook)
    title = graphene.String()
    infographicLink = graphene.String()
    active = graphene.Boolean()

class BibleVideo(graphene.ObjectType):
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
    translations = Metadata()
    metaData = Metadata()

class TokenTranslation(graphene.ObjectType):
    '''For translation/draft of a specific token'''
    token = graphene.String()
    translation = graphene.String()
    occurrence = graphene.Field(TokenOccurence)
    status = graphene.String()
    