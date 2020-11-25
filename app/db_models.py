''' Defines SQL Alchemy models for each Database Table'''

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ContentType(Base):
    '''Corresponds to table content_types in vachan DB(postgres)'''
    __tablename__ = "content_types"

    contentId = Column('content_type_id',Integer, primary_key=True, index=True, autoincrement=True)
    contentType = Column('content_type',String, unique=True)
