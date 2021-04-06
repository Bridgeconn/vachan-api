''' Place to define all data processing and Database CRUD operations 
related to NLP operations and translation apps'''

import re
import os
import glob
import json
from datetime import datetime
from math import floor, ceil
import pygtrie
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

#pylint: disable=E0401
#pylint gives import error if not relative import is used. But app(uvicorn) doesn't accept it

from crud import utils
import db_models
from logger import log
from custom_exceptions import NotAvailableException, TypeException
from schemas_nlp import TranslationDocumentType

###################### Tokenization ######################
def build_memory_trie(translation_memory):
    '''form a trie from a list of known tokens in a source language, to be used for tokenization''' 
    memory_trie = pygtrie.StringTrie()
    space_pattern = re.compile(r'\s+')
    for token in translation_memory:
        key = re.sub(space_pattern,'/', token[0])
        memory_trie[key] = 0
    return memory_trie

mock_translation_memory = ["जीवन के वचन", "जीवन का", "अपनी आँखों से देखा", "पिता के साथ",
                          "यीशु मसीह", "परमेश्‍वर ज्योति", "झूठा ठहराते",
                          "Here is it", "hare", "no"]

def find_phrases(text, stop_words, include_phrases=True):
    '''try forming phrases as <preposition stop word>* <content word> <postposition stop word>*'''
    words = text.split()
    if not include_phrases:
        return words
    if not isinstance(stop_words, dict):
        stop_words = stop_words.__dict__
    phrases = []
    current_phrase = ''
    state = 'pre'
    i = 0
    while i < len(words):
        word = words[i]
        if state == 'pre':
            if word in stop_words['prepositions']:
                current_phrase += ' '+ word # adds prepostion, staying in 'pre' state
            else:
                current_phrase += ' '+ word # adds one content word and goes to 'post' state
                state = 'post'
        elif state == 'post':
            if word in stop_words['postpositions']:
                current_phrase += ' '+ word # adds postposition, staying in 'post' state
            else:
                phrases.append(current_phrase.strip()) # stops the phrase building
                current_phrase = word
                if word in stop_words['prepositions']:
                    state = 'pre'
                else:
                    state = 'post'
        i += 1
    phrases.append(current_phrase.strip())
    return phrases


def tokenize(db_:Session, src_lang, sent_list, use_translation_memory=True, include_phrases=True,#pylint: disable=too-many-branches, disable=too-many-locals, disable=too-many-arguments
    include_stopwords=False, punctuations=None, stop_words=None):
    '''Get phrase and single word tokens and their occurances from input sentence list.
    Performs tokenization using two knowledge sources: translation memory and stopwords list
    input: [(sent_id, sent_text), (sent_id, sent_text), ...]
    output: {"token": [(sent_id, start_offset, end_offset),
                            (sent_id, start_offset, end_offset)..],
             "token": [(sent_id, start_offset, end_offset),
                            (sent_id, start_offset, end_offset)..], ...}'''
    unique_tokens = {}
    if stop_words is None:
        stop_words = utils.stopwords(src_lang)
    if punctuations is None:
        punctuations = utils.punctuations()+utils.numbers()
    # fetch all known tokens for the language and build a trie with it
    # We do this fresh for every tokenization request. Can be optimized
    if use_translation_memory:
        translation_memory = db_.query(db_models.TranslationMemory.token).filter(
            db_models.TranslationMemory.source_language.has(code=src_lang)).all()
        memory_trie = build_memory_trie(translation_memory)
    for sent in sent_list:
        if not isinstance(sent, dict):
            sent = sent.__dict__
        phrases = []
        text = re.sub(r'[\n\r]+', ' ', sent['sentence'])
        #first split the text into chunks based on punctuations
        chunks = [chunk.strip() for chunk in re.split(r'['+"".join(punctuations)+']+', text)]
        updated_chunks = []
        if use_translation_memory:
            for chunk in chunks:
                #search the trie to get the longest matching phrases known to us
                temp = chunk
                new_chunks = ['']
                while temp != "":
                    key = '/'.join(temp.split())
                    lngst = memory_trie.longest_prefix(key)
                    if lngst.key is not None:
                        new_chunks.append("###"+lngst.key.replace('/',' '))
                        temp = temp[len(lngst.key):]
                        new_chunks.append('')
                    else:
                        if " " in temp:
                            indx = temp.index(' ')
                            new_chunks[-1] += temp[:indx+1]
                            temp = temp[indx+1:]
                        else:
                            new_chunks[-1] += temp
                            temp = ""
                updated_chunks += new_chunks
            chunks = [ chk.strip() for chk in updated_chunks if chk.strip() != '']       
        for chunk in chunks:
            # from the left out words in above step, try forming phrases 
            # as <preposition stop word>* <content word> <postposition stop word>* 
            if chunk.startswith('###'):
                phrases.append(chunk.replace("###",""))
            else:
                phrases+= find_phrases(chunk,stop_words, include_phrases)
        start = 0
        if not isinstance(stop_words, dict):
            stop_words = stop_words.__dict__
        sw_list = stop_words['prepositions']+stop_words['postpositions']
        for phrase in phrases:
            if phrase.strip() == '':
                continue
            if (not include_stopwords) and phrase in sw_list:
                continue
            offset = sent['sentence'].find(phrase, start)
            if offset == -1:
                raise NotAvailableException("Tokenization: token, %s, not found in sentence: %s" %(
                    phrase, sent['sentence']))
            start = offset+1
            if phrase not in unique_tokens:
                unique_tokens[phrase] = {
                "occurrences":[{"sentenceId":sent['sentenceId'],
                "offset":[offset, offset+len(phrase)]}],
                "translations":[]}
            else: 
                unique_tokens[phrase]["occurrences"].append(
                    {"sentenceId":sent['sentenceId'], "offset":[offset, offset+len(phrase)]})
    return unique_tokens


