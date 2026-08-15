"""Create dashboard_snapshots and dashboard_view_events tables for Phase 9.6 Executive Dashboard.

Revision ID: 0017_dashboard_snapshots
Revises: 0016_executive_report_exports
Create Date: 2026-08-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0017_dashboard_snapshots'
down_revision: Union[str, None] = '0016_executive_report_exports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums if postgres
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        snapshot_status_enum = postgresql.ENUM(
            'PENDING', 'BUILDING', 'READY', 'FAILED',
            name='snapshot_status_enum',
            create_type=False,
        )
        snapshot_status_enum.create(bind, checkfirst=True)

        snapshot_trigger_enum = postgresql.ENUM(
            'MANUAL', 'AUTOMATIC', 'DATASET_UPDATED', 'REPORT_GENERATED', 'INSIGHTS_UPDATED', 'FORECAST_UPDATED',
            name='snapshot_trigger_enum',
            create_type=False,
        )
        snapshot_trigger_enum.create(bind, checkfirst=True)

    # 2. Create dashboard_snapshots table
    op.create_table(
        'dashboard_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column(
            'status',
            sa.Enum('PENDING', 'BUILDING', 'READY', 'FAILED', name='snapshot_status_enum'),
            nullable=False,
            server_default='READY',
        ),
        sa.Column(
            'trigger',
            sa.Enum('MANUAL', 'AUTOMATIC', 'DATASET_UPDATED', 'REPORT_GENERATED', 'INSIGHTS_UPDATED', 'FORECAST_UPDATED', name='snapshot_trigger_enum'),
            nullable=False,
            server_default='MANUAL',
        ),
        sa.Column('snapshot_hash', sa.String(length=64), nullable=False, server_default=''),
        sa.Column('workspace_generation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('build_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('snapshot_size_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('artifact_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('snapshot_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('artifact_versions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('workspace_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_dashboard_snapshots_id', 'dashboard_snapshots', ['id'])
    op.create_index('ix_dashboard_snapshots_dataset_id', 'dashboard_snapshots', ['dataset_id'])
    op.create_index('ix_dashboard_snapshots_organization_id', 'dashboard_snapshots', ['organization_id'])
    op.create_index('ix_dashboard_snapshots_status', 'dashboard_snapshots', ['status'])
    op.create_index('ix_dashboard_snapshots_snapshot_hash', 'dashboard_snapshots', ['snapshot_hash'])
    op.create_index('ix_dashboard_snapshots_workspace_generation_id', 'dashboard_snapshots', ['workspace_generation_id'])
    op.create_index('ix_dashboard_snapshots_dataset_created', 'dashboard_snapshots', ['dataset_id', 'created_at'])
    op.create_index('ix_dashboard_snapshots_dataset_status', 'dashboard_snapshots', ['dataset_id', 'status'])
    op.create_index('ix_dashboard_snapshots_dataset_hash', 'dashboard_snapshots', ['dataset_id', 'snapshot_hash'])

    # 3. Create dashboard_view_events table
    op.create_table(
        'dashboard_view_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('section', sa.String(length=64), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_dashboard_view_events_id', 'dashboard_view_events', ['id'])
    op.create_index('ix_dashboard_view_events_dataset_id', 'dashboard_view_events', ['dataset_id'])
    op.create_index('ix_dashboard_view_events_section', 'dashboard_view_events', ['section'])
    op.create_index('ix_dashboard_view_events_dataset_viewed', 'dashboard_view_events', ['dataset_id', 'viewed_at'])


def downgrade() -> None:
    op.drop_table('dashboard_view_events')
    op.drop_table('dashboard_snapshots')

    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute('DROP TYPE IF EXISTS snapshot_trigger_enum')
        op.execute('DROP TYPE IF EXISTS snapshot_status_enum')
