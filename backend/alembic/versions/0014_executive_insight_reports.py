"""Create executive_insight_reports table for Phase 9.3 Executive Insight Generator

Revision ID: 0014_executive_insight_reports
Revises: 0013_narrative_reports
Create Date: 2026-08-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0014_executive_insight_reports'
down_revision: Union[str, None] = '0013_narrative_reports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'executive_insight_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('prompt_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('insight_schema_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('provider', sa.String(length=64), nullable=False, server_default='ollama'),
        sa.Column('model', sa.String(length=128), nullable=False, server_default='qwen2.5:1.5b'),
        sa.Column('narrative_confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('insight_confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('generation_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('validation_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fallback_triggered', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_fallback', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('executive_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('top_risks', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('top_opportunities', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('priority_actions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('strategic_themes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('executive_alerts', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('board_commentary', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('full_package_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_executive_insight_reports_id', 'executive_insight_reports', ['id'], unique=False)
    op.create_index('ix_executive_insight_reports_dataset_id', 'executive_insight_reports', ['dataset_id'], unique=False)
    op.create_index('ix_executive_insight_reports_org_id', 'executive_insight_reports', ['organization_id'], unique=False)
    op.create_index('ix_executive_insight_reports_dataset_created', 'executive_insight_reports', ['dataset_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_executive_insight_reports_dataset_created', table_name='executive_insight_reports')
    op.drop_index('ix_executive_insight_reports_org_id', table_name='executive_insight_reports')
    op.drop_index('ix_executive_insight_reports_dataset_id', table_name='executive_insight_reports')
    op.drop_index('ix_executive_insight_reports_id', table_name='executive_insight_reports')
    op.drop_table('executive_insight_reports')
