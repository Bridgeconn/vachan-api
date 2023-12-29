''' Place to define all Database CRUD operations for content tables
bible, commentary, parascriptural, vocabulary ,sign bible video etc'''
#pylint: disable=too-many-lines,line-too-long
import json
import re
from datetime import datetime
from pytz import timezone
from sqlalchemy import or_
from sqlalchemy.orm import Session, defer, joinedload
from sqlalchemy.sql import text
from usfm_grammar import USFMParser,Filter
import db_models #pylint: disable=import-error
from crud import utils  #pylint: disable=import-error
from crud.nlp_sw_crud import update_job #pylint: disable=import-error
from schema import schemas_nlp #pylint: disable=import-error
from custom_exceptions import NotAvailableException, TypeException, AlreadyExistsException,\
    UnprocessableException  #pylint: disable=import-error

ist_timezone = timezone("Asia/Kolkata")

def get_commentaries(db_: Session,**kwargs):#pylint: disable=too-many-locals
    '''Fetches rows of commentries from the table specified by resource_name'''
    resource_name = kwargs.get("resource_name")
    reference = kwargs.get("reference",None)
    commentary_id = kwargs.get("commentary_id",None)
    search_word = kwargs.get("search_word",None)
    commentary = kwargs.get("commentary",None)
    section_type = kwargs.get("section_type",None)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith(db_models.ResourceTypeName.COMMENTARY.value):
        raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[resource_name]
    query = db_.query(model_cls)
    if commentary_id is not None:
        query = query.filter(model_cls.commentaryId == commentary_id)
    if commentary:
        query = query.filter(model_cls.commentary.contains(\
            utils.normalize_unicode(commentary.strip())))
    if section_type:
        filter_conditions = [model_cls.sectionType.contains([item]) for item in section_type]
        filter_condition = or_(*filter_conditions)
        query = query.filter(filter_condition)
    if reference:
        if isinstance(reference, str):
            reference = json.loads(reference)
        query = filter_by_reference(db_,query, model_cls, reference)
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', commentary || ' ' ||"+\
            "jsonb_to_tsvector('simple', reference, '[\"string\", \"numeric\"]') || ' ')" +\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))

    query = query.filter(model_cls.active == active)
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':query.offset(skip).limit(limit).all(),
        'resource_content':resource_db_content}
    return response

def process_reference(db_:Session,item): #pylint: disable=too-many-branches
    '''Calculate refstart and refend ids for a given reference'''
    if item.reference:
        ref = item.reference.__dict__
        if ref['book'] is not None:
            if ref['chapter'] is not None:
                if ref['verseNumber'] is not None:
                    ref_start = utils.create_decimal_ref_id(
                        db_, ref['book'], ref['chapter'], ref['verseNumber'])
                else:
                    # Setting verseNumber to 000 if it's not present - chapter intro
                    ref_start = utils.create_decimal_ref_id(db_, ref['book'], ref['chapter'], 0)
                    ref['verseNumber'] = 0
            else:
                # Setting chapter and verseNumber to 000 if it's both are not present - book intro
                ref_start = utils.create_decimal_ref_id(
                    db_, ref['book'], ref['chapter'], ref['verseNumber'])

        if ref['bookEnd'] is not None:
            if ref['chapter'] is not None:
                if ref['verseEnd'] is not None:
                    ref_end = utils.create_decimal_ref_id(
                        db_, ref['bookEnd'], ref['chapterEnd'], ref['verseEnd'])
                else:
                    # Setting verseEnd to 999 if it's not present
                    ref_end =utils.create_decimal_ref_id(db_, ref['bookEnd'], ref['chapterEnd'],999)
                    ref['verseEnd'] = 999
            else:
                # Setting chapterEnd and verseEnd to 999 if it's both are not present - epilogue
                if ref['verseEnd'] is None:
                    ref_start = utils.create_decimal_ref_id(
                        db_, ref['book'], 999, 999)
                else:
                    raise UnprocessableException("verse will not exist without chapter")
        else:
            ref_end = ref_start
    else:
        ref = None
        ref_end = None
        ref_start = None
    return ref, ref_start, ref_end

def upload_commentaries(db_: Session, resource_name, commentaries, job_id, user_id=None):#pylint: disable=too-many-locals,R1710
    '''Adds rows to the commentary table specified by resource_name'''
    update_args = {
                    "status" : schemas_nlp.JobStatus.STARTED.value,
                    "startTime": datetime.now()}
    update_job(db_, job_id, user_id, update_args)

    update_args = {
                    "status" : schemas_nlp.JobStatus.ERROR.value,
                    "endTime": datetime.now(),
                    "output": {}}

    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if resource_db_content.resourceType.resourceType != db_models.ResourceTypeName.COMMENTARY.value:
        update_args["output"]= {
                "message": 'The operation is supported only on commentaries',
                "resource_name": resource_name,"data": None}
        update_job(db_, job_id, user_id, update_args)
        return None
        # raise TypeException('The operation is supported only on commentaries')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    db_content_out = []
    for item in commentaries:
        #getting reference and its ids
        ref,ref_start,ref_end = process_reference( db_,item)

        query = db_.query(model_cls)
        for row in query.all():
            exist_check = query.filter(model_cls.refStart == ref_start, \
                model_cls.refEnd == ref_end).first()
            if exist_check:
                update_args["output"]= {
                "message": 'Already exist commentary with same values for reference range',
                "data": None}
                update_job(db_, job_id, user_id, update_args)
                return None

        row = model_cls(
            reference = ref,
            refStart=ref_start,
            refEnd=ref_end,
            commentary = utils.normalize_unicode(item.commentary),
            sectionType = item.sectionType,
            active=item.active)
        row_out = {
            "reference" : ref,
            "commentary" :  utils.normalize_unicode(item.commentary),
            "sectionType" : item.sectionType,
            "active": item.active}
        db_content.append(row)
        db_content_out.append(row_out)
    db_.add_all(db_content)
    db_.expire_all()
    resource_db_content.updatedUser = user_id
    update_args = {
        "status" : schemas_nlp.JobStatus.FINISHED.value,
        "endTime": datetime.now(),
        "output": {"message": "Commentaries added successfully","data": db_content_out}}
    update_job(db_, job_id, user_id, update_args)

