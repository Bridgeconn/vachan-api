import pytest
import requests
import json
import re

@pytest.fixture
def supply_url():
	return "https://stagingapi.autographamt.com"

verificationCode_pattern = re.compile(r'/v1/verifications/([\w\d]+)')

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

@pytest.mark.parametrize("firstName,lastName,email, password,email_password",[('savitha','mark','savithamark.093@gmail.com',"1189",'shiny2mark')])
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