"""router for authentication endpoints"""
from fastapi import APIRouter, Depends, Query
#pylint: disable=E0611
from pydantic.types import SecretStr
#pylint: disable=E0401
import schema_auth
import schemas
from authentication import user_register_kratos,user_login_kratos,user_role_add ,\
     verify_role_permision,delete_identity ,AuthHandler
from custom_exceptions import PermisionException, NotAvailableException

router = APIRouter()
auth_handler = AuthHandler()

#Authentication apis
@router.post('/v2/user/register',response_model=schema_auth.RegisterResponse,
responses={400: {"model": schemas.ErrorResponse}},
status_code=201,tags=["Authentication"])
def register(register_details:schema_auth.Registration,
app_type: schema_auth.AppType=Query(schema_auth.AppType.none)):
    """user register"""
    data = user_register_kratos(register_details,app_type)
    return data

@router.get('/v2/user/login',response_model=schema_auth.LoginResponse,
responses={401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
def login(username: str,password: SecretStr):
    """user login"""
    data = user_login_kratos(username,password)
    return data

@router.get('/v2/user/logout',response_model=schema_auth.LogoutResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
def logout(message = Depends(auth_handler.kratos_logout)):
    """user logout"""
    return message

@router.post('/v2/user/userrole',response_model=schema_auth.UseroleResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse},
422: {"model": schemas.ErrorResponse}},
status_code=201,tags=["Authentication"])
def userrole(role_data:schema_auth.UserRole,
permision = Depends(auth_handler.kratos_session_validation)):
    '''Update User Roles.
    * User roles should provide in an ARRAY
    * Array values will overwrite the exisitng array of roles
    * No roles will be allocated on registration , will be consider as a normal user.
    * avaialable roles are
    * [VachanAdmin , AgAdmin , AgUser , VachanUser] '''
    verified = verify_role_permision(api_name="userRole",permision=permision)
    if verified:
        user_id = role_data.userid
        role_list = role_data.roles
        data=user_role_add(user_id,role_list)
    else:
        raise PermisionException("User have no permision to access API")
    return data

@router.delete('/v2/user/delete-identity',response_model=schema_auth.IdentityDeleteResponse,
responses={404: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}},
status_code=200,tags=["Authentication"])
def delete_user(user:schema_auth.UserIdentity,
permision = Depends(auth_handler.kratos_session_validation)):
    """identity delete"""
    verified = verify_role_permision(api_name="delete_identity",permision=permision)
    if verified:
        response = delete_identity(user.userid)
        #pylint: disable=R1720
        if response.status_code == 404:
            raise NotAvailableException("Unable to locate the resource")
        else:
            user_id = user.userid
            out =  {"message":"deleted identity %s"%user_id}
    else:
        raise PermisionException("User have no permision to access API")
    return out
