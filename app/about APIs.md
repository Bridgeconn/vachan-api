# About AgMT/Translation API designs

1. APIs designed as two sets
	- *Translation APIs*: These are independant APIs which does not require the dat they operate on to be store in server database. When AgMT user prefers **not to sync** his project/data to cloud, these APIs may be used. Also a different app like BridgeEngine can use one or more of these APIs if required. But for each of these APIs user may have to upload all the data he wants to process(we dont store it in DB), which may make the APIs **slower**.
	- *AgMT APIs*: Does similar functions as the above APIs, but utilizes the concept of projects and makes use of project data stored in DB.
2. Pagination
	- Pagination is **not implemented** at the API functions. The UI may implement it where ever required. The important places it may be used are in token list and drafts(token occuring verses). But sending only a subset may make the data incomplete, especially for tokenization as we do not store the generated tokens at server. Sending the full data to UI may allow it to implement useful operations like searching, sorting, filtering etc at the UI.

## Discussion Notes, from Meeting(s) with Joel

- Tokenization: This module should work as a black box and underlying algorithm(s) may be different(for different languages, based on available resource for each). The current algo looks okay, but later we can also have statistical methods brought in.

- Sentence Ids: Using an integer ID is good but we can also have a surrogate ID, which can also be strings.

- Window size for suggestion. Estimate how time and space increases with window size and determine an appropriate size for us.

- word segmenter: Allow user to specify word segmenter. Can default it to [\s\n\r]+ we use now

- Book query parameter in tokenize API: add a books query parameter along with sentence_ids and ranges in autographa's get tokens API. It can also be an unspecified, key-value parameter like metaData.

- auto_translate: Call it something else. Something like suggestions....

- stopwords: provide an API to identify stopwords based on frequency from any input corpus

- Draft formats: change plain-text to text, Bible USFM to usfm, Export JSON to alignment-json

- Avoid occurence list and default to apply to all: While applying a token translation, have a query parameter that says "Apply to all" then find all occurences and apply them without having to specify occurence list. But those occurences would be hard to find as per our DB strcuture as we dont store the tokens and occurences anywhere.

## What are pending

* Doing proper testing and adding automated tests for translation related APIs
* Refactor code, eliminating linter warnings: too-many-arguments, too-many-local-variable, too-many-nested-blocks etc
* Setting up usfm-grammar as a separate server with API service and allowing direct USFM upload to AGMT and Vachan DB
* Dockerizing
* Use fuzzy string matching for suggestions
* Auto deployment via git actions
* Language codes. See how we can use/switch-to bcp47 tags.
* Supporting inputs of different formats(convert CSV, doc and USFM to sentence lists)
* Export format. Finer details of alignment JSON and scripture Buritto
* API auth and access management
* Update vachan-admin. Re-write or update vachan-admin app used for data loading to vachan DB, as per V2 APIs
* Use alignment data and glossary from manual alignments and vachan-data project to enrich our translation knowledge
* Test time and space requirements of our methods for tokenization, suggestion etc with enough data
* Have a module to identify stopwords given some corpora, and if possible classify them as pre-positions and post-positions
* Have some translation/utils APIs for knowing(or setting) system settings like stopword list for a language, puctuations, sentence and word delimiters, default window size etc.
