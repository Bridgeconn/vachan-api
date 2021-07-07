'''GraphQL queries and mutations'''


import graphene
import json
from graphql import language
from sqlalchemy.sql import schema

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it

from crud import structurals_crud, contents_crud, projects_crud, nlp_crud
from dependencies import get_db
from graphql_api import types, utils
from graphql_api.types import Metadata
import schemas


############ ADD NEW Language #################
""" ADD Language Input """
class InputAddLang(graphene.InputObjectType):
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString()


class AddLanguage(graphene.Mutation):
    class Arguments:
        language_Addargs = InputAddLang(required=True)

    language = graphene.Field(types.Language)
    '''resolve'''
    def mutate(root,info,language_Addargs):
        schema_model = utils.convert_graphene_obj_to_pydantic(language_Addargs,schemas.LanguageCreate)
        result =structurals_crud.create_language(db_=next(get_db()),lang=schema_model)
        language = types.Language(
            language = result.language,
            code = result.code,
            scriptDirection = result.scriptDirection,
            metaData = result.metaData
        )
        return AddLanguage(language = language)


####### Update Language ##############
""" update Language Input """
class InputUpdateLang(graphene.InputObjectType):
    languageId = graphene.Int()
    language = graphene.String()
    code = graphene.String(description="language code as per bcp47(usually 2 letter code)")
    scriptDirection = graphene.String()
    metaData = graphene.JSONString()

class UpdateLanguage(graphene.Mutation):
    class Arguments:
        language_updateargs = InputUpdateLang(required=True)

    language = graphene.Field(types.Language)

    def mutate(root,info,language_updateargs):
        schema_model = utils.convert_graphene_obj_to_pydantic(language_updateargs,schemas.LanguageEdit)
        result = structurals_crud.update_language(db_=next(get_db()),lang=schema_model)  
        print("==============================================")
        print(result)
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

