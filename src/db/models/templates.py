from sqlalchemy import Integer, Column
from sqlalchemy.orm import declarative_base

# Base class for SQLAlchemy ORM models
Base = declarative_base()

class StandardModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

