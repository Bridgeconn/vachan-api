# Vachan API Version 2
# Change Log


## Logging

Uses 4 logging levels, DEBUG, INFO, WARNING and ERROR. The level can be set with environment variables. The recommended logging level for production deployment is WARNING and for development, it is DEBUG.

On entering every method, writes to log(INFO) that execution starts in that method. Also writes(DEBUG) the various parameters received to it. Then before rasing any error, write to the log(ERROR), the name of the method where the error has occured, the URL details, client IP and also the details of the error. Uses WARNING to note special situations.

The maximum file size for log file is set as 10000000 bytes. After which logging starts on a new file, renaming the old one appending .1, .2, .3 etc to it. The number of back up log files to be kept is set as 10.

## Testing

Adds seperate  set of tests for each API endpoint. Has both positive and negative testcases in each set.

For testing, it connects to the original database, but rolls back all the changes after each test function. So each test is independant of each other from a DB perspective.

For every API endpoint, we perform certain common tests like checking for the correct response object with the default parameters, validation of each of the parameters based on their types, value, etc plus more tests based on itsown bussiness logic.

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
