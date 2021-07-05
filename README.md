# Vachan-api

The server application that provides REST APIs to interact with the underlying Databases (SQL and Graph) and modules in Vachan-Engine.

Currently serving 3 client applications, VachanOnline website, the Vachan Mobile App and AutographaMT Bible translation tool.

## Implementation Details

Implemented Using
- Python 3.7.5
- Fastapi framework
- Postgresql Database
- DGraph Database

## How to set up locally for development and testing

### Clone git repo

```git clone https://github.com/Bridgeconn/vachan-api.git```

```cd vachan-api```

```git checkout version-2```


### Set up virtual Environment

```python3 -m venv vachan-ENV```

```source vachan-ENV/bin/activate```

```pip install --upgrade pip```

```pip install -r requirements.txt``` 

### Set up Postgresql Database

Prerequisite: Postgresql (refer [postgresql website](https://www.postgresql.org/download/linux/ubuntu/) for installation and setup)

1. login to psql (command line interface for Postgres) using your username and password
2. create a new database, in the name you want
  `CREATE DATABASE db_name;`
3. exit from psql ( `\q` or ctl+d )
4. from terminal use command 
  
  `>>> cd DB`
  
  `>>> psql db_name < seed_DB.sql`

  (use your username and password if required
  `>>> psql -U username db_name < seed_DB.sql` )
  
### Set up Environmental Variables

go to the home directory and open `.bashrc` file

```cd ```

```gedit .bashrc```

Edit the following contents appropriatetly and paste to the `.bashrc` file
```
  export VACHAN_SENDINBLUE_KEY="<send_in_blue_key>"
  export VACHAN_HS256_SECRET="<jwt_token_key>"
  export VACHAN_POSTGRES_HOST="localhost"
  export VACHAN_POSTGRES_PORT="5432"
  export VACHAN_POSTGRES_USER="<db_user>"
  export VACHAN_POSTGRES_PASSWORD="<db_password>"
  export VACHAN_POSTGRES_DATABASE="<db_name>"
  export VACHAN_LOGGING_LEVEL="WARNING"
```
After editing .bashrc file they may need to run

`. ~/.bashrc` or 

`source ~/.bashrc`

to refresh the bashrc file or logout and login to refresh it

### Run the app

From the vachan-api folder
1. `mkdir logs`
2. `touch logs/API_logs.log`
3. `cd app`
4. `uvicorn main:app`

If all goes well, you will get a message like this in terminal
```
INFO:     Started server process [17599]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

If you need to run the app on another port `--port` can be used. To run in debug mode `--debug` can be used

```uvicorn main:app --port=7000 --debug```

### Access Documentations

Once the app is running, from your browser access http://127.0.0.1:8000/docs for swagger documentation.

Redoc documentaion is also available at http://127.0.0.1:8000/redoc

### Run Test

To run all the testcases, from the folder vachan-api/app run the command

```python -m pytest```

For runing testselectively, refer [pytest docs](https://docs.pytest.org/en/stable/usage.html#specifying-tests-selecting-tests)
