# Data Upload 

This Python script tackles the challenge of streamlining data uploads to a database. Instead of manually uploading individual files, it leverages the power of automation, condensing the entire process into a single, user-friendly script. You no longer need to deal with tedious, repetitive data uploads – one command is all it takes to initiate the data flow.

But this script goes beyond mere convenience. It starts by efficiently extracting data from a specified CSV file. It then meticulously transforms that raw data into a format perfectly suited for your database, ensuring seamless ingestion. Finally, with a single command, it seamlessly transmits the prepared data to a designated endpoint, completing the entire data upload journey in an automated and error-free manner.

### Contents:

Within this directory, you will discover two Python scripts: `extract.py` and `upload.py.`

#### Automated Data Extraction:

Handling large SQL dump files, particularly those of 2GB size, can be a daunting and time-consuming task when manually extracting tables. To streamline this process, the `extract.py` script has been developed. This script systematically traverses your SQL dump, capturing data and organizing it into CSV files. Each CSV file is named after its corresponding table, ensuring convenient access for future use.


#### Data Upload Utility:

Complementing the data extraction process, `upload.py` facilitates seamless data integration with specific endpoints through POST requests. Utilizing data extracted from the CSV files, this script enables efficient uploading to designated endpoints.

#### Database Schema Handling:

The Python script responsible for data upload incorporates functionality to upload data to a specified schema within the database. If the specified schema does not exist, the script dynamically creates it, ensuring data organization and accessibility.


 
 ## Implementation Details

 Inorder to run the upload file you need make sure the virtual environment is created and it is activated.

### Set up virtual Environment

```python3 -m venv vachan-ENV```

```source Data-ENV/bin/activate```

```pip install --upgrade pip```

```pip install -r requirements.txt```

### Execution Command :

To run the extract script you can use this command
```python3 extract.py```

### Execution Command:

To run the upload script you can use this command
```python3 upload.py```

