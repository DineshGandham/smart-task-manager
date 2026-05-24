"""create tasks and notes tables

Revision ID: 001
Revises:
Create Date: 2026-05-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("tasks",
                    sa.Column("id", sa.String(), nullable=False),
                    sa.Column("title", sa.String(200), nullable=False),
                    sa.Column("description", sa.Text(),                      nullable=True),
                    sa.Column("status",      sa.String(20),  server_default="todo",   nullable=False),
                    sa.Column("priority",    sa.String(20),  server_default="medium", nullable=False),
                    sa.Column("due_date",    sa.Date(),                      nullable=True),
                    sa.Column("tags",        ARRAY(sa.String()), server_default="{}", nullable=False),
                    sa.Column("created_at",  sa.DateTime(timezone=True),    nullable=False),
                    sa.Column("updated_at",  sa.DateTime(timezone=True),    nullable=False),
                    sa.PrimaryKeyConstraint("id"),
            )
    
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_created", "tasks", ["created_at"])

    op.create_table("notes",
                    sa.Column("id",             sa.String(),                    nullable=False),
                    sa.Column("title",          sa.String(200),                 nullable=False),
                    sa.Column("content",        sa.Text(),                      nullable=False),
                    sa.Column("tags",           ARRAY(sa.String()), server_default="{}", nullable=False),
                    sa.Column("linked_task_id", sa.String(),                    nullable=True),
                    sa.Column("created_at",     sa.DateTime(timezone=True),    nullable=False),
                    sa.Column("updated_at",     sa.DateTime(timezone=True),    nullable=False),
                    sa.PrimaryKeyConstraint("id"),
            )
    
    op.create_index("ix_notes_linked_task", "notes", ["linked_task_id"])
    op.create_index("ix_notes_created", "notes", ["created_at"])


def downgrade() -> None:
    op.drop_table("notes")
    op.drop_table("tasks")