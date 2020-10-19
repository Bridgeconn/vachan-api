from fastapi.testclient import TestClient
import os, sys
import pytest

sys.path.append(os.environ["PWD"])

from main import app

client = TestClient(app)

postgres_host = os.environ.get("AGMT_POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("AGMT_POSTGRES_PORT", "5432")
postgres_user = os.environ.get("AGMT_POSTGRES_USER", "postgres") 
postgres_password = os.environ.get("AGMT_POSTGRES_PASSWORD", "secret") 

postgres_database = "test_DB" 

def get_db():                                                                      #--------------To open database connection-------------------#
	"""Opens a new database connection to test DB if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'db'):
		g.db = psycopg2.connect(dbname=postgres_database, user=postgres_user,
			password=postgres_password,	host=postgres_host, port=postgres_port)
	return g.db


@pytest.fixture(autouse=True)
def _mock_db_connection(mocker, get_db):
    """
    This will alter application database connection settings, once and for all the tests
    in unit tests module.
    :param mocker: pytest-mock plugin fixture
    :param get_db: connection class
    :return: True upon successful monkey-patching
    """
    mocker.patch('db.database.dbc', get_db)
    return True