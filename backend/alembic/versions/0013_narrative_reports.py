"""Create narrative_reports table for Phase 9.2 AI Narrative Engine

Revision ID: 0013_narrative_reports
Revises: 0012_multi_tenant_saas
Create Date: 2026-08-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0013_narrative_reports'
down_revision: Union[str, None] = '0012_multi_tenant_saas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'narrative_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prompt_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('provider', sa.String(length=64), nullable=False, server_default='ollama'),
        sa.Column('model', sa.String(length=128), nullable=False, server_default='qwen2.5:1.5b'),
        sa.Column('narrative_confidence', sa.Float(), nullable=False, server_default='0.85'),
        sa.Column('generation_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('validation_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_latency_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('fallback_triggered', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_fallback', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('executive_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('kpi_narrative', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('root_cause_narrative', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('recommendation_narrative', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('forecast_narrative', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('scenario_narrative', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('full_package_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_narrative_reports_id', 'narrative_reports', ['id'], unique=False)
    op.create_index('ix_narrative_reports_dataset_id', 'narrative_reports', ['dataset_id'], unique=False)
    op.create_index('ix_narrative_reports_dataset_created', 'narrative_reports', ['dataset_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_narrative_reports_dataset_created', table_name='narrative_reports')
    op.drop_index('ix_narrative_reports_dataset_id', table_name='narrative_reports')
    op.drop_index('ix_narrative_reports_id', table_name='narrative_reports')
    op.drop_table('narrative_reports')
