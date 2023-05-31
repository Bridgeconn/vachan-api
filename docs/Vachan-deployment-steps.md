# Deploy Vachan-api version-2 from scratch, using Docker

server: api.vachanengine.org(206.189.131.230)


## Stop existing services, if they are present
- vachan-api
- ngnix
- postgres(optional)
```
systemctl disable --now SERVICE-NAME
```

## Setup repo

Decide a location and clone version-2 code(we have used /home/gitautodeploy)

```
git clone --branch <branchname> <remote-repo-url>
git clone --branch version-2 https://github.com/Bridgeconn/vachan-api.git
```
Copy prod.env file to vachan-api/docker
Change the workflow file as per the decided location



## Docker and docker-compose

prefered versions
docker: 24.0.1

for docker installation, if required
https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

to remove sudo need
```
> sudo groupadd docker
> sudo usermod -aG docker $USER
> newgrp docker
> docker run hello-world #(to test)
```

## Start App

```
cd vachan-api/docker
docker compose --env-file prod.env --profile deployment up --build --force-recreate -d
```


The environment values to be set in `prod.env` or `.env`  file and their expected format are:
```
VACHAN_SUPER_USERNAME="<super-admin-emial-id>"
VACHAN_SUPER_PASSWORD="<a-strong-password>"
VACHAN_AUTH_DATABASE="postgresql://<DB-user>:<DB-passwords>@kratos-postgresd:<DB-port>/<DB-name>"
VACHAN_SUPPORT_EMAIL_CREDS="smtps://<email-id>:<password>:<email-service>:<smtp-port>/?skip_ssl_verify=true&legacy_ssl=true"
VACHAN_SUPPORT_EMAIL="<email-id>"
VACHAN_DOMAIN=api.vachanengine.org
VACHAN_KRATOS_PUBLIC_URL="http://api.vachanengine.org:4433/"
VACHAN_KRATOS_ADMIN_URL="http://api.vachanengine.org:4434/"
VACHAN_POSTGRES_PASSWORD="<a-strong-password>"

VACHAN_KRATOS_DB_USER="<vachan_auth_user>"
VACHAN_KRATOS_DB_PASSWORD="<a-strong-password>"
VACHAN_KRATOS_DB_NAME="<vachan_auth_db>"
VACHAN_GITLAB_TOKEN="<api-token-from-gitlab>"
VACHAN_REDIS_PASS="<a-strong-password>"

```

## Enable Auto deployment via github actions

### RSA Keys

```
> cd ~/.ssh # (cd ~ | mkdir .ssh , if not already present)
> ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   # (name the file github-actions
   # dont give passphrase)
> cat github-actions.pub >> authorized_keys
```
refernce: https://zellwk.com/blog/github-actions-deploy/

### Add secrets in github

* VACHAN_DO_HOST = 206.189.131.230
* VACHAN_DO_USERNAME = gitautodeploy
* SSH_KEY 


## Add SSL

Referenced article: https://mindsers.blog/post/https-using-nginx-certbot-docker/




