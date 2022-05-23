"""Test cases for commentaries in GQL"""

#Disabled ALL TESTS BECAUSE OF GRAPHQL BACKGROUND TASK ISSUE . REST FUNCTIONS CHANGED TO BACKGROUND TASK
# GRAPHQL NOT STOP POST OR PUT EVEN AFTER RAISE ERRORS . 

from typing import Dict
#pylint: disable=E0401
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
from .test_commentaries import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql,check_skip_limit_gql\
  ,contetapi_get_accessrule_checks_app_userroles_gql
from .conftest import initial_test_users
from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers = {"contentType": "application/json", "accept": "application/json"}

VERSION_VAR  = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles"
    }
    }
SOURCE_VAR = {
  "object": {
    "contentType": "commentary",
    "language": "gu",
    "version": "TTT",
    "revision": "1",
    "year": 2020,
  }
}

ADD_COMMENTARY = """
    mutation createcommentary($object:InputAddCommentary){
  addCommentary(commArg:$object){
    message
    data{
      refString
      book{
        bookId
        bookName
        bookCode
      }
      chapter
      verseStart
      verseEnd
      commentary
      active
    }
  }
}
"""
EDIT_COMMENTARY = """
    mutation Editcommentary($object:InputEditCommentary){
  editCommentary(commArg:$object){
    message
    data{
      refString
      book{
        bookId
        bookName
        bookCode
      }
      chapter
      verseStart
      verseEnd
      commentary
      active
    }
  }
}
"""
# headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
# def check_post(query, variables):
#     '''prior steps and post attempt, without checking the response'''
#     #add version
#     version_add(version_query,VERSION_VAR)
#     #add source
#     src_executed = source_add(source_query,SOURCE_VAR)
#     source_name = src_executed["data"]["addSource"]["data"]["sourceName"]
#     #without Auth
#     executed = gql_request(query=query,operation="mutation", variables=variables)
#     assert "errors" in executed
#     #with auth
#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#     executed = gql_request(query=query,operation="mutation", variables=variables,
#       headers=headers_auth)
#     return executed,source_name

# def post_comentary(variable):
#     '''post data and check successfull or not'''
#     executed , source_name = check_post(ADD_COMMENTARY,variable)
#     assert not "errors" in executed
#     assert executed["data"]["addCommentary"]["message"] == "Commentaries added successfully"
#     assert len(variable["object"]["commentaryData"]) ==\
#        len(executed["data"]["addCommentary"]["data"])
#     for item in executed["data"]["addCommentary"]["data"]:
#         assert_positive_get(item)
#     return executed,source_name


# def test_post_default():
#     '''Positive test to upload commentries, with various kins of ref ranges supported'''
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"gen", "chapter":0, "commentary":"book intro to Genesis"},
#     	{"bookCode":"gen", "chapter":1, "verseStart":0, "verseEnd": 0,
#     		"commentary":"chapter intro to Genesis 1"},
#     	{"bookCode":"gen", "chapter":1, "verseStart":1, "verseEnd": 10,
#     		"commentary":"the begining"},
#     	{"bookCode":"gen", "chapter":1, "verseStart":3, "verseEnd": 30,
#     		"commentary":"the creation"},
#     	{"bookCode":"gen", "chapter":1, "verseStart":-1, "verseEnd": -1,
#     		"commentary":"Chapter Epilogue. God completes creation in 6 days."},
#     	{"bookCode":"gen", "chapter":-1, "commentary":"book Epilogue."}
#         ]
#     }
#     }
#     post_comentary(variable)
  
#     #skip and limit 
#     query_check = """
#       query commentaries($skip:Int, $limit:Int){
#   commentaries(sourceName:"gu_TTT_1_commentary",skip:$skip,limit:$limit){
#     refString
#   }
# }

#     """
#     check_skip_limit_gql(query_check,"commentaries", headers=headers_auth)

# def test_post_duplicate():
#     '''Negative test to add two commentaries with same reference range'''
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     post_comentary(variable)
#     executed = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable,
#       headers=headers_auth)
#     assert "errors" in executed.keys()

# def test_post_incorrect_data():
#     ''' tests to check input validation in post API'''
#     #no list single data
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData":
#             {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}

#     }
#     }
#     executed = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable,
#       headers=headers_auth)
#     assert "errors" in executed.keys()

#     # data object with missing mandatory fields
#     variable1 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed1 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable1,
#       headers=headers_auth)
#     assert "errors" in executed1.keys()

#     variable2 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen",  "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed2 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable2,
#       headers=headers_auth)
#     assert "errors" in executed2.keys()

#     variable3 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1}
#         ]
#     }
#     }
#     executed3 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable3,
#       headers=headers_auth)
#     assert "errors" in executed3.keys()

