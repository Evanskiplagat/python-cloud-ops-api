"""add audit logs

Revision ID: 20260610_0002
Revises: 20260604_0001
Create Date: 2026-06-10 10:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260610_0002"
down_revision = "20260604_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auditlog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("before_state", sa.JSON(), nullable=True),
        sa.Column("after_state", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_auditlog_actor_user_id", "auditlog", ["actor_user_id"], unique=False)
    op.create_index("ix_auditlog_action", "auditlog", ["action"], unique=False)
    op.create_index("ix_auditlog_entity_type", "auditlog", ["entity_type"], unique=False)
    op.create_index("ix_auditlog_entity_id", "auditlog", ["entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_auditlog_entity_id", table_name="auditlog")
    op.drop_index("ix_auditlog_entity_type", table_name="auditlog")
    op.drop_index("ix_auditlog_action", table_name="auditlog")
    op.drop_index("ix_auditlog_actor_user_id", table_name="auditlog")
    op.drop_table("auditlog")
