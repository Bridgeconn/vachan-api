"""Test cases for AGMT Translation in GQL"""
from math import floor,ceil
import re
from typing import Dict
#pylint: disable=E0401
from .test_gql_agmt_projects import check_post as create_agmtproject
from .test_gql_agmt_projects import PROJECT_CREATE_GLOBAL_QUERY,bible_books,PROJECT_EDIT_GLOBAL_QUERY
from .test_agmt_translation import assert_positive_get_sentence
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql

def assert_positive_get_tokens_gql(item):
    '''common tests for a token response object'''
    assert "token" in item
    assert "occurrences" in item
    assert len(item['occurrences']) > 0
    assert "translationSuggestions" in item
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)

APPLY_TOKEN = """
    mutation applytoken($object:InputApplyToken){
  agmtApplyTokenTranslation(tokenArg:$object){
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
  agmtGetTokenSentances(tokenArg:$object){
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

def test_get_tokens():
  '''Positive tests for tokenization process'''
  resp = create_agmtproject(PROJECT_CREATE_GLOBAL_QUERY,project_data)
  new_project = resp["data"]["createAgmtProject"]["data"]
  project_id = new_project["projectId"]

  # before adding books
  token_get_query = """
      query get_token($projectid:ID!){
  agmtProjectTokens(projectId:$projectid){
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
  var ={
"projectid": project_id
}
  get_resp = gql_request(token_get_query,operation="query",variables=var)
  assert_not_available_content_gql(get_resp["data"]["agmtProjectTokens"])

  put_data = {
     "object": {
        "projectId":int(new_project['projectId']),
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
  }
}  
  executed2 = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
  assert isinstance(executed2, Dict)
  assert executed2["data"]["editAgmtProject"]["message"] == "Project updated successfully"

  # after adding books  
  get_resp = gql_request(token_get_query,operation="query",variables=var)
  assert isinstance(get_resp, Dict)
  for item in get_resp["data"]["agmtProjectTokens"]:
      assert_positive_get_tokens_gql(item)
    

  # with book filter
  query_with_book = """
       query get_token($projectid:ID!,$book:[String]!){
  agmtProjectTokens(projectId:$projectid,books:$book){
    token
  }
}
  """ 
  var_mat = {
  "projectid": project_id,
  "book": ["mat"]
}
  var_mrk = {
  "projectid": project_id,
  "book": ["mrk"]
}  

  executed_mat = gql_request(query_with_book,operation="query",variables=var_mat)
  executed_mrk = gql_request(query_with_book,operation="query",variables=var_mrk)
  total_item = len(executed_mat["data"]["agmtProjectTokens"]) + len(executed_mrk["data"]["agmtProjectTokens"])
  assert len(executed_mat["data"]["agmtProjectTokens"]) == total_item - \
    len(executed_mrk["data"]["agmtProjectTokens"])

  # with range filter
  query_sentance_idrange = """
     query get_token($projectid:ID!,$sen_range:[Int]!){
  agmtProjectTokens(projectId:$projectid,sentenceIdRange:$sen_range){
    token
  }
}
  """
  var = {
  "projectid": project_id,
  "sen_range": [0,10]
}
  executed3 = gql_request(query_sentance_idrange,operation="query",variables=var)
  assert_not_available_content_gql(executed3["data"]["agmtProjectTokens"])

  var = {
  "projectid": project_id,
  "sen_range": [41000000,41999999]
}

  executed4 = gql_request(query_sentance_idrange,operation="query",variables=var)
  assert len(executed4["data"]["agmtProjectTokens"]) == len(executed_mat["data"]["agmtProjectTokens"])

  # with list filter
  query_sentance_list = """
     query get_token($projectid:ID!,$sen_list:[Int]!){
  agmtProjectTokens(projectId:$projectid,sentenceIdList:$sen_list){
    token
  }
}
  """
  var = {
  "projectid": project_id,
   "sen_list": [41000000]
}
  executed5 = gql_request(query_sentance_list,operation="query",variables=var)
  assert_not_available_content_gql(executed5["data"]["agmtProjectTokens"])

  var = {
  "projectid": project_id,
   "sen_list": [41001001]
}
  executed6 = gql_request(query_sentance_list,operation="query",variables=var)
  assert 0 < len(executed6["data"]["agmtProjectTokens"]) < 25

  # translation_memory flag
  query_memory_flag = """
     query get_token($projectid:ID!,$memory:Boolean){
  agmtProjectTokens(projectId:$projectid,useTranslationMemory:$memory){
    token
  }
}
  """
  var = {
  "projectid": project_id,
   "memory": True
}
  executed7 = gql_request(query_memory_flag,operation="query",variables=var)
  assert len(get_resp["data"]["agmtProjectTokens"]) == len(executed7["data"]["agmtProjectTokens"])

  var = {
  "projectid": project_id,
   "memory": False
}
  executed8 = gql_request(query_memory_flag,operation="query",variables=var)
  assert len(executed8["data"]["agmtProjectTokens"]) > 0

  # include_phrases flag
  query_phrases = """
     query get_token($projectid:ID!,$phrase:Boolean){
  agmtProjectTokens(projectId:$projectid,includePhrases:$phrase){
    token
  }
}
  """
  var ={
  "projectid": project_id,
   "phrase": True
}
  executed9 = gql_request(query_phrases,operation="query",variables=var)
  assert len(get_resp["data"]["agmtProjectTokens"]) == len(executed9["data"]["agmtProjectTokens"])

  var ={
  "projectid": project_id,
   "phrase": False
}
  executed10 = gql_request(query_phrases,operation="query",variables=var)
  assert len(executed10["data"]["agmtProjectTokens"]) <= len(executed9["data"]["agmtProjectTokens"])
  for item in executed10["data"]["agmtProjectTokens"]:
        assert " " not in item['token']

  # include_stopwords flag
  query_swords = """
      query get_token($projectid:ID!,$sword:Boolean,$phrase:Boolean){
  agmtProjectTokens(projectId:$projectid,includeStopwords:$sword,includePhrases:$phrase){
    token
  }
}
  """
  var = {
  "projectid": project_id,
   "sword": False,
  "phrase": True
}
  executed11 = gql_request(query_swords,operation="query",variables=var)
  assert len(get_resp["data"]["agmtProjectTokens"]) == len(executed11["data"]["agmtProjectTokens"])
  for item in executed11["data"]["agmtProjectTokens"]:
        assert item['token'] not in sample_stopwords

  var = {
  "projectid": project_id,
   "sword": True,
  "phrase": False
}
  executed12 = gql_request(query_swords,operation="query",variables=var)
  all_tokens = [item['token'] for item in executed12["data"]["agmtProjectTokens"]]
  assert sample_stopwords[0] in all_tokens

def test_tokenization_invalid():
  '''Negative tests for tokenization'''
  resp = create_agmtproject(PROJECT_CREATE_GLOBAL_QUERY,project_data)
  new_project = resp["data"]["createAgmtProject"]["data"]
  project_id = new_project["projectId"]

  # non existant project
  query_non = """
     query get_token($projectid:ID!){
    agmtProjectTokens(projectId:$projectid){
    token
  }
}
  """
  var = {
  "projectid": project_id+1,
}
  
  executed = gql_request(query_non,operation="query",variables=var)
  assert "errors" in executed.keys()

  #invalid book
  query_invalid_book = """
    query get_token($projectid:ID!,$book:[String]!){
  agmtProjectTokens(projectId:$projectid,books:$book){
    token
  }
}
  """ 
  var = {
  "projectid": project_id,
  "book": ["mmm"]
}
  executed1 = gql_request(query_invalid_book,operation="query",variables=var)
  assert "errors" in executed1.keys()

  # only one value for range
  query_sentance_idrange = """
     query get_token($projectid:ID!,$sen_range:[Int]!){
  agmtProjectTokens(projectId:$projectid,sentenceIdRange:$sen_range){
    token
  }
}
  """
  var = {
  "projectid": project_id,
  "sen_range": [0]
}
  executed2 = gql_request(query_sentance_idrange,operation="query",variables=var)
  assert "errors" in executed2.keys()

  # incorrect value for range
  var = {
  "projectid": project_id,
  "sen_range": "gen"
}
  executed3 = gql_request(query_sentance_idrange,operation="query",variables=var)
  assert "errors" in executed3.keys()

def create_project_get_alltoken():
  """create a project and get all token"""
  resp = create_agmtproject(PROJECT_CREATE_GLOBAL_QUERY,project_data)
  new_project = resp["data"]["createAgmtProject"]["data"]
  project_id = new_project["projectId"]

  put_data = {
     "object": {
        "projectId":int(project_id),
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
  }
}  
  executed = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
  assert isinstance(executed, Dict)
  assert executed["data"]["editAgmtProject"]["message"] == "Project updated successfully"

  token_get_query = """
      query get_token($projectid:ID!,$sword:Boolean){
  agmtProjectTokens(projectId:$projectid,includeStopwords:$sword){
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
  var ={
"projectid": project_id,
"sword": True
}
  executed2 = gql_request(token_get_query,operation="query",variables=var)
  all_tokens = executed2["data"]["agmtProjectTokens"]
  
  return project_id , all_tokens

def test_save_translation():
  '''Positive tests for PUT tokens method'''
  project_id , all_tokens =  create_project_get_alltoken() 

  # one occurence
  post_obj_list = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "token": all_tokens[0]['token'],
      "occurrences": [all_tokens[0]["occurrences"][0]],
      "translation": "test translation"
    }
    ]
  }
}

  executed3 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj_list)
  assert isinstance(executed3, Dict)
  assert executed3["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"
  assert executed3["data"]["agmtApplyTokenTranslation"]['data'][0]['draft'].startswith("test translation")  
  assert executed3["data"]["agmtApplyTokenTranslation"]['data'][0]['draftMeta'][0][2] == "confirmed"
  for segment in executed3["data"]["agmtApplyTokenTranslation"]['data'][0]['draftMeta'][1:]:
    assert segment[2] != "confirmed"

  # multiple occurances
  post_obj_list2 = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "token": all_tokens[0]['token'],
      "occurrences": all_tokens[0]["occurrences"],
      "translation": "test translation"
    }
    ]
  }
}
  executed4 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj_list2)
  assert isinstance(executed4, Dict)
  assert executed4["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"
  for sent in executed4["data"]["agmtApplyTokenTranslation"]['data']:
    assert "test translation" in sent['draft']

  # all tokens at once
  post_obj_list3 = []
  for item in all_tokens:
      obj = {
          "token": item['token'],
          "occurrences": item["occurrences"],
          "translation": "test"
      }
      post_obj_list3.append(obj)
  
  post_list3 = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": post_obj_list3
  }
}   

  executed5 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_list3)
  assert isinstance(executed5, Dict)
  assert executed5["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"
  for sent in executed5["data"]["agmtApplyTokenTranslation"]['data']:
        words = re.findall(r'\w+', sent['draft'])
        for wrd in words:
            assert wrd == 'test'

            
def test_save_translation_invalid():
  '''Negative tests for PUT tokens method'''
  project_id , all_tokens =  create_project_get_alltoken() 
  
  # incorrect project id
  post_obj = {
  "object": {
    "projectId": project_id+1,
    "returnDrafts": True,
    "token": [
      {
      "token": all_tokens[0]['token'],
      "occurrences": all_tokens[0]["occurrences"],
      "translation": "sample translation"
    }
    ]
  }
}
  executed3 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj)
  assert "errors" in executed3.keys()

  # without token
  post_obj = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "occurrences": all_tokens[0]["occurrences"],
      "translation": "sample translation"
    }
    ]
  }
}
  executed4 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj)
  assert "errors" in executed4.keys()

  # without occurences
  post_obj = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
       "token": all_tokens[0]['token'], 
      "translation": "sample translation"
    }
    ]
  }
}
  executed5 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj)
  assert "errors" in executed5.keys()

  # without translation
  post_obj = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "token": all_tokens[0]['token'],
      "occurrences": all_tokens[0]["occurrences"]
    }
    ]
  }
}
  executed6 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj)
  assert "errors" in executed6.keys()

  # incorrect occurences
  wrong_occur = all_tokens[0]["occurrences"][0]
  wrong_occur['sentenceId'] = 0
  post_obj = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "token": all_tokens[0]['token'],
      "occurrences": [wrong_occur],
      "translation": "sample translation"
    }
    ]
  }
}
  executed7 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj)
  assert "errors" in executed7.keys()

  # wrong token-occurence pair
  post_obj = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "token": all_tokens[0]['token'],
        "occurrences": all_tokens[1]['occurrences'],
        "translation": "sample translation"
    }
    ]
  }
}
  executed8 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj)
  assert "errors" in executed8.keys()

def test_drafts():
  '''End to end test from tokenization to draft generation'''
  project_id , all_tokens =  create_project_get_alltoken() 
  # translate all tokens at once
  post_obj_list = []
  for item in all_tokens:
      obj = {
          "token": item['token'],
          "occurrences": item["occurrences"],
          "translation": "test"
      }
      post_obj_list.append(obj)

  post_list = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": post_obj_list
  }
}   

  executed = gql_request(APPLY_TOKEN,operation="mutation",variables=post_list)
  assert isinstance(executed, Dict)
  assert executed["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"

  query_draftusfm = """
      query draft($projectid:ID!){
    agmtDraftUsfm(projectId:$projectid)
}
  """
  var = {
  "projectid": project_id,
}
  executed1 = gql_request(query_draftusfm,operation="query",variables=var)
  assert "\\v 1 test test test" in executed1["data"]["agmtDraftUsfm"][0]

  query_draftusfm_book = """
    query draft($projectid:ID!,$book:[String]){
    agmtDraftUsfm(projectId:$projectid,books:$book)
}
  """
  var = {
  "projectid": project_id,
  "book": ["mat"]
}
  executed2 = gql_request(query_draftusfm_book,operation="query",variables=var)
  assert len(executed2["data"]["agmtDraftUsfm"]) == 1
  assert "\\id MAT" in executed2["data"]["agmtDraftUsfm"][0]

  # To be added: proper tests for alignment json drafts
  query_alignment = """
    query alignment($projectid:ID!){
    agmtExportAlignment(projectId:$projectid)
}
  """
  var = {
  "projectid": project_id
}
  executed3 = gql_request(query_alignment,operation="query",variables=var)
  assert isinstance(executed3["data"]["agmtExportAlignment"], dict)

def test_get_token_sentences():
  '''Check if draft-meta is properly segemneted according to specifed token occurence'''
  project_id , all_tokens =  create_project_get_alltoken()
  our_token = all_tokens[0]['token']
  occurrences = all_tokens[0]['occurrences']

  #before translating
  var_sentance = {
  "object": {
    "projectId": project_id,
    "token": our_token,
    "occurance": occurrences
  }
}
  executed = gql_request(GET_TOKEN_SENTANCE,operation="mutation",variables=var_sentance)
  for sent, occur in zip(executed["data"]["agmtGetTokenSentances"]["data"], occurrences):
    assert_positive_get_sentence(sent)
    found_slice = False
    if sent['sentenceId'] == occur["sentenceId"]:
        for meta in sent['draftMeta']:
            if meta[0] == occur['offset']:
                found_slice = True
    assert found_slice

  post_obj_list = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": [
      {
      "token": our_token,
      "occurrences": occurrences,
      "translation": "sample"
    }
    ]
  }
}

  executed2 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj_list)
  assert isinstance(executed2, Dict)
  assert executed2["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"

  # after translation
  executed3 = gql_request(GET_TOKEN_SENTANCE,operation="mutation",variables=var_sentance)
  for sent, occur in zip(executed3["data"]["agmtGetTokenSentances"]["data"], occurrences):
        found_slice = False
        if sent['sentenceId'] == occur["sentenceId"]:
            for meta in sent['draftMeta']:
                if meta[0] == occur['offset']:
                    found_slice = True
                    assert meta[2] == "confirmed"
        assert found_slice

def test_get_sentence():
  '''Positive test for agmt sentence/draft fetch API'''
  project_id , all_tokens =  create_project_get_alltoken()

  # before translation
  query_projectsource = """
    query projectsource($id:ID!){
  agmtProjectSource(projectId:$id){
    sentenceId
    sentence
    draft
    draftMeta
  }
}
  """
  var = {
  "id": project_id
}
  executed = gql_request(query_projectsource,operation="query",variables=var)
  assert len(executed["data"]["agmtProjectSource"]) > 0
  for item in executed["data"]["agmtProjectSource"]:
        assert_positive_get_sentence(item)
        assert item['sentence'] == item['draft']

  # translate all tokens at once
  post_obj_list = []
  for item in all_tokens:
      obj = {
          "token": item['token'],
          "occurrences": item["occurrences"],
          "translation": "test"
      }
      post_obj_list.append(obj)

  post_list = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": post_obj_list
  }
}
  executed1 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_list)
  assert isinstance(executed1, Dict)
  assert executed1["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"
  # after token translation
  executed2 = gql_request(query_projectsource,operation="query",variables=var)
  assert len(executed2["data"]["agmtProjectSource"]) > 0
  for item in executed2["data"]["agmtProjectSource"]:
        assert_positive_get_sentence(item)
        words = re.findall(r'\w+',item['draft'])
        for wrd in words:
            assert wrd == "test"  

def test_progress_n_suggestion():
  '''tests for project progress API of AgMT'''
  resp = create_agmtproject(PROJECT_CREATE_GLOBAL_QUERY,project_data)
  new_project = resp["data"]["createAgmtProject"]["data"]
  project_id = new_project["projectId"]

  # before adding books 
  query_progress = """
    query projectprogress($id:ID!){
  agmtProjectProgress(projectId:$id){
   confirmed
    suggestion
    untranslated
  }
}
  """
  var_prog = {
  "id": project_id
}
  executed_prog = gql_request(query_progress,operation="query",variables=var_prog)
  assert executed_prog["data"]["agmtProjectProgress"]['confirmed'] == 0
  assert executed_prog["data"]["agmtProjectProgress"]['untranslated'] == 0
  assert executed_prog["data"]["agmtProjectProgress"]['suggestion'] == 0

  put_data = {
     "object": {
        "projectId":int(project_id),
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']]
  }
}  
  executed = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation", variables=put_data)
  assert isinstance(executed, Dict)
  assert executed["data"]["editAgmtProject"]["message"] == "Project updated successfully"

  # before translation
  executed_prog1 = gql_request(query_progress,operation="query",variables=var_prog)
  assert executed_prog1["data"]["agmtProjectProgress"]['confirmed'] == 0
  assert executed_prog1["data"]["agmtProjectProgress"]['untranslated'] == 1
  assert executed_prog1["data"]["agmtProjectProgress"]['suggestion'] == 0

  token_get_query = """
      query get_token($projectid:ID!,$sword:Boolean){
  agmtProjectTokens(projectId:$projectid,includeStopwords:$sword){
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
  var ={
"projectid": project_id,
"sword": True
}
  executed2 = gql_request(token_get_query,operation="query",variables=var)
  all_tokens = executed2["data"]["agmtProjectTokens"]

  # translate all tokens at once
  post_obj_list = []
  for item in all_tokens:
      obj = {
          "token": item['token'],
          "occurrences": item["occurrences"],
          "translation": "test"
      }
      post_obj_list.append(obj)

  post_list = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": post_obj_list
  }
}   

  executed = gql_request(APPLY_TOKEN,operation="mutation",variables=post_list)
  assert isinstance(executed, Dict)
  assert executed["data"]["agmtApplyTokenTranslation"]["message"] == "Token translations saved"

  # after token translation
  executed_prog2 = gql_request(query_progress,operation="query",variables=var_prog)
  assert ceil(executed_prog2["data"]["agmtProjectProgress"]['confirmed']) == 1
  assert floor(executed_prog2["data"]["agmtProjectProgress"]['untranslated']) == 0
