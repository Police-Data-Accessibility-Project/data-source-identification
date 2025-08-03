from sqlalchemy import Integer, Column

from src.db.models.templates_.base import Base



class WithIDBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

