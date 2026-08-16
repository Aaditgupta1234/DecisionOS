"""Create audit_records table for Phase 10.3 Audit Center.

Revision ID: 0020_audit_records
Revises: 0019_notifications
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0020_audit_records'
down_revision: Union[str, None] = '0019_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create audit_records table (append-only, immutable)
    op.create_table(
        'audit_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False, server_default='SYSTEM'),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='INFO'),
        sa.Column('entity_type', sa.String(length=50), nullable=False, server_default='system'),
        sa.Column('entity_id', sa.String(length=100), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{\"source_type\": \"system\", \"source_id\": null, \"details\": {}}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 2. Create indexes
    op.create_index('ix_audit_records_id', 'audit_records', ['id'], unique=False)
    op.create_index('ix_audit_records_organization_id', 'audit_records', ['organization_id'], unique=False)
    op.create_index('ix_audit_records_actor_user_id', 'audit_records', ['actor_user_id'], unique=False)
    op.create_index('ix_audit_records_event_type', 'audit_records', ['event_type'], unique=False)
    op.create_index('ix_audit_records_severity', 'audit_records', ['severity'], unique=False)
    op.create_index('ix_audit_records_entity_type', 'audit_records', ['entity_type'], unique=False)
    op.create_index('ix_audit_records_entity_id', 'audit_records', ['entity_id'], unique=False)
    op.create_index('ix_audit_records_created_at', 'audit_records', ['created_at'], unique=False)
    op.create_index('ix_audit_records_org_created', 'audit_records', ['organization_id', 'created_at'], unique=False)
    op.create_index('ix_audit_records_org_event_created', 'audit_records', ['organization_id', 'event_type', 'created_at'], unique=False)
    op.create_index('ix_audit_records_org_entity', 'audit_records', ['organization_id', 'entity_type', 'entity_id'], unique=False)
    op.create_index('ix_audit_records_org_actor_created', 'audit_records', ['organization_id', 'actor_user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_audit_records_org_actor_created', table_name='audit_records')
    op.drop_index('ix_audit_records_org_entity', table_name='audit_records')
    op.drop_index('ix_audit_records_org_event_created', table_name='audit_records')
    op.drop_index('ix_audit_records_org_created', table_name='audit_records')
    op.drop_index('ix_audit_records_created_at', table_name='audit_records')
    op.drop_index('ix_audit_records_entity_id', table_name='audit_records')
    op.drop_index('ix_audit_records_entity_type', table_name='audit_records')
    op.drop_index('ix_audit_records_severity', table_name='audit_records')
    op.drop_index('ix_audit_records_event_type', table_name='audit_records')
    op.drop_index('ix_audit_records_actor_user_id', table_name='audit_records')
    op.drop_index('ix_audit_records_organization_id', table_name='audit_records')
    op.drop_index('ix_audit_records_id', table_name='audit_records')
    op.drop_table('audit_records')
