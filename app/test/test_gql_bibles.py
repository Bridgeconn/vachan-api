"""Test cases for Bibles in GQL"""
import re
import json
from typing import Dict
#pylint: disable=E0401
#pylint: disable=C0301
from .test_bibles import assert_positive_get_for_books,assert_positive_get_for_audio,assert_positive_get_for_verse
from .test_bibles import gospel_books_data,gospel_books_merged_data,gospel_books_split_data
from .test_gql_versions import GLOBAL_QUERY as version_query
from .test_gql_sources import SOURCE_GLOBAL_QUERY as source_query
from .test_gql_versions import check_post as version_add
from .test_gql_sources import check_post as source_add
#pylint: disable=E0611
#pylint: disable=R0914
#pylint: disable=R0915
from . import check_skip_limit_gql, gql_request,assert_not_available_content_gql,\
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
    "contentType": "bible",
    "language": "gu",
    "version": "TTT",
    "revision": "1",
    "year": 3030,
  }
}

BOOK_ADD_QUERY = """
    mutation addbible($object:InputAddBible){
  addBibleBook(bibleArg:$object){
    message
    data{
      book{
        bookId
        bookName
        bookCode
      }
      USFM
      JSON
      audio{
        name
        url
        book{
          bookId
          bookName
          bookCode
        }
        format
        active
      }
      active
    }
  }
}
"""

BOOK_EDIT_QUERY = """
    mutation editbible($object:InputEditBible){
  editBibleBook(bibleArg:$object){
    message
    data{
      book{
        bookId
        bookName
        bookCode
      }
      USFM
      JSON
      audio{
        name
        url
        book{
          bookId
          bookName
          bookCode
        }
        format
        active
      }
      active
    }
  }
}
"""

AUDIO_ADD_QUERY = """
mutation addaudio($object:InputAddAudioBible){
  addAudioBible(audioBibleArg:$object){
    message
    data{
      name
      url
      book{
        bookId
        bookName
        bookCode
      }
      format
      active
    }
  }
}
"""

AUDIO_EDIT_QUERY = """
     mutation editaudio($object:InputEditAudioBible){
  editAudioBible(audioBibleArg:$object){
    message
    data{
      name
      url
      book{
        bookId
        bookName
        bookCode
      }
      format
      active
    }
    
  }
}
"""

headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
def check_post(query, variables,datatype="books"):
  '''prior steps and post attempt, without checking the response'''
  headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
  if datatype is not "audio":
    #add version
    version_add(version_query,VERSION_VAR)
    #add source
    src_executed = source_add(source_query,SOURCE_VAR)
    table_name = src_executed["data"]["addSource"]["data"]["sourceName"]
    #without auth
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert "errors" in executed
    executed = gql_request(query=query,operation="mutation", variables=variables,
      headers=headers_auth)
    assert not "errors" in executed
    return executed,table_name
  else:
    #without auth
    executed = gql_request(query=query,operation="mutation", variables=variables)
    assert "errors" in executed
    #with auth
    executed = gql_request(query=query,operation="mutation", variables=variables,
      headers=headers_auth)
    assert not "errors" in executed
    return executed

def add_bible():
  '''Positive test to upload bible books'''
  variable = {
    "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]
    }
    }
  executed,table = check_post(BOOK_ADD_QUERY,variable)
  assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"
  for i,item in enumerate(executed["data"]["addBibleBook"]['data']):
        assert_positive_get_for_books(item)
        book_code = re.match(r'\\id (\w\w\w)', gospel_books_data[i]['USFM']).group(1)
        assert item['book']['bookCode'] == book_code.lower()
  assert len(gospel_books_data) == len(executed["data"]["addBibleBook"]['data'])
  return executed,table

def add_audio():
  '''Test the API for audio bible info upload'''
  variable = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "audioData":[
  {
    "name": "matthew recording",
    "url": "https://www.somewhere.com/file_mat",
    "books": [
      "mat"
    ],
    "format": "mp3"
  },
  {
    "name": "John recording",
    "url": "https://www.somewhere.com/file_jhn",
    "books": [
      "jhn"
    ],
    "format": "string"
  },
  {
    "name": "letters of John",
    "url": "https://www.somewhere.com/file_jhn_letters",
    "books": [
      "1jn", "2jn", "3jn"
    ],
    "format": "mp3"
  },
  {
    "name": "last books",
    "url": "https://www.somewhere.com/file_rev",
    "books": [
      "rev"
    ],
    "format": "mp3"
  }
]
  }
}
  executed = check_post(AUDIO_ADD_QUERY,variable,datatype="audio")
  assert executed["data"]["addAudioBible"]["message"] == "Bible audios details uploaded successfully"
  assert len(executed["data"]["addAudioBible"]["data"]) == 6
  for item in executed["data"]["addAudioBible"]["data"]:
    assert_positive_get_for_audio(item)
  return executed  
      

