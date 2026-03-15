"""Enhanced User Model - email, last_login, is_active, roles

Revision ID: enhanced_user_model
Revises:
Create Date: 2026-03-15 10:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "enhanced_user_model"
down_revision = "72fbd838071f"  # Poslednja migracija
branch_labels = None
depends_on = None


def upgrade():
    # Dodajemo kolone u user tabelu

    # 1. Email kolona
    op.add_column("user", sa.Column("email", sa.String(120), nullable=True))
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=False)
    op.create_index(op.f("ix_user_role"), "user", ["role"], unique=False)

    # 2. is_active kolona
    op.add_column(
        "user",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # 3. created_at i updated_at
    op.add_column(
        "user",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.add_column("user", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # 4. first_name i last_name
    op.add_column("user", sa.Column("first_name", sa.String(50), nullable=True))
    op.add_column("user", sa.Column("last_name", sa.String(50), nullable=True))

    # 5. last_login (nullable - biće ažuriran pri svakoj prijavi)
    op.add_column("user", sa.Column("last_login", sa.DateTime(), nullable=True))


def downgrade():
    # Brišemo kolone
    op.drop_column("user", "last_login")
    op.drop_column("user", "last_name")
    op.drop_column("user", "first_name")
    op.drop_column("user", "updated_at")
    op.drop_column("user", "created_at")
    op.drop_column("user", "is_active")
    op.drop_index(op.f("ix_user_role"), table_name="user")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_column("user", "email")
