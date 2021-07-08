'''Test cases for language related GraphQL'''
import os
import sys
from typing import Dict
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


def test_get_one_language_with_limit():
    """test for get only 1 field data with limit parameter"""
    default_get_query = """
        {
    languages(limit:1){
        language
    }
    }
    """
    executed = client.execute(default_get_query)
    assert executed == {"data": {"languages": [{"language": "Afar"}]}}
