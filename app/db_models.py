''' Defines SQL Alchemy models for each Database Table'''
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy import DateTime
from pytz import timezone
from database import Base  # pylint: disable=import-error

ist_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')

dynamicTables = {}

class Language(Base): # pylint: disable=too-few-public-methods
    '''Corresponds to table languages in vachan DB(postgres)'''
    __tablename__ = 'languages'

    languageId = Column('language_id', Integer, primary_key=True)
    code = Column('language_code', String, unique=True, index=True)
    language = Column('language_name', String)
    scriptDirection = Column('script_direction', String)
    localScriptName = Column('localscript_name',String)
    metaData = Column('metadata', JSON)
    createdUser = Column('created_user', String)
    createTime = Column('created_at',DateTime,default=ist_time)
    updatedUser = Column('last_updated_user', String)
    updateTime = Column('last_updated_at', DateTime, onupdate=ist_time)
