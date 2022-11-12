"""Test cases for Generic Translation in GQL"""
import re
import csv
import copy
import json
#pylint: disable=E0401
from .test_agmt_translation import assert_positive_get_sentence
from .test_generic_translation import sentence_list,sentences,sample_sent
from .test_gql_agmt_translation import assert_positive_get_tokens_gql
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql
from .conftest import initial_test_users

headers = {"contentType": "application/json", "accept": "application/json"}
headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
query_translate_tkn = """
        query tokentranslate($src:String!,$trg:String!,$udl:Boolean,$sent_list:[SentenceInput]!
,$tkn_tran:[TokenUpdate]!){
  translateToken(sourceLanguage:$src,targetLanguage:$trg,useDataForLearning:$udl,
  sentenceList:$sent_list,tokenTranslations:$tkn_tran){
   	sentenceId
    sentence
    draft
    draftMeta
  }
  }
     """    

query_tokenize = """
        query tokenize($src:String!,$sent_list:[SentenceInput]!,$phrase:Boolean,$sw:Boolean,$tm:Boolean){
  tokenize(sourceLanguage:$src,sentenceList:$sent_list,includePhrases:$phrase,includeStopwords:$sw,
  useTranslationMemory:$tm){
    token
    occurrences{
      sentenceId
      offset
    }
    translationSuggestions
    metaData
  }
}
    """    

