''' Place to define all utitlity functions
related to NLP operations and translation apps'''
import re
import pickle
import pygtrie
from sqlalchemy.orm import Session

from crud import utils
import db_models
from redis_db.utils import  get_routes_from_cache, set_routes_to_cache
from dependencies import log


def build_memory_trie(translation_memory):
    '''form a trie from a list of known tokens in a resource language,
     to be used for tokenization'''
    memory_trie = pygtrie.StringTrie()
    space_pattern = re.compile(r'\s+')
    for token in translation_memory:
        key = re.sub(space_pattern,'/', token[0])
        memory_trie[key] = 0
    return memory_trie

mock_translation_memory = [("जीवन के वचन",), ("जीवन का",), ("अपनी आँखों से देखा",),
                          ("पिता के साथ",),
                          ("यीशु मसीह",), ("परमेश्‍वर ज्योति",), ("झूठा ठहराते",),
                          ("Here is it",), ("hare",), ("no",)]

def find_phrases_loop(words,stop_words,phrases,current_phrase):
    """logic loop for find phrases"""
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
    return phrases, current_phrase

def find_phrases(src_text, stop_words, include_phrases=True, include_stopwords=False):
    '''try forming phrases as <preposition stop word>* <content word> <postposition stop word>*'''
    words = src_text.split()
    if not isinstance(stop_words, dict):
        stop_words = stop_words.__dict__
    sw_list = stop_words['prepositions']+stop_words['postpositions']
    if not include_phrases:
        if not include_stopwords:
            res_words = []
            for wrd in words:
                if wrd not in sw_list:
                    res_words.append(wrd)
            words = res_words
        return words
    phrases = []
    current_phrase = ''

    phrases, current_phrase = find_phrases_loop(words,stop_words,phrases,current_phrase)

    phrases.append(current_phrase.strip())
    if not include_stopwords:
        res_words = []
        for wrd in phrases:
            if wrd not in sw_list:
                res_words.append(wrd)
        phrases = res_words
    return phrases

#tokenize function splits into small functions
def tokenize_get_longest_match(memory_trie,chunks):
    """search the trie to get the longest matching phrases known to us"""
    updated_chunks = []
    for chunk in chunks:
        temp = chunk
        new_chunks = ['']
        while temp != "":
            key = '/'.join(temp.split())
            lngst = memory_trie.longest_prefix(key)
            if lngst.key is not None:
                new_chunks.append("###"+lngst.key.replace('/',' '))
                temp = temp[len(lngst.key)+1:]
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
    return chunks

def tokenize_get_unique_token(phrases,sent,unique_tokens):
    """get unique tokens for tokenize function"""
    start = 0
    dummy_sent = sent['sentence']
    if 'draftMeta' in sent:
        for meta in sent['draftMeta']:
            if meta[2] == "confirmed":
                # changing the confirmed portions to avoid a phrase being matched in it
                dummy_list = list(dummy_sent)
                for pos in range(meta[0][0], meta[0][1]):
                    dummy_list[pos] = "#"
                dummy_sent = "".join(dummy_list)
    for phrase in phrases:
        if phrase.strip() == '':
            continue
        whole_word_pattern = re.compile(f"(^|\\W)({phrase})(\\W|$)")
        find = re.search(whole_word_pattern, dummy_sent[start:])
        if not find:
            # "Ignoring and moving on."
            # "This would happen when portion of the token is already confirmed"
            log.warning(f"Tokenization: token, {phrase}, "+\
                f"not found in sentence: {sent['sentence']}.")
            continue
        offset = find.start(2) + start
        start = offset+len(phrase)
        if phrase not in unique_tokens:
            unique_tokens[phrase] = {
            "occurrences":[{"sentenceId":sent['sentenceId'],
            "offset":[offset, offset+len(phrase)]}],
            "translations":[]}
        else:
            unique_tokens[phrase]["occurrences"].append(
                {"sentenceId":sent['sentenceId'], "offset":[offset, offset+len(phrase)]})
    return unique_tokens

def tokenize_logic(include_phrases,chunks,include_stopwords,stop_words):
    """Logic for tokenize function"""
    phrases = []
    for chunk in chunks:
        # from the left out words in above step, try forming phrases
        # as <preposition stop word>* <content word> <postposition stop word>*
        if chunk.startswith('###'):
            phrases.append(chunk.replace("###",""))
        else:
            phrases+= find_phrases(chunk,stop_words, include_phrases, include_stopwords)

    if not isinstance(stop_words, dict):
        stop_words = stop_words.__dict__

    return phrases,stop_words