def get_generic_tokens(db_:Session, src_language, sentence_list, trg_language=None,
    punctuations=None, stopwords=None,
    use_translation_memory=True, include_phrases=True, include_stopwords=False):
    '''tokenize the input sentences and return token list with details'''
    if isinstance(src_language, str):
        language_code = src_language
        src_language = db_.query(db_models.Language).filter(
            db_models.Language.code == language_code).first()
        if not src_language:
            raise NotAvailableException("Language, %s, not present in DB"%language_code)
    if isinstance(trg_language, str):
        language_code = trg_language
        trg_language = db_.query(db_models.Language).filter(
            db_models.Language.code == language_code).first()
        if not trg_language:
            raise NotAvailableException("Language, %s, not present in DB"%language_code)
    args = {"db_":db_, "src_lang":src_language.code, "sent_list":sentence_list,
        "use_translation_memory":use_translation_memory, "include_phrases":include_phrases,
        "include_stopwords":include_stopwords}
    if stopwords is not None:
        args['stop_words'] = stopwords
    if punctuations is not None:
        args['punctuations'] = punctuations
    tokens = tokenize(**args)
    result = []
    for token in tokens:
        obj = tokens[token]
        obj['token'] = token
        known_info = []
        info_query = db_.query(db_models.TranslationMemory).filter(
                db_models.TranslationMemory.source_lang_id == src_language.languageId,
                db_models.TranslationMemory.token == token)
        if trg_language:
            info_query = info_query.filter(
                or_(db_models.TranslationMemory.target_lang_id == trg_language.languageId,
                    db_models.TranslationMemory.metaData is not None)
                )
        else:
            info_query = info_query.filter(db_models.TranslationMemory.metaData is not None)
        known_info = info_query.all()
        if len(known_info)>0:
            for mem in known_info:
                if trg_language and mem.target_lang_id == trg_language.languageId:
                    obj['translations'] = mem.translations
                    obj['metaData'] = mem.metaData
                    break
                if "metaData" not in obj:
                    obj['metaData'] = mem.metaData
        result.append(obj)
    return result

