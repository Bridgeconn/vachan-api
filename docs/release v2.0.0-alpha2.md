# Plan for release v2.0.0-alpha2

## Date: dec 2021


## Changelog
* Implemented Autographa project Management Module
* Added NLP functions for translation and other related tasks like gloss, stopwords etc
* Provides graphQL interface for all features available in REST
* Implemented authentication using Kratos and access control rules based on user roles as well as resource type.
* Dockerization

## To be completed before release

#### Authentication and access control
1. Have auth and access check defined and implemented for all available REST endpoints
2. Replicate the auth and access check behaviour in REST to graphQL queries and mutations
3. Clean up the code base. Move auth related things to a folder, use ENUMs as much as possible etc
4. Host and use the Kratos instance running on server. Use the same from git actions as well

#### Dockerization
1. Fix issues on the pending PR
2. Add usfm-grammar as a container and make it callable from the utils function which now uses the one installed on server
3. Make all tests possible to be run on git actions. The ones excluded now are those using usfm-grammar
4. Do we need to do auto-deployment upon merge via git actions?

#### SW APIs
1. Implement the SW APIs
2. Manually clean up and load GL stopwords to DB

#### Load Data on server
Get all contents on V1 and load them to hosted instance of V2

1. Bibles
2. Commentaries
3. Dictionaries(tws)
4. Token translations

For now we can connect to the old DB dump and load data to V2 via python scripts calling APIs. 


## Left for later

#### Improving the translation APIs

In the first round of evaluation it was found tokenization API takes too much time

* Try improving the code/db operations to improve the time
* Use fast-api background task to change this API to submit a job, instead of expecting immediate response

#### Scripture burrito
* Add APIs to export/download DB contents like bibles and commentaries from server
* Create a scripture burrito file for the contents being downloaded

#### Project export
* Fix and improve the conversion of project into alignment json format
* Include scripture burrito for this content too

