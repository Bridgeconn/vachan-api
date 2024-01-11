# '''Test cases for deleted items related APIs
# * Dangling tables generated in testcase are in use.
# * It prevents table deletion and the query could get stuck waiting for a response from the database.
# * Hence test cases are commented'''
# # from . import client
# # from . import assert_not_available_content
# # from .test_languages import test_delete_default_superadmin as delete_language
# # from .test_commentaries import test_delete_default_superadmin as delete_commentary
# # from .test_bibles import test_delete_default_superadmin as delete_bible
# # from .test_auth_basic import SUPER_PASSWORD,SUPER_USER, login, logout_user
# # from .conftest import initial_test_users

# # UNIT_URL = '/v2/admin/cleanup'
# # LANG_URL = '/v2/resources/languages'
# # headers = {"contentType": "application/json", "accept": "application/json"}
# # headers_auth = {"contentType": "application/json",
# #                 "accept": "application/json"}

# # def assert_positive_get(item):
# #     '''Check for the properties in the normal return object'''
# #     assert "itemId" in item
# #     assert "deletedFrom" in item

# # def test_delete_deleted_items_language():
# #     ''' positive test case, checking for correct return of deleted item from deleted_items table'''
# #     #Only Super Admin can delete from deleted_items table
# #     #creating and deleting language and adding it into deleted_items table
# #     response = delete_language()
# #     deleteditem_id = response.json()['data']['itemId']

# #     #Login as Super Admin
# #     as_data = {
# #             "user_email": SUPER_USER,
# #             "password": SUPER_PASSWORD
# #         }
# #     response = login(as_data)
# #     assert response.json()['message'] == "Login Succesfull"
# #     test_user_token = response.json()["token"]
# #     headers_sa= {"contentType": "application/json",
# #                     "accept": "application/json",
# #                     'Authorization': "Bearer"+" "+test_user_token
# #             }

# #     get_response =   client.get(UNIT_URL + "?item_id="+str(deleteditem_id), headers=headers_sa)
# #     assert get_response.status_code == 200
# #     assert len(get_response.json()) == 1
# #     for item in get_response.json():
# #         assert_positive_get(item)

# #     #Delete without authentication
# #     headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
# #     response = client.delete(UNIT_URL, headers=headers)
# #     assert response.status_code == 401
# #     assert response.json()['error'] == 'Authentication Error'

# #     #Clearing deleted items with other API user,AgAdmin,AgUser,VachanUser,BcsDev and VachanAdmin
# #     for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev','VachanAdmin']:
# #         headers_au = {"contentType": "application/json",
# #                     "accept": "application/json",
# #                     'Authorization': "Bearer"+" "+initial_test_users[user]['token']
# #         }
# #         response = client.delete(UNIT_URL, headers=headers_au)
# #         assert response.status_code == 403
# #         assert response.json()['error'] == 'Permission Denied'

# #     #Clearing deleted items with Super Admin
# #     response = client.delete(UNIT_URL, headers=headers_sa)
# #     assert response.status_code == 200
# #     assert response.json()['message'] == "Database cleanup done!!"

# #     #Check item is deleted from table
# #     get_response =   client.get(UNIT_URL + "?item_id="+str(deleteditem_id), headers=headers_sa)
# #     assert get_response.status_code == 200
# #     assert_not_available_content(get_response)
# #     logout_user(test_user_token)

# # def test_delete_deleted_items_commentary():
# #     ''' positive test case, checking for correct return of deleted item from deleted_items table'''
# #     #Only Super Admin can delete from deleted_items table
# #     #creating and deleting commentaries and adding it into deleted_items table
# #     response = delete_commentary()[0]
# #     deleteditem_id = response.json()['data']['itemId']
# #     #Login as Super Admin
# #     as_data = {
# #             "user_email": SUPER_USER,
# #             "password": SUPER_PASSWORD
# #         }
# #     response = login(as_data)
# #     assert response.json()['message'] == "Login Succesfull"
# #     test_user_token = response.json()["token"]
# #     headers_sa= {"contentType": "application/json",
# #                     "accept": "application/json",
# #                     'Authorization': "Bearer"+" "+test_user_token
# #             }
# #     get_response =   client.get(UNIT_URL + "?item_id="+str(deleteditem_id), headers=headers_sa)
# #     assert get_response.status_code == 200
# #     assert len(get_response.json()) == 1
# #     for item in get_response.json():
# #         assert_positive_get(item)

