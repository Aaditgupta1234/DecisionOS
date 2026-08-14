"""Create root_cause_analyses table and relationship enums

Revision ID: 0005_root_cause_analysis
Revises: 0004_diagnostic_findings
Create Date: 2026-08-14

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0005_root_cause_analysis'
down_revision: Union[str, None] = '0004_diagnostic_findings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create named PostgreSQL enum types
    rel_type_enum = sa.Enum(
        'CAUSES',
        'CONTRIBUTES_TO',
        'CORRELATES_WITH',
        'AMPLIFIES',
        'DEPENDENT_ON',
        name='relationship_type',
    )
    rel_strength_enum = sa.Enum(
        'VERY_WEAK',
        'WEAK',
        'MODERATE',
        'STRONG',
        'VERY_STRONG',
        name='relationship_strength',
    )

    # 2. Create root_cause_analyses table
    op.create_table(
        'root_cause_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('primary_finding_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnostic_findings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('root_cause_finding_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('diagnostic_findings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship_type', rel_type_enum, nullable=False, server_default='CAUSES'),
        sa.Column('relationship_strength', rel_strength_enum, nullable=False, server_default='STRONG'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('impact_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('supporting_evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='ck_rca_confidence_score_range'),
        sa.CheckConstraint('impact_score >= 0.0 AND impact_score <= 1.0', name='ck_rca_impact_score_range'),
    )
    op.create_index('ix_root_cause_analyses_id', 'root_cause_analyses', ['id'], unique=False)
    op.create_index('ix_root_cause_analyses_dataset_id', 'root_cause_analyses', ['dataset_id'], unique=False)
    op.create_index('ix_root_cause_analyses_primary_finding_id', 'root_cause_analyses', ['primary_finding_id'], unique=False)
    op.create_index('ix_root_cause_analyses_root_cause_finding_id', 'root_cause_analyses', ['root_cause_finding_id'], unique=False)
    op.create_index('ix_root_cause_analyses_relationship_type', 'root_cause_analyses', ['relationship_type'], unique=False)
    op.create_index('ix_root_cause_analyses_relationship_strength', 'root_cause_analyses', ['relationship_strength'], unique=False)
    op.create_index('ix_rca_dataset_impact', 'root_cause_analyses', ['dataset_id', 'impact_score'], unique=False)
    op.create_index('ix_rca_pair', 'root_cause_analyses', ['primary_finding_id', 'root_cause_finding_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_rca_pair', table_name='root_cause_analyses')
    op.drop_index('ix_rca_dataset_impact', table_name='root_cause_analyses')
    op.drop_index('ix_root_cause_analyses_relationship_strength', table_name='root_cause_analyses')
    op.drop_index('ix_root_cause_analyses_relationship_type', table_name='root_cause_analyses')
    op.drop_index('ix_root_cause_analyses_root_cause_finding_id', table_name='root_cause_analyses')
    op.drop_index('ix_root_cause_analyses_primary_finding_id', table_name='root_cause_analyses')
    op.drop_index('ix_root_cause_analyses_dataset_id', table_name='root_cause_analyses')
    op.drop_index('ix_root_cause_analyses_id', table_name='root_cause_analyses')
    op.drop_table('root_cause_analyses')

    rel_strength_enum = sa.Enum(
        'VERY_WEAK',
        'WEAK',
        'MODERATE',
        'STRONG',
        'VERY_STRONG',
        name='relationship_strength',
    )
    rel_strength_enum.drop(op.get_bind(), checkfirst=True)

    rel_type_enum = sa.Enum(
        'CAUSES',
        'CONTRIBUTES_TO',
        'CORRELATES_WITH',
        'AMPLIFIES',
        'DEPENDENT_ON',
        name='relationship_type',
    )
    rel_type_enum.drop(op.get_bind(), checkfirst=True)
