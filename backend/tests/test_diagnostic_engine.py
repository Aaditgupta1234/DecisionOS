"""Unit tests for Phase 5.4 DiagnosticEngine Core orchestration, lifecycle management, and failure handling."""

import uuid
from datetime import datetime, timezone
import pytest

from app.core.constants import (
    DatasetStatus,
    DiagnosticGenerationStatus,
    FindingSeverity,
    FindingType,
    MetricCategory,
    UserRole,
)
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer
from app.diagnostics.diagnostic_engine import DiagnosticEngine, DiagnosticEngineResult
from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.metric_definition import MetricDefinition
from app.models.user import User


class FakeAnalyzerA(BaseDiagnosticAnalyzer):
    """Fake analyzer A returning a High Cancellation finding."""

    async def analyze(self, dataset: Dataset, metrics: list[DatasetMetric]) -> list[DiagnosticFinding]:
        return [
            DiagnosticFinding(
                dataset_id=dataset.id,
                finding_type=FindingType.HIGH_CANCELLATION_RATE,
                severity=FindingSeverity.HIGH,
                title="High Cancellation Rate Detected",
                description="Orders cancellation exceeds 20%.",
                business_impact="Revenue risk.",
                confidence_score=0.9,
            )
        ]


class FakeAnalyzerB(BaseDiagnosticAnalyzer):
    """Fake analyzer B returning a Revenue Drop finding."""

    async def analyze(self, dataset: Dataset, metrics: list[DatasetMetric]) -> list[DiagnosticFinding]:
        return [
            DiagnosticFinding(
                dataset_id=dataset.id,
                finding_type=FindingType.REVENUE_DROP,
                severity=FindingSeverity.CRITICAL,
                title="Severe Revenue Drop Detected",
                description="Revenue dropped by 35%.",
                business_impact="Critical business risk.",
                confidence_score=1.0,
            )
        ]


class EmptyAnalyzer(BaseDiagnosticAnalyzer):
    """Fake analyzer returning zero findings."""

    async def analyze(self, dataset: Dataset, metrics: list[DatasetMetric]) -> list[DiagnosticFinding]:
        return []


class FailingAnalyzer(BaseDiagnosticAnalyzer):
    """Fake analyzer intentionally raising an exception for testing failure paths."""

    async def analyze(self, dataset: Dataset, metrics: list[DatasetMetric]) -> list[DiagnosticFinding]:
        raise RuntimeError("Diagnostic analyzer internal computation failure.")


