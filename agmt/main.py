##### Pylint Configurations #################
# For the complete list of pylint error messages, http://pylint-messages.wikidot.com/all-codes
# To disable pylint "Line too long (%s/%s)" error message.
# pylint: disable=C0301
# To disable too many modules error message.
# pylint: disable=C0302
# To disable Anomalous backslash in string: \'%s\'. String constant might be missing an r prefix.
# pylint: disable=W1401
# To disable missing module docstring error message.
# pylint: disable=C0111
# ##### Pylint Configurations ends here########

import os
import uuid
from functools import wraps
import datetime
from datetime import timedelta
import re
import json
import logging
import flask
from flask import Flask, request, session, redirect, jsonify, make_response
from flask import g
from flask_cors import CORS, cross_origin
import jwt
import requests
import scrypt
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from random import randint
import phrases
from functools import reduce
import traceback

logging.basicConfig(filename='API_logs.log', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

app = Flask(__name__)
CORS(app)

sendinblue_key = os.environ.get("AGMT_SENDINBLUE_KEY")
jwt_hs256_secret = os.environ.get("AGMT_HS256_SECRET", "x709myFlW5")
postgres_host = os.environ.get("AGMT_POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("AGMT_POSTGRES_PORT", "5432")
postgres_user = os.environ.get("AGMT_POSTGRES_USER", "postgres") #uday

postgres_password = os.environ.get("AGMT_POSTGRES_PASSWORD", "secret") # uday@123
postgres_database = os.environ.get("AGMT_POSTGRES_DATABASE", "postgres") # vachan
host_api_url = os.environ.get("AGMT_HOST_API_URL", "localhost:8000")
host_ui_url = os.environ.get("AGMT_HOST_UI_URL","autographamt.com")
system_email = os.environ.get("MTV2_EMAIL_ID", "autographamt@gmail.com")

def get_db():                                                                      #--------------To open database connection-------------------#
	"""Opens a new database connection if there is none yet for the
	current application context.
	"""
	if not hasattr(g, 'db'):
		g.db = psycopg2.connect(dbname=postgres_database, user=postgres_user,
			password=postgres_password,	host=postgres_host, port=postgres_port)
	return g.db

@app.teardown_appcontext                                              #-----------------Close database connection----------------#
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'db'):
		g.db.close()

def getLid(bcv):
	connection = get_db()
	cursor = connection.cursor()
	bcv = str(bcv)
	length = len(bcv)
	book = int(bcv[-length:-6])
	chapter = int(bcv[-6:-3])
	verse = int(bcv[-3:])
	cursor.execute("SELECT ID FROM bcv_lid_map WHERE Book = %s AND Chapter \
	= %s AND Verse = %s", (book, chapter, verse))
	lid_rst = cursor.fetchone()
	if lid_rst:
		lid = int(lid_rst[0])
	else:
		return 'Invalid BCV'
	cursor.close()
	return lid

def getBibleBookIds():
	'''
	Returns a tuple of two dictionarys of the books of the Bible, bookcode has bible book codes
	as the key and bookname has bible book names as the key.
	'''
	bookIdDict = {}
	connection  = get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT book_id, book_name, book_code FROM bible_books_look_up Order by book_id")
	rst = cursor.fetchall()
	for book_id, book_name, book_code in rst:
		bookIdDict[int(book_id)] = book_code
	cursor.close()
	return bookIdDict

# pass the URL with http, if URL will have SSL then will return the same otherwise wihtout SSL URL will return
def return_url(url):
	r = requests.get(url)
	required_url = r.url
	return required_url

@app.route('/', methods=['GET'])
def index():
 return jsonify({"message": "OK: I am live...url: http://autographamt.com/ "}), 200

@app.route("/v1/auth", methods=["POST"])                    #-------------------For login---------------------#
def auth():
	email = request.form["email"]
	password = request.form["password"]
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT email_id FROM autographamt_users WHERE  email_id = %s", (email,))
	est = cursor.fetchone()
	if not est:
		logging.warning('Unregistered user \'%s\' login attempt unsuccessful' % email)
		return '{"success":false, "message":"This email is not registered"}'
	cursor.execute("SELECT u.password_hash, u.password_salt, r.role_name, u.first_name, u.last_name,status FROM \
		autographamt_users u LEFT JOIN roles r ON u.role_id = r.role_id WHERE u.email_id = %s \
			and u.verified is True", (email,))
	rst = cursor.fetchone()
	if not rst:
		return '{"success":false, "message":"Email is not Verified"}'
	active = rst[5]
	if not active:
		return '{"success":false, "message":"User account is not active."}'
	password_hash = rst[0].hex()
	password_salt = bytes.fromhex(rst[1].hex())
	password_hash_new = scrypt.hash(password, password_salt).hex()
	role = rst[2]
	firstName = rst[3]
	lastName = rst[4]

	if password_hash == password_hash_new:
		try:
			access_token = jwt.encode({
				'sub': email,
				'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
				'role': role,
				'app':'mt',
				'firstName': firstName,
				'lastName': lastName
				}, jwt_hs256_secret, algorithm='HS256')
		except Exception as ex:
			print(ex)
			pass
		logging.warning('User: \'' + str(email) + '\' logged in successfully')
		return '{"accessToken": "%s"}\n' % (access_token.decode('utf-8'),)
	logging.warning('User: \'' + str(email) + '\' login attempt unsuccessful: Incorrect Password')
	return '{"success":false, "message":"Incorrect Password"}'

@app.route("/v1/registrations", methods=["POST"])       #-----------------For user registrations-----------------#
def new_registration():
	firstName = request.form['firstName']
	lastName = request.form['lastName']
	email = request.form['email']
	password = request.form['password']
	headers = {"api-key": sendinblue_key}
	url = "https://api.sendinblue.com/v2.0/email"
	verification_code = str(uuid.uuid4()).replace("-", "")
	documentation_url = return_url('http://docs.vachanengine.org/')
	body = '''Hello %s,<br/><br/>Thanks for your interest to use the AutographaMT web service. <br/>
	You need to confirm your email by opening this link:

	https://%s/v1/verifications/%s

	<br/><br/>The documentation for accessing the API is available at %s''' % \
			(firstName, host_api_url, verification_code, documentation_url)
	payload = {
		"to": {email: ""},
		"from": ["noreply@autographamt.in", "Autographa MT"],
		"subject": "AutographaMT - Please verify your email address",
		"html": body,
		}
	connection = get_db()
	password_salt = str(uuid.uuid4()).replace("-", "")
	password_hash = scrypt.hash(password, password_salt)
	cursor = connection.cursor()
	cursor.execute("SELECT user_id,status FROM autographamt_users WHERE email_id = %s", (email,))
	rst = cursor.fetchone()
	if not rst:
		cursor.execute("INSERT INTO autographamt_users (first_name, last_name, email_id, \
			verification_code, password_hash, password_salt, created_at_date,status) \
				VALUES (%s, %s, %s, %s, %s, %s, current_timestamp,true)", \
					(firstName, lastName, email, verification_code, password_hash, password_salt))
		cursor.close()
		connection.commit()
		resp = requests.post(url, data=json.dumps(payload), headers=headers)
		return '{"success":true, "message":"Verification Email has been sent to your email id"}'
	else:
		if rst[1] == False:
			return '{"success":false, "message":"This email has already been Registered. Account is deactivated. "}'
		else:
			return '{"success":false, "message":"This email has already been Registered, "}'

@app.route("/v1/resetpassword", methods=["POST"])    #-----------------For resetting the password------------------#
def reset_password():
	email = request.form['email']
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT email_id,status from autographamt_users WHERE email_id = %s", (email,))
	rst = cursor.fetchone()
	if not rst:
		return '{"success":false, "message":"Email has not yet been registered"}'
	else:
		active = rst[1]
		if not active:
			return '{"success":false, "message":"User account is deactivated."}'
		headers = {"api-key": sendinblue_key}
		url = "https://api.sendinblue.com/v2.0/email"
		# totp = pyotp.TOTP('base32secret3232')       # python otp module
		# verification_code = totp.now()
		verification_code = randint(100001,999999)
		documentation_url = return_url('http://docs.vachanengine.org/')
		body = '''Hi,<br/><br/>Your request for resetting the password has been recieved. <br/>
		Your temporary password is %s. Use this to create a new password at %s .

		<br/><br/>The documentation for accessing the API is available at %s''' % \
				(verification_code, host_ui_url, documentation_url)
		payload = {
			"to": {email: ""},
			"from": ["noreply@autographamt.in", "AutographaMT"],
			"subject": "AutographaMT - Password reset verification mail",
			"html": body,
			}
		cursor.execute("UPDATE autographamt_users SET verification_code= %s WHERE email_id = %s", \
			(verification_code, email))
		cursor.close()
		connection.commit()
		resp = requests.post(url, data=json.dumps(payload), headers=headers)
		return '{"success":true, "message":"Link to reset password has been sent to the registered mail ID"}\n'

@app.route("/v1/forgotpassword", methods=["POST"])    #--------------To set the new password-------------------#
def reset_password2():
	temp_password = request.form['temporaryPassword']
	password = request.form['password']
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT email_id FROM autographamt_users WHERE verification_code = %s \
		AND verified = True", (temp_password,))
	rst = cursor.fetchone()
	if not rst:
		return '{"success":false, "message":"Invalid temporary password."}'
	else:
		email = rst[0]
		password_salt = str(uuid.uuid4()).replace("-", "")
		password_hash = scrypt.hash(password, password_salt)
		cursor.execute("UPDATE autographamt_users SET verification_code = %s, password_hash = %s, \
			password_salt = %s WHERE email_id = %s", (temp_password, password_hash, password_salt, email))
		cursor.close()
		connection.commit()
		return '{"success":true, "message":"Password has been reset. Login with the new password."}'

class TokenError(Exception):

	def __init__(self, error, description, status_code=401, headers=None):
		self.error = error
		self.description = description
		self.status_code = status_code
		self.headers = headers

	def __repr__(self):
		return 'TokenError: %s' % self.error

	def __str__(self):
		return '%s. %s' % (self.error, self.description)

@app.errorhandler(TokenError)
def auth_exception_handler(error):
	return 'Authentication Failed\n', 401

def check_token(f):
	@wraps(f)
	def wrapper(*args, **kwds):
		auth_header_value = request.headers.get('Authorization', None)
		if not auth_header_value:
			raise TokenError('No Authorization header', 'Token missing')
		parts = auth_header_value.split()
		if (len(parts) == 2) and (parts[0].lower() == 'bearer'):
			# check for JWT token
			token = parts[1]
			options = {
				'verify_sub': True,
				'verify_exp': True,
				'verify_role': True
			}
			algorithm = 'HS256'
			leeway = timedelta(seconds=10)
			try:
				decoded = jwt.decode(token, jwt_hs256_secret, options=options, algorithms=[algorithm], leeway=leeway)
				request.email = decoded['sub']
				request.role = decoded['role']
				request.app = decoded['app']
			except jwt.exceptions.DecodeError as e:
				raise TokenError('Invalid token', str(e))
		else:
			raise TokenError('Invalid header', 'Token contains spaces')
		return f(*args, **kwds)
	return wrapper



@app.route("/v1/verifications/<code>", methods=["GET"])
def new_registration2(code):
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("SELECT email_id FROM autographamt_users WHERE verification_code = %s AND verified = False", (code,))
	if cursor.fetchone():
		cursor.execute("UPDATE autographamt_users SET verified = True WHERE verification_code = %s", (code,))
	cursor.close()
	connection.commit()
	return redirect("https://%s/" % (host_ui_url))

def checkAuth():
	email = request.email
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select role_id from autographamt_users where email_id=%s", (email,))
	roleId = cursor.fetchone()[0]
	cursor.close()
	return roleId


@app.route("/v1/autographamt/organisations", methods=["GET"])
@check_token
def autographamtOrganisations():
	try:
		role = checkAuth()
		connection = get_db()
		cursor = connection.cursor()
		email = request.email
		cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
		userId = cursor.fetchone()[0]
		if role == 3:
			connection = get_db()
			cursor = connection.cursor()
			cursor.execute("select organisation_id, organisation_name, organisation_address, \
				organisation_phone, organisation_email, verified, user_id, status from autographamt_organisations\
					order by organisation_id")
			rst = cursor.fetchall()
		elif role == 2:
			connection = get_db()
			cursor = connection.cursor()
			cursor.execute("select organisation_id, organisation_name, organisation_address, \
				organisation_phone, organisation_email, verified, user_id, status from autographamt_organisations\
					where user_id=%s and verified=true order by organisation_id", (userId,))
			rst = cursor.fetchall()
		else:
			return '{"success":false, "message":"UnAuthorized"}'
		cursor.close()
		if not rst:
			return '{"success":false, "message":"No organisation data available"}'
		organisationsList = [
			{
				"organisationId":organisationId,
				"organisationName":organisationName,
				"organisationAddress":organisationAddress,
				"organisationPhone":organisationPhone,
				"organisationEmail":organisationEmail,
				"verified":verified,
				"userId":userId,
				"active":status
			} for organisationId, organisationName, organisationAddress, organisationPhone, organisationEmail, verified, userId, status in rst
		]
		return json.dumps(organisationsList)
	except Exception as ex:
		print(ex)
		return '{"success":false, "message":"Server side error"}'

@app.route("/v1/autographamt/organisations", methods=["POST"])
@check_token
def createOrganisations():
	req = request.get_json(True)
	organisationName = req["organisationName"]
	organisationAddress = req["organisationAddress"]
	organisationPhone = req["organisationPhone"]
	organisationEmail = req["organisationEmail"]
	email = request.email
	try:
		connection = get_db()
		cursor = connection.cursor()

		cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
		userId = cursor.fetchone()[0]
		cursor.execute("select status from autographamt_organisations where organisation_name=%s and \
			organisation_email=%s", (organisationName, organisationEmail))
		rst = cursor.fetchone()
		if not rst:
			cursor.execute("insert into autographamt_organisations (organisation_name, \
				organisation_address, organisation_phone, organisation_email, user_id, status) values (%s,%s,%s,%s,%s,true) ", \
					(organisationName, organisationAddress, organisationPhone, organisationEmail, userId))
			connection.commit()
			cursor.close()
			return '{"success":true, "message":"Organisation request sent"}'
		else:
			status = rst[0]
			if status == False:
				cursor.execute("update autographamt_organisations set status=true, verified=false where organisation_name=%s and \
					organisation_email=%s", (organisationName, organisationEmail,))
				connection.commit()
				cursor.close()
				return '{"success":true, "message":"Organisation re-activation request sent"}'
			return '{"success":false, "message":"Organisation already created"}'
	except Exception as e:
		print(e)
		return json.dumps({'success':False,'message':'server error'})

@app.route("/v1/autographamt/users", methods=["GET"])
@check_token
def autographamtUsers():
	connection = get_db()
	cursor = connection.cursor()
	role = checkAuth()
	if role == 3:
		cursor.execute("select user_id, first_name, last_name, email_id, role_id, verified, status \
			from autographamt_users order by user_id")
	elif role == 2:
		cursor.execute("select user_id, first_name, last_name, email_id, role_id, verified, status \
			from autographamt_users where role_id < 3 order by user_id")
	else:
		cursor.close()
		return '{"success":false, "message":"UnAuthorized to view data"}'
	rst = cursor.fetchall()
	if not rst:
		return '{"success":false, "message":"No user data available"}'
	usersList = [
		{
			"userId":userId,
			"firstName":firstName,
			"lastName":lastName,
			"emailId":emailId,
			"roleId":roleId,
			"verified":verified,
			"active": status
		} for userId, firstName, lastName, emailId, roleId, verified, status in rst
	]
	# print(usersList)
	return json.dumps(usersList)

@app.route("/v1/autographamt/projects", methods=["GET"])
@check_token
def getProjects():
	try:
		connection = get_db()
		cursor = connection.cursor()
		role = checkAuth()
		if role == 2:
			email = request.email
			cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
			userId = cursor.fetchone()[0]
			cursor.execute("select organisation_id from autographamt_organisations where user_id=%s", (userId,))
			organisationIds = [org[0] for org in cursor.fetchall()]
			rst = []
			for orgId in organisationIds:
				cursor.execute("select p.project_id, p.project_name, p.source_id, p.target_id,  \
					p.organisation_id, o.organisation_name, v.version_code, v.version_description, p.status \
						from autographamt_projects p left join autographamt_organisations o on \
						p.organisation_id=o.organisation_id left join sources s on \
							s.source_id=p.source_id \
							left join versions v on s.version_id = v.version_id where p.organisation_id=%s", (orgId,))
				rst += cursor.fetchall()
		elif role == 3:
			cursor.execute("select p.project_id, p.project_name, p.source_id, p.target_id, \
				p.organisation_id, o.organisation_name, v.version_code, v.version_description, p.status \
					from autographamt_projects p left join autographamt_organisations o on \
					p.organisation_id=o.organisation_id left join sources s on \
							s.source_id=p.source_id left join versions v on s.version_id = v.version_id")
			rst = cursor.fetchall()
		else:
			return '{"success": false ,"message":"Not authorized"}'
		if not rst:
			'{"success":false, "message":"No projects created yet"}'
		projectsList = [
			{
				"projectId": projectId,
				"projectName": projectName,
				"sourceId": sourceId,
				"targetId": targetId,
				"organisationId": organisationId,
				"organisationName": organisationName,
				"version":{
					"name": verName,
					"code": verCode
				},
				"active": status
			} for projectId, projectName, sourceId, targetId, organisationId, organisationName, verCode, verName, status in rst
		]
		return json.dumps(projectsList)
	except Exception as ex:
		print(ex)
		return '{"success": false, "message":"Server side error"}'

@app.route("/v1/autographamt/organisations/projects", methods=["POST"])
@check_token
def createProjects():
	req = request.get_json(True)
	sourceId = req["sourceId"]
	targetLanguageId = req["targetLanguageId"]
	organisationId = req["organisationId"]
	role = checkAuth()
	try:
		if role > 1:
			connection = get_db()
			cursor = connection.cursor()
			cursor.execute("select l.language_name, l.language_code from sources s left join languages l on \
				s.language_id=l.language_id where source_id=%s", (sourceId,))
			sourceLanguage, sourceLanguageCode = cursor.fetchone()
			cursor.execute("select language_name, language_code from languages where language_id=%s", (targetLanguageId,))
			targetLanguage, targetLanguageCode = cursor.fetchone()
			projectName = sourceLanguage + '-to-' + targetLanguage + '|' + sourceLanguageCode + '-to-' + targetLanguageCode
			cursor.execute("select status from autographamt_projects where organisation_id=%s and source_id=%s and \
				target_id=%s", (organisationId, sourceId, targetLanguageId))
			rst = cursor.fetchone()
			if not rst:
				cursor.execute("insert into autographamt_projects (project_name, source_id, target_id, organisation_id, status) \
					values (%s,%s,%s,%s,true)", (projectName, sourceId, targetLanguageId, organisationId))
				connection.commit()
				cursor.close()
				return '{"success":true, "message":"Project created"}'
			else:
				status = rst[0]
				if status == False:
					cursor.execute("update autographamt_projects set status=true where organisation_id=%s and source_id=%s and \
						target_id=%s", (organisationId, sourceId, targetLanguageId))
					connection.commit()
					cursor.close()
					return '{"success":true, "message":"Activated the archived project"}'
				else:
					return '{"success":false, "message":"Project already created"}'
		else:
			return '{"success":false, "message":"UnAuthorized"}'

	except Exception as e:
		print(e)
		return '{"success":false, "message":"Server Error"}'

@app.route("/v1/autographamt/projects/assignments/<projectId>", methods=["GET"])
@check_token
def getAssignments(projectId):
	'''
	Returns an array of Users assigned under a project
	'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select u.first_name, u.last_name, u.email_id, a.assignment_id, \
			a.books, a.user_id, a.project_id, u.status from autographamt_assignments a \
			left join autographamt_users u on u.user_id=a.user_id where project_id=%s", (projectId,))
		rst = cursor.fetchall()
		if not rst:
			return json.dumps([])
		else:
			projectUsers = [
				{
					"assignmentId":assignmentId,
					"books":books.split("|"),
					"user":{
						"userName": firstName + " " + lastName,
						"userId": userId,
						"email": email
					},
					"projectId":projectId,
					"userActive":status,
				} for firstName, lastName, email, assignmentId, books, userId, projectId, status in rst
			]
			return json.dumps(projectUsers)

	except Exception as e:
		print(e)
		return json.dumps({'success':False,'message':"Server error"})

@app.route("/v1/autographamt/projects/assignments", methods=["POST"])
def createAssignments():
	req = request.get_json(True)
	userId = req["userId"]
	projectId = req["projectId"]
	books = req["books"]
	# action = req["action"]
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select * from autographamt_assignments where user_id=%s and project_id=%s", (
		userId, projectId
	))
	rst = cursor.fetchone()

	if not rst:

		books = "|".join(books)
		cursor.execute("insert into autographamt_assignments (books, user_id, project_id) \
			values (%s, %s, %s)", (books, userId, projectId))
		connection.commit()
		cursor.close()
		return '{"success":true, "message":"User Role Assigned"}'

	books = "|".join(books)
	cursor.execute("update autographamt_assignments set books=%s where user_id=%s and \
		project_id=%s", (books, userId, projectId))
	connection.commit()
	cursor.close()
	return '{"success":true, "message":"User Role Updated"}'

@app.route("/v1/autographamt/projects/assignments", methods=["DELETE"])
def removeUserFromProject():

	req = request.get_json(True)
	userId = req["userId"]
	projectId = req["projectId"]
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select * from autographamt_assignments where user_id=%s and project_id=%s", (
		userId, projectId
	))

	rst = cursor.fetchone()

	if not rst:
		return '{"success":false, "message":"User Role Does Not exist"}'
	else:
		cursor.execute("delete from autographamt_assignments where user_id=%s and project_id=%s", (
			userId, projectId
		))
		connection.commit()
		cursor.close()
		return '{"success": true, "message":"User removed from Project"}'

def convertStringToList(string):
	if string == "":
		array = []
	else:
		array = string.split("|")
	return array

@app.route("/v1/autographamt/projects/translations/<token>/<projectId>", methods=["GET"])
def getProjectTranslations(token, projectId):
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select t.translation, t.senses from translations t left join \
		translation_projects_look_up p on t.translation_id=p.translation_id where t.token=%s and \
			p.project_id=%s", (token, projectId))
	rst = cursor.fetchone()

	if rst:
		translation, senses = rst
		if senses.strip() == "":
			senses = []
		else:
			senses = senses.split('|')
		return json.dumps({
			"translation":translation,
			"senses":senses
		})
	else:
		return '{"success": false, "message":"No Translation or sense available for this token"}'

@app.route("/v1/autographamt/projects/translations", methods=["POST"])
@check_token
def updateProjectTokenTranslations():
	'''
	An AgMT API
	Adds/updates one token, its translation and senses to the DB
	'''
	try:
		req = request.get_json(True)
		projectId = req["projectId"]
		token = req["token"]
		translation = req["translation"]
		senses_list = req["senses"]
		if "" in senses_list:
			senses_list.remove("")
		senses = "|".join(senses_list)
		email = request.email
		# userId=6
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
		userId = cursor.fetchone()[0]
		cursor.execute("select assignment_id from autographamt_assignments where user_id=%s and \
			project_id=%s", (userId, projectId))
		assignmentExists = cursor.fetchone()
		if not assignmentExists:
			return '{"success":false, "message":"UnAuthorized/ You haven\'t been assigned this project"}'
		cursor.execute("select source_id, target_id from autographamt_projects where project_id=%s", (projectId,))
		sourceId, targetLanguageId = cursor.fetchone()
		cursor.execute("select language_code from languages where language_id=%s", (targetLanguageId,))
		targetLanguageCode = cursor.fetchone()
		if not targetLanguageCode:
			return '{"success":false, "message":"Target Language does not exist"}'
		cursor.execute("select * from sources where source_id=%s", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Source does not exist"}'
		cursor.execute("select t.token, t.translation, t.senses from translations t left join \
			translation_projects_look_up p on t.translation_id=p.translation_id where p.project_id=%s and \
			token=%s",(projectId, token))
		rst = cursor.fetchone()
		if not rst:
			cursor.execute("insert into translations (token, translation, source_id, target_id, \
				user_id, senses) values (%s, %s, %s, %s, %s, %s) returning translation_id", (token, translation, sourceId, targetLanguageId, \
					userId, senses))
			translationId = cursor.fetchone()[0]
			cursor.execute("insert into translation_projects_look_up (translation_id, project_id) values \
				(%s, %s)", (translationId, projectId))
			cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
				user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
					userId, senses))
			connection.commit()
			cursor.close()
			return '{"success":true, "message":"Translation has been inserted"}'
		else:
			if senses == rst[2] and translation == rst[1]:
				return '{"success":false, "message":"No New change. This data has already been saved"}'
			dbSenses = []
			if rst[2] != None or rst[2] != "":
				dbSenses = rst[2].split("|")
			for sense in senses_list:
				if sense not in dbSenses:
					dbSenses.append(senses)
			senses = "|".join(dbSenses)
			cursor.execute("update translations set translation=%s, user_id=%s, senses=%s where source_id=%s and \
				target_id=%s and token=%s",(translation, userId, senses, sourceId, targetLanguageId, token))
			cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
				user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
					userId, senses))
			connection.commit()
			cursor.close()
			return '{"success":true, "message":"Translation has been updated"}'
	except Exception as ex:
		print(ex)
		return '{"success": false, "message":"Server side error"}'


@app.route("/v1/autographamt/projects/bulktranslations", methods=["POST"])
@check_token
def bulkUpdateProjectTokenTranslations():
	'''
	An AgMT API
	Similar funtion as updateProjectTokenTranslations.
	Difference being it takes a 'list' of tokens, their
	translations and senses and add/update them to DB
	'''
	try:
		req = request.get_json(True)
		projectId = req["projectId"]
		tokenTranslations = req["tokenTranslations"]
		email = request.email
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
		userId = cursor.fetchone()[0]
		cursor.execute("select assignment_id from autographamt_assignments where user_id=%s and \
			project_id=%s", (userId, projectId))
		assignmentExists = cursor.fetchone()
		if not assignmentExists:
			return '{"success":false, "message":"UnAuthorized/ You haven\'t been assigned this project"}'
		cursor.execute("select source_id, target_id from autographamt_projects where project_id=%s", (projectId,))
		sourceId, targetLanguageId = cursor.fetchone()
		cursor.execute("select language_code from languages where language_id=%s", (targetLanguageId,))
		targetLanguageCode = cursor.fetchone()
		if not targetLanguageCode:
			return '{"success":false, "message":"Target Language does not exist"}'
		cursor.execute("select * from sources where source_id=%s", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Source does not exist"}'
		if not (tokenTranslations):
			return '{"success":false, "message":"There is no data in excel"}'
		warning = ''
		empty_translation = 0
		empty_senses = 0
		empty_tokenName = 0
		for item in tokenTranslations:
			if (("token" not in item) and ("translation" not in item) and ("senses" not in item)):  #if all fields are empty
				pass
			elif("token" not in item):  # if token is empty
				empty_tokenName += 1
			elif(("translation" not in item) and ("senses" in item) and ("token" in item)): # if translation is empty
				empty_translation += 1
			elif(("token" in item) and ("translation" not in item) and ("senses" not in item)): # if only token is available
				empty_senses += 1
				empty_translation += 1
			elif (("token" in item) and ("translation" in item) and ("senses" in item)):   #if all fields are filled
				token = item['token']
				translation = item['translation']
				senses = item['senses']
				logging.warning('senses \'%s\'' % senses)
				splitSense = senses.split(',')
				logging.warning('splitSense \'%s\'' % splitSense)
				if "" in splitSense:
					splitSense.remove("")
				cursor.execute("select t.token, t.translation, t.senses from translations t left join \
					translation_projects_look_up p on t.translation_id=p.translation_id where p.project_id=%s and \
					token=%s",(projectId, token))
				rst = cursor.fetchone()
				if not rst:
					senses = '|'.join(splitSense)
					cursor.execute("insert into translations (token, translation, source_id, target_id, \
						user_id, senses) values (%s, %s, %s, %s, %s, %s) returning translation_id", (token, translation, sourceId, targetLanguageId, \
							userId, senses))
					translationId = cursor.fetchone()[0]
					cursor.execute("insert into translation_projects_look_up (translation_id, project_id) values \
						(%s, %s)", (translationId, projectId))
					cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
						user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
							userId, senses))
				else:
					dbSenses = []
					if rst[2] != None or rst[2] != "":
							logging.warning('rst[2] \'%s\'' % rst[2])
							dbSenses = rst[2].split("|")
							logging.warning('dbSenses \'%s\'' % dbSenses)
					for sense in splitSense:
						if sense not in dbSenses:
							dbSenses.append(sense)
					senses = "|".join(dbSenses)
					cursor.execute("update translations set translation=%s, user_id=%s, senses=%s where source_id=%s and \
							target_id=%s and token=%s",(translation, userId, senses, sourceId, targetLanguageId, token))
					cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
							user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
								userId, senses))
			
			elif(("token" in item) and ("translation" in item) and ("senses" not in item)): # if only senses are not available
				empty_senses += 1
				token = item['token']
				translation = item['translation']
				cursor.execute("select t.token, t.translation from translations t left join \
					translation_projects_look_up p on t.translation_id=p.translation_id where p.project_id=%s and \
					token=%s",(projectId, token))
				rst = cursor.fetchone()
				if not rst:
					# senses = '|'.join(splitSense)
					cursor.execute("insert into translations (token, translation, source_id, target_id, \
						user_id) values (%s, %s, %s, %s, %s) returning translation_id", (token, translation, sourceId, targetLanguageId, \
							userId))
					translationId = cursor.fetchone()[0]
					cursor.execute("insert into translation_projects_look_up (translation_id, project_id) values \
						(%s, %s)", (translationId, projectId))
					cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
						user_id) values (%s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
							userId))
				else:
					# dbSenses = []
					# if rst[2] != "":
					# 		dbSenses = rst[2].split("|")
					# for sense in splitSense:
					# 	if sense not in dbSenses:
					# 		dbSenses.append(sense)
					# senses = "|".join(dbSenses)
					cursor.execute("update translations set translation=%s, user_id=%s where source_id=%s and \
							target_id=%s and token=%s",(translation, userId, sourceId, targetLanguageId, token))
					cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
							user_id) values (%s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
								userId))
			else:
				pass
		connection.commit()
		cursor.close()
		return '{"success":true, "message":"Translations have been added.\\nEmpty token(s)  '+str(empty_tokenName)+' \\nEmpty translation(s)  '+str(empty_translation)+'\\nEmpty sense(s)  '+str(empty_senses)+'"}'
	except Exception as ex:
		print(ex)
		logging.warning('bulktranslations exception \'%s\'' % ex)
		return '{"success": false, "message":"Server side error"}'


@app.route("/v1/autographamt/users/projects", methods=["GET"])
@check_token
def getUserProjects():
	connection = get_db()
	cursor = connection.cursor()
	email = request.email
	cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
	userId = cursor.fetchone()
	if not userId:
		cursor.close()
		return '{"success":false, "message":"Unregistered User"}'
	else:
		userId = userId[0]
		cursor.execute("select p.project_id, p.project_name, o.organisation_name, a.books, \
			p.source_id, p.target_id, v.version_code, v.version_description, v.revision, p.status \
				from autographamt_assignments a left join autographamt_projects p on \
					a.project_id=p.project_id left join autographamt_organisations o on \
						o.organisation_id=p.organisation_id left join sources s on \
							p.source_id=s.source_id left join versions v \
							on v.version_id=s.version_id where a.user_id=%s", (userId,))
		rst = cursor.fetchall()
		userProjects = [
			{
				"projectId": projectId,
				"projectName": projectName,
				"organisationName": organisationName,
				"books": convertStringToList(books),
				"sourceId":sourceId,
				"targetId": targetId,
				"version": {
					"name": verName,
					"code": verCode,
					"revision" : revision
				},
				"active":status
			} for projectId, projectName, organisationName, books, sourceId, targetId, verCode, verName, revision, status in rst
		]
		if userProjects == []:
			return '{"success":false, "message":"No projects assigned"}'
		else:
			return json.dumps(userProjects)


@app.route("/v1/autographamt/approvals/organisations", methods=["POST"])
@check_token
def organisationApprovals():
	try:
		req = request.get_json(True)
		organisationId = req["organisationId"]
		verified = req["verified"]
		role = checkAuth()
		if role == 3:
			connection = get_db()
			cursor = connection.cursor()
			cursor.execute("select o.user_id, u.role_id from autographamt_organisations o left join \
				autographamt_users u on o.user_id=u.user_id where o.organisation_id=%s", \
					(organisationId,))
			userId, roleId = cursor.fetchone()
			cursor.execute("update autographamt_organisations set verified=%s where \
				organisation_id=%s", (verified, organisationId))
			if roleId < 3:
				cursor.execute("update autographamt_users set role_id=2 where user_id=%s", (userId,))
			# cursor
			connection.commit()
			cursor.close()
			return '{"success":true, "message":"Role Updated"}'
		else:
			# cursor.close()
			return '{"success":false, "message":"Unauthorized"}'
	except Exception as ex:
		print(ex)
		return '{"success":false, "message":"Server error"}'

@app.route("/v1/autographamt/statistics/projects/<projectId>", methods=["GET"])
def getProjectStatistics(projectId):
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select s.table_name from sources s left join autographamt_projects p on \
			s.source_id=p.source_id where p.project_id=%s", (projectId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"sucess":false, "message":"Invalid project id"}'
		tableName = rst[0] + "_tokens"
		bookDict = {}
		cursor.execute("select book_id, book_name, book_code from bible_books_look_up")
		for b_id, b_name, b_code in cursor.fetchall():
			bookDict[b_id] = {
				"name": b_name,
				"code": b_code
			}
		cursor.execute("select book_id, token from " + tableName)
		bookWiseTokens = {}
		for book_id, token in cursor.fetchall():
			if book_id in bookWiseTokens:
				bookWiseTokens[book_id] = bookWiseTokens[book_id] + [token]
			else:
				bookWiseTokens[book_id] = [token]
		cursor.execute("select t.token from translations t left join translation_projects_look_up tl on \
			t.translation_id=tl.translation_id where tl.project_id=%s", (projectId,))
		translatedTokens = [item[0] for item in cursor.fetchall()]
		projectStatistics = {}
		cursor.close()
		pendingPercentageList = []
		completedPercentageList = []
		for key in bookWiseTokens.keys():
			bookCode = bookDict[key]["code"]
			bookName = bookDict[key]["name"]
			bookTokenList = bookWiseTokens[key]
			translatedTokensInBook = set(bookTokenList) & set(translatedTokens)
			unTranslatedTokenList = set(bookTokenList) - translatedTokensInBook
			pendingPercentage = float("{0:.2f}".format(len(unTranslatedTokenList) / len(bookTokenList) * 100))
			completedPercentage = float("{0:.2f}".format(len(translatedTokensInBook) / len(bookTokenList) * 100))
			pendingPercentageList.append(pendingPercentage)
			completedPercentageList.append(completedPercentage)
			projectStatistics[bookCode] = {
				"allTokensCount": len(bookTokenList),
				"translatedTokensCount": len(translatedTokensInBook),
				"completed": completedPercentage,
				"pending": pendingPercentage,
				"bookName": bookName,
			}
		if not projectStatistics:
			pendingTokensStatus = 0
			completedTokensStatus = 0
		else:
			pendingTokensStatus = float("{0:.2f}".format(reduce(lambda x, y: x + y, pendingPercentageList) / len(pendingPercentageList)))
			completedTokensStatus = float("{0:.2f}".format(reduce(lambda x, y: x + y, completedPercentageList) / len(completedPercentageList)))

		return json.dumps({
			"bookWiseData":projectStatistics,
			"projectData":{
				"pending": pendingTokensStatus,
				"completed": completedTokensStatus
			}
		})
	except Exception as ex:
		print(ex)
		return '{"success":false, "message":"Server side error"}'

@app.route("/v1/autographamt/approvals/users", methods=["POST"])
@check_token
def userApproval():
	req = request.get_json(True)
	userId = req["userId"]
	admin = req["admin"]
	if admin:
		roleId = 2
	else:
		roleId = 1
	role = checkAuth()
	if role > 1:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("update autographamt_users set role_id=%s where user_id=%s", (roleId, userId))
		connection.commit()
		cursor.close()
		return '{"success":true, "message":"Role Updated"}'
	else:
		return '{"success":false, "message":"Unauthorized"}'

@app.route("/v1/sources/books/<sourceId>", methods=["GET"])           #-------------------------To find available books and revision number----------------------#
@check_token
def available_books(sourceId):
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select table_name,content_type from sources as s left join content_types c on s.content_id=c.content_id where source_id=%s", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"No data available"}'
		tablename = rst[0]
		if rst[1] != 'bible':
			return json.dumps({'success':False,'message':"Source is "+rst[1]+" not Bible"})
		cursor.execute(sql.SQL("select l.book_code from {} as u left join bible_books_look_up as l \
			on u.book_id=l.book_id").format(sql.Identifier(tablename)))
		rst = cursor.fetchall()
		cursor.close()
		if not rst:
			return '{"success":false, "message":"No Books uploaded under this source"}'
		else:
			return json.dumps(rst)
	except Exception as e:
		print(e)
		return json.dumps({'success':False,'message':"Server error"})

@app.route("/v1/sources/projects/books/<projectId>/<userId>", methods=["GET"])           #-------------------------To find available books and revision number----------------------#
@check_token
def availableProjectBooks(projectId, userId):
	try:
		connection = get_db()
		cursor = connection.cursor()

		cursor.execute("select s.table_name from sources s left join autographamt_projects p on s.source_id=p.source_id \
			where p.project_id=%s", (projectId,))
		tablename = cursor.fetchone()[0]
		cursor.execute(sql.SQL("select l.book_code from {} as b join bible_books_look_up as l on b.book_id=l.book_id").format(sql.Identifier(tablename)))
		rst = cursor.fetchall()
		print("rst:",rst)
		if not rst:
			return '{"success":false, "message":"No Books uploaded under this source"}'
		allBooks = [t[0] for t in rst]
		try:
			cursor.execute("select books from autographamt_assignments where project_id=%s and user_id=%s", \
				(projectId, userId))
		except Exception as ex:
			print(ex)
			return '{"success":false, "message":"Server error. Unable to fetch books from project"}'
		assignedBooks = cursor.fetchone()
		if assignedBooks:
			assignedBooks = convertStringToList(assignedBooks[0])
		else:
			assignedBooks = []
		booksArray = {}

		for book in allBooks:
			if book not in assignedBooks:
				booksArray[book] = {
						"assigned":False
					}
		for aBook in assignedBooks:
			booksArray[aBook] = {
					"assigned":True
				}
		return json.dumps(booksArray)
	except Exception as ex1:
		print(ex1)
		return '{"success":false, "message":"Server side error"}'

@app.route("/v1/tokenlist/<sourceId>/<book>", methods=["GET"])
def getTokenLists(sourceId, book):
	print("comes to getTokenLists")
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	cursor.execute("select book_id from bible_books_look_up where book_code=%s", (book.lower(),))
	bookId = cursor.fetchone()[0]
	tablename = rst[0] + '_tokens'
	tablename_parts = tablename.split('_')
	languageCode = tablename_parts[0]
	version = '_'.join(tablename_parts[1:-2])
	cursor.execute(sql.SQL("select token from {} where book_id=%s").format(sql.Identifier(tablename)), (bookId,))
	tokenList = [item[0] for item in cursor.fetchall()]
	if len(tokenList)==0:
		try:
			print("comes here to tokenize")
			phrases.tokenize(connection, languageCode.lower(), version.lower() , bookId)
			cursor.execute("select token from " + tablename + " where book_id=%s", (bookId,))
			tokenList = [item[0] for item in cursor.fetchall()]
		except Exception as ex:
			print(ex)
			return '{"success":false, "message":"Phrases method error"}'

	cursor.close()
	jsonOut = json.dumps(tokenList)
	# print(jsonOut)
	return jsonOut

@app.route("/v1/tokentranslationlist/<projectId>/<book>", methods=["GET"])
@check_token
def getTokenTranslationList(projectId, book):
	'''
	This method is used to fetch all tokens in a selected book,
	associated with a project. If a translation is added for it, in that project,
	that will also be fetched.
	AUTH: Only accessible to a user who has been assigned that book in that project.
	INPUT: projectId and 3 letter bookCode(lower or upper cases accepted)
	OUTPUT FORMAT:
	[
	 ['token', null, null],
	 ['token', 'translation', null],
	 ['token', 'translation', 'senses1'],
	 ['token', 'translation', 'senses1,sense2'],
	 ['token', 'translation', null],
	 ['token', null, null],
	 ...
	]
	This format of array of arrays and comma seperated string for senses was chosen due to
	the requirement from UI side (the xlsx npm module)
	'''

	try:
		connection = get_db()
		cursor = connection.cursor()
		projectId = int(projectId)

		email = request.email
		cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
		userId = cursor.fetchone()[0]
		cursor.execute("select books from autographamt_assignments where user_id=%s and \
			project_id=%s", (userId, projectId))
		assignments = cursor.fetchone()
		if (not assignments) or (book.lower() not in assignments.split('|')):
			return '{"success":false, "message":"UnAuthorized! You haven\'t been assigned this book/project"}'

		cursor.execute("select s.table_name from sources as s join autographamt_projects as p \
		on s.source_id = p.source_id where p.project_id=%s", (projectId,))
		source_table = cursor.fetchone()[0]
		tablename = source_table + '_tokens'

		cursor.execute("select book_id from bible_books_look_up where book_code=%s", (book,))
		bookId_rst = cursor.fetchone()
		if not bookId_rst:
			return '{"success":false, "message":"Invalid book code. The 3 letter code expected."}'
		bookId = bookId_rst[0]
		cursor.execute(sql.SQL("SELECT s.token, t.translation, t.senses, l.project_id FROM {} s \
			LEFT JOIN translations t ON s.token = t.token \
			LEFT JOIN translation_projects_look_up l ON t.translation_id = l.translation_id \
			where s.book_id=%s;").format(sql.Identifier(tablename)), (bookId,))
		tokenList = [ ]
		for item in cursor.fetchall():
			if item[3] == projectId:
				senses = None
				if item[2]:
					senses = item[2].replace('|',',')
					if senses[-1] == ',':
						senses = senses[:-1]
				tokenList.append([item[0], item[1], senses])
			else:
				tokenList.append([item[0], None, None])
		if len(tokenList)==0:
			try:
				languageCode = source_table.split('_')[0]
				version = '_'.join(source_table.split('_')[1:3])
				phrases.tokenize(connection, languageCode.lower(), version.lower() , bookId)
				cursor.execute(sql.SQL("select token from {} where book_id=%s").format(sql.Identifier(tablename)), (bookId,))
				tokenList = [[item[0], None, None] for item in cursor.fetchall()]
			except Exception as ex:
				print(ex)
				return json.dumps({"success":False, "message":"Phrases method error"})
		if len(tokenList)==0:
			return json.dumps({"success":False, "message": "No tokens available. Check if bible books are uploaded."})
		cursor.close()
		jsonOut = json.dumps(tokenList)
		return jsonOut
	except Exception as e:
		print(e)
		return json.dumps({"success":False, "message": "Server side error"})

def getConcordanceList(db_data):
	concordance = []
	for bookCode, bookName, chapter, verse, text in db_data:
		obj = {
			"bookCode":bookCode,
			"book":bookName,
			"chapterNumber":chapter,
			"verseNumber":verse,
			"verse": text
		}
		concordance.append(obj)
	return concordance


@app.route("/v1/concordances/<sourceId>/<book>/<token>", methods=["GET"])
def generateConcordances(sourceId, book, token):
	connection = get_db()
	cursor = connection.cursor()
	book = book.lower()
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	tablename = cursor.fetchone()[0]+"_cleaned"
	# try:
	cursor.execute("select bb.book_code, bb.book_name, l.chapter, l.verse, b.verse from " + tablename + " b \
	left join bcv_map l on b.ref_id=l.ref_id left join bible_books_look_up bb on l.book=bb.book_id \
		where b.verse like '%" + token + "%' and bb.book_code='" + book +"' order by l.ref_id")
	book_concordance = getConcordanceList(cursor.fetchall())
	cursor.execute("select bb.book_code, bb.book_name, l.chapter, l.verse, b.verse from " + tablename + " b \
	left join bcv_map l on b.ref_id=l.ref_id left join bible_books_look_up bb on l.book=bb.book_id \
		where b.verse like '%" + token + "%' and bb.book_code!='" + book +"' order by l.ref_id \
			limit 100")
	all_books_concordance = getConcordanceList(cursor.fetchall())
	return json.dumps({
		book:book_concordance,
		"all":all_books_concordance
	})
	# except Exception as ex:
	#     return '{"success": false, "messsage":"%s"}' %(ex)


@app.route("/v1/contenttypes", methods=["GET"])
def getContentTypes():
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select c.content_type, c.content_id from sources s left join content_types c on \
		s.content_id=c.content_id")
	rst = cursor.fetchall()
	if not rst:
		return '{"success":false, "message":"There are no contents available"}'
	contentTypes = [{
		"contentType":contentType,
		"contentId": contentId
	} for contentType, contentId in rst]
	return json.dumps(contentTypes)

@app.route("/v1/languages/<contentId>", methods=["GET"])
def getLanguages(contentId):
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select distinct l.language_name, l.language_code, l.language_id from sources s \
		left join languages l on s.language_id=l.language_id where s.content_id=%s", (contentId,))
	rst = cursor.fetchall()
	if not rst:
		return '{"success":false, "message":"No languages available for this content"}'
	languages = [{
		"languageName": languageName,
		"languageCode": languageCode,
		"languageId": languageId
	} for languageName, languageCode, languageId in rst]
	return json.dumps(languages)


@app.route("/v1/languages", methods=["GET"])
def getAllLanguages():
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select language_id, language_name, language_code from languages order by language_name")
	rst = cursor.fetchall()
	allLanguagesData = [
		{
			"languageName": languagename,
			"languageId":languageid,
			"languageCode": languagecode
		} for languageid, languagename, languagecode in rst
	]
	cursor.close()
	return json.dumps(allLanguagesData)

@app.route("/v1/contentdetails", methods=["GET"])
def getContentDetails():
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select content_id, content_type from content_types")
	rst = cursor.fetchall()
	allContentTypeData = [
		{
			"contentId":contentId,
			"contentType":contentType
		} for contentId, contentType in rst
	]
	cursor.close()
	return json.dumps(allContentTypeData)


def parsePunctuations(text):
	content = re.sub(r'([!\"#$%&\\\'\(\)\*\+,\.\/:;<=>\?\@\[\]^_`{|\}~\”\“\‘\’।0123456789])',"",text)
	return content

def parsePunctuationsForDraft(text):
	content = re.sub(r'([!\"#$%&\\\'\(\)\*\+,\.\/:;<=>\?\@\[\]^_`{|\}~\”\“\‘\’।])',r" \1",text)
	return content

def parseDataForDBInsert(usfmData):
	connection = get_db()
	normalVersePattern = re.compile(r'\d+$')
	splitVersePattern = re.compile(r'(\d+)(\w)$')
	mergedVersePattern = re.compile(r'(\d+)-(\d+)$')
	cursor = connection.cursor()
	cursor.execute("select book_id, book_code from bible_books_look_up")
	bookIdDict = {v.lower():k for k,v in cursor.fetchall()}
	bookName = usfmData["metadata"]["id"]["book"].lower()
	chapterData = usfmData["chapters"]
	dbInsertData = []
	verseContent = []
	bookId = bookIdDict[bookName]
	for chapter in chapterData:
		chapterNumber = chapter["header"]["title"]
		verseData = chapter["verses"]
		for verse in verseData:
			crossRefs = ""
			footNotes = ""
			if 'metadata' in verse and 'cross-ref' in verse['metadata']:
				crossRefs = verse['metadata']['cross-ref']
			if 'metadata' in verse and 'footnote' in verse['metadata']:
				footNotes = verse['metadata']['footnote']
			verseNumber = verse['number'].strip()
			if normalVersePattern.match(verseNumber):
				verseText = verse["text"]
				dbVerseText = verseText
				bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
					+ str(verseNumber).zfill(3))
				ref_id = int(bcv)
				dbInsertData.append((ref_id, dbVerseText, crossRefs, footNotes))
				verseContent.append(verseText)
			elif splitVersePattern.match(verseNumber):
				## combine split verses and use the whole number verseNumber
				matchObj = splitVersePattern.match(verseNumber)
				postScript = matchObj.group(2)
				verseNumber = matchObj.group(1)
				if postScript == 'a':
					verseText = verse['text']
					dbVerseText = verseText
					bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
						+ str(verseNumber).zfill(3))
					ref_id = int(bcv)
					dbInsertData.append((ref_id, dbVerseText, crossRefs, footNotes))
					verseContent.append(verseText)
				else:
					prevdbInsertData = dbInsertData[-1]

					verseText = prevdbInsertData[1] + ' '+ verse['text']
					dbVerseText = verseText
					dbInsertData[-1] = (prevdbInsertData[0], dbVerseText, prevdbInsertData[2],prevdbInsertData[3])
					verseContent[-1] = verseText
			elif mergedVersePattern.match(verseNumber):
				## keep the whole text in first verseNumber of merged verses
				verseText = verse['text']
				dbVerseText = verseText
				matchObj = mergedVersePattern.match(verseNumber)
				verseNumber = matchObj.group(1)
				verseNumberend = matchObj.group(2)
				bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
					+ str(verseNumber).zfill(3))
				ref_id = int(bcv)
				dbInsertData.append((ref_id, dbVerseText, crossRefs, footNotes))
				verseContent.append(verseText)
				## add empty text in the rest of the verseNumber range
				for vnum in range(int(verseNumber)+1, int(verseNumberend)+1):
					bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
						+ str(vnum).zfill(3))
					ref_id = int(bcv)
					dbInsertData.append((ref_id, "", "", ""))
					verseContent.append('')

			else:
				print("!!!Unrecognized pattern in verse number!!!")
				print("verseNumber:",verse['number'])
	return dbInsertData

def createTableCommand(fields, tablename):
	command = 'CREATE TABLE %s (%s)' %(tablename, ', '.join(fields))
	return command


@app.route("/v1/sources/bibles", methods=["POST"])
def createBibleSource():
	try:
		req = request.get_json(True)
		language = req["languageCode"]
		versionContentCode = req["versionContentCode"]
		versionContentDescription = req["versionContentDescription"]
		year = req["year"]
		revision = req["revision"]
		license = req["license"]
		contentId = 1
		version = versionContentCode.lower() + '_' + str(revision)
		connection = get_db()
		cursor = connection.cursor()
		bibleTableName = "%s_%s_%s_bible" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
		cleanTableName = "%s_%s_%s_bible_cleaned" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
		tokenTableName = "%s_%s_%s_bible_tokens" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
		cursor.execute("select language_id from languages where language_code=%s", (language,))
		languageId = cursor.fetchone()[0]
		cursor.execute("select s.source_id from sources s left join languages l on \
			s.language_id=l.language_id left join content_types c on s.content_id=c.content_id \
				left join versions v on v.version_id=s.version_id \
				where l.language_code=%s and s.content_id=%s and v.version_code=%s and \
					v.version_description=%s and s.year=%s and v.revision=%s and \
						s.license=%s",(language, contentId, versionContentCode,
							versionContentDescription, year, version, license))
		rst = cursor.fetchone()
		if not rst:
			create_usfm_bible_table_command = createTableCommand(['book_id INT NOT NULL', 'usfm_text TEXT', \
				'json_text JSONB'], bibleTableName)
			create_clean_bible_table_command = createTableCommand(['ref_id INT NOT NULL', 'verse TEXT', \
				'cross_reference TEXT', 'foot_notes TEXT'], cleanTableName)
			create_token_bible_table_command = createTableCommand(['token_id BIGSERIAL PRIMARY KEY', \
				'book_id INT NOT NUll', 'token TEXT NOT NULL'], tokenTableName)
			cursor.execute(create_usfm_bible_table_command)
			cursor.execute(create_clean_bible_table_command)
			cursor.execute(create_token_bible_table_command)
			cur2 = connection.cursor()
			cur2.execute("select version_id from versions where version_code=%s and version_description=%s \
				and revision=%s",(versionContentCode,versionContentDescription,version,))
			rst2 = cur2.fetchone()
			if not rst2:
				cur2.execute("insert into versions(version_code,version_description,revision) values(%s,%s,%s) returning version_id",
						(versionContentCode,versionContentDescription,version,))
				rst2 = cur2.fetchone()
			version_id = rst2[0]
			cursor.execute('insert into sources (table_name, year, license, content_id, language_id, version_id,status) values \
				(%s, %s, %s, %s, %s, %s,true)', (bibleTableName, year, license, contentId, languageId,version_id,))
			connection.commit()
			cursor.close()
			return '{"success": true, "message":"Source Created successfully"}'
		else:
			cursor.close()
			return '{"success": false, "message":"Source already exists"}'
	except Exception as ex:
		print(ex)
		return '{"success":false, "message":"Server side error"}'

@app.route("/v1/bibles/upload", methods=["POST"])
def uploadSource():
	try:
		req = request.get_json(True)
		sourceId = req["sourceId"]
		wholeUsfmText = req["wholeUsfmText"]
		parsedUsfmText = req["parsedUsfmText"]
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select s.table_name from sources as s where s.source_id=%s", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"No source created"}'
		bibleTable = rst[0]
		bookCode = parsedUsfmText["metadata"]["id"]["book"].lower()
		cursor.execute("select book_id from bible_books_look_up where book_code=%s",(bookCode,))
		bookId = cursor.fetchone()[0]
		cursor.execute(sql.SQL("select * from {} where book_id=%s").format(sql.Identifier(bibleTable)),(bookId,))
		rst = cursor.fetchone()
		cursor.close()
		if rst:
			return '{"success":false, "message":"Book already Uploaded"}'
		parsedDbData = parseDataForDBInsert(parsedUsfmText)

		cleanTableName = bibleTable + "_cleaned"
		print(cleanTableName)
		cursor = connection.cursor()
		execute_values(cursor,sql.SQL('insert into {} (ref_id, verse, cross_reference, foot_notes) values %s').format(sql.Identifier(cleanTableName)),
			parsedDbData)
		print("added in ",cleanTableName)
		print("About to insert to ",bibleTable)
		usfmJson = str(json.dumps(parsedUsfmText))
		cursor.execute(sql.SQL('insert into {} (book_id,usfm_text,json_text) values (%s,%s,%s)').format(sql.Identifier(bibleTable)), (bookId, wholeUsfmText,usfmJson,))
		print("Added to ",bibleTable)
		connection.commit()
		cursor.close()
		return '{"success":true, "message":"Inserted %s into database"}' %(bookCode)
	except Exception as ex:
		print(ex)
		return '{"success": false, "message":"Server side error"}'


@app.route("/v1/updatetokentranslations", methods=["POST"])
def updateTokenTranslations():
	req = request.get_json(True)
	token = req["token"]
	translation = req["translation"]
	sourceId = req["sourceId"]
	targetLanguageId = req["targetLanguageId"]
	senses = req["senses"]

	userId = 2
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select language_code from languages where language_id=%s", (targetLanguageId,))
	targetLanguageCode = cursor.fetchone()
	if not targetLanguageCode:
		return '{"success":false, "message":"Target Language does not exist"}'
	cursor.execute("select * from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst:
		return '{"success":false, "message":"Source does not exist"}'
	cursor.execute("select token, translation, senses from translations where source_id=%s and \
		target_id=%s and token=%s",(sourceId, targetLanguageId, token))
	rst = cursor.fetchone()
	if not rst:
		# senses = "|".join(senses)
		cursor.execute("insert into translations (token, translation, source_id, target_id, \
			user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
				userId, senses))
		cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
			user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
				userId, senses))
		connection.commit()
		cursor.close()
		return '{"success":true, "message":"Translation has been inserted"}'
	else:
		if senses == rst[2] and translation == rst[1]:
			return '{"success":false, "message":"No New change. This data has already been saved"}'
		if senses != rst[2] and translation == rst[1]:
			senses = rst[2] + '|' + senses
		if senses == "" and translation != rst[1]:
			senses = rst[2]

		cursor.execute("update translations set translation=%s, user_id=%s, senses=%s where source_id=%s and \
			target_id=%s and token=%s",(translation, userId, senses, sourceId, targetLanguageId, token))
		cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
			user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
				userId, senses))
		connection.commit()
		cursor.close()
		return '{"success":true, "message":"Translation has been updated"}'


@app.route("/v1/info/translatedtokens", methods=["GET"])
@check_token
def getTransaltedTokensInfo():
	try:
		connection = get_db()
		cursor = connection.cursor()
		email = request.email
		cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
		userId = cursor.fetchone()[0]
		cursor.execute("select project_id from autographamt_assignments where user_id=%s", (userId,))
		projectIds = [p[0] for p in cursor.fetchall()]
		translationInfo = []
		for p_id in projectIds:
			cursor.execute("select distinct p.project_id, p.project_name, p.status from translation_projects_look_up \
				t left join autographamt_projects p on t.project_id=p.project_id where p.project_id=%s", \
					(p_id,))
			rst = cursor.fetchall()
			if rst:
				for projectId, projectName, status in rst:
					translationInfo.append({
						"projectId": projectId,
						"projectName": projectName,
						"projectActive":status
					})
		cursor.close()
		return json.dumps(translationInfo)
	except Exception as ex:
		print(ex)
		return '{"success":false, "message":"Server side issue"}'


@app.route("/v1/translatedbooks/<sourceId>/<targetId>", methods=["GET"])
def getTranslatedBooks(sourceId, targetId):
	connection = get_db()
	cursor = connection.cursor()
	# cursor.execute("select t.to_name from tokentranslationslookup t left join \
	#     languages l on t.language_id=l.language_id where l.language_id=%s \
	#         and t.source_id=%s", (targetId, sourceId))
	cursor.execute("select token, translation from translations where source_id=%s \
		and target_id=%s", (sourceId, targetId))
	tokenTranslations = {k:v for k, v in cursor.fetchall()}
	tokenList = list(tokenTranslations.keys())
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()[0]
	tableName = rst + "_tokens"
	#

	cursor.execute(sql.SQL("select b.book_code, t.token from {} t left join bible_books_look_up b on t.book_id=b.book_id").format(sql.Identifier(tableName)))
	rstAllTokens = cursor.fetchall()
	bookWiseTokens = {}
	for bookCode, token in rstAllTokens:
		if bookCode not in bookWiseTokens:
			bookWiseTokens[bookCode] = [token]
		else:
			# temp = bookWiseTokens[bookCode]
			bookWiseTokens[bookCode] = bookWiseTokens[bookCode] + [token]
			# bookWiseTokens[bookCode] = temp
	translatedBooks = []
	for key in bookWiseTokens.keys():
		checkCommonTokens = set(tokenList) & set(bookWiseTokens[key])
		if checkCommonTokens:
			translatedBooks.append(key)
	return json.dumps(translatedBooks)


# @app.route("/v1/downloaddraft", methods=["POST"])
# def downloadDraft():
#     req = request.get_json(True)
#     sourceId = req["sourceId"]
#     targetLanguageId = req["targetLanguageId"]
#     bookList = req["bookList"]
#     connection = get_db()
#     cursor = connection.cursor()
#     cursor.execute("select token, translation from translations where source_id=%s \
#         and target_id=%s", (sourceId, targetLanguageId))

#     rst = cursor.fetchall()
#     if rst:
#         cursor.execute("select book_id, book_code from bible_books_look_up where book_code=%s", (bookList[0],))
#         bookId, bookCode = cursor.fetchone()
#         tokenTranslatedDict = {k:v for k,v in rst}
#         cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
#         source_rst = cursor.fetchone()
#         usfmText = source_rst[0]['usfm'][bookCode]
#         markerPattern = re.compile(r'\\\w+')
#         usfmLineList = []
#         for line in usfmText.split('\n'):
#             usfmWordsList = []
#             for word in line.split():
#                 if re.match(markerPattern, word):
#                     usfmWordsList.append(word)
#                 else:
#                     parsePunct = parsePunctuationsForDraft(word)
#                     punctList = parsePunct.split(" ")
#                     parsedPunctList = []
#                     for item in punctList:
#                         parsedPunctList.append(tokenTranslatedDict.get(item, item))
#                     usfmWordsList.append("".join(parsedPunctList))
#             usfmLineList.append(" ".join(usfmWordsList))
#         translatedUsfmText = "\n".join(usfmLineList)
#         return json.dumps({
#             "translatedUsfmText": translatedUsfmText
#         })


@app.route("/v1/downloaddraft", methods=["POST"])
@check_token
def downloadDraft():
	req = request.get_json(True)
	projectId = req["projectId"]
	bookList = req["bookList"]
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select source_id from autographamt_projects where project_id=%s", (projectId,))
		sourceId = cursor.fetchone()[0]
		usfmMarker = re.compile(r'\\\w+\d?\*?\s?')
		nonLangComponentsTwoSpaces = re.compile(r'\s[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]\s')
		nonLangComponentsTrailingSpace = re.compile(r'[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]\s')
		nonLangComponentsFrontSpace = re.compile(r'\s[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]')
		nonLangComponents = re.compile(r'[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]')

		if phrases.loadPhraseTranslations(connection, projectId):

			cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
			tablename = cursor.fetchone()[0]
			# bookList = ",".join(bookList)
			cursor.execute(sql.SQL("select usfm_text,book_code from {} bb \
					left join bible_books_look_up bl on bb.book_id=bl.book_id \
					where bl.book_code = ANY(%s::text[])").format(sql.Identifier(tablename)),('{'+",".join(bookList)+'}',))
			source_rst = cursor.fetchall()
			# print(source_rst)

			# usfmText = source_rst[0]['usfm'][bookCode]
			finalDraftDict = {}
			for row in source_rst:
				usfm_text = row[0]
				book = row[1]
				usfmLineList = []
				for line in usfm_text.split('\n'):
					usfmWordsList = []
					nonLangCompsTwoSpaces = []
					nonLangCompsTrailingSpace = []
					nonLangCompsFrontSpace = []
					nonLangComps = []
					markers_in_line = re.findall(usfmMarker,line)
					translated_seq = []
					for word_seq in re.split(usfmMarker,line):
						nonLangCompsTwoSpaces += re.findall(nonLangComponentsTwoSpaces,word_seq)
						clean_word_seq = re.sub(nonLangComponentsTwoSpaces,' uuuQQQuuu ',word_seq)
						nonLangCompsTrailingSpace += re.findall(nonLangComponentsTrailingSpace,clean_word_seq)
						clean_word_seq = re.sub(nonLangComponentsTrailingSpace,' QQQuuu ',clean_word_seq)
						nonLangCompsFrontSpace += re.findall(nonLangComponentsFrontSpace,clean_word_seq)
						clean_word_seq = re.sub(nonLangComponentsFrontSpace,' uuuQQQ ',clean_word_seq)
						nonLangComps += re.findall(nonLangComponents,clean_word_seq)
						clean_word_seq = re.sub(nonLangComponents,' QQQ ',clean_word_seq)
						if not re.match(r'\s+$',clean_word_seq) and clean_word_seq!='':
							translated_seq.append(phrases.translateText( clean_word_seq ))

					for i,marker in enumerate(markers_in_line):
						usfmWordsList.append(marker)
						if i<len(translated_seq):
							usfmWordsList.append(translated_seq[i])
					if i+1<len(translated_seq):
						usfmWordsList += translated_seq[i+1:]
					outputLine = " ".join(usfmWordsList)
					if 'bdit' in outputLine:
						print('translated_seq:',translated_seq)
						print(nonLangComps,nonLangCompsFrontSpace,nonLangCompsTrailingSpace,nonLangCompsTwoSpaces)
					for comp in nonLangCompsTwoSpaces:
						outputLine = re.sub(r' uuuQQQuuu '," "+comp+" ",outputLine,1)
					for comp in nonLangCompsTrailingSpace:
						outputLine = re.sub(r' QQQuuu ',comp+" ",outputLine,1)
					for comp in nonLangCompsFrontSpace:
						outputLine = re.sub(r' uuuQQQ '," "+comp,outputLine,1)
					for comp in nonLangComps:
						outputLine = re.sub(r' QQQ ',comp,outputLine,1)
					outputLine = re.sub(r'\s+',' ',outputLine)
					# print(outputLine)

					usfmLineList.append(outputLine)
				translatedUsfmText = "\n".join(usfmLineList)
				finalDraftDict[book] = translatedUsfmText
			return json.dumps({
				"translatedUsfmText": finalDraftDict
			})
		else:
			return '{"success": false, "message":"No translation available"}'
	except Exception as e:
		print(e)
		print("line:",line)
		print(marker,'of',markers_in_line)
		print('usfmWordsList:',usfmWordsList)
		print('translated_seq:',translated_seq)
		print('word_seq:',word_seq)
		print('clean_word_seq:',clean_word_seq)
		return json.dumps({'success':False, 'message':"Server error"})


@app.route("/v1/translationshelps/words/<sourceId>/<token>", methods=["GET"])
def getTranslationWords(sourceId, token):
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select l.language_code from sources s left join languages l \
		on s.language_id=l.language_id where s.source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst:
		return '{"success":false, "message":"Invalid source ID"}'
	tableName = "%s_translation_words" %(rst[0])
	try:
		cursor.execute("select keyword, wordforms, strongs, definition, translationhelp \
			from " + tableName + " where wordforms like '%" + token + "%'")
		tW = cursor.fetchall()
	except:
		return '{"success":false, "message":"No Translation Words available"}'
	#
	if tW:
		translationWord = {}
		for keyword, wordforms, strongs, definition, translationhelp in tW:
			translationWord["keyword"] = keyword
			translationWord["wordforms"] = wordforms
			translationWord["strongs"] = strongs
			translationWord["definition"] = definition
			translationWord["translationhelp"] = translationhelp
			break
		return json.dumps(translationWord)
	else:
		return '{"success":false, "message":"No data"}'

@app.route("/v1/translations/<sourceId>/<targetLanguageId>/<token>", methods=["GET"])
def getTranslatedWords(sourceId, targetLanguageId, token):
	connection = get_db()
	cursor = connection.cursor()

	cursor.execute("select translation, senses from translations where source_id=%s \
		and target_id=%s and token=%s", (sourceId, targetLanguageId, token))
	rst = cursor.fetchone()

	if rst:
		translation, senses = rst
		print(senses)
		if senses != None:
			if senses.strip() == "":
				senses = []
			else:
				senses = senses.split('|')
		return json.dumps({
			"translation":translation,
			"senses":senses
		})
	else:
		return '{"success": false, "message":"No Translation or sense available for this token"}'

@app.route("/v1/translations/<sourceId>/<targetLanguageId>", methods=["GET"])
def getAllTranslatedWords(sourceId, targetLanguageId):
	connection = get_db()
	cursor = connection.cursor()

	cursor.execute("select token,translation, senses from translations where source_id=%s \
		and target_id=%s", (sourceId, targetLanguageId))
	rst = cursor.fetchall()
	print(rst)

	if rst:
		result = []
		for item in rst:
			token,translation, senses = item
			print(senses)
			if senses.strip() == "":
				senses = []
			else:
				senses = senses.split('|')
			result.append({
				"token": token,
				"translation":translation,
				"senses":senses
			})
		return json.dumps(result)
	else:
		return '{"success": false, "message":"No Token Translations or senses available for this language pair"}'


# @app.route("/v1/sources/")

@app.route('/v1/sources/<sourceid>/<outputtype>', methods=["GET"], defaults={'bookid':None})
@app.route('/v1/sources/<sourceid>/<outputtype>/<bookid>', methods=["GET"])
def getbookText(sourceid, outputtype, bookid):
	try:
		connection = get_db()
		cursor = connection.cursor()
		outputtype = outputtype.lower()
		bookIdDict = getBibleBookIds()
		cursor.execute("select table_name from sources where source_id=%s and status=true", (sourceid,))
		rst = cursor.fetchone()
		if not rst:
			return json.dumps({'success':False,'message':'Source not present.'})

		tableName = rst[0]
		returnObj = {}
		if bookid:
			cursor.execute(sql.SQL("select usfm_text, json_text from {} where book_id=%s").format(sql.Identifier(tableName)),(bookid,))
			sourceContent = cursor.fetchone()
			bookCode = (bookIdDict[int(bookid)]).lower()
			if not sourceContent:
				return json.dumps({'success':False,'message':'Book has not been uploaded in the source.'})
			if outputtype == 'usfm':
				returnObj[bookCode] = sourceContent[0]
			elif outputtype == 'json':
				returnObj[bookCode] = sourceContent[1]
			else:
				return json.dumps({'success':False,'message':'Unsupported type. Use "usfm" or "json"'})
		else:
			cursor.execute(sql.SQL("select book_id,usfm_text, json_text from {}").format(sql.Identifier(tableName)))
			sourceContents = cursor.fetchall()
			if not sourceContents:
				return json.dumps({'success':False,'message':'Book has not been uploaded in the source.'})
			if outputtype == 'usfm':
				for row in sourceContents:
					returnObj[row[0]] = row[1]
			elif outputtype == 'json':
				for row in sourceContents:
					bookCode = (bookIdDict[int(row[0])]).lower()
					returnObj[bookCode] = row[2]
			else:
				return json.dumps({'success':False,'message':'Unsupported type. Use "usfm" or "json"'})

		return json.dumps(returnObj)
	except Exception as e:
		print(e)
		return json.dumps({'success':False,'message':'Server error'})


@app.route('/v1/sources/<sourceid>/<outputtype>/<bookid>/<chapterid>', methods=["GET"])
def getVerseInRange(sourceid, outputtype, bookid, chapterid):
	try:
		pass
		connection = get_db()
		cursor = connection.cursor()
		outputtype = outputtype.lower()

		cursor.execute("select table_name from sources where source_id=%s", (sourceid,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Source File not available. Create source"}'

		if outputtype == "clean":
			tablename = rst[0] + '_cleaned'
			cursor.execute(sql.SQL("select b.book_code, b.book_id, b.book_name,bcv.chapter,bcv.verse, t.verse from {} \
				 t left join bcv_map bcv on t.ref_id=bcv.ref_id left join \
					 bible_books_look_up b on b.book_id=bcv.book where bcv.book=%s \
						 and bcv.chapter=%s order by bcv.ref_id").format(sql.Identifier(tablename)), (int(bookid), int(chapterid)))
			cleanedText = cursor.fetchall()
			cleanedText = [{
				"bookId":bookId,
				"bookName": bookName,
				"bookCode": bookCode,
				"chapter":chapter,
				"verse":verse,
				"text": text
			} for  bookCode, bookId, bookName,chapter,verse, text in cleanedText]
			return json.dumps(cleanedText)
		elif outputtype == "json":
			tablename = rst[0]
			cursor.execute(sql.SQL("select json_text from {} where book_id=%s").format(sql.Identifier(tablename)),(bookid,))
			rst2 = cursor.fetchone()
			if not rst2:
				return '{"success":false, "message":"Book not available"}'
			booksIdDict = getBibleBookIds()
			bookCode = (booksIdDict[int(bookid)]).lower()
			jsonContent = rst2[0]

			chapterContent = jsonContent["chapters"]
			chapterContent = chapterContent[int(chapterid) -1]
			return json.dumps(chapterContent)
		else:
			'{"success":false, "message":"Invalid type. Use either `clean` or `json`"}'
	except Exception as e:
		print(e)
		return json.dumps({'success':False,'message':'Server error'})

@app.route("/v1/autographamt/user/delete",methods=["DELETE"])
@check_token
def removeUser():
	req = request.get_json(True)
	userEmail = req["userEmail"]
	role = checkAuth()
	connection = get_db()
	cursor = connection.cursor()
	message = ""
	success = False
	try:
		if role == 3:
		  # delete from user table
			cursor.execute("select user_id from autographamt_users where email_id=%s",(userEmail,))
			userId = cursor.fetchone()
			if userId:
				status = json.loads(deleteUser(userId))
				message += status['message']
				success = status['success']
			else:
				message += "User not present."
			connection.commit()
		else:
			message += "UnAuthorized! Only a super admin can delete users."
	except Exception as e:
		print(e)
		message = "Server error."
	return json.dumps({"success":success,"message":message})

@app.route("/v1/autographamt/user/activate",methods=["POST"])
@check_token
def activateUser():
	req = request.get_json(True)
	userEmail = req["userEmail"]
	role = checkAuth()
	connection = get_db()
	cursor = connection.cursor()
	message = ""
	success = False
	try:
		if role == 3:
			cursor.execute("select user_id,status from autographamt_users where email_id=%s",(userEmail,))
			row = cursor.fetchone()
			if row:
				userId = row[0]
				status = row[1]
				if status==True:
					message = "User account already active."
				else:
					cursor.execute("update autographamt_users set status=true where email_id=%s",(userEmail,))
					connection.commit()
					success = True
					message = "User re-activated"
			else:
				message = "User not present."
			connection.commit()
		else:
			message += "UnAuthorized! Only a super admin can actiavte user accounts."
	except Exception as e:
		print(e)
		message = "Server error."
	return json.dumps({"success":success,"message":message})

@app.route("/v1/autographamt/organisation/delete",methods=["DELETE"])
@check_token
def removeOrg():
	req = request.get_json(True)
	orgId= req["organisationId"]
	role = checkAuth()
	connection = get_db()
	cursor = connection.cursor()
	message = ""
	success = False
	try:
		if role == 3:
			# delete organization
			cursor.execute("select organisation_id from autographamt_organisations where organisation_id=%s",(orgId,))
			org = cursor.fetchone()
			if org:
				status = json.loads(deleteOrganisation(orgId))
				message += status['message']
				success = status['success']
			else:
				message += "Organisation not present."
		else:
			message += "UnAuthorized! Only a super admin can delete organizations."
	except Exception as e:
		print(e)
		message = "Server error."
	return json.dumps({"success":success,"message":message})

@app.route("/v1/autographamt/organisation/activate",methods=["POST"])
@check_token
def activateOrg():
	req = request.get_json(True)
	orgId= req["organisationId"]
	role = checkAuth()
	connection = get_db()
	cursor = connection.cursor()
	message = ""
	success = False
	try:
		if role == 3:
			# delete organization
			cursor.execute("select organisation_id,status from autographamt_organisations where organisation_id=%s",(orgId,))
			row = cursor.fetchone()
			if row:
				status = row[1]
				if status==False:
					cursor.execute("update autographamt_organisations set status=true where organisation_id=%s",(orgId,))
					connection.commit()
					success = True
					message = "Organisation re-activated."
				else:
					message = "Organisation already active"
			else:
				message = "Organisation not present."
		else:
			message += "UnAuthorized! Only a super admin can activate organizations."
	except Exception as e:
		print(e)
		message = "Server error."
	return json.dumps({"success":success,"message":message})


@app.route("/v1/autographamt/project/delete",methods=["DELETE"])
@check_token
def removeProject():
	req = request.get_json(True)
	projectId = req["projectId"]
	role = checkAuth()
	email = request.email
	connection = get_db()
	cursor = connection.cursor()
	message = ""
	success = False
	try:
		if role == 3:
				cursor.execute("select * from autographamt_projects where project_id=%s",(projectId,))
				project = cursor.fetchone()
				if project:
					status = json.loads(deleteProject(projectId))
					message += status["message"]
					success = status["success"]
				else:
					message += "Project not present."
		elif role == 2:
			cursor.execute("select user_id from autographamt_users where email_id=%s",(email,))
			userId = cursor.fetchone()[0]
			cursor.execute("select organisation_id from autographamt_organisations where user_id=%s",(userId,))
			orgIds = cursor.fetchall()
			orgIds = [row[0] for row in orgIds]
			if orgIds:
				cursor.execute("select * from autographamt_projects where project_id=%s and organisation_id= ANY(%s::int[])",(projectId,'{'+','.join(str(n) for n in orgIds)+'}',))
				project = cursor.fetchone()
				if project:
					status = json.loads(deleteProject(projectId))
					message += status["message"]
					success = status["success"]
				else:
					message += "Project not present in the organisation."
			else:
				message += "UnAuthorized! Organisation admin can delete projects of his/her organisation only."
		else:
			message += "UnAuthorized! Only the organisation admin or super admin can delete projects."
	except Exception as e:
		print(e)
		message = "Server error."
	return json.dumps({"success":success,"message":message})

@app.route("/v1/autographamt/project/activate",methods=["POST"])
@check_token
def activateProject():
	req = request.get_json(True)
	projectId = req["projectId"]
	role = checkAuth()
	email = request.email
	connection = get_db()
	cursor = connection.cursor()
	message = ""
	success = False
	try:
		if role == 3:
				cursor.execute("select status from autographamt_projects where project_id=%s",(projectId,))
				row = cursor.fetchone()
				if row:
					status = row[0]
					if status == False:
						cursor.execute('update autographamt_projects set status=true where project_id=%s',(projectId,))
						connection.commit()
						message = "Project re-activated"
						success = True
					else:
						message = "Project already active."
				else:
					message = "Project not present."
		elif role == 2:
			cursor.execute("select user_id from autographamt_users where email_id=%s",(email,))
			userId = cursor.fetchone()[0]
			cursor.execute("select organisation_id from autographamt_organisations where user_id=%s",(userId,))
			orgIds = cursor.fetchall()
			orgIds = [row[0] for row in orgIds]
			if orgIds:
				cursor.execute("select status from autographamt_projects where project_id=%s and organisation_id= ANY(%s::int[])",(projectId,'{'+','.join(str(n) for n in orgIds)+'}',))
				row = cursor.fetchone()
				if row:
					status = row[0]
					if status == False:
						cursor.execute('update autographamt_projects set status=true where project_id=%s',(projectId,))
						connection.commit()
						message = "Project re-activated"
						success = True
					else:
						message = "Project already active."
				else:
					message = "Project not present in the organisation."
			else:
				message = "UnAuthorized! Organisation admin can delete projects of his/her organisation only."
		else:
			message += "UnAuthorized! Only the organisation admin or super admin can delete projects."
	except Exception as e:
		print(e)
		message = "Server error."
	return json.dumps({"success":success,"message":message})

@app.route("/v1/autographamt/source/delete",methods=["DELETE"])
@check_token
def removeSource():
	req = request.get_json(True)
	sourceId = req["sourceId"]
	role = checkAuth()
	if role == 3:
		status = delete_source(sourceId)
		return json.dumps(status)
	else:
		return json.dumps({"success":False,"message":"Unauthorized attempt"})

@app.route("/v1/autographamt/source/activate",methods=["POST"])
@check_token
def activateSource():
	req = request.get_json(True)
	sourceId = req["sourceId"]
	role = checkAuth()
	connection = get_db()
	cursor = connection.cursor()
	if role == 3:
		cursor.execute("select status from sources where source_id=%s",(sourceId,))
		row = cursor.fetchone()
		if row:
			status = row[0]
			if status==False:
				cursor.execute("update sources set status=true where source_id=%s",(sourceId,))
				connection.commit()
				return json.dumps({'success':True,'message':"Source re-activated."})
			else:
				return json.dumps({'success':False,'message':"Source already active."})
		else:
			return json.dumps({'success':False,'message':"Source not present."})

	else:
		return json.dumps({"success":False,"message":"Unauthorized attempt"})


def deleteUser(userId):
	connection = get_db()
	cursor = connection.cursor()
	success = False
	message = ""
	try:
		cursor.execute("select role_id from autographamt_users where user_id=%s",(userId,))
		role = cursor.fetchone()
		if role==3:
			message += "Super admin user cannot be removed."
			return json.dumps({'success':success,'message':message})
		elif role==2:
			cursor.execute("select organisation_id from autographamt_organisations where user_id=%s",(userId,))
			orgIds = cursor.fetchall()
			if len(orgIds)>0:
				message = "Organisation admin cannot be deleted. Delete the organisation first."
				return json.dumps({'success':success,'message':message})
		cursor.execute("select * from autographamt_assignments where user_id=%s",(userId,))
		rst = cursor.fetchone()
		if rst:
			message += "User has translation assignments."
			return json.dumps({'success':success,'message':message})
		cursor.execute("update autographamt_users set status=false where user_id=%s",(userId,))
		connection.commit()
		success = True
		message = "Deactivated user."
	except Exception as e:
		print(e)
		message += "Server error."
	return json.dumps({'success':success,'message':message})



def deleteOrganisation(orgId):
	connection = get_db()
	cursor = connection.cursor()
	success = False
	message = ""
	try:
		cursor.execute("select project_id from autographamt_projects where organisation_id=%s",(orgId,))
		projectIds = cursor.fetchall()
		for projectId in projectIds:
			status = json.loads(deleteProject(projectId))
			if status["success"] == False:
				message = status["message"]
				return json.dumps({'success':success,'message':message})
		cursor.execute("update autographamt_organisations set status=false where organisation_id=%s",(orgId,))
		success = True
		message = "Deactivated organization and its projects."
		connection.commit()
	except Exception as e:
		print(e)
		message = "server error"
	return json.dumps({'success':success,'message':message})


def deleteProject(projectId):
	connection = get_db()
	cursor = connection.cursor()
	success = False
	message = ""
	try:
		cursor.execute("update autographamt_projects set status=false where project_id=%s",(projectId,))
		message += "Deactivated project."
		success = True
		connection.commit()
	except Exception as e:
		print(e)
		message = "Server error"
	return json.dumps({'success':success,'message':message})


def delete_source(source_id):
	connection = get_db()
	cursor = connection.cursor()
	success = False
	message = ""
	try:
		cursor.execute("select status from sources where source_id=%s",(source_id,))
		row = cursor.fetchone()
		if row:
			status = row[0]
			if status==True:
				cursor.execute("select project_name from autographamt_projects where source_id=%s and status=true",(source_id,))
				rows = cursor.fetchall()
				print(rows)
				if not rows:
					cursor.execute("update sources set status=false where source_id=%s",(source_id,))
					connection.commit()
					return {"success":True, "message":"Source deactivated."}
				else:
					return {"success":False,"message":"Source is being used in project(s):"+','.join([r[0] for r in rows])}
			else:
				return {"success":False,"message":"Source is already deactivated."}
		else:
			return {"success":False,"message":"Source not present."}
	except Exception as e:
		print(e)
		return {"success":False,"message":"server side error"}


#####################################################
# VACHAN API
#####################################################

def sourcesPattern(*argv):
	languageName, languageCode, languageId, contentType, contentId, sourceId, \
		versionCode, versionName, status = argv
	pattern = {
		"language":{
			"name": languageName.capitalize(),
			"code": languageCode,
			"id": languageId
		},
		"resources":{
			"type": contentType.capitalize(),
			"id": contentId,
		},
		"source":{
			"id": sourceId
		},
		"version": {
			"code": versionCode,
			"name": versionName
		},
		"status": status
	}
	return pattern

@app.route("/v1/sources", methods=["GET"])
def getSources():
	'''
	For a complete download of all content types stored in the database
	'''
	connection = get_db()
	cursor = connection.cursor()
	try:
		cursor.execute("select s.source_id, v.version_code, v.version_description, c.content_id, \
			c.content_type, l.language_id, l.language_name, l.language_code, s.status from sources s\
				left join content_types c on s.content_id=c.content_id left join languages l on \
					s.language_id=l.language_id left join versions v on s.version_id=v.version_id")
	except Exception as ex:
		print(ex)
	sourcesList = []
	for s_id, ver_code, ver_name, cont_id, cont_name, lang_id, lang_name, lang_code,status in cursor.fetchall():
		sourcesList.append(
			sourcesPattern(lang_name, lang_code, lang_id, cont_name, cont_id, s_id, ver_code, ver_name, status)
		)
	cursor.close()
	return json.dumps(sourcesList)

def biblePattern(*argv):
	try:
		languageName, languageCode, languageId, script, scriptDirection, localScriptName, sourceId, \
			versionCode, versionName, version, metadata, updatedDate,  status, audio_name, audio_url, \
				audio_format, audio_books = argv
	except Exception as ex:
		print(ex)
	pattern = {
		"language":{
			"id": languageId,
			"code": languageCode,
			"name": languageName,
			"script": script,
			"scriptDirection": scriptDirection,
			"localScriptName": localScriptName
		},
		"version":{
			"name": versionName,
			"code": versionCode,
			"longName": version
		},
		"metadata":metadata,
		"audioBible":{"name":audio_name,"url":audio_url,"format":audio_format,"books":audio_books},
		"updatedDate": updatedDate,
		"sourceId": sourceId,
		"status": status
	}
	return pattern

def sortByLanguageObject(languageObject,version):
	'''Sort the list of bible versions by language format by language object.'''
	for index,item in enumerate(languageObject):
		if item['language'] == version["language"]["name"]:
			languageObject[index]["languageVersions"].append(version)
			break
	else:
		languageObject.append({"language": version["language"]["name"],"languageVersions": [version]})
	return languageObject

def sortByLanguageName(languageObject,version):
	'''Sort the list of bible versions by language format by language name.'''
	for index,item in enumerate(languageObject):
		if item["language"]["name"] == version["language"]["name"]:
			version.pop("language")
			languageObject[index]["languageVersions"].append(version)
			break
	else:
		language = version.pop("language")
		languageObject.append({"language": language,"languageVersions": [version]})
	return languageObject

@app.route("/v1/bibles", methods=["GET"])
def getBibles():
	'''Return the list of availabile Bible Languages and Versions.'''
	connection = get_db()
	cursor = connection.cursor()
	#use status param to filter by status, default only true
	status = request.args.get('status')
	query = "select s.source_id, v.revision, v.version_code, v.version_description,v.metadata, \
		l.language_id, l.language_name, l.language_code, local_script_name, script, script_direction, \
			created_at_date, s.status, a.name, a.url, a.format, a.books from sources s left join \
				languages l on s.language_id=l.language_id left join versions v on s.version_id= \
					v.version_id left join audio_bibles a on s.source_id=a.source_id where s.content_id=1 "
	statusQuery = " and s.status=true"
	if status and status.lower() == "both":
		statusQuery = ""
	elif status and status.lower() == "inactive":
		statusQuery = " and s.status=false"
	try:
		cursor.execute(query+statusQuery)
	except Exception as ex:
		print(ex)
	biblesList = []
	language = request.args.get('language')
	for s_id, ver, ver_code, ver_name, metadata, lang_id, lang_name, lang_code, loc_script_name, script, \
		script_dir, updatedDate, status, audio_name, audio_url, audio_format, audio_books in cursor.fetchall():
		biblesList.append(
			biblePattern(
				lang_name,
				lang_code,
				lang_id,
				script,
				script_dir,
				loc_script_name,
				s_id,
				ver_code,
				ver_name,
				ver,
				metadata,
				str(updatedDate),
				status,
				audio_name,
				audio_url,
				audio_format,
				audio_books
			)
		)
	cursor.close()
	sortedList = []
	if(language and language.lower() == "true"):
		sortedList = reduce(sortByLanguageName,biblesList,[])
	else:
		sortedList = reduce(sortByLanguageObject,biblesList,[])
	return json.dumps(sortedList)

@app.route("/v1/bibles/languages", methods=["GET"])
def getBibleLanguages():
	'''Return the list of bible languages.'''
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select distinct(language_id) from sources where content_id=1")
	languageIds = [item[0] for item in cursor.fetchall()]
	cursor.execute("select language_id, language_name, language_code from languages")
	languagesDict = {
		langId:{
			"languageName":langName.capitalize(),
			"languageCode":langCode,
			"languageId": langId
		} for langId, langName, langCode in cursor.fetchall()
	}
	languagesList = [languagesDict[x] for x in languageIds]
	return json.dumps(languagesList)

@app.route("/v1/bibles/<sourceId>/books", methods=["GET"])
def getBibleBooks(sourceId):
	'''Return the list of books in a Bible Language and Version.'''
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst:
		return json.dumps({"success": False, "message": "Invalid Source Id"})
	cursor.execute("select book_id from "+rst[0])
	bookLists = cursor.fetchall()
	if not bookLists:
		return json.dumps({"success": False, "message": "No Books uploaded yet"})
	booksData = []
	cursor.execute("select * from bible_books_look_up order by book_id")
	booksDict = {}
	for bibleBookID, bibleBookFullName, bibleBookCode in cursor.fetchall():
		booksDict[bibleBookID] = {
			"bibleBookID":bibleBookID,
			"abbreviation": bibleBookCode,
			"bibleBookFullName": bibleBookFullName.capitalize()
		}
	for book in bookLists:
		if book[0] in booksDict:
			booksData.append(
				booksDict[book[0]]
			)
	bibleBooks = [
		{
			"sourceId": sourceId,
			"books": booksData
		}
	]
	return json.dumps(bibleBooks)

@app.route("/v1/bibles/<sourceId>/books-chapters", methods=["GET"])
def getBibleBookChapters(sourceId):
	'''Return the list of books and chapter Number in a Bible Language and Version.'''
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst:
		return json.dumps({"success": False, "message": "Invalid Source Id"})
	cursor.execute( sql.SQL("select l.book_id,l.book_name,book_code,json_array_length(cast (json_text->'chapters' as json)) \
		from {} b left join bible_books_look_up l on b.book_id=l.book_id").format(sql.Identifier(rst[0])))
	bookLists = cursor.fetchall()
	if not bookLists:
		return json.dumps({"success": False, "message": "No Books uploaded yet"})
	booksDict = {}
	for bibleBookID, bibleBookFullName, bibleBookCode, chapters in bookLists:
		booksDict[bibleBookCode] = {
			"bibleBookID":bibleBookID,
			"abbreviation": bibleBookCode,
			"bibleBookFullName": bibleBookFullName.capitalize(),
			"chapters": chapters
		}
	bibleBooks = [
		{
			"sourceId": sourceId,
			"books": booksDict
		}
	]
	return json.dumps(bibleBooks)

@app.route("/v1/bibles/<sourceId>/<contentFormat>", methods=["GET"])
def getBible(sourceId, contentFormat):
	'''Return the bible content for a particular Bible version and format.'''
	connection = get_db()
	cursor = connection.cursor()
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst:
		return json.dumps({"success": False, "message": "Invalid Source Id"})
	cursor.execute("select count(*) from "+rst[0])
	if not cursor.fetchone():
		return json.dumps({"success": False, "message": "No Books uploaded yet"})
	if contentFormat.lower() == 'usfm':
		cursor.execute( sql.SQL("select l.book_code,b.usfm_text from {} b \
			left join bible_books_look_up l on b.book_id=l.book_id").format(sql.Identifier(rst[0])))
		bible_data = cursor.fetchall()
		usfm_text = {}
		for book,text in bible_data:
			usfm_text[book]=text
		usfmText = {"sourceId":sourceId,"bibleContent":usfm_text}
	elif contentFormat.lower() == 'json':
		cursor.execute( sql.SQL("select l.book_code,b.json_text from {} b \
			left join bible_books_look_up l on b.book_id=l.book_id").format(sql.Identifier(rst[0])))
		bible_data = cursor.fetchall()
		json_text = {}
		for book,text in bible_data:
			json_text[book]=text
		usfmText = {"sourceId":sourceId,"bibleContent":json_text}
	else:
		return '{"success": false, "message":"Invalid Content Type"}'
	cursor.close()
	return json.dumps(usfmText)


@app.route("/v1/bibles/<sourceId>/books/<bookCode>/<contentFormat>", methods=["GET"])
def getBook(sourceId,bookCode, contentFormat):
	'''Return the content of a book in a particular version and format.'''
	connection = get_db()
	if contentFormat.lower() not in ["usfm","json"]:
		return '{"success": false, "message":"Invalid Content Type"}'
	cursor = connection.cursor()
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst[0]:
		return json.dumps({"success": False, "message": "Invalid Source Id"})
	contentType="usfm_text" if contentFormat.lower() == "usfm" else "json_text"
	cursor.execute( sql.SQL("select {} from {} b left join bible_books_look_up l \
		on b.book_id=l.book_id where l.book_code=%s").format(sql.Identifier(contentType),sql.Identifier(rst[0])),[bookCode])
	rst = cursor.fetchone()
	if not rst[0]:
		return json.dumps({"success": False, "message": "Book not uploaded"})
	else:
		usfmText = {"sourceId":sourceId,"bibleBookCode":bookCode,"bookContent":rst[0]}
	cursor.close()
	return json.dumps(usfmText)

@app.route("/v1/bibles/<sourceId>/books/<biblebookCode>/chapters", methods=["GET"])
def getBibleChapters(sourceId, biblebookCode):
	'''Return number of Chapters and chapter details for a book.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return json.dumps({"success": False, "message": "Invalid Source Id"})

		cursor.execute(sql.SQL("select book_name,json_array_length(cast (json_text->'chapters' as json)) \
		from {} b left join bible_books_look_up l on b.book_id=l.book_id where book_code=%s").\
			format(sql.Identifier(rst[0])),[biblebookCode.lower()])
		bible_book_data = cursor.fetchone()
		if not bible_book_data:
			return '{"success":false, "message":"Book not uploaded"}'
		chapters = []
		book_name,chapter_count = bible_book_data
		for num in range(chapter_count):
			chapters.append(
				{
					"sourceId": sourceId,
					"bibleBookCode": biblebookCode.upper(),
					"chapter":{
						"chapterId": "%s.%s" %(biblebookCode, str(num+1)),
						"number": num+1,
						"reference": book_name.title() + " " + str(num+1)
					}
				}
			)
		return json.dumps(chapters)
	except Exception as ex:
		return '{"success": false, "message":"%s"}' %(str(ex))

@app.route("/v1/bibles/<sourceId>/books/<bookCode>/chapter/<chapterId>", methods=["GET"])
def getChapter(sourceId,bookCode,chapterId):
	'''Return the content of a given bible chapter.'''
	connection = get_db()
	cursor = connection.cursor()
	bookCode=bookCode.lower()
	cursor.execute("select book_id from bible_books_look_up where book_code=%s", (bookCode.lower(),))
	bible_book_data = cursor.fetchone()
	if not bible_book_data:
		return '{"success":false, "message":"Invalid book code"}'
	book_id = bible_book_data[0]
	cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
	rst = cursor.fetchone()
	if not rst:
		return '{"success":false, "message":"Source doesn\'t exist"}'
	table_name=rst[0]
	cursor.execute(sql.SQL("select json_text->'chapters'->%s from {} where book_id=%s")\
		.format(sql.Identifier(table_name)),[int(chapterId)-1,book_id])
	chapter_content = cursor.fetchone()
	if not chapter_content:
		return json.dumps({"success": False, "message": "Book not uploaded"})
	#get data for next and previous chapters
	prevChapter=int(chapterId)-1
	previous={}
	next={}
	if(prevChapter > 0):
		previous={"sourceId":sourceId, "bibleBookCode":bookCode, "chapterId":prevChapter}
	else:
		cursor.execute(sql.SQL("select book_code,json_array_length(cast (json_text->'chapters' as json)) from \
			{} b left join bible_books_look_up l on b.book_id=l.book_id where b.book_id \
				= (select max(book_id) from {} where book_id<%s)").format(sql.Identifier(table_name),sql.Identifier(table_name)),[bible_book_data[0]])
		prev_book = cursor.fetchone()
		if prev_book:
			previous={"sourceId":sourceId, "bibleBookCode":prev_book[0], "chapterId":prev_book[1]}
	#get chapter count and if next chapter less than chapter count return it else get next book
	cursor.execute(sql.SQL("select json_array_length(cast (json_text->'chapters' as json)) from {} \
		where book_id=%s").format(sql.Identifier(table_name)),[book_id])
	chapter_count = cursor.fetchone()[0]
	nextChapter=int(chapterId)+1
	if(nextChapter <= chapter_count):
		next={"sourceId":sourceId, "bibleBookCode":bookCode, "chapterId":nextChapter}
	else:
		cursor.execute(sql.SQL("select book_code from bible_books_look_up where book_id = \
			(select min(book_id) from {} where book_id>%s)").format(sql.Identifier(table_name)),[book_id])
		next_book_id = cursor.fetchone()
		if next_book_id:
			next={"sourceId":sourceId, "bibleBookCode":next_book_id[0], "chapterId":1}
	chapterId=int(chapterId)-1
	if (chapterId>=0 and chapterId<chapter_count):
		usfmText = {"sourceId":sourceId,"bibleBookCode":bookCode,"chapterId":chapterId+1,
			"previous":previous,"next":next,"chapterContent":chapter_content[0]}
	else:
		return json.dumps({"success": False, "message": "Invalid chapter id"})
	cursor.close()
	return json.dumps(usfmText)

@app.route("/v1/bibles/<sourceId>/books/<biblebookCode>/chapters/<chapterId>/verses", methods=["GET"])
def getBibleVerses(sourceId, biblebookCode, chapterId):
	'''Return Verse Id Array for a Bible Book Chapter.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select book_id, book_name from bible_books_look_up \
			where book_code=%s", (biblebookCode.lower(),))
		bibleBookData = cursor.fetchone()
		if not bibleBookData:
			return '{"success":false, "message":"Invalid book code"}'
		cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
		tableName = cursor.fetchone()
		if not tableName:
			return '{"success":false, "message":"Source doesn\'t exist"}'
		startId = int(bibleBookData[0]) * 1000000 + (int(chapterId) * 1000)
		endId = int(bibleBookData[0]) * 1000000 + ((int(chapterId) + 1) * 1000)
		cursor.execute(sql.SQL("select ref_id from {} where ref_id > %s and ref_id < %s order by ref_id").\
			format(sql.Identifier(tableName[0] + "_cleaned")), [startId, endId])
		refIdsList = [x[0] for x in cursor.fetchall()]
		verseList = []
		for ref in refIdsList:
			verseNumber = int(str(ref)[-3:])
			if verseNumber not in verseList:
				verseList.append(verseNumber)
		verses = []
		for num in verseList:
			verses.append(
				{
					"sourceId": sourceId,
					"bibleBookCode": biblebookCode.upper(),
					"chapterId": chapterId,
					"verse": {
						"verseId": "%s.%s" %(chapterId, str(num)),
						"number": num,
						"reference": bibleBookData[1].title() + " %s:%s "  %(chapterId, str(num))
					}
				}
			)
		return json.dumps(verses)
	except Exception as ex:
		return '{"success":false, "message":"%s"}' %(str(ex))

@app.route("/v1/bibles/<sourceId>/books/<bibleBookCode>/chapters/<chapterId>/verses/<verseId>", methods=["GET"])
def getBibleVerseText(sourceId, bibleBookCode, chapterId, verseId):
	'''Return a Verse object for a given Bible and Verse.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select book_id, book_name from bible_books_look_up \
			where book_code=%s", (bibleBookCode.lower(),))
		bibleBookData = cursor.fetchone()
		if not bibleBookData:
			return '{"success":false, "message":"Invalid book code"}'
		cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
		tableName = cursor.fetchone()
		if not tableName:
			return '{"success":false, "message":"Source doesn\'t exist"}'
		bookId = bibleBookData[0]
		ref_id = int(str(bookId).zfill(2) + chapterId.zfill(3) + verseId.zfill(3))
		cursor.execute(sql.SQL("select verse from {} where ref_id=%s").\
			format(sql.Identifier(tableName[0] + "_cleaned")), [ref_id])
		verse = cursor.fetchone()
		if not verse:
			return '{"success": false, "message":"No verse found"}'
		return json.dumps({
			"sourceId": sourceId,
			"bibleBookCode": bibleBookCode,
			"chapterNumber": chapterId,
			"verseNumber": verseId,
			"reference": bibleBookData[1].title() + " %s:%s "  %(chapterId, str(verseId)),
			"verseContent": {
				"text": verse[0]
			}
		})
	except Exception as ex:
		return '{"success":false, "message":"%s"}' %(str(ex))

@app.route("/v1/bibles/<sourceId>/chapters/<chapterId>/verses", methods=["GET"])
def getBibleVerses2(sourceId, chapterId):
	'''Return Verse Id Array for a Bible Book Chapter.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		try:
			bookCode, chapterNumber = chapterId.split('.')
		except:
			return '{"success": false, "message":"Invalid Chapter id format."}'
		cursor.execute("select book_id, book_name from bible_books_look_up \
			where book_code=%s", (bookCode.lower(),))
		bibleBookData = cursor.fetchone()
		if not bibleBookData:
			return '{"success":false, "message":"Invalid book code"}'
		cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
		tableName = cursor.fetchone()
		if not tableName:
			return '{"success":false, "message":"Source doesn\'t exist"}'
		startId = int(bibleBookData[0]) * 1000000 + (int(chapterNumber) * 1000)
		endId = int(bibleBookData[0]) * 1000000 + ((int(chapterNumber) + 1) * 1000)
		cursor.execute(sql.SQL("select ref_id from {} where ref_id > %s and ref_id < %s order by ref_id").\
			format(sql.Identifier(tableName[0] + "_cleaned")), [startId, endId])
		refIdsList = [x[0] for x in cursor.fetchall()]
		verseList = []
		for ref in refIdsList:
			verseNumber = int(str(ref)[-3:])
			if verseNumber not in verseList:
				verseList.append(verseNumber)
		verses = []
		for num in verseList:
			verses.append(
				{
					"sourceId": sourceId,
					"bibleBookCode": bookCode.upper(),
					"chapterId": chapterId,
					"verse": {
						"verseId": "%s.%s" %(chapterId, str(num)),
						"number": num,
						"reference": bibleBookData[1].title() + " %s: %s "  %(chapterNumber, str(num))
					}
				}
			)
		return json.dumps(verses)
	except Exception as ex:
		return '{"success":false, "message":"%s"}' %(str(ex))

@app.route("/v1/bibles/<sourceId>/verses/<verseId>", methods=["GET"])
def getBibleVerseText2(sourceId, verseId):
	'''Return a Verse object for a given Bible and Verse.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		try:
			bookCode, chapterNumber, verseNumber = verseId.split('.')
		except:
			return '{"success": false, "message":"Invalid Verse id format."}'
		cursor.execute("select book_id, book_name from bible_books_look_up \
			where book_code=%s", (bookCode.lower(),))
		bibleBookData = cursor.fetchone()
		if not bibleBookData:
			return '{"success":false, "message":"Invalid book code"}'
		cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
		tableName = cursor.fetchone()
		if not tableName:
			return '{"success":false, "message":"Source doesn\'t exist"}'
		bookId = bibleBookData[0]
		ref_id = int(str(bookId).zfill(2) + chapterNumber.zfill(3) + verseNumber.zfill(3))
		cursor.execute(sql.SQL("select verse from {} where ref_id=%s").\
			format(sql.Identifier(tableName[0] + "_cleaned")), [ref_id])
		verse = cursor.fetchone()
		if not verse:
			return '{"success": false, "message":"No verse found"}'
		return json.dumps({
			"sourceId": sourceId,
			"bibleBookCode": bookCode,
			"chapterNumber": chapterNumber,
			"verseNumber": verseNumber,
			"reference": bibleBookData[1].title() + " %s: %s "  %(chapterNumber, str(verseNumber)),
			"verseContent": {
				"text": verse[0]
			}
		})
	except Exception as ex:
		return '{"success":false, "message":"%s"}' %(str(ex))

def sortCommentariesByLanguage(languageObject,commentary):
	'''Sort the list of commentaries by language name.'''
	for index,item in enumerate(languageObject):
		if item["languageCode"] == commentary["languageCode"]:
			commentary.pop("language")
			commentary.pop("languageCode")
			languageObject[index]["commentaries"].append(commentary)
			break
	else:
		languageCode = commentary.pop("languageCode")
		language = commentary.pop("language")
		languageObject.append({"language": language,"languageCode":languageCode,
			"commentaries": [commentary]})
	return languageObject

def checkAuthorised(cursor,key):
	'''Check if key authorized'''
	authorised = False
	if key and key.strip():
		cursor.execute("select key from content_types where content_type='commentary'")
		db_key = cursor.fetchone()
		if db_key and db_key is not None and key == db_key[0]:
			authorised = True
	return authorised

@app.route("/v1/commentaries", methods=["GET"])
def getBibleCommentaries():
	'''Fetch the list of commentaries with an option to filter by language .'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		query ="select s.source_id,v.version_code,v.version_description,l.language_code,language_name \
			,metadata from versions v inner join sources s on v.version_id = s.version_id inner join \
				languages l on s.language_id=l.language_id where content_id in (select content_id from \
					content_types where content_type = 'commentary') and s.status=true"
		#use language code param to filter by language
		lang_code = request.args.get('language')
		if lang_code and lang_code.strip():
			cursor.execute("select language_id from languages where language_code=%s", (lang_code,))
			language_id = cursor.fetchone()
			if not language_id or language_id is None:
				return '{"success": false, "message":""message":"language code not available.""}'
			cursor.execute(query + " and s.language_id in(%s)", (language_id[0],))
		else:
			cursor.execute(query)
		rst = cursor.fetchall()
		commentaries = []
		authorised = checkAuthorised(cursor,request.args.get('key'))
		for source_id, code, name,language_code,language,metadata in rst:
			if "Copyright" in metadata and metadata["Copyright"]=="True" and not authorised:
				continue
			commentaries.append({ 'sourceId':source_id,'code':code,'name':name,
				'languageCode':language_code,'language':language,'metadata':metadata})
		# Group and sort commentaries by langauge
		commentaries = reduce(sortCommentariesByLanguage,commentaries,[])
		return json.dumps(sorted(commentaries,key=lambda x: x['language']))
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' %(str(ex))

@app.route("/v1/commentaries/<sourceId>/<bookCode>/<chapterId>", methods=["GET"])
def getCommentaryChapter(sourceId,bookCode,chapterId):
	'''Fetch the commentary for a chapter for the given commentary sourceId.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select metadata->'Copyright' from sources s inner join versions v \
			on s.version_id=v.version_id where source_id=%s and content_id in(select content_id \
				from content_types where content_type = 'commentary')", (sourceId,))
		rst = cursor.fetchone()
		if rst[0] and rst[0] =="True":
			#If copyright commentary then check if authorised
			authorised = checkAuthorised(cursor,request.args.get('key'))
			if not authorised:
				return '{"success":false, "message":"Not authorised"}'
		bookCode=bookCode.lower()
		#Get bible book id
		cursor.execute("select book_id from bible_books_look_up where book_code=%s", (bookCode.lower(),))
		bible_book_data = cursor.fetchone()
		if not bible_book_data:
			return '{"success":false, "message":"Invalid book code"}'
		book_id = bible_book_data[0]
		#Validate chapter
		cursor.execute("select count(*) from bcv_map where book=%s and chapter=%s;", (book_id,chapterId,))
		rst = cursor.fetchone()
		if not rst[0]:
			return '{"success":false, "message":"Invalid chapter"}'
		#Get commentary table
		cursor.execute("select table_name from sources where source_id=%s and content_id in(select \
			content_id from content_types where content_type = 'commentary')", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Invalid commentary sourceId"}'
		table_name=rst[0]
		#Get commentary
		cursor.execute(sql.SQL("select verse,commentary from {} where book_id=%s and chapter=%s \
			order by verse").format(sql.Identifier(table_name)),[book_id,int(chapterId)])
		commentary = cursor.fetchall()
		commentaries=[]
		#If first chapter add book intro
		bookIntro=""
		if chapterId == "1":
			cursor.execute(sql.SQL("select commentary from {} where book_id=%s and chapter=0").\
				format(sql.Identifier(table_name)),[book_id])
			bookIntro = cursor.fetchall()[0][0]
		for row in commentary:
			commentaries.append({"verse":row[0],"text":row[1]})
		return json.dumps({ "sourceId":sourceId,"bookCode":bookCode,"chapter":chapterId,\
			"bookIntro":bookIntro,"commentaries":sorted(commentaries, key = lambda i: int(i['verse'].split("-")[0])) })
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' %(str(ex))

def sortDictionaryByLanguage(languageObject,dictionary):
	'''Sort the list of dictionaries by language name.'''
	for index,item in enumerate(languageObject):
		if item["languageCode"] == dictionary["languageCode"]:
			dictionary.pop("language")
			dictionary.pop("languageCode")
			languageObject[index]["dictionaries"].append(dictionary)
			break
	else:
		languageCode = dictionary.pop("languageCode")
		language = dictionary.pop("language").capitalize()
		languageObject.append({"language": language,"languageCode":languageCode,
			"dictionaries": [dictionary]})
	return languageObject

@app.route("/v1/dictionaries", methods=["GET"])
def getDictionaries():
	'''Fetch the list of dictionaries with an option to filter by language .'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		query ="select s.source_id,v.version_code,v.version_description,l.language_code,language_name \
			,metadata from versions v inner join sources s on v.version_id = s.version_id inner join \
				languages l on s.language_id=l.language_id where content_id in (select content_id from \
					content_types where content_type = 'translation_words') "
		#use language code param to filter by language
		lang_code = request.args.get('language')
		if lang_code and lang_code.strip():
			cursor.execute("select language_id from languages where language_code=%s", (lang_code,))
			language_id = cursor.fetchone()
			if not language_id or language_id is None:
				return '{"success": false, "message":""message":"language code not available.""}'
			cursor.execute(query + " and s.language_id in(%s)", (language_id[0],))
		else:
			cursor.execute(query)
		rst = cursor.fetchall()
		dictionaries = []
		for source_id, code, name,language_code,language,metadata in rst:
			dictionaries.append({ 'sourceId':source_id,'code':code,'name':name,
				'languageCode':language_code,'language':language,"metadata":metadata})
		# Group and sort dictionaries by langauge
		dictionaries = reduce(sortDictionaryByLanguage,dictionaries,[])
		return json.dumps(sorted(dictionaries,key=lambda x: x['language']))
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' %(str(ex))

def sortDictionaryByLetter(dictionary,word):
	'''Sort the words in the dictionary by letter.'''
	for index,item in enumerate(dictionary):
		if item["letter"] == word["letter"].upper():
			word.pop("letter")
			dictionary[index]["words"].append(word)
			break
	else:
		letter = word.pop("letter").upper()
		dictionary.append({"letter": letter,"words": [word]})
	return dictionary

@app.route("/v1/dictionaries/<sourceId>", methods=["GET"])
def getDictionaryWords(sourceId):
	'''Fetch the words of a given dictionary.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		#Get dictionary table
		cursor.execute("select table_name from sources where source_id=%s and content_id in(select \
			content_id from content_types where content_type = 'translation_words')", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Invalid dictionary sourceId"}'
		table_name=rst[0]
		#Get dictionary
		cursor.execute(sql.SQL("select id,wordforms from {} order by keyword")
			.format(sql.Identifier(table_name)))
		rst = cursor.fetchall()
		words = []
		for id,wordforms in rst:
			for word in wordforms.split(","):
				word=word.strip()
				if len(word)>0:
					words.append({"letter":word[0],"wordId":id,"word":word})
		# Sort dictionary by word and group by letter
		words = sorted(words,key=lambda w: w['word'].lower())
		words = reduce(sortDictionaryByLetter,words,[])
		return json.dumps(sorted(words,key=lambda x: x['letter']))
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' %(str(ex))

@app.route("/v1/dictionaries/<sourceId>/<wordId>", methods=["GET"])
def getDictionaryWord(sourceId,wordId):
	'''Fetch the meaning for given word of a given dictionary.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		#Get dictionary table
		cursor.execute("select table_name from sources where source_id=%s and content_id in(select \
			content_id from content_types where content_type = 'translation_words')", (sourceId,))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Invalid dictionary sourceId"}'
		table_name=rst[0]
		#Get dictionary
		cursor.execute(sql.SQL("select * from {} where id=%s")
			.format(sql.Identifier(table_name)),[int(wordId)])
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"Invalid wordId"}'
		meaning = {"keyword":rst[1],
			"wordForms":rst[2],
			"strongs":rst[3],
			"definition":rst[4],
			"translationHelp":rst[5],
			"seeAlso":rst[6],
			"ref":rst[7],
			"examples":rst[8]}
		return json.dumps({"sourceId":sourceId, "wordId":wordId, "meaning":meaning})
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' %(str(ex))

def sortInfographicsByBook(infographics, image):
	'''Sort the infographics by book.'''
	for index, item in enumerate(infographics):
		if item["bookId"] == image["bookId"]:
			image.pop("bookId")
			image.pop("bookCode")
			infographics[index]["infographics"].append(image)
			break
	else:
		bookId = image.pop("bookId")
		bookCode = image.pop("bookCode")
		infographics.append(
			{"bookId": bookId, "bookCode": bookCode, "infographics": [image]})
	return infographics


@app.route("/v1/infographics/<languageCode>", methods=["GET"])
def getInfographics(languageCode):
	'''Fetch the metadata for the infographics for the given language .'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute(
			"select language_id from languages where language_code=%s", (languageCode.strip(),))
		language_id = cursor.fetchone()
		if not language_id or language_id is None:
			return '{"success":false, "message":"Invalid language code"}'
		cursor.execute("select table_name,metadata from sources s inner join versions v on \
			s.version_id=v.version_id where content_id in (select content_id from content_types \
				where content_type='infographics') and language_id in (%s) and status=TRUE;",
					   (language_id[0],))
		rst = cursor.fetchone()
		if not rst:
			return '{"success":false, "message":"No infographics available for this language"}'
		table_name = rst[0]
		url = rst[1]
		if url is not None:
			url = url.get("url", "")
		# Get infographics metadata
		cursor.execute(sql.SQL("select i.book_id,b.book_code,title,file_name from {} i inner join \
			bible_books_look_up b on i.book_id=b.book_id order by i.book_id").format(sql.Identifier(table_name)))
		rst = cursor.fetchall()
		books = []
		for bookId, bookCode, title, fileName in rst:
			books.append({"bookId": bookId, "bookCode": bookCode,
						  "title": title, "fileName": fileName})
		# Group and sort dictionaries by book
		books = reduce(sortInfographicsByBook, books, [])
		returnJson = {"languageCode": languageCode, "url": url, "books": books}
		return json.dumps(returnJson)
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' % (str(ex))


def sortAudioBibles(languageObject,audioBible):
	'''Sort the list of audio bible's by language format by language object.'''
	for index,item in enumerate(languageObject):
		if item["language"]["name"] == audioBible["language"]["name"]:
			audioBible.pop("language")
			languageObject[index]["audioBibles"].append(audioBible)
			break
	else:
		language = audioBible.pop("language")
		languageObject.append({"language": language,"audioBibles": [audioBible]})
	return languageObject

@app.route("/v1/audiobibles", methods=["GET"])
def getAudioBibles():
	'''Fetch the metadata for the audiobibles Option to filter by language.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		query = "select a.source_id, name,url, format, language_name, language_code, \
			l.language_id, books from audio_bibles a inner join sources s on a.source_id=s.source_id \
				inner join languages l on s.language_id = l.language_id and a.status=TRUE"
		#use language code param to filter by language
		lang_code = request.args.get('language')
		if lang_code and lang_code.strip():
			cursor.execute("select language_id from languages where language_code=%s", (lang_code,))
			language_id = cursor.fetchone()
			if not language_id or language_id is None:
				return '{"success": false, "message":""message":"language code not available.""}'
			cursor.execute(query + " and s.language_id in(%s)", (language_id[0],))
		else:
			cursor.execute(query)
		rst = cursor.fetchall()
		if not rst:
			return '{"success":false, "message":"No audio bibles available"}'
		audio_bibles = []
		for source_id, name, url, format, language, language_code, language_id, books in rst:
			audio_bibles.append({ 'sourceId':source_id, 'name':name, 'url':url, 'format':format,
				"books":books, 'language':{'name':language,'code':language_code,'id':language_id}})
		# Group and sort dictionaries by book
		audio_bibles = reduce(sortAudioBibles, audio_bibles, [])
		return json.dumps(audio_bibles)
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' % (str(ex))

def sortVideosByLanguage(languageObject,video):
	'''Sort the list of video's by language object.'''
	for index,item in enumerate(languageObject):
		if item["language"]["name"] == video["language"]["name"]:
			video.pop("language")
			languageObject[index]["books"].append(video)
			break
	else:
		language = video.pop("language")
		languageObject.append({"language": language,"books": [video]})
	return languageObject

def sortVideosByBooks(languageObject):
	'''Sort the list of video's by book code.'''
	bookObject = {}
	for item in languageObject["books"]:
		book = item.pop("book")
		if book in bookObject.keys():
			bookObject[book].append(item)
		else:
			bookObject[book]= [item]
	languageObject["books"] = bookObject
	return languageObject

@app.route("/v1/videos", methods=["GET"])
def getVideos():
	'''Fetch the metadata for the videos with an option to filter by language.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		query = "select books,url,title,description,theme,v.language_id,language_name,language_code \
			from bible_videos v inner join languages l on v.language_id=l.language_id"
		#use language code param to filter by language
		lang_code = request.args.get('language')
		if lang_code and lang_code.strip():
			cursor.execute("select language_id from languages where language_code=%s", (lang_code,))
			language_id = cursor.fetchone()
			if not language_id or language_id is None:
				return '{"success": false, "message":""message":"language code not available.""}'
			cursor.execute(query + " and l.language_id in(%s)", (language_id[0],))
		else:
			cursor.execute(query)
		rst = cursor.fetchall()
		if not rst:
			return '{"success":false, "message":"No videos available"}'
		videos = []
		ot_books = "gen,exo,lev,num,deu,jos,jdg,rut,1sa,2sa,1ki,2ki,1ch,2ch,ezr,neh,est,job,psa,\
			pro,ecc,sng,isa,jer,lam,ezk,dan,hos,jol,amo,oba,jon,mic,nam,hab,zep,hag,zec,mal"
		nt_books ="mat,mrk,luk,jhn,act,rom,1co,2co,gal,eph,php,col,1th,2th,1ti,2ti,tit,phm,heb,\
			jas,1pe,2pe,1jn,2jn,3jn,jud,rev"
		for book, url, title, description, theme, language_id, name, code in rst:
			if book == "OT":
				book = ot_books
			elif book == "NT":
				book = nt_books
			elif book == "FB":
				book = ot_books+nt_books
			books = book.split(",")
			for book_code in books:
				videos.append({ 'book':book_code.strip(), 'title':title, 'url':url, 'description':description,
				 'theme':theme, 'language':{'name':name,'code':code,'id':language_id}})
		# Group and sort dictionaries by book
		videos = reduce(sortVideosByLanguage, videos, [])
		videos = map(sortVideosByBooks, videos)
		return json.dumps(list(videos))
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' % (str(ex))

def sortBooksByLanguage(languageObject,bookNames):
	'''Sort the list of book's by language object.'''
	for index,item in enumerate(languageObject):
		if item["language"]["name"] == bookNames["language"]["name"]:
			bookNames.pop("language")
			languageObject[index]["bookNames"].append(bookNames)
			break
	else:
		language = bookNames.pop("language")
		languageObject.append({"language": language,"bookNames": [bookNames]})
	return languageObject

@app.route("/v1/booknames", methods=["GET"])
def getBookNames():
	'''Fetch the bible book names in the native language with an option to filter by language.'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		query = "select short,abbr,long,b.book_id,book_code,l.language_id,language_code,language_name \
			from bible_book_names b inner join bible_books_look_up u on b.book_id=u.book_id inner \
				join languages l on b.language_id=l.language_id"
		#use language code param to filter by language
		lang_code = request.args.get('language')
		if lang_code and lang_code.strip():
			cursor.execute("select language_id from languages where language_code=%s", (lang_code,))
			language_id = cursor.fetchone()
			if not language_id or language_id is None:
				return '{"success": false, "message":""message":"language code not available.""}'
			cursor.execute(query + " and l.language_id in(%s)", (language_id[0],))
		else:
			cursor.execute(query)
		rst = cursor.fetchall()
		if not rst:
			return '{"success":false, "message":"No Book Names available"}'
		books = []
		for short, abbr, long, book_id, book_code, language_id, language_code, language_name in rst:
			books.append({ 'book_id':book_id,'book_code':book_code.strip(),'short':short,'abbr':abbr,'long':long,
				'language':{'name':language_name,'code':language_code,'id':language_id}})
		# Group and sort dictionaries by book
		books = reduce(sortBooksByLanguage, books, [])
		return json.dumps(list(books))
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' % (str(ex))

@app.route("/v1/search/<sourceId>", methods=["GET"])
def searchBible(sourceId):
	'''Fetch the bible verses with the given keyword in the specified sourceId clear text bible'''
	try:
		connection = get_db()
		cursor = connection.cursor()
		cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
		tableName = cursor.fetchone()
		if not tableName:
			return '{"success":false, "message":"Invalid source Id"}'
		keyword = request.args.get('keyword')
		if not keyword:
			return '{"success":false, "message":"Keyword empty"}'
		cursor.execute("select book_id,book_code from bible_books_look_up")
		rst = cursor.fetchall()
		bookMap={}
		for book_id,book_code in rst:
			bookMap[str(book_id)]=book_code
		cursor.execute(sql.SQL("select ref_id,verse from {} where verse ~* {}").\
			format(sql.Identifier(tableName[0] + "_cleaned"),sql.Literal(keyword)))
		rst = cursor.fetchall()
		if not rst:
			return '{"success":false, "message":"Keyword not found in bible"}'
		result =[]
		for ref_id,verse in rst:
			ref = str(ref_id)
			bookCode = bookMap[ref[-8:-6]]
			result.append({'bookCode':bookCode,'chapter':int(ref[-6:-3]),'verse': int(ref[-3:]),'text':verse})
		searchResult = {'sourceId':sourceId,'keyword':keyword,'result':result}
		return json.dumps(searchResult)
	except Exception as ex:
		traceback.print_exc()
		return '{"success":false, "message":"%s"}' % (str(ex))
######################################################
######################################################
