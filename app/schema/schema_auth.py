"""schema for auth related"""
from typing import List
from enum import Enum
from pydantic import BaseModel, validator, types, EmailStr, Field

#pylint: disable=too-few-public-methods

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

# class FilterRoles(str, Enum):
#     '''Filter roles for get users'''
#     ALL = "All"
#     AG = "Autographa"
#     VACHAN = "Vachan-online or vachan-app"
#     API = "API-user"

class UserRole(BaseModel):
    """kratos user role input"""
    userid:str
    roles:list[str]

class UserIdentity(BaseModel):
    """kratos user role input"""
    userid:str

class RegistrationOut(BaseModel):
    """registration output"""
    id:str
    email:str
    Permissions:list

class RegisterResponse(BaseModel):
    """Response object of registration"""
    message:str
    registered_details:RegistrationOut
    token:str = None

class LoginResponse(BaseModel):
    """Response object of login"""
    message:str
    token:str
    userId:str

class LogoutResponse(BaseModel):# print("returned data ------------->", data)
    # print("returned data json -======->", data[0].__dict__)
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

# class TableHeading(int, Enum):
#     """Heading of permission table"""
#     ENDPOINT = 0
#     METHOD = 1
#     REQUESTAPP = 2
#     USERNEEDED = 3
#     RESOURCETYPE = 4
#     PERMISSION = 5

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

class UserProfileResponse(BaseModel):
    """Response object of list of identities"""
    userId:str
    traits: dict
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example":{
            "userId": "ecf57420-9rg0-4048-b56b-dc56fc57c4ed",
            "traits": {
                "name":{"last":"lastname", "first":"firstname"},
                "email":"useremail@test.com",
                "userrole":["AgUser, VachanUser"]
            }
        }}

class UserUpdateResponse(BaseModel):
    """Response object of User Update"""
    message:str
    data: IdentitityListResponse

class RegistrationAppContacts(BaseModel):
    """registration App output"""
    email:EmailStr
    phone:str = None

class RegistrationAppOut(BaseModel):
    """registration App output"""
    id:str
    name:str
    email:str
    organization:str
    contacts:RegistrationAppContacts

class RegisterAppResponse(BaseModel):
    """Response object of App registration"""
    message:str
    registered_details:RegistrationAppOut
    key:str

class RegistrationAppIn(BaseModel):
    """kratos app registration input"""
    email:str
    name:str
    organization:str
    password:types.SecretStr
    contacts:RegistrationAppContacts
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example":{
            "email": "myapp@vachan",
            "name": "my app",
            "organization": "BCS",
            "password": "my secret",
            "contacts": {
                "email": "myappofficial@vachan.org",
                "phone": "+91 1234567890"
            }
        }}
    @validator('contacts')
    def check_phone(cls, val):#pylint: disable=no-self-argument, inconsistent-return-statements
        '''check for phone is present'''
        if val.phone is not None:
            if len(val.phone) <= 0:
                raise ValueError('Phone Should not be blank')
        return {"email" : val.email, "phone" : val.phone}

class LoginResponseApp(BaseModel):
    """Response object of login for app"""
    message:str
    key:str
    appId:str

class AppUpdateResponse(BaseModel):
    """Response object of App data Update"""
    message:str
    data: RegistrationAppOut

class EditAppInput(BaseModel):
    """kratos App update input"""
    ContactEmail:EmailStr
    organization:str
    phone:str = None
    @validator('phone')
    def check_phone(cls, val):#pylint: disable=no-self-argument, inconsistent-return-statements
        '''check for phone is present'''
        if val is not None:
            if len(val) <= 0:
                raise ValueError('Phone Should not be blank')
        return val

class RoleOut(BaseModel):
    '''Return object of roles output'''
    roleId : int
    roleName : str
    roleOfApp : str = None
    roleDescription : str = None
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "roleId": 100011,
                "roleName": "manager",
                "roleOfApp": "xyz",
                "roleDescription": "manager of the app"
            }
        }

class RoleIn(BaseModel):
    """kratos roles update input"""
    roleId :int
    roleName: str
    roleOfApp : str
    roleDescription : str

class RoleResponse(BaseModel):
    '''Return object of role update'''
    message: str
    data: RoleOut