@pytest.fixture
def engine_test_dataset(db_session):
    """Fixture creating a test user and a READY dataset for engine tests."""
    user = User(
        email=f"engine_user_{uuid.uuid4().hex[:8]}@example.com",
        full_name="Engine Tester",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    dataset = Dataset(
        name="Engine Test Dataset",
        original_filename="engine_data.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_engine_data.csv",
        file_path="/tmp/engine_data.csv",
        file_size=2048,
        status=DatasetStatus.READY,
        uploaded_by=user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_validate_dataset_ready_success_and_failure(db_session, engine_test_dataset):
    """Test validate_dataset_ready passes for READY status and raises ValueError for non-READY status."""
    engine = DiagnosticEngine(db_session)

    # 1. READY passes
    await engine.validate_dataset_ready(engine_test_dataset)

    # 2. UPLOADED raises ValueError
    engine_test_dataset.status = DatasetStatus.UPLOADED
    with pytest.raises(ValueError, match="Dataset must be in READY status"):
        await engine.validate_dataset_ready(engine_test_dataset)


@pytest.mark.anyio
async def test_register_analyzer_and_deduplication(db_session):
    """Test analyzer registration and prevention of duplicates."""
    engine = DiagnosticEngine(db_session, analyzers=[])
    analyzer_a = FakeAnalyzerA()

    assert len(engine.analyzers) == 0

    engine.register_analyzer(analyzer_a)
    assert len(engine.analyzers) == 1

    # Duplicate registration ignored
    engine.register_analyzer(analyzer_a)
    assert len(engine.analyzers) == 1

    # Different analyzer added
    engine.register_analyzer(FakeAnalyzerB())
    assert len(engine.analyzers) == 2


@pytest.mark.anyio
async def test_load_dataset_metrics_ordering(db_session, engine_test_dataset):
    """Test load_dataset_metrics retrieves metrics ordered by metric_key ascending."""
    # Create or fetch Metric Definitions with unique test keys
    test_key_rev = f"test_rev_{uuid.uuid4().hex[:6]}"
    test_key_comp = f"test_comp_{uuid.uuid4().hex[:6]}"

    def1 = MetricDefinition(
        name="Test Revenue",
        metric_key=test_key_rev,
        metric_category=MetricCategory.REVENUE,
        required_field="revenue",
    )
    def2 = MetricDefinition(
        name="Test Completion",
        metric_key=test_key_comp,
        metric_category=MetricCategory.ORDERS,
        required_field="order_status",
    )
    db_session.add_all([def1, def2])
    db_session.commit()

    # Create Dataset Metrics
    now = datetime.now(timezone.utc)
    m1 = DatasetMetric(
        dataset_id=engine_test_dataset.id,
        metric_definition_id=def1.id,
        metric_key="z_metric",
        metric_name="Z Metric",
        metric_category=MetricCategory.REVENUE,
        metric_value=50000.0,
        calculated_at=now,
    )
    m2 = DatasetMetric(
        dataset_id=engine_test_dataset.id,
        metric_definition_id=def2.id,
        metric_key="a_metric",
        metric_name="A Metric",
        metric_category=MetricCategory.ORDERS,
        metric_value=75.5,
        calculated_at=now,
    )
    db_session.add_all([m1, m2])
    db_session.commit()

    engine = DiagnosticEngine(db_session)
    loaded = await engine.load_dataset_metrics(engine_test_dataset.id)

    assert len(loaded) == 2
    # a_metric < z_metric alphabetically
    assert loaded[0].metric_key == "a_metric"
    assert loaded[1].metric_key == "z_metric"


@pytest.mark.anyio
async def test_run_analyzers_multiple_and_empty(db_session, engine_test_dataset):
    """Test run_analyzers aggregates findings from registered analyzers and handles empty lists."""
    engine = DiagnosticEngine(db_session, analyzers=[FakeAnalyzerA(), FakeAnalyzerB(), EmptyAnalyzer()])

    findings = await engine.run_analyzers(engine_test_dataset, [])
    assert len(findings) == 2
    assert findings[0].finding_type == FindingType.HIGH_CANCELLATION_RATE
    assert findings[1].finding_type == FindingType.REVENUE_DROP

    # Empty engine
    empty_engine = DiagnosticEngine(db_session)
    empty_findings = await empty_engine.run_analyzers(engine_test_dataset, [])
    assert empty_findings == []


@pytest.mark.anyio
async def test_generate_success_lifecycle(db_session, engine_test_dataset):
    """Test generate() orchestration: validation, cleanup, analyzer execution, persistence, and status update."""
    engine = DiagnosticEngine(db_session, analyzers=[FakeAnalyzerA(), FakeAnalyzerB()])

    result = await engine.generate(engine_test_dataset)

    # 1. Verify result dataclass
    assert isinstance(result, DiagnosticEngineResult)
    assert result.dataset_id == engine_test_dataset.id
    assert result.findings_generated == 2
    assert result.status == DiagnosticGenerationStatus.GENERATED
    assert result.generated_at is not None
    assert result.error is None

    # 2. Verify dataset model state
    db_session.refresh(engine_test_dataset)
    assert engine_test_dataset.diagnostics_generation_status == DiagnosticGenerationStatus.GENERATED
    assert engine_test_dataset.diagnostics_generated_at is not None
    assert engine_test_dataset.diagnostics_generation_error is None

    # 3. Verify persisted findings via repository
    persisted = await engine.repo.get_dataset_findings(engine_test_dataset.id)
    assert len(persisted) == 2


@pytest.mark.anyio
async def test_generate_idempotent_regeneration(db_session, engine_test_dataset):
    """Test running generate() multiple times replaces old findings without leaving duplicate rows."""
    engine = DiagnosticEngine(db_session, analyzers=[FakeAnalyzerA()])

    # First run
    res1 = await engine.generate(engine_test_dataset)
    assert res1.findings_generated == 1
    assert await engine.repo.get_total_findings(engine_test_dataset.id) == 1

    # Second run with different analyzer
    engine.analyzers = [FakeAnalyzerB()]
    res2 = await engine.generate(engine_test_dataset)
    assert res2.findings_generated == 1

    # Only 1 finding should remain (old one deleted)
    findings = await engine.repo.get_dataset_findings(engine_test_dataset.id)
    assert len(findings) == 1
    assert findings[0].finding_type == FindingType.REVENUE_DROP


@pytest.mark.anyio
async def test_generate_failure_handling(db_session, engine_test_dataset):
    """Test engine updates dataset status to FAILED, saves error, and re-raises on exception."""
    engine = DiagnosticEngine(db_session, analyzers=[FailingAnalyzer()])

    with pytest.raises(RuntimeError, match="Diagnostic analyzer internal computation failure."):
        await engine.generate(engine_test_dataset)

    # Verify dataset updated to FAILED with error text
    db_session.refresh(engine_test_dataset)
    assert engine_test_dataset.diagnostics_generation_status == DiagnosticGenerationStatus.FAILED
    assert "Diagnostic analyzer internal computation failure." in engine_test_dataset.diagnostics_generation_error
