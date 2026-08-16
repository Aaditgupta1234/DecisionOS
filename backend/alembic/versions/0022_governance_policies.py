"""Create governance_policies table for Phase 10.6 Platform Administration & Governance.

Revision ID: 0022_governance_policies
Revises: 0021_schedules
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0022_governance_policies'
down_revision: Union[str, None] = '0021_schedules'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'governance_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('policy_type', sa.String(length=50), nullable=False),
        sa.Column('policy_name', sa.String(length=100), nullable=False),
        sa.Column('policy_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE'),
        sa.Column('policy_version', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('effective_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('updated_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_index('ix_governance_policies_id', 'governance_policies', ['id'], unique=False)
    op.create_index('ix_governance_policies_organization_id', 'governance_policies', ['organization_id'], unique=False)
    op.create_index('ix_governance_policies_policy_type', 'governance_policies', ['policy_type'], unique=False)
    op.create_index('ix_governance_policies_status', 'governance_policies', ['status'], unique=False)
    op.create_index('ix_governance_policies_effective_from', 'governance_policies', ['effective_from'], unique=False)
    op.create_index('ix_governance_policies_created_at', 'governance_policies', ['created_at'], unique=False)
    op.create_index('ix_governance_policies_org_type', 'governance_policies', ['organization_id', 'policy_type'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_governance_policies_org_type', table_name='governance_policies')
    op.drop_index('ix_governance_policies_created_at', table_name='governance_policies')
    op.drop_index('ix_governance_policies_effective_from', table_name='governance_policies')
    op.drop_index('ix_governance_policies_status', table_name='governance_policies')
    op.drop_index('ix_governance_policies_policy_type', table_name='governance_policies')
    op.drop_index('ix_governance_policies_organization_id', table_name='governance_policies')
    op.drop_index('ix_governance_policies_id', table_name='governance_policies')
    op.drop_table('governance_policies')
