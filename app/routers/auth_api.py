"""router for authentication endpoints"""
from typing import List
from fastapi import APIRouter, Body, Depends, Query, Request, Path
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import types
from sqlalchemy.orm import Session
from schema import schema_auth, schemas
from custom_exceptions import NotAvailableException
from dependencies import log , get_db
from auth.authentication import user_register_kratos,user_login_kratos,user_role_add ,\
    delete_identity , get_auth_access_check_decorator , get_user_or_none, kratos_logout,\
    get_all_or_one_kratos_users,update_kratos_user
from auth.auth_app import app_register_kratos

router = APIRouter()

#pylint: disable=too-many-arguments
@router.post("/token")
async def form_login(form_data: OAuth2PasswordRequestForm = Depends()):
    '''An additional login option using form input'''
    user = user_login_kratos(form_data.username,form_data.password)
    return {"access_token": user["token"], "token_type": "bearer"}

#Authentication apis
@router.post('/v2/user/register',response_model=schema_auth.RegisterResponse,
    responses={400: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ErrorResponse}},
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
,tags=["Authentication", "App"])
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
responses={403: {"model": schemas.ErrorResponse},404:{"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse}}
,tags=["Authentication", "App"])
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

@router.get('/v2/users', response_model=List[schema_auth.IdentitityListResponse],
responses={401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
@get_auth_access_check_decorator
async def get_identities_list(request: Request,#pylint: disable=unused-argument
    name: str = Query(None, example="Bridgeconn"),
    user_id: str = Query(None, example="ecf57420-9rg0-40t8-b56b-dce1fc52c452"),
    roles:List[schema_auth.FilterRoles]=Query([schema_auth.FilterRoles.ALL]),
    skip: int = Query(0, ge=0),limit: int = Query(100, ge=0),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''fetches all the users
    * the optional query parameter can be used to filter the result set
    * name = fullname, firstname or lastname to search
    * user_id = user_id will not consider other filter params
    * roles= None, select one or more type
    * limit=n: limits the no. of items to be returned to n
    * skip=n: skips the first n objects in return list'''
    log.info('In User List Identities')
    log.debug('name: %s, roles: %s, user_id: %s, skip: %s, limit: %s',
        name, roles, user_id, skip, limit)
    return get_all_or_one_kratos_users(rec_user_id=user_id,skip=skip,
        limit=limit,name=name,roles=roles)

@router.get('/v2/user/{user_id}', response_model=schema_auth.UserProfileResponse,
responses={401: {"model": schemas.ErrorResponse}}
,tags=["Authentication"])
@get_auth_access_check_decorator
async def get_user_profile(request: Request,#pylint: disable=unused-argument
    user_id:str =Path(...,example="4bd012fd-7de8-4d66-928f-4925ee9bb"),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''fetches user profile Data'''
    log.info('In User Profile')
    log.debug('userid: %s',user_id)
    return get_all_or_one_kratos_users(rec_user_id=user_id)[0]

@router.put('/v2/user/role',response_model=schema_auth.UseroleResponse,
responses={403: {"model": schemas.ErrorResponse},
401: {"model": schemas.ErrorResponse},409: {"model": schemas.ErrorResponse},
422: {"model": schemas.ErrorResponse},500: {"model": schemas.ErrorResponse}},
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
    log.debug('role:%s',role_data)
    user_id = role_data.userid
    role_list = role_data.roles
    return user_role_add(user_id,role_list)

@router.put('/v2/user/{user_id}', response_model=schema_auth.UserUpdateResponse,
responses={401: {"model": schemas.ErrorResponse},404: {"model": schemas.ErrorResponse},
500: {"model": schemas.ErrorResponse}},status_code=201,tags=["Authentication"])
@get_auth_access_check_decorator
async def edit_user(request: Request,#pylint: disable=unused-argument
    user_id:str =Path(...,example="4bd012fd-7de8-4d66-928f-4925ee9bb"),
    edit_details:schema_auth.EditUser = Body(...),
    user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''update user data'''
    log.info('In edit User Identity')
    log.debug('user_id: %s, user_details: %s',user_id, edit_details)
    data =  update_kratos_user(rec_user_id=user_id,data=edit_details)
    return {"message":"User details updated successfully","data":data}

@router.delete('/v2/user/delete-identity',response_model=schema_auth.IdentityDeleteResponse,
    responses={404: {"model": schemas.ErrorResponse},
    401: {"model": schemas.ErrorResponse}},
    status_code=200,tags=["Authentication",  "App"])
@get_auth_access_check_decorator
async def delete_user(user:schema_auth.UserIdentity,request: Request,#pylint: disable=unused-argument
user_details =Depends(get_user_or_none),db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''Delete Identity
    * unique Identity key can be used to delete an exisiting identity'''
    log.info('In Identity Delete')
    log.debug('identity-delete:%s',user)
    user_id = user.userid
    delete_identity(user.userid)
    return {"message":f"deleted identity {user_id}"}

# Authentication for Apps
@router.post('/v2/app/register',response_model=schema_auth.RegisterAppResponse,
    responses={400: {"model": schemas.ErrorResponse},422: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ErrorResponse}, 409: {"model": schemas.ErrorResponse}},
    status_code=201,tags=["App"])
# @get_auth_access_check_decorator
async def register_app(register_details:schema_auth.RegistrationAppIn,request: Request,#pylint: disable=unused-argument
user_details =Depends(get_user_or_none),#pylint: disable=unused-argument
db_: Session = Depends(get_db)):#pylint: disable=unused-argument
    '''Registration for Apps
    * email, name, organization, password fiels are mandatory
    * One of the contact details is mandatory'''
    log.info('In App Registration')
    log.debug('APp registration:%s',register_details)
    return app_register_kratos(register_details, db_)
