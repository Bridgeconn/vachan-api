import graphene

from crud import structurals_crud, contents_crud
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
            skip=skip, limit=limit)

    content_types = graphene.List(types.ContentType, content_type=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_content_types(self, info, content_type=None,
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

    versions = graphene.List(types.Version, version_abbreviation=graphene.String(),
        version_name=graphene.String(), revision=graphene.Int(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_versions(self, info, version_abbreviation=None, version_name=None,
        revision=None, skip=0, limit=100, db_=next(get_db())):
        return structurals_crud.get_versions(db_, version_abbreviation,
        version_name, revision, skip = skip, limit = limit)

    contents = graphene.List(types.Source, content_type=graphene.String(),
        version_abbreviation=graphene.String(), revision=graphene.Int(),
        language_code=graphene.String(), license_code=graphene.String(),
        active=graphene.Boolean(), latest_revision=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_contents(self, info, content_type=None, version_abbreviation=None,
        revision=None, language_code=None, license_code=None, active=True,
        latest_revision=True, skip=0, limit=100, db_=next(get_db())):
        results =  structurals_crud.get_sources(db_, content_type, version_abbreviation, revision,
            language_code, license_code, latest_revision=latest_revision, active=active,
            skip=skip, limit=limit)
        # final_result = [types.Source(res) for res in results]
        return results

    bible_books = graphene.List(types.BibleBook, book_id=graphene.Int(),
        book_code=graphene.String(), book_name=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_books(self, info, book_id=None, book_name=None,
        book_code=None, skip=0, limit=100, db_=next(get_db())):
        return structurals_crud.get_bible_books(db_, book_id=book_id,
            book_code=book_code, book_name=book_name, skip=skip, limit=limit)

    commentaries = graphene.List(types.Commentary,
        source_name=graphene.String(required=True),
        book_code=graphene.String(), chapter=graphene.Int(), verse=graphene.Int(),
        last_verse=graphene.Int(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_commentaries(self, info, source_name, book_code=None, chapter=None,
        verse=None, last_verse=None, active=True, skip=0, limit=100, db_=next(get_db())):
        return contents_crud.get_commentaries(db_, source_name, book_code, chapter, verse,
            last_verse, active=active, skip = skip, limit = limit)

    dictionary_words = graphene.List(types.DictionaryWord,
        source_name=graphene.String(required=True),
        search_word=graphene.String(), exact_match=graphene.Boolean(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_dictonary_words(self, info, source_name, search_word=None, exact_match=False,
        active=True, skip=0, limit=100, db_=next(get_db())):
        return contents_crud.get_dictionary_words(db_, source_name, search_word,
            exact_match=exact_match, active=active, skip=skip, limit=limit)

    infographics = graphene.List(types.Infographic, source_name=graphene.String(required=True),
        book_code=graphene.String(),title=graphene.String(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_infographics(self, info, source_name, book_code=None, title=None, active=True,
        skip=0, limit=100, db_=next(get_db())):
        return contents_crud.get_infographics(db_, source_name, book_code, title,
         active=active, skip = skip, limit = limit)

    bible_videos = graphene.List(types.BibleVideo, source_name=graphene.String(required=True),
        book_code=graphene.String(), title=graphene.String(), theme=graphene.String(),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_videos(self, info, source_name, book_code=None, title=None, theme=None,
        active=True, skip=0, limit=100, db_=next(get_db())):
        return contents_crud.get_bible_videos(db_, source_name, book_code, title, theme, active,
            skip=skip, limit=limit)   

    bible_contents = graphene.List(types.BibleContent, source_name=graphene.String(required=True),
        book_code=graphene.String(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_contents(self, info, source_name, book_code=None, active=True,
        skip=0, limit=100, db_=next(get_db())):
        return contents_crud.get_available_bible_books(db_, source_name, book_code, 
            content_type="all", active=active, skip = skip, limit = limit)

    versification = graphene.Field(types.Versification, source_name=graphene.String(required=True))
    def resolve_versification(self, info, source_name, db_=next(get_db())):
        return contents_crud.get_bible_versification(db_, source_name)

    bible_verse = graphene.List(types.BibleVerse, source_name=graphene.String(required=True),
        book_code=graphene.String(), chapter=graphene.Int(), verse=graphene.Int(),
        last_verse=graphene.Int(), search_phrase=graphene.String(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_verse(self, info, source_name, book_code=None, chapter=None, verse=None,
        last_verse=None, search_phrase=None, active=True, skip=0, limit=100, db_=next(get_db())):
        return contents_crud.get_bible_verses(db_, source_name, book_code, chapter, verse,
            last_verse, search_phrase, active=active, skip = skip, limit = limit)

schema=graphene.Schema(query=Query)
