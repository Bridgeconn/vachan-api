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
    contentType = ContentType()
    language = Language()
    version = Version()
    year = graphene.Int()
    license = License()
    metaData = Metadata()
    active = graphene.Boolean()

    def resolve_version(parent, info, db_=next(get_db())):
        return structurals_crud.get_versions(db_, parent.version_id, limit = 1)[0]

