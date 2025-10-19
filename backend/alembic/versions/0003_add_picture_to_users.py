"""add picture to users

Revision ID: 0003
Revises: 0002
Create Date: 2025-10-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add picture column to users table
    op.add_column('users', sa.Column('picture', sa.String(length=512), nullable=True))


def downgrade() -> None:
    # Remove picture column from users table
    op.drop_column('users', 'picture')

