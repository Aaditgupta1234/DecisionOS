"""Create ai_insights table

Revision ID: 0007_ai_insights
Revises: 0006_recommendations
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0007_ai_insights'
down_revision: Union[str, None] = '0006_recommendations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ai_insights table
    op.create_table(
        'ai_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            'dataset_id',
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey('datasets.id', ondelete='CASCADE'),
            nullable=False,
        ),
        sa.Column('insight_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('prompt_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('report_version', sa.String(length=32), nullable=False, server_default='1.0'),
        sa.Column('model_provider', sa.String(length=64), nullable=False, server_default='openai'),
        sa.Column('model_name', sa.String(length=128), nullable=False, server_default='gpt-4o-mini'),
        sa.Column(
            'executive_narrative',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'business_assessment',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'risk_analysis',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'opportunities',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'strategic_priorities',
            sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'),
            nullable=False,
        ),
        sa.Column(
            'action_plan',
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

    # Create indexes
    op.create_index('ix_ai_insights_id', 'ai_insights', ['id'], unique=False)
    op.create_index('ix_ai_insights_dataset_id', 'ai_insights', ['dataset_id'], unique=False)
    op.create_index(
        'ix_ai_insights_dataset_created',
        'ai_insights',
        ['dataset_id', 'created_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_ai_insights_dataset_created', table_name='ai_insights')
    op.drop_index('ix_ai_insights_dataset_id', table_name='ai_insights')
    op.drop_index('ix_ai_insights_id', table_name='ai_insights')
    op.drop_table('ai_insights')
