<a name="_int_4nblkg51"></a>**ERRORS OCCURED DURING VACHAN-API INSTALLATIONS**

1)E:Unable to locate git packages

<a name="_int_sjfdgv8r"></a>**Solution** : sudo apt update 

`                   `sudo apt-get install git

2)E:unable to correct problems you have broken packages

<a name="_int_l7lscw5e"></a>**Solution** : sudo dpkg --remove --force-remove-reinstreq <package-name>
`                   `sudo apt --fix-broken install

`                   `sudo apt install git

Check your software sources and repositories:

Open the "Software & Updates" application.
Go to the "Ubuntu Software" tab.
Verify that the "Main," "Universe," "Restricted," and "Multiverse" repositories are enabled.
Optionally, you can try changing the server mirror to a different location and then retry the installation.

then              sudo apt-get update --fix-missing
`                     `sudo apt-get install git


\3) Failing command: ['/home/user/vachan-api/vachan-ENV/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']

<a name="_int_11bhbt1q"></a>**Solution** : sudo apt install python3-venv

\4) Package 'pgadmin4' has no installation candidate

`   `<a name="_int_1fp1jfmf"></a>**Solution :** sudo apt install pgadmin4-desktop

`    `<https://itslinuxfoss.com/install-pgadmin-ubuntu-22-04/>


\5) unable to connect server connection failed:fatal password authentication failed for user   postgres

<a name="_int_5kojneow"></a>**Solution :** To fix the "FATAL: password authentication failed for user "postgres"" is by: (No matter for the pgsql or the pgAdmin) Changing the password for the postgres user with the following command: 

alter user postgres password 'yourpassword'; 



` `6) raise DockerException(
` `docker.errors.DockerException: Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied'))

` `**<a name="_int_5nelq2pl"></a>Solution** :

`     `1. Enter the command below to create the docker group on the system.

`         `sudo groupadd -f docker

`      `2. Type the following [usermod command](https://phoenixnap.com/kb/usermod-linux) to add the active user to       the docker group.

`         `sudo usermod -aG docker $USER

`     `3. Apply the group changes to the current terminal session by typing:

`        `newgrp docker

`     `4. Check if the docker group is in the list of user groups.

`         `Groups

\7) psql: error: connection to server on socket "/var/run/postgresql/\.<a name="_int_roiiwq81"></a>s\.PGSQL\.5432"    failed: FATAL: role "user" does not exist

**Solution** CREATE ROLE user LOGIN;

GRANT ALL PRIVILEGES ON DATABASE databasename TO user;

\8) raise HTTPexception:(status code=400, detail=error details) fastapi\.exceptions\.HTTPException 

`   `**Solution**: giver superadmin mail id as a new valid mail <a name="_int_d10kdyke"></a>id which you havn't used in earlier installation.     Password should contail combination of uppercase,lowercase,special character and numbers. First characters of username and Password mustbe different inside the bashrc file

\9) 'psql' is not recognized as an internal or external command, operable program or batch file\.

`     `**<a name="_int_ejxjdm8f"></a>Solution** : You can download the latest version of PostgreSQL from the official               website: <https://www.postgresql.org/download/>

Add PostgreSQL to your system's PATH environment variable: If you have already installed PostgreSQL, make sure that the bin directory of the PostgreSQL installation is added to your system's PATH environment variable. To do this, follow these steps:

1. Open the Start menu and search for "Environment Variables".
1. Click on "Edit the system environment variables".
1. In the System Properties window, click on the "Environment Variables" button.
1. Under "System variables", scroll down and find the "Path" variable. Click on "Edit".
1. Click on "New" and add the path to the bin directory of your PostgreSQL installation (<a name="_int_27px4aku"></a>e.g. "C:\Program Files\PostgreSQL\13\bin"). Make sure to separate it from the existing paths using a semicolon (;).
1. Click "OK" to save the changes and close all the windows.

`    `Restart your command prompt: If you made changes to your system's PATH environment     variable, you need to close and reopen your command prompt for the changes to take effect.

After you have installed and configured PostgreSQL and added it to your system's PATH environment variable, you should be able to run the psql command without any issues.


\10) Import Error: No module named 'module\_name'



`  `**Solution**: This error occurs when the required module is not installed or not found. You can try installing the module using pip or the package manager specific to your programming language. For example, if you're using Python, you can run "pip install module\_name" to install the missing module.


\11) Command not found

`   `**Solution**: This error typically occurs when you're trying to run a command that is not recognized by the system. Make sure the command is spelled correctly and that the corresponding package or program is installed. If the command is part of a specific software or tool, refer to the documentation for installation instructions.


\12) File not found

`  `**Solution**: This error occurs when a file or directory specified in the command or code cannot be found. Double-check the file path and make sure it exists in the specified location. If the file is missing, ensure that it has been properly downloaded or created. If the file is meant to be included in your project, verify that it is present in the correct directory.





**NOTES:**

- Ubuntu version 22 already includes Python 3.10.6 as the default version.
- <a name="_int_kioolxfg"></a>Tried to install usfm-grammar in the initial part of installation













