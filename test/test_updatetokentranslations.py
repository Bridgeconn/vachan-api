# -- coding: utf - 8 --
import pytest
import requests
import json

@pytest.fixture
def url():
	return "https://stagingapi.autographamt.com/v1/updatetokentranslations"



@pytest.mark.parametrize('token,translation,sourceId,targetLanguageId,senses',[('असते','ass',24,"181",'as')])
def test_Updatetokentranslationsup8(url,token,translation,sourceId,targetLanguageId,senses):
	data = {'token':token,
			'translation':translation,
            'sourceId':sourceId,
            'targetLanguageId':targetLanguageId,
			'senses':senses
            }
	resp = requests.post(url,data=json.dumps(data))
	out = json.dumps(resp.text)
	assert resp.status_code == 200, resp.text
	# print (out)
	# assert out['success'] == False
	# assert out['message'] == "Source does not exist"


#------------- error need to find---------------------#