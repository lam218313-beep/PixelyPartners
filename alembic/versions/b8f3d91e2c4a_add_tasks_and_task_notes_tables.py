"""add_tasks_and_task_notes_tables

Revision ID: b8f3d91e2c4a
Revises: 0924596a5ab1
Create Date: 2025-11-24 01:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'b8f3d91e2c4a'
down_revision: Union[str, Sequence[str], None] = '0924596a5ab1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add tasks and task_notes tables."""
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ficha_cliente_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('area_estrategica', sa.String(length=100), nullable=True),
        sa.Column('urgencia', sa.String(length=50), nullable=True),
        sa.Column('score_impacto', sa.Integer(), nullable=True),
        sa.Column('score_esfuerzo', sa.Integer(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=True),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDIENTE', 'EN_CURSO', 'HECHO', 'REVISADO', name='taskstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ficha_cliente_id'], ['fichas_cliente.id'], )
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_ficha_cliente_id'), 'tasks', ['ficha_cliente_id'], unique=False)
    
    # Create task_notes table
    op.create_table(
        'task_notes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], )
    )
    op.create_index(op.f('ix_task_notes_id'), 'task_notes', ['id'], unique=False)
    op.create_index(op.f('ix_task_notes_task_id'), 'task_notes', ['task_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop tasks and task_notes tables."""
    op.drop_index(op.f('ix_task_notes_task_id'), table_name='task_notes')
    op.drop_index(op.f('ix_task_notes_id'), table_name='task_notes')
    op.drop_table('task_notes')
    
    op.drop_index(op.f('ix_tasks_ficha_cliente_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    
    op.execute('DROP TYPE taskstatus')
