from flask import Flask, render_template, request
from flask_restful import Api, Resource
import os, logging


logging.basicConfig(filename='API_logs.log', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
sendinblue_key = os.environ.get("VACHAN_SENDINBLUE_KEY")
jwt_hs256_secret = os.environ.get("VACHAN_HS256_SECRET", "x709myFlW5")

postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("VACHAN_POSTGRES_PORT", "5432")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres") 
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret") 
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "vachan_local") 
host_api_url = os.environ.get("VACHAN_HOST_API_URL", "localhost:8000")
host_ui_url = os.environ.get("VACHAN_HOST_UI_URL","autographamt.com")
system_email = os.environ.get("MTV2_EMAIL_ID", "autographamt@gmail.com")


app = Flask(__name__)
api = Api(app)



##### Database ####

class Database(Resource):
    def get(self):
		# intialize a DB connection
        pass

api.add_resource(Database, '/', endpoint = '')

#################

##### Content types #####

class ContentType(Resource):
    def get(self):
		# fetches all the contents types supported in the DB and their details 
        pass

    def post(self):
    	# input: a list of contents to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'contentType': "name", 
		#			'dbTtables': "SQL statement for creation of required tables"}, {}, ...]
    	# create a new content type in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'contentId':
    	#		'<column name>': "new value"}, {}, ...]

    def delete(self):
    	# input: list of content_id s to be deleted
   		# set the active column as false(to re-activate the put method can be used)
        pass

api.add_resource(ContentType, '/contenttype', endpoint = 'contenttype')

# DB changes needed with this:
#	1. Add a new column DB_tables to the content_type tables 
#	which specifies the SQL commands for new tables required for the corresponding content type(except for dictionary whihch may have varying schemas)
#	2. Add a column "active", with bool type
#	 to allow soft delete and reactivation
#	3. if there is a password column in this table, move that to the metadata column of 
#	 sources or versions table which ever is appropriate to the content in question
#################

##### languages #####

class Language(Resource):
    def get(self):
		# fetches all the languages supported in the DB and their code 
        pass

    def get(self, language_code):
		# checks if the language code is valid, if yes returns the details of the selected language
        pass


    def post(self):
    	# input: a list of languages to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'language': "name", 
		#			'code': "",
		#			"localScriptName":"",
		#			"script":"",
		#			"scriptDirection":""}, {}, ...]
    	# create a langugae entry in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'languageId':
    	#		'<column name>': "new value"}, {}, ...]

    def delete(self):
    	# input: list of language_ids to be deleted
   		# set the active column as false(to re-activate, the put method can be used)
        pass

api.add_resource(Language, '/language', endpoint = 'language')
api.add_resource(Language, '/language/<text:language_code>', endpoint = 'language')
################################


##### Version #####

class Version(Resource):
    def get(self):
		# fetches all the versions avaliable for each content type in the DB and their details 
        pass

    def post(self):
    	# input: a list of versions to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'versionName': "",
    	#			'description': "".
    	#			'revision': "", 
		#			'metadata': ""}, {}, ...]
    	# create a new version in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'versionId':
    	#		'<column name>': "new value"}, {}, ...]

api.add_resource(Version, '/version', endpoint = 'version')

#################


##### Source #####

class Source(Resource):
    def get(self):
		# fetches the details of all the active entries in the sources table
        pass

    def get(self, source_id):
    	# fetches the details of the specifed entry in the sources table
    	pass

    def get(self, content_type):
    	# fetches the list of all sources of the specifed content type and their details
    	pass

    def get(self, content_type, language_code):
    	# fetches the list of all sources of the specifed content type & language and their details
    	pass


    def post(self):
    	# input: a list of items to be added to sources table(all post, put and delete methods accept list of items for consistancy)
    	#		[{"sourceName":""
    	#		  "contentType":"",
    	#		  "languageCode":"",
    	#		  "versionName":"",
    	#		  "year":"",
    	#		  "license":""}, {}, ....]
    	# add a new entry to the sources table for each item in the list.
    	# for each new source, depending upon the content type, create necessary new tables in the DB, and add the table name to the sources table
    	#	example, for bible, create the bible table, bible_clean table. (create the bible_tokens table only in the tokenization API)
    	#	for other content types, create one table with predefined schema

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'sourceId':
    	#		'<column name>': "new value"}, {}, ...]


    def delete(self, source_id):
    	# input: list of source_ids to be deleted
   		# set the active column as false(to re-activate the put method can be used)
        pass

api.add_resource(Source, '/source', endpoint = 'source')
api.add_resource(Source, '/source/<int:source_id>', endpoint = 'source')
api.add_resource(Source, '/source/<text:content_type>', endpoint = 'source')
api.add_resource(Source, '/source/<text:content_type>/<text:language_code>', endpoint = 'source')

