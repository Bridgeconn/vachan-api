# Database setup instructions for Vachan

### Prerequisites
* Postgresql

### steps

1. login to psql (command line interface for Postgres) using your username and password
2. create a new database, in the name you want
	`CREATE DATABASE db_name;`
3. exit from psql ( `\d` )
4. from terminal use command 
	`>>> psql db_name < seed_DB.sql`
	(use you username and password if required)

#### For AgMT 
5. Add a new user and verify (via UI or API). Then set the roles to superadmin's in the DB
	`UPDATE autographamt_users SET role_id = 3 where user_id=1;`

	