def get_agmt_tokens(db_:Session, project_id, books, sentence_id_range, sentence_id_list, #pylint: disable=too-many-arguments disable=too-many-locals
    use_translation_memory=True, include_phrases=True, include_stopwords=False):
    '''Get the selected verses from drafts table and tokenize them'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    sentences = obtain_agmt_source(db_, project_id, books, sentence_id_range,sentence_id_list)
    args = {"db_":db_, "src_language":project_row.sourceLanguage, "sentence_list":sentences,
        'trg_language':project_row.targetLanguage,
        "use_translation_memory":use_translation_memory, "include_phrases":include_phrases,
        "include_stopwords":include_stopwords}
    if "stopwords" in project_row.metaData:
        args['stopwords'] = project_row.metaData['stopwords']
    if "punctuations" in project_row.metaData:
        args['punctuations'] = project_row.metaData['punctuations']
    return get_generic_tokens( **args)


###################### Token replacement translation ######################
def replace_token(source, token_offset, translation, draft="", draft_meta=[], tag="confirmed"): #pylint: disable=too-many-arguments, disable=too-many-locals, disable=W0102
    '''make a token replacement and return updated sentence and draft_meta'''
    trans_length = len(translation)
    updated_meta = []
    updated_draft = ""
    translation_offset = [None, None]
    if draft_meta is None or len(draft_meta) == 0:
        draft = source
        draft_meta = [((0,len(source)), (0,len(source)), "untranslated")]
    for meta in draft_meta:
        tkn_offset = meta[0]
        trans_offset = meta[1]
        status = meta[2]
        intersection = set(range(token_offset[0],token_offset[1])).intersection(
            range(tkn_offset[0],tkn_offset[1]))
        if len(intersection) > 0: # our area of interest overlaps with this segment 
            if token_offset[0] == tkn_offset[0]: #begining is same
                translation_offset[0] = trans_offset[0]
                updated_draft += translation
            elif token_offset[0] > tkn_offset[0]: # begins within this segment
                updated_draft += source[tkn_offset[0]: token_offset[0]]
                new_seg_len = token_offset[0] - tkn_offset[0]
                updated_meta.append(((tkn_offset[0], token_offset[0]),
                    (trans_offset[0], trans_offset[0]+new_seg_len),"untranslated"))
                translation_offset[0] = trans_offset[0]+new_seg_len
                updated_draft += translation
            else: # begins before this segment
                pass
            if token_offset[1] == tkn_offset[1]: # ending is the same
                translation_offset[1] = translation_offset[0]+trans_length
                updated_meta.append((token_offset, translation_offset, tag))
                offset_diff = translation_offset[1] - trans_offset[1]
            elif token_offset[1] < tkn_offset[1]: # ends within this segment
                trailing_seg = source[token_offset[1]: tkn_offset[1]]
                translation_offset[1] = translation_offset[0]+trans_length
                updated_meta.append((token_offset, translation_offset, tag))
                updated_draft += trailing_seg
                updated_meta.append(((token_offset[1], tkn_offset[1]),
                    (translation_offset[1],translation_offset[1]+len(trailing_seg)),
                    "untranslated"))
                offset_diff = translation_offset[1]+len(trailing_seg) - trans_offset[1]
            else: # ends after this segment
                pass
        elif tkn_offset[1] < token_offset[1]: # our area of interest come after this segment
            updated_draft += draft[trans_offset[0]: trans_offset[1]]
            updated_meta.append(meta)
        else: # our area of interest was before this segment
            updated_draft += draft[trans_offset[0]: trans_offset[1]]
            updated_meta.append((tkn_offset,
                (trans_offset[0]+offset_diff, trans_offset[1]+offset_diff), status))
    return updated_draft, updated_meta

def replace_bulk_tokens(db_, sentence_list, token_translations, src_code, trg_code, use_data=True):
    '''Substitute tokens with provided trabslations and return drafts and draftMetas'''
    source = db_.query(db_models.Language).filter(
        db_models.Language.code == src_code).first()
    if not source:
        raise NotAvailableException("Language code, %s, not in DB. Please create if required"%src_code)
    target = db_.query(db_models.Language).filter(
        db_models.Language.code == trg_code).first()
    if not source:
        raise NotAvailableException("Language code, %s, not in DB. Please create if required"%trg_code)
    updated_sentences = {sent.sentenceId:sent for sent in sentence_list}
    for token in token_translations:
        for occur in token.occurrences:
            draft_row = updated_sentences[occur.sentenceId]
            if not draft_row:
                raise NotAvailableException("Sentence id, %s, not found in the sentence_list"
                    %occur.sentenceId)
            draft, meta = replace_token(draft_row.sentence, occur.offset, token.translation,
                draft_row.draft, draft_row.draftMeta)
            draft_row.draft = draft
            draft_row.draftMeta = meta
            updated_sentences[occur.sentenceId]  = draft_row
        if use_data:
            memory_row = db_.query(db_models.TranslationMemory).filter(
                db_models.TranslationMemory.source_lang_id == source.languageId,
                db_models.TranslationMemory.target_lang_id == target.languageId,
                db_models.TranslationMemory.token == token.token).first()
            if not memory_row:
                row_args = {"source_lang_id":source.languageId,
                    "target_lang_id":target.languageId,
                    "token":token.token,
                    "translations":{token.translation:{
                        "frequency": len(token.occurrences)}}}
                other_lang_metadata = db_.query(db_models.TranslationMemory.metaData).filter(
                    db_models.TranslationMemory.source_lang_id == source.languageId,
                    db_models.TranslationMemory.token == token.token).first()
                if other_lang_metadata:
                    row_args['metaData'] = other_lang_metadata[0]
                memory_row = db_models.TranslationMemory(**row_args)
                db_.add(memory_row)
                db_.commit()
            else:
                if token.translation not in memory_row.translations:
                    memory_row.translations[token.translation] = {
                        "frequency": len(token.occurrences)}
                    flag_modified(memory_row, "translations")
                    db_.add(memory_row)
                    db_.commit()
                else:
                    old_freq = memory_row.translations[token.translation]['frequency']
                    memory_row.translations[token.translation] = {
                        "frequency": old_freq+len(token.occurrences)}
                    flag_modified(memory_row, "translations")
                    db_.add(memory_row)
                    db_.commit()
    result = [updated_sentences[key] for key in updated_sentences]
    return result


def save_agmt_translations(db_, project_id, token_translations, return_drafts=True, user_id=None):
    '''replace tokens with provided translation in the drafts and update translation memory'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not present"%project_id)
    use_data = True
    if project_row.metaData is not None and "useDataForLearning" in project_row.metaData:
        use_data = project_row.metaData['useDataForLearning']
    db_content = []
    for token in token_translations:
        for occur in token.occurrences:
            draft_row = db_.query(db_models.TranslationDraft).filter(
                db_models.TranslationDraft.project_id == project_id,
                db_models.TranslationDraft.sentenceId == occur.sentenceId).first()
            if not draft_row:
                raise NotAvailableException("Sentence id, %s, not found for the selected project"
                    %occur.sentenceId)
            draft, meta = replace_token(draft_row.sentence, occur.offset, token.translation,
                draft_row.draft, draft_row.draftMeta)
            draft_row.draft = draft
            draft_row.draftMeta = meta
            flag_modified(draft_row, "draftMeta")
            draft_row.updatedUser = user_id
            db_content.append(draft_row)
        if use_data:
            memory_row = db_.query(db_models.TranslationMemory).filter(
                db_models.TranslationMemory.source_lang_id == project_row.source_lang_id,
                db_models.TranslationMemory.target_lang_id == project_row.target_lang_id,
                db_models.TranslationMemory.token == token.token).first()
            if not memory_row:
                row_args = {"source_lang_id":project_row.source_lang_id,
                    "target_lang_id":project_row.target_lang_id,
                    "token":token.token,
                    "translations":{token.translation:{
                        "frequency": len(token.occurrences)}}}
                other_lang_metadata = db_.query(db_models.TranslationMemory.metaData).filter(
                    db_models.TranslationMemory.source_lang_id == project_row.source_lang_id,
                    db_models.TranslationMemory.token == token.token).first()
                if other_lang_metadata:
                    row_args['metaData'] = other_lang_metadata[0]
                memory_row = db_models.TranslationMemory(**row_args)
                db_.add(memory_row)
                db_.commit()
            else:
                if token.translation not in memory_row.translations:
                    memory_row.translations[token.translation] = {
                        "frequency": len(token.occurrences)}
                    flag_modified(memory_row, "translations")
                    db_.add(memory_row)
                    db_.commit()
                else:
                    old_freq = memory_row.translations[token.translation]['frequency']
                    memory_row.translations[token.translation] = {
                        "frequency": old_freq+len(token.occurrences)}
                    flag_modified(memory_row, "translations")
                    db_.add(memory_row)
                    db_.commit()
    project_row.updatedUser = user_id
    db_.add_all(db_content)
    db_.add(project_row)
    db_.commit()
    if return_drafts:
        result = set(db_content)
        return sorted(result, key=lambda x: x.sentenceId)
    return None



###################### AgMT Project Mangement ######################
def create_agmt_project(db_:Session, project, user_id=None):
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
    db_content = db_models.TranslationProject(
        projectName=utils.normalize_unicode(project.projectName),
        source_lang_id=source.languageId,
        target_lang_id=target.languageId,
        documentFormat=project.documentFormat.value,
        active=project.active,
        createdUser=user_id,
        updatedUser=user_id,
        metaData=meta
        )
    db_.add(db_content)
    db_.flush()
    db_content2 = db_models.TranslationProjectUser(
        project_id=db_content.projectId,
        userId=user_id,
        userRole="owner",
        active=True)
    db_.add(db_content2)
    db_.commit()
    return db_content

