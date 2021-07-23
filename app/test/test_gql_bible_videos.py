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
from . import gql_request,assert_not_available_content_gql,check_skip_gql,check_limit_gql

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

def check_post(query, variables):
    '''prior steps and post attempt, without checking the response'''
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    src_executed = source_add(source_query,SOURCE_VAR)
    source_name = src_executed["data"]["addSource"]["data"]["sourceName"]
    executed = gql_request(query=query,operation="mutation", variables=variables)
    return executed,source_name

def post_biblevideo(variable):
    '''post data and check successfull or not'''
    executed , source_name = check_post(ADD_BIBLEVIDEO,variable)
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
        {
  bibleVideos(sourceName:"mr_TTT_1_biblevideo",arg_text){
    title
  }
}
    """
    check_skip_gql(check_query,"bibleVideos")
    check_limit_gql(check_query,"bibleVideos")

    #duplicate 
    executed = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable)
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

    executed1 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable1)
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
    executed2 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable2)
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
    executed3 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable3)
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
    executed4 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable4)
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
    executed5 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable5)
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
    executed6 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable6)
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
    executed7 = gql_request(ADD_BIBLEVIDEO,operation="mutation",variables=variable7)
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
    executed1 = gql_request(query1)
    assert len(executed1["data"]["bibleVideos"]) == 1

    query2 = query.replace("arg_text",'bookCode:"mat"')
    executed2 = gql_request(query2)
    assert len(executed2["data"]["bibleVideos"]) == 2

    # filter with title overview
    query3 = query.replace("arg_text",'title:"Overview: Matthew"')
    executed3 = gql_request(query3)
    assert len(executed3["data"]["bibleVideos"]) == 1

    # filter with theme
    query4 = query.replace("arg_text",'theme:"Old testament"')
    executed4 = gql_request(query4)
    assert len(executed4["data"]["bibleVideos"]) == 2

    query5 = query.replace("arg_text",'theme:"New testament"')
    executed5 = gql_request(query5)
    assert len(executed5["data"]["bibleVideos"]) == 3

    # not available
    query6 = query.replace("arg_text",'bookCode:"rev"')
    executed6 = gql_request(query6)
    assert_not_available_content_gql(executed6["data"]["bibleVideos"])

    query7 = query.replace("arg_text",'bookCode:"mat",theme:"Old testament"')
    executed7 = gql_request(query7)
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
    executed = gql_request(query)
    assert "errors" in executed.keys()

    query0 = """
        {
  bibleVideos(sourceName:"mr_TTT_1_biblevideo",arg_text){
    title
  }
}
    """
    query1 = query0.replace("arg_text","bookCode:60")
    executed1 = gql_request(query1)
    assert "errors" in executed1.keys()

    query2 = query0.replace("arg_text","bookCode:luke")
    executed2 = gql_request(query2)
    assert "errors" in executed2.keys()

    query3 = query0.replace("arg_text","title:1")
    executed3 = gql_request(query3)
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

    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=new_var)
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
    executed2 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable2)
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
    executed = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable)
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
    executed2 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable2)
    assert "errors" in executed2.keys()

    variable3 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Acts of Apostles', 'books': 'acts'}
    ]
    }
} 
    executed3 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable3)
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
    executed4 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable4)
    assert "errors" in executed4.keys()

    variable5 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Acts of Apostles', 'books': [1,2,3]}
    ]
    }
} 
    executed5 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable5)
    assert "errors" in executed5.keys()

    variable6 = {
  "object": {
    "sourceName": "mr_TTT_1_biblevideo",
    "videoData": [
        {'title':'Overview: Acts of Apostles', "videoLink":"Not a link"}
    ]
    }
} 
    executed6 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable6)
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
    executed7 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable7)
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

    executed = gql_request(GET_BIBLEVIDEO)
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
    executed2 = gql_request(EDIT_BIBLEVIDEO,operation="mutation",variables=variable2)
    executed3 = gql_request(GET_BIBLEVIDEO)
    assert len(executed3["data"]["bibleVideos"]) == 2
