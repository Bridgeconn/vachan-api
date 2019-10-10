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
from random import randint
import phrases
from functools import reduce

logging.basicConfig(filename='API_logs.log', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

app = Flask(__name__)
CORS(app)

sendinblue_key = os.environ.get("AGMT_SENDINBLUE_KEY")
jwt_hs256_secret = os.environ.get("AGMT_HS256_SECRET")
postgres_host = os.environ.get("AGMT_POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("AGMT_POSTGRES_PORT", "5432")
postgres_user = os.environ.get("AGMT_POSTGRES_USER", "postgres")
postgres_password = os.environ.get("AGMT_POSTGRES_PASSWORD", "secret")
postgres_database = os.environ.get("AGMT_POSTGRES_DATABASE", "postgres")
# postgres_database = os.environ.get("vachan", "vachan")
host_api_url = os.environ.get("AGMT_HOST_API_URL")
host_ui_url = os.environ.get("AGMT_HOST_UI_URL")
system_email = os.environ.get("MTV2_EMAIL_ID", "autographamt@gmail.com")

def get_db():                                                                      #--------------To open database connection-------------------#
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = psycopg2.connect(dbname=postgres_database, user=postgres_user, password=postgres_password, \
            host=postgres_host, port=postgres_port)
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
    cursor.execute("SELECT u.password_hash, u.password_salt, r.role_name, u.first_name, u.last_name FROM \
        autographamt_users u LEFT JOIN roles r ON u.role_id = r.role_id WHERE u.email_id = %s \
            and u.verified is True", (email,))
    rst = cursor.fetchone()
    if not rst:
        return '{"success":false, "message":"Email is not Verified"}'
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
    body = '''Hello %s,<br/><br/>Thanks for your interest to use the AutographaMT web service. <br/>
    You need to confirm your email by opening this link:

    <a href="https://%s/v1/verifications/%s">https://%s/v1/verifications/%s</a>

    <br/><br/>The documentation for accessing the API is available at <a \
        href="https://docs.autographamt.com">https://docs.autographamt.com</a>''' % \
            (firstName, host_api_url, verification_code, host_api_url, verification_code)
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
    cursor.execute("SELECT email_id FROM autographamt_users WHERE email_id = %s", (email,))
    rst = cursor.fetchone()
    if not rst:
        cursor.execute("INSERT INTO autographamt_users (first_name, last_name, email_id, \
            verification_code, password_hash, password_salt, created_at_date) \
                VALUES (%s, %s, %s, %s, %s, %s, current_timestamp)", \
                    (firstName, lastName, email, verification_code, password_hash, password_salt))
        cursor.close()
        connection.commit()
        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        return '{"success":true, "message":"Verification Email has been sent to your email id"}'
    else:
        return '{"success":false, "message":"This email has already been Registered, "}'

@app.route("/v1/resetpassword", methods=["POST"])    #-----------------For resetting the password------------------#
def reset_password():
    email = request.form['email']
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT email_id from autographamt_users WHERE email_id = %s", (email,))
    if not cursor.fetchone():
        return '{"success":false, "message":"Email has not yet been registered"}'
    else:
        headers = {"api-key": sendinblue_key}
        url = "https://api.sendinblue.com/v2.0/email"
        # totp = pyotp.TOTP('base32secret3232')       # python otp module
        # verification_code = totp.now()
        verification_code = randint(100001,999999)
        body = '''Hi,<br/><br/>your request for resetting the password has been recieved. <br/>
        Your temporary password is %s. Enter your new password by opening this link:

        <a href="https://%s/forgotpassword">https://%s/forgotpassword</a>

        <br/><br/>The documentation for accessing the API is available at <a \
            href="https://docs.autographamt.com">https://docs.autographamt.com</a>''' % \
                (verification_code, host_ui_url, host_ui_url)
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



@app.route("/v1/verifications/<string:code>", methods=["GET"])
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
                organisation_phone, organisation_email, verified, user_id from autographamt_organisations\
                    order by organisation_id")
            rst = cursor.fetchall()
        elif role == 2:
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute("select organisation_id, organisation_name, organisation_address, \
                organisation_phone, organisation_email, verified, user_id from autographamt_organisations\
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
            } for organisationId, organisationName, organisationAddress, organisationPhone, organisationEmail, verified, userId in rst
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
    
    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
    userId = cursor.fetchone()[0]
    cursor.execute("select * from autographamt_organisations where organisation_name=%s and \
        organisation_email=%s", (organisationName, organisationEmail))
    rst = cursor.fetchone()
    if not rst:
        cursor.execute("insert into autographamt_organisations (organisation_name, \
            organisation_address, organisation_phone, organisation_email, user_id) values (%s,%s,%s,%s,%s) ", \
                (organisationName, organisationAddress, organisationPhone, organisationEmail, userId))
        connection.commit()
        cursor.close()
        return '{"success":true, "message":"Organisation request sent"}'
    else:
        return '{"success":false, "message":"Organisation already created"}'

@app.route("/v1/autographamt/users", methods=["GET"])
@check_token
def autographamtUsers():
    connection = get_db()
    cursor = connection.cursor()
    role = checkAuth()
    if role == 3:
        cursor.execute("select user_id, first_name, last_name, email_id, role_id, verified \
            from autographamt_users order by user_id")
    elif role == 2: 
        cursor.execute("select user_id, first_name, last_name, email_id, role_id, verified \
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
            "verified":verified
        } for userId, firstName, lastName, emailId, roleId, verified in rst
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
                cursor.execute("select p.project_id, p.project_name, p.source_id, p.target_id, \
                    p.organisation_id, o.organisation_name, s.version_content_code, s.version_content_description \
                        from autographamt_projects p left join autographamt_organisations o on \
                        p.organisation_id=o.organisation_id left join sources s on \
                            s.source_id=p.source_id where p.organisation_id=%s", (orgId,))
                rst += cursor.fetchall()
        elif role == 3:
            cursor.execute("select p.project_id, p.project_name, p.source_id, p.target_id, \
                p.organisation_id, o.organisation_name, s.version_content_code, s.version_content_description \
                    from autographamt_projects p left join autographamt_organisations o on \
                    p.organisation_id=o.organisation_id left join sources s on \
                            s.source_id=p.source_id")
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
                }
            } for projectId, projectName, sourceId, targetId, organisationId, organisationName, verCode, verName in rst
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
    print(role)
    if role > 1:
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("select l.language_name, l.language_code from sources s left join languages l on \
            s.language_id=l.language_id where source_id=%s", (sourceId,))
        sourceLanguage, sourceLanguageCode = cursor.fetchone()
        cursor.execute("select language_name, language_code from languages where language_id=%s", (targetLanguageId,))
        targetLanguage, targetLanguageCode = cursor.fetchone()
        projectName = sourceLanguage + '-to-' + targetLanguage + '|' + sourceLanguageCode + '-to-' + targetLanguageCode
        print(projectName)
        cursor.execute("select * from autographamt_projects where organisation_id=%s and source_id=%s and \
            target_id=%s", (organisationId, sourceId, targetLanguageId))
        rst = cursor.fetchone()
        if not rst:
            print("insert")
            cursor.execute("insert into autographamt_projects (project_name, source_id, target_id, organisation_id) \
                values (%s,%s,%s,%s)", (projectName, sourceId, targetLanguageId, organisationId))
            connection.commit()
            cursor.close()
            return '{"success":true, "message":"Project created"}'
        else:
            return '{"success":false, "message":"Project already created"}'
    else:
        return '{"success":false, "message":"UnAuthorized"}'

