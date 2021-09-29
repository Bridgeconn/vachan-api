'''returns the required permission name as per the access rules'''
#pylint: disable=E0401
import schema_auth

#pylint: disable=too-many-locals,too-many-statements
def api_permission_map(endpoint, method, requesting_app, resource):
    '''returns the required permission name as per the access rules'''

    message = "API's required permission not defined"

    #Methods related to swither
    def switch_register():
        """register endpoint"""
        permission = None
        if method == 'POST':
            permission = "create"
        return permission

    def switch_login():
        """register endpoint"""
        permission = None
        if method == 'GET':
            permission = "login"
        return permission

    def switch_logout():
        """register endpoint"""
        permission = None
        if method == 'GET':
            permission = "logout"
        return permission

    def switch_userrole():
        """register endpoint"""
        permission = None
        if method == 'PUT':
            permission = "edit-role"
        return permission

    def switch_delete_identity():
        """register endpoint"""
        permission = None
        if method == 'DELETE':
            permission = "detele/deactivate"
        return permission

    def switch_contents():
        """content types endpoint"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.ag:
                permission = "refer-for-translation"
            elif requesting_app == schema_auth.App.vachan:
                permission = "view-on-web"
            elif requesting_app == schema_auth.App.vachan:
                permission = "read-via-vachanadmin"
            elif requesting_app is None:
                permission = "read-via-api"
        elif method == 'POST':
            permission = "create"
        elif method == 'PUT':
            permission = "edit"
        return permission

    def switch_agmt_project():
        """Agmt projects endpoint"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.ag:
                permission = "refer-for-translation"
            elif requesting_app == schema_auth.App.vachan:
                permission = "view-on-web"
            elif requesting_app == schema_auth.App.vachan:
                permission = "view-on-vachan-admin"
            elif requesting_app is None:
                permission = "read-via-api"
        if method == 'POST':
            permission = "create"
        if method == 'PUT':
            if resource==schema_auth.ResourceType.content:
                permission = "translate"
            elif resource==schema_auth.ResourceType.project:
                permission = "edit-Settings"
        return permission

    def switch_agmt_project_tokens():
        """Agmt projects endpoint"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.ag:
                permission = "refer-for-translation"
            elif requesting_app == schema_auth.App.vachan:
                permission = "view-on-web"
            elif requesting_app == schema_auth.App.vachan:
                permission = "view-on-vachan-admin"
            elif requesting_app is None:
                permission = "read-via-api"
        if method == 'PUT':
            permission = "edit-draft"
        if method == 'POST':
            permission = "create"
        return permission

    switcher = {
        "/v2/user/register" : switch_register,
        "/v2/user/login" : switch_login,
        "/v2/user/logout" : switch_logout,
        "/v2/user/userrole" : switch_userrole,
        "/v2/user/delete-identity" : switch_delete_identity,

        "/v2/contents" : switch_contents,

        "/v2/languages" : switch_contents,

        "/v2/licenses" : switch_contents,

        "/v2/versions" : switch_contents,

        "/v2/lookup/bible/books" : switch_contents,

        "/v2/bibles" : switch_contents,

        "/v2/commentaries" : switch_contents,

        "/v2/dictionaries" : switch_contents,

        "/v2/infographics" : switch_contents,

        "/v2/biblevideos" : switch_contents,

        "/v2/autographa/projects" : switch_agmt_project,

        "/v2/autographa/project/user" : switch_agmt_project,

        "/v2/autographa/project/tokens" : switch_agmt_project_tokens,
        "/v2/autographa/project/token-translations" : switch_agmt_project_tokens,

        "/v2/autographa/project/token-sentences" : switch_agmt_project_tokens,

        "/v2/autographa/project/draft" : switch_agmt_project,

        "/v2/autographa/project/sentences" : switch_agmt_project,

        "/v2/autographa/project/progress" : switch_agmt_project,

        "/v2/autographa/project/versification" : switch_agmt_project,

        "/v2/autographa/project/suggesions" : switch_agmt_project_tokens,
        "/v2/translation/suggesions" : switch_agmt_project_tokens,
        "/v2/translation/gloss" : switch_agmt_project_tokens,
        "/v2/translation/learn/gloss" : switch_agmt_project_tokens,
        "/v2/translation/learn/alignment" : switch_agmt_project_tokens,

        "/v2/translation/tokens" : switch_agmt_project_tokens,
        "/v2/translation/token-translate" : switch_agmt_project_tokens,
        "/v2/translation/draft" : switch_agmt_project_tokens,

    }
    switch_func =  switcher.get(endpoint, message)
    if isinstance(switch_func,str):
        raise Exception(message)

    permission = switch_func()

    return permission
