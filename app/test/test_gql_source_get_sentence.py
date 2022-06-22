'''Test cases for extract text contents related APIs'''
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_versions import check_post as version_add
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  assert_not_available_content_gql, gql_request, check_skip_limit_gql
from .conftest import initial_test_users
from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER
from .test_gql_sources import check_post as source_add , SOURCE_GLOBAL_QUERY
from .test_source_get_sentence import assert_positive_get, commentary_data
from .test_gql_bibles import BOOK_ADD_QUERY
from .test_gql_commentaries import ADD_COMMENTARY

from .test_source_get_sentence import assert_positive_get

# headers_auth = {"contentType": "application/json",
#                 "accept": "application/json"}
# headers = {"contentType": "application/json", "accept": "application/json"}

# def create_sources():
#   '''prior steps and post attempt, without checking the response'''
#   version_variable = {
#       "object": {
#       "versionAbbreviation": "TTT",
#       "versionName": "test version for get sentence"
#   }
#   }
#   #Create a version
#   version_add(version_query,version_variable)

#   source_data = {
# "object": {
#   "contentType": "bible",
#   "language": "hi",
#   "version": "TTT",
#   "revision": "1",
#   "year": 2020
# }
# }
#   #create source
#   executed = source_add(SOURCE_GLOBAL_QUERY,source_data)
#   bible_name = executed["data"]["addSource"]["data"]["sourceName"]
#   #Add bible books
#   headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#   book_variable = {
#   "object": {
#       "sourceName": bible_name,
#       "books": [
#       {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
#       {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
#       {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
#       {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
# ]
#   }
#   }
#   executed = gql_request(query=BOOK_ADD_QUERY,operation="mutation", variables=book_variable,
#     headers=headers_auth)
#   assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"

#   source_data["object"]["contentType"] = "commentary"
#   source_data["object"]["language"] = "en"
#   #create source
#   executed = source_add(SOURCE_GLOBAL_QUERY,source_data)
#   commentary_name = executed["data"]["addSource"]["data"]["sourceName"]

#   #Commentaries add
#   comm_variable = {
#   "object": {
#       "sourceName": commentary_name,
#       "commentaryData": [
#       {"bookCode":"gen", "chapter":0, "commentary":"book intro to Genesis"},
#       {"bookCode":"gen", "chapter":1, "verseStart":0, "verseEnd": 0,
#           "commentary":"chapter intro to Genesis 1"},
#       {"bookCode":"gen", "chapter":1, "verseStart":1, "verseEnd": 10,
#           "commentary":"the begining"},
#       {"bookCode":"gen", "chapter":1, "verseStart":3, "verseEnd": 30,
#           "commentary":"the creation"},
#       {"bookCode":"gen", "chapter":1, "verseStart":-1, "verseEnd": -1,
#           "commentary":"Chapter Epilogue. God completes creation in 6 days."},
#       {"bookCode":"gen", "chapter":-1, "commentary":"book Epilogue."},

#       {"bookCode":"exo", "chapter":1, "verseStart":1,
#           "verseEnd":1, "commentary":"first verse of Exodus"},
#       {"bookCode":"exo", "chapter":1, "verseStart":1,
#       "verseEnd":10, "commentary":"first para of Exodus"},
#       {"bookCode":"exo", "chapter":1, "verseStart":1,
#       "verseEnd":25, "commentary":"first few paras of Exodus"},
#       {"bookCode":"exo", "chapter":1, "verseStart":20,
#       "verseEnd":25, "commentary":"a middle para of Exodus"},
#       {"bookCode":"exo", "chapter":0, "commentary":"Book intro to Exodus"}
#   ]
#   }
#   }

#   executed = gql_request(query=ADD_COMMENTARY,operation="mutation", variables=comm_variable,
#     headers=headers_auth)
#   assert executed["data"]["addCommentary"]["message"] == "Commentaries added successfully"

#   return bible_name, commentary_name

# def test_get_poisitive():
#   """normal tests for all possible get queries"""
#   headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
#   # Before adding data
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(sourceName:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": "hi_TTT_1_bible"
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   assert "errors" in executed

#   # Add data
#   bible_name, commentary_name = create_sources()

#   # filtering with various params
#   #Without Auth
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers)
#   assert "errors" in executed
#   #With Auth
#   query_check = """
#       query extracttext($skip:Int, $limit:Int){
#   extractTextContents(skip:$skip,limit:$limit){
#     sentenceId
#     sentence
#     surrogateId
#   }
# }
#     """
#   var1 = {
#   "skip": 0,
#   "limit": 100
# }  

