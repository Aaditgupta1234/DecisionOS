"""Create datasets and dataset_columns tables with JSONB and lifecycle tracking

Revision ID: 0002_create_datasets_tables
Revises: 0001_create_users_table
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0002_create_datasets_tables'
down_revision: Union[str, None] = '0001_create_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dataset_status enum type
    dataset_status_enum = sa.Enum('UPLOADED', 'PROCESSING', 'READY', 'FAILED', name='dataset_status')
    
    # 1. Create datasets table
    op.create_table(
        'datasets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('record_count', sa.Integer(), nullable=True),
        sa.Column('column_count', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', dataset_status_enum, nullable=False, server_default='UPLOADED'),
        sa.Column('validation_errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preview_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_datasets_id', 'datasets', ['id'], unique=False)
    op.create_index('ix_datasets_stored_filename', 'datasets', ['stored_filename'], unique=True)
    op.create_index('ix_datasets_status', 'datasets', ['status'], unique=False)
    op.create_index('ix_datasets_uploaded_by', 'datasets', ['uploaded_by'], unique=False)
    op.create_index('ix_datasets_is_deleted', 'datasets', ['is_deleted'], unique=False)

    # 2. Create dataset_columns table
    op.create_table(
        'dataset_columns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
        sa.Column('normalized_name', sa.String(length=255), nullable=False),
        sa.Column('mapped_field', sa.String(length=255), nullable=True),
        sa.Column('mapping_confidence', sa.Float(), nullable=True),
        sa.Column('data_type', sa.String(length=64), nullable=True),
        sa.Column('sample_value', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_dataset_columns_id', 'dataset_columns', ['id'], unique=False)
    op.create_index('ix_dataset_columns_dataset_id', 'dataset_columns', ['dataset_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_dataset_columns_dataset_id', table_name='dataset_columns')
    op.drop_index('ix_dataset_columns_id', table_name='dataset_columns')
    op.drop_table('dataset_columns')

    op.drop_index('ix_datasets_is_deleted', table_name='datasets')
    op.drop_index('ix_datasets_uploaded_by', table_name='datasets')
    op.drop_index('ix_datasets_status', table_name='datasets')
    op.drop_index('ix_datasets_stored_filename', table_name='datasets')
    op.drop_index('ix_datasets_id', table_name='datasets')
    op.drop_table('datasets')

    dataset_status_enum = sa.Enum('UPLOADED', 'PROCESSING', 'READY', 'FAILED', name='dataset_status')
    dataset_status_enum.drop(op.get_bind(), checkfirst=True)
