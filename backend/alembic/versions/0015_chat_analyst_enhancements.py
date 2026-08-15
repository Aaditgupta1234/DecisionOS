"""Enhance chat_sessions and chat_messages tables for Phase 9.4 AI Chat Analyst

Revision ID: 0015_chat_analyst_enhancements
Revises: 0014_executive_insight_reports
Create Date: 2026-08-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0015_chat_analyst_enhancements'
down_revision: Union[str, None] = '0014_executive_insight_reports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enhance chat_sessions
    op.add_column('chat_sessions', sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True))
    op.add_column('chat_sessions', sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
    op.add_column('chat_sessions', sa.Column('provider', sa.String(length=64), nullable=False, server_default='ollama'))
    op.add_column('chat_sessions', sa.Column('model', sa.String(length=128), nullable=False, server_default='qwen2.5:1.5b'))
    op.add_column('chat_sessions', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.create_index('ix_chat_sessions_org_id', 'chat_sessions', ['organization_id'], unique=False)
    op.create_index('ix_chat_sessions_created_by', 'chat_sessions', ['created_by'], unique=False)

    # 2. Enhance chat_messages
    op.add_column('chat_messages', sa.Column('response_type', sa.String(length=32), nullable=False, server_default='GENERAL'))
    op.add_column('chat_messages', sa.Column('response_time_ms', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('chat_messages', sa.Column('context_tokens', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('chat_messages', sa.Column('prompt_version', sa.String(length=32), nullable=False, server_default='1.0'))
    op.add_column('chat_messages', sa.Column('source_finding_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('chat_messages', sa.Column('source_root_cause_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('chat_messages', sa.Column('source_recommendation_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('chat_messages', sa.Column('source_forecast_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('chat_messages', sa.Column('source_scenario_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column('chat_messages', sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")))


def downgrade() -> None:
    # Downgrade chat_messages
    op.drop_column('chat_messages', 'citations')
    op.drop_column('chat_messages', 'source_scenario_ids')
    op.drop_column('chat_messages', 'source_forecast_ids')
    op.drop_column('chat_messages', 'source_recommendation_ids')
    op.drop_column('chat_messages', 'source_root_cause_ids')
    op.drop_column('chat_messages', 'source_finding_ids')
    op.drop_column('chat_messages', 'prompt_version')
    op.drop_column('chat_messages', 'context_tokens')
    op.drop_column('chat_messages', 'response_time_ms')
    op.drop_column('chat_messages', 'response_type')

    # Downgrade chat_sessions
    op.drop_index('ix_chat_sessions_created_by', table_name='chat_sessions')
    op.drop_index('ix_chat_sessions_org_id', table_name='chat_sessions')
    op.drop_column('chat_sessions', 'is_archived')
    op.drop_column('chat_sessions', 'model')
    op.drop_column('chat_sessions', 'provider')
    op.drop_column('chat_sessions', 'created_by')
    op.drop_column('chat_sessions', 'organization_id')
