''' Place to define all data processing and Database CRUD operations related
    to stop word identification'''
import re
import operator
from datetime import datetime
from nltk import FreqDist
from kneed import KneeLocator
from sqlalchemy.orm import Session
from sqlalchemy import func, update
from fastapi import Request
from custom_exceptions import NotAvailableException

import db_models
from schema import schemas_nlp
from crud import utils
from routers import content_apis


#Based on sqlalchemy
#pylint: disable=W0102,E1101,W0143

###################### Stop words identification ######################

def retrieve_stopwords(db_: Session, language_code, **kwargs):
    '''retreives stopwords of a given language from look up table'''
    include_system_defined = kwargs.get("include_system_defined", True)
    include_user_defined = kwargs.get("include_user_defined", True)
    include_auto_generated = kwargs.get("include_auto_generated", True)
    only_active = kwargs.get("only_active", True)
    skip = kwargs.get("skip", 0)
    limit = kwargs.get("limit", 100)
    query = db_.query(db_models.Language.languageId)
    language_id = query.filter(func.lower(db_models.Language.code) == language_code.lower()).first()
    if not language_id:
        raise NotAvailableException("Language with code %s, not in database"%language_code)
    query = db_.query(db_models.StopWords)
    query = query.filter(db_models.StopWords.languageId == language_id[0])
    if not include_system_defined:
        query = query.filter(db_models.StopWords.confidence != 2)
    if not include_user_defined:
        query = query.filter(db_models.StopWords.confidence != 1)
    if not include_auto_generated:
        query = query.filter(db_models.StopWords.confidence >= 1)
    if only_active:
        query = query.filter(db_models.StopWords.active == only_active)
    query_result = query.offset(skip).limit(limit).all()
    result = []
    for row in query_result:
        result.append({"stopWord": row.stopWord, "confidence": row.confidence, "active": row.active,
            "metaData": row.metaData})
    return result

def update_stopword_info(db_: Session, language_code, sw_json):
    '''updates the given information of a stopword in db'''
    data = {}
    query = db_.query(db_models.Language.languageId)
    language_id = query.filter(func.lower(db_models.Language.code) == language_code.lower()).first()
    if not language_id:
        raise NotAvailableException("Language with code %s, not in database"%language_code)
    language_id = language_id[0]
    stopword = sw_json.stopWord
    value_dic = {}
    if sw_json.active is not None:
        value_dic["active"] = sw_json.active
    if sw_json.metaData is not None:
        value_dic["metaData"] = sw_json.metaData
    update_stmt = (update(db_models.StopWords).where(db_models.StopWords.stopWord == stopword,
        db_models.StopWords.languageId == language_id).values(value_dic))
    result = db_.execute(update_stmt)
    db_.commit()
    if result.rowcount == 0:
        raise NotAvailableException("Language with code %s, does not have stopword %s \
            in database"%(language_code,stopword))
    query = db_.query(db_models.StopWords)
    row = query.filter(db_models.StopWords.stopWord == stopword,
            db_models.StopWords.languageId == language_id).first()
    data = {"stopWord": row.stopWord, "confidence": row.confidence, "active": row.active,
            "metaData": row.metaData}
    return data

def add_stopwords(db_: Session, language_code, stopwords_list, user_id=None):
    '''insert given stopwords into look up table for a given language'''
    language_id = db_.query(db_models.Language.languageId).filter(
        func.lower(db_models.Language.code) == language_code.lower()).first()
    language_id = language_id[0]
    if not language_id:
        raise NotAvailableException("Language with code %s, not in database"%language_code)
    db_content = []
    for word in stopwords_list:
        word = utils.normalize_unicode(word)
        args = {"languageId":language_id,
                "stopWord": word,
                "confidence": 1,
                "active": True,
                "createdUser": user_id}
        sw_row = db_.query(db_models.StopWords).filter(
                            db_models.StopWords.languageId == language_id,
                            db_models.StopWords.stopWord == word).first()
        if sw_row:
            if sw_row.confidence == 2:
                continue
            if sw_row.confidence < 1:
                update_args = {"confidence": 1,
                                "active" : True,
                                "updatedUser": user_id
                              }
                update_stmt = (update(db_models.StopWords).where(db_models.StopWords.stopWord ==
                        word, db_models.StopWords.languageId == language_id).values(update_args))
                result = db_.execute(update_stmt)
                if result.rowcount == 1:
                    row = db_.query(db_models.StopWords).filter(db_models.StopWords.stopWord ==
                        word, db_models.StopWords.languageId == language_id).first()
                    db_content.append({"stopWord": row.stopWord, "confidence": row.confidence,
                     "active": row.active, "metaData": row.metaData})
        else:
            new_sw_row = db_models.StopWords(**args)
            db_.add(new_sw_row)
            db_content.append({"stopWord": new_sw_row.stopWord, "confidence": new_sw_row.confidence,
            "active": new_sw_row.active, "metaData": new_sw_row.metaData})
    db_.commit()
    msg = f"{len(db_content)} stopwords added successfully"
    return msg, db_content

