# Vachan API Version 2
# Change Log


## Logging

Uses 4 logging levels, DEBUG, INFO, WARNING and ERROR. The level can be set with environment variables. The recommended logging level for production deployment is WARNING and for development, it is DEBUG.

On entering every method, writes to log(INFO) that execution starts in that method. Also writes(DEBUG) the various parameters received to it. Then before rasing any error, write to the log(ERROR), the name of the method where the error has occured, the URL details, client IP and also the details of the error. Uses WARNING to note special situations.

The maximum file size for log file is set as 10000000 bytes. After which logging starts on a new file, renaming the old one appending .1, .2, .3 etc to it. The number of back up log files to be kept is set as 10.

## Testing

Adds tests for each API endpoint. Has both positive and negative testcases for each one. The tests relating to one set of APIs(normally those APIs that do GET, PUT and POST operations on one type of DB table) are added per test file, for having modularity.

For testing, it connects to the original database, but rolls back all the changes after each test function. So each test fuction is independant of each other from a DB perspective. This allows us to run tests selectively.

For every API endpoint, we perform certain common tests like checking for the correct response object with the default parameters, validation of each of the parameters based on their types, value, etc plus more tests based on itsown bussiness logic.

#### Issue in dynamic table creation

For testing, we normally use a separate database transaction, which is rolled back after each test function, there by, undoing all DB operations we performed during the test.

In the testing of APIs of dynamic tables(bibles, commentaries etc), the source creation APIs, called by the test client, create new tables in DB. These table creation operations are performed not as transactions attached to the open session, but are bound to the engine(that is how it is done in SQLAlchemy), which makes it not possible to undo by rolling back the session or transaction. 

The effect it makes is that, the tables thus created would remain in the DB even after testing. They will be empty as we are able to roll back all insert or update operations on it. We have created the table creation procedure such that, this wont throw an error when a new table has to be created in same name(when we run the same test next time). But it does show a warning like shown below when we create a new table of same name. 

```SAWarning: This declarative base already contains a class with the same class name and module name as db_models.hin_TTT_1_commentary, and will be replaced in the string-lookup table.```

If we are running tests on local machines, or on git actions, I think this can be overlooked. It will only be an issue if we are to run the tests on (staging) servers. Then also it wont create any issue that prevents the normal functioning of the app, just that a few empty tables will be left as residue in the staging database.

## Deactivation of contents

An active field is included in `sources` table as well as the dynamic tables like `commentaries`, `dictionary`, `bible` etc. This is by default set as `True` indicating the content is active. It can be set to `False` using the `PUT` API of respective table. The `GET`  methods take an optional param `active` to filter active and deactivated contents, which is by default set as `True` returning only active contents on all fetches unless specified other wise. This enables us to implement a soft delete feature. 

Having this on `sources` tables allows us to deactivate an entire source(one table) and having it on other tables allow item vice deactivation like selected commentaries in a set, one book of a bible etc.

## Database Changes

### content_types table

* Removes column 'key'. Can be used in appropriate metadata field of sources table, if required even after the implementation of authorizations module.
* Renames column `content_id` to `content_type_id`
* Removes the sequence used for content_id and use SERIAL datatype instead.
* Adds bible, commentary and infographics as before to the table as seed data. Changes translation_words to dictionary. Also adds bible_video as a content type. 

### languages table

* Removes the sequence used for language_id and use SERIAL datatype instead.
* Removes the language_id from the CSV file used to import the seed languages list. This was done to make sure the sequence value for the ID column would work properly.
* Uses `char(3) UNIQUE NOT NULL` for language_code instead of just `text`
* Makes language_name `NOT NULL`
* Removes the columns local_script_name and script, which did not have value for any of the rows in seed data and wasn't being used by any of the Apps.
* Sets `'left-to-right'` as the default value for script direction at DB itself. This ensures that the 7K languages imported from CSV as seed data, which didnot have this value set, will also have a default value for this column.

### versions table

* Removes the sequence used for version_id and use SERIAL datatype instead.
* Uses integer data type for revision field, instead of text, to avoid any special character coming in, as its value is to be used in table name.
* Make the combination of version_code and revision unique
* Sets default value of revision as 1

### sources table

