''' Place to define all data processing and Database CRUD operations 
related to NLP operations and translation apps'''

import re
import json
import os
import pickle
from math import floor, ceil
import pygtrie
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

#pylint: disable=E0401
#pylint gives import error if not relative import is used. But app(uvicorn) doesn't accept it

from crud import utils
import db_models
from custom_exceptions import NotAvailableException, TypeException

def find_phrases(text, stop_words, include_phrases=True):
    '''try forming phrases as <preposition stop word>* <content word> <postposition stop word>*'''
    words = text.split()
    if not include_phrases:
        return words
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

def tokenize(db_:Session, src_lang, sent_list, use_translation_memory=True, include_phrases=True,#pylint: disable=too-many-branches, disable=too-many-locals, disable=too-many-arguments
    inlcude_stopwords=False, punctuations=None, stop_words=None):
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
    if use_translation_memory:
        translation_memory = db_.query(db_models.TranslationMemory.token).filter(
            db_models.TranslationMemory.source_language.has(code=src_lang)).all()
        memory_trie = build_memory_trie(translation_memory)
    for sent in sent_list:
        phrases = []
        text = re.sub(r'[\n\r]+', ' ', sent[1])
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
        sw_list = stop_words['prepositions']+stop_words['postpositions']
        for phrase in phrases:
            if phrase.strip() == '':
                continue
            if (not inlcude_stopwords) and phrase in sw_list:
                continue
            offset = sent[1].find(phrase, start)
            if offset == -1:
                raise NotAvailableException("Tokenization: token, %s, not found in sentence: %s" %(
                    phrase, sent[1]))
            start = offset+1
            if phrase not in unique_tokens:
                unique_tokens[phrase] = {
                "occurrences":[{"sentenceId":sent[0], "offset":[offset, offset+len(phrase)]}],
                "translations":[]}
            else: 
                unique_tokens[phrase]["occurrences"].append(
                    {"sentenceId":sent[0], "offset":[offset, offset+len(phrase)]})
    return unique_tokens

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

