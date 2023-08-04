'''API endpoints for AgMT app'''

from typing import List
from fastapi import APIRouter, Query, Body, Depends, Request, Path, BackgroundTasks
from sqlalchemy.orm import Session


from dependencies import get_db, log, AddHiddenInput
from schema import schemas, schemas_nlp, schema_auth, schema_content
from crud import nlp_crud, projects_crud, nlp_sw_crud, structurals_crud, utils
from custom_exceptions import GenericException
from routers import content_apis
from auth.authentication import get_user_or_none,get_auth_access_check_decorator

router = APIRouter()
#pylint: disable=too-many-arguments,unused-argument
############## Translation Projects ##########################
@router.get('/v2/text/translate/token-based/projects',
    response_model=List[schemas_nlp.TranslationProject],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    status_code=200, tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def get_projects(request: Request,
    project_name:str=Query(None,example="Hindi-Bilaspuri Gospels"),
    source_language:schemas.LangCodePattern=Query(None,example='en'),
    target_language:schemas.LangCodePattern=Query(None,example='ml'),
    active:bool=True, user_id:str=Query(None),
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db),
    filtering_required=Depends(AddHiddenInput(value=True))):
    '''Fetches the list of proejct and their details'''
    log.info('In get_projects')
    log.debug('project_name: %s, source_language:%s, target_language:%s,\
        active:%s, user_id:%s',project_name, source_language, target_language, active, user_id)
    return projects_crud.get_translation_projects(db_, project_name, source_language,
        target_language, active=active, user_id=user_id, skip=skip, limit=limit)