def update_commentaries(db_: Session, resource_name, commentaries,job_id, user_id=None):#pylint: disable=R1710,too-many-locals
    '''Update rows, that matches book, chapter and verse range fields in the commentary table
    specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    update_args = {"status" : schemas_nlp.JobStatus.STARTED.value,
                    "startTime": datetime.now()}
    update_job(db_, job_id, user_id, update_args)
    update_args = {"status" : schemas_nlp.JobStatus.ERROR.value,
                    "endTime": datetime.now(),"output": {}}
    if resource_db_content.resourceType.resourceType != db_models.ResourceTypeName.COMMENTARY.value:
        update_args["output"]= {"message": 'The operation is supported only on commentaries',
                "resource_name": resource_name,"data": None}
        update_job(db_, job_id, user_id, update_args)
        return None
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    db_content_out = []
    model_cls = db_models.dynamicTables[resource_name]
    query = db_.query(model_cls)
    for item in commentaries:
        row = query.filter(model_cls.commentaryId == item.commentaryId).first()
        if not row:
            update_args["output"]= {
            "message": 'Commentary with given id does not exist',
            "data": None}
            update_job(db_, job_id, user_id, update_args)
            return None
        if item.reference:
            ref = item.reference.__dict__
            if ref['verseNumber'] is not None:
                ref_start = utils.create_decimal_ref_id(
                    db_,ref['book'],ref['chapter'],ref['verseNumber'])
            else:
                ref_start = utils.create_decimal_ref_id(db_,ref['book'],ref['chapter'],0)
            if ref['verseEnd'] is not None:
                ref_end   = utils.create_decimal_ref_id(
                    db_,ref['bookEnd'],ref['chapterEnd'],ref['verseEnd'])
            else:
                ref_end   = utils.create_decimal_ref_id(db_,ref['bookEnd'],ref['chapterEnd'],999)
            row.reference = ref
            row.refStart=ref_start
            row.refEnd=ref_end
        if item.commentary:
            row.commentary = utils.normalize_unicode(item.commentary)
        if item.sectionType:
            row.sectionType = item.sectionType
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
        row_out = {
            "reference" : row.reference,
            "sectionType":row.sectionType,
            "commentary" :  utils.normalize_unicode(row.commentary),
            "active": row.active}
        db_content_out.append(row_out)
    resource_db_content.updatedUser = user_id
    update_args = {
        "status" : schemas_nlp.JobStatus.FINISHED.value,
        "endTime": datetime.now(),
        "output": {"message": "Commentaries updated successfully","data": db_content_out}}
    update_job(db_, job_id, user_id, update_args)

# pylint: disable=duplicate-code
def delete_commentary(db_: Session, delitem:int,table_name=None,
    resource_name=None,user_id=None):
    '''delete particular commentary, selected via resource id'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    model_cls = table_name
    query = db_.query(model_cls)
    db_content = query.filter(model_cls.commentaryId == delitem).first()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    db_.delete(db_content)
    return response
# pylint: enable=duplicate-code

def get_vocabulary_words(db_:Session,**kwargs):#pylint: disable=too-many-locals
    '''Fetches rows of vocabulary from the table specified by resource_name'''
    resource_name=kwargs.get("resource_name")
    search_word=kwargs.get("search_word",None)
    word_id=kwargs.get("word_id",None)
    details = kwargs.get("details",None)
    exact_match = kwargs.get("exact_match",False)
    word_list_only = kwargs.get("word_list_only",False)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith(db_models.ResourceTypeName.VOCABULARY.value):
        raise TypeException('The operation is supported only on vocabularies')
    model_cls = db_models.dynamicTables[resource_name]
    if word_list_only:
        query = db_.query(model_cls.word)
    else:
        query = db_.query(model_cls)
    if word_id:
        query = query.filter(model_cls.wordId == word_id)
        # return query.offset(skip).limit(limit).all()
    if search_word and exact_match:
        query = query.filter(model_cls.word == utils.normalize_unicode(search_word))
    elif search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', word || ' ' ||"+\
            "jsonb_to_tsvector('simple', details, '[\"string\", \"numeric\"]') || ' ')"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))
    if details:
        det = json.loads(details)
        for key in det:
            query = query.filter(model_cls.details.op('->>')(key) == det[key])
    if active is not None:
        query = query.filter(model_cls.active == active)
    if skip is not None:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    res = query.all()
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':res,
        'resource_content':resource_db_content }
    return response

