"""schema for auth related"""
#No name 'BaseModel' in module 'pydantic' (no-name-in-module)
#pylint: disable=E0611
from pydantic import BaseModel

#Too few public methods (0/2) (too-few-public-methods)
#pylint: disable=R0903
class AuthDetails(BaseModel):
    """schema for authentication input"""
    username:str
    password:str

#pylint: disable=R0903
class Registration(BaseModel):
    """kratos registration input"""
    email:str
    password:str
    firstname:str
    lastname:str
    appname:str

#pylint: disable=R0903
class UserRole(BaseModel):
    """kratos user role input"""
    userid:str
    roles:list

#pylint: disable=R0903
class UserIdentity(BaseModel):
    """kratos user role input"""
    userid:str

#pylint: disable=R0903
class RegistrationOut(BaseModel):
    """registration output"""
    id:str
    email:str
    Permisions:list

#pylint: disable=R0903
class RegisterResponse(BaseModel):
    """Response object of registration"""
    details:str
    registered_details:RegistrationOut
    token:str = None

#pylint: disable=R0903
class LoginResponse(BaseModel):
    """Response object of login"""
    details:str
    token:str

#pylint: disable=R0903
class LogoutResponse(BaseModel):
    """Response object of logout"""
    message:str

#pylint: disable=R0903
class CommmonError(BaseModel):
    """login error"""
    error:str
    details:str

#pylint: disable=R0903
class UseroleResponse(BaseModel):
    """user role update response"""
    details:str
    role_list:list

#pylint: disable=R0903
class IdentityDeleteResponse(BaseModel):
    """user identity delete response"""
    success:str
        