"""router for authentication endpoints"""
import json
from custom_exceptions import NotAvailableException
from fastapi import APIRouter, Depends
#pylint: disable=E0401
from authentication import AuthHandler
import schema_auth
#pylint: disable=C0412
from authentication import user_register_kratos,user_login_kratos,user_role_add ,\
     verify_role_permision,delete_identity
from custom_exceptions import PermisionException

router = APIRouter()
auth_handler = AuthHandler()

#Authentication apis
@router.post('/register',response_model=schema_auth.register_response,
responses={400: {"model": schema_auth.commmon_error}},
tags=["Authentication"])
def register(register_details:schema_auth.Registration):
    """user register | Values for App Name : ag , vachan, None """
    data = user_register_kratos(register_details)
    return data

@router.post('/login',response_model=schema_auth.login_response,
responses={401: {"model": schema_auth.commmon_error}},
tags=["Authentication"])
def login(auth_details:schema_auth.AuthDetails):
    """user login"""
    data = user_login_kratos(auth_details)
    return data

@router.post('/logout',response_model=schema_auth.logout_response,
responses={403: {"model": schema_auth.commmon_error},
401: {"model": schema_auth.commmon_error}},
tags=["Authentication"])
def logout(message = Depends(auth_handler.kratos_logout)):
    """user logout"""
    return message

@router.post('/userrole',response_model=schema_auth.userrole_response,
responses={403: {"model": schema_auth.commmon_error},
401: {"model": schema_auth.commmon_error}}
,tags=["Authentication"])
def userrole(role_data:schema_auth.userrole,
permision = Depends(auth_handler.kratos_session_validation)):
    """Update User Roles
        User roles should provide in an ARRAY -
        Array values will overwrite the exisitng array of roles -
        No roles will be allocated on registration , will be consider as a normal user -
        avaialable roles are
        ["VachanAdmin" ,"AgAdmin"]
    """
    verified = verify_role_permision(api_name="userRole",permision=permision)
    if verified:
        user_id = role_data.userid
        role_list = role_data.roles
        data=user_role_add(user_id,role_list)
    else:
        raise PermisionException("User have no permision to access API")
    return data

@router.delete('/delete-identity',response_model=schema_auth.identity_delete_response,
responses={404: {"model": schema_auth.commmon_error},
401: {"model": schema_auth.commmon_error}},
tags=["Authentication"])
def delete_user(user:schema_auth.user_identity,
permision = Depends(auth_handler.kratos_session_validation)):
    """identity delete"""
    verified = verify_role_permision(api_name="delete_identity",permision=permision)
    if verified:
        response = delete_identity(user.userid)
        if response.status_code == 404:
            raise NotAvailableException("Unable to locate the resource")
        else:
            id = user.userid
            out =  {"success":"deleted identity %s"%id}
    else:
        raise PermisionException("User have no permision to access API")
    return out

"""responses={403: {"model": schema_auth.commmon_error},
401: {"model": schema_auth.commmon_error},
404: {"model": schema_auth.commmon_error}},

"""