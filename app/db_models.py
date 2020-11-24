from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ContentType(Base):
    __tablename__ = "content_types"

    contentId = Column('content_id',Integer, primary_key=True, index=True)
    contentType = Column('content_type',String, unique=True)
    key = Column(String)


