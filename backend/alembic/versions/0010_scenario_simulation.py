"""Create scenarios table

Revision ID: 0010_scenario_simulation
Revises: 0009_strategy_plans
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0010_scenario_simulation'
down_revision: Union[str, None] = '0009_strategy_plans'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create named PostgreSQL enum types
    status_enum = sa.Enum('DRAFT', 'COMPLETED', 'ARCHIVED', name='scenario_status')
    status_enum.create(op.get_bind(), checkfirst=True)

    adj_enum = sa.Enum('RELATIVE_PERCENT', 'PERCENTAGE_POINTS', 'ABSOLUTE_VALUE', name='scenario_adjustment_type')
    adj_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'dataset_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('datasets.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('scenario_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column(
            'status',
            sa.Enum('DRAFT', 'COMPLETED', 'ARCHIVED', name='scenario_status'),
            nullable=False,
            server_default='COMPLETED',
        ),
        sa.Column(
            'assumptions',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'baseline_snapshot',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'projected_metrics',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'projected_findings',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'projected_risks',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'projected_opportunities',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'projected_health',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'limitations',
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

    op.create_index('ix_scenarios_id', 'scenarios', ['id'], unique=False)
    op.create_index('ix_scenarios_dataset_id', 'scenarios', ['dataset_id'], unique=False)
    op.create_index(
        'ix_scenarios_dataset_created',
        'scenarios',
        ['dataset_id', 'created_at'],
        unique=False,
    )
    op.create_index(
        'ix_scenarios_dataset_status',
        'scenarios',
        ['dataset_id', 'status'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_scenarios_dataset_status', table_name='scenarios')
    op.drop_index('ix_scenarios_dataset_created', table_name='scenarios')
    op.drop_index('ix_scenarios_dataset_id', table_name='scenarios')
    op.drop_index('ix_scenarios_id', table_name='scenarios')
    op.drop_table('scenarios')

    # Drop enums
    sa.Enum('RELATIVE_PERCENT', 'PERCENTAGE_POINTS', 'ABSOLUTE_VALUE', name='scenario_adjustment_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum('DRAFT', 'COMPLETED', 'ARCHIVED', name='scenario_status').drop(op.get_bind(), checkfirst=True)
