from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres") 
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "postgres") 
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret") 

SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s/%s"%(postgres_user,postgres_password,postgres_host,postgres_database)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()