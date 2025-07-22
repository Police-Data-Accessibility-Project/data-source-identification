"""Change batch completed to ready to label

Revision ID: e285e6e7cf71
Revises: 997f5bf53772
Create Date: 2025-04-17 09:09:38.137131

"""
from typing import Sequence, Union

from src.util.alembic_helpers import alter_enum_value

# revision identifiers, used by Alembic.
revision: str = 'e285e6e7cf71'
down_revision: Union[str, None] = '997f5bf53772'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    alter_enum_value(
        enum_name="batch_status",
        old_value="complete",
        new_value="ready to label"
    )



def downgrade() -> None:
    alter_enum_value(
        enum_name="batch_status",
        old_value="ready to label",
        new_value="complete"
    )
