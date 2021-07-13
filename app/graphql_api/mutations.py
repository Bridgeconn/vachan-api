'''GraphQL queries and mutations'''
from logging import error
import graphene
from pydantic import errors

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
from crud import structurals_crud
#pylint: disable=E0611
from graphql_api import types, utils
import schemas

############ ADD NEW Language #################
class InputAddLang(graphene.InputObjectType):
    """ADD Language Input"""
    language = graphene.String(required=True)
    code = graphene.String(required=True,\
    description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString(description="Expecting a dictionary Type")

#pylint: disable=R0901,too-few-public-methods
class AddLanguage(graphene.Mutation):
    """Mutation class for Add Language"""
    class Arguments:
        """Arguments declaration for the mutation"""
        language_addargs = InputAddLang(required=True)

    data = graphene.Field(types.Language)
    message = graphene.String()

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,language_addargs):
        '''resolve'''
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (language_addargs,schemas.LanguageCreate)
        result =structurals_crud.create_language(db_,lang=schema_model)
        language = types.Language(
                languageId = result.languageId,
                language = result.language,
                code = result.code,
                scriptDirection = result.scriptDirection,
                metaData = result.metaData
        )
        message = "Language created successfully"
        return UpdateLanguage(message=message,data=language)


####### Update Language ##############
class InputUpdateLang(graphene.InputObjectType):
    """ update Language Input """
    languageId = graphene.Int(required=True)
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString(description="Expecting a dictionary Type")

class UpdateLanguage(graphene.Mutation):
    """ Mutation for update language"""
    class Arguments:
        """ Argumnets declare for mutations"""
        language_updateargs = InputUpdateLang(required=True)

    data = graphene.Field(types.Language)
    message = graphene.String()

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,language_updateargs):
        """resolver"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (language_updateargs,schemas.LanguageEdit)
        result = structurals_crud.update_language(db_,lang=schema_model)
        language = types.Language(
                languageId = result.languageId,
                language = result.language,
                code = result.code,
                scriptDirection = result.scriptDirection,
                metaData = result.metaData
        )
        message = "Language edited successfully"
        return UpdateLanguage(message=message,data=language)

########## Add Contents Type ########
class InputContentType(graphene.InputObjectType):
    """ update Language Input """
    contentType = graphene.String(required=True,\
        description="Input object to ceate a new content type : pattern: ^[a-z]+$ :\
        example: commentary")

class createContentTypes(graphene.Mutation):
    """Mutation for Content types Creation"""
    class Arguments:
        contentType = InputContentType(required=True)
        
    data = graphene.Field(types.ContentType)
    message = graphene.String()

    def mutate(self,info,contentType):
        """resolver"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (contentType,schemas.ContentTypeCreate)
        result = structurals_crud.create_content_type(db_,content=schema_model)
        contentType = types.ContentType(
            contentId = result.contentId,
            contentType = result.contentType
        )
        return createContentTypes(message = "Content type created successfully" ,data = contentType )
        

########## ALL MUTATIONS FOR API ########
class VachanMutations(graphene.ObjectType):
    '''All defined mutations'''
    add_language = AddLanguage.Field()
    update_language = UpdateLanguage.Field()
    add_content_type = createContentTypes.Field()
