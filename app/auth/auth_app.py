"""App Authentication related functions related to Kratos API"""

import os
import json
import requests
from custom_exceptions import GenericException, UnprocessableException, AlreadyExistsException,\
    NotAvailableException
from dependencies import log

PUBLIC_BASE_URL = os.environ.get("VACHAN_KRATOS_PUBLIC_URL",
                                    "http://127.0.0.1:4433/")+"self-service/"
ADMIN_BASE_URL = os.environ.get("VACHAN_KRATOS_ADMIN_URL", "http://127.0.0.1:4434/")

def app_register_kratos(register_details, db_):#pylint: disable=too-many-locals, inconsistent-return-statements, unused-argument
    """register app with kratos"""
    # https://github.com/ory/kratos/issues/765 - not yet implemented to select schema in
    #reg flow creation
    # work around for obtaining the same
    registerapp_url = PUBLIC_BASE_URL+"registration/api"
    reg_flow = requests.get(registerapp_url, timeout=10)
    if reg_flow.status_code == 200:
        password = register_details["password"] if \
            isinstance(register_details["password"], str) else \
                register_details["password"].get_secret_value()
        flow_res = json.loads(reg_flow.content)
        reg_flow_id = flow_res["ui"]["action"]
        reg_data = {"traits.email": register_details["email"],
                    "method": "password",
                    "password": password
                }
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data, timeout=10)
        reg_response = json.loads(reg_req.content)
        if reg_req.status_code == 200:
            # update schema to app
            contact_email = register_details["contacts"]["email"]
            contact_phone = register_details["contacts"]["phone"]
            update_data = {
                "id":reg_response["identity"]["id"],
                "state":reg_response["identity"]["state"],
                "schema_id": "app",
                "traits":{
                "email": register_details["email"],
                "name": register_details["name"],
                "organization": register_details["organization"],
                "contacts": {
                    "email": contact_email,
                    "phone": contact_phone
                        }
                    }
                }
            update_url = f"{ADMIN_BASE_URL}admin/identities/{reg_response['identity']['id']}"
            update_req = requests.put(update_url, headers=headers,\
                json=update_data, timeout=10)
            update_response = json.loads(update_req.content)
            if update_req.status_code == 200:
                # call apis for db -> new app (with default role), new role -> here
                #call functions for refresh global var of APP , ROLES --> here
                #if _db value is None
                #no need to update the DB tables (default apps register on)'''
                # register success return data
                return {
                    "message":"Registration Successfull",
                    "registered_details":{
                        "id":update_response["id"],
                        "email":update_response["traits"]["email"],
                        "name": update_response["traits"]["name"],
                        "organization": update_response["traits"]["organization"],
                        "contacts": {
                            "email": update_response["traits"]["contacts"]["email"],
                            "phone": update_response["traits"]["contacts"]["phone"]
                        }
                    },
                    "key":reg_response["session_token"]
                }
            requests.delete(update_url, headers=headers, timeout=10)
            log.error('Register App Failed: %s', update_response['error']['message'])
            raise GenericException(update_response['error']["message"])
        if "messages" in reg_response["ui"]:
            err_txt = reg_response["ui"]["messages"][0]["text"]
            err_msg = \
        "An account with the same identifier (email, phone, username, ...) exists already."
            if err_txt == err_msg:
                log.error('Register App Failed: %s', err_txt)
                raise AlreadyExistsException(err_txt)
        else :
            error_base = reg_response['ui']['nodes']
            for field in error_base:
                if field['messages'] != []:
                    log.error("Reg app failed %s", field['messages'][0]['text'])
                    raise UnprocessableException(field['messages'][0]['text'])

# def app_update_kratos(update_data):
#     """update app data with kratos"""

def get_filter_apps(name=None, app_id=None, org=None):
    """filters apps data from kratos db"""
    base_url = f"{ADMIN_BASE_URL}admin/identities"
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
            "email": "",
            "phone": ""
        }
    },
    {
        "email": os.environ.get("VACHANONLINE_APP_EMAIL", "vachanonline@vachan.testing"),
        "name": "Vachan-online or vachan-app",
        "organization": "BCS",
        "password": os.environ.get("VACHANONLINE_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "",
            "phone": ""
        }
    },
    {
        "email": os.environ.get("VACHANADMIN_APP_EMAIL", "vachanadmin@vachan.testing"),
        "name": "VachanAdmin",
        "organization": "BCS",
        "password": os.environ.get("VACHANADMIN_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "",
            "phone": ""
        }
    },
    {
        "email": os.environ.get("APIUSER_APP_EMAIL", "apiuser@vachan.testing"),
        "name": "API-user",
        "organization": "BCS",
        "password": os.environ.get("APIUSER_APP_SECRET", "secret@!@#$"),
        "contacts": {
            "email": "",
            "phone": ""
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
