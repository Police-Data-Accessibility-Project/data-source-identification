from sqlalchemy.orm import relationship

from src.db.models.helpers import get_created_at_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates import StandardModel


class URLProbedFor404(URLDependentMixin, StandardModel):
    __tablename__ = 'url_probed_for_404'

    last_probed_at = get_created_at_column()

    # Relationships
    url = relationship("URL", uselist=False, back_populates="probed_for_404")
