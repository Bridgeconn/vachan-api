'''API endpoints for AgMT app'''

from typing import List
from fastapi import APIRouter, Query, Body, Depends, Request
from sqlalchemy.orm import Session

from dependencies import get_db, log
import schemas
import schemas_nlp
from crud import nlp_crud, projects_crud
from custom_exceptions import GenericException
from routers import content_apis

router = APIRouter()
#pylint: disable=too-many-arguments
############## Autographa Projects ##########################
@router.get('/v2/autographa/projects', response_model=List[schemas_nlp.TranslationProject],
    status_code=200, tags=['Autographa-Project management'])
def get_projects(project_name:str=Query(None,example="Hindi-Bilaspuri Gospels"),
    source_language:schemas.LangCodePattern=Query(None,example='en'),
    target_language:schemas.LangCodePattern=Query(None,example='ml'),
    active:bool=True, user_id:int=Query(None),
    skip: int=Query(0, ge=0), limit: int=Query(100, ge=0), db_:Session=Depends(get_db)):
    '''Fetches the list of proejct and their details'''
    log.info('In get_projects')
    log.debug('project_name: %s, source_language:%s, target_language:%s,\
        active:%s, user_id:%s',project_name, source_language, target_language, active, user_id)
    return projects_crud.get_agmt_projects(db_, project_name, source_language, target_language,
        active=active, user_id=user_id, skip=skip, limit=limit)

@router.post('/v2/autographa/projects', status_code=201,
    response_model=schemas_nlp.TranslationProjectUpdateResponse,
    tags=['Autographa-Project management'])
def create_project(project_obj:schemas_nlp.TranslationProjectCreate, db_:Session=Depends(get_db)):
    '''Creates a new autographa MT project'''
    log.info('In create_project')
    log.debug('project_obj: %s',project_obj)
    return {'message': "Project created successfully",
        "data": projects_crud.create_agmt_project(db_=db_, project=project_obj, user_id=10101)}

@router.put('/v2/autographa/projects', status_code=201,
    response_model=schemas_nlp.TranslationProjectUpdateResponse,
    tags=['Autographa-Project management'])
def update_project(request: Request, project_obj:schemas_nlp.TranslationProjectEdit,
    db_:Session=Depends(get_db)):
    '''Adds more books to a autographa MT project's source. Delete or activate project.'''
    log.info('In update_project')
    log.debug('project_obj: %s',project_obj)
    if project_obj.selectedBooks:
        sentences = []
        books_param_list = ""
        for buk in project_obj.selectedBooks.books:
            books_param_list += "&books=%s"%(buk)
        response = content_apis.extract_text_contents(
            request=request,
            source_name=project_obj.selectedBooks.bible,
            books=project_obj.selectedBooks.books,
            language_code=None,
            content_type='bible',
            skip=0, limit=100000,
            db_=db_)
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
        "data": projects_crud.update_agmt_project(db_, project_obj, user_id=10101)}

@router.post('/v2/autographa/project/user', status_code=201,
    response_model=schemas_nlp.UserUpdateResponse, tags=['Autographa-Project management'])
def add_user(project_id:int, user_id:int, db_:Session=Depends(get_db)):
    '''Adds new user to a project.'''
    log.info('In add_user')
    log.debug('project_id: %s, user_id:%s',project_id, user_id)
    return {'message': "User added to project successfully",
        "data": projects_crud.add_agmt_user(db_, project_id, user_id, current_user=10101)}

@router.put('/v2/autographa/project/user', status_code=201,
    response_model=schemas_nlp.UserUpdateResponse, tags=['Autographa-Project management'])
def update_user(user_obj:schemas_nlp.ProjectUser, db_:Session=Depends(get_db)):
    '''Changes role, metadata or active status of user of a project.'''
    log.info('In update_user')
    log.debug('user_obj:%s',user_obj)
    return {'message': "User updated in project successfully",
        "data": projects_crud.update_agmt_user(db_, user_obj, current_user=10101)}