@app.route("/v1/autographamt/projects/assignments/<projectId>", methods=["GET"])
@check_token
def getAssignments(projectId):
    '''
    Returns an array of Users assigned under a project
    '''
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select u.first_name, u.last_name, u.email_id, a.assignment_id, \
        a.books, a.user_id, a.project_id from autographamt_assignments a \
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
                "projectId":projectId
            } for firstName, lastName, email, assignmentId, books, userId, projectId in rst
        ]
        return json.dumps(projectUsers)

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
    # else:
    # if action == 'add':
    #     books = list(set(books + rst[1]))
    # else:
    #     books = list(set(rst[1]) - set(books))
    
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
    print('please')
    try:
        print('token')
        req = request.get_json(True)
        projectId = req["projectId"]
        token = req["token"]
        translation = req["translation"]
        senses = req["senses"]
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
            if rst[2] != "":
                dbSenses = rst[2].split("|")
            if senses not in dbSenses:
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
            p.source_id, p.target_id, s.version_content_code, s.version_content_description \
                from autographamt_assignments a left join autographamt_projects p on \
                    a.project_id=p.project_id left join autographamt_organisations o on \
                        o.organisation_id=p.organisation_id left join sources s on \
                            p.source_id=s.source_id where a.user_id=%s", (userId,))
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
                    "code": verCode
                }
            } for projectId, projectName, organisationName, books, sourceId, targetId, verCode, verName in rst
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
        # tableName = 
        tableName = "_".join(rst[0].split("_")[0:-1]) + "_tokens"
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
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    if not rst:
        return '{"success":false, "message":"No data available"}'
    cursor.close()
    # 
    if not rst[0]['usfm']:
        return '{"success":false, "message":"No Books uploaded under this source"}'
    else:
        return json.dumps(list(rst[0]['usfm'].keys()))

@app.route("/v1/sources/projects/books/<projectId>/<userId>", methods=["GET"])           #-------------------------To find available books and revision number----------------------#
@check_token
def availableProjectBooks(projectId, userId):
    try:
        connection = get_db()
        cursor = connection.cursor()
        
        cursor.execute("select s.usfm_text from sources s left join autographamt_projects p on s.source_id=p.source_id \
            where p.project_id=%s", (projectId,))
        rst = cursor.fetchone()
        if not rst:
            return '{"success":false, "message":"No data available"}'
        if not rst[0]['usfm']:
            return '{"success":false, "message":"No Books uploaded under this source"}'
        allBooks = list(rst[0]['usfm'].keys())
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
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    cursor.execute("select book_id from bible_books_look_up where book_code=%s", (book,))
    bookId = cursor.fetchone()[0]
    tablename = rst[0].split('_')
    languageCode = tablename[0]
    version = tablename[1]+"_"+tablename[2]
    tablename.pop(-1)
    tablename = '_'.join(tablename) + '_tokens'
    cursor.execute("select token from " + tablename + " where book_id=%s", (bookId,))
    tokenList = [item[0] for item in cursor.fetchall()]
    if len(tokenList) == 0:
        try:
            phrases.tokenize(connection, languageCode.lower(), version.lower() , bookId)
            cursor.execute("select token from " + tablename + " where book_id=%s", (bookId,))
            tokenList = [item[0] for item in cursor.fetchall()]
        except Exception as ex:
            return '{"success":false, "message":"Phrases method error"}'

    cursor.close()
    return json.dumps(tokenList)

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
    tablename = cursor.fetchone()[0]
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

