'''Database connection module'''

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_port = os.environ.get("VACHAN_POSTGRES_PORT", "5432")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres") #uday
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret") # uday@123
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "postgres") # vachan


SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s/%s"%(
	postgres_user,postgres_password,postgres_host,postgres_database)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
