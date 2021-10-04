'''Common stuff required by main and different routers'''

import os
import logging
from logging.handlers import RotatingFileHandler
from database import SessionLocal

# Define and configure logger so that all other modules can use it
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("VACHAN_LOGGING_LEVEL", "WARNING"))
handler = RotatingFileHandler('../logs/API_logs.log', maxBytes=10000000, backupCount=10)
fmt = logging.Formatter(fmt='%(asctime)s|%(filename)s:%(lineno)d|%(levelname)-8s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
log.addHandler(handler)

def get_db():
    '''To start a DB connection(session)'''
    db_ = SessionLocal()
    try:
        yield db_
    finally:
        # pass
        db_.close()

#test case for getting request context
# def get_request_context(request):
#     """get the context of requests"""
#     print("===>ger_request func",request)
#     request_context = {}
#     request_context['method'] = request.method
#     request_context['endpoint'] = request.url.path
#     if 'app' in request.headers:
#         request_context['app'] = request.headers['app']
#     else:
#         request_context['app'] = None

#     return request_context

# def verify_auth_decorator_params(kwargs):
#     """check passed params to auth from router"""
#     required_params = {
#             "request_context":"",
#             "db_":"",
#             "resource_id":"",
#             "user_id":"",
#             "user_roles":"",
#             "resource_type":""
#         }
#     print("=============>inside check none",kwargs)
#     for param in required_params():
#         if param in kwargs.keys():
#             required_params[param] = kwargs[param]
#         else:
#             required_params[param] = None
#     if 'request' in kwargs.keys():
#         request_context = {}
#         request = kwargs['request']
#         request_context['method'] = request.method
#         request_context['endpoint'] = request.url.path
#         if 'app' in request.headers:
#             request_context['app'] = request.headers['app']
#         else:
#             request_context['app'] = None
#         required_params['request_context'] = request_context
#     return required_params

# #decorator for authentication and access check
# def get_auth_access_check_decorator(func):
#     @wraps(func)
#     async def wrapper(*args, **kwargs):
#         #Before Router function execute
        
#         required_params = verify_auth_decorator_params(kwargs)

#         verified = check_access_rights(required_params['db_'], required_params)
#         if not verified:
#             raise PermisionException("Access Permission Denied for the URL")  

#         #calling router functions
#         response = await func(*args, **kwargs)

#         #After router function execution
#         print("===>After inner fucntion, inside decorator")

#         #returning final response from router function
#         return response
#     return wrapper