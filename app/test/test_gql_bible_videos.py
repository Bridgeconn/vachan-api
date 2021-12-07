"""Test cases for Bible Videos in GQL"""
from typing import Dict
#pylint: disable=E0401
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
from .test_bible_videos import assert_positive_get
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import gql_request,assert_not_available_content_gql,check_skip_limit_gql,\
  contetapi_get_accessrule_checks_app_userroles_gql
from .conftest import initial_test_users
from . test_gql_auth_basic import login,SUPER_PASSWORD,SUPER_USER

headers_auth = {"contentType": "application/json",
                "accept": "application/json"}
headers = {"contentType": "application/json", "accept": "application/json"}

VERSION_VAR  = {
        "object": {
        "versionAbbreviation": "TTT",
        "versionName": "test version for bibles"
    }
    }
SOURCE_VAR = {
  "object": {
    "contentType": "biblevideo",
    "language": "mr",
    "version": "TTT",
    "revision": "1",
    "year": 2020,
  }
}

ADD_BIBLEVIDEO = """
    mutation addbiblevideo($object:InputAddBibleVideo){
  addBibleVideo(videoArg:$object){
    message
    data{
      title
      books
      videoLink
      description
      theme
      active
    }
  }
}
"""
EDIT_BIBLEVIDEO = """
    mutation editbiblevideo($object:InputEditBibleVideo){
  editBibleVideo(videoArg:$object){
    message
    data{
      title
      books
      videoLink
      description
      theme
      active
    }
  }
}
"""

GET_BIBLEVIDEO = """
    {
  bibleVideos(sourceName:"mr_TTT_1_biblevideo"){
    title
    books
    videoLink
    description
    theme
    active
  }
}
"""
headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
def check_post(query, variables):
    '''prior steps and post attempt, without checking the response'''
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    src_executed = source_add(source_query,SOURCE_VAR)
    source_name = src_executed["data"]["addSource"]["data"]["sourceName"]
    #without auth
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert "errors" in executed
    #with auth
    executed = gql_request(query=query,operation="mutation", variables=variables,
      headers=headers_auth)
    return executed,source_name

def post_biblevideo(variable):
    '''post data and check successfull or not'''
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    executed , source_name = check_post(ADD_BIBLEVIDEO,variable)
    assert not "errors" in executed
    assert executed["data"]["addBibleVideo"]["message"] == "Bible videos added successfully"
    assert len(variable["object"]["videoData"]) ==\
       len(executed["data"]["addBibleVideo"]["data"])
    for item in executed["data"]["addBibleVideo"]["data"]:
        assert_positive_get(item)
    return executed,source_name


def test_post_default():
    '''Positive test to upload commentries, with various kins of ref ranges supported'''
    variable = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}
    post_biblevideo(variable)
    
    check_query = """
        query bibleVideos($skip:Int, $limit:Int){
      bibleVideos(sourceName:"mr_TTT_1_biblevideo",skip:$skip,limit:$limit){
        title
  }
}
    """
    check_skip_limit_gql(check_query,"bibleVideos",headers=headers_auth)

    #duplicate 
    executed = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable,
      headers=headers_auth)
    assert "errors" in executed.keys()

