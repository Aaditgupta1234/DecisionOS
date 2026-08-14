"""Create forecasts table

Revision ID: 0011_forecasting
Revises: 0010_scenario_simulation
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0011_forecasting'
down_revision: Union[str, None] = '0010_scenario_simulation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create named PostgreSQL enum types
    status_enum = sa.Enum('COMPLETED', 'FAILED', 'ARCHIVED', name='forecast_status')
    status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create forecasts table
    op.create_table(
        'forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'dataset_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('datasets.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('forecast_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('metric_key', sa.String(length=128), nullable=False),
        sa.Column('horizon', sa.String(length=32), nullable=False),
        sa.Column('frequency', sa.String(length=32), nullable=False),
        sa.Column('model_name', sa.String(length=64), nullable=False, server_default='NAIVE'),
        sa.Column('model_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('confidence_level', sa.Float(), nullable=False, server_default='0.80'),
        sa.Column(
            'status',
            sa.Enum('COMPLETED', 'FAILED', 'ARCHIVED', name='forecast_status'),
            nullable=False,
            server_default='COMPLETED',
        ),
        sa.Column('historical_observation_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column(
            'forecast_points',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'model_metrics',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column('trend', sa.String(length=32), nullable=False, server_default='STABLE'),
        sa.Column(
            'limitations',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'baseline_snapshot',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'metadata_info',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    op.create_index('ix_forecasts_id', 'forecasts', ['id'], unique=False)
    op.create_index('ix_forecasts_dataset_id', 'forecasts', ['dataset_id'], unique=False)
    op.create_index('ix_forecasts_metric_key', 'forecasts', ['metric_key'], unique=False)
    op.create_index('ix_forecasts_status', 'forecasts', ['status'], unique=False)
    op.create_index(
        'ix_forecasts_dataset_created',
        'forecasts',
        ['dataset_id', 'created_at'],
        unique=False,
    )
    op.create_index(
        'ix_forecasts_dataset_metric',
        'forecasts',
        ['dataset_id', 'metric_key'],
        unique=False,
    )
    op.create_index(
        'ix_forecasts_dataset_metric_created',
        'forecasts',
        ['dataset_id', 'metric_key', 'created_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_forecasts_dataset_metric_created', table_name='forecasts')
    op.drop_index('ix_forecasts_dataset_metric', table_name='forecasts')
    op.drop_index('ix_forecasts_dataset_created', table_name='forecasts')
    op.drop_index('ix_forecasts_status', table_name='forecasts')
    op.drop_index('ix_forecasts_metric_key', table_name='forecasts')
    op.drop_index('ix_forecasts_dataset_id', table_name='forecasts')
    op.drop_index('ix_forecasts_id', table_name='forecasts')
    op.drop_table('forecasts')

    # Drop enums
    sa.Enum('COMPLETED', 'FAILED', 'ARCHIVED', name='forecast_status').drop(op.get_bind(), checkfirst=True)
