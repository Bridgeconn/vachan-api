'''Define fixtures for Database managment in testing environment'''
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db, log
from app.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker()
CONN = None

def override_get_db():
    '''To use a separate transaction for test sessions which can then be rolled back'''
    global CONN #pylint: disable=W0603
    db_ = Session(bind=CONN)
    try:
        log.warning('TESTING:overrides default database connection')
        yield db_
    finally:
        pass
        # db_.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope='function', autouse=True)
def db_transaction():
    '''Begins an external transaction at the start of every function'''
    global CONN #pylint: disable=W0603
    log.warning("TESTING: Starts new database transaction")
    try:
        CONN = engine.connect()
        trans = CONN.begin()
        yield CONN
    finally:
        log.warning("TESTING: Rolls back database transaction")
        trans.rollback()
        CONN.close()
