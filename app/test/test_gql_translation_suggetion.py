"""Test cases for translation suggetions in GQL"""
import json
from typing import Dict
#pylint: disable=E0401
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  gql_request,assert_not_available_content_gql,check_skip_limit_gql
from .test_gql_bibles import add_bible
from .test_translation_suggestions import align_data,assert_positive_get_suggetion

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
    {"token":"test case", "translations":["ടെസ്റ്റ് കേസ്"]},
    {"token":"deveopler", "translations":["ടെവെലപ്പര്‍"]},
    {"token":"run", "translations":["റണ്‍"]},
    {"token":"pass", "translations":["പാസ്സ്"]},
    {"token":"tested", "translations":["ടെസ്റ്റഡ്", "ടെസ്റ്റ് ചെയ്തു"],
        "tokenMetaData":"{\"tense\":\"past\"}"}
]        

APPLY_TOKEN = """
    mutation applytoken($object:InputApplyToken){
  applyTokenTranslation(tokenArg:$object){
    message
    data{
      sentenceId
      sentence
      draft
      draftMeta
    }
  }
}
"""

GET_TOKEN_SENTANCE = """
    mutation gettokensentance($object:InputGetSentance){
  getTokenSentances(tokenArg:$object){
 		data{
      sentenceId
      sentence
      draft
      draftMeta
    }
  }
}
"""

project_data = {
     "object": {
    "projectName": "Test agmt workflow",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
  }
}

sample_stopwords = ["के", "की"]

#above just for test remove after 

Add_Gloss = """
     mutation learngloss($object:InputAddGloss){
  addGloss(infoArg:$object){
 		message
    data{
      token
      translations
      metaData
    }
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