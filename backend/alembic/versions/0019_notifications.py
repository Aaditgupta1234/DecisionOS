"""Create notifications table for Phase 10.2 Notification Framework.

Revision ID: 0019_notifications
Revises: 0018_background_jobs
Create Date: 2026-08-16

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0019_notifications'
down_revision: Union[str, None] = '0018_background_jobs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recipient_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('notification_type', sa.String(length=50), nullable=False, server_default='SYSTEM'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='UNREAD'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{\"source_type\": \"system\", \"source_id\": null, \"details\": {}}'::jsonb")),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 2. Create indexes
    op.create_index('ix_notifications_id', 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_organization_id', 'notifications', ['organization_id'], unique=False)
    op.create_index('ix_notifications_recipient_user_id', 'notifications', ['recipient_user_id'], unique=False)
    op.create_index('ix_notifications_notification_type', 'notifications', ['notification_type'], unique=False)
    op.create_index('ix_notifications_status', 'notifications', ['status'], unique=False)
    op.create_index('ix_notifications_org_status', 'notifications', ['organization_id', 'status'], unique=False)
    op.create_index('ix_notifications_recipient_status', 'notifications', ['recipient_user_id', 'status'], unique=False)
    op.create_index('ix_notifications_org_user_status_created', 'notifications', ['organization_id', 'recipient_user_id', 'status', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_notifications_org_user_status_created', table_name='notifications')
    op.drop_index('ix_notifications_recipient_status', table_name='notifications')
    op.drop_index('ix_notifications_org_status', table_name='notifications')
    op.drop_index('ix_notifications_status', table_name='notifications')
    op.drop_index('ix_notifications_notification_type', table_name='notifications')
    op.drop_index('ix_notifications_recipient_user_id', table_name='notifications')
    op.drop_index('ix_notifications_organization_id', table_name='notifications')
    op.drop_index('ix_notifications_id', table_name='notifications')
    op.drop_table('notifications')
