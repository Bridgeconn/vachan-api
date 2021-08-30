"""Test cases for translation suggetions in GQL"""
import copy
import json
from typing import Dict
#pylint: disable=E0401
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  gql_request,assert_not_available_content_gql,check_skip_limit_gql
from .test_gql_bibles import add_bible
from .test_translation_suggestions import align_data,assert_positive_get_suggetion
from .test_gql_generic_translation import sentence_list

def assert_positive_get_tokens_gql(item):
    '''common tests for a token response object'''
    assert "token" in item
    assert "occurrences" in item
    assert len(item['occurrences']) > 0
    assert "translationSuggestions" in item
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)

tokens_trans = [
    {"token":"test", "translations":["ടെസ്റ്റ്"]},
    {"token":"the", "translations":[""]},
    {"token":"test case", "translations":["ടെസ്റ്റ് കേസ്"]},
    {"token":"deveopler", "translations":["ടെവെലപ്പര്‍"]},
    {"token":"run", "translations":["റണ്‍"]},
    {"token":"pass", "translations":["പാസ്സ്"]},
    {"token":"tested", "translations":["ടെസ്റ്റഡ്", "ടെസ്റ്റ് ചെയ്തു"],
        "tokenMetaData":"{\"tense\":\"past\"}"}
]

Add_Gloss = """
     mutation learngloss($object:InputAddGloss){
  addGloss(glossArg:$object){
 		message
    data{
      token
      translations
      metaData
    }
  }
}
"""

Add_Alignment = """
     mutation learnalignment($object:InputAddAlignment){
  addAlignment(alignmentArg:$object){
 		message
    data{
      token
      translations
      metaData
    }
  }
}
"""

