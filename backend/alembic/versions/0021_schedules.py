"""Create schedules and schedule_executions tables for Phase 10.4 Scheduled Intelligence.

Revision ID: 0021_schedules
Revises: 0020_audit_records
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0021_schedules'
down_revision: Union[str, None] = '0020_audit_records'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create schedules table
    op.create_table(
        'schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('schedule_type', sa.String(length=50), nullable=False, server_default='FORECAST_REFRESH'),
        sa.Column('cron_expression', sa.String(length=100), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_schedules_id', 'schedules', ['id'], unique=False)
    op.create_index('ix_schedules_organization_id', 'schedules', ['organization_id'], unique=False)
    op.create_index('ix_schedules_created_by_user_id', 'schedules', ['created_by_user_id'], unique=False)
    op.create_index('ix_schedules_schedule_type', 'schedules', ['schedule_type'], unique=False)
    op.create_index('ix_schedules_is_enabled', 'schedules', ['is_enabled'], unique=False)
    op.create_index('ix_schedules_next_run_at', 'schedules', ['next_run_at'], unique=False)
    op.create_index('ix_schedules_org_enabled_next', 'schedules', ['organization_id', 'is_enabled', 'next_run_at'], unique=False)
    op.create_index('ix_schedules_org_type', 'schedules', ['organization_id', 'schedule_type'], unique=False)

    # 2. Create schedule_executions table
    op.create_table(
        'schedule_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('schedule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('background_jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('execution_status', sa.String(length=20), nullable=False, server_default='SUCCESS'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_schedule_executions_id', 'schedule_executions', ['id'], unique=False)
    op.create_index('ix_schedule_executions_schedule_id', 'schedule_executions', ['schedule_id'], unique=False)
    op.create_index('ix_schedule_executions_organization_id', 'schedule_executions', ['organization_id'], unique=False)
    op.create_index('ix_schedule_executions_job_id', 'schedule_executions', ['job_id'], unique=False)
    op.create_index('ix_schedule_executions_execution_status', 'schedule_executions', ['execution_status'], unique=False)
    op.create_index('ix_schedule_executions_started_at', 'schedule_executions', ['started_at'], unique=False)
    op.create_index('ix_schedule_executions_schedule_started', 'schedule_executions', ['schedule_id', 'started_at'], unique=False)
    op.create_index('ix_schedule_executions_org_status', 'schedule_executions', ['organization_id', 'execution_status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_schedule_executions_org_status', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_schedule_started', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_started_at', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_execution_status', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_job_id', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_organization_id', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_schedule_id', table_name='schedule_executions')
    op.drop_index('ix_schedule_executions_id', table_name='schedule_executions')
    op.drop_table('schedule_executions')

    op.drop_index('ix_schedules_org_type', table_name='schedules')
    op.drop_index('ix_schedules_org_enabled_next', table_name='schedules')
    op.drop_index('ix_schedules_next_run_at', table_name='schedules')
    op.drop_index('ix_schedules_is_enabled', table_name='schedules')
    op.drop_index('ix_schedules_schedule_type', table_name='schedules')
    op.drop_index('ix_schedules_created_by_user_id', table_name='schedules')
    op.drop_index('ix_schedules_organization_id', table_name='schedules')
    op.drop_index('ix_schedules_id', table_name='schedules')
    op.drop_table('schedules')