############## Autographa Translations ##########################
@router.get('/v2/autographa/project/tokens', response_model=List[schemas_nlp.Token],
    response_model_exclude_unset=True,
    status_code=200, tags=['Autographa-Translation'])
def get_tokens(project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=(410010001, 41001999)),
    sentence_id_list:List[int]=Query(None, example=[41001001,41001002,41001003]),
    use_translation_memory:bool=True, include_phrases:bool=True, include_stopwords:bool=False,
    db_:Session=Depends(get_db)):
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
    return nlp_crud.get_agmt_tokens(db_, project_id, books, sentence_id_range, sentence_id_list,
        use_translation_memory=use_translation_memory,
        include_phrases = include_phrases, include_stopwords=include_stopwords)

@router.put('/v2/autographa/project/tokens', response_model=schemas_nlp.TranslateResponse,
    status_code=201, tags=['Autographa-Translation'])
def apply_token_translations(project_id:int=Query(...,example="1022004"),
    token_translations:List[schemas_nlp.TokenUpdate]=Body(...), return_drafts:bool=True,
    db_:Session=Depends(get_db)):
    '''Updates drafts using the provided token translations and returns updated verses'''
    log.info('In apply_token_translations')
    log.debug('project_id: %s, token_translations:%s, ',project_id, token_translations)
    drafts = nlp_crud.save_agmt_translations(db_, project_id, token_translations, return_drafts,
        user_id=10101)
    return {"message": "Token translations saved", "data":drafts}

@router.get('/v2/autographa/project/token-translations', status_code=200,
    response_model=schemas_nlp.Translation,
    tags=['Autographa-Translation'])
def get_token_translation(project_id:int=Query(...,example="1022004"),
    token:str=Query(...,example="duck"),
    sentence_id:int=Query(..., example="41001001"),
    offset:List[int]=Query(..., max_items=2,min_items=2,example=[0,4]),
    db_:Session=Depends(get_db)):
    '''Get the current translation for specific tokens providing their occurence in source'''
    log.info('In get_token_translation')
    occurrences = [{"sentenceId":sentence_id, "offset":offset}]
    log.debug('project_id: %s, token:%s, occurrences:%s',project_id, token, occurrences)
    return projects_crud.obtain_agmt_token_translation(db_, project_id, token, occurrences)[0]

@router.put('/v2/autographa/project/token-sentences', status_code=200,
    response_model = List[schemas_nlp.Sentence],
    tags=['Autographa-Translation'])
def get_token_sentences(project_id:int=Query(...,example="1022004"),
    token:str=Query(...,example="duck"),
    occurrences:List[schemas_nlp.TokenOccurence]=Body(..., example=[
        {"sentenceId":41001001, "offset":[0,4]}]),
    db_:Session=Depends(get_db)):
    '''Pass in the occurence list of a token and get all sentences it is present in with draftMeta
    that allows easy highlight of token and translation'''
    log.info('In get_token_sentences')
    log.debug('project_id: %s, token:%s, occurrences:%s',project_id, token, occurrences)
    return projects_crud.get_agmt_source_per_token(db_, project_id, token, occurrences)

@router.get('/v2/autographa/project/draft', status_code=200, tags=['Autographa-Translation'])
def get_draft(project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    output_format:schemas_nlp.DraftFormats=Query(schemas_nlp.DraftFormats.USFM),
    db_:Session=Depends(get_db)):
    '''Obtains draft, as per current project status, in any of the formats:
    text for UI display, usfm for downloading, or alignment-json for project export'''
    log.info('In get_draft')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s,\
        output_format:%s',project_id, books, sentence_id_list, sentence_id_range,
        output_format)
    return projects_crud.obtain_agmt_draft(db_, project_id, books,
        sentence_id_list, sentence_id_range, output_format=output_format)

@router.get('/v2/autographa/project/sentences', status_code=200,
    response_model_exclude_unset=True,
    response_model=List[schemas_nlp.Sentence], tags=['Autographa-Translation'])
