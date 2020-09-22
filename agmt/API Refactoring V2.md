# API Refactoring
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
	  Uses language Codes, book Codes, source names etc in place of numbers ids we used in V1
* Better Error Messages
	> use consistent error message patterns thought out the App
	> use http_status codes to indicate type of error
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