def test_post_default():
  '''Positive test to upload bible books'''
  add_bible()

  #skip and limit
  query_check ="""
      query bible($skip:Int, $limit:Int){
  bibleContents(sourceName:"gu_TTT_1_bible",skip:$skip,limit:$limit){
    USFM
  }
}
  """
  check_skip_limit_gql(query_check,"bibleContents",headers=headers_auth)

def test_post_put_split_verse():
    """test posting split verse"""
    variable = {
    "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": [
        {"USFM":"\\id rev\n\\c 1\n\\p\n\\v 1a test verse one a\n\\v 1b test verse one b\n\\v 2 test verse two"}]
    }
    }
    executed,table = check_post(BOOK_ADD_QUERY,variable)
    assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(executed["data"]["addBibleBook"]['data']):
          assert_positive_get_for_books(item)
          book_code = re.match(r'\\id (\w\w\w)', gospel_books_split_data[i]['USFM']).group(1)
          assert item['book']['bookCode'] == book_code.lower()
    assert len(gospel_books_split_data) == len(executed["data"]["addBibleBook"]['data'])

    get_bile_verse = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"rev",chapter:1){
    reference{
      bible
      book
      chapter
      verseNumber
      verseNumberEnd
    }
    verseText
  }
}
  """
    #get bible data and check split verses are combined
    executed3 = gql_request(get_bile_verse,headers=headers_auth)
    assert len(executed3["data"]["bibleVerse"]) == 2
    for row in executed3["data"]["bibleVerse"]:
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "test verse one a test verse one b"
        if row["reference"]["verseNumber"] == 2:
            assert row["verseText"] == 'test verse two'

    #update
    variable2 = {
      "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": [
          {"USFM":"\\id rev\n\\c 1\n\\p\n\\v 1a test verse one a edited \n\\v 1b test verse one b edited"}]}}
    #with auth
    executed2 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable2,
      headers=headers_auth)
    assert executed2["data"]["editBibleBook"]["message"] == "Bible books updated successfully"

    #get updated data combine verse re upload usfm
    executed4 = gql_request(get_bile_verse,headers=headers_auth)
    assert len(executed4["data"]["bibleVerse"]) == 1
    for row in executed4["data"]["bibleVerse"]:
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "test verse one a edited test verse one b edited"

def test_post_put_merged_verse():
    """test posting merged verse"""
    variable = {
    "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": [
        {"USFM":"\\id rom\n\\c 1\n\\p\n\\v 1-2 test verse one two merged\n\\v 3 test verse three"}]
    }
    }
    executed,table = check_post(BOOK_ADD_QUERY,variable)
    assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"
    for i,item in enumerate(executed["data"]["addBibleBook"]['data']):
          assert_positive_get_for_books(item)
          book_code = re.match(r'\\id (\w\w\w)', gospel_books_merged_data[i]['USFM']).group(1)
          assert item['book']['bookCode'] == book_code.lower()
    assert len(gospel_books_merged_data) == len(executed["data"]["addBibleBook"]['data'])

    get_bile_verse = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"rom",chapter:1){
    reference{
      bible
      book
      chapter
      verseNumber
      verseNumberEnd
    }
    verseText
  }
}
  """
    #get bible data and check split verses are combined
    executed3 = gql_request(get_bile_verse,headers=headers_auth)
    assert len(executed3["data"]["bibleVerse"]) == 3
    for row in executed3["data"]["bibleVerse"]:
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "test verse one two merged"
        if row["reference"]["verseNumber"] == 2:
            assert row["verseText"] == ''
        if row["reference"]["verseNumber"] == 3:
            assert row["verseText"] == 'test verse three'

    #update
    variable2 = {
      "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": [
          {"USFM":"\\id rom\n\\c 1\n\\p\n\\v 1-2 test verse one two merged edited"}]}}
    #with auth
    executed2 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable2,
      headers=headers_auth)
    assert executed2["data"]["editBibleBook"]["message"] == "Bible books updated successfully"

    #get updated data combine verse re upload usfm
    executed4 = gql_request(get_bile_verse,headers=headers_auth)
    assert len(executed4["data"]["bibleVerse"]) == 2
    for row in executed4["data"]["bibleVerse"]:
        if row["reference"]["verseNumber"] == 1:
            assert row["verseText"] == "test verse one two merged edited"
        if row["reference"]["verseNumber"] == 2:
            assert row["verseText"] == ''