def upload_vocabulary_words(db_: Session, resource_name, vocabulary_words, user_id=None):
    '''Adds rows to the vocabulary table specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != db_models.ResourceTypeName.VOCABULARY.value:
        raise TypeException('The operation is supported only on vocabularies')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in vocabulary_words:
        row = model_cls(
            word = utils.normalize_unicode(item.word),
            details = item.details,
            active = item.active)
        db_content.append(row)
    db_.add_all(db_content)
    db_.expire_all()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def update_vocabulary_words(db_: Session, resource_name, vocabulary_words, user_id=None):
    '''Update rows, that matches the word field in the vocabulary table specified by
      resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != db_models.ResourceTypeName.VOCABULARY.value:
        raise TypeException('The operation is supported only on vocabularies')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in vocabulary_words:
        row = db_.query(model_cls).filter(model_cls.word == item.word).first()
        if not row:
            raise NotAvailableException(f"Vocabulary row with word:{item.word},"+\
                f"not found for {resource_name}")
        if item.details:
            row.details = item.details
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def delete_vocabulary(db_: Session, delitem : int,table_name = None,
    resource_name=None,user_id=None):
    '''delete particular word from vocabulary, selected via resourcename and word id'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    model_cls = table_name
    query = db_.query(model_cls)
    db_content = query.filter(model_cls.wordId == delitem).first()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    db_.delete(db_content)
    return response

def filter_by_reference(db_:Session,query, model_cls, reference):
    '''check reference is present in the given ranges of refStart and refEnd'''

    reference_end = ['bookEnd', 'chapterEnd', 'verseEnd']
    if any(item in reference for item in reference_end):
        # search for cross-chapter references and mutliple verses within chapter
        ref_start_id = utils.create_decimal_ref_id(
            db_,reference['book'], reference['chapter'], reference['verseNumber'])
        ref_end_id   = utils.create_decimal_ref_id(
            db_,reference['bookEnd'], reference['chapterEnd'], reference['verseEnd'])
        query = query.filter(model_cls.refStart <= ref_start_id, model_cls.refEnd >= ref_end_id)
    else:
        # search for a single verse
        ref_id = utils.create_decimal_ref_id(
            db_,reference['book'], reference['chapter'], reference['verseNumber'])
        query = query.filter(model_cls.refStart <= ref_id, model_cls.refEnd >= ref_id)
    return query

def get_parascripturals(db_:Session, resource_name, category=None, title=None,**kwargs): #pylint: disable=too-many-locals
    '''Fetches rows of parascripturals from the table specified by resource_name'''
    description = kwargs.get("description",None)
    content = kwargs.get("content",None)
    search_word = kwargs.get("search_word",None)
    reference = kwargs.get("reference",None)
    link = kwargs.get("link",None)
    metadata = kwargs.get("metadata",None)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    parascript_id=kwargs.get("parascript_id",None)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith(db_models.ResourceTypeName.PARASCRIPTURAL.value):
        raise TypeException('The operation is supported only on parascripturals')
    model_cls = db_models.dynamicTables[resource_name]
    query = db_.query(model_cls)
    if category:
        query = query.filter(model_cls.category == category)
    if title:
        query = query.filter(model_cls.title == utils.normalize_unicode(title.strip()))
    if  description:
        query = query.filter(model_cls.description.contains(
            utils.normalize_unicode(description.strip())))
    if content:
        query = query.filter(model_cls.content.contains(utils.normalize_unicode(content.strip())))
    if link:
        query = query.filter(model_cls.link == link)
    if parascript_id:
        query = query.filter(model_cls.parascriptId == parascript_id)
    if reference:
        query = filter_by_reference(db_,query, model_cls, reference)
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            key_match = db_models.Parascriptural.metaData.op('->>')(key).ilike(f'%{key}%')
            value_match = db_models.Parascriptural.metaData.op('->>')(key).ilike(f'%{meta[key]}%')
            query = query.filter(key_match | value_match)
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text("to_tsvector('simple', category || ' ' ||"+\
            " title || ' ' || "+\
            " content || ' ' || "+\
            " description || ' ' || "+\
            " link || ' ' || "+\
            "jsonb_to_tsvector('simple', reference, '[\"string\", \"numeric\"]') || ' ' || " +
            "jsonb_to_tsvector('simple', metadata, '[\"string\", \"numeric\"]') || ' ')"+\
            " @@ to_tsquery('simple', :pattern)").bindparams(pattern=search_pattern))

    query = query.filter(model_cls.active == active)
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':query.offset(skip).limit(limit).all(),
        'resource_content':resource_db_content
        }
    return response

def upload_parascripturals(db_: Session, resource_name, parascriptural, user_id=None):#pylint: disable=too-many-branches
    '''Adds rows to the parascripturals table specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != \
        db_models.ResourceTypeName.PARASCRIPTURAL.value:
        raise TypeException('The operation is supported only on parascripturals')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in parascriptural:
        #getting reference and its ids
        ref,ref_start,ref_end = process_reference( db_,item)
        if item.content:
            item.content = utils.normalize_unicode(item.content.strip())
        if item.description:
            item.description = utils.normalize_unicode(item.description.strip())
        row = model_cls(
            category = item.category,
            title = utils.normalize_unicode(item.title.strip()),
            description = item.description,
            content =item.content,
            reference = ref,
            refStart=ref_start,
            refEnd=ref_end,
            link = item.link,
            metaData = item.metaData,
            active = item.active,
            createdUser =  user_id)
        db_content.append(row)
    db_.add_all(db_content)
    db_.expire_all()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def update_parascripturals(db_: Session, resource_name, parascripturals, user_id=None):#pylint: disable=too-many-branches
    '''Update rows, that matches type, and title in the parascriptural table
    specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != \
        db_models.ResourceTypeName.PARASCRIPTURAL.value:
        raise TypeException('The operation is supported only on parascripturals')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in parascripturals:
        row = db_.query(model_cls).filter(
            model_cls.category == item.category,
            model_cls.title == utils.normalize_unicode(item.title.strip())).first()
        if not row:
            raise NotAvailableException(f"Parascripturals row with type:{item.category}, "+\
                f"title:{item.title}, "+\
                f"not found for {resource_name}")
        if item.description:
            item.description = utils.normalize_unicode(item.description.strip())
            row.description = item.description
        if item.content:
            row.content = utils.normalize_unicode(item.content.strip())
        if item.link:
            row.link = item.link
        if item.reference:
            ref = item.reference.__dict__
            if ref['verseNumber'] is not None:
                ref_start = utils.create_decimal_ref_id(
                    db_,ref['book'],ref['chapter'],ref['verseNumber'])
            else:
                ref_start = utils.create_decimal_ref_id(db_,ref['book'],ref['chapter'],0)
            if ref['verseEnd'] is not None:
                ref_end   = utils.create_decimal_ref_id(
                    db_,ref['bookEnd'],ref['chapterEnd'],ref['verseEnd'])
            else:
                ref_end   = utils.create_decimal_ref_id(db_,ref['bookEnd'],ref['chapterEnd'],999)
            row.reference = ref
            row.refStart=ref_start
            row.refEnd=ref_end
        if item.metaData:
            row.metaData = item.metaData
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    resource_db_content.updatedUser = user_id
    resource_db_content.updateTime = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def delete_parascriptural(db_: Session, delitem: int,table_name = None,\
    resource_name=None,user_id=None):
    '''delete particular item from parascriptural, selected via resourceName and parascript id'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    model_cls = table_name
    query = db_.query(model_cls)
    db_content = query.filter(model_cls.parascriptId == delitem).first()
    db_.flush()
    db_.delete(db_content)
    #db_.commit()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def get_audio_bible(db_:Session, resource_name, name=None,**kwargs): #pylint: disable=too-many-locals
    '''Fetches rows of audio bibles from the table specified by resource_name'''
    audio_format = kwargs.get("audio_format",None)
    search_word = kwargs.get("search_word",None)
    reference = kwargs.get("reference",None)
    link = kwargs.get("link",None)
    metadata = kwargs.get("metadata",None)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    audio_id=kwargs.get("audio_id",None)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith(db_models.ResourceTypeName.AUDIOBIBLE.value):
        raise TypeException('The operation is supported only on audio bibles')
    model_cls = db_models.dynamicTables[resource_name]
    query = db_.query(model_cls)
    if name:
        query = query.filter(model_cls.name == utils.normalize_unicode(name.strip()))
    if  audio_format:
        query = query.filter(model_cls.audioFormat.contains(
            utils.normalize_unicode(audio_format.strip())))
    if link:
        query = query.filter(model_cls.link == link)
    if audio_id:
        query = query.filter(model_cls.audioId == audio_id)
    if reference:
        query = filter_by_reference(db_,query, model_cls, reference)
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            key_match = db_models.AudioBible.metaData.op('->>')(key).ilike(f'%{key}%')
            value_match = db_models.AudioBible.metaData.op('->>')(key).ilike(f'%{meta[key]}%')
            query = query.filter(key_match | value_match)
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text(
            "to_tsvector('simple', name || ' ' || audio_id || " +
            "' ' || audio_format || ' ' || link || ' ' || " +
            "jsonb_to_tsvector('simple', reference, '[\"string\", \"numeric\"]') || ' ' || " +
            "jsonb_to_tsvector('simple', metadata, '[\"string\", \"numeric\"]') " +
            ") @@ to_tsquery('simple', :pattern)"
        ).bindparams(pattern=search_pattern))

    query = query.filter(model_cls.active == active)
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':query.offset(skip).limit(limit).all(),
        'resource_content':resource_db_content
        }
    return response

