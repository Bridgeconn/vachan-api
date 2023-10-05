# Database Changes Log for Release 
This document captures all database modifications made during each release . It will serve as a reference guide for future deployments, promoting consistency and ease of use across different setups.


##  Beta.31: 05-10-2023 , commit id :7f38ac0b5008341cd923d4cc1d769b2fee47f67a , [#715](https://github.com/Bridgeconn/vachan-api/pull/715/)
This release includes:
- db changes in commentary
    - `chapter`.`verseStart` and `verseEnd` columns are removed
    - new json field `reference` is added which includes `book`,`chapter`,`verseNumber`,`bookEnd`,`chapterEnd` and `verseEnd`
- Actions performed
    - Delete all tables of commentary using DELETE COMMENTARY API
    - Delete all commentary sources using DELETE SOURCE API
    - Add commentary sources using POST SOURCE API
    - Upload commentary data(with changed reference structure) using POST COMMENTARY API

### --------------------------------------------------------------------------------------------------------------------------------------------