def update_agmt_project(db_:Session, project_obj, user_id=None): #pylint: disable=too-many-branches disable=too-many-locals disable=too-many-statements
    '''Either activate or deactivate a project or Add more books to a project,
    adding all new verses to the drafts table'''
    project_row = db_.query(db_models.TranslationProject).get(project_obj.projectId)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_obj.projectId)
    new_books = []
    if project_obj.selectedBooks: 
        if not project_obj.selectedBooks.bible.endswith("_"+db_models.ContentTypeName.bible.value):
            raise TypeException("Operation only supported on Bible tables")
        if not project_obj.selectedBooks.bible+"_cleaned" in db_models.dynamicTables:
            raise NotAvailableException("Bible, %s, not found"%project_obj.selectedBooks.bible)
        bible_cls = db_models.dynamicTables[project_obj.selectedBooks.bible+"_cleaned"]
        verse_query = db_.query(bible_cls)
        for buk in project_obj.selectedBooks.books:
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == buk).first()
            if not book:
                raise NotAvailableException("Book, %s, not found in database" %buk)
            new_books.append(buk)
            refid_start = book.bookId * 1000000
            refid_end = refid_start + 999999
            verses = verse_query.filter(
                bible_cls.refId >= refid_start, bible_cls.refId <= refid_end).all()
            if len(verses) == 0:
                raise NotAvailableException("Book, %s, is empty for %s"%(
                    buk, project_obj.selectedBooks.bible))
            for verse in verses:
                sent = utils.normalize_unicode(verse.verseText)
                offsets = [0, len(sent)]
                draft_row = db_models.TranslationDraft(
                    project_id=project_obj.projectId,
                    sentenceId=verse.refId,
                    surrogateId=buk+","+str(verse.chapter)+","+str(verse.verseNumber),
                    sentence=sent,
                    draft=sent,
                    draftMeta=[[offsets,offsets,"untranslated"]], 
                    updatedUser=user_id)
                db_.add(draft_row)
    if project_obj.uploadedBooks:
        for usfm in project_obj.uploadedBooks:
            usfm_json = utils.parse_usfm(usfm)
            book_code = usfm_json['book']['bookCode'].lower()
            book = db_.query(db_models.BibleBook).filter(
                db_models.BibleBook.bookCode == book_code).first()
            if not book:
                raise NotAvailableException("Book, %s, not found in database"% book_code)
            new_books.append(book_code)
            for chap in usfm_json['chapters']:
                chapter_number = chap['chapterNumber']
                for cont in chap['contents']:
                    if "verseNumber" in cont:
                        verse_number = cont['verseNumber']
                        verse_text = cont['verseText']
                        offsets = [0, len(verse_text)]
                        draft_row = db_models.TranslationDraft(
                            project_id=project_obj.projectId,
                            sentenceId=book.bookId*1000000+
                                int(chapter_number)*1000+int(verse_number),
                            surrogateId=book_code+","+str(chapter_number)+","+str(verse_number),
                            sentence=verse_text,
                            draft=verse_text,
                            draftMeta=[[offsets,offsets,'untranslated']],
                            updatedUser=user_id)
                        db_.add(draft_row)
    db_.commit()
    db_.expire_all()
    if project_obj.active is not None:
        project_row.active = project_obj.active
    if project_obj.useDataForLearning is not None:
        project_row.metaData['useDataForLearning'] = project_obj.useDataForLearning
    if project_obj.stopwords:
        project_row.metaData['stopwords'] = project_obj.stopwords.__dict__
    if project_obj.punctuations:
        project_row.metaData['punctuations'] = project_obj.punctuations
    project_row.updatedUser = user_id
    if len(new_books) > 0:
        project_row.metaData['books'] += new_books
    flag_modified(project_row, "metaData")
    db_.add(project_row)
    db_.commit()
    db_.refresh(project_row)
    return project_row

def get_agmt_projects(db_:Session, project_name=None, source_language=None, target_language=None, #pylint: disable=too-many-arguments
    active=True, user_id=None):
    '''Fetch autographa projects as per the query options'''
    query = db_.query(db_models.TranslationProject)
    if project_name:
        query = query.filter(
            db_models.TranslationProject.projectName == utils.normalize_unicode(project_name))
    if source_language:
        source = db_.query(db_models.Language).filter(db_models.Language.code == source_language
            ).first()
        if not source:
            raise NotAvailableException("Language, %s, not found"%source_language)
        query = query.filter(db_models.TranslationProject.source_lang_id == source.languageId)
    if target_language:
        target = db_.query(db_models.Language).filter(db_models.Language.code == target_language
            ).first()
        if not target:
            raise NotAvailableException("Language, %s, not found"%target_language)
        query = query.filter(db_models.TranslationProject.target_lang_id == target.languageId)
    if user_id:
        query = query.filter(db_models.TranslationProject.users.any(userId=user_id))
    return query.filter(db_models.TranslationProject.active == active).all()