'''
def parseDataForDBInsert(usfmData):
    print('first')
    connection = get_db()
    crossRefPattern = re.compile(r'(\(?(\d+\s)?\S+\s\d+:\d+\,?\)?)')
    footNotesPattern = re.compile(r'\it(.*)\s?\\f\s?\+.*\\ft\s?(.*)\s?\\f\*\\it\*\*')
    cursor = connection.cursor()
    print('Inside parse dat')
    # cursor.execute("select lid, book, chapter, verse from bcv_lid_map")
    # lidDict = {int(str(b).zfill(3) + str(c).zfill(3) + str(v).zfill(3)):l for l,b,c,v in cursor.fetchall()}
    cursor.execute("select book_id, book_code from bible_books_look_up")
    bookIdDict = {v.lower():k for k,v in cursor.fetchall()}
    bookName = usfmData["metadata"]["id"]["book"].lower()
    chapterData = usfmData["chapters"]
    dbInsertData = []
    verseContent = []
    # 
    bookId = bookIdDict[bookName]
    for chapter in chapterData:
        chapterNumber = chapter["header"]["title"]
        verseData = chapter["verses"]
        for verse in verseData:
            verseNumber = verse["number"]
            verseText = verse["text"]
            crossRefs = re.sub(crossRefPattern, r'\1', verseText)
            footNotes = re.sub(footNotesPattern, r'\1', verseText)
            bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
                 + str(verseNumber).zfill(3))
            # lid = lidDict[bcv]
            dbInsertData.append((bcv, verseText, crossRefs, footNotes))
            verseContent.append(verseText)
    tokenList = list(getTokens(' '.join(verseContent)))
    tokenList = [(bookId, token) for token in tokenList]
    # 
    return (dbInsertData, tokenList, bookId)
'''

