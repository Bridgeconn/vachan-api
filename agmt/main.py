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
from flask import Flask, request, session, redirect, jsonify
from flask import g
from flask_cors import CORS, cross_origin
import jwt
import requests
import scrypt
import psycopg2
from random import randint
import phrases

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
    cursor.execute("SELECT u.password_hash, u.password_salt, r.role_name FROM \
        autographamt_users u LEFT JOIN roles r ON u.role_id = r.role_id WHERE u.email_id = %s \
            and u.verified is True", (email,))
    rst = cursor.fetchone()
    if not rst:
        return '{"success":false, "message":"Email is not Verified"}'
    password_hash = rst[0].hex()
    password_salt = bytes.fromhex(rst[1].hex())
    password_hash_new = scrypt.hash(password, password_salt).hex()
    role = rst[2]
    
    if password_hash == password_hash_new:
        try:
            access_token = jwt.encode({'sub': email, 'exp': datetime.datetime.utcnow() + \
                datetime.timedelta(days=1), 'role': role, 'app':'mt'}, jwt_hs256_secret, algorithm='HS256')
        except Exception as ex:
            pass
        logging.warning('User: \'' + str(email) + '\' logged in successfully')
        return '{"access_token": "%s"}\n' % (access_token.decode('utf-8'),)
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


@app.route("/v1/books/<sourceId>", methods=["GET"])           #-------------------------To find available books and revision number----------------------#
# @check_token
def available_books(sourceId):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    if not rst:
        return '{"success":false, "message":"No data available"}'
    cursor.close()
    # 
    return json.dumps(list(rst[0]['usfm'].keys()))

@app.route("/v1/tokenlist/<sourceId>/<book>", methods=["GET"])
def getTokenLists(sourceId, book):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
    rst = cursor.fetchone()
    cursor.execute("select book_id from bible_books_look_up where book_code=%s", (book,))
    bookId = cursor.fetchone()[0]
    tablename = '_'.join(rst[0].split('_')[0:3]) + '_tokens'
    tablename = rst[0].split('_')
    tablename.pop(-1)
    tablename = '_'.join(tablename) + '_tokens'
    cursor.execute("select token from " + tablename + " where book_id=%s", (bookId,))
    tokenList = [item[0] for item in cursor.fetchall()]
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
    # tablename = tablenames[lang.lower()]
    cursor.execute("select table_name from sources where source_id=%s", (sourceId,))
    tablename = cursor.fetchone()[0]
    # tablename = "_".join(rst.split('_')[0:3]) + '_'
    cursor.execute("select bb.book_code, bb.book_name, l.chapter, l.verse, b.verse from " + tablename + " b \
       left join bcv_lid_map l on b.lid=l.lid left join bible_books_look_up bb on l.book=bb.book_id \
           where b.verse like '%" + token + "%' and bb.book_code='" + book +"' order by l.lid")
    book_concordance = getConcordanceList(cursor.fetchall())
    cursor.execute("select bb.book_code, bb.book_name, l.chapter, l.verse, b.verse from " + tablename + " b \
       left join bcv_lid_map l on b.lid=l.lid left join bible_books_look_up bb on l.book=bb.book_id \
           where b.verse like '%" + token + "%' and bb.book_code!='" + book +"' order by l.lid \
               limit 100")
    all_books_concordance = getConcordanceList(cursor.fetchall())
    return json.dumps({
        book:book_concordance,
        "all":all_books_concordance
    })


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

