'''Test cases for contentType related GraphQL APIs'''
from typing import Dict
from . import gql_request
from .test_content_types import assert_positive_get


def test_get_default():
    '''positive test case, without optional params'''
    query = """
            {
    contentTypes{
        contentId
        contentType
    }
    }
    """
    executed = gql_request(query)
    assert isinstance(executed, Dict)
    assert len(executed["data"]["contentTypes"])>0
    assert isinstance(executed["data"]["contentTypes"], list)
    for item in executed["data"]["contentTypes"]:
        assert_positive_get(item)        