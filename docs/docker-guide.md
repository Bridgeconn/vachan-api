# A Guide to Using Docker, for Vachan-api V2

## Setup docker and docker-compose

prefered versions

docker: 20.10.6

docker-compose version:1.29.2

For docker installation, if required
https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

To re-install docker-compose, if using a version lower than 1.29
> `sudo rm $(which docker-compose)`

> https://docs.docker.com/compose/install .

To remove sudo need
```
> sudo groupadd docker
> sudo usermod -aG docker $USER
> newgrp docker
> docker run hello-world #(to test)
```

## Clone the right branch and repo

If you are setting up the vachan-api repo for the first time, clone the specific branch with the following command.

```git clone -b version-2 https://github.com/Bridgeconn/vachan-api.git```

If you have already set up the repo and remotes for development, pull latest code from [upstream/version-2](https://github.com/Bridgeconn/vachan-api/tree/version-2).


```cd vachan-api/docker```


## To start app locally

If you just want to setup and start app locally, from the vachan-api/docker folder, do

```docker-compose up```

VACHAN_SUPER_USERNAME, VACHAN_SUPER_PASSWORD are the minimum required environment variables. This can either be set in the `~/.bashrc` file or save in a local `.env` file and passed to the command as `docker-compose --env-file=path/to/file.env up`.

```
  export VACHAN_SUPER_USERNAME="<super-admin-emial-id>"
  export VACHAN_SUPER_PASSWORD="<a-strong-password>"
```
The username should be your email id and password must be a strong password.

If all goes well you should be able to get proper outputs at `http://localhost`, `http://localhost/docs`,
`http://127.0.0.1:4434/identities` and connect to postgresDB at `localhost`, `5433`

(Error reports from Kratos container related to failed email sending can be ignored as long as above URLs are accessible).

To turn the app down, use

```docker-compose down```

## To run tests

This method is recommended to just run all the tests once to make sure everything works, like in production, CI/CD or locally when verifying a PR. While doing local development and when we may have to run tests selectively and multiple times, after code changes, use the method specificed in [readme](../README.md#set-up-locally-for-development-and-testingwithout-docker).

```docker-compose -f run-test-dependencies.yml up -d```

```docker-compose -f run-tests.yml up --build --force-recreate```

To turn down the running containers

```docker-compose -f run-test-dependencies.yml -f run-tests.yml down```

## To deploy on server
Install docker, docker-compose & git and set up the right repo and branch. 

In the production-deploy version, we would connect the app to the centrally hosted Kratos user DB.
(To start that DB, in the same or different server, use the [this](../docker/Kratos_config/database.yml) docker-compose file.)
```
cd Kratos_config
docker-compose -f database.yml up -d
cd ..
```

Back in the vachan-api server,along with VACHAN_SUPER_USERNAME and VACHAN_SUPER_PASSWORD, need to set VACHAN_AUTH_DATABASE, VACHAN_SUPPORT_EMAIL_CREDS and VACHAN_SUPPORT_EMAIL as environment variables along with other required values, in the `prod.env` file.

Refer the following format
```
VACHAN_SUPER_USERNAME="<super-admin-emial-id>"
VACHAN_SUPER_PASSWORD="<a-strong-password>"
VACHAN_AUTH_DATABASE="postgresql://<DB-user>:<DB-passwords>@<server-ip>:<DB-port>/<DB-name>"
VACHAN_SUPPORT_EMAIL_CREDS="smtps://<email-id>:<password>:<email-service>:<smtp-port>/?skip_ssl_verify=true&legacy_ssl=true"
VACHAN_SUPPORT_EMAIL="<email-id>"
```

To re-create SSL certificates, follow instructions [here](https://mindsers.blog/post/https-using-nginx-certbot-docker/)

```
docker-compose -f production.yml run --rm certbot renew
```

### To start the app

```
cd ~/vachan-api/docker
docker-compose --env-file=prod.env -f production-deploy.yml up --build --force-recreate -d
```

### To re-deploy on server

After git pull, running the same command above, will re-build and re-start the containers.
```ssh user@server_address```

```
cd ~/vachan-api
git pull origin version-2
cd docker
```

```docker-compose --env-file=prod.env -f production-deploy.yml up --build --force-recreate -d```


To start with a fresh DB, stop and remove containers and remove volume `vachan-db-vol`.
To clear all old logs, similarly remove the volume `logs-vol`.
To clear all user data, remove the volume `kratos-sqlite`, on local or on the central server.

Some useful commands for the above tasks
```
docker-compose -f production-deploy.yml down

docker ps # list all running containers
docker ps -a # list all running and stopped containers
docker kill <id> # stop a specific docker container
docker rm $(docker ps -a -q) # removes all running and stopped docker images 

docker volume rm vachan-db-vol
```

For inspecting logs, DB etc check the corresponding docker volumes
```
docker volume list
docker volume inspect vachan-db-vol
sudo -i # to become root user to be able to cd into the voulume directory
cd path/to/docker/volume
ls
...
exit # to switch back to normal user
```

## For Development

To run the app and tests locally during development, you need to have only the Kratos docker containers running locally to facilitate authentication. Virtual environment, Database, usfm-grammar, environment variables etc should be set up seperatly locally. Follow the instructions in [readme](../README.md#set-up-locally-for-development-and-testingwithout-docker) for that.


## Frequently Encountered Issues

1. Compatibility issues with docker-compose version
> To be able to support the docker-copmose files used by us and by Kratos it is strongly recommended you upgrade to a docker-compose version >= 1.29. Instructions are [here](#)

2. Port 5432(or some other) already in use.
> This error occurs because there is a port mapping given in the docker-compose file(quick-start.yml, run-tests.yml, run-test-denpendecies.yml, production-deploy.yml etc) in the format 
```
    ports:
      # <host>:<container>
      - "5432:5432"
```
 and the port `5432` in the host machine is already being used by some other app(eg: local postgres service). You can change the mapped port to an unused value to fix this error
 ```
     ports:
      # <host>:<container>
      - "5435:5432"
```

3. Error related to `sources` table not found upon app start up is due to DB connection or DB initialization issues

4. Error related to super user not created or not found might be related to un successfull setting up of Kratos containers or DB connection

5. To remove users in Kratos
> While developing on local system, if you are running Kratos with quickstart.yml, stop the execution with `ctrl+c` and also do `docker-compose -f quickstart.yml down`. Then, after getting message on terminal that all containers have been removed(not just stopped), restart Kratos with `docker-compose -f quickstart.yml up`