def extract_context(token, offset, sentence, window_size=5,
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

suggestion_trie_in_mem = {"language": None, "model":None}

def auto_translate(db_, sentence_list, source_lang, target_lang, punctuations=None, stop_words=None):
    '''Attempts to tokenize the input sentence and replace each token with top suggestion.
    If draft_meta is provided indicating some portion of sentence is user translated, 
    then it is left untouched.
    Output is of the format [(sent_id, translated text, metadata)]
    metadata: List of (token_offsets, translation_offset, confirmed/suggestion/untranslated)'''
    # load corresponding trie for source and target if not already in memory
    file_name = 'models/suggestion_tries/'+source_lang+'-'+target_lang+'.pkl'
    if suggestion_trie_in_mem["language"] == source_lang: # check if aleady loaded in memory
        sugg_trie = suggestion_trie_in_mem['model']
    elif os.path.exists(file_name): # load from disk
        sugg_trie = pickle.load(open(file_name, 'rb'))
        suggestion_trie_in_mem['language'] = source_lang
        suggestion_trie_in_mem['model'] = sugg_trie
    else: # if learnt model not present, return input as such
        return sentence_list
    args = {"db_":db_, "src_lang":source_lang, "sent_list":sentence_list}
    if punctuations:
        args['punctuations'] = punctuations
    if stop_words:
        args['stop_words'] = stop_words
    tokens = tokenize(**args)
    sentence_dict = {}
    for token in tokens:
        for occurence in tokens[token]:
            offset = (occurence[1], occurence[2])
            index, context = extract_context(token, offset, sentence_dict[occurence[0]]['source'])
            suggestions = get_translation_suggestion(index, context, sugg_trie)
            if len(suggestions) > 0:
                draft, meta = replace_token(sentence_dict[occurence[0]]['source'], offset,
                    suggestions[0][0], sentence_dict[occurence[0]]['draft'],
                    sentence_dict[occurence[0]]['draft_meta'], 
                              "suggestion")
                sentence_dict[occurence[0]]['draft'] = draft
                sentence_dict[occurence[0]]['draftMeta'] = meta
            elif sentence_dict[occurence[0]]['draft'] == '':
                sentence_dict[occurence[0]]['draft'] = sentence_dict[occurence[0]]['source']
                indices = (0,len(sentence_dict[occurence[0]]['source']))
                sentence_dict[occurence[0]]['draftMeta'] = [(indices, indices, "untranslated")]
    result = []
    for sent in sentence_list:
        obj= sentence_dict[sent.sentenceId]
        sent.draft = obj['draft']
        sent.draftMeta = obj['draftMeta']
        result.append(sent)
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

def form_trie_keys(prefix, to_left, to_right, prev_keys):
    '''build the trie tree recursively'''    
    keys = prev_keys
    aaa = bbb = None
    if len(to_left) > 0:
        aaa = '/L:'+to_left.pop(0)
    if len(to_right) > 0:
        bbb = '/R:'+to_right.pop(0)
    if aaa:
        key_left = prefix + aaa
        keys.append(key_left)
        keys = form_trie_keys(key_left, to_left.copy(), to_right.copy(), keys)
    if bbb:
        key_right = prefix + bbb
        keys.append(key_right)
        keys = form_trie_keys(key_right, to_left.copy(), to_right.copy(), keys)
    if aaa and bbb:
        key_both_1 = prefix + aaa + bbb
        key_both_2 = prefix + bbb + aaa
        keys.append(key_both_1)
        keys.append(key_both_2)
        keys = form_trie_keys(key_both_1, to_left.copy(), to_right.copy(), keys)
        keys = form_trie_keys(key_both_2, to_left.copy(), to_right.copy(), keys)
    return keys

def get_training_data_from_drafts(sentence_list, window_size=5):
    '''identify user confirmed token translations and their contexts'''
    training_data = []
    for row in sentence_list:
        source = row.sentence
        for meta in row.draftMeta:
            if meta[2] == "confirmed":
                token = source[meta[0][0]:meta[0][1]]
                index, context = extract_context(token, meta[0], source, window_size)
                training_data.append((index,context))
    return training_data

def build_trie(token_context__trans_list):
    '''Build a trie tree from scratch
    input: [(token,context_list, translation), ...]'''
    suggestion_trie = pygtrie.StringTrie()
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
        for key in keys:
            if suggestion_trie.has_key(key):
                value = suggestion_trie[key]
                if translation in value.keys():
                    value[translation] += 1
                else:
                    value[translation] = 1
                suggestion_trie[key] = value
            else:
                suggestion_trie[key] = {translation: 1}
    return suggestion_trie

def get_translation_suggestion(word, context, suggestion_trie): # pylint: disable=too-many-locals
    '''find the context based translation suggestions for a word.
    Makes use of the learned model, t, for the lang pair, based on translation memory
    output format: [(translation1, score1), (translation2, score2), ...]'''
    if isinstance(word, str):
        token_index = context.index(word)
    elif isinstance(word, int):
        token_index = word
        word = context[token_index]
    single_word_match = list(suggestion_trie.prefixes(word))
    #pdb.set_trace()
    if len(single_word_match) == 0:
        return []
    total_count = sum(single_word_match[0].value.values())
    to_left = [context[i] for i in range(token_index-1, -1, -1)]
    to_right = context[token_index+1:]
    keys = form_trie_keys(word, to_left, to_right, [word])
    keys = sorted(keys, key = lambda x : len(x), reverse=True)
    suggestions = {}
    prev_path_length = 0
    for k in keys:
        if len(k) < prev_path_length:
            # avoid searching with all the lower level keys
            break
        prev_path_length = len(k)
        all_matches = suggestion_trie.prefixes(k)
        for match in all_matches:
            levels = len(match.key.split("/"))
            #pdb.set_trace()
            for trans in match.value:
                score = match.value[trans]*levels*levels / total_count
                if trans in suggestions:
                    if suggestions[trans] < score:
                        suggestions[trans] = score
                else:
                    suggestions[trans] = score
    sorted_suggestions = {k: suggestions[k] for k in sorted(suggestions,
        key=suggestions.get, reverse=True)}
    return [(key, suggestions[key]) for key in sorted_suggestions]

def export_to_json(source_lang, target_lang, sentence_list, last_modified):
    '''input sentence_list is List of (sent_id, source_sent, draft, draft_meta)
    output:json in alignment format'''
    json_output = {#"conformsTo": "alignment-0.1",
                   "metadata":{
                      "resources":{
                          "r0": {
                            "languageCode": source_lang.code,
                            "name": source_lang.language,
                            # "version": "0.1"
                          },
                          "r1": {
                            "languageCode": target_lang.code,
                            "name": target_lang.language,
                            # "version": "9"
                          }
                      },
                      "modified": last_modified
                   },
                   "segments": []
                  }
    for row in sentence_list:
        row_obj = {"resources":{
                        "r0":{
                            "text":row.sentence,
                            # "tokens":re.sub(punct_pattern,'',row[1]).split()
                            "metadata": {"contextId":row.surrogateId}
                        },
                        "r1":{
                            "text": row.draft,
                            # "tokens":re.sub(punct_pattern,'',row[1]).split()
                            "metadata": {"contextId":row.surrogateId}
                        }
                    },
                   "alignments":[]
                  }
        for meta in row.draftMeta:
            algmt = {
              "r0": list(meta[0]),
              "r1": list(meta[1]),
              "status": meta[2]
            }
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
    db_.commit()
    # db_.refresh(db_content)
    # db_content.sourceLanguage
    # db_content.targetLanguage
    # db_content = db_content.__dict__
    # db_content['books'] = None
    # if db_content['metaData'] is not None and "books" in db_content['metaData']:
    #     db_content['books'] = db_content['metaData']['books']
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
                draft_row = db_models.TranslationDraft(
                    project_id=project_obj.projectId,
                    sentenceId=verse.refId,
                    surrogateId=buk+","+str(verse.chapter)+","+str(verse.verseNumber),
                    sentence=utils.normalize_unicode(verse.verseText),
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
                        draft_row = db_models.TranslationDraft(
                            project_id=project_obj.projectId,
                            sentenceId=book.bookId*1000000+
                                int(chapter_number)*1000+int(verse_number),
                            surrogateId=book_code+","+str(chapter_number)+","+str(verse_number),
                            sentence=verse_text,
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
        query = query.filter(db_models.TranslationProject.createdUser == user_id)
    return query.filter(db_models.TranslationProject.active == active).all()

def get_agmt_tokens(db_:Session, project_id, books, sentence_id_range, sentence_id_list, #pylint: disable=too-many-arguments disable=too-many-locals
    use_translation_memory=True, include_phrases=True, inlcude_stopwords=False):
    '''Get the selected verses from drafts table and tokenize them'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    source = db_.query(db_models.Language).get(project_row.source_lang_id)
    sentence_query = db_.query(
        db_models.TranslationDraft.sentenceId, db_models.TranslationDraft.sentence).filter(
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
    sentences = sentence_query.all()
    args = {"db_":db_, "src_lang":source.code, "sent_list":sentences,
        "use_translation_memory":use_translation_memory, "include_phrases":include_phrases,
        "inlcude_stopwords":inlcude_stopwords}
    if "stopwords" in project_row.metaData:
        args['stop_words'] = project_row.metaData['stopwords']
    if "punctuations" in project_row.metaData:
        args['punctuations'] = project_row.metaData['punctuations']
    tokens = tokenize(**args)
    result = []
    for token in tokens:
        obj = tokens[token]
        obj['token'] = token
        known_info = db_.query(db_models.TranslationMemory).filter(
            db_models.TranslationMemory.source_lang_id == project_row.source_lang_id,
            db_models.TranslationMemory.token == token,
            or_(db_models.TranslationMemory.target_lang_id == project_row.target_lang_id,
                db_models.TranslationMemory.metaData is not None)
        ).all()
        if len(known_info)>0:
            for mem in known_info:
                if mem.target_lang_id == project_row.target_lang_id:
                    obj['translations'] = mem.translations
                    obj['metaData'] = mem.metaData
                    break
                elif "metaData" not in obj:
                    obj['metaData'] = mem.metaData
        result.append(obj)
    return result

def save_agmt_translations(db_, project_id, token_translations, return_drafts=True, user_id=None):
    '''replace tokens with provided translation in the drafts and update translation memory'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    use_data = True
    if project_row.metaData is not None and "useDataForLearning" in project_row.metaData:
        use_data = project_row.metaData['useDataForLearning']
    db_content = []
    db_content_2 = []
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
                other_lang_metaData = db_.query(db_models.TranslationMemory.metaData).filter(
                    db_models.TranslationMemory.source_lang_id == project_row.source_lang_id,
                    db_models.TranslationMemory.token == token.token).first()
                if other_lang_metaData:
                    row_args['metaData'] = other_lang_metaData[0]
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

def obtain_agmt_draft(db_:Session, project_id, books, sentence_id_list, sentence_id_range,
        fill_suggestions=False, output_format="text"):
    '''generate draft for selected sentences as text, usfm or json'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
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
    [row.__dict__ for row in draft_rows]
    if fill_suggestions:
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
        [db_.refresh(row) for row in draft_rows]
    else:
        for sent in draft_rows:
            commit_required = False
            if sent.draft is None or sent.draft == "":
                commit_required = True
                sent.draft = sent.sentence
                sent.draftMeta = [((0,len(sent.sentence)), (0,len(sent.sentence)), "untranslated")]
                db_.add(sent)
                flag_modified(sent, "draftMeta")
        if commit_required:
            db_.commit()
    if output_format.value == "text":
        [row.__dict__ for row in draft_rows]
        return draft_rows
    if output_format.value == "usfm":
        return create_usfm(draft_rows)
    if output_format.value == 'alignment-json':
        return export_to_json(project_row.sourceLanguage,
            project_row.targetLanguage, draft_rows, None)
    raise TypeException("Unsupported output format: %s"%output_format)
