'''Define fixtures for Database managment in testing environment'''
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db, log
from app.database import SQLALCHEMY_DATABASE_URL
# from app.schema import schema_auth
from . import TEST_APPS_LIST, TEST_ROLE_LIST

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
                "user_email": "agadmintest@mail.testing",
                "password": "passwordtest@1",
                "firstname": "Autographa",
                "lastname": "Admin",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.AG.value
                "app" : TEST_APPS_LIST['AG']
            },
            "BcsDev":{
                "user_email": "bcsdevtest@mail.test",
                "password": "passwordtest@1",
                "firstname": "BCS",
                "lastname": "Developer",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.API.value
                "app" : TEST_APPS_LIST['API']
            },
            "AgUser":{
                "user_email": "agtest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Autographa",
                "lastname": "User",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.AG.value
                "app" : TEST_APPS_LIST['AG']
            },
            "VachanUser":{ 
                "user_email": "vachantest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Vachan",
                "lastname": "user",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.VACHAN.value
                "app" : TEST_APPS_LIST['VACHAN']
            },
            "APIUser":{
                "user_email": "apitest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Api",
                "lastname": "User",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.API.value
                "app" : TEST_APPS_LIST['API']
            },
            "VachanAdmin":{
                "user_email": "vachanadmintest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Vachan",
                "lastname": "Admin",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.VACHAN.value
                "app" : TEST_APPS_LIST['VACHAN']
            },
            "APIUser2":{
                "user_email": "abctest@mail.test",
                "password": "passwordtest@1",
                "firstname": "Api",
                "lastname": "User two",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.API.value
                "app" : TEST_APPS_LIST['API']
            },
            "AgUser2":{
                "user_email": "agtest2@mail.test",
                "password": "passwordtest@1",
                "firstname": "Autographa",
                "lastname": "User Two",
                "token":"",
                "test_user_id": "",
                # "app" : schema_auth.App.AG.value
                "app" : TEST_APPS_LIST['AG']
            }
        }

API_USER = {
    "email": "apiuser@vachan.testing",
    "name": "API-user",
    "organization": "BCS",
    "password": "secret@!@#$",
    "contacts": {
        "email": "apitestingemail@vachan.com",
        "phone": "None"
    }
}

default_app_keys = {}

#session fixture for access checks working
@pytest.fixture(scope="session", autouse=True)
def create_user_session_run_at_start():
    try:
        print("Session fixture for default apps and create user------------------>")
        from .test_auth_basic import register,delete_user_identity,assign_roles,SUPER_USER,SUPER_PASSWORD
        from .test_auth_app import delete_app_key, generate_app_key, register_app, delete_app
        from app.auth.auth_app import DEFAULT_APPS

        # Generate appkey for default apps
        for app in DEFAULT_APPS:
            data = {
                "app_email": app["email"],
                "password": app["password"]
            }
            response = generate_app_key(data)
            default_app_keys[app["name"]] = {"key" : response.json()['key']}
            default_app_keys[app["name"]]["id"] = response.json()['appId']
        
        #userTokens
        for user_data in initial_test_users:
            current_user = initial_test_users[user_data]
            data = {
                "email": current_user['user_email'],
                "password": current_user['password'],
                "firstname": current_user['firstname'],
                "lastname": current_user['firstname']
            }
            if current_user['app'] == TEST_APPS_LIST['API']:
                current_app_key = None
            else:
                current_app_key = default_app_keys[current_user['app']]["key"]
            response = register(data, app_key= current_app_key)
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
        role_list = [TEST_ROLE_LIST['AGADMIN']]
        response = assign_roles(super_data,role_user_id,role_list)
        assert response.status_code == 201
        assert response.json()["role_list"] == \
            [TEST_ROLE_LIST['AGUSER'], TEST_ROLE_LIST['AGADMIN']]
            # [schema_auth.AdminRoles.AGUSER.value, schema_auth.AdminRoles.AGADMIN.value]
        #VachanAdmin
        role_user_id = initial_test_users["VachanAdmin"]["test_user_id"]
        # role_list = [schema_auth.AdminRoles.VACHANADMIN.value]
        role_list = [TEST_ROLE_LIST['VACHANADMIN']]
        response = assign_roles(super_data,role_user_id,role_list)
        assert response.status_code == 201
        assert response.json()["role_list"] == \
            [TEST_ROLE_LIST['VACHANUSER'], TEST_ROLE_LIST['VACHANADMIN']]
            # [schema_auth.AdminRoles.VACHANUSER.value, schema_auth.AdminRoles.VACHANADMIN.value]
        #BcsDeveloper
        role_user_id = initial_test_users["BcsDev"]["test_user_id"]
        # role_list = [schema_auth.AdminRoles.BCSDEV.value]
        role_list = [TEST_ROLE_LIST['BCSDEV']]
        response = assign_roles(super_data,role_user_id,role_list)
        assert response.status_code == 201
        assert response.json()["role_list"] == \
            [TEST_ROLE_LIST['APIUSER'],TEST_ROLE_LIST['BCSDEV']]
            # [schema_auth.AdminRoles.APIUSER.value, schema_auth.AdminRoles.BCSDEV.value]
        
        # Register API app
        register_resp = register_app(API_USER, default_app_keys[TEST_APPS_LIST['VACHANADMIN']]["key"],
            user_token=initial_test_users["VachanAdmin"]["token"])
        default_app_keys[API_USER["name"]] = {"key" : register_resp.json()["key"]}
        default_app_keys[API_USER["name"]]["id"] = register_resp.json()["registered_details"]["id"]

        yield initial_test_users
    finally:
        # Delete API app
        del_resp = delete_app(default_app_keys[API_USER["name"]]["id"],
            default_app_keys[TEST_APPS_LIST['VACHANADMIN']]["key"],
            user_token=initial_test_users["VachanAdmin"]["token"])

        delete_list = []
        for user_data in initial_test_users:
            current_user = initial_test_users[user_data]
            delete_list.append(current_user["test_user_id"])
        delete_user_identity(delete_list)

        # delete keys of default apps
        for app in default_app_keys:
            if app != API_USER["name"]:
                response = delete_app_key(default_app_keys[app]["key"], app)
                assert response.status_code == 200
        print("Session fixture for create user END------------------>")