class Roles(BaseModel):
    """kratos roles input"""
    roleName: str
    roleOfApp : str
    roleDescription : str


class PermissionOut(BaseModel):
    """auth permission output object"""
    permissionId:int
    permissionName:str
    permissionDescription:str = None
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "permissionId": 100057,
                "permissionName": "create-data",
                "permissionDescription": "Permission to make POST \
                    calls making new entries to server DB"
            }
        }

class PermissionResponse(BaseModel):
    """Response object of Permission creation"""
    message:str
    data:PermissionOut

class PermissionCreateInput(BaseModel):
    """auth permission crearte input"""
    permissionName:str
    permissionDescription:str = None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "permissionName": "create-data",
                "permissionDescription": "Permission to make POST calls\
                     making new entries to server DB"
            }}

class PermissionUpdateInput(BaseModel):
    """auth permission updation input"""
    permissionId:int
    permissionName:str
    permissionDescription:str
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "permissionId": 100001,
                "permissionName":'create-data',
                "permissionDescription": "Permission to make POST calls\
                     making new entries to server DB"
    }}


class ResourceOut(BaseModel):
    """auth resource output object"""
    resourceTypeId:int
    resourceTypeName:str
    resourceTypeDescription:str = None
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "resourceTypeId": 100057,
                "resourceTypeName": "content",
                "resourceTypeDescription": "resource types"
            }
        }


class AccessRuleCreateInput(BaseModel):
    """auth AccessRule crearte input"""
    entitlement:str
    tag:str
    roles:list[str]
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "entitlement": "content",
                "tag": "create",
                "roles":["registeredUser"]
            }}

class AccessRuleUpdateInput(BaseModel):
    """auth AccessRule update input"""
    ruleId:int
    entitlement:str =None
    tag:str = None
    role:str =None
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "ruleId":100000,
                "entitlement": "content",
                "tag": "create",
                "role":"registeredUser"
            }}


class AccessRulesOut(BaseModel):
    """auth Access Rules output object"""
    ruleId:int
    entitlement:ResourceOut = None
    tag:PermissionOut = None
    role:RoleOut = None
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "ruleId": 100057,
                "entitlement": {},
                "tag": {},
                "roles":{}
            }
        }

class AccessRulesResponse(BaseModel):
    """Response object of AccessRules creation"""
    message:str = Field(..., example="Access rule created successfully")
    data:List[AccessRulesOut] = None

class AccessRulesUpdateResponse(BaseModel):
    """Response object of AccessRules updation"""
    message:str = Field(..., example="Access rule updated successfully")
    data:AccessRulesOut = None

class AppDetails(BaseModel):
    """Resposne for App db row"""
    appId:int
    appName:str
    defaultRole:RoleOut = Field(alias="role",default=None)
    useForRegistration:bool
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "appId": 100057,
                "appName": 'vachan',
                "role": {},
                "useForRegistration":True
            }
        }

class Methods(str, Enum):
    """Allowed Methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

class PermissionMapCreateInput(BaseModel):
    """auth Permission Map create input"""
    apiEndpoint:str #change with regex later
    method:Methods
    requestApp:str
    resourceType:str
    permission:str
    filterResults:bool=False
    class Config:
        '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "apiEndpoint":'v2/access/permission-map',
                "method": "GET",
                "requestApp":"vachan",
                "resourceType":"app",
                "permission":"create",
                "filterResults":False
            }}

class PermissionMapOut(BaseModel):
    """auth permission map output object"""
    permissionMapId:int
    apiEndpoint:str
    method:Methods
    requestApp:AppDetails = None
    resourceType:ResourceOut = None
    permission:PermissionOut = None
    filterResults:bool
    active:bool
    class Config:
        ''' telling Pydantic exactly that "it's OK if I pass a non-dict value,
        just get the data from object attributes'''
        orm_mode = True
        # '''display example value in API documentation'''
        schema_extra = {
            "example": {
                "permissionMapId": 100057,
                "apiEndpoint":'v2/access/permission-map',
                "method": "GET",
                "requestApp":{},
                "resourceType": {},
                "permission": {},
                "filterResults":False,
                "active":True
            }
        }


class PermissionMapsResponse(BaseModel):
    """Response object of Permission map creation"""
    message:str = Field(..., example="Permission map created successfully")
    data: PermissionMapOut