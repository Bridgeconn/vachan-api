'''Set testing environment'''

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base, SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker()


def override_get_db():
    '''To use a separate transaction for test sessions which can then be rolled back'''
    connection = engine.connect()
    trans = connection.begin()
    db_ = Session(bind=connection)
    try:
        yield db_
    finally:
        # db_.close()
        trans.rollback()
        connection.close()

app.dependency_overrides[get_db] = override_get_db

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
    response = client.get(unit_url+"?skip=10000;limit=10")
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
    response = client.get(unit_url+"?skip=10000;limit=10")
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