@app.route("/v1/versiondetails", methods=["GET"], defaults={'contentId': None,'languageId':None})
@app.route("/v1/versiondetails/<contentId>/<languageId>", methods=["GET"])
def getVersionDetails(contentId, languageId):
    connection = get_db()
    cursor = connection.cursor()
    if languageId:
        cursor.execute("select s.source_id, s.version_content_code, s.version_content_description, s.year, \
            s.license, s.revision, c.content_type, l.language_name from sources s left join \
                content_types c on s.content_id=c.content_id left join languages l on \
                    s.language_id=l.language_id where s.content_id=%s and s.language_id=%s", (\
                        contentId, languageId))
    else:

        cursor.execute("select s.source_id, s.version_content_code, s.version_content_description, s.year, \
            s.license, s.revision, c.content_type, l.language_name from sources s left join \
                content_types c on s.content_id=c.content_id left join languages l on \
                    s.language_id=l.language_id",)
    rst = cursor.fetchall()
    version_details = [
        {
            "sourceId":sourceId,
            "versionContentDescription":versioncontentdescription,
            "versionContentCode":versioncontentcode,
            "year":year,
            "license":license,
            "revision": revision,
            "contentType":contenttype,
            "languageName":languagename,
        } for sourceId, versioncontentcode, versioncontentdescription, year, license, revision, contenttype, languagename in rst
    ]
    cursor.close()
    return json.dumps(version_details)

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

def getTokens(text):
    crossRefPattern = re.compile(r'(\(?(\d+\s)?\S+\s\d+:\d+\,?\)?)')
    footNotesPattern = re.compile(r'\it(.*)\s?\\f\s?\+.*\\ft\s?(.*)\s?\\f\*\\it\*\*')
    content = re.sub(crossRefPattern, '', text)
    content = re.sub(footNotesPattern, '', content)
    content = re.sub(r'([!\"#$%&\\\'\(\)\*\+,\.\/:;<=>\?\@\[\]^_`{|\}~\”\“\‘\’।0123456789])',"",content)
    content = re.sub(r'\n', ' ', content)
    content = content.strip()
    tokenSet = set(content.split(' '))
    # tokenList = list(tokenSet)
    return tokenSet

def parsePunctuations(text):
    content = re.sub(r'([!\"#$%&\\\'\(\)\*\+,\.\/:;<=>\?\@\[\]^_`{|\}~\”\“\‘\’।0123456789])',"",text)
    return content

def parsePunctuationsForDraft(text):
    content = re.sub(r'([!\"#$%&\\\'\(\)\*\+,\.\/:;<=>\?\@\[\]^_`{|\}~\”\“\‘\’।])',r" \1",text)
    return content

def parseDataForDBInsert(usfmData):
    connection = get_db()
    crossRefPattern = re.compile(r'(\(?(\d+\s)?\S+\s\d+:\d+\,?\)?)')
    footNotesPattern = re.compile(r'\it(.*)\s?\\f\s?\+.*\\ft\s?(.*)\s?\\f\*\\it\*\*')
    cursor = connection.cursor()
    cursor.execute("select lid, book, chapter, verse from bcv_lid_map")
    lidDict = {int(str(b).zfill(3) + str(c).zfill(3) + str(v).zfill(3)):l for l,b,c,v in cursor.fetchall()}
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
            lid = lidDict[bcv]
            dbInsertData.append((lid, verseText, crossRefs, footNotes))
            verseContent.append(verseText)
    tokenList = list(getTokens(' '.join(verseContent)))
    tokenList = [(bookId, token) for token in tokenList]
    # 
    return (dbInsertData, tokenList, bookId)

def createTableCommand(fields, tablename):
    command = 'CREATE TABLE %s (%s)' %(tablename, ', '.join(fields))
    return command


