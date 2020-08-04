#-*-coding:utf-8-*-
import pytest
import requests
import json

@pytest.fixture
# GET API
def url():
	return "https://stagingapi.autographamt.com//v1/bibles/upload"

@pytest.fixture
def data():
    data = {"sourceId":50,"wholeUsfmText":"\\id MAT\r\n\\ide UTF-8\r\n\\rem Copyright Information: Creative Commons Attribution-ShareAlike 4.0 License\r\n\\h मलाकी\r\n\\toc1 मलाकी\r\n\\toc2 मलाकी\r\n\\mt1 Malachi\r\n\\mt1 मलाकी\r\n\\c 1\r\n\\p\r\n\\v 1 मलाकी के द्वारा इस्राएल के लिए कहा हुआ यहोवा का भारी वचन।\r\n\\s इस्राएल परमेश्‍वर का अतिप्रिय","parsedUsfmText":{"metadata":{"id":{"book":"MAT"},"headers":[{"ide":"UTF-8"},{"rem":[{"text":"Copyright Information: Creative Commons Attribution-ShareAlike 4.0 License"}]},{"h":"मलाकी"},{"toc1":[{"text":"मलाकी"}]},{"toc2":[{"text":"मलाकी"}]},[{"mt":[{"text":"Malachi"}],"number":"1"},{"mt":[{"text":"मलाकी"}],"number":"1"}]]},"chapters":[{"header":{"title":"1"},"metadata":[{"styling":[{"marker":"p"}]}],"verses":[{"number":"1 ","metadata":[{"section":{"text":"इस्राएल परमेश्‍वर का अतिप्रिय","marker":"s"},"index":1}],"text objects":[{"text":"मलाकी के द्वारा इस्राएल के लिए कहा हुआ यहोवा का भारी वचन।","index":0}],"text":"मलाकी के द्वारा इस्राएल के लिए कहा हुआ यहोवा का भारी वचन। "}]}],"messages":{"warnings":[]}}}
    return data



# --------------- upload existing data----------------------#
def test_org_sourceUpload(url, data):
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == False
	assert j['message'] == "Book already Uploaded"


#----------------upload new books with updated content------------#
@pytest.mark.skip(reason="need to change the values")
def test_org_sourceUpload1(url, data):
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == True