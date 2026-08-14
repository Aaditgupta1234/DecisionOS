"""Unit tests for Phase 5.5 AnalyzerRegistry lifecycle, registration, and discovery."""

import pytest
from app.diagnostics.analyzer_registry import AnalyzerRegistry
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.diagnostics.customer_analyzer import CustomerDiagnosticAnalyzer
from app.diagnostics.diagnostic_engine import DiagnosticEngine
from app.diagnostics.operational_analyzer import OperationalDiagnosticAnalyzer
from app.diagnostics.product_analyzer import ProductDiagnosticAnalyzer
from app.diagnostics.revenue_analyzer import RevenueDiagnosticAnalyzer
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding


class CustomTestAnalyzer(BaseDiagnosticAnalyzer):
    """Custom analyzer for testing registry additions."""

    async def analyze(self, dataset: Dataset, metrics: list[DatasetMetric]) -> list[DiagnosticFinding]:
        return []


def test_default_analyzer_discovery():
    """Test get_default_analyzers loads and returns all 4 standard domain analyzers."""
    AnalyzerRegistry.reset_to_defaults()
    analyzers = AnalyzerRegistry.get_default_analyzers()

    assert len(analyzers) == 4
    class_names = {a.__class__.__name__ for a in analyzers}
    assert "RevenueDiagnosticAnalyzer" in class_names
    assert "CustomerDiagnosticAnalyzer" in class_names
    assert "OperationalDiagnosticAnalyzer" in class_names
    assert "ProductDiagnosticAnalyzer" in class_names


def test_custom_analyzer_registration_and_lookup():
    """Test registering custom analyzer class and instance and retrieving by name."""
    AnalyzerRegistry.clear()
    assert len(AnalyzerRegistry.get_analyzers()) == 0

    # 1. Register instance
    custom_inst = CustomTestAnalyzer()
    AnalyzerRegistry.register(custom_inst)
    assert len(AnalyzerRegistry.get_analyzers()) == 1
    assert AnalyzerRegistry.get_analyzer("CustomTestAnalyzer") is custom_inst

    # 2. Register class
    AnalyzerRegistry.register_class(RevenueDiagnosticAnalyzer)
    assert len(AnalyzerRegistry.get_analyzers()) == 2
    assert isinstance(AnalyzerRegistry.get_analyzer("RevenueDiagnosticAnalyzer"), RevenueDiagnosticAnalyzer)

    # 3. Missing analyzer returns None
    assert AnalyzerRegistry.get_analyzer("NonExistentAnalyzer") is None


def test_analyzer_registry_deduplication():
    """Test that registering duplicate analyzer instances updates existing entry without count inflation."""
    AnalyzerRegistry.clear()
    a1 = RevenueDiagnosticAnalyzer()
    a2 = RevenueDiagnosticAnalyzer()

    AnalyzerRegistry.register(a1)
    assert len(AnalyzerRegistry.get_analyzers()) == 1

    # Re-registering replaces or keeps single entry
    AnalyzerRegistry.register(a2)
    assert len(AnalyzerRegistry.get_analyzers()) == 1


def test_diagnostic_engine_auto_loads_default_analyzers(db_session):
    """Test that DiagnosticEngine initialized without explicit analyzers automatically loads defaults."""
    AnalyzerRegistry.reset_to_defaults()
    engine = DiagnosticEngine(db_session)

    assert len(engine.analyzers) == 4
    engine_analyzer_types = {type(a) for a in engine.analyzers}
    assert RevenueDiagnosticAnalyzer in engine_analyzer_types
    assert CustomerDiagnosticAnalyzer in engine_analyzer_types
    assert OperationalDiagnosticAnalyzer in engine_analyzer_types
    assert ProductDiagnosticAnalyzer in engine_analyzer_types
