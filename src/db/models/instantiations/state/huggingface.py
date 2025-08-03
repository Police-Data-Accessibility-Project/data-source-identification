from sqlalchemy import Column, Integer, DateTime

from src.db.models.templates_.base import Base


class HuggingFaceUploadState(Base):
    __tablename__ = "huggingface_upload_state"

    id = Column(Integer, primary_key=True)
    last_upload_at = Column(DateTime, nullable=False)