def add_agmt_user(db_:Session, project_id, user_id, current_user=None):
    '''Add an additional user(not the created user) to a project, in translation_project_users'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    db_content = db_models.TranslationProjectUser(
        project_id=project_id,
        userId=user_id,
        userRole='member',
        active=True)
    db_.add(db_content)
    project_row.updatedUser = current_user
    db_.commit()
    return db_content 

def update_agmt_user(db_, user_obj, current_user=10101):
    '''Change role, active status or metadata of user in a project'''
    user_row = db_.query(db_models.TranslationProjectUser).filter(
        db_models.TranslationProjectUser.project_id == user_obj.project_id,
        db_models.TranslationProjectUser.userId == user_obj.userId).first()
    if not user_row:
        raise NotAvailableException("User-project pair not found")
    if user_obj.userRole:
        user_row. userRole = user_obj.userRole
    if user_obj.metaData:
        user_row.metaData = user_obj.metaData
        flag_modified(user_row,'metaData')
    if user_obj.active is not None:
        user_row.active = user_obj.active
    user_row.project.updatedUser = current_user
    db_.add(user_row)
    db_.commit()
    return user_row

def obtain_agmt_source(db_:Session, project_id, books=None, sentence_id_list=None, sentence_id_range=None,
    with_draft=False, fill_suggestions=False):
    '''fetches all or selected source sentences from translation_sentences table'''
    sentence_query = db_.query(db_models.TranslationDraft).filter(
        db_models.TranslationDraft.project_id == project_id)
    if books:
        book_filters = []
        for buk in books:
            book_id = db_.query(db_models.BibleBook.bookId).filter(
                db_models.BibleBook.bookCode==buk).first()
            if not book_id:
                raise NotAvailableException("Book, %s, not in database"%buk)
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
    draft_rows = sentence_query.all()
    if with_draft:
        return draft_rows
    result = []
    for row in draft_rows:
        obj = {"sentenceId": row.sentenceId, "sentence":row.sentence}
        result.append(obj)
    return result

def obtain_agmt_draft(db_:Session, project_id, books, sentence_id_list, sentence_id_range,
    output_format="usfm"):
    '''generate draft for selected sentences as usfm or json'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    draft_rows = obtain_agmt_source(db_, project_id, books, sentence_id_list, sentence_id_range,
        with_draft=True)
    if output_format.value == "usfm":
        return create_usfm(draft_rows)
    if output_format.value == 'alignment-json':
        return export_to_json(project_row.sourceLanguage,
            project_row.targetLanguage, draft_rows, None)
    raise TypeException("Unsupported output format: %s"%output_format)

