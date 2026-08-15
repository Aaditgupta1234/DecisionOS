"""Create report_exports and report_templates tables for Phase 9.5 Reporting Engine

Revision ID: 0016_executive_report_exports
Revises: 0015_chat_analyst_enhancements
Create Date: 2026-08-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0016_executive_report_exports'
down_revision: Union[str, None] = '0015_chat_analyst_enhancements'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums if postgres
    report_type_enum = postgresql.ENUM(
        'EXECUTIVE_SUMMARY',
        'KPI_PERFORMANCE',
        'DIAGNOSTIC',
        'ROOT_CAUSE',
        'RECOMMENDATION_ROADMAP',
        'FORECAST',
        'SCENARIO_PLANNING',
        'EXECUTIVE_INTELLIGENCE',
        'FULL_BOARD_PACKAGE',
        name='report_type_enum',
        create_type=False,
    )
    export_format_enum = postgresql.ENUM('PDF', 'HTML', name='export_format_enum', create_type=False)
    report_status_enum = postgresql.ENUM('PENDING', 'COMPLETED', 'FAILED', name='report_status_enum', create_type=False)

    # 2. Create report_templates table
    op.create_table(
        'report_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('report_type', sa.Enum('EXECUTIVE_SUMMARY', 'KPI_PERFORMANCE', 'DIAGNOSTIC', 'ROOT_CAUSE', 'RECOMMENDATION_ROADMAP', 'FORECAST', 'SCENARIO_PLANNING', 'EXECUTIVE_INTELLIGENCE', 'FULL_BOARD_PACKAGE', name='report_type_enum'), nullable=False),
        sa.Column('version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_report_templates_type_version', 'report_templates', ['report_type', 'version'], unique=False)
    op.create_index('ix_report_templates_org_id', 'report_templates', ['organization_id'], unique=False)

    # 3. Create report_exports table
    op.create_table(
        'report_exports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True),
        sa.Column('report_type', sa.Enum('EXECUTIVE_SUMMARY', 'KPI_PERFORMANCE', 'DIAGNOSTIC', 'ROOT_CAUSE', 'RECOMMENDATION_ROADMAP', 'FORECAST', 'SCENARIO_PLANNING', 'EXECUTIVE_INTELLIGENCE', 'FULL_BOARD_PACKAGE', name='report_type_enum'), nullable=False),
        sa.Column('export_format', sa.Enum('PDF', 'HTML', name='export_format_enum'), nullable=False, server_default='PDF'),
        sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='report_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('template_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('prompt_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('generation_time_ms', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('storage_path', sa.String(length=1024), nullable=False, server_default=''),
        sa.Column('report_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('ix_report_exports_dataset_created', 'report_exports', ['dataset_id', 'created_at'], unique=False)
    op.create_index('ix_report_exports_org_id', 'report_exports', ['organization_id'], unique=False)
    op.create_index('ix_report_exports_status', 'report_exports', ['status'], unique=False)
    op.create_index('ix_report_exports_report_type', 'report_exports', ['report_type'], unique=False)


def downgrade() -> None:
    op.drop_table('report_exports')
    op.drop_table('report_templates')
    op.execute('DROP TYPE IF EXISTS report_status_enum')
    op.execute('DROP TYPE IF EXISTS export_format_enum')
    op.execute('DROP TYPE IF EXISTS report_type_enum')