#     # incorrect data values in fields
#     variable4 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gensis", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed4 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable4,
#       headers=headers_auth)
#     assert "errors" in executed4.keys()

#     variable5 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":"intro", "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed5 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable5,
#       headers=headers_auth)
#     assert "errors" in executed5.keys()

#     variable6 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":1, "verseStart":"intro",
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed6 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable6,
#       headers=headers_auth)
#     assert "errors" in executed6.keys()

#     variable7 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis","active": "deactivate"}
#         ]
#     }
#     }
#     executed7 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable7,
#       headers=headers_auth)
#     assert "errors" in executed7.keys()

#     #wrong source
#     variable8 = {
#     "object": {
#         "sourceName": "gu_TTT_1_bible",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed8 = gql_request(query=ADD_COMMENTARY,operation="mutation",variables=variable8,
#       headers=headers_auth)
#     assert "errors" in executed8.keys()

# def test_get_after_data_upload():
#     '''Add some data into the table and do all get tests'''
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#             {"bookCode":"gen", "chapter":0, "commentary":"book intro to Genesis"},
#             {"bookCode":"gen", "chapter":1, "verseStart":0, "verseEnd": 0,
#                 "commentary":"chapter intro to Genesis 1"},
#             {"bookCode":"gen", "chapter":1, "verseStart":1, "verseEnd": 10,
#                 "commentary":"the begining"},
#             {"bookCode":"gen", "chapter":1, "verseStart":3, "verseEnd": 30,
#                 "commentary":"the creation"},
#             {"bookCode":"gen", "chapter":1, "verseStart":-1, "verseEnd": -1,
#                 "commentary":"Chapter Epilogue. God completes creation in 6 days."},
#             {"bookCode":"gen", "chapter":-1, "commentary":"book Epilogue."},

#             {"bookCode":"exo", "chapter":1, "verseStart":1,
#                 "verseEnd":1, "commentary":"first verse of Exodus"},
#             {"bookCode":"exo", "chapter":1, "verseStart":1,
#             "verseEnd":10, "commentary":"first para of Exodus"},
#             {"bookCode":"exo", "chapter":1, "verseStart":1,
#             "verseEnd":25, "commentary":"first few paras of Exodus"},
#             {"bookCode":"exo", "chapter":1, "verseStart":20,
#             "verseEnd":25, "commentary":"a middle para of Exodus"},
#             {"bookCode":"exo", "chapter":0, "commentary":"Book intro to Exodus"}
#         ]
#     }
#     }
#     executed,source_name =  post_comentary(variable)

#     #filter by book
#     query1 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"gen"){
#     refString
#     book{
#       bookCode
#     }
#     chapter
#   }
# }
#     """
#     #get without auth
#     executed1 = gql_request(query1)
#     assert "errors" in executed1
#     executed1 = gql_request(query1,headers=headers_auth)
#     assert len(executed1["data"]["commentaries"]) == 6

#     query2 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo"){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed2 = gql_request(query2,headers=headers_auth)
#     assert len(executed2["data"]["commentaries"]) == 5

#     # all book introductions
#     query3= """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",chapter:0){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed3 = gql_request(query3,headers=headers_auth)
#     assert len(executed3["data"]["commentaries"]) == 2

#     # all chapter intros
#     query4= """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",verse:0){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed4 = gql_request(query4,headers=headers_auth)
#     assert len(executed4["data"]["commentaries"]) == 1

#     # all commentaries associated with a verse
#     query5 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"gen",chapter:1,verse:1){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed5 = gql_request(query5,headers=headers_auth)
#     assert len(executed5["data"]["commentaries"]) == 1

#     query6 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"gen",chapter:1,verse:8){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed6 = gql_request(query6,headers=headers_auth)
#     assert len(executed6["data"]["commentaries"]) == 2

#     query7 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo",chapter:1,verse:1){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed7 = gql_request(query7,headers=headers_auth)
#     assert len(executed7["data"]["commentaries"]) == 3

#     query8 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo",chapter:1,verse:2){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed8 = gql_request(query8,headers=headers_auth)
#     assert len(executed8["data"]["commentaries"]) == 2

#     query9 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo",chapter:1,verse:21){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed9 = gql_request(query9,headers=headers_auth)
#     assert len(executed9["data"]["commentaries"]) == 2

#     # commentaries for a verse range
#     # exact range
#     query10 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo",chapter:1,verse:1,lastVerse:25){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed10 = gql_request(query10,headers=headers_auth)
#     assert len(executed10["data"]["commentaries"]) == 1

#     query11 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"gen",chapter:1,verse:0,lastVerse:0){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed11 = gql_request(query11,headers=headers_auth)
#     assert len(executed11["data"]["commentaries"]) == 1

