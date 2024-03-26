# Vachan-api

The server application that provides REST APIs to interact with the underlying Databases (SQL and Graph) and modules in Vachan-Engine.

Currently serving 3 client applications, VachanOnline website, the Vachan Mobile App and AutographaMT Bible translation tool.

## Implementation Details

Implemented Using
- Python 3.10.6
- Fastapi framework
- Postgresql Database


## Start App (with docker)

```git clone -b version-2 https://github.com/Bridgeconn/vachan-api.git```

```cd vachan-api/docker```

```docker compose --profile local-run up```
or
```sudo -E docker compose --profile local-run up```

Set environment variables VACHAN_SUPER_USERNAME, VACHAN_SUPER_PASSWORD. Use `--build` and `--force-recreate` flags if there has been code change. Refer [the detailed usage guide](./docs/docker-guide.md#to-start-app-locally) and [section on environments variables](#set-up-environmental-variables), for more information.

If all goes well you should be able to get proper outputs at `http://localhost`, `http://localhost/docs`, `http://localhost/v2/demos/docs`, 
`http://localhost/v2/cms/rest/docs`,`http://localhost/v2/text/translate/token-based/docs`,`http://localhost/v2/auth/docs`,`http://localhost//v2/ai/docs`,`http://127.0.0.1:4434/identities`and connect to postgresDB at `localhost`, `5433`


## Set up locally for development and testing(without docker)

We follow fork and merge git workflow.
* Fork the repo, https://github.com/Bridgeconn/vachan-api.git, to your github account
* Then clone you account locally and keep that as "origin"
* Add the central Bridgeconn repo as "upstream".
* Contribute back via pull requests to the "version-2" branch on this repo.

### Clone git repo

```git clone https://github.com/<your-account>/vachan-api.git```

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

### Set up Environmental Variables

go to the home directory and open `.bashrc` file

```cd ```

```gedit .bashrc```

Edit the following contents appropriatetly and paste to the `.bashrc` file
```
  export VACHAN_POSTGRES_HOST="localhost"
  export VACHAN_POSTGRES_PORT="5432"
  export VACHAN_POSTGRES_USER="<db_user>"
  export VACHAN_POSTGRES_PASSWORD="<db_password>"
  export VACHAN_POSTGRES_DATABASE="<db_name>"
  export VACHAN_POSTGRES_DATA_DIR="<data_dirrctory_path>"
  export VACHAN_LOGGING_LEVEL="WARNING"
  export VACHAN_KRATOS_ADMIN_URL="http://127.0.0.1:4434/"
  export VACHAN_KRATOS_PUBLIC_URL="http://127.0.0.1:4433/"
  export VACHAN_SUPER_USERNAME="<super-admin-emial-id>"
  export VACHAN_SUPER_PASSWORD="<a-strong-password>"
  export VACHAN_DOMAIN=127.0.0.1:8000
```
After editing .bashrc file they may need to run

`. ~/.bashrc` or 

`source ~/.bashrc`

to refresh the bashrc file or logout and login to refresh it



### Run the app

From the vachan-api folder
1. `cd app`
2. `uvicorn main:app`

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

To run  the testcase, from the folder vachan-api/app run the command

```python -m pytest```
