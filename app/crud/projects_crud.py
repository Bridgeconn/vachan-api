''' Place to define all data processing and Database CRUD operations for
Translation Project Management. The translation or NLP related functions of these
projects are included in nlp_crud module'''

import re
import json
import datetime
from functools import wraps
from pytz import timezone
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified
from fastapi import HTTPException
import db_models
from schema import schemas_nlp
from dependencies import log
from crud import utils, nlp_crud
from custom_exceptions import NotAvailableException, TypeException,\
    UnprocessableException, PermissionException
from auth.authentication import get_all_or_one_kratos_users

ist_timezone = timezone("Asia/Kolkata")

#pylint: disable=W0143,E1101
###################### Translation Project Mangement ######################
def create_translation_project(db_:Session, project, user_id=None,app=None):
    '''Add a new project entry to the translation projects table'''
    source = db_.query(db_models.Language).filter(
        db_models.Language.code==project.sourceLanguageCode).first()
    target = db_.query(db_models.Language).filter(
        db_models.Language.code==project.targetLanguageCode).first()
    meta= {}
    meta["books"] = []
    meta["useDataForLearning"] = project.useDataForLearning
    if project.stopwords:
        meta['stopwords'] = project.stopwords.__dict__
    if project.punctuations:
        meta['punctuations'] = project.punctuations
    if project.compatibleWith is None:
        project.compatibleWith = [app]
    db_content = db_models.TranslationProject(
        projectName=utils.normalize_unicode(project.projectName),
        source_lang_id=source.languageId,
        target_lang_id=target.languageId,
        documentFormat=project.documentFormat.value,
        active=project.active,
        createdUser=user_id,
        updatedUser=user_id,
        metaData=meta,
        compatibleWith = project.compatibleWith
        )
    db_.add(db_content)
    db_.flush()
    db_content2 = db_models.TranslationProjectUser(
        project_id=db_content.projectId,
        userId=user_id,
        userRole="projectOwner",
        active=True)
    db_.add(db_content2)
    # db_.commit()
    return db_content

book_pattern_in_surrogate_id = re.compile(r'^[\w\d]\w\w')
def update_translation_project_sentences(db_, project_obj,project_id, new_books, user_id):
    """bulk selected book update in update translation project"""
    for sent in project_obj.sentenceList:
        norm_sent = utils.normalize_unicode(sent.sentence)
        offsets = [0, len(norm_sent)]
        if re.search(book_pattern_in_surrogate_id, sent.surrogateId):
            book_code =  re.search(book_pattern_in_surrogate_id, sent.surrogateId).group(0).lower()
            if book_code not in new_books and book_code in utils.BOOK_CODES:
                new_books.append(book_code)
        draft_row = db_models.TranslationDraft(
            project_id=project_id,
            sentenceId=sent.sentenceId,
            surrogateId=sent.surrogateId,
            sentence=norm_sent,
            draft="",
            draftMeta=[[offsets,[0,0], "untranslated"]],
            updatedUser=user_id)
        db_.add(draft_row)

def get_sentences_from_usfm_json(chapters_json, book_code, book_id):
    '''Obtain the following from USFM content
    * sentence id as per bcv value in int
    * surrogate id as human readable reference
    * sentence from verse text
    * Handle merged verses. Keep one entry using id with first verse number
    * Handle split verses, by combining all parts to form one entry'''
    draft_rows = []
    for chap in chapters_json:
        chapter_number = chap['chapterNumber']
        found_split_verse = None
        splits = []
        for cont in chap['contents']:
            if "verseNumber" in cont:
                verse_number = cont['verseNumber']
                verse_text = cont['verseText']
                try:
                    verse_number_int = int(verse_number)
                    surrogate_id = book_code+" "+str(chapter_number)+":"+verse_number
                except Exception as exe: #pylint: disable=W0703
                    log.error(str(exe))
                    log.warning(
                        "Found a special verse %s. Checking for split verse or merged verses...",
                        verse_number)
                    if "-" in verse_number:
                        verse_number_int = int(verse_number.split('-')[0])
                        surrogate_id = book_code+" "+str(chapter_number)+":"+str(verse_number)
                    elif re.match(r'\d+\D+$', verse_number):
                        split_verse_obj = re.match(r'(\d+)(\D+)$', verse_number)
                        verse_number_int = int(split_verse_obj.group(1))
                        if found_split_verse and found_split_verse == verse_number_int:
                            # found a continuation
                            splits.append(split_verse_obj.group(2))
                            verse_text = draft_rows[-1]['sentence'] +" "+ verse_text
                            draft_rows.pop(-1)
                        else:
                            # found the start of a split verse
                            found_split_verse = verse_number_int
                            splits = [split_verse_obj.group(2)]
                        surrogate_id = book_code+" "+str(chapter_number)+":"+\
                            str(verse_number_int)+ "-".join(splits)
                    else:
                        raise UnprocessableException(
                            f"Error with verse number {verse_number}") from exe
                draft_rows.append({
                    "sentenceId": book_id*1000000+\
                                int(chapter_number)*1000+verse_number_int,
                    "surrogateId": surrogate_id,
                    "sentence": verse_text,
                    "draftMeta": [[[0, len(verse_text)],[0,0], "untranslated"]],
                    })
    return draft_rows