def obtain_agmt_progress(db_, project_id, books, sentence_id_list, sentence_id_range):
    '''Calculate project translation progress in terms of how much of draft is translated'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    draft_rows = obtain_agmt_source(db_, project_id, books, sentence_id_list, sentence_id_range,
        with_draft=True)
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
    result = {"confirmed": confirmed_length/total_length,
        "suggestion": suggestions_length/total_length,
        "untranslated": untranslated_length/total_length}
    return result


###################### Suggestions ######################
suggestion_trie_in_mem = {}
SUGGESTION_DATA_PATH = 'models/suggestion_data'
SUGGESTION_TRIE_PATH = 'models/suggestion_tries'
WINDOW_SIZE = 5

def extract_context(token, offset, sentence, window_size=WINDOW_SIZE,
    punctuations=utils.punctuations()+utils.numbers()):
    '''return token index and context array'''
    punct_pattern = re.compile('['+''.join(punctuations)+']')
    front = sentence[:offset[0]]
    rear = sentence[offset[1]:]
    front = re.sub(punct_pattern, "", front)
    rear = re.sub(punct_pattern, "", rear)
    front = front.split()
    rear = rear.split()
    if len(front) >= window_size/2:
        front  = front[-floor(window_size/2):]
    if len(rear) >= window_size/2:
        rear = rear[:ceil(window_size/2)]
    index = len(front)
    context = front + [token] + rear
    return index, context

def get_training_data_from_drafts(sentence_list, window_size=WINDOW_SIZE):
    '''identify user confirmed token translations and their contexts'''
    training_data = []
    for row in sentence_list:
        source = row.sentence
        for meta in row.draftMeta:
            if meta[2] == "confirmed":
                token = source[meta[0][0]:meta[0][1]]
                index, context = extract_context(token, meta[0], source, window_size)
                trans = row.draft[meta[1][0]:meta[1][1]]
                training_data.append((index, context, trans))
    return training_data

def find_pharses_from_alignments(src_tok_list, trg_tok_list, align_pairs):
    '''Takes one sentence's alignments and finds aligned phrases
    input: src-trg token alignments, a list of {"sourceTokenIndex", "targetTokenIndex"} pairs
    output: aligned multi-token pharses, if available, based on one to many mappings in input'''
    phrases = []
    seen_src = []
    seen_trg = []
    for align in align_pairs:
        if (align.sourceTokenIndex not in seen_src and
            align.targetTokenIndex not in seen_trg): #New single token entry
            new_token = src_tok_list[align.sourceTokenIndex]
            new_translation = trg_tok_list[align.targetTokenIndex]
            phrases.append( {"src_indices": [align.sourceTokenIndex],
                "trg_indices":[align.targetTokenIndex],
                "translation": new_translation, "token": new_token})
        else:
            if align.sourceTokenIndex in seen_src: # Some other trg word is aleady aligned to src
                old_align = None
                for obj in phrases:
                    if align.sourceTokenIndex in obj['src_indices']:
                        old_align = obj
                        break
                if not old_align:
                    raise NotAvailableException("Can't find source token, %s, in %s"%(
                        src_tok_list[align.sourceTokenIndex], phrases))
                trg_indices = sorted(old_align['trg_indices']+ [align.targetTokenIndex])
                translation = " ".join(trg_tok_list[trg_indices[0]:trg_indices[-1]+1])
                phrases.remove(old_align)
                old_align['trg_indices'] = trg_indices
                old_align['translation'] = translation
                phrases.append(old_align)
            if align.targetTokenIndex in seen_trg: # some other src is already aligned to this trg
                old_align = None
                for obj in phrases:
                    if align.targetTokenIndex in obj['trg_indices']:
                        old_align = obj
                        break
                if not old_align:
                    raise NotAvailableException("Cant find target token, %s, in %s"%(
                        trg_tok_list[align.targetTokenIndex], phrases))
                src_indices = sorted(old_align['src_indices']+ [align.sourceTokenIndex])
                new_token = " ".join(src_tok_list[src_indices[0]:src_indices[-1]+1])
                phrases.remove(old_align)
                old_align['src_indices'] = src_indices
                old_align['token'] = new_token
                phrases.append(old_align)
        seen_src.append(align.sourceTokenIndex)
        seen_trg.append(align.targetTokenIndex)
    for obj in phrases: #check and eliminate non-continuous phrase alignments
        deleted = False
        for i in range(len(obj['src_indices'])-1):
            if obj['src_indices'][i] + 1 !=  obj['src_indices'][i+1]:
                log.warning("Eliminating non-continuous src phrase:%s, in %s",
                    obj['src_indices'], src_tok_list)
                phrases.remove(obj)
                deleted = True
        if deleted:
            continue
        for i in range(len(obj['trg_indices'])-1):
            if obj['trg_indices'][i] + 1 !=  obj['src_indices'][i+1]:
                log.warning("Eliminating non-continuous trg phrase:%s, in %s",
                    obj['trg_indices'], trg_tok_list)
                phrases.remove(obj)
    return phrases


def alignments_to_trainingdata(db_:Session, src_lang, trg_lang, alignment_list,
    user_id=None, append=True, window_size=WINDOW_SIZE, output_dir=SUGGESTION_DATA_PATH):
    '''Convert alignments to training data for suggestions module and also add to translation_memory
    input format: [(<src sent>,<trg_sent>,[(0-0), (1-3),(2-1),..]]
    output: <index>\t<context ayrray>\t<translation>'''
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = datetime.now().strftime("%d:%m:%Y-%H:%M:%S")
    output_path = output_dir+"/"+src_lang+"-"+trg_lang+"-"+str(user_id)+"-"+\
        "-"+timestamp+".json"
    output_file = open(output_path, "w", encoding='utf8')
    dict_data = {}
    sugg_data = []
    for sent in alignment_list:
        src_len = len(sent.sourceTokenList)
        phrases = find_pharses_from_alignments(sent.sourceTokenList, sent.targetTokenList,
            sent.alignedTokens)
        for obj in phrases:
            ## prepare data for translation memory/gloss
            if obj["token"] in dict_data:
                dict_data[obj["token"]]['translations'].append(obj['translation'])
            else:
                dict_data[obj["token"]] = {"token": obj["token"], 
                "translations":[obj['translation']]}
            ## prepare data for suggestions trie
            end = obj['src_indices'][0]
            if end == 0:
                pre_context = []
            elif end-ceil(window_size/2) >= 0:
                start = end-ceil(WINDOW_SIZE/2)
                pre_context = sent.sourceTokenList[start:end]
            else:
                pre_context = sent.sourceTokenList[0:end]
            start = obj['src_indices'][-1]+1 
            if start == src_len:
                post_context = []
            elif start + floor(window_size/2) <= src_len:
                end = start + floor(window_size/2)
                post_context = sent.sourceTokenList[start:end]
            else:
                post_context = sent.sourceTokenList[start:]
            context = pre_context + [obj['token']] + post_context
            sugg_data.append((len(pre_context), context, obj['translation']))
    new_trie = build_trie(sugg_data, default_val=0)
    sugg_json = {item[0]:item[1] for item in new_trie.items()}
    json.dump(sugg_json, output_file, ensure_ascii=False)
    output_file.close()    
    new_trie = rebuild_trie(db_, src_lang, trg_lang)
    suggestion_trie_in_mem[src_lang+"-"+trg_lang] = new_trie
    tw_data = add_to_translation_memory(db_, src_lang, trg_lang,
        [dict_data[key] for key in dict_data])
    return tw_data


def form_trie_keys(prefix, to_left, to_right, prev_keys, only_longest=True):
    '''build the trie tree recursively'''    
    keys = prev_keys
    node_a = node_b = None
    if len(to_left) > 0:
        node_a = '/L:'+to_left.pop(0)
    if len(to_right) > 0:
        node_b = '/R:'+to_right.pop(0)
    if node_a:
        key_left = prefix + node_a
        keys.append(key_left)
        keys = form_trie_keys(key_left, to_left.copy(), to_right.copy(), keys,only_longest)
    if node_b:
        key_right = prefix + node_b
        keys.append(key_right)
        keys = form_trie_keys(key_right, to_left.copy(), to_right.copy(), keys, only_longest)
    if node_a and node_b:
        key_both_1 = prefix + node_a + node_b
        key_both_2 = prefix + node_b + node_a
        keys.append(key_both_1)
        keys.append(key_both_2)
        keys = form_trie_keys(key_both_1, to_left.copy(), to_right.copy(), keys, only_longest)
        keys = form_trie_keys(key_both_2, to_left.copy(), to_right.copy(), keys, only_longest)
    sorted_keys = sorted(keys, key=lambda x:len(x), reverse=True)
    if not only_longest:
        return sorted_keys
    result = []
    prev_len = 0
    for res in sorted_keys:
        if len(res) < prev_len:
            break
        prev_len = len(res)
        result.append(res)
    return result

def build_trie(token_context__trans_list, default_val=None):
    '''Build a trie tree from scratch
    input: [(token,context_list, translation), ...]'''
    ttt = pygtrie.StringTrie()
    for item in token_context__trans_list:
        context = item[1]
        translation = item[2]
        if isinstance(item[0], str):
            token = item[0]
            token_index = context.index(token)
        elif isinstance(item[0], int):
            token_index = item[0]
            token = context[token_index]
        else:
            raise TypeException("Expects the token, as string, or index of token, as int,"+
                "in first field of input tuple")
        to_left = [context[i] for i in range(token_index-1, -1, -1)]
        to_right = context[token_index+1:]
        keys = form_trie_keys(token, to_left, to_right, [token])
        if default_val is None:
            val_update = 1/len(keys)
        else:
            val_update = default_val
        for key in keys:
            if ttt.has_key(key):
                value = t[key]
                if translation in value.keys():
                    value[translation] += val_update
                else:
                    value[translation] = val_update
                ttt[key] = value
            else:
                ttt[key] = {translation: val_update}
    return ttt

def rebuild_trie(db_, src, trg):
    '''Collect suggestions data from translation memory and traning data directory
    and rebuild the trie for language pair in memory'''
    db_sents = db_.query(db_models.TranslationDraft, db_models.TranslationProject).filter(
        db_models.TranslationProject.sourceLanguage.has(code = src),
        db_models.TranslationProject.targetLanguage.has(code = trg)).all()
    training_data = get_training_data_from_drafts([item[0] for item in db_sents])
    new_trie = build_trie(training_data)
    files_on_disc = glob.glob(SUGGESTION_DATA_PATH+'/'+src+"-"+trg+'*.json')
    for file in files_on_disc:
        with open(file, 'r') as json_file:
            log.warning("Using %s, to update %s-%s trie"%(file, src, trg))
            json_data = json.load(json_file)
            for key in json_data:
                new_trie[key] = json_data[key]
    return new_trie

def add_to_translation_memory(db_, src_lang, trg_lang, gloss_list):
    '''Add glossary data to translation memory'''
    if isinstance(src_lang, str):
        source_lang = db_.query(db_models.Language).filter(
            db_models.Language.code == src_lang).first()
        if not source_lang:
            raise NotAvailableException("Language, %s, not available"%src_lang)
    else:
        source_lang = src_lang
    if isinstance(trg_lang, str):
        target_lang = db_.query(db_models.Language).filter(
            db_models.Language.code == trg_lang).first()
        if not target_lang:
            raise NotAvailableException("Language, %s, not available"%trg_lang)
    else:
        target_lang = trg_lang
    db_content = []
    for gloss in gloss_list:
        if not isinstance(gloss, dict):
            gloss = gloss.__dict__
        gloss['token'] = utils.normalize_unicode(gloss['token'])
        token_row = db_.query(db_models.TranslationMemory).filter(
            db_models.TranslationMemory.source_lang_id == source_lang.languageId,
            db_models.TranslationMemory.target_lang_id == target_lang.languageId,
            db_models.TranslationMemory.token == gloss['token']).first()
        if token_row:
            if "translations" in gloss:
                for trans in gloss['translations']:
                    trans = utils.normalize_unicode(trans)
                    if trans not in token_row.translations:
                        #using 0, as this is data loaded from outside and not observed in usage
                        token_row.translations[trans] = {"frequency": 0} 
            if 'tokenMetaData' in gloss:
                if token_row.metaData is None:
                    token_row.metaData = {}
                for key in gloss['tokenMetaData']:
                    token_row.metaData[key] = gloss['tokenMetaData'][key]
                flag_modified(token_row, 'metaData')
        else:
            args = {"source_lang_id":source_lang.languageId,
                "target_lang_id": target_lang.languageId,
                "token":gloss['token'],
                "translations":{}}
            if "translations" in gloss:
                #using 0, as this is data loaded from outside and not observed in usage
                args['translations'] = {utils.normalize_unicode(val):{
                    "frequency":0} for val in gloss['translations']}
            if 'tokenMetaData' in gloss:
                args['metaData'] = gloss['tokenMetaData']
            token_row = db_models.TranslationMemory(**args)
        db_content.append(token_row)
    db_.add_all(db_content)
    db_.commit()
    for item in db_content:
        db_.refresh(item)
    return db_content

def get_gloss(db_:Session, index, context, source_lang, target_lang): # pylint: disable=too-many-locals
    '''find the context based translation suggestions(gloss) for a word.
    Makes use of the learned model(trie), for the lang pair, based on translation memory
    output format: [(translation1, score1), (translation2, score2), ...]'''
    if isinstance(index, int):
        word = context[index]
    elif isinstance(index, str):
        word = index
        index = context.index(word)
    to_left = [context[i] for i in range(index-1, -1, -1)]
    to_right = context[index+1:]
    keys = form_trie_keys(word, to_left, to_right, [word], False)
    if source_lang+"-"+target_lang in suggestion_trie_in_mem: # check if aleady loaded in memory
        tree = suggestion_trie_in_mem[source_lang+"-"+target_lang]
    else:  # build trie loading data from disk and DB 
        tree = rebuild_trie(db_, source_lang, target_lang)
    trans = {}
    total = 0
    for key in keys:
        if tree.has_subtrie(key) or tree.has_key(key):
            nodes = tree.values(key)
            level = len(key.split("/"))
            for nod in nodes:
                for sense in nod:
                    if sense in trans:
                        trans[sense] += nod[sense]*level*level
                    else:
                        trans[sense] = nod[sense]*level*level
                    total += nod[sense]
    sorted_trans = sorted(trans.items(), key=lambda x:x[1], reverse=True)
    scored_trans = [(sense[0],sense[1]/total) for sense in sorted_trans]
    return scored_trans

def glossary(db_:Session, source_language, target_language, token, context=None, token_offset=None):
    '''finds possible translation suggestion for a token'''
    if context is None:
        context = token
    if token_offset is None:
        start = context.index(token)
        token_offset= (start, start+len(token))
    index, context_list = extract_context(token, token_offset, context)
    suggs = get_gloss(db_, index, context_list, source_language, target_language)
    res = []
    for sug in suggs:
        res.append({"suggestion":sug[0], "score": sug[1]})
    return res

def auto_translate(db_, sentence_list, source_lang, target_lang, punctuations=None, stop_words=None):
    '''Attempts to tokenize the input sentence and replace each token with top suggestion.
    If draft_meta is provided indicating some portion of sentence is user translated, 
    then it is left untouched.
    Output is of the format [(sent_id, translated text, metadata)]
    metadata: List of (token_offsets, translation_offset, confirmed/suggestion/untranslated)'''
    # load corresponding trie for source and target if not already in memory

    args = {"db_":db_, "src_lang":source_lang, "include_stopwords":True}
    if punctuations:
        args['punctuations'] = punctuations
    if stop_words:
        args['stop_words'] = stop_words
    for sent in sentence_list:
        args['sent_list'] = [{"sentenceId":sent.sentenceId, "sentence":sent.sentence}]
        tokens = tokenize(**args)
        for token in tokens:
            for occurence in tokens[token]['occurrences']:
                offset = occurence['offset']
                index, context = extract_context(token, offset,
                    sent.sentence)
                suggestions = get_gloss(db_, index, context, source_lang, target_lang)
                if len(suggestions) > 0:
                    draft, meta = replace_token(sent.sentence, offset,
                        suggestions[0][0], sent.draft, sent.draftMeta, "suggestion")
                    sent.draft = draft
                    sent.draftMeta = meta
                elif (sent.draft is None or sent.draft == ''):
                    sent.draft = sent.sentence
                    offset = [0,len(sent.sentence)]
                    sent.draftMeta = [[offset, offset, "untranslated"]]
    return sentence_list

def agmt_suggest_translations(db_:Session, project_id, books, sentence_id_range, sentence_id_list,
    confirm_all=False):
    '''Tokenize and auto fill draft with top suggestions'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    draft_rows = obtain_agmt_source(db_, project_id, books, sentence_id_range,sentence_id_list,
        with_draft=True)
    if confirm_all:
        for row in draft_rows:
            for i, meta in enumerate(row.draftMeta):
                if meta[2] == "suggestion":
                    row.draftMeta[i][2] = "confirmed"
                    flag_modified(row, 'draftMeta')
        db_.commit()
        return draft_rows
    args = {"db_":db_, "sentence_list":draft_rows,
        "source_lang":project_row.sourceLanguage.code,
        "target_lang":project_row.targetLanguage.code}
    if "stopwords" in project_row.metaData:
        args['stop_words'] = project_row.metaData.stopwords
    if "punctuations" in project_row.metaData:
        args['punctuations'] = project_row.metaData.punctuations
    updated_drafts = auto_translate(**args)
    db_.add_all(updated_drafts)
    db_.commit()
    return updated_drafts

