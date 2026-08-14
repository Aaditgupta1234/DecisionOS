"""Create strategy_plans table

Revision ID: 0009_strategy_plans
Revises: 0008_ai_chat
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0009_strategy_plans'
down_revision: Union[str, None] = '0008_ai_chat'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create named PostgreSQL enum type
    status_enum = sa.Enum('DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED', name='strategy_plan_status')
    status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create strategy_plans table
    op.create_table(
        'strategy_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'dataset_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('datasets.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('plan_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('recommendation_snapshot_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('prompt_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('model_provider', sa.String(length=64), nullable=False, server_default='openai'),
        sa.Column('model_name', sa.String(length=128), nullable=False, server_default='gpt-4o-mini'),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Strategic Execution Plan'),
        sa.Column(
            'objective',
            sa.Text(),
            nullable=False,
            server_default='Operationalize recommended business interventions into time-phased execution roadmap.',
        ),
        sa.Column(
            'status',
            sa.Enum('DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED', name='strategy_plan_status'),
            nullable=False,
            server_default='DRAFT',
        ),
        sa.Column('executive_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column(
            'strategic_priorities',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'action_items',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'milestones',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'success_criteria',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'source_recommendation_ids',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'metadata_info',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'generated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
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

    op.create_index('ix_strategy_plans_id', 'strategy_plans', ['id'], unique=False)
    op.create_index('ix_strategy_plans_dataset_id', 'strategy_plans', ['dataset_id'], unique=False)
    op.create_index(
        'ix_strategy_plans_dataset_created',
        'strategy_plans',
        ['dataset_id', 'created_at'],
        unique=False,
    )
    op.create_index(
        'ix_strategy_plans_dataset_status',
        'strategy_plans',
        ['dataset_id', 'status'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_strategy_plans_dataset_status', table_name='strategy_plans')
    op.drop_index('ix_strategy_plans_dataset_created', table_name='strategy_plans')
    op.drop_index('ix_strategy_plans_dataset_id', table_name='strategy_plans')
    op.drop_index('ix_strategy_plans_id', table_name='strategy_plans')
    op.drop_table('strategy_plans')

    # Drop enum
    sa.Enum('DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED', name='strategy_plan_status').drop(op.get_bind(), checkfirst=True)