def update_translation_project_uploaded_book(db_,project_obj,project_id,new_books,user_id):
    """bulk uploaded book update in update translation project"""
    for usfm in project_obj.uploadedUSFMs:
        usfm_json = utils.parse_usfm(usfm)
        book_code = usfm_json['book']['bookCode'].lower()
        book = db_.query(db_models.BibleBook).filter(
            db_models.BibleBook.bookCode == book_code).first()
        if not book:
            raise NotAvailableException(f"Book, {book_code}, not found in database")
        new_books.append(book_code)
        draft_rows = get_sentences_from_usfm_json(usfm_json['chapters'], book_code, book.bookId)
        for item in draft_rows:
            db_.add(db_models.TranslationDraft(
                project_id=project_id,
                sentenceId=item['sentenceId'],
                surrogateId=item['surrogateId'],
                sentence=item['sentence'],
                draft="",
                draftMeta=item['draftMeta'],
                updatedUser=user_id))

def update_translation_project(db_:Session, project_obj, project_id, user_id=None):
    '''Either activate or deactivate a project or Add more books to a project,
    adding all new verses to the drafts table'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    new_books = []
    if project_obj.selectedBooks:
        new_books += project_obj.selectedBooks.books
    if project_obj.sentenceList:
        update_translation_project_sentences(db_, project_obj,project_id, new_books, user_id)
    if project_obj.uploadedUSFMs:
        #uploaded usfm book add to project
        update_translation_project_uploaded_book(db_,project_obj,project_id,new_books,user_id)
    # db_.commit()
    # db_.expire_all()
    if project_obj.projectName:
        project_row.projectName = project_obj.projectName
    if project_obj.active is not None:
        project_row.active = project_obj.active
    if project_obj.useDataForLearning is not None:
        project_row.metaData['useDataForLearning'] = project_obj.useDataForLearning
        flag_modified(project_row, "metaData")
    if project_obj.stopwords:
        project_row.metaData['stopwords'] = project_obj.stopwords.__dict__
        flag_modified(project_row, "metaData")
    if project_obj.punctuations:
        project_row.metaData['punctuations'] = project_obj.punctuations
        flag_modified(project_row, "metaData")
    if project_obj.compatibleWith:
        project_row.compatibleWith= project_obj.compatibleWith
    project_row.updatedUser = user_id
    project_row.updateTime = datetime.datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
    if len(new_books) > 0:
        project_row.metaData['books'] += new_books
        flag_modified(project_row, "metaData")
    db_.add(project_row)
    # db_.commit()
    # db_.refresh(project_row)
    return project_row

# pylint: disable=duplicate-code
def check_app_compatibility_decorator(func):#pylint:disable=too-many-statements
    """Decorator function for to check app compatibility"""
    @wraps(func)
    async def wrapper(*args, **kwargs):#pylint: disable=too-many-branches,too-many-statements
        request = kwargs.get('request')
        db_ = kwargs.get("db_")
        query_params = request.query_params
        body = await request.body()
        compatible_with = []
        project_id = None

        if len(body) != 0:
            json_string = body.decode()
            parsed_data = json.loads(json_string)
            if 'projectId' in parsed_data:
                project_id = parsed_data['projectId']
            elif 'project_id' in parsed_data:
                project_id = parsed_data['project_id']
            if 'project_id' in query_params:
                project_id = query_params['project_id']
        else:
            project_id = query_params['project_id']
        if project_id is not None:
            project_obj = db_.query(db_models.TranslationProject).get(project_id)
            if project_obj is not None:
                compatible_with = project_obj.compatibleWith
        else:
            if 'compatibleWith' in parsed_data and parsed_data['compatibleWith'] is not None:
                compatible_with = parsed_data['compatibleWith']
        if 'app' in request.headers:
            client_app = request.headers['app']
            if len(compatible_with) ==0:
                raise HTTPException(status_code=404,detail = \
                    f"Project with id, {project_id}, not present")
            if client_app not in compatible_with:
                raise PermissionException("Incompatible app")
        else:
            raise PermissionException("Incompatible app")
        return await func(*args, **kwargs)
    return wrapper
# pylint: enable=duplicate-code

def get_translation_projects(db_:Session, project_name=None, source_language=None,
    target_language=None, **kwargs):
    '''Fetch autographa projects as per the query options'''
    active = kwargs.get("active",True)
    compatible_with = kwargs.get("compatible_with",None)
    user_id = kwargs.get("user_id",None)
    skip = kwargs.get("skip",0)
    limit = kwargs.get("limit",100)
    query = db_.query(db_models.TranslationProject)
    if project_name:
        query = query.filter(
            db_models.TranslationProject.projectName == utils.normalize_unicode(project_name))
    if source_language:
        source = db_.query(db_models.Language).filter(db_models.Language.code == source_language
            ).first()
        if not source:
            raise NotAvailableException(f"Language, {source_language}, not found")
        query = query.filter(db_models.TranslationProject.source_lang_id == source.languageId)
    if target_language:
        target = db_.query(db_models.Language).filter(db_models.Language.code == target_language
            ).first()
        if not target:
            raise NotAvailableException(f"Language, {target_language}, not found")
        query = query.filter(db_models.TranslationProject.target_lang_id == target.languageId)
    if compatible_with is not None:
        query = query.filter(text(
            "ARRAY[:compatible_with]::text[] <@ translation_projects.compatible_with").bindparams(
            compatible_with=compatible_with))
    if user_id:
        query = query.filter(db_models.TranslationProject.users.any(userId=user_id))
    query = query.filter(db_models.TranslationProject.active == active)
    return query.offset(skip).limit(limit).all()

def remove_translation_project(db_, project_id):
    '''To remove a project'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id {project_id} not found")
    db_.delete(project_row)
    return project_row