###################### Export and download ######################

def obtain_draft(db_:Session, sentence_list, doc_type):
    '''Convert input sentences to required format'''
    if doc_type == TranslationDocumentType.USFM:
        return create_usfm(sentence_list)
    if doc_type == TranslationDocumentType.JSON:
        return export_to_json(None,
            None, sentence_list, None)
    if doc_type == TranslationDocumentType.CSV:
        result = ''
        for sent in sentence_list:
            result += sent.surrogateId+","+sent.sentence+","+sent.draft+"\n"
        return result
    if doc_type == TranslationDocumentType.TEXT:
        punctuations=utils.punctuations()+utils.numbers()
        punct_pattern = re.compile('['+''.join(punctuations)+']')
        result = ''
        prev_id = None
        for sent in sentence_list:
            if prev_id is not None and sent.sentenceId-prev_id > 1:
                result += "\n"
            result += sent.draft
            if not re.match(punct_pattern, sent.draft[-1]):
                result += "."
            result += ' '
            prev_id = sent.sentenceId
        return result

def create_usfm(sent_drafts):
    '''Creates minimal USFM file with basic markers from the input verses list
    input: List of (bbbcccvvv, "generated translation")
    output: List of usfm files, one file per bible book'''
    book_start = '\\id {}\n'
    chapter_start = '\\c {}\n\\p\n'
    verse = '\\v {} {}'
    usfm_files = []
    file = ''
    prev_book = 0
    prev_chapter = 0
    book_code = ''
    sentences = sorted(sent_drafts, key=lambda x:x.sentenceId, reverse=False)
    for sent in sentences:
        if sent.sentenceId < 1001001 or sent.sentenceId > 66999999:
            raise TypeException("SentenceIds should be of bbbcccvvv pattern for creating USFM,"+
                "doesn't support %s"%sent.sentenceId)
        verse_num = sent.sentenceId % 1000
        chapter_num = int((sent.sentenceId /1000) % 1000)
        book_num = int(sent.sentenceId / 1000000)
        if book_num != prev_book:
            if file != '':
                usfm_files.append(file)
            book_code = utils.book_code(book_num)
            if book_code is None:
                raise NotAvailableException("Book number %s not a valid one" %book_num)
            file = book_start.format(book_code)
            prev_book = book_num
        if chapter_num != prev_chapter:
            file += chapter_start.format(chapter_num)
            prev_chapter = chapter_num
        file += verse.format(verse_num, sent.draft)
    if file != '':
        usfm_files.append(file)
    return usfm_files