def parseDataForDBInsert(usfmData):
    connection = get_db()
    # crossRefPattern = re.compile(r'(\(?(\d+\s)?\S+\s\d+:\d+\,?\)?)')
    # footNotesPattern = re.compile(r'\it(.*)\s?\\f\s?\+.*\\ft\s?(.*)\s?\\f\*\\it\*\*')
    normalVersePattern = re.compile(r'\d+$')
    splitVersePattern = re.compile(r'(\d+)(\w)$')
    mergedVersePattern = re.compile(r'(\d+)-(\d+)$')
    cursor = connection.cursor()
    # cursor.execute("select lid, book, chapter, verse from bcv_lid_map")
    # lidDict = {int(str(b).zfill(3) + str(c).zfill(3) + str(v).zfill(3)):l for l,b,c,v in cursor.fetchall()}
    cursor.execute("select book_id, book_code from bible_books_look_up")
    bookIdDict = {v.lower():k for k,v in cursor.fetchall()}
    bookName = usfmData["metadata"]["id"]["book"].lower()
    chapterData = usfmData["chapters"]
    dbInsertData = []
    verseContent = []
    # 
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
                # dbVerseText = re.sub(r"'", r"''", verseText)
                dbVerseText = '$' + verseText + '$'
                # if "'" in dbVerseText:
                #     print(dbVerseText)
                bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
                    + str(verseNumber).zfill(3))
                ref_id = int(bcv)
                # dbInsertData.append((ref_id, verseText, crossRefs, footNotes))
                dbInsertData.append((ref_id, dbVerseText, crossRefs, footNotes))
                verseContent.append(verseText)
            elif splitVersePattern.match(verseNumber):
                ## combine split verses and use the whole number verseNumber
                matchObj = splitVersePattern.match(verseNumber)
                postScript = matchObj.group(2)
                verseNumber = matchObj.group(1)
                if postScript == 'a':
                    verseText = verse['text']
                    # dbVerseText = re.sub("'", "''", verseText)
                    dbVerseText = '$' + verseText + '$'
                    bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
                        + str(verseNumber).zfill(3))
                    ref_id = int(bcv)
                    # dbInsertData.append((ref_id, verseText, crossRefs, footNotes))
                    dbInsertData.append((ref_id, dbVerseText, crossRefs, footNotes))
                    verseContent.append(verseText)
                else:
                    prevdbInsertData = dbInsertData[-1]
                    # prevverseContent = verseContent[-1]

                    verseText = prevdbInsertData[1] + ' '+ verse['text']
                    # dbVerseText = re.sub("'", "''", verseText)
                    dbVerseText = '$' + verseText + '$'
                    # dbInsertData[-1] = (prevdbInsertData[0], verseText, prevdbInsertData[2],prevdbInsertData[3])
                    dbInsertData[-1] = (prevdbInsertData[0], dbVerseText, prevdbInsertData[2],prevdbInsertData[3])
                    verseContent[-1] = verseText
            elif mergedVersePattern.match(verseNumber):
                ## keep the whole text in first verseNumber of merged verses
                verseText = verse['text']
                # dbVerseText = re.sub("'", "''", verseText)
                dbVerseText = '$' + verseText + '$'
                matchObj = mergedVersePattern.match(verseNumber)
                verseNumber = matchObj.group(1)
                verseNumberend = matchObj.group(2)
                bcv = int(str(bookId).zfill(3) + str(chapterNumber).zfill(3) \
                    + str(verseNumber).zfill(3))
                ref_id = int(bcv)
                # dbInsertData.append((ref_id, verseText, crossRefs, footNotes))
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
    # 
    print(dbInsertData[0])
    return (dbInsertData, bookId)

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
        cleanTableName = "%s_%s_%s_bible_cleaned" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
        tokenTableName = "%s_%s_%s_bible_tokens" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
        cursor.execute("select language_id from languages where language_code=%s", (language,))
        languageId = cursor.fetchone()[0]
        cursor.execute("select s.source_id from sources s left join languages l on \
            s.language_id=l.language_id left join content_types c on s.content_id=c.content_id \
                where l.language_code=%s and s.content_id=%s and s.version_content_code=%s and \
                    s.version_content_description=%s and s.year=%s and s.version=%s and \
                        s.license=%s",(language, contentId, versionContentCode, 
                            versionContentDescription, year, version, license))
        rst = cursor.fetchone()
        print('after find')
        if not rst:
            create_clean_bible_table_command = createTableCommand(['ref_id INT NOT NULL', 'verse TEXT', \
                'cross_reference TEXT', 'foot_notes TEXT'], cleanTableName)
            create_token_bible_table_command = createTableCommand(['token_id BIGSERIAL PRIMARY KEY', \
                'book_id INT NOT NUll', 'token TEXT NOT NULL'], tokenTableName)
            cursor.execute(create_clean_bible_table_command)
            cursor.execute(create_token_bible_table_command)
            usfmTextJson = json.dumps({
                "usfm": None,
                "parsedJson": None
            })
            cursor.execute('insert into sources (version_content_code, version_content_description,\
            table_name, year, license, version, content_id, language_id, usfm_text) values \
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (versionContentCode, versionContentDescription, \
                    cleanTableName, year, license, version, contentId, languageId, usfmTextJson))
            connection.commit()
            cursor.close()
            return '{"success": true, "message":"Source Created successfully"}'
        else:
            cursor.close()
            return '{"success": false, "message":"Source already exists"}'
    except Exception as ex:
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
        cursor.execute("select s.usfm_text, s.version_content_code, l.language_code, s.version from \
            sources s left join languages l on s.language_id=l.language_id where \
                source_id=%s", (sourceId,))
        rst = cursor.fetchone()
        # print(rst)
        cursor.close()
        if not rst:
            return '{"success":false, "message":"No source created"}'
        usfmFile = rst[0]["usfm"]
        parsedJsonFile = rst[0]["parsedJson"]
        bookCode = parsedUsfmText["metadata"]["id"]["book"].lower()
        print(bookCode)
        print('whats')
        if usfmFile:
            if bookCode in usfmFile:
                print('happening')
                return '{"success":false, "message":"Book already Uploaded"}'
        else:
            usfmFile = {}
            parsedJsonFile = {}
        # except Exception as ex:
        #     return '{"success":false, "message":"' + str(ex) + '"}'
        print('befire parse')
        parsedDbData, bookId = parseDataForDBInsert(parsedUsfmText)
        languageCode = rst[2]
        versionCode = rst[1]
        print(languageCode, versionCode)
        cursor = connection.cursor()
        usfmFile[bookCode] = wholeUsfmText
        parsedJsonFile[bookCode] = parsedUsfmText
        usfmText = json.dumps({
            "usfm": usfmFile,
            "parsedJson": parsedJsonFile
        })
        version = rst[3]
        dataForDb = str(parsedDbData)[1:-1]
        dataForDb = re.sub("\$'", "$$", dataForDb)
        dataForDb = re.sub("'\$", "$$", dataForDb)
        dataForDb = re.sub('\$"', "$$", dataForDb)
        dataForDb = re.sub('"\$', "$$", dataForDb)
        cleanTableName = "%s_%s_bible_cleaned" %(languageCode.lower(), version.lower())
        
        print(cleanTableName)
        cursor.execute('insert into ' + cleanTableName + ' (ref_id, verse, cross_reference, foot_notes) values '\
            + dataForDb)
        # cursor = connection.cursor()
        # version = rst[0]
        cursor.execute('update sources set usfm_text=%s where source_id=%s', (usfmText, sourceId))
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
    
    print('got Data')
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
    print(rst)
    if not rst:
        print('new')
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
        print('update')
        if senses == rst[2] and translation == rst[1]:
            print(senses)
            print("return 1")
            return '{"success":false, "message":"No New change. This data has already been saved"}'
        if senses != rst[2] and translation == rst[1]:
            print('senses parsing')
            print(senses)
            senses = rst[2] + '|' + senses
        # if senses == rst[2] and translation != rst[1]:
        #     # senses = checkSenses
        #     pass
        if senses == "" and translation != rst[1]:
            senses = rst[2]

        print(' 2nd parse')
        
        
        # senses = '|'.join(list(set(senses.split('|'))))
        # if senses[0] == '|':
        #     print('3rd parse')
        #     print(senses)
        #     senses = senses[1:]
        cursor.execute("update translations set translation=%s, user_id=%s, senses=%s where source_id=%s and \
            target_id=%s and token=%s",(translation, userId, senses, sourceId, targetLanguageId, token))
        cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
            user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
                userId, senses))
        print('values updated')
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
        cursor.execute("select distinct r.version_content_code, l.language_name, r.language_name, \
            r.source_id from translations t left join (select distinct s.source_id, \
                s.version_content_code, ll.language_name  from translations tt left join sources s \
                    on tt.source_id=s.source_id left join languages ll on \
                        s.language_id=ll.language_id) r on t.source_id=r.source_id left \
                            join languages l on t.target_id=l.language_id")
        cursor.execute("select user_id from autographamt_users where email_id=%s", (email,))
        userId = cursor.fetchone()[0]
        cursor.execute("select project_id from autographamt_assignments where user_id=%s", (userId,))
        projectIds = [p[0] for p in cursor.fetchall()]
        translationInfo = []
        for p_id in projectIds:
            cursor.execute("select distinct p.project_id, p.project_name from translation_projects_look_up \
                t left join autographamt_projects p on t.project_id=p.project_id where p.project_id=%s", \
                    (p_id,))
            rst = cursor.fetchall()
            if rst:
                for projectId, projectName in rst:
                    translationInfo.append({
                        "projectId": projectId,
                        "projectName": projectName
                    })
        cursor.close()
        return json.dumps(translationInfo)
    except Exception as ex:
        print(ex)
        return '{"success":false, "message":"Server side issue"}'
    # cursor.execute("select distinct p.project_id, p.project_name, o.organisation_name ")
    # cursor.execute("select distinct r.version_content_code, l.language_name, r.language_name \
    # r.source_id from translations t left join (select distinct s.source_id, s.version_content_code, \
    # ll.language_name  from translations tt left join sources s on tt.source_id=s.source_id \
    #     left join languages ll on s.language_id=ll.language_id) \
    # r on t.source_id=r.source_id left join languages l on t.target_id=l.language_id")
    # rst = cursor.fetchall()
    # # 
    # tokenInformation = {}
    # for v,t,s in rst:
        
    #     if s in tokenInformation:
    #         temp = tokenInformation[s]
    #         if v in temp:
    #             temp[v] = temp[v] + [t]
    #         else:
    #             temp[v] = [t]
    #         tokenInformation[s] = temp
    #     else:
    #         tokenInformation[s] = {
    #             v:[t]
    #         }
    # # tokenInformationList = [{k:v} for k,v in tokenInformation.items()]
    # return json.dumps(tokenInformation)


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
    tableName = "_".join(rst.split("_")[0:-1]) + "_tokens"
    # 

    cursor.execute("select b.book_code, t.token from " + tableName + " t left join \
        bible_books_look_up b on t.book_id=b.book_id")
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
    # sourceId = req["sourceId"]
    # targetLanguageId = req["targetLanguageId"]
    projectId = req["projectId"]
    bookList = req["bookList"]
    connection = get_db()
    cursor = connection.cursor()
    # cursor.execute("select t.token, t.translation from translations t left join \
    #     translation_projects_look_up l on t.translation_id=l.translation_id where l.project_id=%s \
    #     ", (projectId,))

    # rst = cursor.fetchall()
    cursor.execute("select source_id from autographamt_projects where project_id=%s", (projectId,))
    sourceId = cursor.fetchone()[0]
    
    usfmMarker = re.compile(r'\\\w+\d?\s?')
    nonLangComponentsTwoSpaces = re.compile(r'\s[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]\s')
    nonLangComponentsTrailingSpace = re.compile(r'[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]\s')
    nonLangComponentsFrontSpace = re.compile(r'\s[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]')
    nonLangComponents = re.compile(r'[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।]')

    # if phrases.loadPhraseTranslations(connection, sourceId, targetLanguageId):
    if phrases.loadPhraseTranslations(connection, projectId):
        
        # cursor.execute("select book_id, book_code from bible_books_look_up where book_code=%s", (bookList[0],))
        # bookId, bookCode = cursor.fetchone()
        # tokenTranslatedDict = {k:v for k,v in rst}
        cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
        source_rst = cursor.fetchone()
        
        # usfmText = source_rst[0]['usfm'][bookCode]
        finalDraftDict = {}
        for book in bookList:
            usfmText = source_rst[0]['usfm'][book]
            usfmLineList = []
            for line in usfmText.split('\n'):
                usfmWordsList = []
                nonLangCompsTwoSpaces = []
                nonLangCompsTrailingSpace = []
                nonLangCompsFrontSpace = []
                nonLangComps = []
                markers_in_line = re.findall(usfmMarker,line)
                for word_seq in re.split(usfmMarker,line):
                    nonLangCompsTwoSpaces += re.findall(nonLangComponentsTwoSpaces,word_seq)
                    clean_word_seq = re.sub(nonLangComponentsTwoSpaces,' uuuQQQuuu ',word_seq)
                    nonLangCompsTrailingSpace += re.findall(nonLangComponentsTrailingSpace,clean_word_seq)
                    clean_word_seq = re.sub(nonLangComponentsTrailingSpace,' QQQuuu ',clean_word_seq)
                    nonLangCompsFrontSpace += re.findall(nonLangComponentsFrontSpace,clean_word_seq)
                    clean_word_seq = re.sub(nonLangComponentsFrontSpace,' uuuQQQ ',clean_word_seq)
                    nonLangComps += re.findall(nonLangComponents,clean_word_seq)
                    clean_word_seq = re.sub(nonLangComponents,' QQQ ',clean_word_seq)
                    
                    translated_seq = [ phrases.translateText( clean_word_seq ) ]
                
                for i,marker in enumerate(markers_in_line):
                    usfmWordsList.append(marker)
                    usfmWordsList.append(translated_seq[i])
                if i+1<len(translated_seq):
                    usfmWordsList += translated_seq[i+1:]
                outputLine = " ".join(usfmWordsList)
                
                for comp in nonLangCompsTwoSpaces:
                    outputLine = re.sub(r'\s+uuuQQQuuu\s+'," "+comp+" ",outputLine,1)
                for comp in nonLangCompsTrailingSpace:
                    outputLine = re.sub(r'\s+QQQuuu\s+',comp+" ",outputLine,1)
                for comp in nonLangCompsFrontSpace:
                    outputLine = re.sub(r'\s+uuuQQQ\s+'," "+comp,outputLine,1)
                for comp in nonLangComps:
                    outputLine = re.sub(r'\s+QQQ\s+',comp,outputLine,1)
                
                usfmLineList.append(outputLine)
            translatedUsfmText = "\n".join(usfmLineList)
            finalDraftDict[book] = translatedUsfmText
        return json.dumps({
            "translatedUsfmText": finalDraftDict
        })
    else:
        '{"success": false, "message":"No translation available"}'



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
# @app.route("/v1/sources/")

