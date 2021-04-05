'''Executes and tests the AgMT and eneric translation workflows.
This is not part of the automated tests, and data added to DB by running this script will persist.
This is to be used manually during develepment testing'''
import json
import requests

BASE_URL = "http://127.0.0.1:8000/v2/"
headers = {"contentType": "application/json", "accept": "application/json"}

# have a bible source to be used
source_name = "hin_XYZ_1_bible"
project_id = 100000

ver_data = {
    "versionAbbreviation": "XYZ",
    "versionName": "Xyz version to test",
    "revision": "1",
    "metaData": {"owner": "someone", "access-key": "123xyz"}
}

src_data = {
    "contentType": "bible",
    "language": "hin",
    "version": "XYZ",
    "revision": 1,
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
    "projectName": "Test project 1",
    "sourceLanguageCode": "hin",
    "targetLanguageCode": "mal"
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
    "uploadedBooks":[bible_books['mat'], bible_books['mrk']],
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

new_user_id = 20202
user_data = {
	"project_id": project_id,
	"userId": new_user_id,
	"userRole": "test role",
	"metaData": {"somekey": "value"},
	"active": False
}

alignment_src = "hin"
alignment_trg = "mal"
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
      {
        "sourceTokenIndex": 2,
        "targetTokenIndex": 8
      },
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
# resp = requests.post(BASE_URL+"versions", headers=headers, json=ver_data)
# assert resp.json()['message'] == "Version created successfully"

# resp = requests.post(BASE_URL+"sources", headers=headers, json=src_data)
# assert resp.json()['message'] == "Source created successfully"
# source_name = resp.json()['data']['sourceName']

# resp = requests.post(BASE_URL+"bibles/"+source_name+"/books", headers=headers, json=gospel_books_data)
# assert resp.json()['message'] == "Bible books uploaded and processed successfully"

# resp = requests.post(BASE_URL+"autographa/projects", headers=headers, json=project_post_data)
# print(resp)
# print(resp.json())
# assert resp.json()['message'] == "Project created successfully"
# project_update_data['projectId'] = resp.json()['data']['projectId']
# project_id = resp.json()['data']['projectId']

# resp = requests.put(BASE_URL+"autographa/projects", headers=headers, json=project_update_data)
# assert resp.json()['message'] == "Project updated successfully"

# # tokenize
# resp = requests.get(BASE_URL+"autographa/project/tokens?project_id="+str(project_id))
# # print(json.dumps(resp.json()))

# # translate
# resp = requests.put(BASE_URL+"autographa/project/tokens?project_id="+str(project_id),
# 	headers=headers, json=token_update_data)
# assert resp.json()['message'] == "Token translations saved"

# # Additional user
# resp = requests.post(BASE_URL+"autographa/project/user?project_id="+str(project_id)+
# 	";user_id="+str(new_user_id), headers=headers)
# assert resp.json()['message'] == "User added to project successfully"

# resp = requests.put(BASE_URL+"autographa/project/user", headers=headers, json=user_data)
# assert resp.json()['message'] == "User updated in project successfully"

# resp = requests.get(BASE_URL+"autographa/projects?user_id="+str(new_user_id))
# assert len(resp.json()) > 0
# print(resp.json())



# # Suggestions

resp = requests.post(BASE_URL+"translation/learn/alignment?source_language="+alignment_src+
	";target_language="+alignment_trg, headers=headers, json=alignment_data)
print(resp)
print(resp.json())

# resp = requests.put(BASE_URL+"autographa/project/suggest-translation?project_id="+str(project_id),
# 	headers=headers)
# print(resp)
# print(resp.json())

