# API Refactoring
## API Endpoint Design for vachan-api Version 2

## Main Principles followed 
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