def upload_audio_bible(db_: Session, resource_name, audiobibles, user_id=None):#pylint: disable=too-many-branches
    '''Adds rows to the audio bibles table specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != \
        db_models.ResourceTypeName.AUDIOBIBLE.value:
        raise TypeException('The operation is supported only on audio bibles')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in audiobibles:
        #getting reference and its ids
        ref,ref_start,ref_end = process_reference( db_,item)
        if item.name:
            item.name = utils.normalize_unicode(item.name.strip())
        if item.audioFormat:
            item.audioFormat = utils.normalize_unicode(item.audioFormat.strip())
        row = model_cls(
            name = item.name,
            audioFormat =item.audioFormat,
            reference = ref,
            refStart=ref_start,
            refEnd=ref_end,
            link = item.link,
            metaData = item.metaData,
            active = item.active,
            createdUser =  user_id)
        db_content.append(row)
    db_.add_all(db_content)
    db_.expire_all()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def update_audio_bible(db_: Session, resource_name, audiobibles, user_id=None): #pylint: disable=too-many-branches
    '''Update rows, that matches audioId in the audio bibles table
    specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != \
        db_models.ResourceTypeName.AUDIOBIBLE.value:
        raise TypeException('The operation is supported only on audio bibles')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in audiobibles:
        row = db_.query(model_cls).filter(
            model_cls.audioId == item.audioId).first()
        if not row:
            raise NotAvailableException(f"AUdio Bible row with id:{item.audioId}, "+\
                f"not found for {resource_name}")
        if item.name:
            item.name = utils.normalize_unicode(item.name.strip())
            row.name = item.name
        if item.audioFormat:
            item.audioFormat = utils.normalize_unicode(item.audioFormat.strip())
            row.audioFormat = item.audioFormat
        if item.link:
            row.link = item.link
        if item.reference:
            ref = item.reference.__dict__
            if ref['verseNumber'] is not None:
                ref_start = utils.create_decimal_ref_id(
                    db_,ref['book'],ref['chapter'],ref['verseNumber'])
            else:
                ref_start = utils.create_decimal_ref_id(db_,ref['book'],ref['chapter'],0)
            if ref['verseEnd'] is not None:
                ref_end   = utils.create_decimal_ref_id(
                    db_,ref['bookEnd'],ref['chapterEnd'],ref['verseEnd'])
            else:
                ref_end   = utils.create_decimal_ref_id(db_,ref['bookEnd'],ref['chapterEnd'],999)
            row.reference = ref
            row.refStart=ref_start
            row.refEnd=ref_end
        if item.metaData:
            row.metaData = item.metaData
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    resource_db_content.updatedUser = user_id
    resource_db_content.updateTime = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def delete_audio_bible(db_: Session, delitem: int,table_name = None,\
    resource_name=None,user_id=None):
    '''delete particular item from audio bibles, selected via resourceName and audio id'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    model_cls = table_name
    query = db_.query(model_cls)
    db_content = query.filter(model_cls.audioId == delitem).first()
    db_.flush()
    db_.delete(db_content)
    #db_.commit()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def get_sign_bible_videos(db_:Session, resource_name, title=None,**kwargs): #pylint: disable=too-many-locals
    '''Fetches rows of sign bible videos from the table specified by resource_name'''
    description = kwargs.get("description",None)
    search_word = kwargs.get("search_word",None)
    reference = kwargs.get("reference",None)
    link = kwargs.get("link",None)
    metadata = kwargs.get("metadata",None)
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    signvideo_id=kwargs.get("signvideo_id",None)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith(db_models.ResourceTypeName.SIGNBIBLEVIDEO.value):
        raise TypeException('The operation is supported only on sign bible videos')
    model_cls = db_models.dynamicTables[resource_name]
    query = db_.query(model_cls)
    if title:
        query = query.filter(model_cls.title == utils.normalize_unicode(title.strip()))
    if  description:
        query = query.filter(model_cls.description.contains(
            utils.normalize_unicode(description.strip())))
    if link:
        query = query.filter(model_cls.link == link)
    if signvideo_id:
        query = query.filter(model_cls.signVideoId == signvideo_id)
    if reference:
        query = filter_by_reference(db_,query, model_cls, reference)
    if metadata:
        meta = json.loads(metadata)
        for key in meta:
            key_match = db_models.SignBibleVideo.metaData.op('->>')(key).ilike(f'%{key}%')
            value_match = db_models.SignBibleVideo.metaData.op('->>')(key).ilike(f'%{meta[key]}%')
            query = query.filter(key_match | value_match)
    if search_word:
        search_pattern = " & ".join(re.findall(r'\w+', search_word))
        search_pattern += ":*"
        query = query.filter(text(
            "to_tsvector('simple', title || ' ' || signvideo_id || " +
            "' ' || description || ' ' || link || ' ' || " +
            "jsonb_to_tsvector('simple', reference, '[\"string\", \"numeric\"]') || ' ' || " +
            "jsonb_to_tsvector('simple', metadata, '[\"string\", \"numeric\"]') " +
            ") @@ to_tsquery('simple', :pattern)"
        ).bindparams(pattern=search_pattern))

    query = query.filter(model_cls.active == active)
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':query.offset(skip).limit(limit).all(),
        'resource_content':resource_db_content
        }
    return response

def upload_sign_bible_videos(db_: Session, resource_name, signvideos, user_id=None):
    '''Adds rows to the sign bible videos table specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != \
        db_models.ResourceTypeName.SIGNBIBLEVIDEO.value:
        raise TypeException('The operation is supported only on sign bible videos')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in signvideos:
        if item.reference:
            ref = item.reference.__dict__
            if ref['verseNumber'] is not None:
                ref_start = utils.create_decimal_ref_id(
                    db_,ref['book'],ref['chapter'],ref['verseNumber'])
            else:
                #setting verseNumber to 000 if its not present
                ref_start = utils.create_decimal_ref_id(db_,ref['book'],ref['chapter'],0)
                ref['verseNumber'] = 0
            if ref['verseEnd'] is not None:
                ref_end   = utils.create_decimal_ref_id(
                    db_,ref['bookEnd'],ref['chapterEnd'],ref['verseEnd'])
            else:
                #setting verseEnd to 999 if its not present
                ref_end   = utils.create_decimal_ref_id(db_,ref['bookEnd'],ref['chapterEnd'],999)
                ref['verseEnd'] = 999
        else:
            ref = None
            ref_end = None
            ref_start = None
        if item.title:
            item.title = utils.normalize_unicode(item.title.strip())
        if item.description:
            item.description = utils.normalize_unicode(item.description.strip())
        row = model_cls(
            title = item.title,
            description =item.description,
            reference = ref,
            refStart=ref_start,
            refEnd=ref_end,
            link = item.link,
            metaData = item.metaData,
            active = item.active,
            createdUser =  user_id)
        db_content.append(row)
    db_.add_all(db_content)
    db_.expire_all()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def update_sign_bible_videos(db_: Session, resource_name, signvideos, user_id=None): #pylint: disable=too-many-branches
    '''Update rows, that matches signvideoId in the sign bible videos table
    specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != \
        db_models.ResourceTypeName.SIGNBIBLEVIDEO.value:
        raise TypeException('The operation is supported only on sign bible videos')
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in signvideos:
        row = db_.query(model_cls).filter(
            model_cls.signVideoId == item.signVideoId).first()
        if not row:
            raise NotAvailableException(f"Sign Bible Video row with id:{item.signVideoId}, "+\
                f"not found for {resource_name}")
        if item.title:
            item.title = utils.normalize_unicode(item.title.strip())
            row.title = item.title
        if item.description:
            item.description = utils.normalize_unicode(item.description.strip())
            row.description = item.description
        if item.link:
            row.link = item.link
        if item.reference:
            ref = item.reference.__dict__
            if ref['verseNumber'] is not None:
                ref_start = utils.create_decimal_ref_id(
                    db_,ref['book'],ref['chapter'],ref['verseNumber'])
            else:
                ref_start = utils.create_decimal_ref_id(db_,ref['book'],ref['chapter'],0)
            if ref['verseEnd'] is not None:
                ref_end   = utils.create_decimal_ref_id(
                    db_,ref['bookEnd'],ref['chapterEnd'],ref['verseEnd'])
            else:
                ref_end   = utils.create_decimal_ref_id(db_,ref['bookEnd'],ref['chapterEnd'],999)
            row.reference = ref
            row.refStart=ref_start
            row.refEnd=ref_end
        if item.metaData:
            row.metaData = item.metaData
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
    resource_db_content.updatedUser = user_id
    resource_db_content.updateTime = datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response

def delete_sign_bible_videos(db_: Session, delitem: int,table_name = None,\
    resource_name=None,user_id=None):
    '''delete particular item from sign bible video, selected via resourceName and signvideo id'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    model_cls = table_name
    query = db_.query(model_cls)
    db_content = query.filter(model_cls.signVideoId == delitem).first()
    db_.flush()
    db_.delete(db_content)
    #db_.commit()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
    return response