def get_token_trie(db_, src_lang):
    '''either get trie from cache or build one'''
    cached_trie = get_routes_from_cache(key= f"token_trie/{src_lang}")
    if cached_trie is not None:
        memory_trie = pickle.loads(cached_trie)
    else:
        translation_memory = db_.query(db_models.TranslationMemory.token).filter(
            db_models.TranslationMemory.source_language.has(code=src_lang)).all()#pylint: disable=E1101
        reverse_memory = db_.query(db_models.TranslationMemory.translation).filter(
            db_models.TranslationMemory.target_language.has(code=src_lang)).all()#pylint: disable=E1101
        memory_trie = build_memory_trie(translation_memory+reverse_memory)
        value_to_cache = pickle.dumps(memory_trie)
        set_routes_to_cache(key=f"token_trie/{src_lang}", value=value_to_cache)
    return memory_trie


def tokenize(db_:Session, src_lang, sent_list, #pylint: disable=too-many-locals
    use_translation_memory=True, include_phrases=True,**kwargs):
    '''Get phrase and single word tokens and their occurances from input sentence list.
    Performs tokenization using two knowledge resources: translation memory and stopwords list
    input: [(sent_id, sent_text), (sent_id, sent_text), ...]
    output: {"token": [(sent_id, start_offset, end_offset),
                            (sent_id, start_offset, end_offset)..],
             "token": [(sent_id, start_offset, end_offset),
                            (sent_id, start_offset, end_offset)..], ...}'''

    include_stopwords = kwargs.get("include_stopwords",False)
    punctuations = kwargs.get("punctuations",None)
    stop_words = kwargs.get("stop_words",None)
    unique_tokens = {}
    if stop_words is None:
        stop_words = utils.stopwords(src_lang)
    if punctuations is None:
        punctuations = utils.punctuations()+utils.numbers()
    # fetch all known tokens for the language and build a trie with it
    # We do this fresh for every tokenization request. Can be optimized
    if use_translation_memory and include_phrases:
        # redis cache check
        memory_trie = get_token_trie(db_, src_lang)
    for sent in sent_list:
        if not isinstance(sent, dict):
            sent = sent.__dict__
        phrases = []
        src_text = re.sub(r'[\n\r]+', ' ', sent['sentence'])

        #first remove "confirmed" portions from text
        segments = []
        prev_index = 0
        if "draftMeta" in sent:
            for meta in sent['draftMeta']:
                if meta[2] == "confirmed":
                    seg = sent['sentence'][prev_index:meta[0][0]]
                    if len(seg) > 0:
                        segments.append(seg)
                    prev_index = meta[0][1]
        seg = sent['sentence'][prev_index:]
        if len(seg) > 0:
            segments.append(seg)

        #next split the text into chunks based on punctuations
        chunks = []
        for src_text in segments:
            punct_wise_splits = re.split(r'['+"".join(punctuations)+']+', src_text)
            chunks += [chunk.strip() for chunk in punct_wise_splits]

        if use_translation_memory and include_phrases:
            chunks = tokenize_get_longest_match(memory_trie,chunks)

        phrases,stop_words = tokenize_logic(include_phrases,chunks,include_stopwords,stop_words)

        unique_tokens = tokenize_get_unique_token(phrases,sent,unique_tokens)

    return unique_tokens

def replace_token_inside(token_offset, translation, tag, **kwargs):
    '''Replace token when our area of interest overlaps with this segment'''
    src_seg_offset = kwargs.get("src_seg_offset")
    updated_draft = kwargs.get("updated_draft")
    updated_meta = kwargs.get("updated_meta")
    translation_offset = kwargs.get("translation_offset")
    if token_offset[0] == src_seg_offset[0]: #begining is same
        if (updated_draft != "") and (not updated_draft.endswith(" "))\
        and (translation != ""):
            # to have a space b/w existing words and new translation
            updated_draft += " "
            draft_end = len(updated_draft)
            updated_meta.append([[src_seg_offset[0], src_seg_offset[0]],
                [draft_end-1,draft_end],"untranslated"])
        translation_offset[0] = len(updated_draft)
        updated_draft += translation
    elif token_offset[0] > src_seg_offset[0]: # begins within this segment
        draft_end = len(updated_draft)
        updated_meta.append([[src_seg_offset[0], token_offset[0]],
            [draft_end, draft_end],"untranslated"])
        if (updated_draft != "") and (not updated_draft.endswith(" "))\
        and (translation != ""):
            # to have a space b/w existing words and new translation
            updated_draft += " "
            updated_meta.append([[token_offset[0], token_offset[0]],
                [draft_end,draft_end+1],"untranslated"])
        translation_offset[0] = len(updated_draft)
        updated_draft += translation
    else: # begins before this segment
        pass
    if token_offset[1] == src_seg_offset[1]: # ending is the same
        translation_offset[1] = len(updated_draft)
        updated_meta.append((token_offset, translation_offset, tag))
    elif token_offset[1] < src_seg_offset[1]: # ends within this segment
        translation_offset[1] = len(updated_draft)
        updated_meta.append((token_offset, translation_offset, tag))
        updated_meta.append(((token_offset[1], src_seg_offset[1]),
            (translation_offset[1],translation_offset[1]),
            "untranslated"))
    else: # ends after this segment
        pass
    return updated_draft, updated_meta, translation_offset


