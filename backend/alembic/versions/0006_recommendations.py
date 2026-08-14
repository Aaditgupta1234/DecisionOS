"""Create recommendations table and recommendation enums

Revision ID: 0006_recommendations
Revises: 0005_root_cause_analysis
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0006_recommendations'
down_revision: Union[str, None] = '0005_root_cause_analysis'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create named PostgreSQL enum types
    rec_type_enum = sa.Enum(
        'REVENUE_GROWTH',
        'CUSTOMER_RETENTION',
        'CUSTOMER_ACQUISITION',
        'PRODUCT_OPTIMIZATION',
        'PRICING_STRATEGY',
        'PROCESS_IMPROVEMENT',
        'OPERATIONAL_EFFICIENCY',
        'COST_OPTIMIZATION',
        'RISK_MITIGATION',
        name='recommendation_type',
    )
    rec_priority_enum = sa.Enum(
        'LOW',
        'MEDIUM',
        'HIGH',
        'CRITICAL',
        name='recommendation_priority',
    )
    time_to_value_enum = sa.Enum(
        'IMMEDIATE',
        'SHORT_TERM',
        'MEDIUM_TERM',
        'LONG_TERM',
        name='expected_time_to_value',
    )
    rec_status_enum = sa.Enum(
        'PENDING',
        'ACCEPTED',
        'REJECTED',
        'IMPLEMENTED',
        'ARCHIVED',
        name='recommendation_status',
    )
    rec_source_enum = sa.Enum(
        'RULE_ENGINE',
        'AI_INSIGHT',
        'USER_CUSTOM',
        'HYBRID',
        name='recommendation_source',
    )

    # 2. Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnostic_findings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('root_cause_analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('root_cause_analyses.id', ondelete='SET NULL'), nullable=True),
        sa.Column('recommendation_type', rec_type_enum, nullable=False),
        sa.Column('priority', rec_priority_enum, nullable=False),
        sa.Column('status', rec_status_enum, nullable=False, server_default='PENDING'),
        sa.Column('source', rec_source_enum, nullable=False, server_default='RULE_ENGINE'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('why_recommended', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('estimated_impact_score', sa.Float(), nullable=False, server_default='0.7'),
        sa.Column('estimated_effort_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('expected_time_to_value', time_to_value_enum, nullable=False, server_default='SHORT_TERM'),
        sa.Column('action_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('success_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('outcomes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('implemented_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='ck_rec_confidence_score_range'),
        sa.CheckConstraint('estimated_impact_score >= 0.0 AND estimated_impact_score <= 1.0', name='ck_rec_impact_score_range'),
        sa.CheckConstraint('estimated_effort_score >= 0.0 AND estimated_effort_score <= 1.0', name='ck_rec_effort_score_range'),
    )
    op.create_index('ix_recommendations_id', 'recommendations', ['id'], unique=False)
    op.create_index('ix_recommendations_dataset_id', 'recommendations', ['dataset_id'], unique=False)
    op.create_index('ix_recommendations_finding_id', 'recommendations', ['finding_id'], unique=False)
    op.create_index('ix_recommendations_rca_id', 'recommendations', ['root_cause_analysis_id'], unique=False)
    op.create_index('ix_recommendations_type', 'recommendations', ['recommendation_type'], unique=False)
    op.create_index('ix_recommendations_priority', 'recommendations', ['priority'], unique=False)
    op.create_index('ix_recommendations_status', 'recommendations', ['status'], unique=False)
    op.create_index('ix_recommendations_dataset_priority', 'recommendations', ['dataset_id', 'priority'], unique=False)
    op.create_index('ix_recommendations_dataset_status', 'recommendations', ['dataset_id', 'status'], unique=False)
    op.create_index('ix_recommendations_dataset_impact', 'recommendations', ['dataset_id', 'estimated_impact_score'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_recommendations_dataset_impact', table_name='recommendations')
    op.drop_index('ix_recommendations_dataset_status', table_name='recommendations')
    op.drop_index('ix_recommendations_dataset_priority', table_name='recommendations')
    op.drop_index('ix_recommendations_status', table_name='recommendations')
    op.drop_index('ix_recommendations_priority', table_name='recommendations')
    op.drop_index('ix_recommendations_type', table_name='recommendations')
    op.drop_index('ix_recommendations_rca_id', table_name='recommendations')
    op.drop_index('ix_recommendations_finding_id', table_name='recommendations')
    op.drop_index('ix_recommendations_dataset_id', table_name='recommendations')
    op.drop_index('ix_recommendations_id', table_name='recommendations')
    op.drop_table('recommendations')
