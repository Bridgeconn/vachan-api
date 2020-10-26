# -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"


@pytest.fixture
def get_adm_accessToken():
	email = "alex@yopmail.com"
	password = "1189"
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

@pytest.fixture
def get_supAdmin_accessToken():
	email = 'savitha.mark@bridgeconn.com'
	password = '221189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

@pytest.fixture
def get_trans_accessToken():
	email = 'ag2@yopmail.com'
	password = '1189'
	url = "https://stagingapi.autographamt.com/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token


# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('असते','ass',"35","39",'as')])
# def test_Updatetokentranslationsup12(supply_url,get_supAdmin_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.dumps(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == True, str(j)
# 	# assert j['message'] == "Translation has been inserted", str(j)


@pytest.mark.parametrize('projectId,token,translation,senses',[("39",'असते',"111",'as')])
def test_updateProjectTokenTranslationssup8(supply_url,get_supAdmin_accessToken,projectId,token,translation,senses):
	url = supply_url + '/v1/autographamt/projects/translations'
	data = {'projectId':projectId,
			'token':token,
            'translation':translation,
			'senses':senses
            }
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.dumps(resp.text)
	assert resp.status_code == 200, resp.text
	print(j)
	# assert j['success'] == False, str(j)
	# assert j['message'] == "UnAuthorized/ You haven\'t been assigned this project", str(j)

# @pytest.mark.parametrize('projectId,token,translation,senses',[("39",'असते',"111",'as')])
# def test_updateProjectTokenTranslationssup9(supply_url,get_supAdmin_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.dumps(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	print(j)
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "Source does not exist", str(j)


# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('असते','ass',"3702","181",'as')])
# def test_updateProjectTokenTranslations10(supply_url,get_supAdmin_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.dumps(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	(j)
# 	# assert j['success'] == True, str(j)
# 	# assert j['message'] == "Translation has been inserted", str(j)



# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('असते','ass',"3702","181",'as')])
# def test_updateProjectTokenTranslations11(supply_url,get_supAdmin_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.dumps(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == True, str(j)
# 	# assert j['message'] == "No New change. This data has already been saved", str(j)


# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('असते','ass',"3702","181",'as')])
# def test_updateProjectTokenTranslations18(supply_url,get_supAdmin_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
# 	j = json.dumps(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == True, str(j)
# 	# assert j['message'] == "Translation has been updated", str(j)

# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('आणि','uda',"3702","181","sg")])
# def test_updateProjectTokenTranslationstr(supply_url,get_trans_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "Target Language does not exist", str(j)

# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('आणि','uda',"3702","181","sg")])
# def test_updateProjectTokenTranslationstr2(supply_url,get_trans_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_trans_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "No New change. This data has already been saved", str(j)



# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('आनंद','udaharan',"3702","", "tt")])
# def test_updateProjectTokenTranslationsad2(supply_url,get_adm_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "Target Language does not exist", str(j)


# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('आला','udaharan'," "," "," ")])
# def test_updateProjectTokenTranslationsad3(supply_url,get_adm_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "Source does not exist", str(j)


# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('आला','ala',"45","181","wsd")])
# def test_updateProjectTokenTranslationsad4(supply_url,get_adm_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "Translation has been updated", str(j)


# @pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('असते','asate',"45","181","gv")])
# def test_updateProjectTokenTranslationsad5(supply_url,get_adm_accessToken,token,translation,sourceId,targetLanguageId,senses):
# 	url = supply_url + '/v1/updatetokentranslations'
# 	data = {'token':token,
# 			'translation':translation,
#             'sourceId':sourceId,
#             'targetLanguageId':targetLanguageId,
# 			'senses':senses
#             }
# 	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_adm_accessToken)})
# 	j = json.loads(resp.text)
# 	assert resp.status_code == 200, resp.text
# 	# assert j['success'] == False, str(j)
# 	# assert j['message'] == "No New change. This data has already been saved", str(j)

