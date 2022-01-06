'''GraphQL queries and mutations'''

import graphene
from graphql_api import types, utils
from schema import schemas_nlp
from routers import content_apis, auth_api, translation_apis
from auth.authentication import get_user_or_none_graphql
from dependencies import log

#Pylint error :- Query class have all resolver functions
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
        log.info('In GraphQL Get Language')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        # configuring the request params
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/languages"
        return content_apis.get_language(request=req, language_code=language_code,
        language_name=language_name, search_word=search_word, skip=skip,
        limit=limit, user_details=user_details, db_=db_)
        # return structurals_crud.get_languages(db_, language_code=language_code,
        #     language_name=language_name, search_word=search_word,
        #     skip=skip, limit=limit)

    content_types = graphene.List(types.ContentType,
        description="Query supported content types in vachan-db",
        content_type=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_content_types(self, info, content_type=None,
        skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Content Types')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/contents"
        return content_apis.get_contents(request=req,content_type=content_type,skip=skip,
            limit=limit,user_details=user_details,db_=db_)
        # return structurals_crud.get_content_types(db_, content_type, skip, limit)

    licenses = graphene.List(types.License,
        description="Query uploaded licenses in vachan-db", license_code=graphene.String(),
        license_name=graphene.String(), permission=types.LicensePermission(),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_licenses(self, info, license_code=None, license_name=None,
        permission=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Content Licesnes')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/licenses"
        return content_apis.get_license(request=req, license_code=license_code,
        license_name=license_name,permission=permission, active=active, skip=skip,
        limit=limit, user_details=user_details, db_=db_)
        # return structurals_crud.get_licenses(db_, license_code, license_name, permission,
        # active, skip = skip, limit = limit)

    versions = graphene.List(types.Version,
        description="Query defined versions in vachan-db", version_abbreviation=graphene.String(),
        version_name=graphene.String(), revision=graphene.Int(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_versions(self, info, version_abbreviation=None, version_name=None,
        revision=None, skip=0, limit=100, metadata=None):
        '''resolver'''
        log.info('In GraphQL Get Content versions')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/versions"
        return content_apis.get_version(request=req, version_abbreviation=version_abbreviation,
        version_name=version_name, revision=revision, skip=skip, limit=limit,
        user_details=user_details, db_=db_,metadata=metadata)
        # return structurals_crud.get_versions(db_, version_abbreviation,
        # version_name, revision, skip = skip, limit = limit)

    contents = graphene.List(types.Source,
        description="Query added contents in vachan-db", content_type=graphene.String(),
        version_abbreviation=graphene.String(), revision=graphene.Int(),
        language_code=graphene.String(
            description="language code as per bcp47(usually 2 letter code)"),
        license_code=graphene.String(),
        access_tag = graphene.List(types.SourcePermissions),
        active=graphene.Boolean(), latest_revision=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_contents(self, info, content_type=None, version_abbreviation=None,#pylint: disable=too-many-locals
        revision=None, language_code=None, license_code=None, active=True,
        latest_revision=True, skip=0, limit=100,metadata=None,
        access_tag= None):
        '''resolver'''
        log.info('In GraphQL Get Contents(Sources)')
        if access_tag:
            # permission_list = [perm for perm in types.SourcePermissions.__enum__]
            permission_list = list(types.SourcePermissions.__enum__)#pylint: disable=no-member
            access_tag = [perm_tag for perm_tag in permission_list for tag in
                access_tag if tag == perm_tag.value]
        # print("------------------------------>>>",access_tag)
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/sources"
        results = content_apis.get_source(request=req, content_type=content_type,
        version_abbreviation=version_abbreviation, revision=revision, language_code=language_code
        ,license_code=license_code, metadata=metadata, access_tag=access_tag, active=active,
        latest_revision=latest_revision, skip=skip, limit=limit, user_details=user_details,
        db_=db_)
        return results

    bible_books = graphene.List(types.BibleBook,
        description="Query bible book names and codes used in vachan-db", book_id=graphene.Int(),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        book_name=graphene.String(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_books(self, info, book_id=None, book_name=None,
        book_code=None, skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Bible Books')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/lookup/bible/books"
        results = content_apis.get_bible_book(request=req,book_id=book_id,
            book_code=book_code,book_name=book_name,user_details=user_details,
            skip=skip, limit=limit, db_=db_)
        return results

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
        log.info('In GraphQL Get Commentaries')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/commentaries/{source_name}"
        req.path_params["source_name"] = source_name
        results = content_apis.get_commentary(request=req, source_name=source_name,
        book_code=book_code, chapter=chapter, verse=verse, last_verse=last_verse,
        active=active,skip=skip,limit=limit,user_details=user_details,
        db_=db_)
        return results

    dictionary_words = graphene.List(types.DictionaryWord,
        description="Query lexicons/dictionaries added in vachan-db",
        source_name=graphene.String(required=True),
        search_word=graphene.String(), exact_match=graphene.Boolean(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_dictionary_words(self, info, source_name, search_word=None, exact_match=False,
        active=True, skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Dictionaries')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/dictionaries/{source_name}"
        req.path_params["source_name"] = source_name
        results = content_apis.get_dictionary_word(request= req,
            source_name= source_name, search_word= search_word,
            exact_match= exact_match, active= active, skip= skip,
            limit= limit, user_details = user_details, db_= db_,
            details=None)
        return results

    infographics = graphene.List(types.Infographic,
        description="Query infographics in vachan-db", source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        title=graphene.String(), active=graphene.Boolean(),
        skip=graphene.Int(), limit=graphene.Int())
    def resolve_infographics(self, info, source_name, book_code=None, title=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Infographics')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/infographics/{source_name}"
        req.path_params["source_name"] = source_name
        results = content_apis.get_infographic(request=req,
            source_name=source_name, book_code= book_code,
            title= title, active= active, skip= skip, limit= limit,
            user_details = user_details, db_= db_)
        return results

    bible_videos = graphene.List(types.BibleVideo,
        description="Query Bible Videos listed in vachan-db",
        source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        title=graphene.String(), theme=graphene.String(),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_videos(self, info, source_name, book_code=None, title=None, theme=None,
        active=True, skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Bible Videos')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/biblevideos/{source_name}"
        req.path_params["source_name"] = source_name
        results = content_apis.get_biblevideo(request = req,
            source_name =source_name, book_code = book_code,
            title =title, theme = theme, skip = skip, limit = limit,
            user_details =user_details, db_ = db_, active=active)
        return results

    bible_contents = graphene.List(types.BibleContent,
        description="Query bible usfms, jsons and audios in vachan-db",
        source_name=graphene.String(required=True),
        book_code=graphene.String(description="3 letter code like, gen, mat etc"),
        active=graphene.Boolean(), skip=graphene.Int(), limit=graphene.Int())
    def resolve_bible_contents(self, info, source_name, book_code=None, active=True,
        skip=0, limit=100):
        '''resolver'''
        log.info('In GraphQL Get Bible Contents')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/bibles/{source_name}/books"
        req.path_params["source_name"] = source_name
        results = content_apis.get_available_bible_book(request= req,
            source_name= source_name, book_code= book_code, active= active,
            skip= skip, limit= limit, user_details =user_details, db_= db_,
            content_type = "all")
        return results

    versification = graphene.Field(types.Versification,
        description="Query versification structure of a bible in vachan-db",
        source_name=graphene.String(required=True))
    def resolve_versification(self, info, source_name):
        '''resolver'''
        log.info('In GraphQL Get Versification')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/bibles/{source_name}/versification"
        req.path_params["source_name"] = source_name
        results = content_apis.get_bible_versification(request=req,
            source_name = source_name, user_details = user_details, db_=db_)
        return results

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
        log.info('In GraphQL Get Bible Verses')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = f"/v2/bibles/{source_name}/verses"
        req.path_params["source_name"] = source_name
        results = content_apis.get_bible_verse(request= req,
            source_name= source_name, book_code= book_code,
            chapter= chapter, verse= verse, last_verse= last_verse,
            search_phrase= search_phrase, active= active, skip= skip,
            limit= limit, user_details =user_details, db_= db_)
        return results

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
        log.info('In GraphQL Get Agmt Projects')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/projects"
        results = translation_apis.get_projects(request= req,
            project_name=project_name, source_language=source_language,
            target_language=target_language, active=active, user_id=user_id,
            skip= skip, limit= limit, user_details =user_details, db_=db_)
        return results

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
        log.info('In GraphQL Get AGMT Project Tokens')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/project/tokens"
        results = translation_apis.get_tokens(request= req, project_id=project_id,
        books=books, sentence_id_range=sentence_id_range, sentence_id_list=sentence_id_list,
        use_translation_memory=use_translation_memory, include_phrases=include_phrases,
        include_stopwords=include_stopwords, user_details = user_details, db_= db_)
        return results

    agmt_project_token_translation = graphene.Field(types.TokenTranslation,
        description="Query the translation done for a token in an AgMT project",
        project_id=graphene.ID(required=True), sentence_id=graphene.Int(required=True),
        offset=graphene.List(graphene.Int, required=True,
        description="Requires exactly two numbers"))
    def resolve_agmt_project_token_translation(self, info, project_id, sentence_id, offset):
        '''resolver'''
        log.info('In GraphQL AGMT Project Token Translations')
        db_ = info.context["request"].db_session
        # occurrences = [{"sentenceId":sentence_id, "offset":offset}]
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/project/token-translations"
        # return projects_crud.obtain_agmt_token_translation(db_, project_id, token=None,
        #     occurrences=occurrences)[0]
        results = translation_apis.get_token_translation(request=req,project_id=project_id,
        token=None, sentence_id=sentence_id, offset=offset, user_details=user_details,
        db_=db_)
        return results

    #Agmt get token Sentance
    agmt_project_token_sentences = graphene.List(types.Sentence,
        description="Query the translation done for sentance in an AgMT project",
        project_id=graphene.ID(required=True),token=graphene.String(required=True),
        occurrences = graphene.List(types.TokenOccurenceInput,required=True))
    def resolve_agmt_project_token_sentences(self, info, project_id, token, occurrences):
        '''resolver'''
        log.info('In GraphQL Get AGMT Token Sentence')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/autographa/project/token-sentences"
        # return projects_crud.get_agmt_source_per_token(db_,project_id,token,occurrences)
        results = translation_apis.get_token_sentences(request=req, project_id=project_id,
        token=token, occurrences=occurrences, user_details=user_details, db_=db_)
        return results

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
    async def resolve_suggest_translation(self, info, source_language,
        sentence_list, target_language, punctuations=None, stopwords=None):
        '''resolver'''
        log.info('In GraphQL Get Suggest Translation')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/suggestions"
        # results =  nlp_crud.auto_translate(db_=db_,sentence_list=sentence_list,source_lang=\
        #     source_language,target_lang=target_language,punctuations=punctuations,\
        #         stop_words=stopwords)
        results = await translation_apis.suggest_translation(request=req,
            source_language=source_language,target_language=target_language,
            sentence_list=sentence_list,punctuations=punctuations,stopwords=stopwords,
            user_details=user_details, db_=db_)
        content_list = []
        for item in results:
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
        log.info('In GraphQL Get AGMT Draft USFM')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/project/draft"
        # return projects_crud.obtain_agmt_draft(db_, project_id, books,
        #     sentence_id_list, sentence_id_range, output_format=schemas_nlp.DraftFormats.USFM)
        results = translation_apis.get_draft(request=req, project_id=project_id,
        books=books, sentence_id_list=sentence_id_list, sentence_id_range=sentence_id_range,
        output_format= schemas_nlp.DraftFormats.USFM ,user_details=user_details, db_=db_)
        return results

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
        log.info('In GraphQL Get AGMT Alignment')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/project/draft"
        # return projects_crud.obtain_agmt_draft(db_, project_id, books,
        #     sentence_id_list, sentence_id_range, output_format=schemas_nlp.DraftFormats.JSON)
        results = translation_apis.get_draft(request=req, project_id=project_id,
        books=books, sentence_id_list=sentence_id_list, sentence_id_range=sentence_id_range,
        output_format= schemas_nlp.DraftFormats.JSON ,user_details=user_details, db_=db_)
        return results

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
        log.info('In GraphQL Get AGMT Project Source')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/project/sentences"
        # return nlp_crud.obtain_agmt_source(db_, project_id, books, sentence_id_list,
        #     sentence_id_range, with_draft=True)
        results = translation_apis.get_project_source(request= req,project_id=project_id,
            books=books,sentence_id_list=sentence_id_list,sentence_id_range=sentence_id_range,
            with_draft=True, user_details =user_details, db_= db_)
        return results

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
        log.info('In GraphQL Get AGMT Project Progress')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/autographa/project/progress"
        # return projects_crud.obtain_agmt_progress(db_, project_id, books,
        #     sentence_id_list, sentence_id_range)
        results = translation_apis.get_progress(request= req,project_id=project_id,
            books=books,sentence_id_list=sentence_id_list,
            sentence_id_range=sentence_id_range, user_details =user_details, db_=db_)
        return results

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
        log.info('In GraphQL Get Gloss')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/translation/gloss"
        # return nlp_crud.glossary(db_, source_language, target_language, token,
        # context=context,token_offset=token_offset)
        results = translation_apis.get_glossary(request=req, source_language=source_language,
            target_language=target_language,token=token, context=context, token_offset=token_offset,
            user_details=user_details, db_=db_)
        return results

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
        log.info('In GraphQL Tokenize')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/tokens"
        # return nlp_crud.get_generic_tokens(db_, source_language, sentence_list, target_language,
        #     punctuations= punctuations, stopwords=stopwords, include_phrases = include_phrases,
        #     use_translation_memory=use_translation_memory, include_stopwords=include_stopwords)
        results = translation_apis.tokenize(request=req, source_language=source_language,
            sentence_list=sentence_list, target_language=target_language,
            use_translation_memory = use_translation_memory, include_phrases=include_phrases,
            include_stopwords=include_stopwords, punctuations=punctuations, stopwords=stopwords,
            user_details=user_details, db_=db_)
        return results

    translate_token = graphene.List(types.Sentence,
        description='replace provided tokens with translation in the input sentences',
        source_language=graphene.String(required=True,
            description="language code as per bcp47(usually 2 letter code)"),
        target_language=graphene.String(required=True,
            description="language code as per bcp47(usually 2 letter code)"),
        sentence_list=graphene.List(types.SentenceInput, required=True),
        token_translations=graphene.List(types.TokenUpdate, required=True),
        use_data_for_learning=graphene.Boolean())
    async def resolve_translate_token(self, info, source_language, target_language, sentence_list,
        token_translations, use_data_for_learning=True):
        '''resolver'''
        log.info('In GraphQL Translate Token')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/token-translate"
        new_sent_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        new_token_list =[ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.TokenUpdate)
                for item in token_translations]
        # return nlp_crud.replace_bulk_tokens(db_, new_sent_list, new_token_list, source_language,
        #     target_language, use_data_for_learning=use_data_for_learning)
        results = await translation_apis.token_replace(request=req, sentence_list=new_sent_list,
            token_translations= new_token_list, source_language=source_language,
            target_language=target_language, use_data_for_learning=use_data_for_learning,
            user_details=user_details,db_=db_)
        return results["data"]


    convert_to_usfm = graphene.List(graphene.String,
        description="Converts drafts to usfm",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_usfm(self, info, sentence_list):
        '''resolver'''
        log.info('In GraphQL Convert to USFM')
        # db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/draft"
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        # return nlp_crud.obtain_draft(new_list,
        #     doc_type=schemas_nlp.TranslationDocumentType.USFM)
        results = translation_apis.generate_draft(request=req, sentence_list=new_list,
            doc_type=schemas_nlp.TranslationDocumentType.USFM,user_details=user_details)
        return results

    convert_to_alignment = graphene.Field(types.Metadata,
        description="Converts sentences and drafts to alignment-json",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_alignment(self, info, sentence_list):
        '''resolver'''
        log.info('In GraphQL Convert to Alignment')
        # db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/draft"
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        # return nlp_crud.obtain_draft(new_list,
        #     doc_type=schemas_nlp.TranslationDocumentType.JSON)
        results = translation_apis.generate_draft(request=req, sentence_list=new_list,
            doc_type=schemas_nlp.TranslationDocumentType.JSON, user_details=user_details)
        return results

    convert_to_csv = graphene.String(
        description="Converts sentences and drafts to CSV format",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_csv(self, info, sentence_list):
        '''resolver'''
        log.info('In GraphQL Convert to CSV')
        # db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/draft"
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        # return nlp_crud.obtain_draft(new_list,
        #     doc_type=schemas_nlp.TranslationDocumentType.CSV)
        results = translation_apis.generate_draft(request=req, sentence_list=new_list,
            doc_type=schemas_nlp.TranslationDocumentType.CSV,user_details=user_details)
        return results

    convert_to_text = graphene.String(
        description="Converts drafts to alignment-json",
        sentence_list=graphene.List(types.SentenceInput, required=True))
    def resolve_convert_to_text(self, info, sentence_list):
        '''resolver'''
        log.info('In GraphQL Get Convert to Text')
        # db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "PUT"
        req.scope['path'] = "/v2/translation/draft"
        new_list = [ utils.convert_graphene_obj_to_pydantic(item, schemas_nlp.DraftInput)
                for item in sentence_list]
        # return nlp_crud.obtain_draft(new_list,
        #     doc_type=schemas_nlp.TranslationDocumentType.TEXT)
        results = translation_apis.generate_draft(request=req, sentence_list=new_list,
            doc_type=schemas_nlp.TranslationDocumentType.TEXT,user_details=user_details)
        return results

    login = graphene.Field(types.LoginResponse,
        description="Login User for getting Token",
        user_email = graphene.String(required=True),
        password = graphene.String(required=True))
    def resolve_login(self, info, user_email , password):
        """resolver"""
        log.info('In GraphQL User Login')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/user/login"
        return auth_api.login(user_email= user_email,password= password,
            request= req ,user_details = user_details, db_= db_)

    logout = graphene.String(
        description="Logout user")
    def resolve_logout(self, info):
        """resolve"""
        log.info('In GraphQL User Logout')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/user/logout"
        response = auth_api.logout(request=req,
            user_details=user_details, db_=db_)
        return response["message"]

    #Source Get-Sentence Extract Text Contents
    extract_text_contents = graphene.List(types.ExtractSentenceResposne,
        description="""A generic API for all content type tables to get just the text
        contents of that table that could be used for translation, as corpus for NLP 
        operations like SW identification.If source_name is provided, only that filter 
        will be considered over content_type & language""",
        source_name=graphene.String(),
        books = graphene.List(graphene.String,description="3 letter code like, gen, mat etc"),
        language_code=graphene.String(
                description="language code as per bcp47(usually 2 letter code)"),
        content_type=graphene.String(),skip=graphene.Int(), limit=graphene.Int())
    async def resolve_extract_text_contents(self, info, source_name=None,
        books=None, language_code=None, content_type=None, skip=0, limit=100):
        """resolve"""
        log.info('In GraphQL Extract Text contents')
        db_ = info.context["request"].db_session
        user_details , req = get_user_or_none_graphql(info)
        req.scope['method'] = "GET"
        req.scope['path'] = "/v2/sources/get-sentence"
        response = await content_apis.extract_text_contents(request=req,
            source_name=source_name, books=books, language_code=language_code,
            content_type=content_type, skip=skip, limit=limit,
            user_details= user_details, db_=db_)
        return response
