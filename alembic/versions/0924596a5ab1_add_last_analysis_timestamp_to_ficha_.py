"""add_last_analysis_timestamp_to_ficha_cliente

Revision ID: 0924596a5ab1
Revises: f62d190dfcf4
Create Date: 2025-11-20 12:40:45.625248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0924596a5ab1'
down_revision: Union[str, Sequence[str], None] = 'f62d190dfcf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('fichas_cliente', 
        sa.Column('last_analysis_timestamp', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('fichas_cliente', 'last_analysis_timestamp')
