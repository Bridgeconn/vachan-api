'''Test cases for extract text contents related APIs'''
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_versions import check_post as version_add
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  gql_request
from .conftest import initial_test_users
from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER
from .test_gql_sources import check_post as source_add , SOURCE_GLOBAL_QUERY
from .test_source_get_sentence import assert_positive_get, commentary_data

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers = {"contentType": "application/json", "accept": "application/json"}

def create_sources():
    '''prior steps and post attempt, without checking the response'''
    version_variable = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version for get sentence"
    }
    }
    #Create a version
    version_add(version_query,version_variable)

    source_data = {
  "object": {
    "contentType": "bible",
    "language": "hi",
    "version": "TTT",
    "revision": "1",
    "year": 2020
  }
}
    #create source
    executed = source_add(SOURCE_GLOBAL_QUERY,source_data)
    bible_name = executed["data"]["addSource"]["data"]["sourceName"]