def ref_to_bcv(book,chapter,verse):
    '''convert reference to BCV format'''
    bbb = str(book).zfill(3)
    ccc = str(chapter).zfill(3)
    vvv = str(verse).zfill(3)
    return bbb + ccc + vvv

def bcv_to_ref(bcvref,db_):
    '''convert bcv to reference'''
    bbb = str(bcvref)[0:-6]
    book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookId == int(bbb)).first()
    ref = {
        "book": book.bookCode,
        "chapter": str(bcvref)[-6:-3],
        "verseNumber": str(bcvref)[-3:]
      }
    return ref

def bible_split_verse_completion(db_content2,split_indexs):
    """create split verse entry in db object"""
    post_script_list = []
    for indx in split_indexs:
        for char in db_content2[indx].metaData["tempcontent"]:
            post_script_list.append(char)
        post_script_list.sort()
        for char in post_script_list:
            db_content2[indx].verseText = \
                    db_content2[indx].verseText + ' '+ db_content2[indx].metaData\
                        ["tempcontent"][char]["verseText"]
            db_content2[indx].verseText=db_content2[indx].verseText.strip()
        db_content2[indx].metaData.pop("tempcontent")
        post_script_list = []
    return db_content2

def bible_verse_type_check(content, model_cls_2, book, db_content2, chapter_number,*args):#pylint: disable=too-many-locals
    """manage upload bible books verses based on verse type normal, merged
    verse or split verse"""
    split_indexs = args[0]
    normal_verse_pattern = re.compile(r'\d+$')
    split_verse_pattern = re.compile(r'(\d+)(\w+)$')
    merged_verse_pattern = re.compile(r'(\d+)-(\d+)$')
    metadata_field = {"publishedVersification":[]}
    #NormalVerseNumber Pattern
    # print("CONTENT",content)
    if normal_verse_pattern.match(str(content['verseNumber'])):
        row_other = model_cls_2(
        book_id = book.bookId,
        chapter = chapter_number,
        verseNumber = content['verseNumber'],
        verseText = utils.normalize_unicode(content['verseText'].strip()))
        db_content2.append(row_other)
    #splitVerseNumber Pattern
    # combine split verses and use the whole number verseNumber
    elif split_verse_pattern.match(str(content['verseNumber'])):
        match_obj = split_verse_pattern.match(content['verseNumber'])
        post_script = match_obj.group(2)
        verse_number = match_obj.group(1)

        if not len(db_content2)==0 and book.bookId == db_content2[-1].book_id and\
            chapter_number == db_content2[-1].chapter\
            and verse_number == db_content2[-1].verseNumber:
            metadata_field['publishedVersification'].append(
                {"verseNumber": content["verseNumber"], "verseText":content["verseText"]})
            db_content2[-1].metaData['publishedVersification'].append(
                metadata_field['publishedVersification'][0])
            db_content2[-1].metaData['tempcontent'][post_script] = \
                {"verseText":utils.normalize_unicode(content['verseText'].strip()),
                "verseNumber":verse_number}
        else:
            #first time split verse
            split_indexs.append(len(db_content2))
            metadata_field["tempcontent"] = {
                post_script:{"verseText":utils.normalize_unicode(content['verseText'].strip()),
                "verseNumber":verse_number}}
            metadata_field['publishedVersification'].append(
                {"verseNumber": content["verseNumber"], "verseText":content["verseText"]})
            row_other = model_cls_2(
            book_id = book.bookId,
            chapter = chapter_number,
            verseNumber = verse_number,
            verseText = '',
            metaData = metadata_field)
            db_content2.append(row_other)
    #mergedVerseNumber Pattern , keep the whole text in first verseNumber of merged verses
    elif merged_verse_pattern.match(str(content['verseNumber'])):
        match_obj = merged_verse_pattern.match(content['verseNumber'])
        verse_number = match_obj.group(1)
        verse_number_end = match_obj.group(2)
        metadata_field['publishedVersification'].append({"verseNumber":content['verseNumber'],
            "verseText":content['verseText']})
        row_other = model_cls_2(
            book_id = book.bookId,
            chapter = chapter_number,
            verseNumber = verse_number,
            verseText = utils.normalize_unicode(content['verseText'].strip()),
            metaData = metadata_field)
        db_content2.append(row_other)
        ## add empty text in the rest of the verseNumber range
        for versenum in range(int(verse_number)+1, int(verse_number_end)+1):
            row_other = model_cls_2(
                book_id = book.bookId,
                chapter = chapter_number,
                verseNumber = versenum,
                verseText = "",
                metaData = metadata_field)
            db_content2.append(row_other)
    else:
        raise TypeException(#pylint: disable=raising-format-tuple,too-many-function-args
            "Unrecognized pattern in %s chapter %s verse %s",
            book.bookName, chapter_number, content['verseNumber'])
    return db_content2, split_indexs


