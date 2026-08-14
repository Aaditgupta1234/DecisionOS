"""Diagnostics package providing Root Cause Engine, analyzer contracts, and domain analyzers."""

from app.diagnostics.analyzer_registry import AnalyzerRegistry
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.diagnostics.customer_analyzer import CustomerDiagnosticAnalyzer
from app.diagnostics.diagnostic_engine import DiagnosticEngine, DiagnosticEngineResult
from app.diagnostics.evidence_builder import EvidenceBuilder
from app.diagnostics.metric_keys import MetricKeys
from app.diagnostics.operational_analyzer import OperationalDiagnosticAnalyzer
from app.diagnostics.product_analyzer import ProductDiagnosticAnalyzer
from app.diagnostics.revenue_analyzer import RevenueDiagnosticAnalyzer
from app.diagnostics.severity import calculate_confidence, calculate_severity

__all__ = [
    "AnalyzerRegistry",
    "BaseDiagnosticAnalyzer",
    "CustomerDiagnosticAnalyzer",
    "DiagnosticEngine",
    "DiagnosticEngineResult",
    "EvidenceBuilder",
    "MetricKeys",
    "OperationalDiagnosticAnalyzer",
    "ProductDiagnosticAnalyzer",
    "RevenueDiagnosticAnalyzer",
    "calculate_confidence",
    "calculate_severity",
]
