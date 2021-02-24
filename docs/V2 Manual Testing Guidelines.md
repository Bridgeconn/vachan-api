# Vachan API Version 2

## Guidelines for Manual Testing

API server deployed at: http://128.199.18.6

API Documentations available at: http://128.199.18.6/docs and http://128.199.18.6/redoc 

## Key Points to be Tested

* Test if the documentation provided is clear and adequate for understanding and using the APIs, by developers who work on a client appication. 
* Test if the documentation is correct as per how the API accepts values, performs functions or returns messages or values.
* Test if the APIs perform the functions they are expected to do, effectively
* Test if the error cases are handled or reported properly(example, when inputs are wrong)
* Test if the desgin of API functions are in line with what the client applications need

## How to do the testing

Any API testing methods or tools can be used for this. One way suggested is to use the [swagger](http://128.199.18.6/docs) or [redoc](http://128.199.18.6/redoc) documentations and invoke and test APIs from there, where we have an interactive interface.

#### Steps to Test using Interactive API Documentations

For every API, a basic explanation of what functionality it performs, what are the inputs and outputs it take and example values for all input and output fields are provided in the documentation. These APIs can be invoked and output can be viewed there itself, to be tested.

It is recommended that the APIs are tested in the same order they are given in the documentation, but not mandatory to do so. The different methods(GET, PUT, POST) in each set can be tested in varying order based on the logic of the tester and what is required by the APIs(example, there may not be any logic in testing a PUT method to edit data, without adding some data first, by the corresponding POST method).

For testing of some set of APIs like bibles, commentary etc they require versions and sources to be present in the database. So adding below, the list of all versions and sources to be created, for testing them with already provided example values in the documentation. Testing team can follow these examples or use different/more values as they need.

#### versions
1.  ```
	{
	  "versionAbbreviation": "KJV",
	  "versionName": "King James Version",
	  "revision": 1,
	  "metaData": {
	    "publishedIn": "1611"
	  }
	}
	```

2. ```
	{
	  "versionAbbreviation": "IRV",
	  "versionName": "Indian Revised Version",
	  "revision": 1
	}
	```

3. ```
	{
	  "versionAbbreviation": "BBC",
	  "versionName": "Bridgeway Bible Commentaries",
	  "revision": 1
	}
	```

4. ```
	{
	  "versionAbbreviation": "TW",
	  "versionName": "Translation Words",
	  "revision": 1
	}
	```

5. ```
	{
	  "versionAbbreviation": "TBP",
	  "versionName": "The Bible Project",
	  "revision": 1
	}
	```

#### sources

1. ```
	{
	  "contentType": "commentary",
	  "language": "eng",
	  "version": "KJV",
	  "revision": 1,
	  "year": 2020,
	  "license": "ISC",
	  "metaData": {
	    "otherName": "KJBC, King James Bible Commentaries"
	  }
	}
	```

2. ```
	{
	  "contentType": "bible",
	  "language": "hin",
	  "version": "IRV",
	  "revision": 1,
	  "year": 2020,
	  "license": "ISC"
	}
	```

3. ```
	{
	  "contentType": "commentary",
	  "language": "eng",
	  "version": "BBC",
	  "revision": 1,
	  "year": 2020
	}
	```

4. ```
	{
	  "contentType": "dictionary",
	  "language": "eng",
	  "version": "TW",
	  "revision": 1,
	  "year": 2020
	}
	```

5. ```
	{
	  "contentType": "infographic",
	  "language": "hin",
	  "version": "IRV",
	  "revision": 1,
	  "year": 2020
	}
	```

6. ```
	{
	  "contentType": "biblevideo",
	  "language": "eng",
	  "version": "TBP",
	  "revision": 1,
	  "year": 2020
	}
	```

## Tests already done while development

All the tests done during development are available [here](https://github.com/Bridgeconn/vachan-api/tree/version-2/app/test)

Tests are added module wise. Test files are named in the pattern `test_module.py`

## What is not implemented yet

* All APIs that are related to AutographaMT application alone are not yet implemented
* User management, role/access management and authentication are not implemeneted yet.