def add_project_user(db_:Session, project_id, user_id, current_user=None):
    '''Add an additional user(not the created user) to a project, in translation_project_users'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    get_all_or_one_kratos_users(user_id)
    db_content = db_models.TranslationProjectUser(
        project_id=project_id,
        userId=user_id,
        userRole='projectMember',
        active=True)
    db_.add(db_content)
    project_row.updatedUser = current_user
    response = {
        "db_content" : db_content,
        "project_content" : project_row
    }
    # db_.commit()
    return response

def update_project_user(db_, user_obj, project_id,current_user=10101):
    '''Change role, active status or metadata of user in a project'''
    user_row = db_.query(db_models.TranslationProjectUser).filter(
        db_models.TranslationProjectUser.project_id == project_id,
        db_models.TranslationProjectUser.userId == user_obj.userId).first()
    if not user_row:
        raise NotAvailableException("User-project pair not found")
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if user_obj.userRole:
        user_row. userRole = user_obj.userRole
    if user_obj.metaData:
        user_row.metaData = user_obj.metaData
        flag_modified(user_row,'metaData')
    if user_obj.active is not None:
        user_row.active = user_obj.active
    user_row.project.updatedUser = current_user
    db_.add(user_row)
    # db_.commit()
    response = { #pylint: disable=unused-variable
        "db_content" : user_row,
        "project_content" : project_row
    }
    return user_row

def remove_project_user(db_, project_id, user_id, current_user=None):
    '''To remove/un-assign a user from a project'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    user_row = db_.query(db_models.TranslationProjectUser).filter(
        db_models.TranslationProjectUser.project_id == project_id,
        db_models.TranslationProjectUser.userId == user_id).first()
    if not user_row:
        raise NotAvailableException("User-project pair not found")
    if user_id == current_user:
        raise PermissionException("A user cannot remove oneself from a project.")
    db_.delete(user_row)
    # db_.commit()
    response = {
        "db_content": user_row,
        "project_content": project_row
    }
    return response

