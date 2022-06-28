'''Customize predefined errors and define new ones'''

class GenericException(Exception):
    '''Format for Database error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Error"
        self.detail = detail
        self.status_code = 500

class DatabaseException(Exception):
    '''Format for Database error'''
    def __init__(self, detail):
        super().__init__()
        self.name = "Database Error"
        self.logging_info = detail.__dict__
        if 'orig' in detail.__dict__:
            self.detail = str(detail.__dict__['orig']).replace('DETAIL:','')
        else:
            self.detail = str(detail)
        self.status_code = 502

class GitlabException(Exception):
    '''Format for Gitlab error in media access APIs'''
    def __init__(self, detail):
        super().__init__()
        self.name = "Gitlab Access Error"
        self.detail = detail
        self.status_code = 502

class NotAvailableException(Exception):
    '''Format for not available Exception'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Requested Content Not Available"
        self.detail = detail
        self.status_code = 404

class AlreadyExistsException(Exception):
    '''Format for already exists error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Already Exists"
        self.detail = detail
        self.status_code = 409

class TypeException(Exception):
    '''Format for type error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Not the Required Type"
        self.detail = detail
        self.status_code = 415

class PermissionException(Exception):
    '''Format for permission error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Permission Denied"
        self.detail = detail
        self.status_code = 403

class UnAuthorizedException(Exception):
    """Format for un authorized error"""
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Authentication Error"
        self.detail = detail
        self.status_code = 401

class UnprocessableException(Exception):
    """Format for Unprocessable error"""
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Unprocessable Data"
        self.detail = detail
        self.status_code = 422
