"""router for authentication endpoints"""
from fastapi import APIRouter, Depends, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import types
from sqlalchemy.orm import Session
from schema import schema_auth, schemas
from custom_exceptions import NotAvailableException
from dependencies import log , get_db
from auth.authentication import user_register_kratos,user_login_kratos,user_role_add ,\
    delete_identity , get_auth_access_check_decorator , get_user_or_none, kratos_logout

router = APIRouter()

@router.post("/token")
async def form_login(form_data: OAuth2PasswordRequestForm = Depends()):
    '''An additional login option using form input'''
    user = user_login_kratos(form_data.username,form_data.password)
    return {"access_token": user["token"], "token_type": "bearer"}

#Authentication apis
@router.post('/v2/user/register',response_model=schema_auth.RegisterResponse,
responses={400: {"model": schemas.ErrorResponse}},
status_code=201,tags=["Authentication"])
@get_auth_access_check_decorator
async def register(register_details:schema_auth.Registration,request: Request,#pylint: disable=unused-argument
app_type: schema_auth.AppInput=Query(schema_auth.App.API),user_details =Depends(get_user_or_none),#pylint: disable=unused-argument
db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''Registration for Users
    * user_email and password fiels are mandatory
    * App type will be None by default, App Type will decide \
        a default role for user
    * first and last name fields are optional'''
    log.info('In User Registration')
    log.debug('registration:%s',register_details)
    return user_register_kratos(register_details,app_type)

@router.get('/v2/user/login',response_model=schema_auth.LoginResponse,
responses={401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
@get_auth_access_check_decorator
async def login(user_email: str,password: types.SecretStr,
    request: Request,user_details =Depends(get_user_or_none),#pylint: disable=unused-argument
    db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''Login for All Users
    * user_email and password fiels are mandatory
    * Successful login will return a token for user for a time period'''
    log.info('In User Login')
    log.debug('login:%s',user_email)
    return user_login_kratos(user_email,password)

@router.get('/v2/user/logout',response_model=schema_auth.LogoutResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
def logout(request: Request,user_details =Depends(get_user_or_none),#pylint: disable=unused-argument
    db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''Logout
    * Loging out will end the expiry of a token even if the time period not expired.
    * Successful login will return a token for user for a time period'''
    log.info('In User Logout')
    if 'Authorization' in request.headers:
        token = request.headers['Authorization']
        token = token = token.split(' ')[1]
        message = kratos_logout(token)
        log.debug('logout:%s',message)
    else:
        raise NotAvailableException(
        "The provided Session Token could not be found, is invalid, or otherwise malformed")
    return message

@router.put('/v2/user/userrole',response_model=schema_auth.UseroleResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse},
422: {"model": schemas.ErrorResponse}},
status_code=201,tags=["Authentication"])
@get_auth_access_check_decorator
async def userrole(role_data:schema_auth.UserRole,request: Request,#pylint: disable=unused-argument
user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):#pylint: disable=unused-argument
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
    return user_role_add(user_id,role_list)

@router.delete('/v2/user/delete-identity',response_model=schema_auth.IdentityDeleteResponse,
responses={404: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}},
status_code=200,tags=["Authentication"])
@get_auth_access_check_decorator
async def delete_user(user:schema_auth.UserIdentity,request: Request,#pylint: disable=unused-argument
user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''Delete Identity
    * unique Identity key can be used to delete an exisiting identity'''
    log.info('In Identity Delete')
    log.debug('identity-delete:%s',user)
    user_id = user.userid
    delete_identity(user.userid)
    return {"message":"deleted identity %s"%user_id}