def upload_bible_books(db_: Session, resource_name, books, user_id=None):  # pylint: disable=too-many-locals,too-many-branches
    '''Adds rows to the bible table and corresponding bible_cleaned specified by resource_name'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != db_models.ResourceTypeName.BIBLE.value:
        raise TypeException('The operation is supported only on bible')
    model_cls_2 = db_models.dynamicTables[resource_name + '_cleaned']
    db_content = []
    db_content2 = []
    split_indexs = []
    for item in books:
        #checks for uploaded books
        book = upload_bible_books_checks(db_, item, resource_name, db_content)
        usfm_parser = USFMParser(item.USFM)
        item.JSON =usfm_parser.to_usj(include_markers= Filter.BCV+Filter.TEXT)
        for chapter in item.JSON["content"]:
            if isinstance(chapter, dict) and chapter.get("type") == "chapter:c":
                if "number" not in chapter:
                    raise TypeException("JSON is not of the required format..")
                try:
                    chapter_number = int(chapter['number'])
                    # print("CHAPTERNUM", chapter_number)
                except ValueError as exe:
                    raise TypeException("JSON is not of the required format. Chapter number should be an integer.") from exe
        # Iterate over the content of the chapter
        for content in item.JSON["content"]:
            if isinstance(content, dict) and content.get("type") == "verse:v":
                # verseNumber = content.get("number", "")
                # print("VERSE" ,content)
                verseNumber = content.get("number", "")
                # verseText = content.get("content", "")
                # print("VERSENUM", verseNumber)
                next_index = item.JSON["content"].index(content) + 1
                if next_index < len(item.JSON["content"]) and isinstance(item.JSON["content"][next_index], str):
                    verseText = item.JSON["content"][next_index]
                    # print("VERSETEXT", verseText)
                if verseNumber:
                    if verseText is None:
                        raise TypeException("JSON is not of the required format. verseText not found")
                   # Include verse and verse text in content
                    content["verseNumber"] = verseNumber
                    content["verseText"] = verseText
                   # Call your function to process the verse
                    db_content2, split_indexs = \
                        bible_verse_type_check(content, model_cls_2,
                            book, db_content2, chapter_number, split_indexs)
    if len(split_indexs) > 0:
        db_content2 = bible_split_verse_completion(db_content2, split_indexs)
    db_.add_all(db_content)
    db_.add_all(db_content2)
    resource_db_content.updatedUser = user_id
    # db_.commit()
    response = {
        'db_content':db_content,
        'resource_content':resource_db_content
    }
    return response




def upload_bible_books_checks(db_, item, resource_name, db_content):
    """checks for uploaded bible books"""
    model_cls = db_models.dynamicTables[resource_name]
    book_code = None
    usfm_parser = USFMParser(item.USFM)
    if item.USFM:
        try:
            item.JSON =usfm_parser.to_usj( )
        except Exception as exe:
            raise TypeException("USFM is not of the required format.") from exe
    # if item.USFM is None:
    #     try:
    #         item.USFM = utils.form_usfm(item.JSON)
    #     except Exception as exe:
    #         raise TypeException("Input JSON is not of the required format.") from exe
    try:
        # Accessing the book code directly from the JSON structure
        book_code = item.JSON["content"][0]["code"]
    except Exception as exe:
        raise TypeException("Input JSON is not of the required format") from exe
    book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == book_code.lower() ).first()
    if not book:
        raise NotAvailableException(f'Bible Book code, {book_code}, not found in database')
    row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
    if row:
        if row.USFM:
            raise AlreadyExistsException(f"Bible book, {book.bookCode}, already present in DB")
        row.USFM = utils.normalize_unicode(item.USFM)
        row.JSON = item.JSON
        row.active = True
    else:
        row = model_cls(
            book_id=book.bookId,
            USFM=utils.normalize_unicode(item.USFM),
            JSON=item.JSON,
            active=True)
    db_.flush()
    db_content.append(row)
    return book


def update_bible_books(db_: Session, resource_name, books, user_id=None):
    '''change values of bible books already uploaded'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    if not resource_db_content:
        raise NotAvailableException(f'Resource {resource_name}, not found in database')
    if resource_db_content.resourceType.resourceType != db_models.ResourceTypeName.BIBLE.value:
        raise TypeException('The operation is supported only on bible')
    # update the bible table
    model_cls = db_models.dynamicTables[resource_name]
    db_content = []
    for item in books:
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        row = db_.query(model_cls).filter(model_cls.book_id == book.bookId).first()
        if not row:
            raise NotAvailableException(f"Bible book, {item.bookCode}, not found in Database")
        if item.USFM:
            usfm_parser = USFMParser(item.USFM)
            item.JSON =usfm_parser.to_usj( )
            row.USFM = utils.normalize_unicode(item.USFM)
            row.JSON = item.JSON
        if item.active is not None:
            row.active = item.active
        db_.flush()
        db_content.append(row)
        db_.commit()
        resource_db_content = update_bible_books_cleaned\
            (db_,resource_name,books,resource_db_content,user_id)
        response = {
        'db_content':db_content,
        'resource_content':resource_db_content
        }
        # return db_content
        return response



