''' Place to define all data processing and Database CRUD operations related
    to stop word identification'''

from sqlalchemy.orm import Session
from sqlalchemy import func, update
from custom_exceptions import NotAvailableException

import db_models
from crud import utils

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
    print("user_id", user_id)
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