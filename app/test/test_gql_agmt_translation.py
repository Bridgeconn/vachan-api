"""Test cases for AGMT Translation in GQL"""
import re
from typing import Dict
#pylint: disable=E0401
from .test_gql_agmt_projects import check_post as create_agmtproject
from .test_gql_agmt_projects import PROJECT_CREATE_GLOBAL_QUERY,bible_books,PROJECT_EDIT_GLOBAL_QUERY
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql,check_skip_limit_gql

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
  "book": ["mat"]
}  

  executed_mat = gql_request(query_with_book,operation="query",variables=var_mat)
  executed_mrk = gql_request(query_with_book,operation="query",variables=var_mrk)
  total_item = len(executed_mat["data"]["agmtProjectTokens"]) + len(executed_mrk["data"]["agmtProjectTokens"])
  assert len(get_resp["data"]["agmtProjectTokens"]) == total_item

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
  assert total_item == len(executed7["data"]["agmtProjectTokens"])

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
  assert total_item == len(executed9["data"]["agmtProjectTokens"])

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
  assert total_item == len(executed11["data"]["agmtProjectTokens"])
  for item in executed11["data"]["agmtProjectTokens"]:
        assert item['token'] not in sample_stopwords

  var = {
  "projectid": project_id,
   "sword": True,
  "phrase": False
}
  executed12 = gql_request(query_swords,operation="query",variables=var)
  assert total_item == len(executed12["data"]["agmtProjectTokens"])
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
    {
  "projectid": project_id,
}
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

def test_save_translation():
  '''Positive tests for PUT tokens method'''  
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
  assert executed3["data"]["applyTokenTranslation"]["message"] == "Token translations saved"
  assert executed3["data"]["applyTokenTranslation"]['data'][0]['draft'].startswith("test translation")  
  assert executed3["data"]["applyTokenTranslation"]['data'][0]['draftMeta'][0][2] == "confirmed"
  for segment in executed3["data"]["applyTokenTranslation"]['data'][0]['draftMeta'][1:]:
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
  assert executed4["data"]["applyTokenTranslation"]["message"] == "Token translations saved"
  for sent in executed4["data"]["applyTokenTranslation"]['data']:
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

  executed5 = gql_request(APPLY_TOKEN,operation="mutation",variables=post_obj_list3)
  assert isinstance(executed5, Dict)
  assert executed5["data"]["applyTokenTranslation"]["message"] == "Token translations saved"
  for sent in executed5["data"]["applyTokenTranslation"]['data']:
        words = re.findall(r'\w+', sent['draft'])
        for wrd in words:
            assert wrd == 'test'

            

  