'''Common stuff required by main and different routers'''

#pylint: disable=E0401
#pylint gives import error if relative import is not used. But app(uvicorn) doesn't accept it
import os
import logging
from logging.handlers import RotatingFileHandler
from database import SessionLocal

# Define and configure logger so that all other modules can use it
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("VACHAN_LOGGING_LEVEL", "WARNING"))
handler = RotatingFileHandler('../logs/API_logs.log', maxBytes=10000000, backupCount=10)
fmt = logging.Formatter(fmt='%(asctime)s|%(filename)s:%(lineno)d|%(levelname)-8s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
log.addHandler(handler)

def get_db():
    '''To start a DB connection(session)'''
    db_ = SessionLocal()
    try:
        yield db_
    finally:
        # pass
        db_.close()