@app.route('/v1/sources/<sourceid>/<outputtype>', methods=["GET"], defaults={'bookid':None})
@app.route('/v1/sources/<sourceid>/<outputtype>/<bookid>', methods=["GET"])
def getbookText(sourceid, outputtype, bookid):
    connection = get_db()
    cursor = connection.cursor()
    outputtype = outputtype.lower()
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceid,))
    jsonFile = cursor.fetchone()
    if not jsonFile:
        return '{"success":false, "message":"Source File not available. Upload source"}'
    jsonFile = jsonFile[0]
    bookIdDict = getBibleBookIds()
    if outputtype == 'usfm':
        usfmText = jsonFile["usfm"]
        if bookid:
            bookCode = (bookIdDict[int(bookid)]).lower()
            if bookCode in usfmText:
                usfmContent = {
                    bookCode:usfmText[bookCode]
                }
                return json.dumps(usfmContent)
            else:
                return '{"success":false, "message":"This Book has not been uploaded yet"}'
        else:
            usfmContent = usfmText
        return json.dumps({
            bookCode:usfmContent
        })
    elif outputtype == 'json':
        jsonText = jsonFile["parsedJson"]
        if bookid:
            bookCode = (bookIdDict[int(bookid)]).lower()
            if bookCode in jsonText:
                jsonContent = {
                    bookCode:jsonText[bookCode]
                }
            else:
                return '{"success":false, "message":"This Book has not been uploaded yet"}'
        else:
            jsonContent = jsonText
        return json.dumps(jsonContent)
    else:
        '{"success":false, "message":"Invalid type. Use either `usfm` or `json`"}'


