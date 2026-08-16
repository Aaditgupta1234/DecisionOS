"""Create portfolio_snapshots and workspace_benchmarks tables for Phase 11.0.

Revision ID: 0024_portfolio_tables
Revises: 0023_organization_settings
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0024_portfolio_tables'
down_revision: Union[str, None] = '0023_organization_settings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create portfolio_snapshots table
    op.create_table(
        'portfolio_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('snapshot_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('workspace_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('analyzed_workspace_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_health_score', sa.Float(), nullable=True),
        sa.Column('median_health_score', sa.Float(), nullable=True),
        sa.Column('best_workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='SET NULL'), nullable=True),
        sa.Column('best_workspace_score', sa.Float(), nullable=True),
        sa.Column('worst_workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='SET NULL'), nullable=True),
        sa.Column('worst_workspace_score', sa.Float(), nullable=True),
        sa.Column('portfolio_status', sa.String(length=50), nullable=False, server_default='INSUFFICIENT_DATA'),
        sa.Column('summary_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('portfolio_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_portfolio_snapshots_id', 'portfolio_snapshots', ['id'], unique=False)
    op.create_index('ix_portfolio_snapshots_organization_id', 'portfolio_snapshots', ['organization_id'], unique=False)
    op.create_index('ix_portfolio_snapshots_snapshot_date', 'portfolio_snapshots', ['snapshot_date'], unique=False)
    op.create_index('ix_portfolio_snapshots_portfolio_status', 'portfolio_snapshots', ['portfolio_status'], unique=False)
    op.create_index('ix_portfolio_snapshots_org_date', 'portfolio_snapshots', ['organization_id', 'snapshot_date'], unique=False)
    op.create_index('ix_portfolio_snapshots_org_status', 'portfolio_snapshots', ['organization_id', 'portfolio_status'], unique=False)

    # 2. Create workspace_benchmarks table
    op.create_table(
        'workspace_benchmarks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('portfolio_snapshot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('portfolio_snapshots.id', ondelete='SET NULL'), nullable=True),
        sa.Column('benchmark_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('rank', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_ranked', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('percentile', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('percentile_rank', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('benchmark_tier', sa.String(length=50), nullable=False, server_default='TOP'),
        sa.Column('benchmark_available', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('kpi_score', sa.Float(), nullable=True),
        sa.Column('finding_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_finding_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('recommendation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('forecast_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('organization_id', 'workspace_id', 'benchmark_date', name='uq_workspace_benchmarks_org_ws_date'),
    )

    op.create_index('ix_workspace_benchmarks_id', 'workspace_benchmarks', ['id'], unique=False)
    op.create_index('ix_workspace_benchmarks_organization_id', 'workspace_benchmarks', ['organization_id'], unique=False)
    op.create_index('ix_workspace_benchmarks_workspace_id', 'workspace_benchmarks', ['workspace_id'], unique=False)
    op.create_index('ix_workspace_benchmarks_snapshot_id', 'workspace_benchmarks', ['portfolio_snapshot_id'], unique=False)
    op.create_index('ix_workspace_benchmarks_benchmark_date', 'workspace_benchmarks', ['benchmark_date'], unique=False)
    op.create_index('ix_workspace_benchmarks_org_ws_date', 'workspace_benchmarks', ['organization_id', 'workspace_id', 'benchmark_date'], unique=False)
    op.create_index('ix_workspace_benchmarks_org_rank', 'workspace_benchmarks', ['organization_id', 'rank'], unique=False)


def downgrade() -> None:
    op.drop_table('workspace_benchmarks')
    op.drop_table('portfolio_snapshots')