def test_post_optional():
  '''Positive test fr post with optional JSON upload'''
  #json data , json and usf data
  post_data = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "books":[
      {
        "JSON": "{\"book\":{\"bookCode\":\"ACT\"},\"chapters\":[{\"chapterNumber\":\"1\",\"contents\":[{\"verseNumber\":\"1\",\"verseText\":\"First verse of acts\"},{\"verseNumber\":\"2\",\"verseText\":\"Second verse of acts\"},{\"verseNumber\":\"3\",\"verseText\":\"Thrid verse of acts\"}]}]}"
      },
      {
        "USFM":"\\id rev\n\\c 1\n\\p\n\\v 1 test verse one revelations\n\\v 2 test verse two" ,
        "JSON":"{\"book\":{\"bookCode\":\"REV\"},\"chapters\":[{\"chapterNumber\":1,\"contents\":[{\"verseNumber\":1,\"verseText\":\"one verse of revelations\"}]}]}"
      }
    ]
  }
}

  executed , table= check_post(BOOK_ADD_QUERY,post_data)
  assert len(executed["data"]["addBibleBook"]["data"]) == 2

def test_post_duplicate():
  '''test posting the same book twice'''
  variable = {
  "object": {
      "sourceName": "gu_TTT_1_bible",
      "books": [
      {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
      ]
  }
  }
  executed,table = check_post(BOOK_ADD_QUERY,variable)
  assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"
  executed2 = gql_request(BOOK_ADD_QUERY,operation="mutation",variables=variable,
    headers=headers_auth)
  assert "errors" in executed2.keys()

def test_post_incorrect_data():
  ''' tests to check input validation in post API'''    
  #wrong format data
  variable = {
  "object": {
      "sourceName": "gu_TTT_1_bible",
      "books": 
      {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
      
  }
  }
  executed = gql_request(query=BOOK_ADD_QUERY,operation="mutation", variables=variable,
      headers=headers_auth)
  assert "errors" in executed.keys()

  #incorrect data value
  variable2 = {
    "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": 
        {'USFM': '<id gen><c 1><p><v 1 test content>'}
        
    }
}
  executed2 = gql_request(BOOK_ADD_QUERY,operation = "mutation",variables=variable2,
    headers=headers_auth)
  assert "errors" in executed2.keys()

  #incorrect source 
  variable3 = {
  "object": {
      "sourceName": "kl_TTT_1_bible",
      "books": [
      "{\"USFM\":\"\\\\id mat\\n\\\\c 1\\n\\\\p\\n\\\\v 1 test verse one\\n\\\\v 2 test verse two\"}"
      ]
  }
  }
  executed3 = gql_request(BOOK_ADD_QUERY,operation = "mutation",variables=variable3,
    headers=headers_auth)
  assert "errors" in executed3.keys()

def test_post_audio():
  variable = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "audioData":[
  {
    "name": "matthew recording",
    "url": "https://www.somewhere.com/file_mat",
    "books": [
      "mat"
    ],
    "format": "mp3"
  },
  {
    "name": "John recording",
    "url": "https://www.somewhere.com/file_jhn",
    "books": [
      "jhn"
    ],
    "format": "string"
  },
  {
    "name": "letters of John",
    "url": "https://www.somewhere.com/file_jhn_letters",
    "books": [
      "1jn", "2jn", "3jn"
    ],
    "format": "mp3"
  },
  {
    "name": "last books",
    "url": "https://www.somewhere.com/file_rev",
    "books": [
      "rev"
    ],
    "format": "mp3"
  }
]
  }
}
  add_bible()
  add_audio()

  #attempt duplicate
  executed2 = gql_request(AUDIO_ADD_QUERY,operation = "mutation",variables=variable,
    headers=headers_auth)
  assert "errors" in executed2.keys()

  #incorrect data url
  variable3 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "name": "matthew recording",
      "url": "invalid url ",
      "books": [
        "mat"
      ],
      "format": "mp3"
    }
  ]
    }
  }
  executed3 = gql_request(AUDIO_ADD_QUERY,operation = "mutation",variables=variable3,
    headers=headers_auth)
  assert "errors" in executed3.keys()

  #incorrect data book
  variable4 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "name": "matthew recording",
      "url": "https://www.somewhere.com/file_rev",
      "books": [
        "kkk"
      ],
      "format": "mp3"
    }
  ]
    }
  }
  executed4 = gql_request(AUDIO_ADD_QUERY,operation = "mutation",variables=variable4,
    headers=headers_auth)
  assert "errors" in executed4.keys()

  #incorrect data booklist
  variable5 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "name": "matthew recording",
      "url": "https://www.somewhere.com/file_rev",
      "books": ["not a valid book"],
      "format": "mp3"
    }
  ]
    }
  }
  executed5 = gql_request(BOOK_ADD_QUERY,operation = "mutation",variables=variable5,
    headers=headers_auth)
  assert "errors" in executed5.keys()

