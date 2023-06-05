# Solutions for errors you may encounter during Vachan-api setup 

### 1) E: Unable to locate git packages  

  **Solution:** 
  - `sudo apt update`
  - `sudo apt-get install git`


### 2) E: Unable to correct problems you have broken packages  
   **Solution:** 
   - `sudo dpkg --remove --force-remove-reinstreq <package-name>`
   - `sudo apt --fix-broken install`
   - `sudo apt install git`
   
   Check your software sources and repositories:
   - Open the "Software & Updates" application.
   - Go to the "Ubuntu Software" tab.
   - Verify that the "Main," "Universe," "Restricted," and "Multiverse" repositories are enabled.
   - Optionally, you can try changing the server mirror to a different location and then retry the installation.
   
   Then run:
   - `sudo apt-get update --fix-missing`
   - `sudo apt-get install git`

### 3) The virtual environment was not created successfully because ensurepip is not available.Failing command: ['/home/athulya/vachan-api/vachan-ENV/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']
  
   **Solution:** 

   `sudo apt install python3-venv`

### 4) Package 'pgadmin4' has no installation candidate
   
   **Solution:**
   
   `sudo apt install pgadmin4-desktop`
   
   More information: [Installation Guide for pgAdmin on Ubuntu 22.04](https://itslinuxfoss.com/install-pgadmin-ubuntu-22-04/)

### 5) Unable to connect server connection failed: fatal password   authentication failed for user postgres

   **Solution:**

 To fix the "FATAL: password authentication failed for user 'postgres'" error, change the password for the postgres user with the following command:
   
   `alter user postgres password 'yourpassword';`



### 6) DockerException: Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied'))

   **Solution:** 
   1. Enter the command below to create the docker group on the system:

      `sudo groupadd -f docker`
   2. Add the active user to the docker group:

      `sudo usermod -aG docker $USER`
   3. Apply the group changes to the current terminal session:

      `newgrp docker`
   4. Check if the docker group is in the list of user groups.


### 7) psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL: role "user" does not exist

  **Solution:** 
   - `CREATE ROLE user LOGIN;`
   - `GRANT ALL PRIVILEGES ON DATABASE databasename TO user;`

GRANT ALL PRIVILEGES ON DATABASE databasename TO user;



### 8) raise HTTPexception:(status code=400, detail=error details) fastapi.exceptions.HTTPException

**Solution:** 
    
Provide a new valid email address for the superadmin account that you haven't used in earlier installations. Make sure the password contains a combination of uppercase, lowercase, special characters, and numbers. The first characters of the username and password must be different inside the bashrc file.

### 9) 'psql' is not recognized as an internal or external command, operable program or batch file.
    
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

### 10) Import Error: No module named 'module_name'

**Solution:** 

This error occurs when the required module is not installed or not found. You can try installing the module using pip or the package manager specific to your programming language. For example, if you're using Python, you can run `pip install module_name` to install the missing module.

### 11) Command not found

**Solution:** 
   
   This error typically occurs when you're trying to run a command that is not recognized by the system. Make sure the command is spelled correctly and that the corresponding package or program is installed. If the command is part of a specific software or tool, refer to the documentation for installation instructions.

### 12) File not found

**Solution:** 

This error occurs when a file or directory specified in the command or code cannot be found. Double-check the file path and make sure it exists in the specified location. If the file is missing, ensure that it has been properly downloaded or created. If the file is meant to be included in your project, verify that it is present in the correct directory.


## NOTES:
- Ubuntu version 22 already includes Python 3.10.6 as the default version.
- Tried to install usfm-grammar in the initial part of installation.















