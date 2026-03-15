"""Add plan_aktivnosti table

Revision ID: a1b2c3d4e5f6
Revises: 199acb367744
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '199acb367744'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('plan_aktivnosti',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(length=20), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=True),
        sa.Column('activity', sa.String(length=500), nullable=False),
        sa.Column('organizer_guide', sa.String(length=300), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plan_aktivnosti_month'), 'plan_aktivnosti', ['month'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_plan_aktivnosti_month'), table_name='plan_aktivnosti')
    op.drop_table('plan_aktivnosti')
