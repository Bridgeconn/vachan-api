from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class ContentType(Base):
    __tablename__ = "content_types"

    content_id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, unique=True)
    key = Column(String)


