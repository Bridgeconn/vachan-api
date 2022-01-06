# Release v2.0.0-alpha2

## Date: Jan 7, 2022

## Changelog
* Implemented Autographa Project Management and Module
* Added NLP functions for translation and other related tasks like gloss, stopwords etc
* Provides graphQL interface for all features available in REST
* Implemented authentication using Kratos and access control rules based on user roles as well as resource type. App connects to a central Kratos DB, shareable across other Apps.
* Started using dockerization
* Automated deployment via github actions

## Pending

#### Load Data on server
Get all contents on V1 and load them to hosted instance of V2

1. Bibles
2. Commentaries
3. Dictionaries(tws)
4. Token translations

For now we can connect to the old DB dump and load data to V2 via python scripts calling APIs. 

#### Improving the translation APIs

In the first round of evaluation it was found tokenization API takes too much time

* Try improving the code/db operations to improve the time
* Use fast-api background task to change this API to submit a job, instead of expecting immediate response

#### Scripture burrito
* Add APIs to export/download DB contents like bibles and commentaries from server
* Create a scripture burrito file for the contents being downloaded

###### Project export
* Fix and improve the conversion of project into alignment json format
* Include scripture burrito for this content too

#### Support for generic Markdown content
