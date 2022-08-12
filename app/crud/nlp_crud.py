''' Place to define all data processing and Database CRUD operations
related to NLP operations and translation apps'''

import re
import os
import json
from datetime import datetime
from math import floor, ceil
from pathlib import Path
import pygtrie
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import text

from crud import utils
from crud import nlp_tokenization as nlp_utils
import db_models
from dependencies import log
from custom_exceptions import NotAvailableException, TypeException, GenericException
from schema.schemas_nlp import TranslationDocumentType

#Based on sqlalchemy
#pylint: disable=W0102,E1101,W0143,C0206
###################### Tokenization ######################

def get_generic_tokens_result(db_, trg_language, src_language, args):
    """get generic token function result generation"""
    tokens = nlp_utils.tokenize(**args)
    result = []
    for token in tokens:
        obj = tokens[token]
        obj['token'] = token
        trg = None
        if trg_language is not None:
            trg = trg_language.code
        known_info = glossary(db_, src_language.code, trg, token)
        obj['translations'] = known_info['translations']
        if "metaData" in known_info:
            obj['metaData'] = known_info['metaData']
        result.append(obj)
    return result

def get_generic_tokens(db_:Session, src_language, sentence_list, trg_language=None,
    **kwargs):
    '''tokenize the input sentences and return token list with details'''
    punctuations = kwargs.get("punctuations",None)
    stopwords = kwargs.get("stopwords",None)
    use_translation_memory = kwargs.get("use_translation_memory",True)
    include_phrases = kwargs.get("include_phrases",True)
    include_stopwords = kwargs.get("include_stopwords",False)
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
    #generate result based on tokens
    result = get_generic_tokens_result(db_, trg_language, src_language, args)
    return result

def get_agmt_tokens(db_:Session, project_id, books, sentence_id_range, sentence_id_list,
    **kwargs):
    '''Get the selected verses from drafts table and tokenize them'''
    use_translation_memory = kwargs.get("use_translation_memory",True)
    include_phrases = kwargs.get("include_phrases",True)
    include_stopwords = kwargs.get("include_stopwords",False)
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    sentences = obtain_agmt_source(db_, project_id, books, sentence_id_range,sentence_id_list)
    sentences = sentences['db_content']
    args = {"db_":db_, "src_language":project_row.sourceLanguage, "sentence_list":sentences,
        'trg_language':project_row.targetLanguage,
        "use_translation_memory":use_translation_memory, "include_phrases":include_phrases,
        "include_stopwords":include_stopwords}
    if "stopwords" in project_row.metaData:
        args['stopwords'] = project_row.metaData['stopwords']
    if "punctuations" in project_row.metaData:
        args['punctuations'] = project_row.metaData['punctuations']
    # return get_generic_tokens( **args)
    response = {
        'db_content':get_generic_tokens( **args),
        'project_content':project_row
        }
    return response

###################### Token replacement translation ######################
def replace_bulk_tokens_gloss_list(token_translations, updated_sentences):
    """gloss list logic for replace bulk token function"""
    gloss_list = []
    for token in token_translations:
        for occur in token.occurrences:
            draft_row = updated_sentences[occur.sentenceId]
            if not draft_row:
                raise NotAvailableException("Sentence id, %s, not found in the sentence_list"
                    %occur.sentenceId)
            if token.token != draft_row.sentence[occur.offset[0]:occur.offset[1]]:
                raise GenericException("Token, %s, and its occurence, not matching"%(
                    token.token))
            draft, meta = nlp_utils.replace_token(draft_row.sentence, occur.offset,
                 token.translation,draft_row.draftMeta, draft=draft_row.draft)
            draft_row.draft = draft
            draft_row.draftMeta = meta
            updated_sentences[occur.sentenceId]  = draft_row
            gloss = {"token": token.token, "translations":{token.translation:{
                        "frequency": len(token.occurrences)}}}
            gloss_list.append(gloss)
    return gloss_list

