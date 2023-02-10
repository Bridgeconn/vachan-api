## Instructions to add new languages stopwords


### File adding steps

```
folder : db/csvs/stop_words

filename : languagename.csv (eg: hindi.csv)

csv headers :- 
    language_id : languageid (eg:100018)
    stopword : stopword text
    confidence :  value should be 2
    created_user :  value should be NULL
    last_updated_user :  value should be NULL
    active : True
```

### Change in seed_DB file

- open file `seed_DB.sql` in db/
- find COPY command for stopword csv in the seed_DB file (It will be after `CREATE TABLE public.stopwords_look_up`)
- duplicate the one COPY command and replace the csv file name with new language file name added in the db/csvs/stop_words folder

eg:
```
language file name : arabic.csv

copy command :

\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/arabic.csv' DELIMITER ',' CSV HEADER;
```