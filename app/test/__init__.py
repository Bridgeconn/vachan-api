'''Set testing environment and define common tests'''

import os
import sys
import pytest
from fastapi.testclient import TestClient

from app.main import app, get_db, log

client = TestClient(app)

def assert_input_validation_error(response):
    '''Check for input validation error in response'''
    assert response.status_code == 422
    assert "error" in response.json()
    assert response.json()['error'] == "Input Validation Error"

def assert_not_available_content(response):
    '''Checks for empty array returned when requetsed content not available'''
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json())==0

def check_skip(unit_url):
    '''All tests for the skip parameter of an API endpoint'''
    response1 = client.get(unit_url+"?skip=0")
    assert response1.status_code == 200
    assert isinstance( response1.json(), list)
    if len(response1.json()) > 1:
        response2 = client.get(unit_url+"?skip=1")
        assert response2.status_code == 200
        assert isinstance( response2.json(), list)
        assert response1.json()[1] == response2.json()[0]

    # fetch a non existant page, with skip and limit values
    response = client.get(unit_url+"?skip=50000&limit=10")
    assert_not_available_content(response)

    # skip should be an integer
    response = client.get(unit_url+"?skip=abc")
    assert_input_validation_error(response)

    # skip should be a positive integer
    response = client.get(unit_url+"?skip=-10")
    assert_input_validation_error(response)


def check_limit(unit_url):
    '''All tests for the limit parameter of an API endpoint'''
    response = client.get(unit_url+"?limit=3")
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) <= 3

    # fetch a non existant page, with skip and limit values
    response = client.get(unit_url+"?skip=50000&limit=10")
    assert_not_available_content(response)

    # limit should be an integer
    response = client.get(unit_url+"?limit=abc")
    assert_input_validation_error(response)

    # limit should be a positive integer
    response = client.get(unit_url+"?limit=-1")
    assert_input_validation_error(response)

def check_default_get(unit_url, assert_positive_get):
    '''checks for an array of items of particular type'''
    response = client.get(unit_url)
    assert response.status_code == 200
    assert isinstance( response.json(), list)
    assert len(response.json()) > 0
    for item in response.json():
        assert_positive_get(item)

    check_skip(unit_url)
    check_limit(unit_url)

def check_soft_delete(unit_url, check_post, data, delete_data):
    '''set active field to False'''
    response, source_name = check_post(data)
    assert response.status_code == 201

    get_response1 = client.get(unit_url+source_name)
    assert len(get_response1.json()) == len(data)


    # positive PUT
    for item in delete_data:
        item['active'] = False
    headers = {"contentType": "application/json", "accept": "application/json"}
    response = client.put(unit_url+source_name,headers=headers, json=delete_data)
    assert response.status_code == 201
    assert response.json()['message'].endswith('updated successfully')
    for item in response.json()['data']:
        assert not item['active']

    get_response2 = client.get(unit_url+source_name)
    assert len(get_response2.json()) == len(data) - len(delete_data)

    get_response3 = client.get(unit_url+source_name+'?active=false')
    assert len(get_response3.json()) == len(delete_data)
    