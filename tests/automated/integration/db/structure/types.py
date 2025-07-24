from typing import TypeAlias

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from tests.automated.integration.db.structure.testers.models.foreign_key import ForeignKeyTester
from tests.automated.integration.db.structure.testers.models.unique_constraint import UniqueConstraintTester

SATypes: TypeAlias = sa.Integer or sa.String or postgresql.ENUM or sa.TIMESTAMP or sa.Text
ConstraintTester: TypeAlias = UniqueConstraintTester or ForeignKeyTester
