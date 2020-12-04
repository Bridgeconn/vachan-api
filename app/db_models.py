''' Defines SQL Alchemy models for each Database Table'''

from sqlalchemy import Column, Integer, String
# from sqlalchemyimport Boolean, ForeignKey
# from sqlalchemy.orm import relationship

from database import Base


class ContentType(Base): # pylint: disable=too-few-public-methods 
    '''Corresponds to table content_types in vachan DB(postgres)'''
    __tablename__ = "content_types"

    contentId = Column('content_type_id',Integer, primary_key=True)
    contentType = Column('content_type',String, unique=True)

class Language(Base): # pylint: disable=too-few-public-methods 
    '''Corresponds to table languages in vachan DB(postgres)'''
    __tablename__ = 'languages'

    languageId = Column('language_id', Integer, primary_key=True)
    code = Column('language_code', String, unique=True, index=True)
    language = Column('language_name', String)
    scriptDirection = Column('script_direction', String)
