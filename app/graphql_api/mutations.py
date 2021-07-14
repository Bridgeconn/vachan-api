'''GraphQL queries and mutations'''
from enum import Enum
from typing import Optional
import graphene

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

class CreateContentTypes(graphene.Mutation):
    """Mutation for Content types Creation"""
    class Arguments:
        "mutation arguments"
        content_type = InputContentType(required=True)

    data = graphene.Field(types.ContentType)
    message = graphene.String()

#pylint: disable=R0201,no-self-use
    def mutate(self,info,content_type):
        """resolver"""
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (content_type,schemas.ContentTypeCreate)
        result = structurals_crud.create_content_type(db_,content=schema_model)
        contentType = types.ContentType(
            contentId = result.contentId,
            contentType = result.contentType
        )
        return CreateContentTypes(message = "Content type created successfully"\
            ,data = contentType )

########## Add License ########
enum_val = types.LicensePermission

class InputAddLicense(graphene.InputObjectType):
    """Add license Input"""
    name = graphene.String(required=True)
    code = graphene.String(required=True,description=\
        "pattern: ^[a-zA-Z0-9\.\_\-]+$")
    license = graphene.String(required=True)
    permissions = graphene.List(enum_val, default_value =\
        ["Private_use"],description="Expecting a list\
        [ Commercial_use, Modification, Distribution, Patent_use, Private_use ]")
        
#pylint: disable=R0901,too-few-public-methods
class AddLicense(graphene.Mutation):
    """Mutation class for Add Licenses"""
    class Arguments:
        """Arguments declaration for the mutation"""
        license_args = InputAddLicense(required=True)

    message = graphene.String()
    data = graphene.Field(types.License)

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,license_args):
        '''resolve'''
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (license_args,schemas.LicenseCreate)
        result =structurals_crud.create_license(db_,schema_model,user_id=None)
        license = types.License(
            name = result.name,
            code = result.code,
            license = result.license,
            permissions = result.permissions,
            active = result.active
        )
        message = "License uploaded successfully"
        return AddLicense(message=message,data=license)    

########## Edit License ########
enum_val = types.LicensePermission

class InputEditLicense(graphene.InputObjectType):
    """Edit license Input"""
    name = graphene.String()
    code = graphene.String(required=True,description=\
        "pattern: ^[a-zA-Z0-9\.\_\-]+$")
    license = graphene.String()
    permissions = graphene.List(enum_val, default_value =\
        ["Private_use"],description="Expecting a list\
        [ Commercial_use, Modification, Distribution, Patent_use, Private_use ]")
    active = graphene.Boolean()
        
#pylint: disable=R0901,too-few-public-methods
class EditLicense(graphene.Mutation):
    """Mutation class for Edit Licenses"""
    class Arguments:
        """Arguments declaration for the mutation"""
        license_args = InputEditLicense()

    message = graphene.String()
    data = graphene.Field(types.License)

#pylint: disable=R0201,no-self-use
#pylint: disable=W0613
    def mutate(self,info,license_args):
        '''resolve'''
        db_ = info.context["request"].db_session
        schema_model = utils.convert_graphene_obj_to_pydantic\
            (license_args,schemas.LicenseEdit)
        result =structurals_crud.update_license(db_,schema_model,user_id=None)
        license = types.License(
            name = result.name,
            code = result.code,
            license = result.license,
            permissions = result.permissions,
            active = result.active
        )
        message = "License edited successfully"
        return AddLicense(message=message,data=license)           

########## ALL MUTATIONS FOR API ########
class VachanMutations(graphene.ObjectType):
    '''All defined mutations'''
    add_language = AddLanguage.Field()
    update_language = UpdateLanguage.Field()
    add_content_type = CreateContentTypes.Field()
    add_license = AddLicense.Field()
    edit_license = EditLicense.Field()