def test_put_books():
  '''adds some books and change them using put APIs'''
  add_bible()

  #update without specifying the book code
  variable2 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "books": [
        {
          "USFM": "\\id mat\n\\c 1\n\\p\n\\v 1 edited test verse one"
        }
      ]
    }
  }
  #without Auth
  executed2 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable2)
  assert "errors" in executed2
  #with auth
  executed2 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable2,
    headers=headers_auth)
  assert executed2["data"]["editBibleBook"]["message"] == "Bible books updated successfully"
  assert len(executed2["data"]["editBibleBook"]["data"]) == 1
  assert_positive_get_for_books(executed2["data"]["editBibleBook"]["data"][0])
  resp_usfm = executed2["data"]["editBibleBook"]["data"][0]["USFM"].lower().strip().replace("\n", "")
  assert  resp_usfm == variable2["object"]["books"][0]["USFM"].replace("\n", "")
  assert executed2["data"]["editBibleBook"]["data"][0]["book"]["bookCode"] == "mat"

  #not passing USFM and JSON
  variable3 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "books": [
      {
        "USFM": None,
        "JSON": None
      }
    ]
  }
}
  executed3 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable3,
    headers=headers_auth)
  assert "errors" in executed3.keys()

  #to change status
  variable4 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "books": [
      {
        "bookCode": "jhn",
        "USFM": "\\id jhn\n\\c 1\n\\p\n\\v 1 edited test verse one",
        "active": False
      }
    ]
  }
}
  executed4 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable4,
    headers=headers_auth)
  assert executed4["data"]["editBibleBook"]["message"] == "Bible books updated successfully"
  assert len(executed4["data"]["editBibleBook"]["data"]) == 1
  assert_positive_get_for_books(executed4["data"]["editBibleBook"]["data"][0])
  assert not executed4["data"]["editBibleBook"]["data"][0]["active"]
  assert  executed4["data"]["editBibleBook"]["data"][0]["book"]["bookCode"] == "jhn"

  #not available book
  variable5 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "books": [
      {
        "bookCode": "rom",
        "USFM": "\\id rom\n\\c 1\n\\p\n\\v 1 edited test verse one",
        "active": False
      }
    ]
  }
}
  executed5 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable5,
    headers=headers_auth)
  assert "errors" in executed5.keys()

