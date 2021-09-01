from pydantic import BaseModel

class AuthDetails(BaseModel):
    """schema for authentication"""
    username:str
    password:str

class Registration(BaseModel):
    """kratos registration"""
    email:str
    password:str
    firstname:str
    lastname:str
    appname:str

class userrole(BaseModel):
    """kratos user role"""
    userid:str
    roles:list
