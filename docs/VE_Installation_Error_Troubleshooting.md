# Troubleshooting Common Errors in Vachan-API Setup: Solutions and Fixes

### 1) Unable to locate git packages  

  **Solution:** 
  - `sudo apt update`
  - `sudo apt-get install git`


### 2) Issues with Broken Packages
   **Solution:** 
   - `sudo dpkg --remove --force-remove-reinstreq <package-name>`
   - `sudo apt --fix-broken install`
   
   
   Check your software sources and repositories:
   - Open the "Software & Updates" application.
   - Go to the "Ubuntu Software" tab.
   - Verify that the "Main," "Universe," "Restricted," and "Multiverse" repositories are enabled.
   - Optionally, you can try changing the server mirror to a different location and then retry the installation.
   

### 3) The virtual environment was not created successfully because ensurepip is not available.Failing command: ['~/vachan-api/vachan-ENV/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']
  
   **Solution:** 

   `sudo apt install python3-venv`

### 4) Package 'pgadmin4' has no installation candidate
   
   **Solution:**
   
   - `curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add`
   - `sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'`
   - `sudo apt install pgadmin4-desktop`
   
   More information: [Installation Guide for pgAdmin on Ubuntu 22.04](https://itslinuxfoss.com/install-pgadmin-ubuntu-22-04/)

### 5) Unable to connect server connection failed: fatal password   authentication failed for user postgres

   **Solution:**

 To fix the "FATAL: password authentication failed for user 'postgres'" error, change the password for the postgres user with the following command:
   
   `alter user postgres password 'yourpassword';`


### 6) Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get [How to fix Docker Permission Denied](http://%2Fvar%2Frun%2Fdocker.sock/v1.24/version): dial unix /var/run/docker.sock: connect: permission denied 
   
   **Solution:** 

   1. Enter the command below to create the docker group on the system:

      `sudo groupadd -f docker`
   2. Add the active user to the docker group:

      `sudo usermod -aG docker $USER`
   3. Apply the group changes to the current terminal session:

      `newgrp docker`
   4. Check if the docker group is in the list of user groups.

### 7)Docker daemon not running
 
 **Solution**
  - Run the command `systemctl status docker` to check the status of the  Docker daemon.;
   - If the Docker daemon is not running, start it using the command `sudo systemctl start docker`
 


### 8) psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL: role "user" does not exist

  **Solution:** 
   - `CREATE ROLE user LOGIN;`
   - `GRANT ALL PRIVILEGES ON DATABASE databasename TO user;`

### 9) raise HTTPexception:(status code=400, detail=error details) fastapi.exceptions.HTTPException

**Solution:** 
    
1. Provide a valid email address for the SuperAdmin username
2. Ensure that your password incorporates a combination of uppercase and   lowercase letters, special characters, and numbers.
3. Avoid using passwords that closely resemble  your username


### 10) 'psql' is not recognized as an internal or external command, operable program or batch file.
    
**Solution:**

- Download the latest version of PostgreSQL from the official website: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
- Add PostgreSQL to your system's PATH environment variable:
       
    - Open the Start menu and search for "Environment Variables".
    - Click on "Edit the system environment variables".
    - In the System Properties window, click on the "Environment Variables" button.
    - Under "System variables," scroll down and find the "Path" variable. Click on "Edit".
    - Click on "New" and add the path to the bin directory of your PostgreSQL installation (e.g. "C:\Program Files\PostgreSQL\13\bin"). Make sure to separate it from the existing paths using a semicolon (;).
    - Click "OK" to save the changes and close all the windows.
    - Restart your command prompt: If you made changes to your system's PATH environment variable, you need to close and reopen your command prompt for the changes to take effect.
    - After you have installed and configured PostgreSQL and added it to your system's PATH environment variable, you should be able to run the `psql` command without any issues.

### 11) Import Error: No module named 'module_name'

**Solution:** 

This error occurs when the required module is not installed or not found. You can try installing the module using pip or the package manager specific to your programming language. For example, if you're using Python, you can run `pip install module_name` to install the missing module.



## NOTES:
- Ubuntu version 22 already includes Python 3.10.6 as the default version.
- install usfm-grammar before installing any other package in case there are any installation issues with it.