@app.route('/v1/sources/<sourceid>/<outputtype>/<bookid>/<chapterid>', methods=["GET"])
def getVerseInRange(sourceid, outputtype, bookid, chapterid):
    connection = get_db()
    cursor = connection.cursor()
    outputtype = outputtype.lower()
    
    cursor.execute("select table_name, usfm_text from sources where source_id=%s", (sourceid,))
    rst = cursor.fetchone()
    if not rst:
        return '{"success":false, "message":"Source File not available. Upload source"}'
    if outputtype == "clean":
        cursor.execute("select b.book_code, b.book_id, b.book_name, t.verse from " + \
            rst[0] + " t left join bcv_lid_map bcv on t.lid=bcv.lid left join \
                 bible_books_look_up b on b.book_id=bcv.book where bcv.book=%s \
                     and bcv.chapter=%s order by bcv.lid", (int(bookid), int(chapterid)))
        cleanedText = cursor.fetchall()
        cleanedText = [{
            "bookId":bookId,
            "bookName": bookName,
            "bookCode": bookCode,
            "text": text
        } for bookId, bookName, bookCode, text in cleanedText]
        return json.dumps(cleanedText)
    elif outputtype == "json":
        booksIdDict = getBibleBookIds()
        bookCode = (booksIdDict[int(bookid)]).lower()
        jsonContent = rst[1]["parsedJson"]
        # 
        if bookCode in jsonContent:
            bookContent = jsonContent[bookCode]
            chapterContent = bookContent["chapters"]
            chapterContent = chapterContent[int(chapterid) -1]
            return json.dumps(chapterContent)
        else:
            return '{"success":false, "message":"Book not available"}'
    else:
        '{"success":false, "message":"Invalid type. Use either `clean` or `json`"}'


#####################################################
# VACHAN API
#####################################################

def sourcesPattern(*argv):
    languageName, languageCode, languageId, contentType, contentId, sourceId, \
        versionCode, versionName = argv
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
        }
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
        cursor.execute("select s.source_id, s.version_content_code, s.version_content_description, \
            c.content_id, c.content_type, l.language_id, l.language_name, l.language_code from sources s\
                left join content_types c on s.content_id=c.content_id left join languages l on \
                    s.language_id=l.language_id")
    except Exception as ex:
        print(ex)
    sourcesList = []
    for s_id, ver_code, ver_name, cont_id, cont_name, lang_id, lang_name, lang_code in cursor.fetchall():
        sourcesList.append(
            sourcesPattern(lang_name, lang_code, lang_id, cont_name, cont_id, s_id, ver_code, ver_name)
        )
    cursor.close()
    return json.dumps(sourcesList)

