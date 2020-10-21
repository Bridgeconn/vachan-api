from fastapi.testclient import TestClient
import os, sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.environ["PWD"])

from main import app, get_db


postgres_host = os.environ.get("AGMT_POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("AGMT_POSTGRES_PORT", "5432")
postgres_user = os.environ.get("AGMT_POSTGRES_USER", "postgres") 
postgres_password = os.environ.get("AGMT_POSTGRES_PASSWORD", "secret") 
postgres_database = "test_DB" 

SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s/%s"%(postgres_user,postgres_password,postgres_host,postgres_database)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
