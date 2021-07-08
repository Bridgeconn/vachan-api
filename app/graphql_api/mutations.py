'''GraphQL queries and mutations'''


import graphene

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
#pylint: disable=E0611

from crud import structurals_crud
from dependencies import get_db
from graphql_api import types, utils
import schemas


############ ADD NEW Language #################
class InputAddLang(graphene.InputObjectType):
    """ADD Language Input"""
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString()

#pylint: disable=R0901,too-few-public-methods
class AddLanguage(graphene.Mutation):
    """Mutation class for Add Language"""
    class Arguments:
        """Arguments declaration for the mutation"""
        language_addargs = InputAddLang(required=True)

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    language = graphene.Field(types.Language)
    def mutate(self,info,language_addargs):
        '''resolve'''
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (language_addargs,schemas.LanguageCreate)
        result =structurals_crud.create_language(db_=next(get_db()),lang=schema_model)
        language = types.Language(
            language = result.language,
            code = result.code,
            scriptDirection = result.scriptDirection,
            metaData = result.metaData
        )
        return AddLanguage(language = language)


####### Update Language ##############
class InputUpdateLang(graphene.InputObjectType):
    """ update Language Input """
    languageId = graphene.Int()
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString()

class UpdateLanguage(graphene.Mutation):
    """ Mutation for update language"""
    class Arguments:
        """ Argumnets declare for mutations"""
        language_updateargs = InputUpdateLang(required=True)

    language = graphene.Field(types.Language)

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,language_updateargs):
        """resolver"""
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (language_updateargs,schemas.LanguageEdit)
        result = structurals_crud.update_language(db_=next(get_db()),lang=schema_model)
        language = types.Language(
            language = result.language,
            code = result.code,
            scriptDirection = result.scriptDirection,
            metaData = result.metaData
        )
        return UpdateLanguage(language=language)


########## ALL MUTATIONS FOR API ########
class VachanMutations(graphene.ObjectType):
    '''All defined mutations'''
    add_language = AddLanguage.Field()
    update_language = UpdateLanguage.Field()