def biblePattern(*argv):
    try:
        languageName, languageCode, languageId, script, scriptDirection, localScriptName, sourceId, \
            versionCode, versionName, version, updatedDate = argv
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
        "audioBible":[],
        "updatedDate": updatedDate,
        "sourceId": sourceId
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
    try:
        cursor.execute("select s.source_id, s.version, s.version_content_code, s.version_content_description, \
            l.language_id, l.language_name, l.language_code, local_script_name, script, \
                script_direction, created_at_date from sources s left join languages l on s.language_id=l.language_id where \
                    s.content_id=1")
    except Exception as ex:
        print(ex)
    biblesList = []
    language = request.args.get('language')
    for s_id, ver, ver_code, ver_name, lang_id, lang_name, lang_code, loc_script_name, script, script_dir, \
        updatedDate in cursor.fetchall():
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
                str(updatedDate)
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
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    if not rst:
        return json.dumps({"success": False, "message": "Invalid Source Id"})
    if 'usfm' not in rst[0]:
        return json.dumps({"success": False, "message": "No Books uploaded yet"})
    bookLists = [item for item in rst[0]["usfm"].keys()]
    booksData = []
    cursor.execute("select * from bible_books_look_up order by book_id")
    booksDict = {}
    for bibleBookID, bibleBookFullName, bibleBookCode in cursor.fetchall():
        booksDict[bibleBookCode] = {
            "bibleBookID":bibleBookID,
            "abbreviation": bibleBookCode,
            "bibleBookFullName": bibleBookFullName.capitalize()
        }
    for book in bookLists:
        if book in booksDict:
            booksData.append(
                booksDict[book]
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
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    if not rst:
        return json.dumps({"success": False, "message": "Invalid Source Id"})
    if 'usfm' not in rst[0]:
        return json.dumps({"success": False, "message": "No Books uploaded yet"})
    bookLists = [{"bookName":item,"chapters":len(rst[0]["parsedJson"][item]["chapters"])} for item in rst[0]["usfm"].keys()]
    booksData = []
    cursor.execute("select * from bible_books_look_up order by book_id")
    booksDict = {}
    for bibleBookID, bibleBookFullName, bibleBookCode in cursor.fetchall():
        booksDict[bibleBookCode] = {
            "bibleBookID":bibleBookID,
            "abbreviation": bibleBookCode,
            "bibleBookFullName": bibleBookFullName.capitalize()
        }
    for bookObject in bookLists:
        book = bookObject["bookName"]
        if book in booksDict:
            booksDict[book]["chapters"]= bookObject["chapters"]
            booksData.append(
                booksDict[book]
            )
    bibleBooks = [
        {
            "sourceId": sourceId,
            "books": booksData
        }
    ]
    return json.dumps(bibleBooks)

@app.route("/v1/bibles/<sourceId>/<contentFormat>", methods=["GET"])
def getBible(sourceId, contentFormat):
    '''Return the bible content for a particular Bible version and format.'''
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    if not rst:
        return json.dumps({"success": False, "message": "Invalid Source Id"})
    if 'usfm' not in rst[0]:
        return json.dumps({"success": False, "message": "No Books uploaded yet"})
    if contentFormat.lower() == 'usfm':
        usfmText = {"sourceId":sourceId,"bibleContent":rst[0]["usfm"]}
    elif contentFormat.lower() == 'json':
        usfmText = {"sourceId":sourceId,"bibleContent":rst[0]["parsedJson"]}
    else:
        return '{"success": false, "message":"Invalid Content Type"}'
    cursor.close()
    return json.dumps(usfmText)
    

@app.route("/v1/bibles/<sourceId>/books/<bookCode>/<contentFormat>", methods=["GET"])
def getBook(sourceId,bookCode, contentFormat):
    '''Return the content of a book in a particular version and format.'''
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    contentType="usfm" if contentFormat.lower() == "usfm" else "parsedJson"
    if not rst:
        return json.dumps({"success": False, "message": "Invalid Source Id"})
    if 'usfm' not in rst[0]:
        return json.dumps({"success": False, "message": "No Books uploaded yet"})
    elif contentFormat.lower() == 'json' or contentFormat.lower() == 'usfm':
        if bookCode in rst[0][contentType]:
            usfmText = {"sourceId":sourceId,"bibleBookCode":bookCode,"bookContent":rst[0][contentType][bookCode]}
        else:
            return json.dumps({"success": False, "message": "Book not uploaded yet"})
    else:
        return '{"success": false, "message":"Invalid Content Type"}'
    cursor.close()
    return json.dumps(usfmText)

@app.route("/v1/bibles/<sourceId>/books/<biblebookCode>/chapters", methods=["GET"])
def getBibleChapters(sourceId, biblebookCode):
    '''Return a Chapter object with content of all verses for the Chapter.'''
    try:
        connection = get_db()
        cursor = connection.cursor()
        cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
            where book_code=%s", (biblebookCode.lower(),))
        bibleBookData = cursor.fetchone()
        if not bibleBookData:
            return '{"success":false, "message":"Invalid book code"}'
        cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
        tableName = cursor.fetchone()
        if not tableName:
            return '{"success":false, "message":"Source doesn\'t exist"}'
        startId = int(bibleBookData[0]) * 1000000
        endId = (int(bibleBookData[0]) + 1) * 1000000
        cursor.execute("select ref_id from " + tableName[0] + " where ref_id > %s \
            and ref_id < %s order by ref_id", (startId, endId))
        refIdsList = [x[0] for x in cursor.fetchall()]
        chapterList = []
        for ref in refIdsList:
            chapterNumber = int(str(ref)[-6:-3])
            if chapterNumber not in chapterList:
                chapterList.append(chapterNumber)
        chapters = []
        for num in chapterList:
            chapters.append(
                {
                    "sourceId": sourceId,
                    "bibleBookCode": biblebookCode.upper(),
                    "chapter":{
                        "chapterId": "%s.%s" %(biblebookCode, str(num)),
                        "number": num,
                        "reference": " ".join(w.capitalize() for w in bibleBookData[2].split(' ')) + " " + str(num)
                    }
                }
            )
        return json.dumps(chapters)
    except Exception as ex:
        return '{"success": false, "message":"%s"}' %(str(ex))

def getChapterList(sourceId,bibleBookData,cursor):
    '''Return the list of chapters for the given book.'''
    cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
    tableName = cursor.fetchone()
    if not tableName:
        return '{"success":false, "message":"Source doesn\'t exist"}'
    startId = int(bibleBookData[0]) * 1000000
    endId = (int(bibleBookData[0]) + 1) * 1000000
    cursor.execute("select ref_id from " + tableName[0] + " where ref_id > %s \
        and ref_id < %s order by ref_id", (startId, endId))
    refIdsList = [x[0] for x in cursor.fetchall()]
    chapterList = []
    for ref in refIdsList:
        chapterNumber = int(str(ref)[-6:-3])
        if chapterNumber not in chapterList:
            chapterList.append(chapterNumber)
    return chapterList

def getBookById(bookId,cursor):
    '''Return the book details from the database for the given book id.'''
    cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
        where book_id=%s", (bookId,))
    return cursor.fetchone()

@app.route("/v1/bibles/<sourceId>/books/<bookCode>/chapter/<chapterId>", methods=["GET"])
def getChapter(sourceId,bookCode,chapterId):
    '''Return the content of a given bible chapter.'''
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
            where book_code=%s", (bookCode.lower(),))
    bibleBookData = cursor.fetchone()
    if not bibleBookData:
        return '{"success":false, "message":"Invalid book code"}'
    cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
    tableName = cursor.fetchone()
    if not tableName:
        return '{"success":false, "message":"Source doesn\'t exist"}'
    chapterList = getChapterList(sourceId,bibleBookData,cursor)
    prevChapter=int(chapterId)-1
    nextChapter=int(chapterId)+1
    previous={}
    next={}
    if(prevChapter in chapterList):
        previous={"sourceId":sourceId, "bibleBookCode":bookCode, "chapterId":prevChapter}
    else:
        query = "select MAX(ref_id) from %s where ref_id<%%s" % tableName[0]
        cursor.execute(query,(str(int(bibleBookData[0])*1000000),))
        prevBookId = cursor.fetchone()
        if prevBookId[0] != None:
            prevBook =getBookById(int(prevBookId[0])//1000000,cursor)
            previous={"sourceId":sourceId, "bibleBookCode":prevBook[1], "chapterId":(int(prevBookId[0])//1000)%1000}
    if(nextChapter in chapterList):
        next={"sourceId":sourceId, "bibleBookCode":bookCode, "chapterId":nextChapter}
    else:
        query = "select MIN(ref_id) from %s where ref_id>%%s" % tableName[0]
        cursor.execute(query,(str(int(bibleBookData[0])*1000000+200000),))
        nextBookId = cursor.fetchone()
        if nextBookId[0] != None:
            nextBook =getBookById(int(nextBookId[0])//1000000,cursor)
            next={"sourceId":sourceId, "bibleBookCode":nextBook[1], "chapterId":(int(nextBookId[0])//1000)%1000}    
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    chapterId=int(chapterId)-1
    if not rst:
        return json.dumps({"success": False, "message": "Invalid Source Id"})
    if 'usfm' not in rst[0]:
        return json.dumps({"success": False, "message": "No Books uploaded yet"})
    elif bookCode in rst[0]["parsedJson"]:
        if chapterId>=0 and chapterId<len(rst[0]["parsedJson"][bookCode]["chapters"]):
            usfmText = {"sourceId":sourceId,"bibleBookCode":bookCode,"chapterId":chapterId+1,"previous":previous,"next":next,"chapterContent":rst[0]["parsedJson"][bookCode]["chapters"][chapterId]}
        else:
            return json.dumps({"success": False, "message": "Invalid chapter id"})
    else:
        return json.dumps({"success": False, "message": "Book not uploaded yet"})
    cursor.close()
    return json.dumps(usfmText)

@app.route("/v1/bibles/<sourceId>/books/<biblebookCode>/chapters/<chapterId>/verses", methods=["GET"])
def getBibleVerses(sourceId, biblebookCode, chapterId):
    '''Return Verse Id Array for a Bible Book Chapter.'''
    try:
        connection = get_db()
        cursor = connection.cursor()
        # try:
        #     bookCode, chapterNumber = chapterId.split('.')
        # except:
        #     return '{"success": false, "message":"Invalid Chapter id format."}'
        cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
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
        cursor.execute("select ref_id from " + tableName[0] + " where ref_id > %s \
            and ref_id < %s order by ref_id", (startId, endId))
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
                        "reference": " ".join(w.capitalize() for w in bibleBookData[2].split(' ')) \
                            + " %s: %s "  %(chapterId, str(num))
                    }
                }
            )
        return json.dumps(verses)
    except Exception as ex:
        return '{"success":false, "message":"%s"}' %(str(ex))



@app.route("/v1/bibles/<sourceId>/books/<bibleBookCode>/chapters/<chapterId>/verses/<verseId>", methods=["GET"])
def getBibleVerseText(sourceId, bibleBookCode, chapterId, verseId):
    '''Return a Verse object for a given Bible and Verse.'''
    try:
        connection = get_db()
        cursor = connection.cursor()
        # try:
        #     bookCode, chapterNumber, verseNumber = verseId.split('.')
        # except:
        #     return '{"success": false, "message":"Invalid Verse id format."}'
        cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
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
        cursor.execute("select verse from " + tableName[0] + " where ref_id=%s", (ref_id,))
        verse = cursor.fetchone()
        if not verse:
            return '{"success": false, "message":"No verse found"}'
        return json.dumps({
            "sourceId": sourceId,
            "bibleBookCode": bibleBookCode,
            "chapterNumber": chapterId,
            "verseNumber": verseId,
            "reference":  " ".join(w.capitalize() for w in bibleBookData[2].split(' ')) \
                            + " %s: %s "  %(chapterId, str(verseId)),
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
        cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
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
        cursor.execute("select ref_id from " + tableName[0] + " where ref_id > %s \
            and ref_id < %s order by ref_id", (startId, endId))
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
                        "reference": " ".join(w.capitalize() for w in bibleBookData[2].split(' ')) \
                            + " %s: %s "  %(chapterNumber, str(num))
                    }
                }
            )
        return json.dumps(verses)
    except Exception as ex:
        return '{"success":false, "message":"%s"}' %(str(ex))

@app.route("/v1/bibles/<sourceId>/verses/<verseId>", methods=["GET"])
def getBibleVerseText2(sourceId, verseId):
    '''Return a Verse object for a given Bible and Verse.'''
    try:
        connection = get_db()
        cursor = connection.cursor()
        try:
            bookCode, chapterNumber, verseNumber = verseId.split('.')
        except:
            return '{"success": false, "message":"Invalid Verse id format."}'
        cursor.execute("select book_id, book_code, book_name from bible_books_look_up \
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
        cursor.execute("select verse from " + tableName[0] + " where ref_id=%s", (ref_id,))
        verse = cursor.fetchone()
        if not verse:
            return '{"success": false, "message":"No verse found"}'
        return make_response({
            "sourceId": sourceId,
            "bibleBookCode": bookCode,
            "chapterNumber": chapterNumber,
            "verseNumber": verseNumber,
            "reference":  " ".join(w.capitalize() for w in bibleBookData[2].split(' ')) \
                            + " %s: %s "  %(chapterNumber, str(verseNumber)),
            "verseContent": {
                "text": verse[0]
            }
        })
        # return jsonify(verse[0])
    except Exception as ex:
        return '{"success":false, "message":"%s"}' %(str(ex))
    

######################################################
######################################################
