"""Create metric_definitions and dataset_metrics tables with KPI tracking

Revision ID: 0003_create_metrics_tables
Revises: 0002_create_datasets_tables
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0003_create_metrics_tables'
down_revision: Union[str, None] = '0002_create_datasets_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create enum types
    metrics_gen_status_enum = sa.Enum('PENDING', 'GENERATED', 'FAILED', name='metrics_generation_status')
    metric_category_enum = sa.Enum('REVENUE', 'ORDERS', 'CUSTOMERS', 'REVIEWS', 'DELIVERY', 'QUALITY', name='metric_category')

    # 2. Add KPI tracking columns to datasets table
    op.add_column('datasets', sa.Column('metrics_generation_status', metrics_gen_status_enum, nullable=False, server_default='PENDING'))
    op.add_column('datasets', sa.Column('metrics_generated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('datasets', sa.Column('metrics_generation_error', sa.Text(), nullable=True))
    op.create_index('ix_datasets_metrics_generation_status', 'datasets', ['metrics_generation_status'], unique=False)

    # 3. Create metric_definitions table
    op.create_table(
        'metric_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('metric_key', sa.String(length=128), nullable=False),
        sa.Column('metric_category', metric_category_enum, nullable=False),
        sa.Column('formula', sa.String(length=512), nullable=True),
        sa.Column('required_field', sa.String(length=128), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_metric_definitions_id', 'metric_definitions', ['id'], unique=False)
    op.create_index('ix_metric_definitions_metric_key', 'metric_definitions', ['metric_key'], unique=True)
    op.create_index('ix_metric_definitions_metric_category', 'metric_definitions', ['metric_category'], unique=False)

    # 4. Create dataset_metrics table
    op.create_table(
        'dataset_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_definition_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('metric_definitions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('generated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('metric_key', sa.String(length=128), nullable=False),
        sa.Column('metric_name', sa.String(length=255), nullable=False),
        sa.Column('metric_category', metric_category_enum, nullable=False),
        sa.Column('metric_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_dataset_metrics_id', 'dataset_metrics', ['id'], unique=False)
    op.create_index('ix_dataset_metrics_dataset_id', 'dataset_metrics', ['dataset_id'], unique=False)
    op.create_index('ix_dataset_metrics_metric_definition_id', 'dataset_metrics', ['metric_definition_id'], unique=False)
    op.create_index('ix_dataset_metrics_generated_by', 'dataset_metrics', ['generated_by'], unique=False)
    op.create_index('ix_dataset_metrics_metric_key', 'dataset_metrics', ['metric_key'], unique=False)
    op.create_index('ix_dataset_metrics_metric_category', 'dataset_metrics', ['metric_category'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_dataset_metrics_metric_category', table_name='dataset_metrics')
    op.drop_index('ix_dataset_metrics_metric_key', table_name='dataset_metrics')
    op.drop_index('ix_dataset_metrics_generated_by', table_name='dataset_metrics')
    op.drop_index('ix_dataset_metrics_metric_definition_id', table_name='dataset_metrics')
    op.drop_index('ix_dataset_metrics_dataset_id', table_name='dataset_metrics')
    op.drop_index('ix_dataset_metrics_id', table_name='dataset_metrics')
    op.drop_table('dataset_metrics')

    op.drop_index('ix_metric_definitions_metric_category', table_name='metric_definitions')
    op.drop_index('ix_metric_definitions_metric_key', table_name='metric_definitions')
    op.drop_index('ix_metric_definitions_id', table_name='metric_definitions')
    op.drop_table('metric_definitions')

    op.drop_index('ix_datasets_metrics_generation_status', table_name='datasets')
    op.drop_column('datasets', 'metrics_generation_error')
    op.drop_column('datasets', 'metrics_generated_at')
    op.drop_column('datasets', 'metrics_generation_status')

    metric_category_enum = sa.Enum('REVENUE', 'ORDERS', 'CUSTOMERS', 'REVIEWS', 'DELIVERY', 'QUALITY', name='metric_category')
    metric_category_enum.drop(op.get_bind(), checkfirst=True)

    metrics_gen_status_enum = sa.Enum('PENDING', 'GENERATED', 'FAILED', name='metrics_generation_status')
    metrics_gen_status_enum.drop(op.get_bind(), checkfirst=True)