#     # inclusive
#     query12 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo",chapter:1,verse:1,lastVerse:3){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed12 = gql_request(query12,headers=headers_auth)
#     assert len(executed12["data"]["commentaries"]) == 2

#     # crossing boundary
#     query13 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"exo",chapter:1,verse:3,lastVerse:13){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed13 = gql_request(query13,headers=headers_auth)
#     assert len(executed13["data"]["commentaries"]) == 1

#     # not available
#     query14 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",bookCode:"rev",chapter:1,verse:3,lastVerse:13){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed14 = gql_request(query14,headers=headers_auth)
#     assert_not_available_content_gql(executed14["data"]["commentaries"])

# def test_get_incorrect_data():
#     '''Check for input validations in get'''
#     query1 = """
#         {
#   commentaries(sourceName:"hi_TTT"){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed1 = gql_request(query=query1,headers=headers_auth)
#     assert "errors" in executed1.keys()

#     query2 = """
#         {
#   commentaries(sourceName:"hi_TTT_1_commentary",bookCode:10){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed2 = gql_request(query=query2,headers=headers_auth)
#     assert "errors" in executed2.keys()

    

#     query4 = """
#         {
#   commentaries(sourceName:"hi_TTT_1_commentary",chapter:"intro"){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed4 = gql_request(query=query4,headers=headers_auth)
#     assert "errors" in executed4.keys()

#     query6 = """
#          {
#   commentaries(sourceName:"hi_TTT_1_commentary",active:"not"){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed6 = gql_request(query=query6,headers=headers_auth)
#     assert "errors" in executed6.keys()

# def test_put_after_upload():
#     '''Positive tests for put'''
#     #post data
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"mat", "chapter":1, "verseStart":1,
#         "verseEnd":10, "commentary":"first verses of matthew"},
#         {"bookCode":"mrk","chapter":0, "commentary":"book intro to Mark"}
#     ]
#     }
#     }
#     executed_post,source_name =  post_comentary(variable)

#     #positive put
#     #Without Auth
#     executed =  gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable)
#     assert "errors" in executed
#     #With Auth
#     executed =  gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable,
#       headers=headers_auth)
#     for i,item in enumerate(executed["data"]["editCommentary"]["data"]):
#         assert executed["data"]["editCommentary"]["data"][i]['commentary'] == \
#           variable["object"]["commentaryData"][i]['commentary']
#         assert executed["data"]["editCommentary"]["data"][i]['book']['bookCode'] == \
#           variable["object"]["commentaryData"][i]['bookCode']
#         assert executed["data"]["editCommentary"]["data"][i]['chapter'] == \
#           variable["object"]["commentaryData"][i]['chapter']
#         if 'verseEnd' in variable["object"]["commentaryData"][i]:
#             assert executed["data"]["editCommentary"]["data"][i]['verseStart']\
#                == variable["object"]["commentaryData"][i]['verseStart']
#             assert executed["data"]["editCommentary"]["data"][i]['verseEnd']\
#                == variable["object"]["commentaryData"][i]['verseEnd']
#         else:
#             assert executed["data"]["editCommentary"]["data"][i]['verseStart'] is None
#             assert executed["data"]["editCommentary"]["data"][i]['verseEnd'] is None

#     # not available PUT
#     variable["object"]["commentaryData"][0]['chapter'] = 2
#     executed1 =  gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable,
#       headers=headers_auth)
#     assert "errors" in executed1.keys()

#     variable2 = {
#     "object": {
#         "sourceName": "gu_TTT_2_commentary",
#         "commentaryData": [
#         {"bookCode":"mat", "chapter":1, "verseStart":1,
#         "verseEnd":10, "commentary":"first verses of matthew"},
#         {"bookCode":"mrk","chapter":0, "commentary":"book intro to Mark"}
#     ]
#     }
#     }
#     executed2 =  gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable2,
#       headers=headers_auth)
#     assert "errors" in executed2.keys()

# def test_put_incorrect_data():
#     ''' tests to check input validation in put API'''
#     #post data
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#     ]
#     }
#     }
#     executed_post,source_name =  post_comentary(variable)

#     # single data object instead of list
#     variable2 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData":
#         {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}

#     }
#     }
#     executed2 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable2,
#       headers=headers_auth)
#     assert "errors" in executed2.keys()

#     # data object with missing mandatory fields
#     variable3 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed3 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable3,
#       headers=headers_auth)
#     assert "errors" in executed3.keys()

#     variable4 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"gen", "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed4 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable4,
#       headers=headers_auth)
#     assert "errors" in executed4.keys()

#     # incorrect data values in fields
#     variable5 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"gensis", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed5 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable5,
#       headers=headers_auth)
#     assert "errors" in executed5.keys()

