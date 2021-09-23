"""schema for auth related"""

#pylint: disable=E0611
from enum import Enum
from typing import List
from pydantic import BaseModel
from pydantic import types

#pylint: disable=C0103

#pylint: disable=R0903
class AppType(str, Enum):
    '''user role based on app'''
    aguser = 'AgUser'
    vachanuser = 'VachanUser'
    none = 'None'

#pylint: disable=R0903
class Registration(BaseModel):
    """kratos registration input"""
    email:str
    password:types.SecretStr
    firstname:str = None
    lastname:str = None

#pylint: disable=R0903
class AdminRoles(str, Enum):
    '''Admin Roles'''
    superadmin = 'SuperAdmin'
    vachanadmin = 'VachanAdmin'
    agadmin = 'AgAdmin'
    aguser = 'AgUser'
    vachanuser = 'VachanUser'

#pylint: disable=R0903
class UserRole(BaseModel):
    """kratos user role input"""
    userid:str
    roles:List[AdminRoles]

#pylint: disable=R0903
class UserIdentity(BaseModel):
    """kratos user role input"""
    userid:str

#pylint: disable=R0903
class RegistrationOut(BaseModel):
    """registration output"""
    id:str
    email:str
    Permisions:List[AppType]

#pylint: disable=R0903
class RegisterResponse(BaseModel):
    """Response object of registration"""
    message:str
    registered_details:RegistrationOut
    token:str = None

#pylint: disable=R0903
class LoginResponse(BaseModel):
    """Response object of login"""
    message:str
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
    message:str
    role_list:list

#pylint: disable=R0903
class IdentityDeleteResponse(BaseModel):
    """user identity delete response"""
    message:str
        