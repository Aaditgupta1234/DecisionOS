"""Create organization_settings table for Phase 10.6 Platform Administration & Governance.

Revision ID: 0023_organization_settings
Revises: 0022_governance_policies
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0023_organization_settings'
down_revision: Union[str, None] = '0022_governance_policies'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organization_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'),
        sa.Column('notification_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('dashboard_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('monitoring_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('organization_id', name='uq_organization_settings_org_id'),
    )

    op.create_index('ix_organization_settings_id', 'organization_settings', ['id'], unique=False)
    op.create_index('ix_organization_settings_organization_id', 'organization_settings', ['organization_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_organization_settings_organization_id', table_name='organization_settings')
    op.drop_index('ix_organization_settings_id', table_name='organization_settings')
    op.drop_table('organization_settings')