def replace_token_outside(token_offset, draft, **kwargs):
    '''Replace token when our area of interest doesn't overlap with this segment'''
    src_seg_offset = kwargs.get("src_seg_offset")
    draft_seg_offset = kwargs.get("draft_seg_offset")
    status = kwargs.get("status")
    updated_draft = kwargs.get("updated_draft")
    updated_meta = kwargs.get("updated_meta")
    meta = kwargs.get("meta")
    if src_seg_offset[1] < token_offset[1]: # our area of interest come after this segment
        draft_end = len(updated_draft)
        updated_draft += draft[draft_seg_offset[0]: draft_seg_offset[1]]
        updated_meta.append(meta)
    else: # our area of interest was before this segment
        draft_end = len(updated_draft)
        offset_diff = draft_end - draft_seg_offset[0]
        this_draft_seg = draft[draft_seg_offset[0]: draft_seg_offset[1]]
        if updated_draft=="" or updated_draft.endswith(" ") or this_draft_seg.startswith(" "):
            updated_draft += this_draft_seg
        elif this_draft_seg != "":
            updated_draft += " "+this_draft_seg
            updated_meta.append([[src_seg_offset[0], src_seg_offset[0]],
                [draft_end, draft_end+1], "untranslated"])
            offset_diff += 1
        updated_meta.append([src_seg_offset,
            [draft_seg_offset[0]+offset_diff, draft_seg_offset[1]+offset_diff], status])
    return updated_draft, updated_meta

def replace_token(resource, token_offset, translation,draft_meta, tag="confirmed",#pylint: disable=too-many-locals
    **kwargs):
    '''Make a token replacement in draft and return updated draft and draft_meta.
    Assumption: All characters of resource and draft will have corresponding entry in draftMeta.
    Alignment: draftMeta for words in resource or draft that are not aligned
        for resource word s1-s5: [[1,5],[0,0], "untranslated"]
        for draft word d10-d17: [[8,8],[10,17, "untranslated"]'''
    draft= kwargs.get("draft","")
    updated_meta = []
    updated_draft = ""
    translation_offset = [None, None]
    if draft_meta is None or len(draft_meta) == 0:
        draft = ""
        draft_meta = [[[0,len(resource)], [0,0], "untranslated"]]
    draft_meta = sorted(draft_meta, key=lambda meta: tuple(meta[1])) # sort in order of draft
    for meta in draft_meta:
        src_seg_offset = meta[0]
        draft_seg_offset = meta[1]
        status = meta[2]
        if src_seg_offset[0] == src_seg_offset[1] and src_seg_offset[0] != token_offset[0]:
            intersection = set(range(token_offset[0],token_offset[1])). intersection(
                [src_seg_offset[0]])
        else:
            intersection = set(range(token_offset[0],token_offset[1])).intersection(
                range(src_seg_offset[0],src_seg_offset[1]))
        if len(intersection) > 0: # our area of interest overlaps with this segment
            updated_draft, updated_meta, translation_offset = replace_token_inside(
                token_offset=token_offset,
                translation=translation,
                tag=tag,
                src_seg_offset=src_seg_offset,
                draft_seg_offset=draft_seg_offset,
                status=status,
                updated_draft=updated_draft,
                updated_meta=updated_meta,
                translation_offset=translation_offset
                )
        else:
            updated_draft, updated_meta = replace_token_outside(token_offset=token_offset,
                draft=draft,
                src_seg_offset=src_seg_offset,
                draft_seg_offset=draft_seg_offset,
                status=status,
                updated_draft=updated_draft,
                updated_meta=updated_meta,
                meta=meta
                )
    utils.validate_draft_meta(resource, updated_draft, updated_meta)
    return updated_draft, updated_meta
