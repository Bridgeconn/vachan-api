"""App Authentication related functions related to Kratos API"""

import os
import json
import requests
from custom_exceptions import GenericException, UnprocessableException, AlreadyExistsException
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
        flow_res = json.loads(reg_flow.content)
        reg_flow_id = flow_res["ui"]["action"]
        reg_data = {"traits.email": register_details.email,
                    "method": "password",
                    "password": register_details.password.get_secret_value()
                }
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        reg_req = requests.post(reg_flow_id,headers=headers,json=reg_data, timeout=10)
        reg_response = json.loads(reg_req.content)
        if reg_req.status_code == 200:
            # update schema to app
            contact_email = register_details.contacts["email"]
            contact_phone = register_details.contacts["phone"]
            update_data = {
                "id":reg_response["identity"]["id"],
                "state":reg_response["identity"]["state"],
                "schema_id": "app",
                "traits":{
                "email": register_details.email,
                "name": register_details.name,
                "organization": register_details.organization,
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
            log.error('Register App Failed: %s', update_response['message'])
            raise GenericException(update_response["message"])
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

        log.error("Unexpected response from Kratos")
        log.error(reg_req.status_code)
        log.error(reg_req.json())
        raise GenericException("Got unexpected response from Kratos")

# def app_update_kratos(update_data):
#     """update app data with kratos"""
