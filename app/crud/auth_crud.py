''' Place to define all Database CRUD operations for Roles'''
import json
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.sql import text
import db_models
from custom_exceptions import NotAvailableException
from crud import utils
from auth.auth_globals import generate_roles, APPS

def create_role(db_: Session, role_details, user_id=None):
    '''Adds a row to roles table'''
    if role_details.roleOfApp.lower() not in [app.lower() for app in APPS]:
        raise NotAvailableException(f"{role_details.roleOfApp} is not registered")

    db_content = db_models.Roles(roleName = role_details.roleName.lower(),
        roleOfApp = role_details.roleOfApp,
        roleDescription = role_details.roleDescription,
        createdUser= user_id,
        updatedUser=user_id,active=True)
    db_.add(db_content)
    # db_.commit()
    # db_.refresh(db_content)
    generate_roles()
    return db_content

# def get_role(db_: Session, role_name = None, role_of_app = None, role_description=None,
#     role_id = None, **kwargs):
#     '''Fetches rows of role, with pagination and various filters'''
#     skip = kwargs.get("skip",0)
#     limit = kwargs.get("limit",100)
#     query = db_.query(db_models.Roles)
#     if role_name:
#         query = query.filter(func.lower(db_models.Roles.roleName) == role_name.lower())
#     if role_of_app:
#         query = query.filter(func.lower(db_models.Roles.roleOfApp) == role_of_app.lower())
#     if role_description:
#         query = query.filter(func.lower(db_models.Roles.roleDescription) == role_description.lower())
#     if role_id is not None:
#         query = query.filter(db_models.Roles.roleId == role_id)
#     return query.offset(skip).limit(limit).all()


# def get_role(db_:Session, role_name =None,role_of_app =None,search_word =None, **kwargs):
#     '''Fetches rows of role_of_app from the table specified by roles'''
#     details = kwargs.get("details",None)
#     exact_match = kwargs.get("exact_match",False)
#     word_list_only = kwargs.get("word_list_only",False)
#     active = kwargs.get("active",True)
#     skip = kwargs.get("skip",0)
#     limit = kwargs.get("limit",100)
#     if role_name not in db_models.dynamicTables:
#         raise NotAvailableException(f'{role_name} not found in database.')
#     # if not source_name.endswith(db_models.ContentTypeName.DICTIONARY.value):
#     #     raise TypeException('The operation is supported only on dictionaries')
#     model_cls = db_models.dynamicTables[role_name]
#     if role_of_app:
#         query = query.filter(func.lower(db_models.Roles.roleOfApp) == role_of_app.lower())
#     if word_list_only:
#         query = db_.query(model_cls.word)
#     else:
#         query = db_.query(model_cls)
#     if search_word and exact_match:
#         query = query.filter(model_cls.word == utils.normalize_unicode(search_word))
#     elif search_word:
#         search_pattern = " & ".join(re.findall(r'\w+', search_word))
#         search_pattern += ":*"
#         query = query.filter(text("to_tsvector('simple', word || ' ' ||"+\
#             "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"+\
#             " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
#     if details:
#         det = json.loads(details)
#         for key in det:
#             query = query.filter(model_cls.details.op('->>')(key) == det[key])
#     query = query.filter(model_cls.active == active)
#     res = query.offset(skip).limit(limit).all()
#     roles_db_content = db_.query(db_models.Roles).filter(
#         db_models.Rols.roleName == role_name).first()
    # response = {
#         'db_content':res,
#         'roles_content':roles_db_content }
#     return response

# elif search_word:
#         search_pattern = " & ".join(re.findall(r'\w+', search_word))
#         search_pattern += ":*"
#         query = query.filter(text("to_tsvector('simple', word || ' ' ||"+\
#             "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"+\
#             " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))


 



# def get_languages(db_: Session,language_name = None, search_word=None,
#     language_id = None, **kwargs):
#     '''Fetches rows of language, with pagination and various filters'''
#     skip = kwargs.get("skip",0)
#     limit = kwargs.get("limit",100)
#     query = db_.query(db_models.Language)
#     if language_code:
#         query = query.filter(func.lower(db_models.Language.code) == language_code.lower())
#     if language_name:
#         query = query.filter(func.lower(db_models.Language.language) == language_name.lower())
#     if search_word:
#         search_pattern = " & ".join(re.findall(r'\w+', search_word))
#         search_pattern += ":*"
#         query = query.filter(text("to_tsvector('simple', language_code || ' ' ||"+\
#             " language_name || ' ' || "+\
#             "jsonb_to_tsvector('simple', metadata, '[\"string\", \"numeric\"]') || ' ')"+\
#             " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
#     if language_id is not None:
#         query = query.filter(db_models.Language.languageId == language_id)
#     return query.offset(skip).limit(limit).all()

# def get_role(db_: Session, role_name = None, role_of_app = None, search_word=None,
#     role_id = None, **kwargs):

def get_role(db_: Session,search_word=None,role_name =None,role_of_app =None,
    **kwargs):
    '''Fetches rows of role, with pagination and various filters'''
    exact_match = kwargs.get("exact_match",False)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.Roles)
    if role_name:
        query = query.filter(func.lower(db_models.Roles.roleName) == role_name.lower())
    if role_of_app:
        query = query.filter(func.lower(db_models.Roles.roleOfApp) == role_of_app.lower())
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', word || ' ' ||"+\
            "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    # if role_id is not None:
    #     query = query.filter(db_models.Roles.roleId == role_id)
    return query.offset(skip).limit(limit).all()