# Point to discuss
# uses language code, content name, version name etc, instead of their ID values like in previous implementation

#################

#### Bible #######
class Bible(Resource):
    def get(self, source_id):
		# fetches the details of the specified bible
		# like, verision, revision, language, books present
        pass

    def get(self, source_id, book_code, output_type):
    	# input: output_types can be usfm, json or text.
    	# if text, returns cleaned contents in .._bible_cleaned table. 
    	# otherwise, from corresponding column of .._bible table
		# fetches contents of the entire book
		# 
        pass


    def get(self, source_id, book_code, chapter, output_type):
    	# input: output_types can be usfm, json or text.
    	# if output_type is usfm,then split the usfm contents by '\c',
    	#    check the chapter number of each slice and return the appropriate slice.
    	#	 include the usfm head section also with the content if chapter is 1
        pass

    def get(self, ref_id_start, ref_id_end):
    	# input: ref_id s can be used smartly to specify any kind of range. It need not be a valid ref_id 
    	# 		for example to get all verses of chapter 3 of book 5 we can use 
    	# 			ref_id_start = 5003000, ref_id_end= 5004000
    	# This APi always returns cleaned text from the .._bible_cleaned table. 
    	#     if foot-note or cross-ref is present for a verse, returns that too
    	#		[{'ref_id':'',
    	#			'verse':"",
    	#			'cross-ref':'',
    	#			'foot-note':''}, {}, ...]
   		pass


    def post(self):
    	# input: a list of bible books to be added(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'sourceId': "", 
		#			'usfm': "",
		#			"json":""}, {}, ...]
    	# Adds the contents to .._bible table and .._bible_cleaned table, if contents not already present for the books uploaded
    	pass

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'souceId':
    	#		'usfm': "new value",
    	#		'json':"", }, {}, ...]
    	# unlike in other put methos, both columns(usfm & json) and values are mandatory in this, 
    	# as they are inter-dependant values
    	pass


api.add_resource(Bible, '/bible', endpoint = 'bible')
api.add_resource(Bible, '/bible/book/<int:source_id>/<text:book_code>/<text:output_type>', endpoint = 'bible/book')
api.add_resource(Bible, '/bible/book/chapter/<int:source_id>/<text:book_code>/<int:chapter>/<text:output_type>', endpoint = 'bible/book/chapter')
api.add_resource(Bible, '/bible/verse/<int:source_id>/<int:ref_id_start>/<int:ref_id_end>', endpoint = 'bible/verse')

### points to discuss, ############
# 	1. do we need provision to delete each uploaded  book ?
#       we do have 'put' if you need to update it
#	2. Do we need a /bible get API to list all bibles(/sources/<text:content_type> does that now) ?

#############################

##### Bible Books #####

class BibleBook(Resource):
    def get(self):
		# fetches all the bible book names(Eng) and codes 
        pass

    def get(self, language_code):
		# fetches all the bible book details in the specified language
        pass


    def post(self):
    	# input: a list of bible book name details in any of languages to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'bookId': "",
    	#			'languageId': "".
    	#			'abbr': "", 
		#			'shortName': ""
		#			'longName': ""}, {}, ...]
    	# Note: only bible_book_names table can be updated. Not the bible books look up

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'versionId':
    	#		'<column name>': "new value"}, {}, ...]

api.add_resource(BibleBook, '/biblebook', endpoint = 'biblebook')
api.add_resource(BibleBook, '/biblebook/<text:language_code>', endpoint = 'biblebook')

##### DB chande suggested #######

# change the columns name from 
#	1. 'short' to 'short_name', 
#	2. 'long' to 'long_name' and 
#	3. 'abbr' to 'abbreviation' 

##################################


##### Commentry #####

class Commentary(Resource):
    def get(self, source_id):
		# fetches the details of the specified commentary
		# like, verision, revision, language, books present
        pass

    def get(self, source_id, book_code):
		# fetches commentary of the entire book
        pass


    def get(self, source_id, book_code, chapter):
		# fetches commentary of the selected chapter of the book
        pass

    def get(self, ref_id_start, ref_id_end):
    	# input: ref_id s can be used smartly to specify any kind of range. It need not be a valid ref_id 
    	# 		for example to get all commnataries of chapter 3 of book 5 we can use 
    	# 			ref_id_start = 5003000, ref_id_end= 5004000
   		pass

    def post(self):
    	# input: a list of commentries to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'sourceId': "",
    	#			'bookId': "".
    	#			'chapter': "", 
		#			'verseNumber': "", 
		#			"commentary":""}, {}, ...]
    	# create a new row in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'sourceId':
    	#		'book': "", "chapter": "", "verse": "", 'commentary': "new value"}, {}, ...]
    	#		All keys in the input json are mandatory as th book-chapter-verse is the unique identifier of the row

