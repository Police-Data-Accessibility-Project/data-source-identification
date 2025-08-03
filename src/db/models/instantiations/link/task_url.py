from sqlalchemy import UniqueConstraint, Column, Integer, ForeignKey

from src.db.models.templates_.base import Base


class LinkTaskURL(Base):
    __tablename__ = 'link_task_urls'
    __table_args__ = (UniqueConstraint(
        "task_id",
        "url_id",
        name="uq_task_id_url_id"),
    )

    task_id = Column(Integer, ForeignKey('tasks.id', ondelete="CASCADE"), primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id', ondelete="CASCADE"), primary_key=True)
