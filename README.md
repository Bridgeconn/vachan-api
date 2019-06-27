# vachan-api
The backend server that hosts all the API logic for the Vachan Engine.


### Prerequisites
[Postgres DB](https://www.postgresql.org/download/linux/ubuntu/)

### Set up and run
1. Create Postgres Database
2. Create tables using `/agmt/db.sql` file
3. Create and activate Python virual environment
4. Install Python dependencies using `pip3 install -r requirements.txt`
5. Run `gunicorn main:app`
