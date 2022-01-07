# Release v2.0.0-alpha.2

## Date: Jan 7, 2022

## New in this Version
* Autographa Project Management Module. 
> * Supports multiple kinds of tokenizations(single word & phrases, user-defined tokens, book-wise, chapter-wise, multiple-books etc,)
> * multiple translations/senses for same token
> * context based translation suggestions
> * possible to view draft while translation is in progress
> * scalable to support non-USFM documents
* NLP functions for translation and other related tasks like gloss, stopwords etc
* GraphQL interface for all features available in REST
* Authentication using Kratos and access control rules based on user roles as well as resource type(Attribute-Based-Access-Control). App connects to a central Kratos DB, shareable across other Apps.
* Dockerization
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