def update_bible_books_cleaned(db_,resource_name,books,resource_db_content,user_id):#pylint: disable=too-many-branches,too-many-locals
    """update bible cleaned table"""
    db_content2 = []
    split_indexs = []
    model_cls_2 = db_models.dynamicTables[resource_name+'_cleaned']
    for item in books:#pylint: disable=too-many-nested-blocks
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == item.bookCode.lower() ).first()
        print("RESFT",item)
        if item.USFM:
            db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).delete()
            usfm_parser = USFMParser(item.USFM)
            item.JSON =usfm_parser.to_usj(include_markers= Filter.BCV+Filter.TEXT)
            for chapter in item.JSON["content"]:
                if isinstance(chapter, dict) and chapter.get("type") == "chapter:c":
                    if "number" not in chapter:
                        raise TypeException("JSON is not of the required format..")
                    try:
                        chapter_number = int(chapter['number'])
                    except ValueError as exe:
                        raise TypeException("JSON is not of the required format.\ Chapter number should be an integer.") from exe
            # Iterate over the content of the chapter
            for content in item.JSON["content"]:
                if isinstance(content, dict) and content.get("type") == "verse:v":
                    verseNumber = content.get("number", "")
                    next_index = item.JSON["content"].index(content) + 1
                    if next_index < len(item.JSON["content"]) and isinstance(item.JSON["content"][next_index], str):
                        verseText = item.JSON["content"][next_index]
                    if verseNumber:
                        if verseText is None:
                            raise TypeException("JSON is not of the required format. verseText not found")
                        # Include verse and verse text in content
                        content["verseNumber"] = verseNumber
                        content["verseText"] = verseText
                        # print("CONTENT",content)
                        # Call your function to process the verse
                        db_content2, split_indexs = \
                            bible_verse_type_check(content, model_cls_2, book, db_content2, chapter_number, split_indexs)
                        print(" ssmbook",book.bookId)
        if item.active is not None:
            #  set all the verse rows' active flag accordingly
            rows = db_.query(model_cls_2).filter(
                model_cls_2.book_id == book.bookId).all()
            for row in rows:
                row.active = item.active
    if len(split_indexs) > 0:
        db_content2 = bible_split_verse_completion(db_content2, split_indexs)
    db_.add_all(db_content2)
    db_.flush()
    db_.commit()
    # resource_db_content.updatedUser = user_id
    resource_db_content.updatedUser = user_id
    return resource_db_content
    # db_.commit()






def get_bible_versification(db_, resource_name):
    '''select the reference list from bible_cleaned table'''
    model_cls = db_models.dynamicTables[resource_name+"_cleaned"]
    query = db_.query(model_cls).prefix_with(
        "'"+resource_name+"' as bible, ")
    query = query.options(defer(model_cls.verseText))
    query = query.order_by(model_cls.refId)
    versification = {"maxVerses":{}, "mappedVerses":{}, "excludedVerses":[], "partialVerses":{}}
    prev_book_code = None
    prev_chapter = 0
    prev_verse = 0
    for row in query.all():
        if row.book.bookCode != prev_book_code:
            if prev_book_code is not None:
                versification['maxVerses'][prev_book_code].append(prev_verse)
            versification['maxVerses'][row.book.bookCode] = []
            prev_book_code = row.book.bookCode
            prev_chapter = row.chapter
        elif row.chapter != prev_chapter:
            versification['maxVerses'][row.book.bookCode].append(prev_verse)
            if prev_chapter+1 != row.chapter:
                for chap in range(prev_chapter+1, row.chapter): #pylint: disable=unused-variable
                    versification['maxVerses'][row.book.bookCode].append(0)
            prev_chapter = row.chapter
        elif row.verseNumber != prev_verse + 1:
            for i in range(prev_verse+1, row.verseNumber):
                versification['excludedVerses'].append(f'{prev_book_code} {row.chapter}:{i}')
        prev_verse = row.verseNumber
    if prev_book_code is not None:
        versification['maxVerses'][prev_book_code].append(prev_verse)
    # return versification
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':versification,
        'resource_content':resource_db_content
        }
    return response

def get_available_bible_books(db_, resource_name,book_code=None, content_type=None,#pylint: disable=too-many-locals
    biblecontent_id=None, **kwargs):
    '''fetches the contents of .._bible table based of provided resource_name and other options'''
    active = kwargs.get("active",True)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith('_bible'):
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[resource_name]
    query = db_.query(model_cls).options(joinedload(model_cls.book))
    fetched = None
    if biblecontent_id:
        query = query.filter(model_cls.bookContentId  == biblecontent_id)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if content_type == "usfm":
        query = query.options(defer(model_cls.JSON))
    elif content_type == "json":
        query = query.options(defer(model_cls.USFM))
    elif content_type == "all":
        query = query.filter(model_cls.active == active)
        fetched = query.offset(skip).limit(limit).all()
    elif content_type is None:
        query = query.options(defer(model_cls.JSON), defer(model_cls.USFM))
    if not fetched:
        fetched = query.filter(model_cls.active == active).offset(skip).limit(limit).all()
    results = [res.__dict__ for res in fetched]
    # return results
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':results,
        'resource_content':resource_db_content
        }
    return response

def delete_bible_book(db_: Session, delitem: int,\
    resource_name=None,user_id=None):
    '''delete particular item from bible, selected via resourcename and bible content id'''
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    model_cls  = db_models.dynamicTables[resource_name]
    model_cls2 =  db_models.dynamicTables[resource_name+'_cleaned']
    query = db_.query(model_cls)
    query2 = db_.query(model_cls2)
    db_content = query.filter(model_cls.bookContentId == delitem).first()
    db_content2 = query2.filter(db_content.book_id == model_cls2.book_id).all()
    db_.flush()
    db_.delete(db_content)
    for item in db_content2:
        db_.delete(item)
    #db_.commit()
    resource_db_content.updatedUser = user_id
    response = {
        'db_content'    :db_content,
        'db_content2'   :db_content2,
        'resource_content':resource_db_content
        }
    return response

def get_bible_verses(db_:Session, resource_name, book_code=None, chapter=None, verse=None,#pylint: disable=too-many-locals
    **kwargs):
    '''queries the bible cleaned table for verses'''
    last_verse = kwargs.get("last_verse",None)
    search_phrase = kwargs.get("search_phrase",None)
    if resource_name not in db_models.dynamicTables:
        raise NotAvailableException(f'{resource_name} not found in database.')
    if not resource_name.endswith('_bible'):
        raise TypeException('The operation is supported only on bible')
    model_cls = db_models.dynamicTables[resource_name+'_cleaned']
    query = db_.query(model_cls)
    if book_code:
        query = query.filter(model_cls.book.has(bookCode=book_code.lower()))
    if chapter:
        query = query.filter(model_cls.chapter == chapter)
    if verse:
        if not last_verse:
            last_verse = verse
        query = query.filter(model_cls.verseNumber >= verse, model_cls.verseNumber <= last_verse)
    if search_phrase:
        query = query.filter(model_cls.verseText.like(
            '%'+utils.normalize_unicode(search_phrase.strip())+"%"))
    results = query.filter(model_cls.active ==
        kwargs.get("active",True)).offset(kwargs.get("skip",0)).limit(kwargs.get("limit",100)).all()
    ref_combined_results = []
    for res in results:
        ref_combined = {}
        ref_combined['verseText'] = res.verseText
        ref_combined['metaData'] = res.metaData
        ref = { "bible": resource_name,
                "book": res.book.bookCode,
                "chapter": res.chapter,
                "verseNumber":res.verseNumber}
        ref_combined['reference'] = ref
        ref_combined_results.append(ref_combined)
    # return ref_combined_results
    resource_db_content = db_.query(db_models.Resource).filter(
        db_models.Resource.resourceName == resource_name).first()
    response = {
        'db_content':ref_combined_results,
        'resource_content':resource_db_content
        }
    return response

def extract_text(db_:Session, tables, books, skip=0, limit=100):
    '''get all text field contents from the list of tables provided.
    The text column would be determined based on the table type'''
    sentence_list = []
    for table in tables:
        if table.resourceType.resourceType == db_models.ResourceTypeName.BIBLE.value:
            model_cls = db_models.dynamicTables[table.resourceName+'_cleaned']
            query = db_.query(model_cls.refId.label('sentenceId'),
                model_cls.ref_string.label('surrogateId'),
                model_cls.verseText.label('sentence')).join(model_cls.book)
        elif table.resourceType.resourceType == db_models.ResourceTypeName.COMMENTARY.value:
            model_cls = db_models.dynamicTables[table.resourceName]
            query = db_.query(model_cls.commentaryId.label('sentenceId'),
                model_cls.ref_string.label('surrogateId'),
                model_cls.commentary.label('sentence'))
        else:
            continue
        if books is not None:
            if table.resourceType.resourceType == db_models.ResourceTypeName.BIBLE.value:
                query = query.filter(
                     db_models.BibleBook.bookCode.in_([buk.lower() for buk in books]))
            else:
                query = query.filter(
                    model_cls.reference['book'].astext.in_([buk.lower() for buk in books]))
        sentence_list += query.offset(skip).limit(limit).all()
        if len(sentence_list) >= limit:
            sentence_list = sentence_list[:limit]
            break
    return sentence_list
    