def replace_bulk_tokens(db_, sentence_list, token_translations, src_code, trg_code, **kwargs):
    '''Substitute tokens with provided trabslations and get updated drafts, draftMetas
    and add knowledge to translation memory'''
    use_data = kwargs.get("use_data_for_learning",True)
    source = db_.query(db_models.Language).filter(
        db_models.Language.code == src_code).first()
    if not source:
        raise NotAvailableException("Language, %s, not in DB. Please create if required"%src_code)
    target = db_.query(db_models.Language).filter(
        db_models.Language.code == trg_code).first()
    if not source:
        raise NotAvailableException("Language, %s, not in DB. Please create if required"%trg_code)
    updated_sentences = {sent.sentenceId:sent for sent in sentence_list}

    #get gloss list
    gloss_list = replace_bulk_tokens_gloss_list(token_translations, updated_sentences)
    if use_data:
        add_to_translation_memory(db_, source, target, gloss_list)

    result = [updated_sentences[key] for key in updated_sentences]
    return result

def save_agmt_translations__gloss_list(db_, token_translations, project_id, user_id):
    """get gloss list for save_agmt_translations function"""
    db_content = []
    gloss_list = []
    for token in token_translations:
        for occur in token.occurrences:
            draft_row = db_.query(db_models.TranslationDraft).filter(
                db_models.TranslationDraft.project_id == project_id,
                db_models.TranslationDraft.sentenceId == occur.sentenceId).first()
            if not draft_row:
                raise NotAvailableException("Sentence id, %s, not found for the selected project"
                    %occur.sentenceId)
            if token.token != draft_row.sentence[occur.offset[0]:occur.offset[1]]:
                raise GenericException("Token, %s, and its occurence, not matching"%(
                    token.token))
            draft, meta = nlp_utils.replace_token(draft_row.sentence, occur.offset,
            token.translation, draft_row.draftMeta, draft=draft_row.draft)
            draft_row.draft = draft
            draft_row.draftMeta = meta
            flag_modified(draft_row, "draftMeta")
            draft_row.updatedUser = user_id
            db_content.append(draft_row)
        gloss = {"token": token.token, "translations":{token.translation:{
            "frequency": len(token.occurrences)}}}
        gloss_list.append(gloss)
    return gloss_list,db_content

def save_agmt_translations(db_, project_id, token_translations, return_drafts=True, user_id=None):
    '''replace tokens with provided translation in the drafts and update translation memory'''
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not present"%project_id)
    use_data = True
    if project_row.metaData is not None and "useDataForLearning" in project_row.metaData:
        use_data = project_row.metaData['useDataForLearning']

    #get gloss list
    gloss_list, db_content = \
        save_agmt_translations__gloss_list(db_, token_translations,project_id,user_id)
    project_row.updatedUser = user_id
    db_.add_all(db_content)
    db_.add(project_row)
    # db_.commit()
    if use_data:
        add_to_translation_memory(db_, project_row.sourceLanguage, project_row.targetLanguage,
            gloss_list)
    # if return_drafts:
    #     result = set(db_content)
    #     return sorted(result, key=lambda x: x.sentenceId)
    # return None
    if return_drafts:
        result = set(db_content)
        result =  sorted(result, key=lambda x: x.sentenceId)
    else:
        result = None
    response = {
        'db_content':result,
        'project_content':project_row
        }
    return response

###################### Suggestions ######################
suggestion_trie_in_mem = {}
SUGGESTION_DATA_PATH = Path('models/suggestion_data')
SUGGESTION_TRIE_PATH = Path('models/suggestion_tries')
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

def check_eliminate_phrase_alignemnts(phrases, src_tok_list, trg_tok_list):
    """check and eliminate non-continuous phrase alignments"""
    for obj in phrases:
        deleted = False
        for i in range(len(obj['src_indices'])-1):
            if ((obj['src_indices'][i] != obj['src_indices'][i+1])
                and (obj['src_indices'][i] + 1 !=  obj['src_indices'][i+1])):
                log.warning("Eliminating non-continuous src phrase:%s, in %s",
                    obj['src_indices'], src_tok_list)
                phrases.remove(obj)
                deleted = True
        if deleted:
            continue
        for i in range(len(obj['trg_indices'])-1):
            if ((obj['trg_indices'][i] != obj['trg_indices'][i])
                and (obj['trg_indices'][i] + 1 !=  obj['src_indices'][i+1])):
                log.warning("Eliminating non-continuous trg phrase:%s, in %s",
                    obj['trg_indices'], trg_tok_list)
                phrases.remove(obj)
    return phrases