#   executed = gql_request(query_check,variables=var1,headers=headers_auth)
#   full_resp = executed["data"]["extractTextContents"]
#   for item in full_resp:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert_positive_get(item)

#   #language code
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(languageCode:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": "hi"
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   only_hi = executed["data"]["extractTextContents"]
#   for item in only_hi:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert_positive_get(item)
#   assert 0 < len(only_hi) <= len(full_resp)

#   #Content type
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(contentType:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": "commentary"
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   only_commentary = executed["data"]["extractTextContents"]
#   for item in only_commentary:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert_positive_get(item)
#   assert 0 < len(only_commentary) < len(full_resp)+len(only_commentary)

#   #Source name bible
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(sourceName:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": bible_name
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   chosen_bible = executed["data"]["extractTextContents"]
#   for item in chosen_bible:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert len(chosen_bible) == 8
#     assert_positive_get(item)

#   #Source name commentary
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(sourceName:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": commentary_name
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   chosen_commentary = executed["data"]["extractTextContents"]
#   for item in chosen_commentary:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert len(chosen_commentary) == 11
#     assert_positive_get(item)

#   qry_book = """
#   query extracttext($tag:String!,$book:[String]){
# extractTextContents(sourceName:$tag,books:$book){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
#   """

#   for buk in ['mat','mrk','luk','jhn']:
#     var = {
#   "tag": bible_name,
#   "book": buk
# } 
#   executed = gql_request(qry_book,operation="query",variables=var,headers=headers_auth)
#   chosen_book = executed["data"]["extractTextContents"]
#   assert len(chosen_book) == 2
#   for item in chosen_book:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert_positive_get(item)

#   var = {
#   "tag": commentary_name,
#   "book": "gen"
# }

#   executed = gql_request(qry_book,operation="query",variables=var,headers=headers_auth)
#   chosen_book = executed["data"]["extractTextContents"]
#   assert len(chosen_book) == 6
#   for item in chosen_book:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert_positive_get(item)

#   var = {
#   "tag": commentary_name,
#   "book": "exo"
# }

#   executed = gql_request(qry_book,operation="query",variables=var,headers=headers_auth)
#   chosen_book = executed["data"]["extractTextContents"]
#   assert len(chosen_book) == 5
#   for item in chosen_book:
#     item["sentenceId"] = int(item["sentenceId"])
#     assert_positive_get(item)

#   #check skip and limit
#   check_skip_limit_gql(query_check,"extractTextContents",headers_auth)

# def test_get_negatives():
#   '''error or not available cases'''
#   # Add data
#   bible_name, commentary_name = create_sources()
  
#   qry_book = """
#   query extracttext($tag:String!,$book:[String]){
#   extractTextContents(sourceName:$tag,books:$book){
#   sentenceId
#   sentence
#   surrogateId
#   }
#   }
#   """

#   for buk in ['mat','mrk','luk','jhn']:
#     var = {
#   "tag": commentary_name,
#   "book": buk
#   } 
#     executed = gql_request(qry_book,operation="query",variables=var,headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["extractTextContents"])

#   for buk in ['gen', 'exo']:
#     var = {
#   "tag": bible_name,
#   "book": buk
#   } 
#     executed = gql_request(qry_book,operation="query",variables=var,headers=headers_auth)
#     assert_not_available_content_gql(executed["data"]["extractTextContents"])


#   #Wrong source name
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(sourceName:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": bible_name.replace('bible','commentary')
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   assert "errors" in executed

#   #Wrong content type
#   #Content type
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(contentType:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": "usfm"
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   assert "errors" in executed

#   #Wrong language
#   #language code
#   get_qry = """
#   query extracttext($tag:String!){
# extractTextContents(languageCode:$tag){
#   sentenceId
#   sentence
#   surrogateId
# }
# }
# """
#   var = {
#   "tag": "ur"
# }
#   executed = gql_request(get_qry,operation="query",variables=var,headers=headers_auth)
#   assert "errors" in executed