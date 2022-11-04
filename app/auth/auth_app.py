"""App Authentication related functions related to Kratos API"""

import os
import json
import requests
from custom_exceptions import GenericException, UnprocessableException, AlreadyExistsException,\
    NotAvailableException
from dependencies import log

PUBLIC_BASE_URL_APP = os.environ.get("VACHAN_KRATOS_APP_PUBLIC_URL",
                                    "http://127.0.0.1:4443/")+"self-service/"
ADMIN_BASE_URL_APP = os.environ.get("VACHAN_KRATOS_APP_ADMIN_URL", "http://127.0.0.1:4444/")

def app_register_kratos(register_details, db_):#pylint: disable=too-many-locals, inconsistent-return-statements, unused-argument
    """register app with kratos"""
    # https://github.com/ory/kratos/issues/765 - not yet implemented to select schema in
    #reg flow creation
    # work around for obtaining the same
    registerapp_url = PUBLIC_BASE_URL_APP+"registration/api"
    reg_flow = requests.get(registerapp_url, timeout=10)
    print("register -------------: ", register_details.contacts["phone"])
    if reg_flow.status_code == 200:
        password = register_details["password"] if \
            "password" in register_details else \
            register_details.password.get_secret_value()
        if "email" in register_details:
            email = register_details["email"]
            name = register_details["name"]
            org = register_details["organization"]
            contact_email = register_details["contacts"]["email"]
            contact_phone = register_details["contacts"]["phone"]
        else:
            email = register_details.email
            name = register_details.name
            org = register_details.organization
            contact_email = register_details.contacts["email"]
            contact_phone = "" if register_details.contacts["phone"] is None\
                else register_details.contacts["phone"]
        app_reg_flow_res = json.loads(reg_flow.content)
        app_reg_flow_id = app_reg_flow_res["ui"]["action"]
        app_reg_data = {
                "traits.email": email,
                "traits.name": name,
                "traits.organization": org,
                "traits.contacts.phone": contact_phone,
                "traits.contacts.email": contact_email,
                "password": password,
                "method": "password"
                    }
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        app_reg_req = requests.post(app_reg_flow_id,headers=headers,json=app_reg_data, timeout=10)
        app_reg_response = json.loads(app_reg_req.content)
        if app_reg_req.status_code == 200:
            # call apis/crud for db -> new app (with default role), new role -> here
            #call functions for refresh global var of APP , ROLES --> here
            #if _db value is None
            #no need to update the DB tables (default apps register on)'''
            # register success return data
            app_data = app_reg_response["session"]["identity"]
            return {
                "message":"Registration Successfull",
                "registered_details":{
                    "id":app_data["id"],
                    "email":app_data["traits"]["email"],
                    "name": app_data["traits"]["name"],
                    "organization": app_data["traits"]["organization"],
                    "contacts": {
                        "email": app_data["traits"]["contacts"]["email"],
                        "phone": app_data["traits"]["contacts"]["phone"]\
                            if "phone" in app_data["traits"]["contacts"]\
                            else None
                    }
                },
                "key":app_reg_response["session_token"]
            }
        if "messages" in app_reg_response["ui"]:
            err_txt = app_reg_response["ui"]["messages"][0]["text"]
            err_msg = \
        "An account with the same identifier (email, phone, username, ...) exists already."
            if err_txt == err_msg:
                log.error('Register App Failed: %s', err_txt)
                raise AlreadyExistsException(err_txt)
        else :
            error_base = app_reg_response['ui']['nodes']
            for field in error_base:
                if field['messages'] != []:
                    log.error("Reg app failed %s", field['messages'][0]['text'])
                    raise UnprocessableException(field['messages'][0]['text'])

# def app_update_kratos(update_data):
#     """update app data with kratos"""

def get_filter_apps(name=None, app_id=None, org=None):
    """filters apps data from kratos db"""
    base_url = f"{ADMIN_BASE_URL_APP}admin/identities"
    app_data = []
    if app_id is not None:
        response = requests.get(base_url+"/"+app_id, timeout=10)
        if response.status_code == 200:
            content = json.loads(response.content)
            app_data.append(content["traits"])
        else:
            raise NotAvailableException("App with Id not Exist")
    else:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            for data in json.loads(response.content):
                name_status = True
                org_status = True
                if data["schema_id"] == 'app':
                    if name is None and org is None:
                        app_data.append()
                        continue
                    if name is not None:
                        # name_status = True if name.lower() == \
                        #     data["traits"]["name"].lower() else False
                        name_status = name.lower() == data["traits"]["name"].lower()
                    if org is not None:
                        org_status = org.lower() == data["traits"]["organization"]
                    if name_status and org_status:
                        app_data.append(data["traits"])
        else:
            raise GenericException(detail=json.loads(response.content))
    return app_data


def register_default_apps_on_startup():
    """register default apps on startup of vachan"""
    default_apps = [
    {
        "email": os.environ.get("AG_APP_EMAIL", "Autographa@vachan.testing"),
        "name": "Autographa",
        "organization": "BCS",
        "password": os.environ.get("AG_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "None",
            "phone": "None"
        }
    },
    {
        "email": os.environ.get("VACHANONLINE_APP_EMAIL", "vachanonline@vachan.testing"),
        "name": "Vachan-online or vachan-app",
        "organization": "BCS",
        "password": os.environ.get("VACHANONLINE_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "None",
            "phone": "None"
        }
    },
    {
        "email": os.environ.get("VACHANADMIN_APP_EMAIL", "vachanadmin@vachan.testing"),
        "name": "VachanAdmin",
        "organization": "BCS",
        "password": os.environ.get("VACHANADMIN_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "None",
            "phone": "None"
        }
    },
    {
        "email": os.environ.get("APIUSER_APP_EMAIL", "apiuser@vachan.testing"),
        "name": "API-user",
        "organization": "BCS",
        "password": os.environ.get("APIUSER_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "None",
            "phone": "None"
        }
    }]

    for app in default_apps:
        data = get_filter_apps(app["name"])
        if len(data) > 0:
            print(f"exist app {app['name']}")
            log.info('app %s already exist', app["name"])
        else:
            print("not exist app")
            app_register_kratos(app, db_=None)