def obtain_project_draft(db_:Session, project_id, books, sentence_id_list, sentence_id_range,
    **kwargs):
    '''generate draft for selected sentences as usfm or json'''
    output_format = kwargs.get("output_format","usfm")
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    draft_rows = obtain_project_source(db_, project_id, books, sentence_id_list,
        sentence_id_range, with_draft=True)
    draft_rows = draft_rows['db_content']
    if output_format == schemas_nlp.DraftFormats.USFM :
        draft_out = nlp_crud.create_usfm(draft_rows)
    elif output_format == schemas_nlp.DraftFormats.JSON:
        draft_out = nlp_crud.export_to_json(project_row.sourceLanguage,
            project_row.targetLanguage, draft_rows, None)
    elif output_format == schemas_nlp.DraftFormats.PRINT:
        draft_out = nlp_crud.export_to_print(draft_rows)
    else:
        raise TypeException(f"Unsupported output format: {output_format}")
    response = {
        'db_content':draft_out,
        'project_content':project_row
        }
    return response

def update_project_draft(db_:Session, project_id, sentence_list, user_id):
    '''Directly write to the draft and draftMeta fields of project sentences'''
    sentence_id_list = [sent.sentenceId for sent in sentence_list]
    source_resp = obtain_project_source(db_, project_id,
        sentence_id_list=sentence_id_list, with_draft=True)
    project_row = source_resp['project_content']
    sentences = source_resp['db_content']
    for input_sent in sentence_list:
        sent = None
        for read_sent in sentences:
            if input_sent.sentenceId == read_sent.sentenceId:
                sent = read_sent
                break
        if not sent:
            raise NotAvailableException(f"Sentence id: {input_sent.sentenceId},"+\
                " not found in project")
        utils.validate_draft_meta(sentence=sent.sentence, draft=input_sent.draft,
            draft_meta=input_sent.draftMeta)
        sent.draft = input_sent.draft
        sent.draftMeta = input_sent.draftMeta
        sent.updatedUser = user_id
    project_row.updatedUser = user_id
    project_row.updateTime = datetime.datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
    response_result = {
        'db_content':sentences,
        'project_content':project_row
        }
    #Also add any new confirmed translations to translation memory
    gloss_list = []
    for sent in sentences:
        for meta_item in sent.draftMeta:
            if meta_item[2] != "confirmed":
                continue
            gloss_list.append({
                "token": sent.sentence[meta_item[0][0]:meta_item[0][1]],
                "translations":[sent.draft[meta_item[1][0]:meta_item[1][1]]]
                })
    nlp_crud.add_to_translation_memory(db_,
        project_row.sourceLanguage.code,
        project_row.targetLanguage.code, gloss_list, default_val=1)
    return response_result

def obtain_project_progress(db_, project_id, books, sentence_id_list, sentence_id_range):#pylint: disable=too-many-locals
    '''Calculate project translation progress in terms of how much of draft is translated'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    draft_rows = obtain_project_source(db_, project_id, books, sentence_id_list,
        sentence_id_range, with_draft=True)
    draft_rows = draft_rows["db_content"]
    confirmed_length = 0
    suggestions_length = 0
    untranslated_length = 0
    for row in draft_rows:
        for segment in row.draftMeta:
            token_len = segment[0][1] - segment[0][0]
            if token_len <= 1:
                continue #possibly spaces or punctuations
            if segment[2] == "confirmed":
                confirmed_length += token_len
            elif segment[2] == "suggestion":
                suggestions_length += token_len
            else:
                untranslated_length += token_len
    total_length = confirmed_length + suggestions_length + untranslated_length
    if total_length == 0:
        total_length = 1
    result = {"confirmed": confirmed_length/total_length,
        "suggestion": suggestions_length/total_length,
        "untranslated": untranslated_length/total_length}
    # return result
    response_result = {
        'db_content':result,
        'project_content':project_row
        }
    return response_result

def obtain_project_token_translation(db_, project_id, token, occurrences): # pylint: disable=unused-argument
    '''Get the current translation for specific tokens providing their occurence in source'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    new_occurences = []
    for occur in occurrences:
        if not isinstance(occur, dict):
            new_occurences.append(occur.__dict__ )
        else:
            new_occurences.append(occur)
    occurrences = new_occurences
    sentence_list = [occur["sentenceId"] for occur in occurrences]
    draft_rows = obtain_project_source(db_, project_id, sentence_id_list=sentence_list,
        with_draft=True)
    draft_rows = draft_rows["db_content"]
    translations = pin_point_token_in_draft(occurrences, draft_rows)
    # return translations
    response = {
        'db_content':translations[0],
        'project_content':project_row
        }
    return response

