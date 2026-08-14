"""Create diagnostic_findings table and add diagnostic tracking to datasets

Revision ID: 0004_diagnostic_findings
Revises: 0003_create_metrics_tables
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0004_diagnostic_findings'
down_revision: Union[str, None] = '0003_create_metrics_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create named PostgreSQL enum types
    diag_gen_status_enum = sa.Enum('PENDING', 'GENERATED', 'FAILED', name='diagnostic_generation_status')
    finding_sev_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='finding_severity')
    finding_type_enum = sa.Enum(
        'REVENUE_DROP',
        'REVENUE_CONCENTRATION',
        'HIGH_CANCELLATION_RATE',
        'LOW_COMPLETION_RATE',
        'CUSTOMER_CONCENTRATION',
        'REVIEW_SCORE_DECLINE',
        'DELIVERY_DELAY',
        'DATA_QUALITY_RISK',
        name='finding_type',
    )

    # 2. Add diagnostic tracking columns to datasets table with server_default for safe backfills
    op.add_column(
        'datasets',
        sa.Column('diagnostics_generation_status', diag_gen_status_enum, nullable=False, server_default='PENDING'),
    )
    op.add_column('datasets', sa.Column('diagnostics_generated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('datasets', sa.Column('diagnostics_generation_error', sa.Text(), nullable=True))
    op.create_index('ix_datasets_diagnostics_generation_status', 'datasets', ['diagnostics_generation_status'], unique=False)

    # 3. Create diagnostic_findings table
    op.create_table(
        'diagnostic_findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('finding_type', finding_type_enum, nullable=False),
        sa.Column('severity', finding_sev_enum, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('business_impact', sa.Text(), nullable=False),
        sa.Column('metric_key', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('supporting_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='ck_confidence_score_range'),
    )
    op.create_index('ix_diagnostic_findings_id', 'diagnostic_findings', ['id'], unique=False)
    op.create_index('ix_diagnostic_findings_dataset_id', 'diagnostic_findings', ['dataset_id'], unique=False)
    op.create_index('ix_diagnostic_findings_finding_type', 'diagnostic_findings', ['finding_type'], unique=False)
    op.create_index('ix_diagnostic_findings_severity', 'diagnostic_findings', ['severity'], unique=False)
    op.create_index('ix_diagnostic_findings_metric_key', 'diagnostic_findings', ['metric_key'], unique=False)
    op.create_index(
        'ix_diagnostic_findings_dataset_severity',
        'diagnostic_findings',
        ['dataset_id', 'severity'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_diagnostic_findings_dataset_severity', table_name='diagnostic_findings')
    op.drop_index('ix_diagnostic_findings_metric_key', table_name='diagnostic_findings')
    op.drop_index('ix_diagnostic_findings_severity', table_name='diagnostic_findings')
    op.drop_index('ix_diagnostic_findings_finding_type', table_name='diagnostic_findings')
    op.drop_index('ix_diagnostic_findings_dataset_id', table_name='diagnostic_findings')
    op.drop_index('ix_diagnostic_findings_id', table_name='diagnostic_findings')
    op.drop_table('diagnostic_findings')

    op.drop_index('ix_datasets_diagnostics_generation_status', table_name='datasets')
    op.drop_column('datasets', 'diagnostics_generation_error')
    op.drop_column('datasets', 'diagnostics_generated_at')
    op.drop_column('datasets', 'diagnostics_generation_status')

    finding_type_enum = sa.Enum(
        'REVENUE_DROP',
        'REVENUE_CONCENTRATION',
        'HIGH_CANCELLATION_RATE',
        'LOW_COMPLETION_RATE',
        'CUSTOMER_CONCENTRATION',
        'REVIEW_SCORE_DECLINE',
        'DELIVERY_DELAY',
        'DATA_QUALITY_RISK',
        name='finding_type',
    )
    finding_type_enum.drop(op.get_bind(), checkfirst=True)

    finding_sev_enum = sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='finding_severity')
    finding_sev_enum.drop(op.get_bind(), checkfirst=True)

    diag_gen_status_enum = sa.Enum('PENDING', 'GENERATED', 'FAILED', name='diagnostic_generation_status')
    diag_gen_status_enum.drop(op.get_bind(), checkfirst=True)
