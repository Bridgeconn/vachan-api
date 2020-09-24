# API Refactoring


## Why API Refactoring ?

1. Poor code quality

	As we are working on adding features and fixing bugs on the V1 APIs we see lots of things which shouldn't be done the way it is, or could be done better. For example in many places in code, we form SQL queries by python string concatination. Because, these codes were written by different developers over a long time period and for a variety of needs, there are lots of inconsistancies, from naming of variables to implementation logic, which makes it hard to maintain. The code base includes (but uses or doesn't use) code portions written for the 
	* AgMT V1 APIs, 
	* The alignment app, 
	* AgMT V2 APIs (all the above mostly by Bijo)
	* VO apis (by Revant)
	All of which have been modified here and there, by Kavitha and Joel Johnson, as and when needs came.

2. In-consistancy in APIs

	Often it is very difficult to understand expected inputs, outputs and even fuctionality of an API or function. We usually read the code to understand what inputs be given, how it is processed and what are the values returned from an API. For example some APIs which were written earlier use form data input while recent ones use JSON data input. Also there is no consistancy in endpoint names, which makes it not possible to understand what an API does.

3. Use better coding practices

	Often several needs for standardizing the way we write code comes up as a need.
	* Use code linting
	* Use better libraries(like SQLAlchemy)

4. Lack of good documentation

	The lack of documentation has been a big problem. The attempt of creating a swagger documentation, with Savitha's help, wasn't very successful. Though she created one, it was not being effectively updated and maintained and more importantly not being used.

5. No tests

	Often the APIs where developed by the UI developer itself and where only tested using the UI manually. There were no proper test cases created(neither for UI nor for API) at the time of implementation. An Attempt was made to add tests for these APIs afterwards, again with Savitha's and Joel Johnson's help. But, it wasn't effective either. Though tests were written, it hardly check for the possible flaws, and we are often finding them when issues comes up from user end. The problem of tests not being defined during the definition and implementaion of APIs is very evident.

6. Database changes

	The whole DB design was once reviewed and revised to solve many of the issues it had and also to make it more standardized and scalable. Sticking to those design decisions, now we see
	* some issues that were not fixed at that time(like an un-necessary translation_projects_lookup table which does no good but just increases the number of joins required)
	* some principles then decided upon, are not followed when new contents were added to DB (naming tables and fields, how tables are connected together etc)
	* some changes we feel are required in newly added data(bookcodes should be JSON array and not comma separated string, which column should have the NOT NULL constaint etc)

## Why Vachan-API Version 2

* Each of the above listed issue is very important and needs to be fixed as early as possible. But each requires a complete code review and revisal/rewritting. So it is better to do all at once in one go. Other wise it would result in unnecessay extra work, like if we first refine all the tests and documentation and then later change the APIs, all effort spend on tests and docs are wasted and it will have to be redone.

* If we could stick to the APIs and revise only the underlying implementaion, then the clients wouldn't be affected with the changes. But the inputs, endpoints, outputs all need to be 
standardized. 

It is important to have the V1 APIs as it is, as currently 3 clients(AgMT, VO and VO App) are using them. So we can have a better parallel version 2 and let the clients switch versions on their conviniance.

## API Endpoint Design for vachan-api Version 2

### Main Principles followed 
* Uniformity
	> Attempted to bring uniformity in how each resource is 
	> * stored in Database
	> * accessed via GET, PUT and POST methods
	> * given end-point names(using plurals, following same pattern etc) and input-output objects names and structure
* Scalability
	> Considers new data and processing requiremnts that would come in future
	> * Dynamically creating new tables
	> * Provision to add new contents and edit contents in all tables
	> * Keeping flexibility of schema with JSON objects in places where variation can be expected
* Human readability/understandability of input output values
	> have tried to avoid the use of id values as much as possible in inputs and outputs.
	> Uses language Codes, book Codes, source names etc in place of number ids we used in V1
* Better Error Messages
	> * use consistent error message patterns thought out the App
	> * use http_status codes to indicate type of error
* Data validation
	> Make use of the input and output datatype validation provisions in the Fast API as much as possible
	> * specifies expected datatype like int, string etc
	> * defines patterns for special cases like, language code, book code, source name etc
	> * defines JSON strutures of Body parameters as well as output objects
* Documentation
	> Using FastApi we can generate swagger and redoc documentation automatically if necessary steps are followed while writing codes.
	> * using meaningful function names
	> * adding description for every API as comments in the required format
	> * defining and specifying all inputs and output format for every API 
	> Following these practices, we will have good quality API documentaion which will become very useful for our API clients, especially if we expect external clients

### How to setup and run the V2 app

