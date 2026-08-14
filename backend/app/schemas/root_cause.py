"""Pydantic schemas for Root Cause Analysis requests, responses, graph serialization, and Phase 6 AI summaries."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import FindingSeverity, FindingType, RelationshipStrength, RelationshipType
from app.schemas.diagnostic import DiagnosticFindingResponse


class CausalChainNode(BaseModel):
    """Schema representing a node vertex in the causal graph."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique UUID string of the diagnostic finding.")
    title: str = Field(..., description="Human-readable title of the finding.")
    category: str = Field(..., description="Business category domain (e.g. REVENUE, CUSTOMER).")
    subtype: str = Field(..., description="Granular finding subtype.")
    severity: str = Field(..., description="Severity classification (LOW, MEDIUM, HIGH, CRITICAL).")
    confidence_score: float = Field(..., description="Finding confidence score [0.0 - 1.0].")


class CausalChainEdge(BaseModel):
    """Schema representing a directed causal edge from cause to effect in the graph."""
    model_config = ConfigDict(from_attributes=True)

    source_id: str = Field(..., description="UUID of the driver/cause finding.")
    target_id: str = Field(..., description="UUID of the impacted/effect finding.")
    relationship_type: str = Field(..., description="Causal relationship type (CAUSES, CONTRIBUTES_TO, etc.).")
    relationship_strength: str = Field(..., description="Relationship strength tier (STRONG, VERY_STRONG, etc.).")
    confidence_score: float = Field(..., description="Edge confidence score [0.0 - 1.0].")
    impact_score: float = Field(..., description="Edge business impact score [0.0 - 1.0].")


class CausalGraphResponse(BaseModel):
    """Schema for the full Directed Acyclic Graph (DAG) of causal findings."""
    nodes: List[CausalChainNode] = Field(default_factory=list, description="List of finding vertices.")
    edges: List[CausalChainEdge] = Field(default_factory=list, description="List of directed causal edges.")


class RootCauseAnalysisResponse(BaseModel):
    """Schema representing a validated single RootCauseAnalysis entity."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique identifier of the root cause analysis record.")
    dataset_id: UUID = Field(..., description="Foreign key reference to the dataset.")
    primary_finding_id: UUID = Field(..., description="Foreign key to the primary symptom/effect finding.")
    root_cause_finding_id: UUID = Field(..., description="Foreign key to the underlying cause finding.")
    relationship_type: RelationshipType = Field(..., description="Classification of the causal link.")
    relationship_strength: RelationshipStrength = Field(..., description="Discrete strength tier.")
    confidence_score: float = Field(..., description="Combined confidence score [0.0 - 1.0].")
    impact_score: float = Field(..., description="Downstream business impact score [0.0 - 1.0].")
    explanation: str = Field(..., description="Clear human-readable narrative explanation.")
    supporting_evidence: Optional[Dict[str, Any]] = Field(None, description="Detailed metrics, rule, and correlation data.")
    created_at: datetime = Field(..., description="Timestamp when the analysis was persisted.")
    primary_finding: Optional[DiagnosticFindingResponse] = Field(None, description="Eager-loaded primary finding entity.")
    root_cause_finding: Optional[DiagnosticFindingResponse] = Field(None, description="Eager-loaded root cause finding entity.")


class RootCauseItem(BaseModel):
    """Sub-item schema detailing a single root cause within a consolidated issue summary."""
    finding_id: UUID = Field(..., description="UUID of the cause finding.")
    title: str = Field(..., description="Title of the cause finding.")
    category: str = Field(..., description="Category of the cause finding.")
    subtype: str = Field(..., description="Subtype of the cause finding.")
    severity: str = Field(..., description="Severity of the cause finding.")
    relationship_type: str = Field(..., description="Relationship classification.")
    relationship_strength: str = Field(..., description="Strength tier.")
    confidence_score: float = Field(..., description="Confidence score.")
    impact_score: float = Field(..., description="Impact score.")
    explanation: str = Field(..., description="Narrative explanation.")


class RootCauseSummary(BaseModel):
    """
    Consolidated issue summary schema designed for direct consumption by Phase 6 LLM Insights.
    
    Groups all upstream causes and multi-hop causal chains for a major business symptom.
    """
    primary_issue: str = Field(..., description="Title and magnitude of the primary business problem.")
    primary_finding_id: UUID = Field(..., description="UUID of the primary finding.")
    primary_severity: str = Field(..., description="Severity of the primary finding.")
    root_causes: List[RootCauseItem] = Field(default_factory=list, description="Ranked list of underlying root causes.")
    overall_confidence: float = Field(..., description="Aggregated confidence across causal drivers.")
    highest_impact: float = Field(..., description="Highest impact score among causal drivers.")
    causal_chains: List[List[str]] = Field(default_factory=list, description="Full ordered causal paths leading to the primary issue.")


class DatasetRootCausesResponse(BaseModel):
    """Top-level response schema aggregating all root cause analyses, summaries, and graph for a dataset."""
    dataset_id: UUID = Field(..., description="Dataset identifier.")
    total_root_causes: int = Field(..., description="Total count of validated causal relationships.")
    analyses: List[RootCauseAnalysisResponse] = Field(default_factory=list, description="Individual causal records.")
    summaries: List[RootCauseSummary] = Field(default_factory=list, description="Synthesized AI-ready problem summaries.")
    graph: CausalGraphResponse = Field(..., description="DAG representation for interactive visualization.")


class GenerateRootCauseRequest(BaseModel):
    """Request schema for triggering root cause analysis on a dataset."""
    dataset_id: UUID = Field(..., description="Target dataset UUID.")
    recalculate_diagnostics: bool = Field(False, description="Whether to re-execute diagnostic finding analyzers first.")
