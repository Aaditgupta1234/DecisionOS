"""Create multi-tenant organizations and memberships tables with dataset backfill

Revision ID: 0012_multi_tenant_saas
Revises: 0011_forecasting
Create Date: 2026-08-14

"""
import uuid
from typing import Sequence, Union
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0012_multi_tenant_saas'
down_revision: Union[str, None] = '0011_forecasting'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # 1. Create org_role enum
    org_role_enum = sa.Enum('OWNER', 'ADMIN', 'ANALYST', 'VIEWER', name='org_role')
    org_role_enum.create(bind, checkfirst=True)

    # 2. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), unique=True, nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('logo_url', sa.String(length=1024), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_organizations_id', 'organizations', ['id'], unique=False)
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)
    op.create_index('ix_organizations_created_by', 'organizations', ['created_by'], unique=False)
    op.create_index('ix_organizations_is_active', 'organizations', ['is_active'], unique=False)

    # 3. Create organization_members table
    op.create_table(
        'organization_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'ANALYST', 'VIEWER', name='org_role'), nullable=False, server_default='ANALYST'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_org_member_user'),
    )
    op.create_index('ix_organization_members_id', 'organization_members', ['id'], unique=False)
    op.create_index('ix_organization_members_organization_id', 'organization_members', ['organization_id'], unique=False)
    op.create_index('ix_organization_members_user_id', 'organization_members', ['user_id'], unique=False)
    op.create_index('ix_organization_members_role', 'organization_members', ['role'], unique=False)

    # 4. Add organization_id column to datasets
    op.add_column(
        'datasets',
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
    )
    op.create_index('ix_datasets_organization_id', 'datasets', ['organization_id'], unique=False)

    # 5. Data Migration / Backfill
    # Auto-provision Personal Organization for any existing users
    try:
        users = bind.execute(sa.text("SELECT id, email, full_name FROM users")).fetchall()
        now = datetime.now(timezone.utc)
        for u in users:
            user_id = u[0]
            email = u[1]
            org_id = uuid.uuid4()
            slug = f"org-{str(user_id)[:8]}"
            name = f"{email.split('@')[0]}'s Workspace"

            bind.execute(
                sa.text(
                    "INSERT INTO organizations (id, name, slug, created_by, is_active, created_at, updated_at) "
                    "VALUES (:id, :name, :slug, :created_by, :is_active, :created_at, :updated_at)"
                ),
                {
                    "id": str(org_id),
                    "name": name,
                    "slug": slug,
                    "created_by": str(user_id),
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )

            bind.execute(
                sa.text(
                    "INSERT INTO organization_members (id, organization_id, user_id, role, created_at, updated_at) "
                    "VALUES (:id, :org_id, :user_id, :role, :created_at, :updated_at)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "org_id": str(org_id),
                    "user_id": str(user_id),
                    "role": "OWNER",
                    "created_at": now,
                    "updated_at": now,
                },
            )

            # Associate user's datasets with this organization
            bind.execute(
                sa.text(
                    "UPDATE datasets SET organization_id = :org_id WHERE uploaded_by = :user_id AND organization_id IS NULL"
                ),
                {"org_id": str(org_id), "user_id": str(user_id)},
            )
    except Exception:
        # If running in SQLite in-memory or empty table, continue safely
        pass


def downgrade() -> None:
    op.drop_index('ix_datasets_organization_id', table_name='datasets')
    op.drop_column('datasets', 'organization_id')
    op.drop_table('organization_members')
    op.drop_table('organizations')
    bind = op.get_bind()
    org_role_enum = sa.Enum('OWNER', 'ADMIN', 'ANALYST', 'VIEWER', name='org_role')
    org_role_enum.drop(bind, checkfirst=True)
