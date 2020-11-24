from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ContentType(Base):
    __tablename__ = "content_types"

    contentId = Column('content_type_id',Integer, primary_key=True, index=True, autoincrement=True)
    contentType = Column('content_type',String, unique=True)

