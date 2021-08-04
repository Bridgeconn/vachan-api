'''Executes and tests the AgMT and generic translation workflows.
This is not part of the automated tests, and data added to DB by running this script will persist.
This is to be used manually during develepment testing'''
from app.test import gql_request
import json
from .test_gql_agmt_translation import assert_positive_get_tokens_gql
from .test_translation_workflow import bible_books,ALIGNMENT_SRC,alignment_data,ALIGNMENT_TRG
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
from .test_gql_bibles import BOOK_ADD_QUERY
from .test_gql_agmt_projects import check_post as create_agmt_project
from .test_gql_agmt_projects import PROJECT_CREATE_GLOBAL_QUERY,USER_CREATE_GLOBAL_QUERY,PROJECT_EDIT_GLOBAL_QUERY,\
    USER_EDIT_GLOBAL_QUERY,PROJECT_GET_GLOBAL_QUERY
from .test_gql_agmt_translation import APPLY_TOKEN
from .test_gql_translation_suggetion import Add_Alignment

# have a bible source to be used
source_name = "hi_XYZ_1_bible" # pylint: disable=C0103
project_id = None # pylint: disable=C0103

version_variable = {
    "object": {
        "versionAbbreviation": "XYZ",
        "versionName": "Xyz version to test",
        "revision": "1",
        "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
    }
    }

src_var={
  "object": {
    "contentType": "bible",
    "language": "hi",
    "version": "XYZ",
    "revision": "1",
    "year": 2020,
    "license": "CC-BY-SA",
    "metaData": "{\"owner\":\"someone\",\"access-key\":\"123xyz\"}"
  }
}

project_post_data = {
     "object": {
    "projectName": "Test project 4",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
  }
}



token_update_data = [
	{
		"token":"यीशु मसीह",
		"occurrences":[
			{"sentenceId":41001001, "offset":[31, 40]}],
		"translation":"യേശു ക്രിസ്തു"
	},
	{
		"token":"पुत्र",
		"occurrences":[
			{"sentenceId":41001001, "offset":[25,30]}],
		"translation":"പുത്രന്‍"
	},
	{
		"token":"इब्राहीम",
		"occurrences":[
			{"sentenceId":41001002, "offset":[0, 8]}],
		"translation":"അബ്രഹാം"
	}
]

