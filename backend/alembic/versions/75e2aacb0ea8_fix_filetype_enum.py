"""fix_filetype_enum

Revision ID: 75e2aacb0ea8
Revises: 03884f5af62e
Create Date: 2025-08-17 10:27:34.909817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75e2aacb0ea8'
down_revision: Union[str, Sequence[str], None] = '03884f5af62e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the missing filetype enum
    filetype_enum = sa.Enum('VIDEO', 'THUMBNAIL', 'AUDIO', 'TRANSCRIPT', 'EXPORT', name='filetype')
    filetype_enum.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the filetype enum
    filetype_enum = sa.Enum('VIDEO', 'THUMBNAIL', 'AUDIO', 'TRANSCRIPT', 'EXPORT', name='filetype')
    filetype_enum.drop(op.get_bind(), checkfirst=True)
