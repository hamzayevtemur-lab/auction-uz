from sqlalchemy import Column, Integer, String
from ..database import Base

class Category(Base):
    __tablename__ = "categories"

    id      = Column(Integer, primary_key=True, index=True)
    name_uz = Column(String(100), nullable=False)
    name_ru = Column(String(100), nullable=True)
    icon    = Column(String(50),  nullable=True)
    slug    = Column(String(100), unique=True, nullable=False)
