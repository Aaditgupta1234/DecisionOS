"""Domain models for ExecutiveSummary, IntelligenceReport, and Report Export interfaces."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.constants import BusinessHealthStatus, ReportExportFormat
from app.intelligence.constants import CANONICAL_REPORT_VERSION


@dataclass
class ExecutiveSummary:
    """
    High-level business summary synthesized from top findings, root causes,
    prescribed actions, and business health scoring.
    
    Attributes:
        dataset_id: Target dataset UUID.
        generated_at: Timestamp when summary was built.
        primary_issue: Headline of the most critical business anomaly detected.
        severity: Severity tier of the primary issue (CRITICAL, HIGH, etc.).
        top_root_cause: Title of the primary causal driver initiating the issue.
        top_recommendation: Title of the top-ranked strategic recommendation.
        key_risks: Concise bullet points of top business vulnerabilities.
        overall_confidence: Composite confidence score across findings and rules [0.0 - 1.0].
        confidence_breakdown: Confidence averages for findings, root causes, and recommendations.
        business_health_score: Integer health index [0 - 100].
        business_health_status: Discrete health classification (EXCELLENT, WATCH_LIST, CRITICAL, etc.).
        expected_business_impact: High-level narrative of projected business returns.
    """

    dataset_id: UUID
    generated_at: datetime
    primary_issue: str
    severity: str
    top_root_cause: Optional[str]
    top_recommendation: Optional[str]
    key_risks: List[str]
    overall_confidence: float
    confidence_breakdown: Dict[str, float]
    business_health_score: int
    business_health_status: BusinessHealthStatus
    expected_business_impact: str
    health_score_explanation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes executive summary to dictionary."""
        d = asdict(self)
        d["dataset_id"] = str(self.dataset_id)
        d["generated_at"] = self.generated_at.isoformat()
        d["business_health_status"] = (
            self.business_health_status.value
            if hasattr(self.business_health_status, "value")
            else str(self.business_health_status)
        )
        return d


@dataclass
class IntelligenceReport:
    """
    Canonical, unified business intelligence artifact compiling metrics,
    findings, causal links, recommendations, and executive summaries.
    
    Attributes:
        report_version: Semantic schema version (e.g. "1.0").
        dataset_id: Target dataset UUID.
        dataset_name: Name of the dataset analyzed.
        generated_at: Timestamp when this report was compiled.
        dataset_last_updated_at: Timestamp when underlying data was last modified.
        artifact_counts: Counts of metrics, findings, root causes, and recommendations.
        metrics: Serialized list of KPI records.
        findings: Serialized list of diagnostic finding records.
        root_causes: Serialized list of root cause analysis records.
        recommendations: Serialized list of recommendation records.
        executive_summary: High-level executive synthesis.
    """

    report_version: str = CANONICAL_REPORT_VERSION
    dataset_id: UUID = field(default_factory=UUID)
    dataset_name: str = ""
    generated_at: datetime = field(default_factory=datetime.utcnow)
    dataset_last_updated_at: Optional[datetime] = None
    artifact_counts: Dict[str, int] = field(default_factory=dict)
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    root_causes: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    executive_summary: Optional[ExecutiveSummary] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the intelligence report to a complete JSON-compatible dictionary."""
        return {
            "report_version": self.report_version,
            "dataset_id": str(self.dataset_id),
            "dataset_name": self.dataset_name,
            "generated_at": self.generated_at.isoformat(),
            "dataset_last_updated_at": (
                self.dataset_last_updated_at.isoformat()
                if self.dataset_last_updated_at
                else None
            ),
            "artifact_counts": self.artifact_counts,
            "metrics": self.metrics,
            "findings": self.findings,
            "root_causes": self.root_causes,
            "recommendations": self.recommendations,
            "executive_summary": (
                self.executive_summary.to_dict() if self.executive_summary else None
            ),
        }


@dataclass
class ExportInterface:
    """
    Interface definition for future PDF, PowerPoint, and executive export engines.
    """

    format: ReportExportFormat = ReportExportFormat.PDF
    include_sections: List[str] = field(
        default_factory=lambda: [
            "executive_summary",
            "metrics",
            "findings",
            "root_causes",
            "recommendations",
        ]
    )
    title_override: Optional[str] = None
    template_style: str = "executive_dark"
    author: Optional[str] = None
