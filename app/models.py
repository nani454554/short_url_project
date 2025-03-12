from sqlalchemy import Column, String, Integer
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_id = Column(String, unique=True, index=True)
    original_url = Column(String)
    clicks = Column(Integer, default=0)