def test_put_audios():
  """test audio edit"""
  add_bible()
  '''Add some audios and change them afterwards using PUT'''
  add_audio()

  variable2 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "url": "https://www.somewhere.com/file_mat_new",
      "books": [
        "mat"
      ]
    }]
      }
    }
  executed2 = gql_request(query=AUDIO_EDIT_QUERY,operation="mutation", variables=variable2,
    headers=headers_auth)
  assert executed2["data"]["editAudioBible"]["message"] == "Bible audios details updated successfully"
  assert executed2["data"]["editAudioBible"]["data"][0]["url"] == "https://www.somewhere.com/file_mat_new"

  #missing book info

  variable3 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "url": "https://www.somewhere.com/file_mat_new",
    "format": "mp3"
    }]
      }
    }
  executed3 = gql_request(query=AUDIO_EDIT_QUERY,operation="mutation", variables=variable3,
    headers=headers_auth)
  assert "errors" in executed3.keys()

  #invalid datas
  variable4 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "url": "in valid url",
      "books": [
        "mat"
      ]
  }]
      }
    }
  executed4 = gql_request(query=AUDIO_EDIT_QUERY,operation="mutation", variables=variable4,
    headers=headers_auth)
  assert "errors" in executed4.keys() 

  variable5 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "url": "https://www.somewhere.com/file_mat_new",
      "books": [
        "kkk"
      ]
    }]
      }
    }
  executed5 = gql_request(query=AUDIO_EDIT_QUERY,operation="mutation", variables=variable5,
    headers=headers_auth)
  assert "errors" in executed5.keys()

def test_get_books_contenttype():
  '''Add some books data into the table and do content type related get tests'''
  add_bible()

  #content type all
  query1 = """
        {
    bibleContents(sourceName:"gu_TTT_1_bible"){
      book {
        bookId
        bookName
        bookCode
      }
      USFM
      JSON
      audio {
        name
        url
        format
        active
      }
      active
    }
  }
  """
  executed1 = gql_request(query=query1,headers=headers_auth)
  assert isinstance(executed1, Dict)
  assert len(executed1["data"]["bibleContents"]) > 0
  items = executed1["data"]["bibleContents"]
  for item in items:
      assert_positive_get_for_books(item)
      assert "USFM"  in item
      assert "JSON" in item
      assert "audio" in item
      assert item["audio"] is None

  #filter with book code 
  query2 = """
      {
  bibleContents(sourceName:"gu_TTT_1_bible",bookCode:"mat"){
    book {
      bookId
      bookName
      bookCode
    }
    USFM
    JSON
    audio {
      name
      url
      format
      active
    }
    active
  }
}
  """
  executed2 = gql_request(query=query2,headers=headers_auth)
  assert isinstance(executed2, Dict)
  assert len(executed2["data"]["bibleContents"]) > 0
  items = executed2["data"]["bibleContents"]
  for item in items:
      assert_positive_get_for_books(item)
      assert "USFM"  in item
      assert "JSON"  in item
      assert "audio" in item
      assert item["audio"] is None

#filter with wrong bookcode
  query3 = """
      {
  bibleContents(sourceName:"gu_TTT_1_bible",bookCode:"kkk"){
    book {
      bookCode
    }
    USFM
    JSON
  }
}
  """
  executed3 = gql_request(query=query3,headers=headers_auth)
  assert_not_available_content_gql(executed3["data"]["bibleContents"])

  #add audio
  add_audio()

  executed5 = gql_request(query=query2,headers=headers_auth)
  assert isinstance(executed5, Dict)
  assert len(executed5["data"]["bibleContents"]) > 0
  items = executed5["data"]["bibleContents"]
  for item in items:
      assert_positive_get_for_books(item)
      assert "USFM"  in item
      assert "JSON"  in item
      assert "audio" in item
      assert not item["audio"] is None

