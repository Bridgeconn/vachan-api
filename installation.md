
## Set up Vachan Engine locally using Makefile

### _Installing and Executing Makefile_

For your convinience we have made our installation steps into an single Makefile. So after cloning the vachan-api repository into your local machine you can see yourself it will have an makefile. So in order to run this makefile first you need to install 
<br>

```sudo apt update ```

```sudo apt install make```
<br>

with this command to you can succesfully install **make**  which is important to run our makefile


### **To run the makefile**
In order to run the makefile you need to go inside the _vachan-api_  folder and run the following command on your terminal

```cd vachan-api```

```Make setup```

During the execution of this command, the Makefile will initiate and prompt for your permission at various stages of the setup process, which you will need to provide manually.


### **Important Considerations: Key Points to Remember During Makefile Execution**

*When running the Makefile, it is crucial to keep a few things in mind. As the Makefile automates the installation process, in case it halts midway, you have the option to rerun that particular process without restarting the entire Makefile. Consequently, it will provide you with specific commands for each process, allowing for more targeted execution and troubleshooting.*
<br>

#### **To install basic python pre-requisite into your system**
```make pre-requisite```

*This will install python3-pip and python3-venv into your local machine.*
<br>

#### **To make an virtual environment onto your system**

```make venv-configure```
<br>

#### **To activate the Virtual Environment**

```make venv-activate```
<br>

#### **To install python packages required for the project**

```make install-dependencies```

*This will install requirements.txt file which is important python packages we need to run for the vachan-api and it will be installed onto your virtual environment*
<br>

####  **To check if all the above mentioned packages are installed onto your virtual environment**

```make check-package```
<br>

#### **To install PostgreSQL 15.3 onto your system**

```make installing-psql```
<br>

####  **To populate your database with data**

```make into-database```
<br>

#### **To modify your _.bashrc_ file**

```make environmental-variables```
<br>

#### _**Important points to remember**_

* Provide a valid email address for the SuperAdmin username

* Ensure that your password incorporates a combination of uppercase and   lowercase letters, special characters, and numbers

* Avoid using passwords that closely resemble  your username and to run it
<br>

#### **To install Usfm-Grammar 2.0**

```make installing-usfmgrammar```
<br>

#### **To install Docker and Docker-Compose**

```make installing-docker```
<br>

#### **To run kratos-Config from your system**

```make kratosconfig```
<br>

### In case the Makefile fails to work or encounters issues during execution, an alternative option is to follow our manual method. Detailed instructions for the manual setup can be found in the [README](https://github.com/Bridgeconn/vachan-api/blob/version-2/README.md) file.