def test_tokenize():
    '''Positve tests for generic tokenization API'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    var = {
  "src": "en",
  "sent_list": sentence_list,
  "phrase":True,
  "sw":False,
  "tm":False
}
    #Without Auth
    def_executed = gql_request(query_tokenize,operation="query",variables=var)
    assert "errors" in def_executed
    #With Auth
    def_executed = gql_request(query_tokenize,operation="query",variables=var,
      headers=headers_auth)
    assert len(def_executed["data"]["tokenize"]) > 10
    for item in def_executed["data"]["tokenize"]:
        assert_positive_get_tokens_gql(item)

    var1 = {
  "src": "en",
  "sent_list": sentence_list,
  "phrase":True,
  "sw":False,
  "tm":False
}
    executed = gql_request(query_tokenize,operation="query",variables=var1,
      headers=headers_auth)
    assert len(def_executed["data"]["tokenize"]) == \
        len(executed["data"]["tokenize"])

    var2 = {
  "src": "en",
  "sent_list": sentence_list[:3],
  "phrase":True,
  "sw":False,
  "tm":False
}
    executed2 = gql_request(query_tokenize,operation="query",variables=var2,
      headers=headers_auth)
    for item in def_executed["data"]["tokenize"]:
        assert_positive_get_tokens_gql(item)
    assert len(def_executed["data"]["tokenize"]) > len(executed2["data"]["tokenize"])

    # include_phrases flag false
    var3 = {
  "src": "en",
  "sent_list": sentence_list,
  "phrase":False,
  "sw":False,
  "tm":False
}
    executed3 = gql_request(query_tokenize,operation="query",variables=var3,
      headers=headers_auth)
    assert len(executed3["data"]["tokenize"]) <= \
        len(def_executed["data"]["tokenize"])
    for item in executed3["data"]["tokenize"]:
        assert_positive_get_tokens_gql(item)
        assert " " not in item['token']    

    # include stopwords flag
    sample_stopwords = ["the", "is", "a"]
    var4 = {
  "src": "en",
  "sent_list": sentence_list,
  "phrase":True,
  "sw":False,
  "tm":False
}
    executed4 = gql_request(query_tokenize,operation="query",variables=var4,
      headers=headers_auth)
    for item in executed4["data"]["tokenize"]:
        assert_positive_get_tokens_gql(item)
        assert item['token'] not in sample_stopwords

    var5 = {
  "src": "en",
  "sent_list": sentence_list,
  "phrase":True,
  "sw":True,
  "tm":False
}
    executed5 = gql_request(query_tokenize,operation="query",variables=var5,
      headers=headers_auth)
    for item in executed5["data"]["tokenize"]:
        assert_positive_get_tokens_gql(item)

    var6 = {
  "src": "en",
  "sent_list": sentence_list,
  "phrase":False,
  "sw":True,
  "tm":False
}
    executed6 = gql_request(query_tokenize,operation="query",variables=var6,
      headers=headers_auth)
    all_words = [item['token'] for item in executed6["data"]["tokenize"]]
    for swd in sample_stopwords:
        assert swd in all_words
       
def test_tokenize_with_diff_flags():
    '''Postive tests for tokenizing a single input sentence with varying parameters'''
    
    var = {
  "src": "hi",
  "sent_list": [{
                "sentenceId":1, 
                "sentence":sample_sent}],
            "stopwords":{
                "prepositions":["इस"],
                "postpositions":["के", "की", "है"]
            },
  "phrase":False,
  "sw":True,
  "tm":False
}       

    var_stopword = {"stopwords":{
                "prepositions":["इस"],
                "postpositions":["के", "की", "है"]
            }}

    executed = gql_request(query_tokenize,operation="query",variables=var,  
      headers=headers_auth)
    all_words = [item['token'] for item in executed["data"]["tokenize"]]
    for word in sample_sent.split(): # covers all words in source
        assert word in all_words
    assert len(all_words) == len(set(all_words)) #unique
    for word in all_words: # no phrases
        assert " " not in word

    var["phrase"] = True
    executed1 = gql_request(query_tokenize,operation="query",variables=var,
      headers=headers_auth)
    all_tokens = [item['token'] for item in executed1["data"]["tokenize"]]
    assert "इस प्रकार है" in all_tokens
    assert "इब्राहीम के" in all_tokens

    var["phrase"] = True
    var["sw"] = False
    executed2 = gql_request(query_tokenize,operation="query",variables=var,
      headers=headers_auth)
    all_tokens = [item['token'] for item in executed2["data"]["tokenize"]]
    # no independant stopwords are present
    for swd in var_stopword["stopwords"]['prepositions'] + \
        var_stopword["stopwords"]['postpositions']:
        assert swd not in all_tokens
    assert "इस प्रकार है" in all_tokens # stopwords coming within phrases are included
    assert "इब्राहीम के" in all_tokens

    # make a translation
    post_obj={
  "src": "hi",
  "trg": "en",
  "udl": True,
  "sent_list": [{
                "sentenceId":1,
                "sentence":sample_sent}],
            "stopwords":{
                "prepositions":["इस"],
                "postpositions":["के", "की", "है"]
            },
  "tkn_tran": [
        { "token": "यीशु मसीह",
          "occurrences": [
            { "sentenceId": 1,
              "offset": [31,40]}
          ],
          "translation": "Jesus Christ"}
      ]
}
    #Without Auth
    executed3 = gql_request(query_translate_tkn,operation="query",variables=post_obj)
    assert "errors" in executed3
    #With Auth
    executed3 = gql_request(query_translate_tkn,operation="query",variables=post_obj,
      headers=headers_auth)

    # after a translation testing for use_translation_memory flag
    var["phrase"] = True
    var["sw"] = True
    var["tm"] = True
    executed4 = gql_request(query_tokenize,operation="query",variables=var,headers=headers_auth)
    all_tokens = [item['token'] for item in executed4["data"]["tokenize"]]
    assert "यीशु मसीह" in all_tokens
    assert "की" in all_tokens

    var["phrase"] = True
    var["sw"] = False
    var["tm"] = True
    executed5 = gql_request(query_tokenize,operation="query",variables=var,headers=headers_auth)
    all_tokens = [item['token'] for item in executed5["data"]["tokenize"]]
    assert "यीशु मसीह" in all_tokens
    assert "की" not in all_tokens

    var["tm"] = False
    executed6 = gql_request(query_tokenize,operation="query",variables=var,headers=headers_auth)
    all_tokens = [item['token'] for item in executed6["data"]["tokenize"]]
    assert "यीशु मसीह" not in all_tokens
    assert "यीशु" in all_tokens

def test_token_translate():
    '''Positive tests to apply token translationa nd obtain drafts'''
    headers_auth = {"contentType": "application/json",
                "accept": "application/json"
            }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanUser']['token']
    #tokenize
    var = {
  "src": "hi",
  "sent_list": [{
                "sentenceId":1,
                "sentence":sample_sent}],
            "stopwords":{
                "prepositions":["इस"],
                "postpositions":["के", "की", "है"]
            },
  "phrase":False,
  "sw":True,
  "tm":False
}
    executed = gql_request(query_tokenize,operation="query",variables=var,
      headers=headers_auth)
    all_tokens = executed["data"]["tokenize"]
    for tok in all_tokens:
        assert_positive_get_tokens_gql(tok)
        assert tok != "यीशु मसीह"
    # translate one token
    post_obj={
  "src": "hi",
  "trg": "en",
  "udl": True,
  "sent_list": [{
                "sentenceId":1,
                "sentence":sample_sent}],
            "stopwords":{
                "prepositions":["इस"],
                "postpositions":["के", "की", "है"]
            }
}
    post_obj['tkn_tran'] = [
        { "token": all_tokens[0]['token'],
          "occurrences": [all_tokens[0]['occurrences'][0]],
          "translation": "test"}
      ]
    post_obj["udl"] = False
    executed = gql_request(query_translate_tkn,operation="query",variables=post_obj,
      headers=headers_auth)
    return_sent = executed["data"]["translateToken"][0]
    assert_positive_get_sentence(return_sent)
    assert return_sent['draft'].startswith("test")
    assert return_sent['draftMeta'][0][2] == "confirmed"
    assert return_sent['draftMeta'][1][2] == "untranslated"
    assert len(return_sent['draftMeta']) == 2

    # translate all tokens
    post_obj["udl"] = False
    post_obj["tkn_tran"]= []
    for tok in all_tokens:
        obj = {"token": tok['token'], "occurrences":tok["occurrences"], "translation":"test"}
        post_obj['tkn_tran'].append(obj)
        
    executed2 = gql_request(query_translate_tkn,operation="query",variables=post_obj,
      headers=headers_auth)
    return_sent = executed2["data"]["translateToken"][0]
    assert_positive_get_sentence(return_sent)
    words_in_draft = re.findall(r'\w+',return_sent['draft'])
    for word in words_in_draft:
        assert word == 'test'
    for meta in return_sent['draftMeta']:
        if meta[0][1] - meta[0][0] > 1: # all non space and non-punct parts of input
            assert meta[2] == "confirmed"

    # make a translation for a token not in token list
    # it combines & re-translates 2 already translated tokens
    # and use data for learning
    return_sent_obj = copy.deepcopy(return_sent)
    return_sent_obj["draftMeta"] = json.dumps(return_sent["draftMeta"])
    post_obj["sent_list"] = [return_sent_obj]
    post_obj["udl"] = True
    post_obj['tkn_tran'] = [
        { "token": "यीशु मसीह",
          "occurrences": [
            { "sentenceId": 1,
              "offset": [31,40]}
          ],
          "translation": "Jesus Christ"}
      ]

    executed3 = gql_request(query_translate_tkn,operation="query",variables=post_obj,
      headers=headers_auth)
    new_return_sent = executed3["data"]["translateToken"][0]
    assert "Jesus Christ" in new_return_sent['draft']
    # combined two segments to one
    found_combined = False
    found_seperate = False
    for meta in new_return_sent['draftMeta']:
        match meta[0]:
            case [31, 35]:
                found_seperate = True
            case [36,40]:
                found_seperate = True
            case [31,40]:
                found_combined = True
    assert found_combined
    assert not found_seperate


def test_draft_generation():
    '''tests conversion of sentence list to differnt draft formats'''
    verse_start = 41001001
    for i,sentence in enumerate(sentence_list):
        sentence['sentenceId'] = verse_start+i

    query_usfm = """
      query convertusfm($sentence:[SentenceInput]!){
  convertToUsfm(sentenceList:$sentence)
}
    """
    var = {
        "sentence": sentence_list 
    }
    #Without Auth
    executed = gql_request(query_usfm,operation="query",variables=var)
    assert "errors" in executed
    executed = gql_request(query_usfm,operation="query",variables=var,
      headers=headers_auth)
    assert "\\id MAT" in executed["data"]["convertToUsfm"][0]
    assert sentence_list[0]['sentence'] in executed["data"]["convertToUsfm"][0]

    query_csv = """
      query convertcsv($sentence:[SentenceInput]!){
  convertToCsv(sentenceList:$sentence)
}
    """
    #Without Auth
    executed1 = gql_request(query_csv,operation="query",variables=var)
    assert "errors" in executed1
    #With Auth
    executed1 = gql_request(query_csv,operation="query",variables=var,
      headers=headers_auth)
    assert sentence_list[0]['sentence'] in executed1["data"]["convertToCsv"]
    lines = executed1["data"]["convertToCsv"][0].split('\n')
    parse_csv = True
    try:
        csv.reader(lines)
    except csv.Error:
        parse_csv = False
    assert parse_csv

    query_text = """
      query converttext($sentence:[SentenceInput]!){
  convertToText(sentenceList:$sentence)
}
    """
    #Without Auth
    executed1 = gql_request(query_text,operation="query",variables=var)
    assert "errors" in executed1
    #With Auth
    executed1 = gql_request(query_text,operation="query",variables=var,
      headers=headers_auth)
    input_text = " ".join([sent['sentence'] for sent in sentence_list])
    assert input_text.strip() == executed1["data"]["convertToText"].strip()


    query_alignment = """
      query converttext($sentence:[SentenceInput]!){
  convertToAlignment(sentenceList:$sentence)
}
    """
    var_align = {
  "sentence": [
  {
    "sentenceId": "41001001",
    "sentence": "इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है",
    "draft": "അബ്രാഹാം के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस प्रकार है",
    "draftMeta": "[[[0,8],[0,8],\"confirmed\"],[[8,64],[8,64],\"untranslated\"]]"
  }
]
}
    #Without Auth
    executed2 = gql_request(query_alignment,operation="query",variables=var_align)
    assert "errors" in executed2
    #With auth
    executed2 = gql_request(query_alignment,operation="query",variables=var_align,
      headers=headers_auth)
    assert len(executed2["data"]["convertToAlignment"]) > 0
    assert "metadata" in executed2["data"]["convertToAlignment"].keys()
    assert "segments" in executed2["data"]["convertToAlignment"].keys()
    assert isinstance(executed2["data"]["convertToAlignment"]["segments"],list)
    assert "resources" in executed2["data"]["convertToAlignment"]["segments"][0].keys()
    assert "alignments" in executed2["data"]["convertToAlignment"]["segments"][0].keys()