def find_pharses_from_alignments(src_tok_list, trg_tok_list, align_pairs):
    '''Takes one sentence's alignments and finds aligned phrases
    input: src-trg token alignments, a list of {"sourceTokenIndex", "targetTokenIndex"} pairs
    output: aligned multi-token pharses, if available, based on one to many mappings in input'''
    phrases = []
    seen_src = []
    seen_trg = []
    src_tok_list = [tok.lower() for tok in src_tok_list]
    trg_tok_list = [tok.lower() for tok in trg_tok_list]
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
    #check and eliminate non-continuous phrase alignments
    phrases = check_eliminate_phrase_alignemnts(phrases, src_tok_list, trg_tok_list)
    return phrases

def alignment_prepare_trainingdata(alignment_list, window_size):
    """prepare data for translation memory/gloss"""
    dict_data = {}
    sugg_data = []
    for sent in alignment_list:
        src_len = len(sent.sourceTokenList)
        src_toks = [utils.normalize_unicode(tok) for tok in sent.sourceTokenList]
        trg_toks = [utils.normalize_unicode(tok) for tok in sent.targetTokenList]
        phrases = find_pharses_from_alignments(src_toks, trg_toks, sent.alignedTokens)
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
            # split multiword tokens in context
            pre_context = ' '.join(pre_context).split(' ')
            post_context = ' '.join(post_context).split(' ')

            context = pre_context + [obj['token']] + post_context
            sugg_data.append((len(pre_context), context, obj['translation']))
    return dict_data, sugg_data

def alignments_to_trainingdata(db_:Session,window_size=WINDOW_SIZE,
    output_dir=SUGGESTION_DATA_PATH,**kwargs):
    '''Convert alignments to training data for suggestions module and also add to translation_memory
    input format: [(<src sent>,<trg_sent>,[(0-0), (1-3),(2-1),..]]
    output: <index>\t<context ayrray>\t<translation>'''
    src_lang = kwargs.get("src_lang")
    trg_lang = kwargs.get("trg_lang")
    user_id = kwargs.get("user_id")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    timestamp = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    output_path = output_dir / (src_lang+"-"+trg_lang+"-"+str(user_id)+"-"+\
        "-"+timestamp+".json")
    with open(output_path, "w", encoding='utf-8') as output_file:
        #prepare data
        dict_data, sugg_data = \
            alignment_prepare_trainingdata(kwargs.get("alignment_list"), window_size)

        new_trie = build_trie(sugg_data)
        sugg_json = {item[0]:item[1] for item in new_trie.items()}
        json.dump(sugg_json, output_file, ensure_ascii=False)

    log.warning("trie model saved on server: %s", output_path)
    new_trie = rebuild_trie(db_, src_lang, trg_lang)
    suggestion_trie_in_mem[src_lang+"-"+trg_lang] = new_trie

    # increments frequency by 1, as the gloss was observed in usage in alignment
    tw_data = add_to_translation_memory(db_, src_lang, trg_lang,
        [dict_data[key] for key in dict_data], default_val=1)
    return tw_data

def from_trie_keys_checks(to_left, to_right, prefix, keys, only_longest):
    """check for the build trie tree"""
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
    return keys

def form_trie_keys(prefix, to_left, to_right, prev_keys, only_longest=True):
    '''build the trie tree recursively'''
    keys = prev_keys
    #checks function
    keys = from_trie_keys_checks(to_left, to_right, prefix, keys, only_longest)
    sorted_keys = sorted(keys, key=len, reverse=True)
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
                value = ttt[key]
                if translation in value.keys():
                    value[translation] += val_update
                else:
                    value[translation] = val_update
                ttt[key] = value
            else:
                ttt[key] = {translation: val_update}
    return ttt