def get_project_source(project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    with_draft:bool=False, db_:Session=Depends(get_db)):
    '''Obtains source sentences or verses, as per the filters'''
    log.info('In get_source')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s, with_draft:%s',
        project_id, books, sentence_id_list, sentence_id_range, with_draft)
    return nlp_crud.obtain_agmt_source(db_, project_id, books, sentence_id_range, sentence_id_list,
        with_draft=with_draft)

@router.get('/v2/autographa/project/progress', status_code=200,
    response_model=schemas_nlp.Progress, tags=['Autographa-Translation'])
def get_progress(project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    db_:Session=Depends(get_db)):
    '''Obtains source sentences or verses, as per the filters'''
    log.info('In get_progress')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s',
        project_id, books, sentence_id_list, sentence_id_range)
    return projects_crud.obtain_agmt_progress(db_, project_id, books,
        sentence_id_list, sentence_id_range)

@router.get('/v2/autographa/project/versification', status_code=200,
    response_model=schemas.Versification, tags=['Autographa-Translation'])
def get_project_versification(project_id:int=Query(...,example="1022004"),
    db_:Session=Depends(get_db)):
    '''Obtains versification structure for source sentences or verses'''
    log.info('In get_project_versification')
    log.debug('project_id: %s', project_id)
    return projects_crud.get_agmt_source_versification(db_, project_id)

@router.put('/v2/autographa/project/suggestions', status_code=201,
    response_model=List[schemas_nlp.Sentence],
    tags=["Translation Suggestion"])
def suggest_auto_translation(project_id:int=Query(...,example="1022004"),
    books:List[schemas.BookCodePattern]=Query(None,example=["mat", "mrk"]),
    sentence_id_list:List[int]=Query(None,example=[41001001,41001002,41001003]),
    sentence_id_range:List[int]=Query(None,max_items=2,min_items=2,example=[41001001,41001999]),
    confirm_all:bool=False, db_:Session=Depends(get_db)):
    '''Try to fill draft with suggestions. If confirm_all is set, will only change status of all
    "suggestion" to "confirmed" in the selected sentences and will not fill in new suggestion'''
    log.info('In suggest_translation')
    log.debug('project_id: %s, books:%s, sentence_id_list:%s, sentence_id_range:%s',
        project_id, books, sentence_id_list, sentence_id_range)
    return nlp_crud.agmt_suggest_translations(db_, project_id, books,
        sentence_id_list=sentence_id_list, sentence_id_range=sentence_id_range,
        confirm_all=confirm_all)

########### Generic Translation ##################
@router.put('/v2/translation/tokens', response_model=List[schemas_nlp.Token],
    response_model_exclude_unset=True,
    status_code=200, tags=['Generic Translation'])
def tokenize(source_language:schemas.LangCodePattern=Query(...,example="hi"),
    sentence_list:List[schemas_nlp.SentenceInput]=Body(...),
    target_language:schemas.LangCodePattern=Query(None,example="ml"),
    use_translation_memory:bool=True, include_phrases:bool=True, include_stopwords:bool=False,
    punctuations:List[str]=Body(None), stopwords:schemas_nlp.Stopwords=Body(None),
    db_:Session=Depends(get_db)):
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

@router.put('/v2/translation/token-translate', response_model=schemas_nlp.TranslateResponse,
    status_code=200, tags=['Generic Translation'])
def token_replace(sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    token_translations:List[schemas_nlp.TokenUpdate]=Body(...),
    source_language:schemas.LangCodePattern=Query(...,example='hi'),
    target_language:schemas.LangCodePattern=Query(...,example='ml'),
    use_data_for_learning:bool=True, db_:Session=Depends(get_db)):
    '''Perform token replacement on provided sentences and
    returns obtained drafts and draft_meta'''
    log.info('In token_replace')
    log.debug('sentence_list:%s, token_translations:%s,\
        source_lanuage:%s, target_language:%s, use_data_for_learning:%s',
        sentence_list, token_translations, source_language, target_language, use_data_for_learning)
    result = nlp_crud.replace_bulk_tokens(db_, sentence_list, token_translations, source_language,
        target_language, use_data_for_learning=use_data_for_learning)
    return {"message": "Tokens replaced with translations", "data": result}

