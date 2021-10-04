"""router for authentication endpoints"""
from fastapi import APIRouter, Depends, Query, Request
from pydantic import types
from sqlalchemy.orm import Session
import schema_auth
import schemas
from dependencies import log , get_db
from authentication import user_register_kratos,user_login_kratos,user_role_add ,\
     delete_identity ,AuthHandler, get_request_context_access_rights,\
         get_auth_access_check_decorator
from custom_exceptions import PermisionException, NotAvailableException

router = APIRouter()
auth_handler = AuthHandler()

#Authentication apis
@router.post('/v2/user/register',response_model=schema_auth.RegisterResponse,
responses={400: {"model": schemas.ErrorResponse}},
status_code=201,tags=["Authentication"])
@get_auth_access_check_decorator
async def register(register_details:schema_auth.Registration,request: Request,
app_type: schema_auth.App=Query(schema_auth.App.API),db_: Session = Depends(get_db)):
    '''Registration for Users
    * user_email and password fiels are mandatory
    * App type will be None by default, App Type will decide \
        a default role for user
    * first and last name fields are optional'''
    log.info('In User Registration')
    log.debug('registration:%s',register_details)

    # verified = get_request_context_access_rights(request,db_,resource_id=None,user_id=None,
    #     user_roles=None,resource_type=None)
    # if verified:
    #     data = user_register_kratos(register_details,app_type)
    # else:
    #     raise PermisionException("Access Permission Denied for the URL")
    return user_register_kratos(register_details,app_type)

@router.get('/v2/user/login',response_model=schema_auth.LoginResponse,
responses={401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
@get_auth_access_check_decorator
async def login(user_email: str,password: types.SecretStr,
    request: Request,db_: Session = Depends(get_db)):
    '''Login for All Users
    * user_email and password fiels are mandatory
    * Successful login will return a token for user for a time period'''
    log.info('In User Login')
    log.debug('login:%s',user_email)
    print("====>Login router is working")
    # verified = get_request_context_access_rights(request,db_,resource_id=None,user_id=None,
    #     user_roles=None,resource_type=None)
    # if verified:
    #     data = user_login_kratos(user_email,password)
    # else:
    #     raise PermisionException("Access Permission Denied for the URL")
    return user_login_kratos(user_email,password)

@router.get('/v2/user/logout',response_model=schema_auth.LogoutResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
def logout(message = Depends(auth_handler.kratos_logout)):
    '''Logout
    * Loging out will end the expiry of a token even if the time period not expired.
    * Successful login will return a token for user for a time period'''
    log.info('In User Logout')
    log.debug('logout:%s',message)
    return message

@router.put('/v2/user/userrole',response_model=schema_auth.UseroleResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse},
422: {"model": schemas.ErrorResponse}},
status_code=201,tags=["Authentication"])
@get_auth_access_check_decorator
async def userrole(role_data:schema_auth.UserRole,request: Request,
user_details = Depends(auth_handler.kratos_session_validation),db_: Session = Depends(get_db)):
    '''Update User Roles.
    * User roles should provide in an ARRAY
    * Array values will overwrite the exisitng array of roles
    * No roles will be allocated on registration , will be consider as a normal user.
    * avaialable roles are
    * [VachanAdmin , AgAdmin , AgUser , VachanUser] '''
    log.info('In User Role')
    log.debug('userrole:%s',role_data)

    user_id = role_data.userid
    role_list = role_data.roles
    # verified = get_request_context_access_rights(request,db_,resource_id=None,
    # user_id=user_details["user_id"], user_roles=user_details["user_roles"],
    # resource_type=None)
    # if verified:
    #     user_id = role_data.userid
    #     role_list = role_data.roles
    #     data=user_role_add(user_id,role_list)
    # else:
    #     raise PermisionException("User have no permision to access API")
    return user_role_add(user_id,role_list)

@router.delete('/v2/user/delete-identity',response_model=schema_auth.IdentityDeleteResponse,
responses={404: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}},
status_code=200,tags=["Authentication"])
@get_auth_access_check_decorator
async def delete_user(user:schema_auth.UserIdentity,request: Request,
user_details = Depends(auth_handler.kratos_session_validation),db_: Session = Depends(get_db)):
    '''Delete Identity
    * unique Identity key can be used to delete an exisiting identity'''
    log.info('In Identity Delete')
    log.debug('identity-delete:%s',user)

    user_id = user.userid
    delete_identity(user.userid)
    # verified = get_request_context_access_rights(request,db_,resource_id=None,
    # user_id=user_details["user_id"], user_roles=user_details["user_roles"],
    # resource_type=None)
    # # if verified:
    #     response = delete_identity(user.userid)

    #     if response.status_code == 404:
    #         raise NotAvailableException("Unable to locate the resource")

    #     user_id = user.userid
    #     out =  {"message":"deleted identity %s"%user_id}
    # else:
    #     raise PermisionException("User have no permision to access API")
    return {"message":"deleted identity %s"%user_id}