# #      #Delete without authentication
# #     headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
# #     response = client.delete(UNIT_URL, headers=headers)
# #     assert response.status_code == 401
# #     assert response.json()['error'] == 'Authentication Error'

# #     #Clearing deleted items with other API user,AgAdmin,AgUser,VachanUser,BcsDev and VachanAdmin
# #     for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev','VachanAdmin']:
# #         headers_au = {"contentType": "application/json",
# #                     "accept": "application/json",
# #                     'Authorization': "Bearer"+" "+initial_test_users[user]['token']
# #         }
# #         response = client.delete(UNIT_URL, headers=headers_au)
# #         assert response.status_code == 403
# #         assert response.json()['error'] == 'Permission Denied'

# #     #Clearing deleted items with Super Admin
# #     response = client.delete(UNIT_URL, headers=headers_sa)
# #     assert response.status_code == 200
# #     assert response.json()['message'] == "Database cleanup done!!"

# #     #Check item is deleted from table
# #     get_response =   client.get(UNIT_URL + "?item_id="+str(deleteditem_id), headers=headers_sa)
# #     assert get_response.status_code == 200
# #     assert_not_available_content(get_response)
# #     logout_user(test_user_token)

# # def test_delete_deleted_items_bible():
# #     ''' positive test case, checking for correct return of deleted item from deleted_items table'''
# #     #Only Super Admin can delete from deleted_items table
# #     #creating and deleting bibles and adding it into deleted_items table
# #     response = delete_bible()[0]
# #     deleteditem_id = response.json()['data']['itemId']

# #     #Login as Super Admin
# #     as_data = {
# #             "user_email": SUPER_USER,
# #             "password": SUPER_PASSWORD
# #         }
# #     response = login(as_data)
# #     assert response.json()['message'] == "Login Succesfull"
# #     test_user_token = response.json()["token"]
# #     headers_sa= {"contentType": "application/json",
# #                     "accept": "application/json",
# #                     'Authorization': "Bearer"+" "+test_user_token
# #             }
# #     get_response =   client.get(UNIT_URL + "?item_id="+str(deleteditem_id), headers=headers_sa)
# #     assert get_response.status_code == 200
# #     assert len(get_response.json()) == 1
# #     for item in get_response.json():
# #         assert_positive_get(item)

# #     #Delete without authentication
# #     headers = {"contentType": "application/json", "accept": "application/json"}#pylint: disable=redefined-outer-name
# #     response = client.delete(UNIT_URL, headers=headers)
# #     assert response.status_code == 401
# #     assert response.json()['error'] == 'Authentication Error'

# #     #Clearing deleted items with other API user,AgAdmin,AgUser,VachanUser,BcsDev and VachanAdmin
# #     for user in ['APIUser','AgAdmin','AgUser','VachanUser','BcsDev','VachanAdmin']:
# #         headers_au = {"contentType": "application/json",
# #                     "accept": "application/json",
# #                     'Authorization': "Bearer"+" "+initial_test_users[user]['token']
# #         }
# #         response = client.delete(UNIT_URL, headers=headers_au)
# #         assert response.status_code == 403
# #         assert response.json()['error'] == 'Permission Denied'

# #     #Clearing deleted items with Super Admin
# #     response = client.delete(UNIT_URL, headers=headers_sa)
# #     assert response.status_code == 200
# #     assert response.json()['message'] == "Database cleanup done!!"

# #     #Check item is deleted from table
# #     get_response =   client.get(UNIT_URL + "?item_id="+str(deleteditem_id), headers=headers_sa)
# #     assert get_response.status_code == 200
# #     assert_not_available_content(get_response)
# #     logout_user(test_user_token)