def display_tree(tree):
    '''pretty prints a trie'''
    for path in tree.items():
        nodes = path[0].split('/')
        for nod in nodes:
            print('\t-',nod,end='')
        print(' => ',path[1])

def rebuild_trie(db_, src, trg):
    '''Collect suggestions data from translation memory and traning data directory
    and rebuild the trie for language pair in memory'''
    db_sents = db_.query(db_models.TranslationDraft, db_models.TranslationProject).filter(
        db_models.TranslationProject.sourceLanguage.has(code = src),
        db_models.TranslationProject.targetLanguage.has(code = trg)).all()
    training_data = get_training_data_from_drafts([item[0] for item in db_sents])
    new_trie = build_trie(training_data)
    files_on_disc = SUGGESTION_DATA_PATH.glob(src+"-"+trg+'*.json')
    for file in files_on_disc:
        with open(file, 'r', encoding='utf-8') as json_file:
            log.warning("Using %s, to update %s-%s trie",file, src, trg)
            json_data = json.load(json_file)
            for key in json_data:
                new_trie[key] = json_data[key]
    # display_tree(new_trie)
    return new_trie

def add_metadata_to_first_occurance(db_, gloss, source_lang, target_lang, *args):
    """Always add meta data to the first occurance of a source token only'''"""
    recieved_args = args[0]
    db_content = args[1]
    if 'tokenMetaData' in gloss and gloss['tokenMetaData'] is not None:
        # Always add meta data to the first occurance of a source token only'''
        token_row = db_.query(db_models.TranslationMemory).filter(
            db_models.TranslationMemory.source_lang_id == source_lang.languageId,
            db_models.TranslationMemory.target_lang_id == target_lang.languageId,
            db_models.TranslationMemory.token == gloss['token']).order_by(
            db_models.TranslationMemory.tokenId.asc()).first()
        if token_row:
            if not token_row.metaData:
                token_row.metaData = {}
            for key in gloss['tokenMetaData']:
                token_row.metaData[key] = gloss['tokenMetaData'][key]
            flag_modified(token_row, 'metaData')
        else:
            updated_args = recieved_args
            updated_args['metaData'] = gloss['tokenMetaData']
            token_row = db_models.TranslationMemory(**updated_args)
        db_.add(token_row)
        db_content.append(token_row)
    return db_content

def add_translation_memory_gloss_dataprocess(db_, gloss_list, source_lang,
    target_lang, default_val):
    """gloss data process"""
    db_content = []
    for gloss in gloss_list:
        if not isinstance(gloss, dict):
            gloss = gloss.__dict__
        gloss['token'] = utils.normalize_unicode(gloss['token']).lower()
        args = {"source_lang_id":source_lang.languageId,
                "target_lang_id": target_lang.languageId,
                "token":gloss['token'],
                "tokenRom":utils.to_eng(gloss['token'])}
        if "translations" in gloss and gloss['translations'] is not None:
            for trans in gloss['translations']:
                if (isinstance(gloss['translations'], dict) and
                    'frequency' in gloss['translations'][trans]):
                    freq_val = gloss['translations'][trans]['frequency']
                else:
                    freq_val = default_val
                trans = utils.normalize_unicode(trans).lower()
                token_row = db_.query(db_models.TranslationMemory).filter(
                    db_models.TranslationMemory.source_lang_id == source_lang.languageId,
                    db_models.TranslationMemory.target_lang_id == target_lang.languageId,
                    db_models.TranslationMemory.token == gloss['token'],
                    db_models.TranslationMemory.translation == trans).first()
                if token_row:
                    token_row.frequency += freq_val
                else:
                    updated_args = args
                    updated_args["translation"] = trans
                    updated_args["translationRom"]=utils.to_eng(trans)
                    updated_args["frequency"]=freq_val
                    updated_args["metaData"]=None
                    token_row = db_models.TranslationMemory(**updated_args)
                db_.add(token_row)
                db_content.append(token_row)
        db_.flush()

        #add meta data to the first occurance of a source token only
        db_content =  add_metadata_to_first_occurance(db_, gloss, source_lang,
            target_lang, args, db_content)
    db_.commit()
    return db_content