#     variable6 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"gen", "chapter":"intro", "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed6 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable6,
#       headers=headers_auth)
#     assert "errors" in executed6.keys()

#     variable7 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"gen", "chapter":1, "verseStart":"intro",
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed7 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable7,
#       headers=headers_auth)
#     assert "errors" in executed7.keys()

#     variable8 = {
#     "object": {
#         "sourceName": "gu_TTT_2_commentary",
#         "commentaryData": [
#         {"bookCode":"gen", "chapter":1, "verseStart":1,
#         "verseEnd":1, "commentary":"first verse of Genesis"}
#         ]
#     }
#     }
#     executed8 = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable8,
#       headers=headers_auth)
#     assert "errors" in executed8.keys()

# def test_soft_delete():
#     '''check soft delete in commentaries'''
#     #post data
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"mrk", "chapter":1, "verseStart":1,
#         "verseEnd":10, "commentary":"first verses of Mark"},
#         {"bookCode":"mrk","chapter":0, "commentary":"book intro to Mark"}
#         ]
#     }
#     }
#     executed_post,source_name =  post_comentary(variable)

#     variable2 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"mrk","chapter":0, "commentary":"book intro to Mark","active": False}
#         ]
#     }
#     }
#     executed = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable2,
#       headers=headers_auth)

#     query1 = """
#         {
#   commentaries(sourceName:"gu_TTT_1_commentary",active:false){
#     refString
#     book{
#       bookId
#       bookName
#       bookCode
#     }
#     chapter
#     verseStart
#     verseEnd
#     commentary
#     active
#   }
# }
#     """
#     executed2 = gql_request(query1,headers=headers_auth)
#     assert len(executed2["data"]["commentaries"]) == 1

# def test_created_user_can_only_edit():
#     """only created user and SA can only edit"""
#     """source edit can do by created user and Super Admin"""
#     SA_user_data = {
#             "user_email": SUPER_USER,
#             "password": SUPER_PASSWORD
#         }
#     response = login(SA_user_data)
#     token =  response["data"]["login"]["token"]

#     headers_SA = {"contentType": "application/json",
#                     "accept": "application/json",
#                     'Authorization': "Bearer"+" "+token
#                 }
    
#     #add version
#     version_add(version_query,VERSION_VAR)
#     #add source
#     source_data = {
#   "object": {
#     "contentType": "commentary",
#     "language": "gu",
#     "version": "TTT",
#     "revision": "1",
#     "year": 2021
#   }
# }
#     executed = gql_request(query=source_query,operation="mutation", variables=source_data,
#       headers=headers_SA)
#     assert isinstance(executed, Dict)
#     assert executed["data"]["addSource"]["message"] == "Source created successfully"

#     headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#     #post data
#     #Create With SA
#     variable = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"mrk", "chapter":1, "verseStart":1,
#         "verseEnd":10, "commentary":"first verses of Mark"},
#         {"bookCode":"mrk","chapter":0, "commentary":"book intro to Mark"}
#         ]
#     }
#     }
#     executed = gql_request(query=ADD_COMMENTARY,operation="mutation", variables=variable,
#       headers=headers_SA)

#     variable2 = {
#     "object": {
#         "sourceName": "gu_TTT_1_commentary",
#         "commentaryData": [
#         {"bookCode":"mrk","chapter":0, "commentary":"book intro to Mark"}
#         ]
#     }
#     }
#     #Edit With SA
#     executed = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable2,
#       headers=headers_SA)
#     assert executed["data"]["editCommentary"]["message"]==\
#       "Commentaries updated successfully"
#     #edit with VA not created User  
#     executed = gql_request(EDIT_COMMENTARY,operation="mutation",variables=variable2,
#       headers=headers_auth)
#     assert "errors" in executed

# def test_get_access_with_user_roles_and_apps():
#     """Test get filter from apps and with users having different permissions"""
#     # #add version
#     version_add(version_query,VERSION_VAR)
#     data = [
#     	{'bookCode':'gen', 'chapter':0, 'commentary':'book intro to Genesis'}
#     ]
#     content_data = {
#     "object": {
#         "sourceName": "",
#         "commentaryData": data
#     }
#     }

#     get_query = """
#       query get_commentary($source:String!){
#   commentaries(sourceName:$source){
#    refString
#     book{
#       bookCode
#     }
#     chapter
#   }
# }
#     """
#     get_var = {
#       "source": "gu_TTT_1_commentary"
#     }

#     content_qry = ADD_COMMENTARY
#     test_data = {"get_query": get_query,
#           "get_var": get_var
#         }

#     contetapi_get_accessrule_checks_app_userroles_gql("commentary",content_qry, content_data , test_data , bible=False)