def clean_text(text):
    '''Cleaning text by removing punctuations, extra spaces'''
    punctuations = utils.punctuations()
    text = re.sub(r'['+"".join(punctuations)+']', '', text)
    text = re.sub(r'\n|\s\s+', ' ', text)
    return text.lower().strip()

async def get_data(db_, request, language_code, sentence_list, **kwargs):
    '''Collecting data for stopword generation'''
    sentences = []
    if sentence_list:
        sentences += [item.sentence for item in sentence_list]
    use_server_data = kwargs.get("use_server_data")
    if use_server_data:
        server_data = await content_apis.extract_text_contents(
            request=request, #pylint: disable=W0613
            source_name=None,
            books=None,
            language_code=language_code,
            content_type=None,
            skip=0, limit=100000,
            user_details=kwargs.get('user_details'),
            db_=db_)
        if server_data:
            if "error" not in server_data:
                sentences += [item[2] for item in server_data]
    return sentences

def find_knee(sentences):
    '''Finding most frequent words from a list of words using kneed package'''
    data = clean_text(' '.join(sentences))
    fdist = FreqDist(data.split())
    fdist_dict = dict(sorted(dict(fdist).items(), key=operator.itemgetter(1),reverse=True))
    token_indices = list(range(len(fdist_dict)))
    kneedle = KneeLocator(token_indices, list(fdist_dict.values()), curve='convex',
                    direction='decreasing')
    stop_words = list(fdist_dict.keys())[:kneedle.knee]
    sw_scored = []
    frq_sum = sum(list(fdist_dict.values())[:kneedle.knee])
    for word in stop_words:
        score = (fdist_dict[word])/frq_sum
        sw_scored.append((word, score))
    return sw_scored

async def filter_translation_words(db_, request, gl_lang_code, stopwords, user_details=None):
    '''Filter the translation words from generated stopwords using tws of gl'''
    tw_lookup = {'hi': 'hi_TW_1_dictionary', 'ml': 'ml_TW_1_dictionary', 'te':
        'te_TW_1_dictionary', 'kan': 'kan_TW_1_dictionary', 'ta': 'ta_TW_1_dictionary',
        'mr': 'mr_TW_1_dictionary', 'pa': 'pa_TW_1_dictionary', 'as': 'as_TW_1_dictionary',
        'gu': 'gu_TW_1_dictionary', 'ur': 'ur_TW_1_dictionary', 'or': 'or_TW_1_dictionary',
        'bn': 'bn_TW_1_dictionary'}
    query = db_.query(db_models.Language.languageId)
    gl_id = query.filter(func.lower(db_models.Language.code) == gl_lang_code.lower()).first()
    if not gl_id:
        raise NotAvailableException("Gateway Language with code %s, not in database. "
                %gl_lang_code)
    gl_id = gl_id[0]
    source_name = tw_lookup[gl_lang_code]
    response = await content_apis.get_dictionary_word(
        request=request, #pylint: disable=W0613
        source_name=source_name,
        search_word =None,
        details=None,
        active=True,
        skip=0, limit=100000,
        user_details=user_details,
        db_=db_)
    if response:
        translation_words = [row.word for row in response['db_content']]
        translation_words = [item.strip() for item in translation_words if item.strip()!='']
        stopwords = [item for item in stopwords if item[0] not in translation_words]
    return stopwords

def add_generated_sws(db_, language_id, stopwords, user_id):
    '''Inserting automatically generated stopwords into db'''
    for item in stopwords:
        word = utils.normalize_unicode(item[0])
        args = {"languageId":language_id,
                "stopWord": word,
                "confidence": item[1],
                "createdUser": user_id}
        sw_row = db_.query(db_models.StopWords).filter(
                            db_models.StopWords.languageId == language_id,
                            db_models.StopWords.stopWord == word).first()
        if sw_row:
            if sw_row.confidence < item[1]:
                update_args = {"confidence": item[1],
                                "updatedUser": user_id
                              }
                update_stmt = (update(db_models.StopWords).where(db_models.StopWords.stopWord ==
                        word, db_models.StopWords.languageId == language_id).values(update_args))
                db_.execute(update_stmt)
        else:
            new_sw_row = db_models.StopWords(**args)
            db_.add(new_sw_row)
    db_.commit()

