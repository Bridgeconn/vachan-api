# **Database Changes Log for Release**
This document captures all database modifications made during each release . It will serve as a reference guide for future deployments, promoting consistency and ease of use across different setups.


##  **Beta.31:**
#### **Release Date : 19-09-2023**
#### **Commit Id :7f38ac0b5008341cd923d4cc1d769b2fee47f67a**
#### **PR: [#715](https://github.com/Bridgeconn/vachan-api/pull/715/)**
This release includes:
- db changes in commentary
    - `chapter`.`verseStart` and `verseEnd` columns are removed
    - new json field `reference` is added which includes `book`,`chapter`,`verseNumber`,`bookEnd`,`chapterEnd` and `verseEnd`
- Actions performed
    - Delete all tables of commentary using `DELETE COMMENTARY` API **OR**
        ```
        DROP TABLE <table_name>;
        ```
    - Delete all commentary resources using `DELETE RESOURCE` API **OR**
        ```
        DELETE from resources WHERE resource_name=<commentary_resource_name>;
        ```
    - Add commentary resources using `POST RESOURCE` API **OR**
        ```
        INSERT INTO resources (version,resource_table,year,labels, license_id,resourcetype_id,language_id,version_id,active, metadata)VALUES (<version>,<resource_table>,<year>,<labels>,<license_id>,<resourcetype_id>,<language_id>,<version_id>,t, <metadata>);
        ```
    - Upload commentary data(with changed reference structure) using `POST COMMENTARY` API **OR**

        ```
        ALTER TABLE <commentary_table> ADD COLUMN reference JSONB;
        UPDATE <commentary_table> SET reference = jsonb_build_object('book', book,
                            'chapter', chapter,
                            'verseNumber', verse,
                            'bookEnd', book,'
                            'chapterEnd', chapter ,'
                            'verseEnd', verse);

        ALTER TABLE <commnetary_table> DROP COLUMN book,
                                        DROP COLUMN verseStart,
                                        DROP COLUMN verseEnd;                               
        ```


### **--------------------------------------------------------------------------------------------------------------------**