api.add_resource(Commentary, '/commentary', endpoint = '/commentary')
api.add_resource(Bible, '/commentary/<int:source_id>/<int:ref_id_start>/<int:ref_id_end>', endpoint = '/commentary')
api.add_resource(Bible, '/commentary/book/<int:source_id>/<text:book_code>', endpoint = '/commentary/book')
api.add_resource(Bible, '/commentary/book/chapter/<int:source_id>/<text:book_code>/<int:chapter>', endpoint = '/commentary/book/chapter')

###### DB changes suggested ##############
#	1. have a consitant pattern in table names
#			at present, some table ends with 'notes'(hin_irv_notes) and another with 'commentary' (eng_mhcc commentary) 
#			have a common last word like the bible tables
#		language_code + version + revision(if present) + contentType can be considered for all content table names
############################################


########### Dictionary ###################
class Dictionary(Resource):
    def get(self, source_id):
		# fetches the details of the specified dictionary
		# like, verision, revision, language
        pass

    def get(self, source_id, word_pattern):
		# input: word_pattern can be the full or partial value of the word column
		#		for the entire contents of the dictionary an _ can be passed for word_pattern
		# the API should be written in a way, so that different column names can be handled, 
		#	in case, different dictionary tables have different fields 
        pass

    def post(self):
    	# input: a list of commentries to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'sourceId': "",
    	#			fieldOne: }, {}, ...]
    	# create a dictionary table with schema as per the input values(if not already created) and add values to it

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'sourceId':"",
    	#		'keyword':"",
    	#		'<column name>': "new value"}, {}, ...]

api.add_resource(Dictionary, '/dictionary', endpoint = '/infographics')
api.add_resource(Dictionary, '/dictionary/<int:source_id>', endpoint = '/infographics')
api.add_resource(Dictionary, '/dictionary/<int:source_id>/<text:word_pattern>', endpoint = '/infographics')

#	1. have a consitant pattern in table names by adding dictionary to the end 
#		language_code + version + revision(if present) + contentType can be considered for all content table names
###########################################



########### Infographic ###################

class Infographics(Resource):
    def get(self, source_id):
		# fetches the details of the specified infographic
		# like, verision, revision, language, books present
        pass

    def get(self, source_id, book_code):
		# fetches infographics of the selected book
        pass

    def post(self):
    	# input: a list of commentries to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'sourceId': "",
    	#			'bookId': "",
		#			"infographics":""}, {}, ...]
    	# create a new version in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'sourceId':
    	#		'bookId': "", 
    	#		'infographics': "new value"}, {}, ...]
    	#		All fields in the input json are mandatory 

api.add_resource(Infographics, '/infographics', endpoint = '/infographics')
api.add_resource(Infographics, '/infographics/<int:source_id>', endpoint = '/infographics')
api.add_resource(Infographics, '/infographics/<int:source_id>/<text:book_code>', endpoint = '/infographics')


###########################################


########### Audio bible ###################
class AudioBible(Resource):
    def get(self, bible_source_id):
		# fetches the details of the audio bible
		# available for the specified bible
        pass

    def get(self, bible_source_id, book_code):
		# fetches details of the audio bible
		# available for the specified bible and book
        pass

    def post(self):
    	# input: a list of audio bible details to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'sourceId': "",
    	#			'name': "",
		#			"url":"",...}, {}, ...]
    	# create a new version in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'auidoId':
    	#		'<column name>': "new value"}, {}, ...]

api.add_resource(AudioBible, '/audiobible', endpoint = '/audiobible')
api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>', endpoint = '/audiobible')
api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>/<text:book_code>', endpoint = '/audiobible')

### DB change ####
# field books should accept only valid book codes(or list of book_codes)

###########################################


########### bible videos ###################
class AudioBible(Resource):
    def get(self, id):
		# fetches the details of the bible video
        pass

    def get(self, language_code):
		# fetches details of the bible videos available in that language
        pass

    def get(self, language_code, book_code):
		# fetches details of the bible videos available in that language and book
        pass

    def post(self):
    	# input: a list of video bible details to be created(all post, put and delete methods accept list of items for consistancy)
    	#		 [{'title':"",
    	#			'book': "",
		#			"languageCode":"",...}, {}, ...]
    	# create a new entry in the DB

    def put(self):
    	# input: list of updations(all post, put and delete methods accept list of items for consistancy)
    	#		[{'videoId':
    	#		'<column name>': "new value"}, {}, ...]

api.add_resource(AudioBible, '/audiobible', endpoint = '/audiobible')
api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>', endpoint = '/audiobible')
api.add_resource(AudioBible, '/audiobible/<int:bible_source_id>/<text:book_code>', endpoint = '/audiobible')


### DB change ####
# field books should accept only valid book codes(or list of book_codes)

###########################################