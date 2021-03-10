''' Place to define all data processing and Database CRUD operations 
related to NLP operations and translation apps'''

import re
from math import floor, ceil
import pygtrie
import sqlalchemy

from crud import normalize_unicode, utils
import db_models
from custom_exceptions import NotAvailableException, TypeException, AlreadyExistsException

def find_phrases(text, stop_words):
    '''try forming phrases as <preposition stop word>* <content word> <postposition stop word>*'''
    words = text.split()
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
        key = re.sub(space_pattern,'/', token)
        memory_trie[key] = 0
    return memory_trie

mock_translation_memory = ["जीवन के वचन", "जीवन का", "अपनी आँखों से देखा", "पिता के साथ",
                          "यीशु मसीह", "परमेश्‍वर ज्योति", "झूठा ठहराते",
                          "Here is it", "hare", "no"]

def tokenize(src_lang, sent_list, punctuations=None, stop_words=None): #pylint: disable=too-many-branches, disable=too-many-locals
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
    memory_trie = build_memory_trie(mock_translation_memory)
    for sent in sent_list:
        phrases = []
        text = re.sub(r'[\n\r]+', ' ', sent[1])
        #first split the text into chunks based on punctuations
        chunks = [chunk.strip() for chunk in re.split(r'['+"".join(punctuations)+']+', text)]
        updated_chunks = []
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
                phrases+=find_phrases(chunk,stop_words)
        start = 0
        for phrase in phrases:
            offset = sent[1].find(phrase, start)
            if offset == -1:
                raise NotAvailableException("Tokenization: token, %s, not found in sentence: %s" %(
                    phrase, sent[1]))
            start = offset+1
            if phrase not in unique_tokens:
                unique_tokens[phrase] = [(sent[0], offset, offset+len(phrase))]
            else: 
                unique_tokens[phrase].append((sent[0], offset, offset+len(phrase)))
    return unique_tokens

def replace_token(source, token_offset, translation, draft="", draft_meta=[], tag="confirmed"): #pylint: disable=too-many-arguments, disable=too-many-locals, disable=W0102
    '''make a token replacement and return updated sentence and draft_meta'''
    trans_length = len(translation)
    updated_meta = []
    updated_draft = ""
    translation_offset = [None, None]
    if len(draft_meta) == 0:
        draft = source
        draft_meta.append(((0,len(source)), (0,len(source)), "untranslated"))
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

def auto_translate(sentence_list, source_lang, target_lang, punctuations=None, stop_words=None):
    '''Attempts to tokenize the input sentence and replace each token with top suggestion.
    If draft_meta is provided indicating some portion of sentence is user translated, 
    then it is left untouched.
    Output is of the format [(sent_id, translated text, metadata)]
    metadata: List of (token_offsets, translation_offset, confirmed/suggestion/untranslated)'''
    if not punctuations:
        punctuations = utils.punctuations()+utils.numbers()
    if not stop_words:
        stop_words = utils.stopwords(source_lang)
    sentence_dict = {}
    for item in sentence_list:
        sent_obj = {
            "source": item[1],
            "draft":item[2],
            "draft_meta":item[3]
        }
        if sent_obj['draft'] is None:
            sent_obj['draft'] = ''
        if sent_obj['draft_meta'] is None:
            sent_obj['draft_meta'] = []
        sentence_dict[item[0]]=sent_obj 
    suggestions_model = t # load corresponding trie for source and target if not already in memory
    tokens = tokenize(source_lang, sentence_list)
    for token in tokens:
        for occurence in tokens[token]:
            offset = (occurence[1], occurence[2])
            index, context = extract_context(token, offset, sentence_dict[occurence[0]]['source'])
            suggestions = get_translation_suggestion(index, context, t)
            if len(suggestions) > 0:
                draft, meta = replace_token(sentence_dict[occurence[0]]['source'], offset,
                    suggestions[0][0], sentence_dict[occurence[0]]['draft'],
                    sentence_dict[occurence[0]]['draft_meta'], 
                              "suggestion")
                sentence_dict[occurence[0]]['draft'] = draft
                sentence_dict[occurence[0]]['draft_meta'] = meta
            elif sentence_dict[occurence[0]]['draft'] == '':
                sentence_dict[occurence[0]]['draft'] = sentence_dict[occurence[0]]['source']
                indices = (0,len(sentence_dict[occurence[0]]['source']))
                sentence_dict[occurence[0]]['draft_meta'] = [(indices, indices, "untranslated")]
    return sentence_dict

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
    sentences = sorted(sent_drafts, key=lambda x:x[0], reverse=False)
    for sent in sentences:
        verse_num = sent[0] % 1000
        chapter_num = int((sent[0] /1000) % 1000)
        book_num = int(sent[0] / 1000000)
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
        file += verse.format(verse_num, sent[1])
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
        source = row[1]
        for meta in row[3]:
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
    json_output = {"conformsTo": "alignment-0.1",
                   "metadata":{
                      "resources":{
                          "r0": {
                            "languageCode": source_lang['code'],
                            "name": source_lang['name'],
#                             "version": "0.1"
                          },
                          "r1": {
                            "languageCode": target_lang['code'],
                            "name": target_lang['name'],
#                             "version": "9"
                          }
                      },
                      "modified": last_modified
                   },
                   "segments": []
                  }
    for row in sentence_list:
        row_obj = {"resources":{
                        "r0":{
                            "text":row[1],
#                             "tokens":re.sub(punct_pattern,'',row[1]).split()
                            "metadata": {"contextId":row[0]}
                        },
                        "r1":{
                            "text": row[2],
#                             "tokens":re.sub(punct_pattern,'',row[1]).split()
                            "metadata": {"contextId":row[0]}
                        }
                    },
                   "alignments":[]
                  }
        for meta in row[3]:
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
