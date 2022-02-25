'''Database connection module'''

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

postgres_host = os.environ.get("VACHAN_POSTGRES_HOST", "localhost")
postgres_user = os.environ.get("VACHAN_POSTGRES_USER", "postgres")
postgres_database = os.environ.get("VACHAN_POSTGRES_DATABASE", "vachan")
postgres_password = os.environ.get("VACHAN_POSTGRES_PASSWORD", "secret")
postgres_port = os.environ.get("VACHAN_POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://%s:%s@%s:%s/%s"%(
	postgres_user,postgres_password,postgres_host, postgres_port,postgres_database)

connection_url = os.environ.get("VACHAN_POSTGRES_CONN", SQLALCHEMY_DATABASE_URL)

engine = create_engine(connection_url, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# meta = MetaData(naming_convention={
#         "ix": "%(table_name)s_ix_%(column_0_label)s",
#         "uq": "uq_%(table_name)s_%(column_0_name)s",
#         "ck": "ck_%(table_name)s_%(constraint_name)s",
#         "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#         "pk": "pk_%(table_name)s"
#       })
# Base = declarative_base(metadata=meta)

Base = declarative_base()