gospel_books_data_manual = [
        {
        "USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
        "JSON":"{\n\"book\":{\n\"bookCode\":\"MAT\"\n},\n\"chapters\":[\n{\n\"chapterNumber\":\"1\",\n\"contents\":[\n{\n\"p\":null\n},\n{\n\"verseNumber\":\"1\",\n\"verseText\":\"testverseone\",\n\"contents\":[\n\"testverseone\"\n]\n},\n{\n\"verseNumber\":\"2\",\n\"verseText\":\"testversetwo\",\n\"contents\":[\n\"testversetwo\"\n]\n}\n]\n}\n],\n\"_messages\":{\n\"_warnings\":[\n\"Emptylinespresent.\",\n\"Bookcodeisinlowercase.\"\n]\n}\n}"
},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":"{\n\"book\":{\n\"bookCode\":\"MRK\"\n},\n\"chapters\":[\n{\n\"chapterNumber\":\"1\",\n\"contents\":[\n{\n\"p\":null\n},\n{\n\"verseNumber\":\"1\",\n\"verseText\":\"testverseone\",\n\"contents\":[\n\"testverseone\"\n]\n},\n{\n\"verseNumber\":\"2\",\n\"verseText\":\"testversetwo\",\n\"contents\":[\n\"testversetwo\"\n]\n}\n]\n}\n],\n\"_messages\":{\n\"_warnings\":[\n\"Emptylinespresent.\",\n\"Bookcodeisinlowercase.\"\n]\n}\n}"
        },
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":"{\n\"book\":{\n\"bookCode\":\"LUK\"\n},\n\"chapters\":[\n{\n\"chapterNumber\":\"1\",\n\"contents\":[\n{\n\"p\":null\n},\n{\n\"verseNumber\":\"1\",\n\"verseText\":\"testverseone\",\n\"contents\":[\n\"testverseone\"\n]\n},\n{\n\"verseNumber\":\"2\",\n\"verseText\":\"testversetwo\",\n\"contents\":[\n\"testversetwo\"\n]\n}\n]\n}\n],\n\"_messages\":{\n\"_warnings\":[\n\"Emptylinespresent.\",\n\"Bookcodeisinlowercase.\"\n]\n}\n}"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":"{\n\"book\":{\n\"bookCode\":\"JHN\"\n},\n\"chapters\":[\n{\n\"chapterNumber\":\"1\",\n\"contents\":[\n{\n\"p\":null\n},\n{\n\"verseNumber\":\"1\",\n\"verseText\":\"testverseone\",\n\"contents\":[\n\"testverseone\"\n]\n},\n{\n\"verseNumber\":\"2\",\n\"verseText\":\"testversetwo\",\n\"contents\":[\n\"testversetwo\"\n]\n}\n]\n}\n],\n\"_messages\":{\n\"_warnings\":[\n\"Emptylinespresent.\",\n\"Bookcodeisinlowercase.\"\n]\n}\n}"}
]

NEW_USER_ID = 20202


def test_end_to_end_translation():
    '''happy path test for AGMT translation workflow'''
    #create version
    version_add(version_query,version_variable)
    #create source
    executed_src = source_add(source_query,src_var)
    source_name = executed_src["data"]["addSource"]["data"]["sourceName"]

    
    #add bible
    post_data_bible = {
  "object": {
    "sourceName": source_name,
    "books":gospel_books_data_manual
}
    }
    executed_bible = gql_request(BOOK_ADD_QUERY,operation="mutation",variables=post_data_bible)
    assert len(executed_bible["data"]["addBibleBook"]["data"]) == 4
    assert executed_bible["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"
    
    #create project
    executed_project = create_agmt_project(PROJECT_CREATE_GLOBAL_QUERY,project_post_data)
    project_id =  executed_project["data"]["createAgmtProject"]["data"]["projectId"]

    #update project
    project_update_data = {
     "object": {
        "projectId":project_id,
        "uploadedBooks":[bible_books['mat'], bible_books['mrk']],
        "selectedBooks": {
            "bible": source_name,
            "books": ["luk", "jhn"]
          }
  }
}
    executed_prj_upd = gql_request(query=PROJECT_EDIT_GLOBAL_QUERY,operation="mutation",\
         variables=project_update_data)
    assert executed_prj_upd["data"]["editAgmtProject"]["message"] == "Project updated successfully"

    # tokenize
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
    for item in get_resp["data"]["agmtProjectTokens"]:
      assert_positive_get_tokens_gql(item)

    # translate
    post_token_list = {
  "object": {
    "projectId": project_id,
    "returnDrafts": True,
    "token": token_update_data
  }
}

    executed_tokenize = gql_request(APPLY_TOKEN,operation="mutation",variables=post_token_list)
    assert executed_tokenize["data"]["applyAgmtTokenTranslation"]["message"] == "Token translations saved"

    # Additional user add and update
    user_data = {
  "object": {
    "projectId": project_id,
    "userId": NEW_USER_ID
  }
}
    executed_user_create = gql_request(USER_CREATE_GLOBAL_QUERY,operation="mutation",variables=user_data)
    assert executed_user_create["data"]["createAgmtProjectUser"]["message"]\
         == "User added in project successfully"

    user_up_data = {
  "object": {
    "projectId": project_id,
    "userId": NEW_USER_ID,
    "userRole": "test role",
	"metaData": "{\"somekey\":\"value\"}"
  }
}
    
    executed_up_user = gql_request(USER_EDIT_GLOBAL_QUERY,operation="mutation",variables=user_up_data)
    assert executed_up_user["data"]["editAgmtProjectUser"]["message"] == \
        "User updated in project successfully"

    executed_user_get = gql_request(query=PROJECT_GET_GLOBAL_QUERY)
    assert len(executed_user_get["data"]["agmtProjects"][0]["users"]) > 0

    # # Suggestions
    var_align = {
  "object": {
    "sourceLanguage": ALIGNMENT_SRC,
    "targetLanguage": ALIGNMENT_TRG,
    "data": alignment_data
  }
}
    executed_align = gql_request(Add_Alignment,operation="mutation",variables=var_align)
    assert executed_align["data"]["addAlignment"]["message"] == "Added to Alignments"

    # tokenize after adding token "परमेश्वर" via alignment
    query_auto_suggest = """
        mutation autosuggest($object:InputAutoTranslation){
  suggestAutoTranslation(infoArg:$object){
    data{
      sentenceId
      sentence
      draft
      draftMeta
    }
  }
}
    """
    var_auto_sugg = {
  "object": {
    "projectId": project_id,
    "sentenceIdList": 42001001
  }
}
    executed_auto_sugg = gql_request(query_auto_suggest,operation="mutation",variables=var_auto_sugg)
    draft = executed_auto_sugg["data"]["suggestAutoTranslation"]["data"][0]['draft']
    assert "ദൈവം" in draft
    assert "പുത്രന്‍" in draft
    assert "യേശു ക്രിസ്തു" in draft