def test_get_books_filter():
  '''add some usfm and audio data and test get api based on book_code and active filters '''
  
  add_bible()

  #active true filter
  query1 = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible",active:true){
    book {
      bookCode
    }
    USFM
    JSON
  }
}
  """
  query2 = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible"){
    book {
      bookCode
    }
  }
}
  """  
  query3 = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible",active:false){
    book {
      bookId
    }
    USFM
    JSON
  }
}
  """  
  executed1 = gql_request(query=query1,headers=headers_auth)
  executed2 = gql_request(query=query2,headers=headers_auth)
  executed3 = gql_request(query=query3,headers=headers_auth)
  assert len(executed1["data"]["bibleContents"]) == len(executed2["data"]["bibleContents"])
  assert_not_available_content_gql(executed3["data"]["bibleContents"])

def test_get_books_versification():
  '''add some usfm and audio data and test get api based on book_code and active filters '''
  add_bible()

  query1 = """
      {
  versification(sourceName:"gu_TTT_1_bible"){
    maxVerses
    mappedVerses
    excludedVerses
    partialVerses
  }
}
  """
  executed1 = gql_request(query1,headers=headers_auth)
  assert len(executed1["data"]["versification"]["maxVerses"]) == 4
  assert executed1["data"]["versification"]["maxVerses"]['mat'][0] == 2
  assert executed1["data"]["versification"]["maxVerses"]['mrk'][0] == 2
  assert executed1["data"]["versification"]["maxVerses"]['luk'][0] == 2
  assert executed1["data"]["versification"]["maxVerses"]['jhn'][0] == 2
  #versification for books after adding audio

  add_audio()
  executed3 = gql_request(query1,headers=headers_auth)
  assert len(executed1["data"]["versification"]["maxVerses"]) == \
    len(executed3["data"]["versification"]["maxVerses"])

def test_get_verses():
  '''Upload some bibles and fetch verses'''
  add_bible()

  query1 = """
      {
  bibleVerse(sourceName:"gu_TTT_1_bible"){
    refId
    refString
    reference{
      bible
      book
      chapter
      verseNumber
      verseNumberEnd
    }
    verseText
  }
}
  """
  executed1 = gql_request(query1,headers=headers_auth)
  assert len(executed1["data"]["bibleVerse"]) == 8
  for item in executed1["data"]["bibleVerse"]:
      assert_positive_get_for_verse(item)

  query2 = """
    {
  bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"mat"){
    refId
    refString
  }
}
  """
  executed2 = gql_request(query2,headers=headers_auth)
  assert len(executed2["data"]["bibleVerse"]) == 2

  query3 = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"mat",chapter:1){
  refId
  refString
}
}
  """
  executed3 = gql_request(query3,headers=headers_auth)
  assert len(executed3["data"]["bibleVerse"]) == 2

  query4 = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"mat",chapter:1,verse:1){
  refId
  refString
}
}
  """
  executed4 = gql_request(query4,headers=headers_auth)
  assert len(executed4["data"]["bibleVerse"]) == 1

  query5 = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"mat",chapter:1,verse:1,lastVerse:10){
  refId
  refString
}
}
  """
  executed5 = gql_request(query5,headers=headers_auth)
  assert len(executed5["data"]["bibleVerse"]) == 2

  query6 = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"mat",chapter:1,verse:10){
  refId
  refString
}
}
  """
  executed6 = gql_request(query6,headers=headers_auth)
  assert_not_available_content_gql(executed6["data"]["bibleVerse"])

  query7 = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"act",chapter:2){
  refId
  refString
}
}
  """
  executed7 = gql_request(query7,headers=headers_auth)
  assert_not_available_content_gql(executed7["data"]["bibleVerse"])

  # add audio
  add_audio()

  query8 = """
    {
bibleVerse(sourceName:"gu_TTT_1_bible",bookCode:"rev",chapter:1,verse:10){
  refId
  refString
}
}
  """
  executed8 = gql_request(query8,headers=headers_auth)
  assert_not_available_content_gql(executed8["data"]["bibleVerse"])

def test_audio_delete():
  '''add data, update active field with put and try get apis with active filters'''
  add_bible()
  add_audio()

  query = """
    {
bibleContents(sourceName:"gu_TTT_1_bible"){
  book{
  bookName
}
  audio{
    name
    active
  }
  active
}
}
  """
  executed = gql_request(query,headers=headers_auth)
  assert len(executed["data"]["bibleContents"]) == 8
  
  #delete one audio , but not book

  variable1 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "url": "https://www.somewhere.com/file_mat_new",
      "books": [
        "mat"
      ],
      "active": False
    }]
      }
    }
  executed1 = gql_request(AUDIO_EDIT_QUERY,operation="mutation",variables=variable1,
    headers=headers_auth)
  executed2 = gql_request(query,headers=headers_auth)
  assert len(executed2["data"]["bibleContents"]) == 8
  assert executed2["data"]["bibleContents"][0]["active"]
  assert not executed2["data"]["bibleContents"][0]["audio"]["active"]


  #try delete non existing audio
  query2 = """
      mutation editaudio($object:InputEditAudioBible){
editAudioBible(audioBibleArg:$object){
  message
  data{
    name
    url
    book{
      bookId
      bookName
      bookCode
    }
    format
    active
  }
  
}
}
  """
  variable2 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "audioData":[
    {
      "url": "https://www.somewhere.com/file_mat",
      "books": [
        "mrk"
      ],
      "active": False
    }]
      }
    }
  executed2 = gql_request(query2,operation="mutation",variables=variable2,headers=headers_auth)
  assert "errors" in executed2.keys()

