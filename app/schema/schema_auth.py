"""schema for auth related"""
from enum import Enum
from typing import List
from pydantic import BaseModel
from pydantic import types

#pylint: disable=too-few-public-methods
class ResourceType(str, Enum):
    '''Classify DB resources for defineing access rights on them'''
    METACONTENT = "meta contents like licences, languages, versions or content types"
    CONTENT = "contents like bibles, commentaries, infographics, dictionary or videos"
    PROJECT = "Ag or translation project"
    USER = "all users in our system (Kratos)"
    TRANSLATION = "generic translation apis"
    LOOKUP = "Lookup contents"
    RESEARCH = "Research-Material"

class App(str, Enum):
    '''Defined apps'''
    AG = "Autographa"
    VACHAN = "Vachan-online or vachan-app"
    API = "API-user"
    VACHANADMIN = "VachanAdmin"

class AppInput(str, Enum):
    '''Input fields for App in Registration'''
    AG = "Autographa"
    VACHAN = "Vachan-online or vachan-app"
    API = "API-user"

class Registration(BaseModel):
    """kratos registration input"""
    email:str
    password:types.SecretStr
    firstname:str = None
    lastname:str = None

class EditUser(BaseModel):
    """kratos registration input"""
    firstname:str
    lastname:str

class AdminRoles(str, Enum):
    '''Admin Roles'''
    SUPERADMIN = 'SuperAdmin'
    VACHANADMIN = 'VachanAdmin'
    AGADMIN = 'AgAdmin'
    AGUSER = 'AgUser'
    VACHANUSER = 'VachanUser'
    APIUSER = 'APIUser'
    BCSDEV = 'BcsDeveloper'

class FilterRoles(str, Enum):
    '''Filter roles for get users'''
    ALL = "All"
    AG = "Autographa"
    VACHAN = "Vachan-online or vachan-app"
    API = "API-user"

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
    Permissions:List[App]

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

class TableHeading(int, Enum):
    """Heading of permission table"""
    ENDPOINT = 0
    METHOD = 1
    REQUESTAPP = 2
    USERNEEDED = 3
    RESOURCETYPE = 4
    PERMISSION = 5

class IdentitityListResponse(BaseModel):
    """Response object of list of identities"""
    userId:str
    name: dict
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example":{
            "userId": "ecf57420-9rg0-4048-b56b-dc56fc57c4ed",
            "name": {
                "last": "lastname",
                "first": "firstname",
                "fullname": "Full Name"
            }
        }}
