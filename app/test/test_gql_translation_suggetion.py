"""Test cases for translation suggetions in GQL"""
from typing import Dict
#pylint: disable=E0401
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import  gql_request,assert_not_available_content_gql,check_skip_limit_gql
from .test_gql_bibles import add_bible

def assert_positive_get_tokens(item):
    '''common tests for a token response object'''
    assert "token" in item
    assert "occurrences" in item
    assert len(item['occurrences']) > 0
    assert "translations" in item
    for trans in item['translations']:
        assert isinstance(item['translations'][trans], (int, float))
    if "metaData" in item and item['metaData'] is not None:
        assert isinstance(item['metaData'], dict)

        