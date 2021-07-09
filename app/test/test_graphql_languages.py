'''Test cases for language related GraphQL'''
import os
import sys
from typing import Dict
#pylint: disable=E0611
#pylint: disable=E0401
from test.test_languages import assert_positive_get
from graphene.test import Client
import graphene
current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
#pylint: disable=C0413
#pylint: disable=E0401
from graphql_api import queries, mutations

schema=graphene.Schema(query=queries.Query,mutation=mutations.VachanMutations)
client = Client(schema)


def test_get_all_data():
    """test for get all data as per the following query"""
    default_get_query = """
        {
    languages{
        languageId
        language
        code
        scriptDirection
        metaData
    }
    }
    """
    executed = client.execute(default_get_query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["languages"])>0
    assert isinstance(executed["data"]["languages"], list)
    for item in executed["data"]["languages"]:
        assert_positive_get(item)


def test_get_one_language_with_argument():
    """test for get only 1 field data with  name"""
    default_get_query = """
        {
    languages(languageName:"Afar"){
        language
    }
    }
    """
    executed = client.execute(default_get_query)
    assert executed == {"data": {"languages": [{"language": "Afar"}]}}


def test_check_gql_skip():
    '''Skip Test for languages'''
    query_skip0 = """
            {
    languages(skip:0){
        languageId
        language
    }
    }
    """
    query_skip1 = """
            {
    languages(skip:1){
        languageId
        language
    }
    }
    """
    executed = client.execute(query_skip0)
    assert isinstance(executed, Dict)
    if len(executed["data"]["languages"]) > 1:
        executed2 = client.execute(query_skip1)
        assert isinstance(executed2, Dict)
        assert executed["data"]["languages"][1] == executed2["data"]["languages"][0]