def add_to_translation_memory(db_, src_lang, trg_lang, gloss_list, default_val=0):
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

    #function for gloss data process
    db_content= add_translation_memory_gloss_dataprocess(db_, gloss_list, source_lang,
            target_lang, default_val)

    result_dict = {}
    for item in db_content:
        db_.refresh(item)
        if item.token not in result_dict:
            result_dict[item.token] = {"token":item.token, "translations":{}}
        if item.translation is not None:
            result_dict[item.token]["translations"][item.translation] = {"frequency":item.frequency}
        if item.metaData is not None:
            result_dict[item.token]["metaData"] = item.metaData
    result_list = [result_dict[entry] for entry in result_dict]
    return result_list

def get_gloss_chop_word(db_, no_trie_match, trans, matched_word,*args):
    """get gloss chop word functionality"""
    total = args[0]
    word = args[1]
    pass_no = args[2]
    source_lang = args[3]
    target_lang = args[4]

    if len(trans) == 0 and pass_no<3 and len(word)>4:
        # try chopping off the last letter
        chopped_word = word[:-1]
        result = get_gloss(db_, 0, [chopped_word], source_lang, target_lang,
            pass_no=pass_no+1)
        if len(result['translations']) > 0:
            return result
    if total == 0:
        total = 1
    sorted_trans = sorted(trans.items(), key=lambda x:x[1], reverse=True)
    scored_trans = {}
    for sense in sorted_trans:
        scored_trans[sense[0]]=sense[1]/total
    result = {}
    if no_trie_match and matched_word:
        result['token'] = matched_word
    else:
        result['token'] = word
    result['translations'] = scored_trans

    return result

def gloss_forward_reverse_query(db_, word, source_lang, target_lang, total, *args):
    """get forward and reverse query"""
    trans = args[0]
    forward_query = db_.query(db_models.TranslationMemory).with_entities(
        db_models.TranslationMemory.token,
        db_models.TranslationMemory.translation,
        db_models.TranslationMemory.frequency,
        text("levenshtein(source_token,:word1) as lev_score").bindparams(word1=word)
        ).filter(
            db_models.TranslationMemory.source_language.has(code=source_lang),
            db_models.TranslationMemory.target_language.has(code=target_lang),
            text("soundex(source_token_romanized) = soundex(:word2)").\
                bindparams(word2=utils.to_eng(word)),
            text("levenshtein(source_token,:word3) < 4").bindparams(word3=word))
    reverse_query = db_.query(db_models.TranslationMemory).with_entities(
        db_models.TranslationMemory.translation,
        db_models.TranslationMemory.token,
        db_models.TranslationMemory.frequency,
        text("levenshtein(translation,:word1) as lev_score").bindparams(word1=word)
        ).filter(
            db_models.TranslationMemory.source_language.has(code=target_lang),
            db_models.TranslationMemory.target_language.has(code=source_lang),
            text("soundex(translation_romanized) = soundex(:word2)").\
                bindparams(word2=utils.to_eng(word)),
            text("levenshtein(translation,:word3) < 4").bindparams(word3=word))
    forward_dict_entires =  forward_query.all()
    reverse_dict_entires = reverse_query.all()
    matched_word = None
    for row in forward_dict_entires+ reverse_dict_entires:
        if not matched_word:
            matched_word = row[0]
        if row[1] not in trans:
            trans[row[1]] = row[2]/(row[3]+1)
            total += 1
    return matched_word , total