async def extract_stopwords(db_, request, language_id, language_code, gl_lang_code, *args):
    '''Extract stopwords from available data and stores in db'''
    user_details = args[0]
    sentences = args[1]
    msg = ''
    result = []
    stopwords = find_knee(sentences)
    if gl_lang_code is None:
        msg = "Stopwords identified out of limited resources. Manual verification recommended"
    else:
        stopwords = await filter_translation_words(db_, request, gl_lang_code, stopwords,
            user_details)
    result = []
    if stopwords:
        add_generated_sws(db_, language_id, stopwords, user_details['user_id'])
        for item in stopwords:
            result.append({"stopWord": item[0], "confidence": item[1], "active": True,
                "metaData": None})
        if msg == '':
            msg = "Automatically generated stopwords for the given language"
    update_args = {
                    "status" : schemas_nlp.JobStatus.FINISHED.value,
                    "endTime": datetime.now(),
                    "output": {"message": msg, "language": language_code,"data": result}
                  }
    return update_args

def create_job(db_, user_id):
    '''Creates a new job in db table Jobs'''
    db_content = db_models.Jobs(
        userId=user_id,
        status=schemas_nlp.JobStatus.CREATED.value
        )
    db_.add(db_content)
    db_.commit()
    return db_content

def update_job(db_, job_id, user_id, update_args):
    '''Updates the fields of an already existing job in db'''
    # job_entry = (update(db_models.Jobs).where(db_models.Jobs.jobId == job_id,
    #     db_models.Jobs.userId == user_id).values(update_args))
    query = db_.query(db_models.Jobs)
    job_entry = query.filter(db_models.Jobs.jobId == job_id).first()
    job_entry.status = update_args['status']
    if "output" in update_args:
        job_entry.output = update_args['output']
    if "endTime" in update_args:
        job_entry.endTime = update_args['endTime']
    # db_.add(job_entry)
    db_.commit()


async def generate_stopwords(db_: Session, request: Request, *args, user_details=None,  **kwargs):
    '''Automatically generate stopwords for given language'''
    msg = ''
    language_code = args[0]
    gl_lang_code = args[1]
    sentence_list = args[2]
    job_id = args[3]
    user_id = None
    if user_details is not None:
        user_id = user_details['user_id']
    update_args = {
                    "status" : schemas_nlp.JobStatus.STARTED.value,
                    "startTime": datetime.now()
                   }
    update_job(db_, job_id, user_id, update_args)
    language_id = db_.query(db_models.Language.languageId).filter(func.lower(
                            db_models.Language.code) == language_code.lower()).first()
    if not language_id:
        update_args = {
                    "status" : schemas_nlp.JobStatus.ERROR.value,
                    "endTime": datetime.now(),
                    "output": {"message": "Language with code %s, not in database"%language_code,
                     "language": language_code,"data": None}
                    }
        update_job(db_, job_id, user_id, update_args)
        raise NotAvailableException("Language with code %s, not in database"%language_code)
    language_id = language_id[0]
    kwargs['user_details'] = user_details
    sentences = await get_data(db_, request, language_code, sentence_list, **kwargs)
    if len(sentences) < 1000:
        # raise UnprocessableException("Not enough data to generate stopwords")
        msg = "Not enough data to generate stopwords"
        update_args = {
                        "status" : schemas_nlp.JobStatus.FINISHED.value,
                        "endTime": datetime.now(),
                        "output": {"message": msg, "language": language_code,"data": None}
                      }
    else:
        update_args = {
                        "status" : schemas_nlp.JobStatus.IN_PROGRESS.value,
                        "output": {"message": '', "language": language_code,"data": None}
                      }
        update_job(db_, job_id, user_id, update_args)
        update_args = await extract_stopwords(db_, request, language_id, language_code,
                                 gl_lang_code, user_details, sentences)
    update_job(db_, job_id, user_id, update_args)
    query = db_.query(db_models.Jobs)
    query_result = query.filter(db_models.Jobs.jobId == job_id).first()


def check_job_status(db_: Session, job_id):
    '''Checking job status'''
    query = db_.query(db_models.Jobs)
    query_result = query.filter(db_models.Jobs.jobId == job_id).first()
    msg = ''
    if query_result.status == schemas_nlp.JobStatus.CREATED.value:
        msg = "Job is created, not started yet"
    elif query_result.status in [schemas_nlp.JobStatus.IN_PROGRESS.value,
                                schemas_nlp.JobStatus.PENDING.value]:
        msg = "Job is in progress, check status after some time!"
    elif  query_result.status == schemas_nlp.JobStatus.ERROR.value:
        msg = "Job is terminated with an error"
    result = []
    if query_result.status == schemas_nlp.JobStatus.FINISHED.value:
        msg = query_result.output['message']
        del query_result.output['message']
        result =  {'message': msg, 'data': {'jobId':job_id, 'status': query_result.status,
                 'output': query_result.output}}
    else:
        result =  {'message': msg, 'data': {'jobId':job_id, 'status': query_result.status,
                   'output': None}}
    return result
    