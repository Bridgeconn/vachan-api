# API Server Set up Documentation - Python Flask

## Reference online resource
- [Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04)
- [Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04)

## Prerequisites
 - Ubuntu Server 18.04/16.04
 - DNS

## Server Initial Set up

### Install primary python packages and nginx
> Run commands
 -  `sudo apt-get update`
 - `sudo apt-get install python3-pip python3-dev nginx`
 - `sudo apt-get install libpq-dev`

## Postgres Database set Up

### Install Postgress SQL:
 - Run Command `sudo apt-get install postgresql`

### Create Postgres user and password:
 - Run command `sudo su postgres`. Switches to postgres user
 - Run command `psql` in postgres user shell
 - Run command `CREATE USER <username> WITH SUPERUSER PASSWORD '<password>'`. Enter user username and password fot the DB. For ex: `CREATE USER agmt WITH SUPERUSER PASSWORD 'pass&14'`
 
## Set Environment variables: (Command -> `gedit .bashrc` from home directory)
- Paste follwing with the credentials to the `bashrc` file.
  ```
  export AGMT_SENDINBLUE_KEY="<send_in_blue_key>"
  export AGMT_HS256_SECRET="<jwt_token_key>"
  export AGMT_POSTGRES_HOST="localhost"
  export AGMT_POSTGRES_PORT="5432"
  export AGMT_POSTGRES_USER="<db_user>"
  export AGMT_POSTGRES_PASSWORD="<db_password>"
  export AGMT_POSTGRES_DATABASE="<db_name>"
  ```

## Python Virtual Environment

### Install Virtual Environment
 - Run command `sudo pip3 install virtualenv`

### Create Virtual Environment
 - Run Command `virtualenv myprojectenv`. You can enter your custom name instead of `myprojectenv`.

### Activate Virtual Environment
 - Run Command `source myprojectenv/bin/activate`. Activate the virtual environment before installing dependencies.

 ## Set Up your Flask Application

 ### Clone Project and Install dependencies
 - Clone project repo to server
 - Navigate to project directory containing the `requirements.txt` file.
 - Install Python dependencies by running command `pip3 install -r requirements.txt`

### Create Initial DB tables
 - Navigate to project directory containing the `db.sql` file. (Inside `agmt` folder)
 - Run Command `psql -d <db_name> -f ./db.sql`
 
### Test Flask App
 - Run Command `gunicorn main:app` inside the project folder containing the `main.py` file.
 - If the gunicorn server has started successfully, close and set up Nginx and Gunicorn WSGI.

## Set up and enable the configuration files for Flask API server
 - Assuming the Server user Name is `amt`, python virtual environment name is `venv3`, the project folder name is `vachan-api` and the `main.py` file is in `vachan-api/agmt/` folder then the config files will be like:
 - Save config files in project directory named `vachanconfig`

### Set up Gunicorn

#### Gunicorn config file
 - Copy and edit the files according to the project credentials and directories and save file as `gunicorn.service`. You could use your custom name for the file.
    ```
    [Unit]
    Description=gunicorn daemon
    After=network.target
    
    [Service]
    User=amt
    Group=amt
    WorkingDirectory=/home/amt/vachan-api/agmt
    Environment="AGMT_SENDINBLUE_KEY=<send_in_blue_key>"
    Environment="AGMT_HS256_SECRET=<jwt_algorithm_key>"
    Environment="AGMT_POSTGRES_USER=<db_user_name>"
    Environment="AGMT_POSTGRES_PASSWORD=<db_password>"
    Environment="AGMT_POSTGRES_DATABASE=<db_name>"
    Environment="AGMT_HOST_API_URL=<api_url>"
    Environment="AGMT_HOST_UI_URL=<UI_url>"
    ExecStart=/home/amt/venv3/bin/gunicorn --workers 3 --bind unix:/home/amt/vachan-api/agmt/agmt.sock   main:app
    
    [Install]
    WantedBy=multi-user.target
    ```

#### Link files in `systemd` folder
 - Run Command to create sym link of the `gunicorn.service` file in `systemd` folder
   - `sudo ln -s /home/amt/vachan-api/vachnaconfig/gunicorn.service /etc/systemd/system/`

#### Start Gunicorn service
 - Run the commands
   - `sudo systemctl start gunicorn.service`
   - `sudo systemctl enable gunicorn.service`

### Set up Nginx config file

#### Nginx file
 - Copy and edit the files according to the project credentials and directories and save file as `nginx.conf`. You could use your custom name for the file.
 - For enabling ssl refer online documentation.

    ```
    server {
        listen 80;
        server_name <server_domain_name>;
    
       location / {
            include proxy_params;
            proxy_pass http://unix:/home/amt/vachan-api/agmt/agmt.sock;
        }
    
    }
    ```

#### Link files to `sites-enabled`
 - `nginx.conf` file has to be linked first to `sites-available` and from `sites-available` to `sites-enabled`.
 - Run the commands
    - `sudo ln -s /home/amt/vachan-api/vachnaconfig/nginx.conf /etc/nginx/sites-available/`
    - `sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled`
 - Run command `sudo nginx -t` to check for syntax errors in the `nginx.conf` file.

#### Start Nginx process with our latest config
 - Run Command `sudo systemctl restart nginx`
