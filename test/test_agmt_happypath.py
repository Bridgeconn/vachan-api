import pytest
import requests
import json
import re
import time

import smtplib
import time
import imaplib
import email


####################################################
########       AGMT HAPPY PATH TESTING       #######
####################################################
testuser1_email = 'agmttest1@gmail.com'
testuser1_email_password = 'd4c3b2a1'
testuser1_first_password = '222222'
testuser1_password = '111111'
testuser2_email = 'agmttest2@gmail.com'
testuser2_email_password = 'd4c3b2a1'
testuser2_password = '111111'
pytest.testuser1_userId = None
pytest.testuser2_userId = None
pytest.organisation_id = None
pytest.project_id = None
pytest.source_id = None
pytest.translated_tokens = []
pytest.source_present = False
target_lang_id = 3
source_usfm = '''\\id MRK
\\c 1
\\p
\\v 1 one two three four five
\\v 2 once I caught a fish alive!
'''

source_json = '''
{"metadata":{"id":{"book":"MRK"}},"chapters":[{"header":{"title":"1"},"metadata":[{"styling":[{"marker":"p"}]}],"verses":[{"number":"1 ","text objects":[{"text":"one two three four five","index":0}],"text":"one two three four five "},{"number":"2 ","text objects":[{"text":"once I caught a fish alive!","index":0}],"text":"once I caught a fish alive! "}]}],"messages":{"warnings":[]}}
'''

expected_target = '''\\id  MRK
\\c  1
\\p 
\\v  1 eak tho theen   chaar paanch 
\\v  2 once I caught a fish alive!
'''
translations = {
	"four five": "chaar paanch", "one two three": "eak tho theen"
}

verificationCode_pattern = re.compile(r'/v1/verifications/([\w\d]+)')
temppass_pattern = re.compile(r'Your temporary password is (\d+)\.')


@pytest.fixture
def supply_url():
	# return "http://localhost:8000"
	return "https://stagingapi.autographamt.com"

