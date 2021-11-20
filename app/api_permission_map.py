'''returns the required permission name as per the access rules'''
#pylint: disable=E0401
import schema_auth

#pylint: disable=too-many-locals,too-many-statements
def api_permission_map(endpoint, request_context, requesting_app, resource, user_details):
    '''returns the required permission name as per the access rules'''

    message = "API's required permission not defined"
    method = request_context['method']
    # check sourcename is present or not
    if not request_context['path_params'] == {} and\
        'source_name' in request_context['path_params'].keys():
        source_name = request_context['path_params']['source_name']
    else:
        source_name = None

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
        if not 'error' in user_details.keys():
            if method == 'PUT':
                permission = "edit-role"
        else:
            raise user_details['error']
        return permission

    def switch_delete_identity():
        """register endpoint"""
        permission = None
        if not 'error' in user_details.keys():
            if method == 'DELETE':
                permission = "detele/deactivate"
        else:
            raise user_details['error']
        return permission

    def switch_contents():
        """content types endpoint"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.AG:
                permission = "refer-for-translation"
            elif requesting_app == schema_auth.App.VACHAN:
                permission = "view-on-web"
            elif requesting_app == schema_auth.App.VACHANADMIN:
                permission = "read-via-vachanadmin"
            elif requesting_app is None or \
                requesting_app == schema_auth.App.API:
                permission = "read-via-api"
        elif method == 'POST':
            if not 'error' in user_details.keys():
                permission = "create"
            else:
                raise user_details['error']
        elif method == 'PUT':
            if not 'error' in user_details.keys():
                permission = "edit"
            else:
                raise user_details['error']
        return permission

    def switch_agmt_project():#pylint: disable=too-many-branches
        """Agmt projects endpoint"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.AG:
                permission = "view-project"
            elif requesting_app == schema_auth.App.VACHAN:
                permission = "view-on-web"
            elif requesting_app == schema_auth.App.VACHANADMIN:
                permission = "view-on-vachan-admin"
            elif requesting_app is None:
                permission = "read-via-api"
        if method == 'POST':
            if requesting_app == schema_auth.App.AG:
                if not 'error' in user_details.keys():
                    permission = "create"
                else:
                    raise user_details['error']
        if method == 'PUT':
            if requesting_app == schema_auth.App.AG:
                if not 'error' in user_details.keys():
                    if resource==schema_auth.ResourceType.CONTENT:
                        permission = "translate"
                    elif resource==schema_auth.ResourceType.PROJECT:
                        permission = "edit-Settings"
                else:
                    raise user_details['error']
        return permission

    def switch_agmt_project_user():#pylint: disable=too-many-branches
        """Agmt projects user endpoint"""
        permission = None
        if method == 'POST':
            if requesting_app == schema_auth.App.AG:
                if not 'error' in user_details.keys():
                    permission = "create-user"
                else:
                    raise user_details['error']
        if method == 'PUT':
            if requesting_app == schema_auth.App.AG:
                if not 'error' in user_details.keys():
                    permission = "edit-Settings"
                else:
                    raise user_details['error']
        return permission

    def switch_agmt_project_tokens():
        """Agmt projects endpoint"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.AG:
                permission = "read-draft"
            # elif requesting_app == schema_auth.App.VACHAN:
            #     permission = "view-on-web"
            # elif requesting_app == schema_auth.App.VACHANADMIN:
            #     permission = "view-on-vachan-admin"
            # elif requesting_app is None:
            #     permission = "read-via-api"
        if method == 'PUT':
            if not 'error' in user_details.keys():
                permission = "edit-draft"
            else:
                raise user_details['error']
        # if method == 'POST':
        #     if not 'error' in user_details.keys():
        #         permission = "create"
        #     else:
        #         raise user_details['error']
        return permission

    def switch_agmt_project_draft():
        """agmt project draft"""
        permission = None
        if method == 'GET':
            if requesting_app == schema_auth.App.AG:
                permission = "read-draft"
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

        "/v2/sources" : switch_contents,

        "/v2/sources/get-sentence" : switch_contents,

        "/v2/lookup/bible/books" : switch_contents,

        f"/v2/bibles/{source_name}/books" : switch_contents,

        f"/v2/bibles/{source_name}/versification" : switch_contents,

        f"/v2/bibles/{source_name}/verses" : switch_contents,

        f"/v2/bibles/{source_name}/audios" : switch_contents,

        f"/v2/commentaries/{source_name}" : switch_contents,

        f"/v2/dictionaries/{source_name}" : switch_contents,

        f"/v2/infographics/{source_name}" : switch_contents,

        f"/v2/biblevideos/{source_name}" : switch_contents,

        "/v2/autographa/projects" : switch_agmt_project,

        "/v2/autographa/project/user" : switch_agmt_project_user,

        "/v2/autographa/project/tokens" : switch_agmt_project_tokens,

        "/v2/autographa/project/token-translations" : switch_agmt_project_tokens,

        "/v2/autographa/project/token-sentences" : switch_agmt_project_tokens,

        "/v2/autographa/project/draft" : switch_agmt_project_draft,

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