def export_to_json(source_lang, target_lang, sentence_list, last_modified):
    '''input sentence_list is List of (sent_id, source_sent, draft, draft_meta)
    output:json in alignment format'''
    json_output = {#"conformsTo": "alignment-0.1",
                   "metadata":{
                      "resources":{
                          "r0": {
                            # "languageCode": source_lang.code,
                            # "name": source_lang.language,
                            # "version": "0.1"
                          },
                          "r1": {
                            # "languageCode": target_lang.code,
                            # "name": target_lang.language,
                            # "version": "9"
                          }
                      },
                      "modified": last_modified
                   },
                   "segments": []
                  }
    if source_lang:
        json_output['metaData']['resources']['r0'] = {"languageCode": source_lang.code,
            "name": source_lang.language}
    if target_lang:
        json_output['metaData']['resources']['r1'] = {"languageCode": target_lang.code,
            "name": target_lang.language}
    for row in sentence_list:
        row_obj = {"resources":{
                        "r0":{
                            "text":row.sentence,
                            "tokens":[],
                            "metadata": {"contextId":row.surrogateId}
                        },
                        "r1":{
                            "text": row.draft,
                            "tokens":[],
                            "metadata": {"contextId":row.surrogateId}
                        }
                    },
                   "alignments":[]
                  }
        for i,meta in enumerate(row.draftMeta):
            algmt = {
              "r0": [i],
              "r1": [i],
              "status": meta[2]
            }
            src_token = row.sentence[meta[0][0]:meta[0][1]]
            trg_token = row.draft[meta[1][0]:meta[1][1]]
            row_obj['resources']['r0']['tokens'].append(src_token)
            row_obj['resources']['r1']['tokens'].append(trg_token)
            if meta[2] == "confirmed":
                algmt['score'] = 1
                algmt['verfied'] = True
            elif meta[2] == "suggestion":
                algmt['score'] = 0.5
                algmt['verified'] = False
            else:
                algmt['score'] = 0
                algmt['verified'] = False
            row_obj['alignments'].append(algmt)
        json_output['segments'].append(row_obj)
    return json_output