query_tokenize = """
    query tokenize($trg:String,$src:String!,$sent_list:[SentenceInput]!,$phrase:Boolean,$sw:Boolean,$tm:Boolean){
  tokenize(sourceLanguage:$src,sentenceList:$sent_list,includePhrases:$phrase,includeStopwords:$sw,
  useTranslationMemory:$tm,targetLanguage:$trg){
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

def test_learn_n_suggest():
    '''Positive tests for adding knowledge and getting suggestions'''

    # add dictionary
    var = {
  "object": {
    "sourceLanguage": "en",
    "targetLanguage": "ml",
    "data": tokens_trans 
  }
}
    executed = gql_request(Add_Gloss,operation="mutation",variables=var)
    assert executed["data"]["addGloss"]["message"] == "Added to glossary"

    # check if suggestions are given in token list
    var = {
  "src": "en",
  "trg": "ml",
  "sent_list": sentence_list,
  "phrase":True,
  "sw":False,
  "tm":True
}
    def_executed = gql_request(query_tokenize,operation="query",variables=var)
    assert len(def_executed["data"]["tokenize"]) > 10
    found_testcase = False
    found_tested = False 
    for item in def_executed["data"]["tokenize"]:
        if item['token'] == "tested":
            assert "ടെസ്റ്റഡ്" in item['translationSuggestions']
            assert "ടെസ്റ്റ് ചെയ്തു" in item['translationSuggestions']
            assert item["metaData"]["tense"] == "past"
            found_tested = True
        assert_positive_get_tokens_gql(item)
        if item['token'] == "test case":
            assert "ടെസ്റ്റ് കേസ്" in item['translationSuggestions']
            assert item['translationSuggestions']["ടെസ്റ്റ് കേസ്"] == 0
            found_testcase = True
    assert found_tested
    assert found_testcase

    # add alignmnet
    var1 = {
  "object": {
    "sourceLanguage": "en",
    "targetLanguage": "ml",
    "data": align_data
  }
}
    executed1 = gql_request(Add_Alignment,operation="mutation",variables=var1)
    assert executed1["data"]["addAlignment"]["message"] == "Added to Alignments"
    found_lower_developer = False
    for item in executed1["data"]["addAlignment"]['data']:
        if item['token'] == 'developer':
            found_lower_developer = True
    assert found_lower_developer

    # try tokenizing again
    def_executed1 = gql_request(query_tokenize,operation="query",variables=var)
    found_atestcase  = False
    found_lower_developer = False
    for item in def_executed1["data"]["tokenize"]:
        assert_positive_get_tokens_gql(item)
        if item['token'] == 'a test case':
            assert "ഒരു ടെസ്റ്റ് കേസ്" in item['translationSuggestions']
            found_atestcase = True
        if item['token'] == 'developer':
            assert item['translationSuggestions']['ടെവെലപ്പര്‍'] == 1
            found_lower_developer = True
    assert found_atestcase
    assert found_lower_developer

    # get gloss

    # only a dict entry not in draft or alignment
    query_get_gloss = """
        query getgloss($src:String!,$trg:String!,$token:String!,$context:String,$tknoffset:[Int]){
  gloss(sourceLanguage:$src,targetLanguage:$trg,token:$token,context:$context,tokenOffset:$tknoffset){
    token
    translations
    metaData
  }
}
    """    
    var3 = {
  "src": "en",
 	 "trg": "ml",
  "token": "test"
}
    executed3 = gql_request(query_get_gloss,operation="query",variables=var3)
    assert isinstance(executed3["data"]["gloss"], dict)
    assert len(executed3["data"]["gloss"]['translations']) > 0
    assert_positive_get_suggetion(executed3["data"]["gloss"])
    found_test = False
    for item in executed3["data"]["gloss"]['translations']:
        if item == "ടെസ്റ്റ്":
            found_test = True
    assert found_test

    # learnt from alignment
    var4 = {
  "src": "en",
 	 "trg": "ml",
  "token": "a test case"
}
    executed4 = gql_request(query_get_gloss,operation="query",variables=var4)
    assert isinstance(executed4["data"]["gloss"], dict)
    assert len(executed4["data"]["gloss"]['translations']) > 0
    assert_positive_get_suggetion(executed4["data"]["gloss"])
    found_atestcase = False
    for item in executed4["data"]["gloss"]['translations']:
        if item == "ഒരു ടെസ്റ്റ് കേസ്":
            found_atestcase = True
    assert found_atestcase

    # with different contexts
    sense1 = "സന്തോഷവാന്‍"
    sense2 = "സന്തോഷവാന്‍ ആയ"

    #no context
    var4 = {
  "src": "en",
 	 "trg": "ml",
  "token": "happy"
}
    executed5 = gql_request(query_get_gloss,operation="query",variables=var4)
    assert isinstance(executed5["data"]["gloss"], dict)
    assert len(executed5["data"]["gloss"]['translations']) > 0
    assert_positive_get_suggetion(executed5["data"]["gloss"])
    found_sense1 = False
    found_sense2 = False
    for item in executed5["data"]["gloss"]['translations']:
        if item == sense1:
            found_sense1 = True
            score1 = executed5["data"]["gloss"]['translations'][item]
        if item == sense2:
            found_sense2 = True
            score2 = executed5["data"]["gloss"]['translations'][item]
    assert found_sense1
    assert found_sense2
    assert score1 == score2

    # context 1
    var6 = {
  "src": "en",
 	 "trg": "ml",
  "token": "happy",
  "context":"the happy user went home"

}
    executed6 = gql_request(query_get_gloss,operation="query",variables=var6)
    assert isinstance(executed6["data"]["gloss"], dict)
    assert len(executed6["data"]["gloss"]['translations']) > 0
    assert_positive_get_suggetion(executed6["data"]["gloss"])
    found_sense1 = False
    found_sense2 = False
    for item in executed6["data"]["gloss"]['translations']:
        if item == sense1:
            found_sense1 = True
            score1 = executed6["data"]["gloss"]['translations'][item]
        if item == sense2:
            found_sense2 = True
            score2 = executed6["data"]["gloss"]['translations'][item]
    assert found_sense1
    assert found_sense2
    assert score1 < score2

    # context 2
    var7 = {
  "src": "en",
 	 "trg": "ml",
  "token": "happy",
  "context":"now user is not happy"

}
    executed7 = gql_request(query_get_gloss,operation="query",variables=var7)
    assert isinstance(executed7["data"]["gloss"], dict)
    assert len(executed7["data"]["gloss"]['translations']) > 0
    assert_positive_get_suggetion(executed7["data"]["gloss"])
    found_sense1 = False
    found_sense2 = False
    for item in executed7["data"]["gloss"]['translations']:
        if item == sense1:
            found_sense1 = True
            score1 = executed7["data"]["gloss"]['translations'][item]
        if item == sense2:
            found_sense2 = True
            score2 = executed7["data"]["gloss"]['translations'][item]
    assert found_sense1
    assert found_sense2
    assert score1 > score2

    # auto translate
    sentence_list[0]['sentence'] = "This his wish "+sentence_list[0]['sentence']

    suggest_translation_query = """
       query suggesttranslation($source_lan:String!,$target_lan:String!,$sentenceList:[SentenceInput]!,
$punctuations:[String],$stopwords:Stopwords){
  suggestTranslation(sourceLanguage:$source_lan,targetLanguage:$target_lan,sentenceList:$sentenceList,
  punctuations:$punctuations,stopwords:$stopwords){
    sentenceId
    sentence
    draft
    draftMeta
  }
}
    """
    var_suggest = {
  "source_lan": "en",
  "target_lan": "ml",
  "sentenceList": sentence_list
}
  
    query_text = """
      query converttext($sentence:[SentenceInput]!){
  convertToText(sentenceList:$sentence)
}
    """

    executed_sug = gql_request(suggest_translation_query,operation="query",variables=var_suggest)
    input = executed_sug["data"]["suggestTranslation"]
    for item in input:
      item["draftMeta"] = json.dumps(item["draftMeta"])

    var_text = {
  "sentence": input
}
    
    draft = gql_request(query_text,operation="query",variables=var_text)
    assert "ഒരു ടെസ്റ്റ് കേസ്." in draft["data"]["convertToText"]
    assert "ടെസ്റ്റ് കേസ് ടെസ്റ്റ് ചെയ്തു" in draft["data"]["convertToText"] or "ടെസ്റ്റ് കേസ് ടെസ്റ്റഡ്" in draft["data"]["convertToText"]
    assert "ടെവെലപ്പര്‍" in draft["data"]["convertToText"]
    assert "ഇത് ആണ്  sad story of a poor ടെസ്റ്റ് " in draft["data"]["convertToText"]