@router.put('/v2/translation/draft', status_code=200, tags=['Generic Translation'])
def generate_draft(sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    doc_type:schemas_nlp.TranslationDocumentType=Query(schemas_nlp.TranslationDocumentType.USFM)):
    '''Converts the drafts in input sentences to following output formats:
    usfm, text, csv or alignment-json'''
    log.info('In generate_draft')
    log.debug('sentence_list:%s, doc_type:%s',sentence_list, doc_type)
    return nlp_crud.obtain_draft(sentence_list, doc_type)

@router.put('/v2/translation/suggestions', response_model=List[schemas_nlp.Sentence],
    status_code=200, tags=["Translation Suggestion"])
def suggest_translation(source_language:schemas.LangCodePattern=Query(...,example="hi"),
    target_language:schemas.LangCodePattern=Query(...,example="ml"),
    sentence_list:List[schemas_nlp.DraftInput]=Body(...),
    punctuations:List[str]=Body(None), stopwords:schemas_nlp.Stopwords=Body(None),
    db_:Session=Depends(get_db)):
    '''Attempts to tokenize sentences and prepare draft with autogenerated suggestions
    If draft and draft_meta are provided indicating some portion of sentence is user translated,
    then it is left untouched.'''
    log.info("In suggest_translation")
    log.debug('source_language:%s, target_language:%s, sentence_list:%s,punctuations:%s\
        stopwords:%s', source_language, target_language, sentence_list, punctuations, stopwords)
    return nlp_crud.auto_translate(db_, sentence_list, source_language, target_language,
        punctuations=punctuations, stopwords=stopwords)

@router.get('/v2/translation/gloss', response_model=schemas_nlp.GlossOutput,
    status_code=200, tags=["Translation Suggestion"])
def get_glossary(source_language:schemas.LangCodePattern=Query(...,example="en"),
    target_language:schemas.LangCodePattern=Query(...,example="hi"),
    token:str=Query(...,example="duck"),
    context:str=Query(None,example="The duck swam in the lake"),
    token_offset:List[int]=Query(None,max_items=2,min_items=2,example=(4,8)),
    db_:Session=Depends(get_db)):
    '''Finds translation suggestions or gloss for one token in the given context'''
    log.info('In get_glossary')
    log.debug('source_language:%s, target_language:%s, token:%s, context:%s,\
        token_offset:%s',source_language, target_language, token,
            context, token_offset)
    return nlp_crud.glossary(db_, source_language, target_language, token,
    context=context, token_offset=token_offset)

@router.post('/v2/translation/learn/gloss', response_model=schemas_nlp.GlossUpdateResponse,
    status_code=201, tags=["Translation Suggestion"])
def add_gloss(source_language:schemas.LangCodePattern=Query(...,example='en'),
    target_language:schemas.LangCodePattern=Query(..., example="hi"),
    token_translations:List[schemas_nlp.GlossInput]=Body(...), db_:Session=Depends(get_db)):
    '''Load a list of predefined tokens and translations to improve tokenization and suggestion'''
    log.info('In add_gloss')
    log.debug('source_language:%s, target_language:%s, token_translations:%s',
        source_language, target_language, token_translations)
    tw_data = nlp_crud.add_to_translation_memory(db_,source_language, target_language,
        token_translations)
    return { "message": "Added to glossary", "data":tw_data }

@router.post('/v2/translation/learn/alignment', response_model=schemas_nlp.GlossUpdateResponse,
    status_code=201, tags=["Translation Suggestion"])
def add_alignments(source_language:schemas.LangCodePattern, target_language:schemas.LangCodePattern,
    alignments:List[schemas_nlp.Alignment], db_:Session=Depends(get_db)):
    '''Prepares training data with alignments and update translation memory & suggestion models'''
    log.info('In add_alignments')
    log.debug('source_language:%s, target_language:%s, alignments:%s',
        source_language, target_language, alignments)
    tw_data = nlp_crud.alignments_to_trainingdata(db_,src_lang=source_language,
    trg_lang=target_language, alignment_list=alignments, user_id=20202)
    return { "message": "Alignments used for learning", "data":tw_data }