def versification_check(row, prev_book_code, versification, prev_verse, prev_chapter):
    """versification check for project source versification"""
    if row.sentenceId not in range(1000000,68000000):
        raise TypeException("For versification, sentenceIds need to be refids(bbcccvvv)")
    book_id = int(row.sentenceId/1000000)
    chapter = int(row.sentenceId/1000)%1000
    verse = row.sentenceId%1000
    book_code = utils.books[book_id]['book_code']
    if book_code != prev_book_code:
        if prev_book_code is not None:
            versification['maxVerses'][prev_book_code].append(prev_verse)
        versification['maxVerses'][book_code] = []
        prev_book_code = book_code
        prev_chapter = chapter
    elif chapter != prev_chapter:
        versification['maxVerses'][book_code].append(prev_verse)
        if prev_chapter+1 != chapter:
            for chap in range(prev_chapter+1, chapter): #pylint: disable=unused-variable
                versification['maxVerses'][book_code].append(0)
        prev_chapter = chapter
    elif verse != prev_verse + 1:
        for i in range(prev_verse+1, verse):
            versification['excludedVerses'].append(f'{prev_book_code} {chapter}:{i}')
    prev_verse = verse
    return prev_book_code, versification, prev_verse

def get_project_source_versification(db_, project_id):
    '''considering the project source is always bible verses, get their versification structure'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    query = db_.query(db_models.TranslationDraft).filter(
        db_models.TranslationDraft.project_id==project_id)
    verse_rows = query.order_by(db_models.TranslationDraft.sentenceId).all()
    versification = {"maxVerses":{}, "mappedVerses":{}, "excludedVerses":[], "partialVerses":{}}
    prev_book_code = None
    prev_chapter = 0
    prev_verse = 0
    for row in verse_rows:
        #versification checks
        prev_book_code, versification, prev_verse =\
             versification_check(row, prev_book_code, versification, prev_verse, prev_chapter)
    if prev_book_code is not None:
        versification['maxVerses'][prev_book_code].append(prev_verse)
    # return versification
    response = {
        'db_content':versification,
        'project_content':project_row
        }
    return response

def get_project_source_per_token(db_:Session, project_id, token, occurrences): #pylint: disable=unused-argument
    '''get sentences and drafts for the token, which splits the token & translation in metadraft
    allowing it to be easily identifiable and highlightable at UI'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not present")
    sent_ids = [occur.sentenceId for occur in occurrences]
    draft_rows = obtain_project_source(db_, project_id,
        sentence_id_list=sent_ids, with_draft=True)
    draft_rows = draft_rows['db_content']
    occur_list = []
    for occur in occurrences:
        occur_list.append(occur.__dict__)
    translations = pin_point_token_in_draft(occur_list, draft_rows)
    for draft, trans in zip(draft_rows, translations):
        for mta in trans['meta_to_be_replaced']:
            draft.draftMeta.remove(mta)
        for mta in trans['replacement_meta']:
            draft.draftMeta.append(mta)
    # return draft_rows
    draft_dicts = [item.__dict__ for item in draft_rows]
    response = {
        'db_content':draft_dicts,
        'project_content':project_row
        }
    return response

