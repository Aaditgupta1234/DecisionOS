"""Pydantic schemas package for data validation and response formatting."""

from app.schemas.base import ErrorResponse, SuccessResponse
from app.schemas.dataset import (
    DatasetColumnResponse,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetMappingRequest,
    DatasetMappingResponse,
    DatasetPreviewResponse,
    DatasetUploadResponse,
    MappingSuggestion,
)
from app.schemas.diagnostic import (
    DiagnosticFindingListResponse,
    DiagnosticFindingResponse,
    DiagnosticGenerationResponse,
    DiagnosticGenerationStatusResponse,
    DiagnosticSeverityBreakdown,
    DiagnosticSummaryResponse,
)
from app.schemas.root_cause import (
    CausalChainEdge,
    CausalChainNode,
    CausalGraphResponse,
    DatasetRootCausesResponse,
    GenerateRootCauseRequest,
    RootCauseAnalysisResponse,
    RootCauseItem,
    RootCauseSummary,
)
from app.schemas.metric import (
    MetricDefinitionResponse,
    MetricGenerationResponse,
    MetricResponse,
    MetricSummaryResponse,
)
from app.schemas.recommendation import (
    DatasetRecommendationsResponse,
    GenerateRecommendationsRequest,
    RecommendationItem,
    RecommendationOutcome,
    RecommendationResponse,
    RecommendationSummary,
    UpdateRecommendationStatusRequest,
)
from app.schemas.intelligence import (
    BusinessHealthResponse,
    ExecutiveSummaryResponse,
    IntelligenceReportResponse,
    ReportExportSchema,
)
from app.schemas.ai import (
    AIHealthResponse,
    AIProviderInfo,
    AIProvidersResponse,
    AITestRequest,
    AITestResponse,
)
from app.schemas.narrative import (
    DatasetNarrativePackageResponse,
    ExecutiveNarrativeResponse,
    ForecastNarrativeRequest,
    ForecastNarrativeResponse,
    KPINarrativeResponse,
    NarrativeGenerateRequest,
    NarrativeMetadata,
    NarrativeReportHistoryItem,
    RecommendationNarrativeResponse,
    RootCauseNarrativeResponse,
    ScenarioNarrativeRequest,
    ScenarioNarrativeResponse,
)
from app.schemas.executive_insight import (
    BoardCommentary,
    ExecutiveAlert,
    ExecutiveInsightHistoryItem,
    ExecutiveInsightMetadata,
    ExecutiveInsightPackage,
    ExecutiveInsightRequest,
    OpportunityInsight,
    PriorityAction,
    RiskInsight,
    StrategicTheme,
)
from app.schemas.token import TokenPayload, TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate

__all__ = [
    # Base
    "SuccessResponse",
    "ErrorResponse",
    # Auth & Tokens
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "TokenResponse",
    "TokenPayload",
    # Datasets
    "DatasetColumnResponse",
    "DatasetUploadResponse",
    "DatasetListResponse",
    "DatasetDetailResponse",
    "DatasetPreviewResponse",
    "MappingSuggestion",
    "DatasetMappingRequest",
    "DatasetMappingResponse",
    # Metrics
    "MetricDefinitionResponse",
    "MetricResponse",
    "MetricGenerationResponse",
    "MetricSummaryResponse",
    # Diagnostics
    "DiagnosticFindingResponse",
    "DiagnosticFindingListResponse",
    "DiagnosticSeverityBreakdown",
    "DiagnosticSummaryResponse",
    "DiagnosticGenerationResponse",
    "DiagnosticGenerationStatusResponse",
    # Root Cause Analysis
    "RootCauseAnalysisResponse",
    "RootCauseItem",
    "RootCauseSummary",
    "CausalChainNode",
    "CausalChainEdge",
    "CausalGraphResponse",
    "DatasetRootCausesResponse",
    "GenerateRootCauseRequest",
    # Recommendations
    "RecommendationOutcome",
    "RecommendationResponse",
    "UpdateRecommendationStatusRequest",
    "RecommendationItem",
    "RecommendationSummary",
    "DatasetRecommendationsResponse",
    "GenerateRecommendationsRequest",
    # Intelligence Layer
    "BusinessHealthResponse",
    "ExecutiveSummaryResponse",
    "IntelligenceReportResponse",
    "ReportExportSchema",
    # AI Provider Layer
    "AIHealthResponse",
    "AIProviderInfo",
    "AIProvidersResponse",
    "AITestRequest",
    "AITestResponse",
    # AI Narrative Engine
    "NarrativeMetadata",
    "NarrativeGenerateRequest",
    "ForecastNarrativeRequest",
    "ScenarioNarrativeRequest",
    "ExecutiveNarrativeResponse",
    "KPINarrativeResponse",
    "RootCauseNarrativeResponse",
    "RecommendationNarrativeResponse",
    "ForecastNarrativeResponse",
    "ScenarioNarrativeResponse",
    "DatasetNarrativePackageResponse",
    "NarrativeReportHistoryItem",
    # Executive Insights
    "ExecutiveInsightRequest",
    "ExecutiveInsightMetadata",
    "RiskInsight",
    "OpportunityInsight",
    "PriorityAction",
    "StrategicTheme",
    "ExecutiveAlert",
    "BoardCommentary",
    "ExecutiveInsightPackage",
    "ExecutiveInsightHistoryItem",
]