def test_post_incorrect_data():
    ''' tests to check input validation in post API'''

    # single data object instead of list
    variable1 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
        {'title':'Overview: Genesis', 'theme': 'Old testament',
        'description':"brief description",
        'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
  }
}

    executed1 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable1,
      headers=headers_auth)
    assert "errors" in executed1.keys()
    
    # data object with missing mandatory fields
    variable2 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
         [
        {'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}
    executed2 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2.keys()

    variable3 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
         [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}
    executed3 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable3,
      headers=headers_auth)
    assert "errors" in executed3.keys()

    variable4 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
         [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen']}
    ]
  }
}
    executed4 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable4,
      headers=headers_auth)
    assert "errors" in executed4.keys()
    
    # incorrect data values in fields 
    variable5 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
         [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': 'gen', 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}
    executed5 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable5,
      headers=headers_auth)
    assert "errors" in executed5.keys()

    variable6 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
        [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'vid'}
    ]
  }
}
    executed6 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable6,
      headers=headers_auth)
    assert "errors" in executed6.keys()

    variable7 = {
  "object": {
    "sourceName": "mq_TTF_1_biblevideo",
    "videoData": 
        [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}
    executed7 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable7,
      headers=headers_auth)
    assert "errors" in executed7.keys()
    
def test_get_after_data_upload():
    '''Add some infographics data into the table and do all get tests'''
    variable = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Gospels', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}
    post_biblevideo(variable)

    #filter by book
    query = """
        {
  bibleVideos(sourceName:"mr_TTT_1_biblevideo",arg_text){
    title
  }
}
    """
    query1 = query.replace("arg_text",'bookCode:"gen"')
    #without Auth
    executed1 = gql_request(query1)
    assert "errors" in executed1
    #with Auth
    executed1 = gql_request(query1,headers=headers_auth)
    assert len(executed1["data"]["bibleVideos"]) == 1

    query2 = query.replace("arg_text",'bookCode:"mat"')
    executed2 = gql_request(query2,headers=headers_auth)
    assert len(executed2["data"]["bibleVideos"]) == 2

    # filter with title overview
    query3 = query.replace("arg_text",'title:"Overview: Matthew"')
    executed3 = gql_request(query3,headers=headers_auth)
    assert len(executed3["data"]["bibleVideos"]) == 1

    # filter with theme
    query4 = query.replace("arg_text",'theme:"Old testament"')
    executed4 = gql_request(query4,headers=headers_auth)
    assert len(executed4["data"]["bibleVideos"]) == 2

    query5 = query.replace("arg_text",'theme:"New testament"')
    executed5 = gql_request(query5,headers=headers_auth)
    assert len(executed5["data"]["bibleVideos"]) == 3

    # not available
    query6 = query.replace("arg_text",'bookCode:"rev"')
    executed6 = gql_request(query6,headers=headers_auth)
    assert_not_available_content_gql(executed6["data"]["bibleVideos"])

    query7 = query.replace("arg_text",'bookCode:"mat",theme:"Old testament"')
    executed7 = gql_request(query7,headers=headers_auth)
    assert_not_available_content_gql(executed7["data"]["bibleVideos"])

def test_get_incorrect_data():
    '''Check for input validations in get'''    
    query = """
        {
  bibleVideos(sourceName:"mr_TTT"){
    title
  }
}
    """
    executed = gql_request(query,headers=headers_auth)
    assert "errors" in executed.keys()

    query0 = """
        {
  bibleVideos(sourceName:"mr_TTT_1_biblevideo",arg_text){
    title
  }
}
    """
    query1 = query0.replace("arg_text","bookCode:60")
    executed1 = gql_request(query1,headers=headers_auth)
    assert "errors" in executed1.keys()

    query2 = query0.replace("arg_text","bookCode:luke")
    executed2 = gql_request(query2,headers=headers_auth)
    assert "errors" in executed2.keys()

    query3 = query0.replace("arg_text","title:1")
    executed3 = gql_request(query3,headers=headers_auth)
    assert "errors" in executed3.keys()

def test_put_after_upload():
    '''Positive tests for put'''
    variable = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}

    post_biblevideo(variable)

    new_var = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Matthew', 'active': False},
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament history'},
        {'title':'Overview: Exodus', 'videoLink': 'https://www.youtube.com/biblevideos/newvid'}
    ]
  }
}
    #Without Auth
    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=new_var)
    assert "errors" in executed
    #With Auth
    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=new_var,
      headers=headers_auth)
    assert executed["data"]["editBibleVideo"]["message"] == "Bible videos updated successfully"
    assert len(executed["data"]["editBibleVideo"]["data"]) > 0
    for item in executed["data"]["editBibleVideo"]["data"]:
        assert_positive_get(item)
        if item['title'] == 'Overview: Exodus':
            assert item['videoLink'].endswith('newvid')
        if item['title'] == 'Overview: Matthew':
            assert not item['active']
        if item['title'] == 'Overview: Acts of Apostles':
            assert item['theme'] == 'New testament history'

    # not available PUT
    variable2 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Acts', 'theme': 'New testament history'}
    ]
  }
}
    executed2 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2.keys()
        