def test_book_delete():
  '''add data, update active field with put and try get apis with active filters'''
  add_bible()
  query = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible"){
   book{
    bookName
  }
  }
}
  """
  executed = gql_request(query,headers=headers_auth)
  assert len(executed["data"]["bibleContents"]) == 4

  #soft delete one book
  query1 = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible"){
   book{
    bookName
  }
  }
}
  """
  variable1 = {
  "object": {
    "sourceName": "gu_TTT_1_bible",
    "books":[{
      "bookCode": "mat",
      "USFM": "\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
      "active": False
    }]
  }
}

  query2 = """
       mutation editaudio($object:InputEditAudioBible){
  editAudioBible(audioBibleArg:$object){
    message
    data{
      name
      url
      book{
        bookId
        bookName
        bookCode
      }
      format
      active
    }
    
  }
}
    """
  variable2 = {
      "object": {
        "sourceName": "gu_TTT_1_bible",
        "audioData":[
      {
        "url": "https://www.somewhere.com/file_mat",
        "books": [
          "mat"
        ],
        "active": False
      }]
        }
      }
  executed2 = gql_request(query2,operation="mutation",variables=variable2,
    headers=headers_auth)
  executed1 = gql_request(BOOK_EDIT_QUERY,operation="mutation",variables=variable1,
    headers=headers_auth)
  executed3 = gql_request(query1,headers=headers_auth)
  assert len(executed3["data"]["bibleContents"]) == 3

  query4 = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible",active:false){
   book{
    bookName
  }
  }
}
  """

  executed4 = gql_request(query4,headers=headers_auth)
  assert len(executed4["data"]["bibleContents"]) == 1

  #add audio 4 audio adding
  add_audio()

  query5 = """
    {
  bibleContents(sourceName:"gu_TTT_1_bible"){
   book{
    bookName
  }
  }
}
  """

  executed5 = gql_request(query5,headers=headers_auth)
  assert len(executed5["data"]["bibleContents"]) == 8


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
    "contentType": "bible",
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
        "sourceName": "gu_TTT_1_bible",
        "books": [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]
    }
    }

    executed = gql_request(query=BOOK_ADD_QUERY,operation="mutation", variables=variable,
      headers=headers_SA)
    assert executed["data"]["addBibleBook"]["message"] == "Bible books uploaded and processed successfully"

    #update without specifying the book code
    variable2 = {
    "object": {
      "sourceName": "gu_TTT_1_bible",
      "books": [
        {
          "USFM": "\\id mat\n\\c 1\n\\p\n\\v 1 edited test verse one"
        }
      ]
    }
  }
    #Edit with SA created user
    executed2 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable2,
      headers=headers_SA)
    assert executed2["data"]["editBibleBook"]["message"] == "Bible books updated successfully"
    #edit with VA not created user
    executed2 = gql_request(BOOK_EDIT_QUERY,operation = "mutation",variables=variable2,
      headers=headers_auth)
    assert "errors" in executed2

def test_get_access_with_user_roles_and_apps():
    """Test get filter from apps and with users having different permissions"""
    # #add version
    version_add(version_query,VERSION_VAR)

    content_data = {
    "object": {
        "sourceName": "gu_TTT_1_bible",
        "books": [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two"}
]
    }
    }

    get_query_book = """
      query get_bibles($source:String!){
  bibleContents(sourceName:$source){
   book{
      bookId
    }
    USFM
  }
}
    """
    get_var = {
      "source": "gu_TTT_1_commentary"
    }

    get_query_versification = """
       query get_versification($source:String!){
  versification(sourceName:$source){
   maxVerses
  }
}
    """
    get_query_verses = """
       query get_verses($source:String!){
  bibleVerse(sourceName:$source){
   verseText
  }
}
    """

    content_qry = BOOK_ADD_QUERY
    test_data = {"books":{"get_query": get_query_book},
                 "versification":{"get_query": get_query_versification},
                  "verses":{"get_query": get_query_verses},
                "get_var": get_var  
        }

    contetapi_get_accessrule_checks_app_userroles_gql("bible",content_qry, content_data , 
      test_data , bible=True)