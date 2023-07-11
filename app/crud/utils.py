'''Utility functions'''
import subprocess
import json
import itertools

import unicodedata
from unidecode import unidecode
import requests

from custom_exceptions import TypeException, UnprocessableException
#pylint: disable=R1732
def normalize_unicode(text, form="NFKC"):
    '''to normalize text contents before adding them to DB'''
    return unicodedata.normalize(form, text)

def punctuations():
    '''list of punctuations commonly seen in our resource files'''
    return [',', '"', '!', '.', ':', ';', '\n', '\\','“','”',
        '“','*','।','?',';',"'","’","(",")","‘","—"]

def numbers():
    '''list of number characters, to be used along with punctuations'''
    return ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

books = {
1: {"book_code": "gen", "book_name": "genesis"},
2: {"book_code": "exo", "book_name": "exodus"},
3: {"book_code": "lev", "book_name": "leviticus"},
4: {"book_code": "num", "book_name": "numbers"},
5: {"book_code": "deu", "book_name": "deuteronomy"},
6: {"book_code": "jos", "book_name": "joshua"},
7: {"book_code": "jdg", "book_name": "judges"},
8: {"book_code": "rut", "book_name": "ruth"},
9: {"book_code": "1sa", "book_name": "1 samuel"},
10: {"book_code": "2sa", "book_name": "2 samuel"},
11: {"book_code": "1ki", "book_name": "1 kings"},
12: {"book_code": "2ki", "book_name": "2 kings"},
13: {"book_code": "1ch", "book_name": "1 chronicles"},
14: {"book_code": "2ch", "book_name": "2 chronicles"},
15: {"book_code": "ezr", "book_name": "ezra"},
16: {"book_code": "neh", "book_name": "nehemiah"},
17: {"book_code": "est", "book_name": "esther"},
18: {"book_code": "job", "book_name": "job"},
19: {"book_code": "psa", "book_name": "psalms"},
20: {"book_code": "pro", "book_name": "proverbs"},
21: {"book_code": "ecc", "book_name": "ecclesiastes"},
22: {"book_code": "sng", "book_name": "song of solomon"},
23: {"book_code": "isa", "book_name": "isaiah"},
24: {"book_code": "jer", "book_name": "jeremiah"},
25: {"book_code": "lam", "book_name": "lamentations"},
26: {"book_code": "ezk", "book_name": "ezekiel"},
27: {"book_code": "dan", "book_name": "daniel"},
28: {"book_code": "hos", "book_name": "hosea"},
29: {"book_code": "jol", "book_name": "joel"},
30: {"book_code": "amo", "book_name": "amos"},
31: {"book_code": "oba", "book_name": "obadiah"},
32: {"book_code": "jon", "book_name": "jonah"},
33: {"book_code": "mic", "book_name": "micah"},
34: {"book_code": "nam", "book_name": "nahum"},
35: {"book_code": "hab", "book_name": "habakkuk"},
36: {"book_code": "zep", "book_name": "zephaniah"},
37: {"book_code": "hag", "book_name": "haggai"},
38: {"book_code": "zec", "book_name": "zechariah"},
39: {"book_code": "mal", "book_name": "malachi"},
41: {"book_code": "mat", "book_name": "matthew"},
42: {"book_code": "mrk", "book_name": "mark"},
43: {"book_code": "luk", "book_name": "luke"},
44: {"book_code": "jhn", "book_name": "john"},
45: {"book_code": "act", "book_name": "acts"},
46: {"book_code": "rom", "book_name": "romans"},
47: {"book_code": "1co", "book_name": "1 corinthians"},
48: {"book_code": "2co", "book_name": "2 corinthians"},
49: {"book_code": "gal", "book_name": "galatians"},
50: {"book_code": "eph", "book_name": "ephesians"},
51: {"book_code": "php", "book_name": "philippians"},
52: {"book_code": "col", "book_name": "colossians"},
53: {"book_code": "1th", "book_name": "1 thessalonians"},
54: {"book_code": "2th", "book_name": "2 thessalonians"},
55: {"book_code": "1ti", "book_name": "1 timothy"},
56: {"book_code": "2ti", "book_name": "2 timothy"},
57: {"book_code": "tit", "book_name": "titus"},
58: {"book_code": "phm", "book_name": "philemon"},
59: {"book_code": "heb", "book_name": "hebrews"},
60: {"book_code": "jas", "book_name": "james"},
61: {"book_code": "1pe", "book_name": "1 peter"},
62: {"book_code": "2pe", "book_name": "2 peter"},
63: {"book_code": "1jn", "book_name": "1 john"},
64: {"book_code": "2jn", "book_name": "2 john"},
65: {"book_code": "3jn", "book_name": "3 john"},
66: {"book_code": "jud", "book_name": "jude"},
67: {"book_code": "rev", "book_name": "revelation"}
}

BOOK_CODES = [ val['book_code'] for key, val in books.items()]


def book_code(book_num):
    '''get the book for for the input bokk number'''
    if book_num in books:
        return books[book_num]['book_code'].upper()
    return None

