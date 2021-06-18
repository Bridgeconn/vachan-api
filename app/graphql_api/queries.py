import graphene

from crud import structurals_crud, contents_crud, projects_crud, nlp_crud
from dependencies import get_db, log
from graphql_api import types
import schemas_nlp


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

    agmt_projects = graphene.List(types.TranslationProject, project_name=graphene.String(),
        source_language=graphene.String(), target_language=graphene.String(),
        user_id=graphene.Int(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_agmt_projects(self, info, project_name=None,
        source_language=None, target_language=None, user_id=None, active=True,
        skip=0, limit=100, db_=next(get_db())):
        return projects_crud.get_agmt_projects(db_, project_name, source_language, target_language,
            active, user_id, skip=skip, limit=limit)

    agmt_project_tokens = graphene.List(types.Token, project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String), sentence_id_range=graphene.List(graphene.Int,
        description="Requires exactly two numbers indicating a range"),
        sentence_id_list=graphene.List(graphene.Int), use_translation_memory=graphene.Boolean(),
        include_phrases=graphene.Boolean(), include_stopwords=graphene.Boolean())
    def resolve_agmt_project_tokens(self, info, project_id, books=None, sentence_id_range=None,
        sentence_id_list=None, use_translation_memory=True, include_phrases=True,
        include_stopwords=False, db_=next(get_db())):
        return nlp_crud.get_agmt_tokens(db_, project_id, books, sentence_id_range, sentence_id_list,
            use_translation_memory, include_phrases, include_stopwords)

    agmt_project_token_translation = graphene.Field(types.TokenTranslation,
        project_id=graphene.ID(required=True), sentence_id=graphene.Int(required=True),
        offset=graphene.List(graphene.Int, required=True,
        description="Requires exactly two numbers"))
    def resolve_agmt_project_token_translation(self, info, project_id, sentence_id, offset,
        db_=next(get_db())):
        occurrences = [{"sentenceId":sentence_id, "offset":offset}]
        return projects_crud.obtain_agmt_token_translation(db_, project_id, token=None,
            occurrences=occurrences)[0]
    
    agmt_draft_usfm = graphene.List(graphene.String, project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String), sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_draft_usfm(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None, db_=next(get_db())):
        return projects_crud.obtain_agmt_draft(db_, project_id, books,
            sentence_id_list, sentence_id_range, output_format=schemas_nlp.DraftFormats.USFM)

    agmt_export_alignment = graphene.Field(types.Metadata, project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String), sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_export_alignment(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None, db_=next(get_db())):
        return projects_crud.obtain_agmt_draft(db_, project_id, books,
            sentence_id_list, sentence_id_range, output_format=schemas_nlp.DraftFormats.JSON)

    agmt_project_source = graphene.List(types.Sentence, project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String), sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_project_source(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None, db_=next(get_db())):
        return nlp_crud.obtain_agmt_source(db_, project_id, books, sentence_id_list, sentence_id_range,
            with_draft=True)

    agmt_project_progress = graphene.Field(types.Progress, project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String), sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_project_progress(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None, db_=next(get_db())):
        print("comes in resolver")
        return projects_crud.obtain_agmt_progress(db_, project_id, books,
            sentence_id_list, sentence_id_range)

    gloss = graphene.Field(types.Gloss, source_language=graphene.String(required=True),
        target_language=graphene.String(required=True), token=graphene.String(required=True),
        context=graphene.String(description="sentence or phrase including the token"), 
        token_offset=graphene.List(graphene.Int, description="Requires exactly two numbers"))
    def resolve_gloss(self, info, source_language, target_language, token, context=None,
        token_offset=None, db_=next(get_db())):
        return nlp_crud.glossary(db_, source_language, target_language, token,context,token_offset)

schema=graphene.Schema(query=Query)
