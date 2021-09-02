"""schema for auth related"""
from pydantic import BaseModel

class AuthDetails(BaseModel):
    """schema for authentication input"""
    username:str
    password:str

class Registration(BaseModel):
    """kratos registration input"""
    email:str
    password:str
    firstname:str
    lastname:str
    appname:str

class userrole(BaseModel):
    """kratos user role input"""
    userid:str
    roles:list

class user_identity(BaseModel):
    """kratos user role input"""
    userid:str

class registration_out(BaseModel):
    """registration output"""
    id:str
    email:str
    Permisions:list

class register_response(BaseModel):
    """Response object of registration"""
    details:str
    registered_details:registration_out
    token:str = None

class login_response(BaseModel):
    """Response object of login"""
    details:str
    token:str

class logout_response(BaseModel):
    """Response object of logout"""
    message:str

class commmon_error(BaseModel):
    """login error"""
    error:str
    details:str

class userrole_response(BaseModel):
    """user role update response"""
    details:str
    role_list:list

class identity_delete_response(BaseModel):
    """user identity delete response"""
    success:str
        