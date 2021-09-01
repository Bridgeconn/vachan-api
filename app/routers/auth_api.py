from fastapi import APIRouter, Query, Body, Depends, Path
from authentication import AuthHandler
import schema_auth
from authentication import user_register_kratos,user_login_kratos,user_role_add , verify_role_permision
from custom_exceptions import PermisionException

router = APIRouter()
auth_handler = AuthHandler()

#Authentication apis
@router.post('/register',tags=["Authentication"])
def register(register_details:schema_auth.Registration):
    """user register | Values for App Name : ag , vachan, None """
    data = user_register_kratos(register_details)
    return data

@router.post('/login',tags=["Authentication"])
def login(auth_details:schema_auth.AuthDetails):
    """user login"""
    data = user_login_kratos(auth_details)
    return data

@router.post('/logout',tags=["Authentication"])
def logout(message = Depends(auth_handler.kratos_logout)):
    """user logout"""
    return message

@router.post('/userrole',tags=["Authentication"])
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
        return data
    else:
        raise PermisionException("User have no permision to access API")
