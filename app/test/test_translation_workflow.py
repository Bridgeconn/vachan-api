'''Executes and tests the AgMT and generic translation workflows.
This is not part of the automated tests, and data added to DB by running this script will persist.
This is to be used manually during develepment testing'''
import json
import requests
from . import client
from .test_versions import check_post
from .test_resources import check_post as source_post
from .conftest import initial_test_users

BASE_URL = "v2/"
headers = {"contentType": "application/json", "accept": "application/json"}

# have a bible source to be used
source_name = "hi_XYZ_1_bible" # pylint: disable=C0103
project_id = None # pylint: disable=C0103

ver_data = {
    "versionAbbreviation": "XYZ",
    "versionName": "Xyz version to test",
    "revision": "1",
    "metaData": {"owner": "someone", "access-key": "123xyz"}
}

src_data = {
    "resourceType": "bible",
    "language": "hi",
    "version": "XYZ",
    "revision": 1,
    "accessPermissions": [
            "content","open-access"
        ],
    "year": 2020,
    "license": "CC-BY-SA",
    "metaData": {"owner": "someone", "access-key": "123xyz"}
}

gospel_books_data = [
        {"USFM":"\\id mat\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "MAT"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
    }''')},
        {"USFM":"\\id mrk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "MRK"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
    }''')},
        {"USFM":"\\id luk\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "LUK"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
    }''')},
        {"USFM":"\\id jhn\n\\c 1\n\\p\n\\v 1 test verse one\n\\v 2 test verse two",
         "JSON":json.loads('''{
    "book": {
        "bookCode": "JHN"
    },
    "chapters": [
        {
            "chapterNumber": "1",
            "contents": [
                {
                    "p": null
                },
                {
                    "verseNumber": "1",
                    "verseText": "test verse one",
                    "contents": [
                        "test verse one"
                    ]
                },
                {
                    "verseNumber": "2",
                    "verseText": "test verse two",
                    "contents": [
                        "test verse two"
                    ]
                }
            ]
        }
    ],
    "_messages": {
        "_warnings": [
            "Empty lines present. ",
            "Book code is in lowercase. "
        ]
    }
    }''')},
]

project_post_data = {
    "projectName": "Test project 4",
    "sourceLanguageCode": "hi",
    "targetLanguageCode": "ml"
}

bible_books = {
    "mat":  "\\id MAT\n\\c 1\n\\p\n\\v 1 इब्राहीम के वंशज दाऊद के पुत्र यीशु मसीह की वंशावली इस "+
            "प्रकार है:\n\\v 2 इब्राहीम का पुत्र था इसहाक और इसहाक का पुत्र हुआ याकूब। फिर याकूब "+
            "से यहूदा और उसके भाई उत्पन्न हुए।\n\\v 3 यहूदा के बेटे थे फिरिस और जोरह। (उनकी माँ "+
            "का नाम तामार था।) फिरिस, हिस्रोन का पिता था। हिस्रोन राम का पिता था।",
    "mrk":    "\\id MRK\n\\c 1\n\\p\n\\v 1 यह परमेश्वर के पुत्र यीशु मसीह के शुभ संदेश का प्रारम्भ"+
            " है।\n\\v 2 भविष्यवक्ता यशायाह की पुस्तक में लिखा है कि: “सुन! मैं अपने दूत को तुझसे"+
            " पहले भेज रहा हूँ। वह तेरे लिये मार्ग तैयार करेगा।”\n\\v 3 “जंगल में किसी पुकारने "+
            "वाले का शब्द सुनाई दे रहा है: ‘प्रभु के लिये मार्ग तैयार करो। और उसके लिये राहें "+
            "सीधी बनाओ।’”\n\\v 4 यूहन्ना लोगों को जंगल में बपतिस्मा देते आया था। उसने लोगों से"+
            " पापों की क्षमा के लिए मन फिराव का बपतिस्मा लेने को कहा।\n\\v 5 फिर समूचे यहूदिया"+
            " देश के और यरूशलेम के लोग उसके पास गये और उस ने यर्दन नदी में उन्हें बपतिस्मा दिया"+
            "। क्योंकि उन्होंने अपने पाप मान लिये थे।"
}

project_update_data = {
	"projectId":project_id,
    "uploadedUSFMs":[bible_books['mat'], bible_books['mrk']],
    "selectedBooks":{"bible": source_name,
    				 "books": ['luk', 'jhn']}

}

token_update_data = [
	{
		"token":"यीशु मसीह",
		"occurrences":[
			{"sentenceId":41001001, "offset":[31, 40]}],
		"translation":"യേശു ക്രിസ്തു"
	},
	{
		"token":"पुत्र",
		"occurrences":[
			{"sentenceId":41001001, "offset":[25,30]}],
		"translation":"പുത്രന്‍"
	},
	{
		"token":"इब्राहीम",
		"occurrences":[
			{"sentenceId":41001002, "offset":[0, 8]}],
		"translation":"അബ്രഹാം"
	}
]

NEW_USER_ID = initial_test_users['AgUser']['test_user_id']
user_data = {
	"project_id": project_id,
	"userId": NEW_USER_ID,
	"userRole": "test role",
	"metaData": {"somekey": "value"},
	"active": False
}

ALIGNMENT_SRC = "hi"
ALIGNMENT_TRG = "ml"
alignment_data = [
{
    "sourceTokenList": [
      "क्योंकि","परमेश्वर","ने","जगत","से","ऐसा","प्रेम","रखा","कि","उसने",
      "अपना","एकलौता","पुत्र","दे","दिया","ताकि","जो","कोई","उस","पर","विश्वास","करे",
      "वह","नाश","न","हो","परन्तु","अनन्त","जीवन","पाए"
    ],
    "targetTokenList": [
      "തന്റെ",
      "ഏകജാതനായ","പുത്രനിൽ",
      "വിശ്വസിക്കുന്ന","ഏവനും","നശിച്ചുപോകാതെ","നിത്യജീവൻ",
      "പ്രാപിക്കേണ്ടതിന്","ദൈവം","അവനെ","നല്കുവാൻ","തക്കവണ്ണം",
      "ലോകത്തെ","സ്നേഹിച്ചു"
    ],
    "alignedTokens": [
      {
        "sourceTokenIndex": 1,
        "targetTokenIndex": 8
      },
      # {
      #   "sourceTokenIndex": 2,
      #   "targetTokenIndex": 8
      # },
      {
        "sourceTokenIndex": 3,
        "targetTokenIndex": 12
      },
      {
        "sourceTokenIndex": 4,
        "targetTokenIndex": 12
      },
      {
        "sourceTokenIndex": 5,
        "targetTokenIndex": 11
      },
      {
        "sourceTokenIndex": 6,
        "targetTokenIndex": 13
      },
      {
        "sourceTokenIndex": 7,
        "targetTokenIndex": 13
      },
      {
        "sourceTokenIndex": 8,
        "targetTokenIndex": 13
      },
      {
        "sourceTokenIndex": 9,
        "targetTokenIndex": 0
      },
      {
        "sourceTokenIndex": 10,
        "targetTokenIndex": 0
      },
      {
        "sourceTokenIndex": 11,
        "targetTokenIndex": 1
      },
      {
        "sourceTokenIndex": 12,
        "targetTokenIndex": 1
      },
      {
        "sourceTokenIndex": 11,
        "targetTokenIndex": 2
      },
      {
        "sourceTokenIndex": 12,
        "targetTokenIndex": 2
      },
      {
        "sourceTokenIndex": 13,
        "targetTokenIndex": 10
      },
      {
        "sourceTokenIndex": 14,
        "targetTokenIndex": 10
      },
      {
        "sourceTokenIndex": 20,
        "targetTokenIndex": 3
      },
      {
        "sourceTokenIndex": 21,
        "targetTokenIndex": 3
      },
      {
        "sourceTokenIndex": 18,
        "targetTokenIndex": 4
      },
      {
        "sourceTokenIndex": 19,
        "targetTokenIndex": 4
      },

      {
        "sourceTokenIndex": 23,
        "targetTokenIndex": 5
      },
      {
        "sourceTokenIndex": 24,
        "targetTokenIndex": 5
      },
      {
        "sourceTokenIndex": 25,
        "targetTokenIndex": 5
      },
      {
        "sourceTokenIndex": 27,
        "targetTokenIndex": 6
      },
      {
        "sourceTokenIndex": 28,
        "targetTokenIndex": 6
      },
      {
        "sourceTokenIndex": 29,
        "targetTokenIndex": 7
      }
	]
}
]

def test_end_to_end_translation():
    '''happy path test for AGMT translation workflow'''
    # resp = client.post(BASE_URL+"versions", headers=headers, json=ver_data)
    resp = check_post(ver_data)
    assert resp.json()['message'] == "Version created successfully"


    # resp = client.post(BASE_URL+"sources", headers=headers, json=src_data)
    resp = source_post(src_data)
    assert resp.json()['message'] == "Resource created successfully"
    source_name = resp.json()['data']['resourceName']

    headers_auth = {"contentType": "application/json",
                "accept": "application/json",
                "app":"Autographa"
            }
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['VachanAdmin']['token']
    resp = client.post(BASE_URL+"resources/bibles/"+source_name+"/books", headers=headers_auth,
    json=gospel_books_data)
    assert resp.json()['message'] == "Bible books uploaded and processed successfully"

    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    resp = client.post(BASE_URL+"text/translate/token-based/projects", headers=headers_auth, json=project_post_data)
    assert resp.json()['message'] == "Project created successfully"
    proj_id = resp.json()['data']['projectId']

    resp = client.put(BASE_URL+"text/translate/token-based/projects"+'?project_id='+str(proj_id), \
      headers=headers_auth, json=project_update_data)
    assert resp.json()['message'] == "Project updated successfully"

    # tokenize
    resp = client.get(BASE_URL+"text/translate/token-based/project/tokens?project_id="+str(proj_id),headers=headers_auth)
    assert resp.status_code == 200

    # translate
    resp = client.put(BASE_URL+"text/translate/token-based/project/tokens?project_id="+str(proj_id),
    	headers=headers_auth, json=token_update_data)
    assert resp.json()['message'] == "Token translations saved"

    # Additional user
    NEW_USER_ID = initial_test_users['AgUser']['test_user_id']
    headers_auth['Authorization'] = "Bearer"+" "+initial_test_users['AgAdmin']['token']
    resp = client.post(BASE_URL+"text/translate/token-based/project/user?project_id="+str(proj_id)+
    	"&user_id="+str(NEW_USER_ID), headers=headers_auth)
    assert resp.json()['message'] == "User added to project successfully"

    user_data['userId'] = NEW_USER_ID
    resp = client.put(BASE_URL+"text/translate/token-based/project/user"'?project_id='+str(proj_id),\
       headers=headers_auth, json=user_data)
    # print(resp.json())
    assert resp.json()['message'] == "User updated in project successfully"

    resp = client.get(BASE_URL+"text/translate/token-based/projects?user_id="+str(NEW_USER_ID),headers=headers_auth)
    assert len(resp.json()) > 0

    # # Suggestions

    resp = client.post(BASE_URL+"nlp/alignment?source_language="+ALIGNMENT_SRC+
    	"&target_language="+ALIGNMENT_TRG, headers=headers_auth, json=alignment_data)
    # print("**",resp)
    assert resp.status_code == 201
    # print(resp)
    

    # tokenize after adding token "परमेश्वर" via alignment
    resp = client.put(BASE_URL+"text/translate/token-based/project/suggestions?project_id="+str(proj_id)+
        "&sentence_id_list=42001001",
    	headers=headers_auth)
    draft = resp.json()[0]['draft']
    assert "ദൈവം" in draft
    assert "പുത്രന്‍" in draft
    assert "യേശു ക്രിസ്തു" in draft