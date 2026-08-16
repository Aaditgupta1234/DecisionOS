"""Create background_jobs table for Phase 10.1 Background Job Infrastructure.

Revision ID: 0018_background_jobs
Revises: 0017_dashboard_snapshots
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0018_background_jobs'
down_revision: Union[str, None] = '0017_dashboard_snapshots'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create table
    op.create_table(
        'background_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('progress_percent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('result_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{\"summary\": {}, \"artifacts\": {}, \"warnings\": []}'::jsonb")),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 2. Create indexes
    op.create_index('ix_background_jobs_id', 'background_jobs', ['id'], unique=False)
    op.create_index('ix_background_jobs_organization_id', 'background_jobs', ['organization_id'], unique=False)
    op.create_index('ix_background_jobs_created_by_user_id', 'background_jobs', ['created_by_user_id'], unique=False)
    op.create_index('ix_background_jobs_job_type', 'background_jobs', ['job_type'], unique=False)
    op.create_index('ix_background_jobs_status', 'background_jobs', ['status'], unique=False)
    op.create_index('ix_background_jobs_org_status', 'background_jobs', ['organization_id', 'status'], unique=False)
    op.create_index('ix_background_jobs_org_created', 'background_jobs', ['organization_id', 'created_at'], unique=False)
    op.create_index('ix_background_jobs_org_type', 'background_jobs', ['organization_id', 'job_type'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_background_jobs_org_type', table_name='background_jobs')
    op.drop_index('ix_background_jobs_org_created', table_name='background_jobs')
    op.drop_index('ix_background_jobs_org_status', table_name='background_jobs')
    op.drop_index('ix_background_jobs_status', table_name='background_jobs')
    op.drop_index('ix_background_jobs_job_type', table_name='background_jobs')
    op.drop_index('ix_background_jobs_created_by_user_id', table_name='background_jobs')
    op.drop_index('ix_background_jobs_organization_id', table_name='background_jobs')
    op.drop_index('ix_background_jobs_id', table_name='background_jobs')
    op.drop_table('background_jobs')
