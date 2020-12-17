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

### bible_books_look_up

* Stores the bible book names, ids and codes in an external CSV file and copies to table as seed data. Ealier it was being added as 66 insert statements within the seed DB creation script.
* We are now using book_id = 41 for Matthew, instead of 40 we used in version 1.This will increment all book_ids in NT by one. This is done as per [the standard followed in USFM]()https://github.com/ubsicap/usfm/blob/master/docs/identification/books.rst

### commentaries table

* we were using one `verse` field in V1. Now we have `verse_start` and `verse_end` in its place. 
This is done because, from the data we have on V1, it is clear that all entries in them have verse ranges instead of one verse. We were using `text` type for that field and indicating range as `1-10` separated by `-`. The only exceptions were in chapter introductions which has `0` for verse field. As querying this text field is less efficient in terms of performance as well as expressibility, it has been modiifed as two `int` fields. We continue to use `0` to indicate chapter intro and `-1` to indicate chapter epilogue for `verseStart` and `verseEnd`.