@app.route("/v1/uploadsources", methods=["POST"])
def uploadSource():
    req = request.get_json(True)
    language = req["languageCode"]
    contentType = req["contentType"]
    versionContentCode = req["versionContentCode"]
    versionContentDescription = req["versionContentDescription"]
    year = req["year"]
    revision = req["revision"]
    license = req["license"]
    wholeUsfmText = req["wholeUsfmText"]
    parsedUsfmText = req["parsedUsfmText"]
    connection = get_db()
    cursor = connection.cursor()
    bookCode = parsedUsfmText["metadata"]["id"]["book"].lower()
    cleanTableName = "%s_%s_%s_bible_cleaned" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
    tokenTableName = "%s_%s_%s_bible_tokens" %(language.lower(), versionContentCode.lower(), str(revision).replace('.', '_'))
    cursor.execute("select language_id from languages where language_code=%s", (language,))
    languageId = cursor.fetchone()[0]
    cursor.execute('select content_id from content_types where content_type=%s', (contentType,))
    contentId = cursor.fetchone()[0]
    cursor.execute("select s.source_id from sources s left join languages l on \
        s.language_id=l.language_id left join content_types c on s.content_id=c.content_id \
            where l.language_code=%s and c.content_type=%s and s.version_content_code=%s and \
                s.version_content_description=%s and s.year=%s and s.revision=%s and \
                    s.license=%s",(language, contentType, versionContentCode, 
                        versionContentDescription, year, revision, license))
    rst = cursor.fetchone()
    
    newSource = False
    if not rst:
        create_clean_bible_table_command = createTableCommand(['lid INT NOT NULL', 'verse TEXT', \
            'cross_reference TEXT', 'foot_notes TEXT'], cleanTableName)
        create_token_bible_table_command = createTableCommand(['token_id BIGSERIAL PRIMARY KEY', \
            'book_id INT NOT NUll', 'token TEXT NOT NULL'], tokenTableName)
        cursor.execute(create_clean_bible_table_command)
        cursor.execute(create_token_bible_table_command)
        usfmText = {
            bookCode: wholeUsfmText
        }
        parsedJsonText = {
            bookCode: parsedUsfmText
        }
        usfmTextJson = json.dumps({
            "usfm": usfmText,
            "parsedJson": parsedJsonText
        })
        cursor.execute('insert into sources (version_content_code, version_content_description,\
         table_name, year, license, revision, content_id, language_id, usfm_text) values \
             (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (versionContentCode, versionContentDescription, \
                 cleanTableName, year, license, revision, contentId, languageId, usfmTextJson))
        newSource = True
    
    cursor.execute("select usfm_text from sources where table_name=%s", (cleanTableName,))
    usfm_rst = cursor.fetchone()[0]
    
    usfmFile = usfm_rst["usfm"]
    parsedJsonFile = usfm_rst["parsedJson"]
    # 
    if bookCode in usfmFile and newSource:
        pass
    elif bookCode not in usfmFile:
        usfmFile[bookCode] = wholeUsfmText
        parsedJsonFile[bookCode] = parsedUsfmText
        usfmText = json.dumps({
            "usfm": usfmFile,
            "parsedJson": parsedJsonFile
        })
        cursor.execute('update sources set usfm_text=%s where source_id=%s', (usfmText, rst[0]))
    # if bookCode not in usfmFile:
    else:
        
        return '{"success":false, "message":"Book %s already inserted into database"}' %(bookCode)
    parsedDbData, tokenDBData, bookId = parseDataForDBInsert(parsedUsfmText)
    
    cursor.execute('insert into ' + cleanTableName + ' (lid, verse, cross_reference, foot_notes) values '\
        + str(parsedDbData)[1:-1])
    # cursor.execute('insert into ' + tokenTableName + ' (book_id, token) values ' + str(tokenDBData)[1:-1])
    
    try:
        phrases.tokenize(connection, language.lower(), versionContentCode.lower()+'_'+str(revision).replace('.', '_') , bookId)
    except Exception as ex:
        
        return '{"success":false, "message":"Phrases method error"}'
    
    connection.commit()
    cursor.close()
    return '{"success":true, "message":"Inserted %s into database"}' %(bookCode)
    

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
        # translation = translation
        
        
        
        checkSenses = '|'.join(senses)
        if checkSenses == rst[2] and translation == rst[1]:
            return '{"success":false, "message":"No New change. This data has already been saved"}'
        if checkSenses != rst[2] and translation == rst[1]:
            
            if rst[2] == "":
                senses = checkSenses
            else:
                senses = rst[2] + '|' + checkSenses
            # senses = rst[2]
        if checkSenses == rst[2] and translation != rst[1]:
            senses = checkSenses
        
        
        
        senses = '|'.join(list(set(senses.split('|'))))
        cursor.execute("update translations set translation=%s, user_id=%s, senses=%s where source_id=%s and \
            target_id=%s and token=%s",(translation, userId, senses, sourceId, targetLanguageId, token))
        cursor.execute("insert into translations_history (token, translation, source_id, target_id, \
            user_id, senses) values (%s, %s, %s, %s, %s, %s)", (token, translation, sourceId, targetLanguageId, \
                userId, senses))
        connection.commit()
        cursor.close()
        return '{"success":true, "message":"Translation has been updated"}'


@app.route("/v1/info/translatedtokens", methods=["GET"])
def getTransaltedTokensInfo():
    connection = get_db()
    cursor = connection.cursor()
    # cursor.execute("select distinct s.language, target_id from translations")
    # sourceIds = cursor.fetchall()
    # sourceIds = [x[0] for x in sourceIds]


    cursor.execute("select distinct r.version_content_code, l.language_name, r.language_name \
    from translations t left join (select distinct s.source_id, s.version_content_code, \
    ll.language_name  from translations tt left join sources s on tt.source_id=s.source_id \
        left join languages ll on s.language_id=ll.language_id) \
    r on t.source_id=r.source_id left join languages l on t.target_id=l.language_id")
    rst = cursor.fetchall()
    # 
    tokenInformation = {}
    for v,t,s in rst:
        
        if s in tokenInformation:
            temp = tokenInformation[s]
            if v in temp:
                temp[v] = temp[v] + [t]
            else:
                temp[v] = [t]
            tokenInformation[s] = temp
        else:
            tokenInformation[s] = {
                v:[t]
            }
    # tokenInformationList = [{k:v} for k,v in tokenInformation.items()]
    return json.dumps(tokenInformation)


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
def downloadDraft():
    req = request.get_json(True)
    sourceId = req["sourceId"]
    targetLanguageId = req["targetLanguageId"]
    bookList = req["bookList"]
    connection = get_db()
    cursor = connection.cursor()

    
    usfmMarker = re.compile(r'\\\w+\d?\s?')
    nonLangComponents = re.compile(r'[!"#$%&\\\'()*+,./:;<=>?@\[\]^_`{|\}~”“‘’।0-9]+')
    
    if phrases.loadPhraseTranslations(connection, sourceId, targetLanguageId):
        cursor.execute("select book_id, book_code from bible_books_look_up where book_code=%s", (bookList[0],))
        bookId, bookCode = cursor.fetchone()
        
        # tokenTranslatedDict = {k:v for k,v in rst}
        cursor.execute("select usfm_text from sources where source_id=%s", (sourceId,))
        source_rst = cursor.fetchone()
        usfmText = source_rst[0]['usfm'][bookCode]
        usfmLineList = []
        
        
        for line in usfmText.split('\n'):
            usfmWordsList = []
            nonLangComps = []
            markers_in_line = re.findall(usfmMarker,line)
            for word_seq in re.split(usfmMarker,line):
                nonLangComps += re.findall(nonLangComponents,word_seq)
                clean_word_seq = re.sub(nonLangComponents,' ### ',word_seq)
                translated_seq = [ phrases.translateText( clean_word_seq.strip() ) ]
            for i,marker in enumerate(markers_in_line):
                usfmWordsList.append(marker)
                usfmWordsList.append(translated_seq[i])
            if i+1<len(translated_seq):
                usfmWordsList += translated_seq[i+1:]
            
            outputLine = " ".join(usfmWordsList)
            
            for comp in nonLangComps:
                outputLine = re.sub(r'<###>',comp,outputLine,1)
            
            usfmLineList.append(outputLine)
        translatedUsfmText = "\n".join(usfmLineList)
        return json.dumps({
            "translatedUsfmText": translatedUsfmText
        })
    



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

