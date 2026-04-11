"""Merge plan_aktivnosti and enhanced_user_model branches

Revision ID: 132238bfd91f
Revises: 
Create Date: 2026-04-10 17:02:36.651234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '132238bfd91f'
down_revision = ('a1b2c3d4e5f6', 'enhanced_user_model')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