* Removes the sequence used for source_id and use SERIAL datatype instead.
* The field, table_name, is made unique
* Adds four columns created_at, created_user, last_updated_at, last_updated_user to track DB changes. the first two are to be set while source creation. The other two, when a user performs any action on the respective content tables.(These two columns are not for tracking updations on sources table rows but the actual content tables like hin_IRV_1_bible)
* Renames the column status to active, which is used for soft delete and re-activation.
* filed `license` is changed to a FK, referncing the license row in `licenses` table, intead of storing the actual license here, it defaults to CC-BY-SA(Creative Commons License)

### bible_books_look_up

* Stores the bible book names, ids and codes in an external CSV file and copies to table as seed data. Ealier it was being added as 66 insert statements within the seed DB creation script.
* We are now using book_id = 41 for Matthew, instead of 40 we used in version 1.This will increment all book_ids in NT by one. This is done as per [the standard followed in USFM]()https://github.com/ubsicap/usfm/blob/master/docs/identification/books.rst

### commentaries table

* we were using one `verse` field in V1. Now we have `verse_start` and `verse_end` in its place. 
This is done because, from the data we have on V1, it is clear that all entries in them have verse ranges instead of one verse. We were using `text` type for that field and indicating range as `1-10` separated by `-`. The only exceptions were in chapter introductions which has `0` for verse field. As querying this text field is less efficient in terms of performance as well as expressibility, it has been modiifed as two `int` fields. We continue to use `0` to indicate chapter intro and `-1` to indicate chapter epilogue for `verseStart` and `verseEnd`.
* Combination of fields `book_id`, `chapter`, `verse_start`, `verse_end` are made unique. This acts as a composite candidate key for updation of `commentary` field. Only the `commentary` field is editable via API.
* adds an `active` field to enable row(item) vice soft delete
 

### dictionary table

Currently we only have Strongs numbers as a dictionary table.
But we can have a wide variety of lexical collections with varying informations required to be stored in the DB. So chhosing a flexible table structure and APIs to accomodate future needs.
* Have only 3 predefined columns; `word_id`, `word` and `details`
* `details` column will be of JSON datatype and will have all the additional info we have in that collection(for each word) as key-value pairs
* querying is possible based on any of the key value pair in `details`
* In `details` field, updation is not possible on single key value pair, but only as the whole object.
* adds an `active` field to enable row(item) vice soft delete

### infographics table

* The combination of `book_id` and `title` is made unique, and is used are a composite candidate key for updation of `infograhic_url`, which is the only field editable via API.
* The field `filename` is renamed as `infographic_url`. 
* Though the type is `Text` for `infographic_url` in database, from the python code it ensures that, only a proper URL can be added to this field.
* The `infographic_url` field is not unique which would allow the same link to be added for multiple books, if applicable.
* adds an `active` field to enable row(item) vice soft delete

### bible_video table

* `biblevideo` is made an entry in contentTypes table
* New source to be added to sources table and new table to be created for every language, at least(if version name and revision are same)
* removes the field language from the table
* field `books` has datatype array of strings, instead of comma separated text. (From the python code it is ensured that it accept only valid book codes, becasue array of FKs is not possible)
* `title` field is made unique(for one table. Repetition is possible with different language, version or revision) and is used to identify rows uniquely for updation. `title` field cannot be altered via API.


### infographic table

* `infographic` made an entry in content types table and they are now required to be entered in sources table providing the langugage, version,  and revision details. Thus the table naming will be in uniformity with other tables in lang_ver_rev_contenttype pattern
* `title`, `book` combination is made unique.
* `file_name` field is changed to a `url` field requiring it to a complete path(can use file://, http:// or other protocols)

### bible, bible_cleaned, bible_audio tables

* `footnotes` and `cross-ref` filed are removed from `bible_cleaned` tables. As they are not used anywhere now. If required, it can be added as separate tables related to same source, avoiding the sparse fileds in bible_cleaned tables
* `active` fields are added enabling book wise de-activation in bible, bible_cleaned tables
* `bible_audio` tables are made dynamic tables associated with each of the bible sources like `bible_cleaned` tables, instead of the single predefined table before. But POST and PUT operations are defined separatelt for this table enabling bulk updates from CSVs as before.

### licenses table

* New table. Stores the full text of the license, a short name called code and name. Allows the users to upload licenses of there own and connect them to contents uploaded in DB
* `license_code` is used to uniquely identify the rows via APIs even though there is another autogenerated PK field, similar to othet tables in DB
* referenced by sources table
* Two licenses ISC and CC-BY-SA are pre-loaded, and all sources, if not specified, defaults to CC-BY-SA