@router.post('/v2/text/translate/token-based/projects', status_code=201,
    response_model=schemas_nlp.TranslationProjectUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def create_project(request: Request,
    project_obj:schemas_nlp.TranslationProjectCreate,
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Creates a new translation project'''
    log.info('In create_project')
    log.debug('project_obj: %s',project_obj)
    return {'message': "Project created successfully",
        "data": projects_crud.create_translation_project(db_=db_, project=project_obj,
            user_id=user_details['user_id'])}

@router.put('/v2/text/translate/token-based/projects', status_code=201,
    response_model=schemas_nlp.TranslationProjectUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def update_project(request: Request, project_obj:schemas_nlp.TranslationProjectEdit,
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.PROJECT.value))):
    # operates_on=schema_auth.ResourceType.PROJECT.value):
    '''Adds more books to a Translation project's source. Delete or activate project.'''
    log.info('In update_project')
    log.debug('project_obj: %s',project_obj)
    if project_obj.selectedBooks:
        sentences = []
        books_param_list = ""
        for buk in project_obj.selectedBooks.books:
            books_param_list += f"&books={buk}"#pylint: disable=R1713

        # request.scope['method'] = 'GET'
        # request._url = URL('/v2/resources')#pylint: disable=protected-access
        response = await content_apis.extract_text_contents(
            request=request,
            resource_name=project_obj.selectedBooks.bible,
            #typeerror
            books=project_obj.selectedBooks.books,
            language_code=None,
            content_type='bible',
            skip=0, limit=100000,
            user_details = user_details,
            db_=db_,
            operates_on=schema_auth.ResourceType.CONTENT.value)
        if "error" in response:
            raise GenericException(response['error'])
        for item in response:
            sentences.append(schemas_nlp.SentenceInput(
                sentenceId=item[0], surrogateId=item[1], sentence=item[2]))
        if project_obj.sentenceList is not None:
            project_obj.sentenceList += sentences
        else:
            project_obj.sentenceList = sentences
    return {'message': "Project updated successfully",
        "data": projects_crud.update_translation_project(db_, project_obj,
            user_id=user_details['user_id'])}

@router.delete('/v2/text/translate/token-based/projects', status_code=201,
    response_model=schemas.DeleteResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}, 403:{"model": schemas.ErrorResponse}},
    tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def remove_project(request: Request,
    project_id:int = Query(..., example=100001),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Removes a project.'''
    log.info('In remove_project')
    log.debug('project_id:%s',project_id)
    deleted_content = projects_crud.remove_translation_project(db_, project_id)
    delcont = structurals_crud.add_deleted_data(db_, del_content= deleted_content,
        table_name = "translation_projects", deleting_user=user_details['user_id'])
    return {'message': f"Project with identity {project_id} deleted successfully",
            "data": delcont}

@router.post('/v2/text/translate/token-based/project/user', status_code=201,
    response_model=schemas_nlp.UserUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def add_user(request: Request,project_id:int, user_id:str,
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Adds new user to a project.'''
    log.info('In add_user')
    log.debug('project_id: %s, user_id:%s',project_id, user_id)
    return {'message': "User added to project successfully",
        "data": projects_crud.add_project_user(db_, project_id, user_id,
            current_user=user_details['user_id'])}

@router.put('/v2/text/translate/token-based/project/user', status_code=201,
    response_model=schemas_nlp.UserUpdateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def update_user(request: Request,user_obj:schemas_nlp.ProjectUser,
    user_details =Depends(get_user_or_none),db_:Session=Depends(get_db)):
    '''Changes role, metadata or active status of user of a project.'''
    log.info('In update_user')
    log.debug('user_obj:%s',user_obj)
    return {'message': "User updated in project successfully",
        "data": projects_crud.update_project_user(db_, user_obj,
            current_user=user_details['user_id'])}

@router.delete('/v2/text/translate/token-based/project/user', status_code=201,
    response_model=schemas.DeleteResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}, 403:{"model": schemas.ErrorResponse}},
    tags=['Translation-Project management'])
@get_auth_access_check_decorator
async def remove_user(request: Request,project_id:int, user_id:str,
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Removes a user from a project.'''
    log.info('In remove_user')
    log.debug('project_id:%s, user_id:%s',project_id, user_id)
    deleted_content = projects_crud.remove_project_user(db_, project_id, user_id,
            current_user=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_, del_content= deleted_content['db_content'],
        table_name = "translation_project_users", deleting_user=user_details['user_id'])
    return {'message':  "User removed from project successfully",
            "data": delcont}

############## Translation APIs ##########################
@router.get('/v2/text/translate/token-based/project/tokens', response_model=List[schemas_nlp.Token],
    response_model_exclude_unset=True,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    status_code=200, tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_tokens(request: Request, project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=(410010001, 41001999)),
    sentence_id_list:List[int]=Query(None, example=[41001001,41001002,41001003]),
    use_translation_memory:bool=True, include_phrases:bool=True, include_stopwords:bool=False,
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Tokenize the source texts. Optional params books,
    sentence_id_range or sentence_id_list can be used to specify the source verses.
    If more than one of these filters are given, only one would be used
    in the following order of priority: books, range, list.
    Flags use_translation_memory, include_phrases and include_stopwords can be
    used to alter the tokens output as per user need'''
    log.info('In get_tokens')
    log.debug('project_id: %s, books:%s, sentence_id_range:%s, sentence_id_list:%s, \
        use_translation_memory:%s, include_phrases:%s, include_stopwords:%s', project_id,
        books, sentence_id_range, sentence_id_range, use_translation_memory,
        include_phrases, include_stopwords)
    return nlp_crud.get_project_tokens(db_, project_id, books, sentence_id_range, sentence_id_list,
        use_translation_memory=use_translation_memory,
        include_phrases = include_phrases, include_stopwords=include_stopwords)

@router.put('/v2/text/translate/token-based/project/tokens',
    response_model=schemas_nlp.TranslateResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    status_code=201, tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def apply_token_translations(request: Request,project_id:int=Query(...,example="1022004"),
    token_translations:List[schemas_nlp.TokenUpdate]=Body(...), return_drafts:bool=True,
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Updates drafts using the provided token translations and returns updated verses'''
    log.info('In apply_token_translations')
    log.debug('project_id: %s, token_translations:%s, ',project_id, token_translations)
    drafts = nlp_crud.save_project_translations(db_, project_id, token_translations, return_drafts,
        user_id=user_details['user_id'])
    return {"message": "Token translations saved", "data":drafts}

@router.get('/v2/text/translate/token-based/project/token-translations', status_code=200,
    response_model= schemas_nlp.Translation,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_token_translation(request: Request,project_id:int=Query(...,example="1022004"),
    token:str=Query(...,example="duck"),
    sentence_id:int=Query(..., example="41001001"),
    offset:List[int]=Query(..., max_items=2,min_items=2,example=[0,4]),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Get the current translation for specific tokens providing their occurence in source'''
    log.info('In get_token_translation')
    occurrences = [{"sentenceId":sentence_id, "offset":offset}]
    log.debug('project_id: %s, token:%s, occurrences:%s',project_id, token, occurrences)
    return projects_crud.obtain_project_token_translation(db_, project_id, token, occurrences)

@router.put('/v2/text/translate/token-based/project/token-sentences', status_code=200,
    response_model = List[schemas_nlp.Sentence],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_token_sentences(request: Request,project_id:int=Query(...,example="1022004"),
    token:str=Query(...,example="duck"),
    occurrences:List[schemas_nlp.TokenOccurence]=Body(..., example=[
        {"sentenceId":41001001, "offset":[0,4]}]),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Pass in the occurence list of a token and get all sentences it is present in with draftMeta
    that allows easy highlight of token and translation'''
    log.info('In get_token_sentences')
    log.debug('project_id: %s, token:%s, occurrences:%s',project_id, token, occurrences)
    return projects_crud.get_project_source_per_token(db_, project_id, token, occurrences)

@router.get('/v2/text/translate/token-based/project/draft', status_code=200,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    415: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_draft(request: Request,project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    output_format:schemas_nlp.DraftFormats=Query(schemas_nlp.DraftFormats.USFM),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Obtains draft, as per current project status, in any of the formats:
    text for UI display, usfm for downloading, or alignment-json for project export'''
    log.info('In get_draft')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s,\
        output_format:%s',project_id, books, sentence_id_list, sentence_id_range,
        output_format)
    return projects_crud.obtain_project_draft(db_, project_id, books,
        sentence_id_list, sentence_id_range, output_format=output_format)

@router.put('/v2/text/translate/token-based/project/draft', status_code=201,
    response_model = List[schemas_nlp.Sentence],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    415: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def update_draft(request: Request,project_id:int=Query(...,example="1022004"),
    sentence_list:List[schemas_nlp.ProjectDraftInput]=Body(...),
    user_details =Depends(get_user_or_none),db_:Session=Depends(get_db)):
    '''Obtains draft, as per current project status, in any of the formats:
    text for UI display, usfm for downloading, or alignment-json for project export'''
    log.info('In update_draft')
    log.debug('project_id: %s, sentence_list:%s, user_details:%s',
        project_id, sentence_list, user_details)
    return projects_crud.update_project_draft(db_, project_id, sentence_list,
        user_details['user_id'])

@router.get('/v2/text/translate/token-based/project/sentences', status_code=200,
    response_model_exclude_unset=True, response_model=List[schemas_nlp.Sentence],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_project_source(request: Request,project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    with_draft:bool=False, only_ids:bool=False, user_details =Depends(get_user_or_none),
    db_:Session=Depends(get_db)):
    '''Obtains source sentences or verses, as per the filters'''
    log.info('In get_source')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s, \
         with_draft:%s, only_ids:%s',project_id, books, sentence_id_list, sentence_id_range,
        with_draft, only_ids)
    return projects_crud.obtain_project_source(db_, project_id, books, sentence_id_range,
        sentence_id_list, with_draft=with_draft, only_ids=only_ids)

@router.delete('/v2/text/translate/token-based/project/sentences', status_code=201,
    response_model=schemas.DeleteResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}, 403:{"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def remove_sentence(request: Request,project_id:int=Query(...,example="1022004"),
    sentence_id:int=Query(...,example="41001001"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Remove sentence.'''
    log.info('In remove_sentence')
    log.debug('project_id:%s, sentence_id:%s',project_id, sentence_id)
    deleted_content = projects_crud.remove_project_sentence(db_, project_id,sentence_id,
        user_id=user_details['user_id'])
    delcont = structurals_crud.add_deleted_data(db_, del_content=  deleted_content['db_content'],
        table_name = "translation_sentences", deleting_user=user_details['user_id'])
    return {'message': f"Sentence with identity {sentence_id} deleted successfully",
            "data": delcont}

@router.get('/v2/text/translate/token-based/project/progress', status_code=200,
    response_model= schemas_nlp.Progress,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_progress(request: Request,project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Obtains source sentences or verses, as per the filters'''
    log.info('In get_progress')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s',
        project_id, books, sentence_id_list, sentence_id_range)
    return projects_crud.obtain_project_progress(db_, project_id, books,
        sentence_id_list, sentence_id_range)

@router.get('/v2/text/translate/token-based/project/versification', status_code=200,
    response_model= schema_content.Versification,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Project-Based-Translation'])
@get_auth_access_check_decorator
async def get_project_versification(request: Request,project_id:int=Query(...,example="1022004"),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Obtains versification structure for source sentences or verses'''
    log.info('In get_project_versification')
    log.debug('project_id: %s', project_id)
    return projects_crud.get_project_source_versification(db_, project_id)

@router.put('/v2/text/translate/token-based/project/suggestions', status_code=201,
    response_model=List[schemas_nlp.Sentence],
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=["Translation Suggestion"])
@get_auth_access_check_decorator
async def suggest_auto_translation(request: Request,project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    confirm_all:bool=False,user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Try to fill draft with suggestions. If confirm_all is set, will only change status of all
    "suggestion" to "confirmed" in the selected sentences and will not fill in new suggestion'''
    log.info('In suggest_translation')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s',
        project_id, books, sentence_id_list, sentence_id_range)
    return nlp_crud.project_suggest_translations(db_, project_id, books,
        sentence_id_list = sentence_id_list, user_id = user_details['user_id'],
        sentence_id_range = sentence_id_range,confirm_all = confirm_all)

########### Generic Translation ##################
@router.put('/v2/text/translate/token-based/tokens', response_model=List[schemas_nlp.Token],
    response_model_exclude_unset=True, status_code=200,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Generic Translation'])
@get_auth_access_check_decorator
async def tokenize(request: Request,
                   source_language:schemas.LangCodePattern=Query(...,example="hi"),
    sentence_list:List[schemas_nlp.SentenceInput]=Body(...),
    target_language:schemas.LangCodePattern=Query(None,example="ml"),
    use_translation_memory:bool=True, include_phrases:bool=True, include_stopwords:bool=False,
    punctuations:List[str]=Body(None), stopwords:schemas_nlp.Stopwords=Body(None),
    user_details =Depends(get_user_or_none),db_:Session=Depends(get_db)):
    '''Tokenize any set of input sentences.
    Makes use of translation memory and stopwords for forming better phrase tokens.
    Flags use_translation_memory, include_phrases and include_stopwords can be
    used to alter the tokens output as per user need'''
    log.info('In tokenize')
    log.debug('source_language: %s, sentence_list:%s, target_language:%s, punctuations:%s,\
        stopwords:%s, use_translation_memory:%s, include_phrases:%s, include_stopwords:%s',
        source_language, sentence_list, target_language, punctuations, stopwords,
        use_translation_memory, include_phrases, include_stopwords)
    return nlp_crud.get_generic_tokens(db_, source_language, sentence_list, target_language,
        punctuations =punctuations, stopwords = stopwords,
        use_translation_memory = use_translation_memory, include_phrases = include_phrases,
        include_stopwords = include_stopwords)

@router.put('/v2/text/translate/token-based/token-translate',
    response_model=schemas_nlp.TranslateResponse,
    status_code=200,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    tags=['Generic Translation'])
@get_auth_access_check_decorator
async def token_replace(request: Request,sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    token_translations:List[schemas_nlp.TokenUpdate]=Body(...),
    source_language:schemas.LangCodePattern=Query(...,example='hi'),
    target_language:schemas.LangCodePattern=Query(...,example='ml'),
    use_data_for_learning:bool=True,
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Perform token replacement on provided sentences and
    returns obtained drafts and draft_meta'''
    log.info('In token_replace')
    log.debug('sentence_list:%s, token_translations:%s,\
        source_lanuage:%s, target_language:%s, use_data_for_learning:%s',
        sentence_list, token_translations, source_language,
        target_language, use_data_for_learning)
    result = nlp_crud.replace_bulk_tokens(db_, sentence_list, token_translations, source_language,
        target_language, use_data_for_learning=use_data_for_learning)
    return {"message": "Tokens replaced with translations", "data": result}

@router.put('/v2/text/translate/token-based/draft', status_code=200,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    415: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse}},
    tags=['Generic Translation'])
@get_auth_access_check_decorator
async def generate_draft(request: Request,sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    doc_type:schemas_nlp.TranslationDocumentType=Query(schemas_nlp.TranslationDocumentType.USFM),
    user_details =Depends(get_user_or_none)):
    '''Converts the drafts in input sentences to following output formats:
    usfm, text, csv or alignment-json'''
    log.info('In generate_draft')
    log.debug('sentence_list:%s, doc_type:%s',sentence_list, doc_type)
    for sent in sentence_list:
        if sent.draftMeta is not None and sent.draftMeta != []:
            utils.validate_draft_meta(sent.sentence, sent.draft, sent.draftMeta)
    return nlp_crud.obtain_draft(sentence_list, doc_type)

@router.put('/v2/text/translate/token-based/suggestions', response_model=List[schemas_nlp.Sentence],
    status_code=200,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    tags=["Translation Suggestion"])
@get_auth_access_check_decorator
async def suggest_translation(request: Request,
    source_language:schemas.LangCodePattern=Query(...,example="hi"),
    target_language:schemas.LangCodePattern=Query(...,example="ml"),
    sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    punctuations:List[str]=Body(None), stopwords:schemas_nlp.Stopwords=Body(None),
    user_details =Depends(get_user_or_none),db_:Session=Depends(get_db)):
    '''Attempts to tokenize sentences and prepare draft with autogenerated suggestions
    If draft and draft_meta are provided indicating some portion of sentence is user translated,
    then it is left untouched.'''
    log.info("In suggest_translation")
    log.debug('source_language:%s, target_language:%s, sentence_list:%s,punctuations:%s\
        stopwords:%s', source_language, target_language, sentence_list, punctuations, stopwords)
    for sent in sentence_list:
        if sent.draftMeta is not None and sent.draftMeta != []:
            utils.validate_draft_meta(sent.sentence, sent.draft, sent.draftMeta)
    return nlp_crud.auto_translate(db_, sentence_list, source_language, target_language,
        punctuations=punctuations, stopwords=stopwords)

@router.get('/v2/nlp/gloss', response_model=schemas_nlp.GlossOutput,
    status_code=200,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    tags=["Nlp"])
@get_auth_access_check_decorator
async def get_glossary(request: Request,
    source_language:schemas.LangCodePattern=Query(...,example="en"),
    target_language:schemas.LangCodePattern=Query(...,example="hi"),
    token:str=Query(...,example="duck"),
    context:str=Query(None,example="The duck swam in the lake"),
    token_offset:List[int]=Query(None,max_items=2,min_items=2,example=(4,8)),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Finds translation suggestions or gloss for one token in the given context'''
    log.info('In get_glossary')
    log.debug('source_language:%s, target_language:%s, token:%s, context:%s,\
        token_offset:%s',source_language, target_language, token,
            context, token_offset)
    return nlp_crud.glossary(db_, source_language, target_language, token,
    context=context, token_offset=token_offset)

@router.get('/v2/nlp/gloss-entries', response_model=List[schemas_nlp.TranslationMemoryOut],
    status_code=200,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    tags=["Nlp"])
@get_auth_access_check_decorator
async def get_glossary_entries(request: Request,
    source_language:schemas.LangCodePattern=Query(...,example="en"),
    target_language:schemas.LangCodePattern=Query(...,example="hi"),
    token:str=Query(None,example="duck"),
    skip: int=Query(None, ge=0), limit: int=Query(None, ge=0),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Searches the translation memory for matching entries. Not context aware'''
    log.info('In get_glossary_entries')
    log.debug('source_language:%s, target_language:%s, token:%s',
        source_language, target_language, token)
    response = nlp_crud.get_glossary_list(db_, source_language, target_language, token,
    skip=skip, limit=limit)
    return response['token_translation_count']

@router.get('/v2/nlp/gloss-entries/count',
    response_model= schemas_nlp.GlossCount,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},415:{"model": schemas.ErrorResponse},
    404:{"model": schemas.ErrorResponse},}, status_code=200, tags=["Nlp"])
@get_auth_access_check_decorator
async def get_gloss_count(request: Request,
    source_language:schemas.LangCodePattern=Query(...,example="en"),
    target_language:schemas.LangCodePattern=Query(...,example="hi"),
    token:str=Query(None,example="love"),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Counts all glossary entries in translation memory between two languages.
        * Also counts unique tokens in translation memory
   `    * Can filter with or without search word/token
        * Source and target language should be specified
        * "tokenTranslationCount" in response counts different
            translations of same word as different.
        * "tokenCount" in response doesn't consider the multiple translations
            but give the count of unique source tokens.'''
    log.info('In get_glossary_count')
    log.debug('source_language:%s, target_language:%s, token:%s',
        source_language, target_language, token)
    response = nlp_crud.get_glossary_list(db_, source_language, target_language, token)
    response['tokenTranslationCount'] = len(response['token_translation_count'])
    response['tokenCount'] = len(response['token_count'])
    return response

@router.post('/v2/nlp/gloss', response_model=schemas_nlp.GlossUpdateResponse,
    status_code=201,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=["Nlp"])
@get_auth_access_check_decorator
async def add_gloss(request: Request,
    source_language:schemas.LangCodePattern=Query(...,example='en'),
    target_language:schemas.LangCodePattern=Query(..., example="hi"),
    token_translations:List[schemas_nlp.GlossInput]=Body(...),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Load a list of predefined tokens and translations to improve tokenization and suggestion'''
    log.info('In add_gloss')
    log.debug('source_language:%s, target_language:%s, token_translations:%s',
        source_language, target_language, token_translations)
    tw_data = nlp_crud.add_to_translation_memory(db_,source_language, target_language,
        token_translations)
    return { "message": "Added to glossary", "data":tw_data }

@router.put('/v2/nlp/gloss', response_model=schemas_nlp.TranslationMemoryUpdateResponse,
    status_code=200,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    tags=["Nlp"])
@get_auth_access_check_decorator
async def update_glossary(request: Request,
    token_info:schemas_nlp.TranslationMemoryUpdate=Body(...),
    user_details =Depends(get_user_or_none),db_:Session=Depends(get_db)):
    '''Updates translation and/or metadata of a token'''
    log.info("In update-glossary")
    token_data = nlp_crud.edit_glossary(db_,token_info=token_info)
    return { "message": "Glossary Updated", "data":token_data }

@router.delete('/v2/nlp/gloss', status_code=201,
    response_model=schemas.DeleteResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}, 403:{"model": schemas.ErrorResponse}},
    tags=['Nlp'])
@get_auth_access_check_decorator
async def remove_glossary(request: Request,
    source_lang:schemas.LangCodePattern=Query(...,example="en"),
    target_lang:schemas.LangCodePattern=Query(...,example="hi"),
    token:str=Query(...,example="duck"),
    translation:str=Query(None,example="बत्तख"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Remove glossary.'''
    log.info('In remove_gloss')
    log.debug('source_language:%s,target_language:%s,token:%s,translation:%s',
        source_lang,target_lang,token,translation)
    deleted_content = nlp_crud.remove_glossary(db_, source_lang,target_lang,token,translation)
    delcont = structurals_crud.add_deleted_data(db_, del_content=  deleted_content['db_content'],
        table_name = "translation_memory", deleting_user=user_details['user_id'])
    return {'message': f"Token-Translation pair {token} -> {translation} deleted successfully",
            "data": delcont}

@router.post('/v2/nlp/alignment', response_model=schemas_nlp.GlossUpdateResponse,
    status_code=201,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    415: {"model": schemas.ErrorResponse}},tags=["Nlp"])
@get_auth_access_check_decorator
async def add_alignments(request: Request,
    source_language:schemas.LangCodePattern, target_language:schemas.LangCodePattern,
    alignments:List[schemas_nlp.Alignment],
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Prepares training data with alignments and update translation memory & suggestion models'''
    log.info('In add_alignments')
    log.debug('source_language:%s, target_language:%s, alignments:%s',
        source_language, target_language, alignments)
    tw_data = nlp_crud.alignments_to_trainingdata(db_,src_lang=source_language,
    trg_lang=target_language, alignment_list=alignments, user_id=user_details['user_id'])
    return { "message": "Alignments used for learning", "data":tw_data }

@router.get('/v2/lookup/stopwords/{language_code}', response_model=List[schemas_nlp.StopWords],
    response_model_exclude_none=True, status_code=200,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=["Lookups"])
@get_auth_access_check_decorator
async def get_stop_words(request: Request,
    language_code:schemas.LangCodePattern=Path(...,example="hi"),
    include_system_defined:bool=True, include_user_defined:bool=True,
    include_auto_generated :bool=True, only_active:bool=True, skip: int=Query(0, ge=0),
    limit: int=Query(100, ge=0),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Api to retreive stopwords from lookup table'''
    log.info('In get_stop_words')
    log.debug('language_code:%s, include_system_defined:%s, include_user_defined:%s, \
        include_auto_generated:%s ,only_active:%s',language_code, include_system_defined,
        include_user_defined, include_auto_generated, only_active)
    return nlp_sw_crud.retrieve_stopwords(db_, language_code,
        include_system_defined=include_system_defined, include_user_defined=include_user_defined,
        include_auto_generated=include_auto_generated, only_active=only_active, skip=skip,
        limit=limit)

@router.put('/v2/lookup/stopwords/{language_code}',
    response_model=schemas_nlp.StopWordUpdateResponse, response_model_exclude_none=True,
    status_code=201,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Lookups'])
@get_auth_access_check_decorator
async def update_stop_words(request: Request,
    language_code:schemas.LangCodePattern=Path(...,example="hi"),
    sw_info:schemas_nlp.StopWordUpdate=Body(...),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Api to update fields of a stopword in lookup table'''
    log.info('In update_stop_words')
    log.debug('language_code:%s, sw_info:%s',language_code, sw_info)
    sw_data = nlp_sw_crud.update_stopword_info(db_, language_code, sw_info,user_details['user_id'])
    return { "message": "Stopword info updated successfully", "data":sw_data }

@router.post('/v2/lookup/stopwords/{language_code}',
    response_model=schemas_nlp.StopWordsAddResponse, response_model_exclude_none=True,
    status_code=201,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}},
    tags=['Lookups'])
@get_auth_access_check_decorator
async def add_stopwords(request: Request,
    language_code:schemas.LangCodePattern=Path(...,example="hi"),
    stopwords_list:List[str]=Body(..., example=["और", "के", "उसका"]),
    user_details =Depends(get_user_or_none), db_:Session=Depends(get_db)):
    '''Insert provided stopwords into db and returns added data'''
    log.info('In add_stopwords')
    log.debug('language_code:%s, stopwords_list:%s',language_code, stopwords_list)
    result = nlp_sw_crud.add_stopwords(db_, language_code, stopwords_list,
        user_id=user_details['user_id'])
    msg = f"{len(result)} stopwords added successfully"
    return {"message": msg, "data": result}

@router.delete('/v2/lookup/stopwords/{language_code}', status_code=201,
    response_model=schemas.DeleteResponse,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse},
    404: {"model": schemas.ErrorResponse}, 403:{"model": schemas.ErrorResponse}},
    tags=['Lookups'])
@get_auth_access_check_decorator
async def remove_stopword(request: Request,
    lang:schemas.LangCodePattern=Query(...,example="en"),
    stopword:str=Query(...,example="as"),
    user_details =Depends(get_user_or_none), db_: Session = Depends(get_db)):
    '''Api to remove stopwords from lookup table'''
    log.info('In remove_stopword')
    log.debug('language:%s,stopword:%s',lang,stopword)
    deleted_content = nlp_sw_crud.remove_stopword(db_, lang, stopword)
    delcont = structurals_crud.add_deleted_data(db_, del_content= deleted_content['db_content'],
        table_name = "stopwords_look_up", deleting_user=user_details['user_id'])
    return {'message':  "Stopword removed successfully",
            "data": delcont}

@router.post('/v2/nlp/stopwords/generate',
    response_model=schemas_nlp.StopWordsGenerateResponse, response_model_exclude_none=True,
    status_code=201,responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},401: {"model": schemas.ErrorResponse}},
    tags=['Nlp'])
@get_auth_access_check_decorator
async def generate_stopwords(request: Request, background_tasks: BackgroundTasks,
    language_code:schemas.LangCodePattern=Query(...,example="bi"),
    use_server_data:bool=True,
    source_name: schemas.TableNamePattern=Query(None,example="en_TW_1_vocabulary"),
    user_details =Depends(get_user_or_none),
    sentence_list:List[schemas_nlp.SentenceInput]=Body(None), db_:Session=Depends(get_db),
    operates_on=Depends(AddHiddenInput(value=schema_auth.ResourceType.LOOKUP.value))):#pylint: disable=unused-argument
    '''Auto generate stop words for a given language'''
    log.info('In generate_stopwords')
    log.debug('language_code:%s, use_server_data:%s, source_name:%s, sentence_list:%s',
        language_code, use_server_data, source_name, sentence_list)

    # job_info = create_job(
    #         request=request, #pylint: disable=W0613
    #         db_=db_, user_id=user_details['user_id'])
    job_info = nlp_sw_crud.create_job(db_=db_, user_id=user_details['user_id'])
    job_id = job_info.jobId
    background_tasks.add_task(nlp_sw_crud.generate_stopwords, db_, request, language_code,
        source_name, sentence_list, job_id, use_server_data=use_server_data,
        user_details=user_details)
    msg = "Generating stop words in background"
    # data = {"jobId": job_info['data']['jobId'], "status": job_info['data']['status']}
    data = {"jobId": job_info.jobId, "status": job_info.status}
    return {"message": msg, "data": data}

#################### Jobs ####################

# @router.post('/v2/jobs', response_model=schemas_nlp.JobCreateResponse, status_code=201,
#     tags=['Jobs'])
# def create_job(request:Request, #pylint: disable=W0613
#                 db_:Session=Depends(get_db), user_id="10101"):
#     '''Creates a new job'''
#     log.info('In create_job')
#     job_info = nlp_sw_crud.create_job(db_=db_, user_id=user_id)
#     return {'message': "Job created successfully",
#         "data": {"jobId": job_info.jobId, "status": job_info.status}}

@router.get('/v2/jobs', response_model=schemas_nlp.JobStatusResponse,
    response_model_exclude_none=True, status_code=200,
    responses={502: {"model": schemas.ErrorResponse},
    422: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse}},
    tags=['Jobs'])
@get_auth_access_check_decorator
async def check_job_status(request: Request,
    job_id:int=Query(...,example="100000"),user_details =Depends(get_user_or_none),
    db_:Session=Depends(get_db)):
    '''Checking the status of a job'''
    log.info('In check_job_status')
    log.debug('job_id:%s', job_id)
    result = nlp_sw_crud.check_job_status(db_, job_id)
    return result
