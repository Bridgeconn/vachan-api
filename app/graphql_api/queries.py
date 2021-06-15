import graphene

from crud import structurals_crud
from dependencies import get_db, log
from graphql_api import types


class Query(graphene.ObjectType):
    languages = graphene.List(types.Language, search_word=graphene.String(),
        language_name=graphene.String(), language_code=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_languages(self, info,
        search_word=None, language_code=None, language_name=None, language_id=None,
        skip=0, limit=100, db_=next(get_db())):
        return structurals_crud.get_languages(db_, language_code=language_code,
            language_name=language_name, search_word=search_word,
            skip=skp, limit=limit)

    contents = graphene.List(types.ContentType, content_type=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_contents(self, info, content_type=None,
        skip=0, limit=100, db_=next(get_db())):
        return structurals_crud.get_content_types(db_, content_type, skip, limit)

    licenses = graphene.List(types.License, license_code=graphene.String(),
        license_name=graphene.String(), permission=types.LicensePermission(),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_licenses(self, info, license_code=None, license_name=None,
        permission=None, active=True,
        skip=0, limit=100, db_=next(get_db())):
        return structurals_crud.get_licenses(db_, license_code, license_name, permission,
        active, skip = skip, limit = limit)





schema=graphene.Schema(query=Query)
