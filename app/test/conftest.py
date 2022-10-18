'''Define fixtures for Database managment in testing environment'''
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.custom_exceptions import NotAvailableException
from app.main import app, get_db, log
from app.database import SQLALCHEMY_DATABASE_URL
from app.schema import schema_auth
from app.auth.auth_globals import generate_apps, generate_roles

ALL_APPS, ALL_INPUT_APPS = generate_apps()
ALL_ROLES = generate_roles()
# print("-------------------gneerated apps data in conftest --- '''''''''''''''''''''''' ==> ", ALL_APPS, ALL_INPUT_APPS)
# print("-------------------gneerated roles data in conftest --- '''''''''''''''''''''''' ==> ", ALL_ROLES)

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

#Users data with apps
initial_test_users = {
            "AgAdmin": {
                "user_email": "agadmintest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Autographa",
                "lastname": "Admin",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.AG.value
                "app" : 'Autographa' if 'Autographa' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "BcsDev":{
                "user_email": "bcsdevtest@mail.test",
                "password": "passwordtest@1",
                "firstname": "BCS",
                "lastname": "Developer",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.API.value
                "app" : 'API-user' if 'API-user' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "AgUser":{
                "user_email": "agtest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Autographa",
                "lastname": "User",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.AG.value
                "app" : 'Autographa' if 'Autographa' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "VachanUser":{ 
                "user_email": "vachantest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Vachan",
                "lastname": "user",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.VACHAN.value
                "app" : 'Vachan-online or vachan-app' if 'Vachan-online or vachan-app' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "APIUser":{
                "user_email": "apitest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Api",
                "lastname": "User",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.API.value
                "app" : 'API-user' if 'API-user' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "VachanAdmin":{
                "user_email": "vachanadmintest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Vachan",
                "lastname": "Admin",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.VACHAN.value
                "app" : 'Vachan-online or vachan-app' if 'Vachan-online or vachan-app' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "APIUser2":{
                "user_email": "abctest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Api",
                "lastname": "User two",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.API.value
                "app" : 'API-user' if 'API-user' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            },
            "AgUser2":{
                "user_email": "agtest2@mail.test",
                "password": "passwordtest@1",
                "firstname": "Autographa",
                "lastname": "User Two",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.AG.value
                "app" : 'Autographa' if 'Autographa' in ALL_APPS.keys() else NotAvailableException('Not a Valid app , app is not registred ')
            }
        }

#session fixture for access checks working
@pytest.fixture(scope="session", autouse=True)
def create_user_session_run_at_start():
    try:
        print("Session fixture for create user------------------>")
        from .test_auth_basic import register,delete_user_identity,assign_roles,SUPER_USER,SUPER_PASSWORD
        
        for user_data in initial_test_users:
            current_user = initial_test_users[user_data]
            data = {
                "email": current_user['user_email'],
                "password": current_user['password'],
                "firstname": current_user['firstname'],
                "lastname": current_user['firstname']
            }
            response = register(data, apptype=current_user['app'])
            current_user['test_user_id'] = response.json()["registered_details"]["id"]
            current_user['token'] = response.json()["token"]
        #admin roles provide for
        super_data = {
        "user_email": SUPER_USER,
        "password": SUPER_PASSWORD
        }
        #AgAdmin
        role_user_id = initial_test_users["AgAdmin"]["test_user_id"]
        # role_list = [schema_auth.AdminRoles.AGADMIN.value]
        role_list = ['AgAdmin'] if 'AgAdmin' in ALL_ROLES else NotAvailableException('Not a Valid role , role is not registred ')
        response = assign_roles(super_data,role_user_id,role_list)
        assert response.status_code == 201
        assert response.json()["role_list"] == \
            ['AgUser', 'AgAdmin']
            # [schema_auth.AdminRoles.AGUSER.value, schema_auth.AdminRoles.AGADMIN.value]
        #VachanAdmin
        role_user_id = initial_test_users["VachanAdmin"]["test_user_id"]
        # role_list = [schema_auth.AdminRoles.VACHANADMIN.value]
        role_list = ['VachanAdmin'] if 'VachanAdmin' in ALL_ROLES else NotAvailableException('Not a Valid role , role is not registred ')
        response = assign_roles(super_data,role_user_id,role_list)
        assert response.status_code == 201
        assert response.json()["role_list"] == \
            ['VachanUser', 'VachanAdmin']
            # [schema_auth.AdminRoles.VACHANUSER.value, schema_auth.AdminRoles.VACHANADMIN.value]
        #BcsDeveloper
        role_user_id = initial_test_users["BcsDev"]["test_user_id"]
        # role_list = [schema_auth.AdminRoles.BCSDEV.value]
        role_list = ['BcsDeveloper'] if 'BcsDeveloper' in ALL_ROLES else NotAvailableException('Not a Valid role , role is not registred ')
        response = assign_roles(super_data,role_user_id,role_list)
        assert response.status_code == 201
        assert response.json()["role_list"] == \
            ['APIUser','BcsDeveloper']
            # [schema_auth.AdminRoles.APIUSER.value, schema_auth.AdminRoles.BCSDEV.value]
        yield initial_test_users
    finally:
        delete_list = []
        for user_data in initial_test_users:
            current_user = initial_test_users[user_data]
            delete_list.append(current_user["test_user_id"])
        delete_user_identity(delete_list)
        print("Session fixture for create user END------------------>")

