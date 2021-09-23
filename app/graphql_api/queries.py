'''GraphQL queries and mutations'''

import graphene
from crud import structurals_crud, contents_crud, projects_crud, nlp_crud
from graphql_api import types, utils
import schemas_nlp

#pylint: disable=R0201
#pylint: disable=too-many-arguments,too-many-public-methods
class Query(graphene.ObjectType):
    '''All defined queries'''
    languages = graphene.List(types.Language,
        description="Query languages in vachan-db",
        search_word=graphene.String(),
        language_name=graphene.String(), language_code=graphene.String(
            description="language code as per bcp47(usually 2 letter code)"),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_languages(self, info,
        search_word=None, language_code=None, language_name=None,
        skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return structurals_crud.get_languages(db_, language_code=language_code,
            language_name=language_name, search_word=search_word,
            skip=skip, limit=limit)

    content_types = graphene.List(types.ContentType,
        description="Query supported content types in vachan-db",
        content_type=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_content_types(self, info, content_type=None,
        skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return structurals_crud.get_content_types(db_, content_type, skip, limit)

    licenses = graphene.List(types.License,
        description="Query uploaded licenses in vachan-db", license_code=graphene.String(),
        license_name=graphene.String(), permission=types.LicensePermission(),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_licenses(self, info, license_code=None, license_name=None,
        permission=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return structurals_crud.get_licenses(db_, license_code, license_name, permission,
        active, skip = skip, limit = limit)

    versions = graphene.List(types.Version,
        description="Query defined versions in vachan-db", version_abbreviation=graphene.String(),
        version_name=graphene.String(), revision=graphene.Int(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_versions(self, info, version_abbreviation=None, version_name=None,
        revision=None, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return structurals_crud.get_versions(db_, version_abbreviation,
        version_name, revision, skip = skip, limit = limit)

    contents = graphene.List(types.Source,
        description="Query added contents in vachan-db", content_type=graphene.String(),
        version_abbreviation=graphene.String(), revision=graphene.Int(),
        language_code=graphene.String(
            description="language code as per bcp47(usually 2 letter code)"),
        license_code=graphene.String(),
        active=graphene.Boolean(), latest_revision=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_contents(self, info, content_type=None, version_abbreviation=None,
        revision=None, language_code=None, license_code=None, active=True,
        latest_revision=True, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        results =  structurals_crud.get_sources(db_, content_type, version_abbreviation,
        revision=revision,language_code=language_code, license_code=license_code,
        latest_revision=latest_revision,active=active, skip=skip, limit=limit)
        return results

    bible_books = graphene.List(types.BibleBook,
        description="Query bible book names and codes used in vachan-db", book_id=graphene.Int(),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        book_name=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_books(self, info, book_id=None, book_name=None,
        book_code=None, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return structurals_crud.get_bible_books(db_, book_id=book_id,
            book_code=book_code, book_name=book_name, skip=skip, limit=limit)

    commentaries = graphene.List(types.Commentary,
        description="Query commentaries added in vachan-db",
        source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        chapter=graphene.Int(), verse=graphene.Int(),
        last_verse=graphene.Int(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_commentaries(self, info, source_name, book_code=None, chapter=None,
        verse=None, last_verse=None, active=True, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_commentaries(db_, source_name, book_code, chapter, verse,
            last_verse, active=active, skip = skip, limit = limit)

    dictionary_words = graphene.List(types.DictionaryWord,
        description="Query lexicons/dictionaries added in vachan-db",
        source_name=graphene.String(required=True),
        search_word=graphene.String(), exact_match=graphene.Boolean(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_dictionary_words(self, info, source_name, search_word=None, exact_match=False,
        active=True, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_dictionary_words(db_, source_name, search_word,
            exact_match=exact_match, active=active, skip=skip, limit=limit)

    infographics = graphene.List(types.Infographic,
        description="Query infographics in vachan-db", source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        title=graphene.String(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_infographics(self, info, source_name, book_code=None, title=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_infographics(db_, source_name, book_code, title,
         active=active, skip = skip, limit = limit)

    bible_videos = graphene.List(types.BibleVideo,
        description="Query Bible Videos listed in vachan-db",
        source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        title=graphene.String(), theme=graphene.String(),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_videos(self, info, source_name, book_code=None, title=None, theme=None,
        active=True, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_bible_videos(db_, source_name, book_code, title, theme,
        active=active, skip=skip, limit=limit)

    bible_contents = graphene.List(types.BibleContent,
        description="Query bible usfms, jsons and audios in vachan-db",
        source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_contents(self, info, source_name, book_code=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_available_bible_books(db_, source_name, book_code,
            content_type="all", active=active, skip = skip, limit = limit)

    versification = graphene.Field(types.Versification,
        description="Query versification structure of a bible in vachan-db",
        source_name=graphene.String(required=True))
    def resolve_versification(self, info, source_name):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_bible_versification(db_, source_name)

    bible_verse = graphene.List(types.BibleVerse,
        description="Query verses of a bible in vachan-db",
        source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        chapter=graphene.Int(), verse=graphene.Int(),
        last_verse=graphene.Int(), search_phrase=graphene.String(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_verse(self, info, source_name, book_code=None, chapter=None, verse=None,
        last_verse=None, search_phrase=None, active=True, skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return contents_crud.get_bible_verses(db_, source_name, book_code, chapter, verse,
            last_verse = last_verse, search_phrase = search_phrase,
            active=active, skip = skip, limit = limit)

    agmt_projects = graphene.List(types.TranslationProject,
        description="Query AutographaMT projects on vachan-db", project_name=graphene.String(),
        source_language=graphene.String(
            description="language code as per bcp47(usually 2 letters)"),
        target_language=graphene.String(
            description="language code as per bcp47(usually 2 letters)"),
        user_id=graphene.Int(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_agmt_projects(self, info, project_name=None,
        source_language=None, target_language=None, user_id=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        db_ = info.context["request"].db_session
        return projects_crud.get_agmt_projects(db_, project_name, source_language, target_language,
            active=active, user_id=user_id, skip=skip, limit=limit)

    agmt_project_tokens = graphene.List(types.Token,
        description="Tokenize specified portions of source in an AgMT project",
        project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String, description="3 letter codes like, gen, mat etc"),
        sentence_id_range=graphene.List(graphene.Int,
        description="Requires exactly two numbers indicating a range"),
        sentence_id_list=graphene.List(graphene.Int), use_translation_memory=graphene.Boolean(),
        include_phrases=graphene.Boolean(), include_stopwords=graphene.Boolean())
    def resolve_agmt_project_tokens(self, info, project_id, books=None, sentence_id_range=None,
        sentence_id_list=None, use_translation_memory=True, include_phrases=True,
        include_stopwords=False):
        '''resolver'''
        db_ = info.context["request"].db_session
        return nlp_crud.get_agmt_tokens(db_, project_id, books, sentence_id_range, sentence_id_list,
            use_translation_memory=use_translation_memory,
            include_phrases=include_phrases, include_stopwords=include_stopwords)

    agmt_project_token_translation = graphene.Field(types.TokenTranslation,
        description="Query the translation done for a token in an AgMT project",
        project_id=graphene.ID(required=True), sentence_id=graphene.Int(required=True),
        offset=graphene.List(graphene.Int, required=True,
        description="Requires exactly two numbers"))
    def resolve_agmt_project_token_translation(self, info, project_id, sentence_id, offset):
        '''resolver'''
        db_ = info.context["request"].db_session
        occurrences = [{"sentenceId":sentence_id, "offset":offset}]
        return projects_crud.obtain_agmt_token_translation(db_, project_id, token=None,
            occurrences=occurrences)[0]

    #Agmt get token Sentance
    agmt_project_token_sentences = graphene.List(types.Sentence,
        description="Query the translation done for sentance in an AgMT project",
        project_id=graphene.ID(required=True),token=graphene.String(required=True),
        occurrences = graphene.List(types.TokenOccurenceInput,required=True))
    def resolve_agmt_project_token_sentences(self, info, project_id, token, occurrences):
        '''resolver'''
        db_ = info.context["request"].db_session
        return projects_crud.get_agmt_source_per_token(db_,project_id,token,occurrences)

    #suggest Translation
    suggest_translation = graphene.List(types.Sentence,
        description="tokenize sentences and prepare draft with autogenerated suggestions",
        source_language=graphene.String(required=True,
        description="language code as per bcp47(usually 2 letter code)"),
        target_language=graphene.String(required=True,
            description="language code as per bcp47(usually 2 letters)"),
        sentence_list=graphene.List(types.SentenceInput, required=True),
        punctuations=graphene.List(graphene.String),
        stopwords=graphene.Argument(types.Stopwords))
    def resolve_suggest_translation(self, info, source_language, sentence_list, target_language,
            punctuations=None, stopwords=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        result =  nlp_crud.auto_translate(db_=db_,sentence_list=sentence_list,source_lang=\
            source_language,target_lang=target_language,punctuations=punctuations,\
                stop_words=stopwords)
        content_list = []
        for item in result:
            content = {
            "sentenceId":item.sentenceId,
            "sentence":item.sentence,
            "draft":item.draft,
            "draftMeta":item.draftMeta
            }
            content_list.append(content)
        return content_list

    agmt_draft_usfm = graphene.List(graphene.String,
        description='Obtain the current draft as USFM from an AgMT project',
        project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String, description="3 letter codes like, gen, mat etc"),
        sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_draft_usfm(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        return projects_crud.obtain_agmt_draft(db_, project_id, books,
            sentence_id_list, sentence_id_range, output_format=schemas_nlp.DraftFormats.USFM)

    agmt_export_alignment = graphene.Field(types.Metadata,
        description='Obtain the current translations in alignment json format from an AgMT project',
        project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String, description="3 letter code like, gen, mat etc"),
        sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_export_alignment(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        return projects_crud.obtain_agmt_draft(db_, project_id, books,
            sentence_id_list, sentence_id_range, output_format=schemas_nlp.DraftFormats.JSON)

    agmt_project_source = graphene.List(types.Sentence,
        description='Query the source from an AgMT project',
        project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String, description="3 letter code like, gen, mat etc"),
        sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_project_source(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        return nlp_crud.obtain_agmt_source(db_, project_id, books, sentence_id_list,
            sentence_id_range, with_draft=True)

    agmt_project_progress = graphene.Field(types.Progress,
        description='Find the translation progress of an AgMT project',
        project_id=graphene.ID(required=True),
        books=graphene.List(graphene.String, description="3 letter code like, gen, mat etc"),
        sentence_id_list=graphene.List(graphene.Int),
        sentence_id_range=graphene.List(graphene.Int,
            description='Requires exactly two numbers indicating a range'))
    def resolve_agmt_project_progress(self, info, project_id, books=None, sentence_id_list=None,
        sentence_id_range=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        return projects_crud.obtain_agmt_progress(db_, project_id, books,
            sentence_id_list, sentence_id_range)

    gloss = graphene.Field(types.Gloss,
        description='Obtain known translations and other details from translation memory',
        source_language=graphene.String(required=True,
        description="language code as per bcp47(usually 2 letter code)"),
        target_language=graphene.String(required=True,
            description="language code as per bcp47(usually 2 letter code)"),
        token=graphene.String(required=True),
        context=graphene.String(description="sentence or phrase including the token"),
        token_offset=graphene.List(graphene.Int, description="Requires exactly two numbers"))
    def resolve_gloss(self, info, source_language, target_language, token, context=None,
        token_offset=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        return nlp_crud.glossary(db_, source_language, target_language, token,
        context=context,token_offset=token_offset)

    tokenize = graphene.List(types.Token,
        description='Tokenize a set of sentences',
        source_language=graphene.String(required=True,
        description="language code as per bcp47(usually 2 letter code)"),
        target_language=graphene.String(
            description="language code as per bcp47(usually 2 letters)"),
        sentence_list=graphene.List(types.SentenceInput, required=True),
        use_translation_memory=graphene.Boolean(), include_phrases=graphene.Boolean(),
        include_stopwords=graphene.Boolean(), punctuations=graphene.List(graphene.String),
        stopwords=graphene.Argument(types.Stopwords))
    def resolve_tokenize(self, info, source_language, sentence_list, target_language=None,
            use_translation_memory=True, include_phrases=True,
            include_stopwords=False, punctuations=None, stopwords=None):
        '''resolver'''
        db_ = info.context["request"].db_session
        return nlp_crud.get_generic_tokens(db_, source_language, sentence_list, target_language,
            punctuations= punctuations, stopwords=stopwords, include_phrases = include_phrases,
            use_translation_memory=use_translation_memory, include_stopwords=include_stopwords)

    translate_token = graphene.List(types.Sentence,
        description='replace provided tokens with translation in the input sentences',
        source_language=graphene.String(required=True,
            description="language code as per bcp47(usually 2 letter code)"),
        target_language=graphene.String(required=True,
            description="language code as per bcp47(usually 2 letter code)"),
        sentence_list=graphene.List(types.SentenceInput, required=True),
        token_translations=graphene.List(types.TokenUpdate, required=True),
        use_data_for_learning=graphene.Boolean())
    def resolve_translate_token(self, info, source_language, target_language, sentence_list,
        token_translations, use_data_for_learning=True):
        '''resolver'''
        db_ = info.context["request"].db_session
        new_sent_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        new_token_list =[ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.TokenUpdate)
                for item in token_translations]
        return nlp_crud.replace_bulk_tokens(db_, new_sent_list, new_token_list, source_language,
            target_language, use_data_for_learning=use_data_for_learning)


    convert_to_usfm = graphene.List(graphene.String,
        description="Converts drafts to usfm",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_usfm(self, _, sentence_list):
        '''resolver'''
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        return nlp_crud.obtain_draft(new_list,
            doc_type=schemas_nlp.TranslationDocumentType.USFM)

    convert_to_alignment = graphene.Field(types.Metadata,
        description="Converts sentences and drafts to alignment-json",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_alignment(self, _, sentence_list):
        '''resolver'''
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        return nlp_crud.obtain_draft(new_list,
            doc_type=schemas_nlp.TranslationDocumentType.JSON)

    convert_to_csv = graphene.String(
        description="Converts sentences and drafts to CSV format",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_csv(self, _, sentence_list):
        '''resolver'''
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        return nlp_crud.obtain_draft(new_list,
            doc_type=schemas_nlp.TranslationDocumentType.CSV)

    convert_to_text = graphene.String(
        description="Converts drafts to alignment-json",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_text(self, _, sentence_list):
        '''resolver'''
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        return nlp_crud.obtain_draft(new_list,
            doc_type=schemas_nlp.TranslationDocumentType.TEXT)