def test_put_incorrect_data():
    ''' tests to check input validation in put API'''
    variable = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'active':True},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'active':True},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid', 'active':True}
    ]
  }
}

    post_biblevideo(variable)

    # single data object instead of list
    variable = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": 
        {'title':'Overview: Genesis', 'theme': 'Old testament',
        'description':"brief description",
        'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
  }
} 
    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable,
      headers=headers_auth)
    assert "errors" in executed.keys()

    # data object with missing mandatory fields
    variable2 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'theme': 'New testament',
        "videoLink":"http://anotherplace.com/something"}
    ]
  }
} 
    executed2 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2.keys()

    variable3 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Acts of Apostles', 'books': 'acts'}
    ]
    }
} 
    executed3 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable3,
      headers=headers_auth)
    assert "errors" in executed3.keys()

    # incorrect data values in fields
    variable4 =  {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':123, 'active':'not'}
    ]
    }
} 
    executed4 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable4,
      headers=headers_auth)
    assert "errors" in executed4.keys()

    variable5 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Acts of Apostles', 'books': [1,2,3]}
    ]
    }
} 
    executed5 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable5,
      headers=headers_auth)
    assert "errors" in executed5.keys()

    variable6 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Acts of Apostles', "videoLink":"Not a link"}
    ]
    }
} 
    executed6 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable6,
      headers=headers_auth)
    assert "errors" in executed6.keys()

    #wrong source
    variable7 =  {
  "object": {
    "sourceName": "mr_RFG_1_bib",
    "videoData": [
        {'title':'Overview: Genesis', 'theme': 'Old testament',
        'description':"brief description",
        'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
    }
} 
    executed7 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable7,
      headers=headers_auth)
    assert "errors" in executed7.keys()

def test_soft_delete():
    '''check soft delete in infographics'''
    variable = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Words of Jesus', 'theme': 'New testament',
            'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'active':True},
        {'title':'Miracles of Jesus', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'active':True},
        {'title':'Miracles the Israelites saw', 'theme': 'Old testament',
            'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid', 'active':True}
    ]
  }
}

    post_biblevideo(variable)

    executed = gql_request(GET_BIBLEVIDEO,headers=headers_auth)
    assert len(executed["data"]["bibleVideos"]) == 3

    variable2 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Words of Jesus', 'theme': 'New testament',
            'description':"brief description",
            'books': ['mat', 'mrk', 'luk', 'jhn'],
            'videoLink': 'https://www.youtube.com/biblevideos/vid',
            'active':False}
    ]
  }
}
    executed2 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable2,
      headers=headers_auth)
    executed3 = gql_request(GET_BIBLEVIDEO,headers=headers_auth)
    assert len(executed3["data"]["bibleVideos"]) == 2

def test_created_user_can_only_edit():
    """only created user and SA can only edit"""
    """source edit can do by created user and Super Admin"""
    SA_user_data = {
            "user_email": SUPER_USER,
            "password": SUPER_PASSWORD
        }
    response = login(SA_user_data)
    token =  response["data"]["login"]["token"]

    headers_SA = {"contentType": "application/json",
                    "accept": "application/json",
                    'Authorization': "Bearer"+" "+token
                }
    
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    source_data = {
  "object": {
    "contentType": "biblevideo",
    "language": "gu",
    "version": "TTT",
    "revision": "1",
    "year": 2021
  }
}
    executed = gql_request(query=source_query,operation="mutation", variables=source_data,
      headers=headers_SA)
    assert isinstance(executed, Dict)
    assert executed["data"]["addSource"]["message"] == "Source created successfully"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    #post data
    #Create With SA

    variable = {
  "object": {
    "sourceName": "gu_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament',
            'description':"brief description",
            'books': ['act'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Matthew', 'theme': 'New testament', 'description':"brief description",
            'books': ['mat'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}

    executed = gql_request(query=ADD_BIBLEVIDEO,operation="mutation", variables=variable,
      headers=headers_SA)
    assert executed["data"]["addBibleVideo"]["message"] == "Bible videos added successfully"

    new_var = {
  "object": {
    "sourceName": "gu_TTT_1_biblevideo",
    "videoData":  [
        {'title':'Overview: Matthew', 'active': False},
        {'title':'Overview: Acts of Apostles', 'theme': 'New testament history'},
        {'title':'Overview: Exodus', 'videoLink': 'https://www.youtube.com/biblevideos/newvid'}
    ]
  }
}
    #Edit with SA created User
    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=new_var,
      headers=headers_SA)
    assert executed["data"]["editBibleVideo"]["message"] == "Bible videos updated successfully"
    #edit with VA not craeted user
    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=new_var,
      headers=headers_auth)
    assert "errors" in executed

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    # #add version
    version_add(version_query,VERSION_VAR)

    content_data = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Genesis', 'theme': 'Old testament', 'description':"brief description",
            'books': ['gen'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'},
        {'title':'Overview: Exodus', 'theme': 'Old testament', 'description':"brief description",
            'books': ['exo'], 'videoLink': 'https://www.youtube.com/biblevideos/vid'}
    ]
  }
}

    get_query = """
      query get_bible_videos($source:String!){
  bibleVideos(sourceName:$source){
   title
  }
}
    """
    get_var = {
      "source": "gu_TTT_1_commentary"
    }

    content_qry = ADD_BIBLEVIDEO
    test_data = {"get_query": get_query,
          "get_var": get_var
        }

    contetapi_get_accessrule_checks_app_userroles_gql("biblevideo",content_qry, content_data , 
      test_data , bible=False)