def get_gloss(db_:Session, *args, **kwargs):#pylint: disable=too-many-locals,too-many-branches
    '''find the context based translation suggestions(gloss) for a word.
    Makes use of the learned model(trie), for the lang pair, based on translation memory
    output format: [(translation1, score1), (translation2, score2), ...]'''
    index = args[0]
    context = args[1]
    source_lang = args[2]
    target_lang = args[3]
    pass_no = kwargs.get("pass_no",1)
    if isinstance(index, int):
        word = context[index]
    elif isinstance(index, str):
        word = index
        index = context.index(word)
    word = utils.normalize_unicode(word).lower()
    context = [utils.normalize_unicode(con).lower() for con in context]
    to_left = [context[i] for i in range(index-1, -1, -1)]
    to_right = context[index+1:]
    trans = {}
    total = 0
    no_trie_match = True
    if len(to_right)+len(to_left) > 0:#pylint: disable=too-many-nested-blocks
        keys = form_trie_keys(word, to_left, to_right, [word], False)
        if source_lang+"-"+target_lang in suggestion_trie_in_mem: # check if aleady loaded in memory
            tree = suggestion_trie_in_mem[source_lang+"-"+target_lang]
        else:  # build trie loading data from disk and DB
            tree = rebuild_trie(db_, source_lang, target_lang)
            suggestion_trie_in_mem[source_lang+"-"+target_lang] = tree
        for key in keys:
            if tree.has_subtrie(key) or tree.has_key(key):
                # print("found:",key)
                no_trie_match = False
                nodes = tree.values(key)
                level = len(key.split("/"))
                for nod in nodes:
                    for sense in nod:
                        if sense in trans:
                            trans[sense] += nod[sense]*level*level
                        else:
                            trans[sense] = nod[sense]*level*level
                        total += nod[sense]
            else:
                pass
                # print("not found:",key)

    #get forward reverse query
    matched_word , total = \
        gloss_forward_reverse_query(db_, word, source_lang, target_lang, total, trans)

    #get gloss chop word
    result = get_gloss_chop_word(db_, no_trie_match,
        trans, matched_word, total, word, pass_no, source_lang, target_lang)

    # check for metadata
    metadata_query = db_.query(db_models.TranslationMemory.metaData).filter(
        db_models.TranslationMemory.token == word,
        db_models.TranslationMemory.metaData is not None).order_by(
        db_models.TranslationMemory.tokenId)
    mdt = metadata_query.first()
    if mdt:
        result['metaData'] = mdt[0]
    return result

def glossary(db_:Session, source_language, target_language, token, **kwargs):
    '''finds possible translation suggestion for a token'''
    context = kwargs.get("context",None)
    token_offset = kwargs.get("token_offset",None)
    if context is None:
        context = token
    if token_offset is None:
        start = context.index(token)
        token_offset= (start, start+len(token))
    index, context_list = extract_context(token, token_offset, context)
    suggs = get_gloss(db_, index, context_list, source_language, target_language)
    return suggs

def auto_translate_token_logic(db_,tokens, sent, source_lang, target_lang):
    """auto translate token loop"""
    for token in tokens:
        for occurence in tokens[token]['occurrences']:
            offset = occurence['offset']
            index, context = extract_context(token, offset,
                sent.sentence)
            gloss = get_gloss(db_, index, context, source_lang, target_lang)
            suggestions = list(gloss['translations'].keys())
            if len(suggestions) > 0:
                draft, meta = nlp_utils.replace_token(sent.sentence, offset,
                    suggestions[0], sent.draftMeta, "suggestion",draft=sent.draft)
            else:
                # splits the source sentence into tokens(in draftmeta)
                # even if there is no transltion suggestion available.
                draft, meta = nlp_utils.replace_token(sent.sentence, offset,
                    token, sent.draftMeta, "untranslated",draft=sent.draft)
            sent.draft = draft
            sent.draftMeta = meta

def auto_translate(db_, sentence_list, source_lang, target_lang, **kwargs):
    '''Attempts to tokenize the input sentence and replace each token with top suggestion.
    If draft_meta is provided indicating some portion of sentence is user translated,
    then it is left untouched.'''
    punctuations = kwargs.get("punctuations",None)
    stop_words = kwargs.get("stop_words",None)
    args = {"db_":db_, "src_lang":source_lang, "include_stopwords":False, "include_phrases":True}
    if punctuations:
        args['punctuations'] = punctuations
    if stop_words:
        args['stop_words'] = stop_words
    for sent in sentence_list:
        args['sent_list'] = [{"sentenceId":sent.sentenceId,
                                "sentence":sent.sentence,
                                "draftMeta":sent.draftMeta if sent.draftMeta is not None else []}]
        tokens = nlp_utils.tokenize(**args)

        #auto tranaslte token loop
        auto_translate_token_logic(db_,tokens, sent, source_lang, target_lang)

    return sentence_list

