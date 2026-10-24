"""index foreign keys

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-23 21:25:04.690288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Index the foreign keys every project/task query filters on."""
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)
    op.create_index(op.f('ix_tasks_project_id'), 'tasks', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tasks_project_id'), table_name='tasks')
    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
