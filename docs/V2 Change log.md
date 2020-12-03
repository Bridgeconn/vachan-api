# Vachan API Version 2
# Change Log


## Logging

Uses 4 logging levels, DEBUG, INFO, WARNING and ERROR. The level can be set with environment variables. The recommended logging level for production deployment is WARNING and for development, it is DEBUG.

On entering every method, writes to log(INFO) that execution starts in that method. Also writes(DEBUG) the various parameters received to it. Then before rasing any error, write to the log(ERROR), the name of the method where the error has occured, the URL details, client IP and also the details of the error. Uses WARNING to note special situations.

The maximum file size for log file is set as 10000000 bytes. After which logging starts on a new file, renaming the old one appending .1, .2, .3 etc to it. The number of back up log files to be kept is set as 10.

## Testing

Adds seperate  set of tests for each API endpoint. Has both positive and negative testcases in each set.

For testing, it connects to the original database, but rolls back all the changes after each test. So each test is independant of each other from a DB perspective.

## Database Changes

### content_types table

* Removes column 'key'. Can be used in appropriate metadata field of sources table, if required even after the implementation of authorizations module.
* Renames column `content_id` to `content_type_id`
* Removes the sequence used for content_id and use SERIAL datatype instead.
* Adds bible, commentary and infographics as before to the table as seed data. Changes translation_words to dictionary. Also adds bible_video as a content type. 

