from fastapi.testclient import TestClient
import os, sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.environ["PWD"])

from main import app, get_db
from database import Base


postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres") 
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "postgres") 
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret") 

SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s/%s"%(postgres_user,postgres_password,postgres_host,postgres_database)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker()


def override_get_db():
	connection = engine.connect()
	trans = connection.begin()
	db = Session(bind=connection)
	try:
		yield db
	finally:
		db.close()
		trans.rollback()
		connection.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