known_stopwords = {
    "en": { "postpositions" : ["t", "s"],
             "prepositions": ["am", "is", "are", "was", "were", "be", "been", "being", "have",
                "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and",
                "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for",
                "with", "about", "against", "between", "into", "through", "during", "before",
                "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
                "over", "under", "again", "further", "then", "once", "here", "there", "when",
                "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
                "other", "some", "such", "no", "nor", "not", "only", "same", "so", "than",
                "too", "very", "can", "will", "just", "don", "should"]},
    "hi": { "postpositions" : ["के", "का", "में", "की", "है", "और", "से", "हैं", "को", "पर",
                "होता", "कि","जो", "कर", "मे", "गया", "करने", "किया", "लिये", "ने", "बनी", "नहीं",
                "तो", "ही", "या", "दिया", "हो", "था", "हुआ", "तक", "साथ", "करना", "वाले",
                "बाद", "लिए", "सकते", "ये", "थे", "दो", "होने", "वे", "करते", "करें", "होती", "थी",
                "हुई", "जा", "होते", "हुए", "करता", "तरह", "रहा", "सकता", "रहे", "रखें"],
             "prepositions": ["कोई", "व", "न", "ना", "इसी", "अभी", "जैसे", "सभी", "सबसे",
                "यह", "इस", "एवं", "कुछ", "किसी", "बहुत", "इसे", "उस", "कई", "एस"] }
}

def stopwords(lang):
    '''returns the stopwords if defined for the language. else empty object'''
    if lang in known_stopwords :
        return known_stopwords[lang]
    return {"prepositions":[], "postpositions":[]}

def parse_usfm(usfm_string):
    '''parse an uploaded usfm file using usfm-grammar'''
    file= open("temp.usfm", "w", encoding='utf-8')
    file.write(normalize_unicode(usfm_string))
    file.close()
    process = subprocess.Popen('$(npm -g root)/usfm-grammar/cli.js temp.usfm',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    stdout, stderr = process.communicate()
    if stderr:
        raise TypeException(stderr.decode('utf-8'))
    usfm_json = json.loads(stdout.decode('utf-8'))
    return usfm_json

def form_usfm(json_obj):
    '''convert a usfm-grammar format JSON into usfm'''
    file = open("temp.json", "w", encoding='utf-8')
    json.dump(json_obj, file)
    # file.write(json_obj)
    file.close()
    process = subprocess.Popen('$(npm -g root)/usfm-grammar/cli.js --output=usfm temp.json',
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True)
    stdout, stderr = process.communicate()
    if stderr:
        raise TypeException(stderr.decode('utf-8'))
    usfm_string = stdout.decode('utf-8')
    return usfm_string


def to_eng(data):
    '''Convert to roman/english script.
    Not an acurate transliteration. But good enough for doing soundex'''
    data = normalize_unicode(data)
    return unidecode(data)

def validate_language_tag(tag):
    '''uses an external service to validate newly added language sub tags'''
    url = "https://schneegans.de/lv/?tags=%s&format=json"
    resp = requests.get(url%(tag), timeout=10)
    if resp.status_code != 200:
        resp.raise_for_status()
    return resp.json()[0]['Valid'], ' '.join(resp.json()[0]['Messages'])


def convert_dict_obj_to_pydantic(input_obj, target_class):
    '''convert a graphene input object into specified pydantic model'''
    kwargs = {}
    for key in input_obj:
        kwargs[key] = input_obj[key]
    new_obj = target_class(**kwargs)
    return new_obj

def convert_dict_to_sqlalchemy(input_obj, target_class):
    '''convert a dictionary object into specified db_model object,
    if all key names are identical'''
    kwargs = {}
    for key in input_obj:
        kwargs[key] = input_obj[key]
    new_obj = target_class(**kwargs)
    return new_obj

def validate_draft_meta(sentence, draft, draft_meta):
    '''Check if indices are proper in draftMeta, as per values in sentence and draft'''
    src_segs = [list(meta[0]) for meta in draft_meta]
    trg_segs = [list(meta[1]) for meta in draft_meta]
    try:
        #Ensure the offset ranges dont overlap
        for seg1, seg2 in itertools.product(src_segs, src_segs):
            if seg1 != seg2:
                intersection = set(range(seg1[0],seg1[1])).intersection(
                    range(seg2[0],seg2[1]))
                assert not intersection, f"Resource segments {seg1} and {seg2} overlaps!"
        for seg1, seg2 in itertools.product(trg_segs, trg_segs):
            if seg1 != seg2:
                intersection = set(range(seg1[0],seg1[1])).intersection(
                    range(seg2[0],seg2[1]))
                assert not intersection, f"Target segments {seg1} and {seg2} overlaps!"
        # Ensure the index values are within the range of string length and from left to right
        # and non empty
        src_len = len(sentence)
        for seg in src_segs:
            assert 0 <= seg[0] <= seg[1] <= src_len, f"Resource segment {seg}, is improper!"
        trg_len = len(draft)
        for seg in trg_segs:
            assert 0 <= seg[0] <= seg[1] <= trg_len, f"Target segment {seg}, is improper!"
        for meta in draft_meta:
            assert meta[2] in ['confirmed', 'suggestion', 'untranslated'],\
                "invalid value where confirmed, suggestion or untranslated is expected"

        # Ensure all portions of draft have a target segment corresponding to it
        sorted_trg_segs = sorted(trg_segs)
        pointer = 0
        for seg in sorted_trg_segs:
            assert seg[0] == pointer, "All portions of the draft should have "+\
                                    "a draftmeta segment showing its status. "+\
                                    f"Expecting a draft segment starting with {pointer}"
            pointer = seg[1]
        if trg_len > 0:
            assert sorted_trg_segs[-1][1] == trg_len, "All portions of the draft should have "+\
                                    "a draftmeta segment showing its status. "+\
                                    f"Expecting a draft segment ending in {trg_len}"
    except AssertionError as exe:
        raise UnprocessableException("Incorrect metadata:"+str(exe)) from exe
    except Exception as exe:
        raise UnprocessableException("Incorrect metadata.") from exe
