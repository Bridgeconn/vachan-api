''' Place to define all data processing and Database CRUD operations related
    to stop word identification'''

from sqlalchemy.orm import Session
from sqlalchemy import func
from custom_exceptions import NotAvailableException

import db_models

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
    query = query.offset(skip).limit(limit).all()
    result = []
    for row in query:
        sw_type = ''
        if row.confidence == 2:
            sw_type = 'System defined'
        elif row.confidence == 1:
            sw_type = 'User defined'
        else:
            sw_type = 'Auto generated'
        conf_val = None
        if row.confidence not in [1, 2]:
            conf_val = row.confidence
        result.append({"stopword": row.stopWord, "stopwordType": sw_type, "confidence": conf_val,
        "active": row.active})
    return result
