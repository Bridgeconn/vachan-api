# Vachan-api

The server application that provides REST APIs to interact with the underlying Databases (SQL and Graph) and modules in Vachan-Engine.

Currently serving 3 client applications, VachanOnline website, the Vachan Mobile App and AutographaMT Bible translation tool.

## Implementation Details

Implemented Using
- Python 3.10.6
- Fastapi framework
- Postgresql Database
- Ory Kratos for Authentication
- Redis for caching and job queueing 
- Usfm-grammar
- Makefile


## Set up locally for development and testing


### **_Steps_**

>Fork the repo into your github account and then use the terminal to clone the repository on your local machine with the following steps

```mkdir vachan-api```

```cd vachan-api```

```git init```

```git remote add upstream https://github.com/Bridgeconn/vachan-api.git```

```git remote add origin  https://github.com/<your-account>/vachan-api.git```

```git fetch upstream```

```git checkout -b version-2```

```git pull upstream version-2```


## Things going on in Makefile

Since you probably don't know much about makefile, its automatiting our installation process. So we will guide through whats going on here.

*  ### Set up virtual Environment 
*  ### Activate the Virtual Environment
*  ### Installing required python packages to run the project
*  ### Install PostgreSQL 15.3
*  ### Populate the database with data
*  ### Install Usfm-Grammar2.0
*  ### Install Docker and Docker-compose
*  ### Run kratos-config


## Installation of Vachan-Engine into your localhost

For your convinience we have made our installation steps into an single Makefile. So after cloning the vachan-api repository into your local machine you can see yourself it will have an makefile. So in order to run this makefile first you need to install 

> sudo apt update\
sudo apt install make

so with this you can run the makefile easily.

### **To run the makefile**
In order to run the makefile you need to go inside the _vachan-api_  folder and run the following command on your terminal

> cd vachan-api 

> Make setup

With this command the makefile will run and as the setup process goes on it will ask permission from yourself which you have to give by yourself.

### **Things to remember**

*There are somethings to remember while running the makefile. Since the makefile is an automated process of our installation, if it stops in midway you can try run that process again without running the whole makefile again.So that i will provide you commands for each process.*

#### **To install basic python pre-requisite into your system**


*This will install python3-pip and python3-venv into your local machine.*

> make pre-requisite

#### **To make an virtual environment onto your system**

>	make venv-configure

#### **To activate the Virtual Environment**

>	make venv-activate

#### **To install python packages required for the project**

*This will install requirements.txt file which is important python packages we need to run for the vachan-api and it will be installed onto your virtual environment

>	make install-dependencies

####  **To check if all the above mentioned packages are installed onto your virtual environment**

>	make check-package

#### **To install PostgreSQL 15.3 onto your system**

>	make installing-psql

####  **To populate your database with data**

>	make into-database

#### **To modify your _.bashrc_ file**

_Some things to note_

* Provide a valid email address for the SuperAdmin username

* Ensure that your password incorporates a combination of uppercase and   lowercase letters, special characters, and numbers.

* Avoid using passwords that closely resemble  your username

and to run it

>	make environmental-variables

#### **To install Usfm-Grammar 2.0**

>	make installing-usfmgrammar


#### **To install Docker and Docker-Compose**

>	make installing-docker

#### **To run kratos-Config from your system**

>	make kratosconfig


### If the make file doesn't work or you cant run it properly you can try our mannual method and you can find it on README.md 
