# About AgMT/Translation API designs

1. APIs designed as two sets
	- *Translation APIs*: These are independant APIs which does not require the dat they operate on to be store in server database. When AgMT user prefers **not to sync** his project/data to cloud, these APIs may be used. Also a different app like BridgeEngine can use one or more of these APIs if required. But for each of these APIs user may have to upload all the data he wants to process(we dont store it in DB), which may make the APIs **slower**.
	- *AgMT APIs*: Does similar functions as the above APIs, but utilizes the concept of projects and makes use of project data stored in DB.
2. Pagination
	- Pagination is **not implemented** at the API functions. The UI may implement it where ever required. The important places it may be used are in token list and drafts(token occuring verses). But sending only a subset may make the data incomplete, especially for tokenization as we do not store the generated tokens at server. Sending the full data to UI may allow it to implement useful operations like searching, sorting, filtering etc at the UI.