##### Setting up 
1. Pull the `V2-API-Planning` branch from https://github.com/kavitharaju/vachan-api

* `git pull https://github.com/kavitharaju/vachan-api V2-API-Planning`

* `cd vachan-api`

2. Set up a virtual environment using the requirements.txt file

* `python3 -m venv vachan-ENV`

* `source vachan-ENV/bon/activate`

* `pip install -r requirements.txt`

##### Run App
From witth in virtual environment,
1. `cd agmt`
2. `uvicorn vachan_api_serverV2:app`
If all goes well, you will get a message like this in terminal
```
INFO:     Started server process [17599]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

##### Access API docs
Once the app is running, from your browser access http://127.0.0.1:8000/docs for swagger documentation.

Redoc documentaion is also available at http://127.0.0.1:8000/redoc

### Old APIs and substitutes for them
<table><tr><th>Sl No</th><th>Old API</th><th>Function</th><th>New API</th></tr>
<tr>
<td>1.</td>
<td><pre>GET "/v1/sources"</pre></td>
<td>For a complete download of all content types stored in the database</td>
<td><pre>GET "/v2/sources"</pre></td>
</tr>

<tr>
<td>2.</td>
<td><pre>GET "/v1/bibles"</pre></td>
<td>Return the list of availabile Bible Languages and Versions.</td>
<td><pre>GET "/v2/sources?contentType=bible"</pre></td>
</tr>

<tr>
<td>3.</td>
<td><pre>GET "/v1/bibles/languages"</pre></td>
<td>Return the list of bible languages.</td>
<td><pre>GET "/v2/sources?contentType=bible"</pre></td>
</tr>

<tr>
<td>4.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books"</pre></td>
<td>Return the list of books in a Bible Language and Version.</td>
<td><pre>GET '/v2/bibles/{sourceName}/books'</pre></td>
</tr>
<tr>
<td>5.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books-chapters"</pre></td>
<td>Return the list of books and chapter Number in a Bible Language and Version.</td>
<td><pre>GET "/v2/bibles/{sourceName}/books"</pre></td>
</tr>

<tr>
<td>6.</td>
<td><pre>GET "/v1/bibles/{sourceId}/{contentFormat}"</pre></td>
<td>Return the bible content for a particular Bible version and format.</td>
<td><pre>GET "/v2/bibles/{sourceName}/books/{bookCode}/{contentType}"</pre></td>
</tr>

<tr>
<td>7.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books/{bookCode}/{contentFormat}"</pre></td>
<td>Return the content of a book in a particular version and format.</td>
<td><pre>GET "/v2/bibles/{sourceName}/books/{bookCode}/{contentType}"</pre></td>
</tr>

<tr>
<td>8.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books/{biblebookCode}/chapters"</pre></td>
<td>Return number of Chapters and chapter details for a book.</td>
<td><pre>GET "/v2/bibles/{sourceName}/books?bookCode=gen"</pre></td>
</tr>

<tr>
<td>9.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books/{bookCode}/chapter/{chapterId}"</pre></td>
<td>Return the content of a given bible chapter.</td>
<td><pre>GET "/v2/bibles/{sourceName}/verses?bookCode=gen;chapter=1"</pre></td>
</tr>

<tr>
<td>10.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books/{biblebookCode}/chapters/{chapterId}/verses"</pre></td>
<td>Return Verse Id Array for a Bible Book Chapter.</td>
<td><pre>GET "/v2/bibles/{sourceName}/verses?bookCode=gen;chapter=1"</pre></td>
</tr>

<tr>
<td>11.</td>
<td><pre>GET "/v1/bibles/{sourceId}/books/{bibleBookCode}/chapters/{chapterId}/verses/<verseId>"</pre></td>
<td>Return a Verse object for a given Bible and Verse.</td>
<td><pre>GET "/v2/bibles/{sourceName}/verses?bookCode=gen;chapter=1;verse=1"</pre></td>
</tr>

<tr>
<td>12.</td>
<td><pre>GET "/v1/bibles/{sourceId}/chapters/{chapterId}/verses"</pre></td>
<td>Return Verse Id Array for a Bible Book Chapter.</td>
<td><pre>GET "/v2/bibles/{sourceName}/verses?bookCode=gen;chapter=1"</pre></td>
</tr>

<tr>
<td>13.</td>
<td><pre>GET "/v1/bibles/{sourceId}/verses/{verseId>}</pre></td>
<td>Return a Verse object for a given Bible and Verse.</td>
<td><pre>GET "/v2/bibles/{sourceName}/verses?bookCode=gen;chapter=1;verse=1"</pre></td>
</tr>

<tr>
<td>14.</td>
<td><pre>POST "/v1/sources/commentary"</pre></td>
<td>Add a commentary source, put associated entries in source and versions</td>
<td><pre>POST '/v2/sources'</pre></td>
</tr>

<tr>
<td>15.</td>
<td><pre>GET "/v1/commentaries"</pre></td>
<td>Fetch the list of commentaries with an option to filter by language .</td>
<td><pre>GET '/v2/sources?contentType=commentry;languageCode=hin'</pre></td>
</tr>

<tr>
<td>16.</td>
<td><pre>GET "/v1/commentaries/{sourceId}/{bookCode}/<chapterId>"</pre></td>
<td>Fetch the commentary for a chapter for the given commentary sourceId.</td>
<td><pre>GET '/v2/commentaries/{sourceName};bookCode=gen;chapter=1'</pre></td>
</tr>

<tr>
<td>17.</td>
<td><pre>POST "/v1/sources/dictionary"</pre></td>
<td>Add a dictionary source, put associated entries in source and versions</td>
<td><pre>POST '/v2/sources'
and 
POST '/v2/dictionaries/{sourceName}'</pre></td>
</tr>

<tr>
<td>18.</td>
<td><pre>GET "/v1/dictionaries"</pre></td>
<td>Fetch the list of dictionaries with an option to filter by language .</td>
<td><pre>GET "v2/sources?contentType=dictionary;language=hin"</pre></td>
</tr>

<tr>
<td>19.</td>
<td><pre>GET "/v1/dictionaries/{sourceId}"</pre></td>
<td>Fetch the words of a given dictionary.</td>
<td><pre>GET '/v2/dictionaries/{sourceName}'</pre></td>
</tr>

<tr>
<td>20.</td>
<td><pre>GET "/v1/dictionaries/{sourceId}/<wordId>"</pre></td>
<td>Fetch the meaning for given word of a given dictionary.</td>
<td><pre>GET '/v2/dictionaries/{sourceName}?searchIndex=word'</pre></td>
</tr>

<tr>
<td>21.</td>
<td><pre>POST "/v1/sources/infographic"</pre></td>
<td>Add a infographic source, put associated entries in source and versions</td>
<td><pre>POST '/v2/sources'
and 
POST '/v2/infographics/{sourceName}'</pre></td>
</tr>

<tr>
<td>22.</td>
<td><pre>GET "/v1/infographics/{languageCode}"</pre></td>
<td>Fetch the metadata for the infographics for the given language .</td>
<td><pre>GET "/v2/sources?contentType=infographics;language=hin"</pre></td>
</tr>

<tr>
<td>23.</td>
<td><pre>POST "/v1/sources/audiobible"</pre></td>
<td>Add a audio bible.</td>
<td><pre>POST '/v2/bibles/{sourceName}/audios</pre></td>
</tr>

<tr>
<td>24.</td>
<td><pre>GET "/v1/audiobibles"</pre></td>
<td>Fetch the metadata for the audiobibles Option to filter by language.</td>
<td><pre>GET "/v2/bibles/{sourceName}?contentType=audio"</pre></td>
</tr>

<tr>
<td>25.</td>
<td><pre>POST "/v1/sources/video"</pre></td>
<td>Add videos for given language.</td>
<td><pre>POST '/v2/sources'
and 
POST '/v2/biblevideos/{sourceName}'</pre></td>
</tr>

<tr>
<td>26.</td>
<td><pre>GET "/v1/videos"</pre></td>
<td>Fetch the metadata for the videos with an option to filter by language.</td>
<td><pre>GET "/v2/biblevideos/{sourceName}" </pre></td>
</tr>

<tr>
<td>27.</td>
<td><pre>GET "/v1/booknames"</pre></td>
<td>Fetch the bible book names in the native language with an option to filter by language.</td>
<td><pre>GET "/v2/bibles/{sourceName}/books"</pre></td>
</tr>

<tr>
<td>28.</td>
<td><pre>GET "/v1/search/{sourceId}"</pre></td>
<td>Fetch the bible verses with the given keyword in the specified sourceId clear text bible</td>
<td><pre>GET "/v2/bibles/{sourceName}/verses?searchPhrase=query"</pre></td>
</tr>

<tr>
<td>29.</td>
<td><pre>PUT "/v1/sources/metadata"</pre></td>
<td>Append bible metadata for a source .</td>
<td><pre>PUT "/v2/sources"</pre></td>
</tr>

<tr>
<td>30.</td>
<td><pre>POST "/v1/biblebooknames"</pre></td>
<td>Add bible book names for a local language</td>
<td><pre>PUT "/v2/bibles/{sourceName}/books"   </pre></td>
</tr>
</table>