@pytest.fixture
def get_translator_accessToken(supply_url):
	url = supply_url + "/v1/auth"
	data = {'email':testuser2_email,
			'password':testuser2_password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

@pytest.fixture
def get_admin_accessToken(supply_url):
	url = supply_url + "/v1/auth"
	data = {'email':testuser1_email,
			'password':testuser1_password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']
	return token

@pytest.fixture
def get_supAdmin_accessToken(supply_url):
	# email = 'savitha.mark@bridgeconn.com'
	# password = '221189'
	email = 'bijob89@gmail.com'
	password = '111111'
	url = supply_url + "/v1/auth"
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	respobj = json.loads(resp.text)
	token = respobj['accessToken']

	return token

def get_mail(email_id,password):
	ORG_EMAIL   = "@gmail.com"
	FROM_EMAIL  = email_id
	FROM_PWD    = password
	SMTP_SERVER = "imap.gmail.com"
	SMTP_PORT   = 993
	AGMT_EMAIL = 'noreply@autographamt.in'
	try:
		mail = imaplib.IMAP4_SSL(SMTP_SERVER)
		mail.login(FROM_EMAIL,FROM_PWD)
		mail.select('inbox')

		type, data = mail.search(None, 'ALL')
		mail_ids = data[0]

		id_list = mail_ids.split()   
		first_email_id = int(id_list[0])
		latest_email_id = int(id_list[-1])
		# for i in range(latest_email_id,first_email_id, -1):
		for i in range(5):
			if i == len(id_list) :
				break
			typ, data = mail.fetch(id_list[-(i)], '(RFC822)' )

			for response_part in data:
				if isinstance(response_part, tuple):
					msg = email.message_from_string(response_part[1].decode('utf-8'))
					email_body = msg.get_payload(decode=True)
					email_subject = msg['Subject']
					if email_subject.startswith('AutographaMT'):
						return email_body.decode('utf-8')
	except Exception as e:
		print( str(e))
	return "Verification mail not received!"




############## User Account Management ############################

# create test users 
@pytest.mark.parametrize("firstName,lastName,email, password,email_password",[('testuser1','admin',testuser1_email,testuser1_first_password,testuser1_email_password),('testuser2','translator',testuser2_email,testuser2_password,testuser2_email_password)])
def test_user_register(supply_url,get_supAdmin_accessToken, firstName,lastName,email,password,email_password):
	url = supply_url + "/v1/registrations"
	data = {'firstName':firstName,
			'lastName':lastName,
			'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	if j['success'] == True:
		assert j['message'] == "Verification Email has been sent to your email id",str(j['message'])
		time.sleep(10)
		# verify by email
		email = get_mail(email_addr,email_password)
		matchObj = re.search(verificationCode_pattern,email)
		verification_code = matchObj.group(1)
		url = supply_url + "/v1/verifications/" + verification_code
		resp = requests.get(url,allow_redirects=False)
		assert resp.status_code == 302,resp.status_code
	else:
		assert j['message'] == "This email has already been Registered. Account is deactivated. "
		# Actiavte deactiavted user
		url = supply_url + "/v1/autographamt/user/activate"
		data = {"userEmail":email}
		resp = requests.post(url, data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
		j = json.loads(resp.text)
		assert j['success'] == True
		assert j['message'] == "User re-activated"


# reset password 
@pytest.mark.parametrize("email",[(testuser1_email),(testuser2_email)])
def test_user_passReset(supply_url,email):
	url = supply_url + "/v1/resetpassword" 
	data = {'email':email}
	resp = requests.post(url, data=data)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == True,str(j['success'])
	assert j['message'] == "Link to reset password has been sent to the registered mail ID",str(j['message'])
	time.sleep(10)

@pytest.mark.parametrize("email_id,email_password,new_password",
	[(testuser1_email, testuser1_email_password,testuser1_password),
	 (testuser2_email, testuser2_email_password,testuser2_password)])
def test_user_setnewPass(supply_url, email_id,email_password,new_password):
	email_body = get_mail(email_id,email_password)
	matchObj = re.search(temppass_pattern,email_body)
	temporaryPassword = matchObj.group(1)
	url = supply_url + "/v1/forgotpassword"
	data = {'temporaryPassword':temporaryPassword,
			'password': new_password
			}
	resp = requests.post(url, data=data)
	j = json.loads(resp.text)
	assert resp.status_code == 200, request.text
	assert j['success'] == True,str(j['success'])
	assert j['message'] == "Password has been reset. Login with the new password.",str(j['message'])

# sign in 
@pytest.mark.parametrize("email,password",[(testuser1_email,testuser1_password),(testuser2_email,testuser2_password)])
def test_user_signin(supply_url,email,password):
	url = supply_url + "/v1/auth" 
	data = {'email':email,
			'password':password}
	resp = requests.post(url, data=data)
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert "accessToken" in j, "success="+str(j['success'])+j['message']


############# Organisation and project management ################

# request to create organisation
@pytest.mark.parametrize('org_name, org_addr, org_phone, org_email',[('test_org','Delhi','000',testuser1_email)])
def test_org_create(supply_url,get_admin_accessToken,org_name, org_addr, org_phone, org_email):
	url = supply_url + '/v1/autographamt/organisations'
	data = {'organisationName': org_name,
			'organisationAddress': org_addr,
			'organisationPhone': org_phone,
			'organisationEmail': org_email}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	if j['success'] == True:
		assert j['message'] in ["Organisation request sent", "Organisation re-activation request sent"]

# list organisation by super admin
def test_org_list(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/organisations'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list),type(j)
	for org in j:
		if org["organisationName"] ==  'test_org':
			pytest.organisation_id = org["organisationId"]

# approve organization by super admin
# @pytest.mark.parametrize('org_id',[(pytest.organisation_id)])
def test_org_approve(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/autographamt/approvals/organisations'
	data = {'organisationId':pytest.organisation_id,
			'verified':True
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	print(j)
	assert resp.status_code == 200, resp.text
	assert j['success'] == True, str(j)
	assert j['message'] == "Role Updated", str(j)

# create source
@pytest.mark.parametrize('languageCode,versionContentCode,versionContentDescription,year,revision,license',
	[('aaa','TST','For testing','2019','2','CC BY SA')])
def test_org_sourceCreate(supply_url,get_supAdmin_accessToken,languageCode,versionContentCode,versionContentDescription,year,revision,license):
	url = supply_url + '/v1/sources/bibles'
	data = {'languageCode':languageCode,
			'versionContentCode':versionContentCode,
			'versionContentDescription':versionContentDescription,
			'year':year,
			'revision': revision,
			'license' : license
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	if j['success'] == True:
		assert j['message'] == "Source Created successfully"
	else:
		assert j['message'] == "Source already exists"
		pytest.source_present = True

# list sources
def test_org_sourceGet(supply_url,get_supAdmin_accessToken):
	url = supply_url + '/v1/sources'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	for src in j:
		if src['language']['code'] == 'aaa' and src['version']['code'] == "TST": 
			pytest.source_id = src['source']['id']	
	if pytest.source_present:
		url = supply_url + "/v1/autographamt/source/activate"
		data = {'sourceId':pytest.source_id}
		resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
		j = json.loads(resp.text)
		assert j['success'] == True
		assert j['message'] == "Source re-activated."

# upload source
@pytest.mark.parametrize('usfm_text,json_obj',[(source_usfm,source_json)])
def test_org_sourceUpload(supply_url, usfm_text, json_obj):
	url = supply_url + "/v1/bibles/upload"
	data = {
	"sourceId": pytest.source_id,
	"wholeUsfmText":usfm_text,
	"parsedUsfmText":json.loads(json_obj)}
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	if not pytest.source_present:
		assert j['success'] == True, j
		assert j['message'] == "Inserted mrk into database", j['message']
	else:
		assert j['success'] == False
		assert j['message'] == "Book already Uploaded"

# create project
def test_org_projectCreate(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/organisations/projects'
	data = {
			'sourceId':pytest.source_id,
			'targetLanguageId':target_lang_id,
			'organisationId':pytest.organisation_id
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	if j['success'] == True:
		assert j['message'] in ["Project created","Activated the archived project"]

# list users
def test_org_userList(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/users'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200, resp.text
	assert isinstance(j,list), j
	for usr in j:
		if usr['lastName'] == 'translator':
			pytest.testuser2_userId =usr['userId']
		elif usr['firstName'] == 'admin':
			pytest.testuser1_userId = usr['userId']


# list projects 
def test_org_projectList(supply_url,get_admin_accessToken):
	url = supply_url + '/v1/autographamt/projects'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_admin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance(j,list)
	for proj in j:
		if proj['sourceId'] == pytest.source_id and proj['targetId']==target_lang_id and proj['organisationId']==pytest.organisation_id:
			pytest.project_id =  proj['projectId']


# assign project by testuser1 to testuser2
def test_org_projectAssign(supply_url):
	url = supply_url + '/v1/autographamt/projects/assignments'
	data = {'userId': pytest.testuser2_userId,
			'projectId': pytest.project_id,
			'books': ['mrk']
			}
	resp = requests.post(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == True
	assert j['message'] == "User Role Assigned"


#################### Translation ###################################

# project assignments
def test_translate_getAssignments(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/autographamt/projects/assignments/'+str(pytest.project_id)
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance(j,list)
	assert j[0]['user']['userId'] == pytest.testuser2_userId


# get assigned books 
def test_translate_getAssignedBooks(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/sources/projects/books/'+str(pytest.project_id)+"/"+str(pytest.testuser2_userId)
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j["mrk"]['assigned'] == True

# add translation
@pytest.mark.parametrize('token,trans',[(k,translations[k] ) for k in translations ])
def test_translate_updateToken(supply_url,get_translator_accessToken,token,trans):
	url = supply_url + '/v1/autographamt/projects/translations'
	data = {'token':token,
			'translation':trans,
			'projectId':pytest.project_id,
			'senses':[]
			}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	if j['success'] == True:
		assert j['message'] == "Translation has been inserted"
	else:
		assert j['message'] == "No New change. This data has already been saved"

# get tokens 
def test_translate_gettokenList(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/tokenlist/' + str(pytest.source_id) +'/mat'
	resp = requests.get(url,headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert isinstance(j,list)


# generate draft 
def test_translate_draft(supply_url,get_translator_accessToken):
	url = supply_url + '/v1/downloaddraft'
	data = { "projectId":pytest.project_id,
			"bookList":['mrk']}
	resp = requests.post(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_translator_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j["translatedUsfmText"]['mrk'] == expected_target


######################## Clean Up ###############################################

def test_delete_userAssignment(supply_url):
	url = supply_url + "/v1/autographamt/projects/assignments"
	data = { "userId":pytest.testuser2_userId,
				"projectId":pytest.project_id}
	resp = requests.delete(url,data=json.dumps(data))
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['success'] == True
	assert j['message'] == "User removed from Project"

# delete org & projects
def test_delete_project(supply_url,get_supAdmin_accessToken):
	url = supply_url + "/v1/autographamt/organisation/delete"
	data = {'organisationId':pytest.organisation_id}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "Deactivated organization and its projects."


# delete users
@pytest.mark.parametrize("userEmail",[(testuser2_email),(testuser1_email)])
def test_delete_user(supply_url,get_supAdmin_accessToken,userEmail):
	url = supply_url + "/v1/autographamt/user/delete"
	data = {'userEmail':userEmail}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "Deactivated user."

# delete source
def test_delete_sourceBible(supply_url,get_supAdmin_accessToken):
	url = supply_url + "/v1/autographamt/source/delete"
	data =  {"sourceId":pytest.source_id}
	resp = requests.delete(url,data=json.dumps(data),headers={'Authorization': 'bearer {}'.format(get_supAdmin_accessToken)})
	j = json.loads(resp.text)
	assert resp.status_code == 200
	assert j['message'] == "Source deactivated."