def pin_point_token_in_draft(occurrences, draft_rows):#pylint: disable=too-many-locals,too-many-branches
    '''find out token's aligned portion in draft'''
    translations = []
    for occur, row in zip(occurrences, draft_rows):
        trans_offset = [None, None]
        new_token_offset = [None, None]
        status = None
        segments_of_interest = []
        for meta in row.draftMeta:
            token_offset = occur["offset"]
            segment_offset = meta[0]
            intersection = set(range(token_offset[0],token_offset[1])).intersection(
            range(segment_offset[0],segment_offset[1]))
            if len(intersection) > 0: # our area of interest overlaps with this segment
                segments_of_interest.append(meta)
                if meta[2] != "untranslated":
                    if token_offset[0] >= segment_offset[0]: #begining is this segment
                        trans_offset[0] = meta[1][0]
                        new_token_offset[0] = meta[0][0]
                    else: # begins before this segment
                        pass
                    if token_offset[1] <= segment_offset[1]: # ends in the segment
                        trans_offset[1] = meta[1][1]
                        new_token_offset[1] = meta[0][1]
                    else: # ends after this segment
                        pass
                    status = meta[2]
                else:
                    offset_diff = meta[1][0] - meta[0][0]
                    if token_offset[0] >= segment_offset[0]: #begining is this segment
                        trans_offset[0] = token_offset[0] + offset_diff
                        new_token_offset[0] = token_offset[0]
                    else: # begins before this segment
                        pass
                    if token_offset[1] <= segment_offset[1]: # ends in the segment
                        trans_offset[1] = token_offset[1] + offset_diff
                        new_token_offset[1] = token_offset[1]
                    else: # ends after this segment
                        pass
                    if status is None:
                        status = meta[2]
        new_metas = [
                    [[segments_of_interest[0][0][0],new_token_offset[0]],
                     [segments_of_interest[0][1][0], trans_offset[0]],
                     segments_of_interest[0][2]],
                    [new_token_offset, trans_offset, status],
                    [[new_token_offset[1], segments_of_interest[-1][0][1]],
                     [trans_offset[1], segments_of_interest[-1][1][1]],
                     segments_of_interest[-1][2]]
                    ]
        replacements = []
        for mta in new_metas:
            if mta[0][1] - mta[0][0] > 0:
                replacements.append(mta)
        res = {
                "token": row.sentence[new_token_offset[0]: new_token_offset[1]],
                "translation": row.draft[trans_offset[0]: trans_offset[1]],
                "occurrence": {
                    "sentenceId": occur["sentenceId"],
                    "offset": new_token_offset
                },
                "status": status,
                "meta_to_be_replaced":segments_of_interest,
                "replacement_meta":replacements
        }
        translations.append(res)
    return translations

#########################################################
def obtain_project_source(db_:Session, project_id, books=None, sentence_id_range=None,#pylint: disable=too-many-locals
    sentence_id_list=None, **kwargs):
    '''fetches all or selected source sentences from translation_sentences table'''
    with_draft= kwargs.get("with_draft",False)
    only_ids = kwargs.get("only_ids",False)
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    sentence_query = db_.query(db_models.TranslationDraft).filter(
        db_models.TranslationDraft.project_id == project_id)
    if books:
        book_filters = []
        for buk in books:
            book_id = db_.query(db_models.BibleBook.bookId).filter(
                db_models.BibleBook.bookCode==buk).first()
            if not book_id:
                raise NotAvailableException(f"Book, {buk}, not in database")
            book_filters.append(
                db_models.TranslationDraft.sentenceId.between(
                    book_id[0]*1000000, book_id[0]*1000000 + 999999))
        sentence_query = sentence_query.filter(or_(*book_filters))
    elif sentence_id_range:
        sentence_query = sentence_query.filter(
            db_models.TranslationDraft.sentenceId.between(
                sentence_id_range[0],sentence_id_range[1]))
    elif sentence_id_list:
        sentence_query = sentence_query.filter(
            db_models.TranslationDraft.sentenceId.in_(sentence_id_list))
    draft_rows = sentence_query.order_by(db_models.TranslationDraft.sentenceId).all()
    if only_ids:
        result = []
        for row in draft_rows:
            obj = {"sentenceId": row.sentenceId,
                "surrogateId":row.surrogateId}
            result.append(obj)
    elif with_draft:
        result =  draft_rows
    else:
        result = []
        for row in draft_rows:
            obj = {"sentenceId": row.sentenceId,
                "surrogateId":row.surrogateId,"sentence":row.sentence}
            result.append(obj)
    response = {
        'db_content':result,
        'project_content':project_row
        }
    return response

def remove_project_sentence(db_, project_id, sentence_id,user_id):
    '''To remove a sentence'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException(f"Project with id, {project_id}, not found")
    sentence_row = db_.query(db_models.TranslationDraft).filter(
        db_models.TranslationDraft.project_id == project_id,
        db_models.TranslationDraft.sentenceId == sentence_id).first()
    if not sentence_row:
        raise NotAvailableException(f"Sentence with id {sentence_id} not found")
    # if user_id == current_user:
    #     raise PermissionException("A user cannot remove oneself from a project.")
    db_.delete(sentence_row)
    project_row.updatedUser = user_id
    project_row.updateTime = datetime.datetime.now(ist_timezone).strftime('%Y-%m-%d %H:%M:%S')
    # db_.commit()
    response = {
        "db_content": sentence_row,
        "project_content": project_row
    }
    return response
