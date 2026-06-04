"""initial schema

Revision ID: 20260604_0001
Revises:
Create Date: 2026-06-04 23:35:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260604_0001"
down_revision = None
branch_labels = None
depends_on = None


role_enum = sa.Enum("ADMIN", "DEVOPS_ENGINEER", "DEVELOPER", "VIEWER", name="role")
server_status_enum = sa.Enum("RUNNING", "DEGRADED", "STOPPED", "UNKNOWN", name="serverstatus")
deployment_status_enum = sa.Enum(
    "PENDING", "RUNNING", "SUCCEEDED", "FAILED", "ROLLED_BACK", name="deploymentstatus"
)
incident_severity_enum = sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="incidentseverity")
incident_status_enum = sa.Enum("OPEN", "INVESTIGATING", "RESOLVED", name="incidentstatus")


def upgrade() -> None:
    bind = op.get_bind()
    role_enum.create(bind, checkfirst=True)
    server_status_enum.create(bind, checkfirst=True)
    deployment_status_enum.create(bind, checkfirst=True)
    incident_severity_enum.create(bind, checkfirst=True)
    incident_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "server",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("environment", sa.String(length=50), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=False),
        sa.Column("cpu_usage", sa.Float(), nullable=False),
        sa.Column("memory_usage", sa.Float(), nullable=False),
        sa.Column("status", server_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_server_name", "server", ["name"], unique=False)
    op.create_index("ix_server_environment", "server", ["environment"], unique=False)
    op.create_index("ix_server_ip_address", "server", ["ip_address"], unique=True)

    op.create_table(
        "deployment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column("environment", sa.String(length=50), nullable=False),
        sa.Column("status", deployment_status_enum, nullable=False),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_deployment_service", "deployment", ["service"], unique=False)
    op.create_index("ix_deployment_version", "deployment", ["version"], unique=False)
    op.create_index("ix_deployment_environment", "deployment", ["environment"], unique=False)
    op.create_index("ix_deployment_deployed_at", "deployment", ["deployed_at"], unique=False)

    op.create_table(
        "incident",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", incident_severity_enum, nullable=False),
        sa.Column("status", incident_status_enum, nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_incident_title", "incident", ["title"], unique=False)
    op.create_index("ix_incident_severity", "incident", ["severity"], unique=False)
    op.create_index("ix_incident_status", "incident", ["status"], unique=False)

    op.create_table(
        "incidentevent",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incident.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_incidentevent_incident_id", "incidentevent", ["incident_id"], unique=False)

    op.create_table(
        "uptimetarget",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("environment", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_uptimetarget_name", "uptimetarget", ["name"], unique=False)
    op.create_index("ix_uptimetarget_environment", "uptimetarget", ["environment"], unique=False)
    op.create_unique_constraint("uq_uptimetarget_url", "uptimetarget", ["url"])

    op.create_table(
        "uptimecheck",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("uptimetarget.id", ondelete="CASCADE"), nullable=False),
        sa.Column("response_time_ms", sa.Float(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_uptimecheck_target_id", "uptimecheck", ["target_id"], unique=False)
    op.create_index("ix_uptimecheck_checked_at", "uptimecheck", ["checked_at"], unique=False)

    op.create_table(
        "downtimeevent",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("uptimetarget.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=False),
    )
    op.create_index("ix_downtimeevent_target_id", "downtimeevent", ["target_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_downtimeevent_target_id", table_name="downtimeevent")
    op.drop_table("downtimeevent")
    op.drop_index("ix_uptimecheck_checked_at", table_name="uptimecheck")
    op.drop_index("ix_uptimecheck_target_id", table_name="uptimecheck")
    op.drop_table("uptimecheck")
    op.drop_constraint("uq_uptimetarget_url", "uptimetarget", type_="unique")
    op.drop_index("ix_uptimetarget_environment", table_name="uptimetarget")
    op.drop_index("ix_uptimetarget_name", table_name="uptimetarget")
    op.drop_table("uptimetarget")
    op.drop_index("ix_incidentevent_incident_id", table_name="incidentevent")
    op.drop_table("incidentevent")
    op.drop_index("ix_incident_status", table_name="incident")
    op.drop_index("ix_incident_severity", table_name="incident")
    op.drop_index("ix_incident_title", table_name="incident")
    op.drop_table("incident")
    op.drop_index("ix_deployment_deployed_at", table_name="deployment")
    op.drop_index("ix_deployment_environment", table_name="deployment")
    op.drop_index("ix_deployment_version", table_name="deployment")
    op.drop_index("ix_deployment_service", table_name="deployment")
    op.drop_table("deployment")
    op.drop_index("ix_server_ip_address", table_name="server")
    op.drop_index("ix_server_environment", table_name="server")
    op.drop_index("ix_server_name", table_name="server")
    op.drop_table("server")
    op.drop_index("ix_user_email", table_name="user")
    op.drop_table("user")

    bind = op.get_bind()
    incident_status_enum.drop(bind, checkfirst=True)
    incident_severity_enum.drop(bind, checkfirst=True)
    deployment_status_enum.drop(bind, checkfirst=True)
    server_status_enum.drop(bind, checkfirst=True)
    role_enum.drop(bind, checkfirst=True)
