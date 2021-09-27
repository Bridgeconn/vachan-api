"""schema for auth related"""

from enum import Enum
from typing import List
from pydantic import BaseModel
from pydantic import types


#pylint: disable=R0903
class AppType(str, Enum):
    '''user role based on app'''
    AGUSER = 'AgUser'
    VACHANUSER = 'VachanUser'
    NONE = 'None'


class Registration(BaseModel):
    """kratos registration input"""
    email:str
    password:types.SecretStr
    firstname:str = None
    lastname:str = None

class AdminRoles(str, Enum):
    '''Admin Roles'''
    SUPERADMIN = 'SuperAdmin'
    VACHANADMIN = 'VachanAdmin'
    AGADMIN = 'AgAdmin'
    AGUSER = 'AgUser'
    VACHANUSER = 'VachanUser'

class UserRole(BaseModel):
    """kratos user role input"""
    userid:str
    roles:List[AdminRoles]

class UserIdentity(BaseModel):
    """kratos user role input"""
    userid:str

class RegistrationOut(BaseModel):
    """registration output"""
    id:str
    email:str
    Permisions:List[AppType]

class RegisterResponse(BaseModel):
    """Response object of registration"""
    message:str
    registered_details:RegistrationOut
    token:str = None

class LoginResponse(BaseModel):
    """Response object of login"""
    message:str
    token:str

class LogoutResponse(BaseModel):
    """Response object of logout"""
    message:str

class CommmonError(BaseModel):
    """login error"""
    error:str
    details:str

class UseroleResponse(BaseModel):
    """user role update response"""
    message:str
    role_list:list

class IdentityDeleteResponse(BaseModel):
    """user identity delete response"""
    message:str
        