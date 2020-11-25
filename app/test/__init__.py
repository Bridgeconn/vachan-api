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
        db_.close()
        trans.rollback()
        connection.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
