"""add users table and user_id to tasks and notes

Revision ID: 002
Revises: 001
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa

revision      = "002"
down_revision = "001"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    # ── users table ───────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id",         sa.String(),                  nullable=False),
        sa.Column("email",      sa.String(255),               nullable=False),
        sa.Column("username",   sa.String(50),                nullable=False),
        sa.Column("password",   sa.String(255),               nullable=False),
        sa.Column("is_active",  sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),   nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),   nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email",    "users", ["email"],    unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # ── add user_id to tasks ──────────────────────────────────────────────────
    op.add_column("tasks", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_tasks_user_id", "tasks", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"])

    # ── add user_id to notes ──────────────────────────────────────────────────
    op.add_column("notes", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_notes_user_id", "notes", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_index("ix_notes_user_id", "notes", ["user_id"])


def downgrade() -> None:
    op.drop_constraint("fk_notes_user_id", "notes", type_="foreignkey")
    op.drop_index("ix_notes_user_id", "notes")
    op.drop_column("notes", "user_id")

    op.drop_constraint("fk_tasks_user_id", "tasks", type_="foreignkey")
    op.drop_index("ix_tasks_user_id", "tasks")
    op.drop_column("tasks", "user_id")

    op.drop_table("users")