def agmt_suggest_translations(db_:Session, project_id, books, sentence_id_range, sentence_id_list,
    **kwargs):
    '''Tokenize and auto fill draft with top suggestions'''
    confirm_all= kwargs.get("confirm_all",False)
    project_row = db_.query(db_models.TranslationProject).get(project_id)
    if not project_row:
        raise NotAvailableException("Project with id, %s, not found"%project_id)
    draft_rows = obtain_agmt_source(db_, project_id, books, sentence_id_range,sentence_id_list,
        with_draft=True)
    draft_rows = draft_rows['db_content']
    if confirm_all:
        for row in draft_rows:
            for i, meta in enumerate(row.draftMeta):
                if meta[2] == "suggestion":
                    row.draftMeta[i][2] = "confirmed"
                    flag_modified(row, 'draftMeta')
        # db_.add_all(draft_rows)
        # db_.commit()
        # return draft_rows
        updated_drafts = draft_rows
    else:
        args = {"db_":db_, "sentence_list":draft_rows,
            "source_lang":project_row.sourceLanguage.code,
            "target_lang":project_row.targetLanguage.code}
        if "stopwords" in project_row.metaData:
            args['stop_words'] = project_row.metaData['stopwords']
        if "punctuations" in project_row.metaData:
            args['punctuations'] = project_row.metaData['punctuations']
        updated_drafts = auto_translate(**args)
        db_.add_all(updated_drafts)
        # db_.commit()
        # return updated_drafts
    response = {
        'db_content':updated_drafts,
        'project_content':project_row
        }
    return response

###################### Export and download ######################
def obtain_draft(sentence_list, doc_type):
    '''Convert input sentences to required format'''
    for sent in sentence_list:
        if sent.draft is None or sent.draft == '':
            sent.draft = sent.sentence
            offset = [0, len(sent.sentence)]
            sent.draftMeta = [offset, offset, "untranslated"]
    if doc_type == TranslationDocumentType.USFM:
        result = create_usfm(sentence_list)
        return result
    if doc_type == TranslationDocumentType.JSON:
        result = export_to_json(None, None, sentence_list, None)
        return result
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
    return None

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

def export_to_print(sentence_list):
    '''get a response with just id and draft to print'''
    output_json = {}
    for row in sentence_list:
        output_json[row.surrogateId] = row.draft
    return output_json

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
                           }},
                      "modified": last_modified},
                   "segments": []}
    if source_lang:
        json_output['metadata']['resources']['r0'] = {"languageCode": source_lang.code,
            "name": source_lang.language}
    if target_lang:
        json_output['metadata']['resources']['r1'] = {"languageCode": target_lang.code,
            "name": target_lang.language}
    for row in sentence_list:
        row_obj = {"resources":{
                        "r0":{
                            "text":row.sentence,
                            "tokens":[],
                            "metadata": {"contextId":row.surrogateId}},
                        "r1":{
                            "text": row.draft,
                            "tokens":[],
                            "metadata": {"contextId":row.surrogateId}}},
                   "alignments":[]}
        for i,meta in enumerate(row.draftMeta):
            algmt = {
              "r0": [i],
              "r1": [i],
              "status": meta[2]}
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

#########################################################
def obtain_agmt_source(db_:Session, project_id, books=None, sentence_id_range=None,#pylint: disable=too-many-locals
    sentence_id_list=None, **kwargs):
    '''fetches all or selected source sentences from translation_sentences table'''
    with_draft= kwargs.get("with_draft",False)
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
    draft_rows = sentence_query.order_by(db_models.TranslationDraft.sentenceId).all()
    if with_draft:
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
