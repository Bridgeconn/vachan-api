import graphene
from graphene.types import Scalar

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
