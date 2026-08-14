"""Unit tests for Phase 5.3 DiagnosticRepository layer covering CRUD, filtering, pagination, and aggregations."""

import uuid
from datetime import datetime, timezone, timedelta
import pytest

from app.core.constants import (
    FindingSeverity,
    FindingType,
    UserRole,
)
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.user import User
from app.repositories.diagnostic_repository import DiagnosticRepository


@pytest.fixture
def test_dataset(db_session):
    """Fixture creating a test user and dataset for repository tests."""
    user = User(
        email=f"repo_test_{uuid.uuid4().hex[:8]}@example.com",
        full_name="Repo Tester",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    dataset = Dataset(
        name="Repository Test Dataset",
        original_filename="repo_sales.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_repo_sales.csv",
        file_path="/tmp/repo_sales.csv",
        file_size=1024,
        uploaded_by=user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.mark.anyio
async def test_create_single_finding(db_session, test_dataset):
    """Test create() persists a single diagnostic finding and returns refreshed ORM entity."""
    repo = DiagnosticRepository(db_session)

    finding = await repo.create(
        dataset_id=test_dataset.id,
        finding_type=FindingType.HIGH_CANCELLATION_RATE,
        severity=FindingSeverity.HIGH,
        title="High Order Cancellation Rate",
        description="Cancellation rate is 25%.",
        business_impact="Revenue loss of $5,000.",
        metric_key="completion_rate",
        confidence_score=0.92,
        supporting_data={"cancellation_rate": 25.0},
    )

    assert finding.id is not None
    assert finding.dataset_id == test_dataset.id
    assert finding.finding_type == FindingType.HIGH_CANCELLATION_RATE
    assert finding.severity == FindingSeverity.HIGH
    assert finding.title == "High Order Cancellation Rate"
    assert finding.confidence_score == 0.92
    assert finding.supporting_data == {"cancellation_rate": 25.0}
    assert finding.generated_at is not None


@pytest.mark.anyio
async def test_create_many_findings(db_session, test_dataset):
    """Test create_many() bulk persists multiple findings and refreshes them."""
    repo = DiagnosticRepository(db_session)

    findings_in = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_DROP,
            severity=FindingSeverity.CRITICAL,
            title="Revenue Drop",
            description="Revenue dropped 30%.",
            business_impact="High impact.",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.DELIVERY_DELAY,
            severity=FindingSeverity.MEDIUM,
            title="Delivery Delay",
            description="Avg delivery 6 days.",
            business_impact="Customer dissatisfaction.",
        ),
    ]

    saved = await repo.create_many(findings_in)
    assert len(saved) == 2
    for f in saved:
        assert f.id is not None
        assert f.generated_at is not None

    total = await repo.get_total_findings(test_dataset.id)
    assert total == 2


@pytest.mark.anyio
async def test_create_many_large_batch(db_session, test_dataset):
    """Test create_many() with a large batch of 50 findings."""
    repo = DiagnosticRepository(db_session)

    large_batch = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.DATA_QUALITY_RISK,
            severity=FindingSeverity.LOW,
            title=f"Data Quality Item {i}",
            description=f"Missing values on column {i}.",
            business_impact="Minor impact.",
        )
        for i in range(50)
    ]

    saved = await repo.create_many(large_batch)
    assert len(saved) == 50

    total = await repo.get_total_findings(test_dataset.id)
    assert total == 50


@pytest.mark.anyio
async def test_get_by_id_success_and_missing(db_session, test_dataset):
    """Test get_by_id returns finding when found, None when missing."""
    repo = DiagnosticRepository(db_session)

    created = await repo.create(
        dataset_id=test_dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Concentration",
        description="Top customer generates 60% revenue.",
        business_impact="Client churn risk.",
    )

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.title == "Customer Concentration"

    missing = await repo.get_by_id(uuid.uuid4())
    assert missing is None


@pytest.mark.anyio
async def test_get_dataset_findings_ordering_and_pagination(db_session, test_dataset):
    """Test get_dataset_findings ordering by (generated_at DESC, id DESC) and limit/offset."""
    repo = DiagnosticRepository(db_session)
    now = datetime.now(timezone.utc)

    findings = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_DROP,
            severity=FindingSeverity.LOW,
            title=f"Finding {i}",
            description="Desc",
            business_impact="Impact",
            generated_at=now + timedelta(minutes=i * 10),
        )
        for i in range(5)
    ]
    await repo.create_many(findings)

    # All 5 ordered newest-first (Finding 4 should be first)
    all_findings = await repo.get_dataset_findings(test_dataset.id, limit=10, offset=0)
    assert len(all_findings) == 5
    assert all_findings[0].title == "Finding 4"
    assert all_findings[4].title == "Finding 0"

    # Pagination: limit=2, offset=0 -> Findings 4, 3
    page1 = await repo.get_dataset_findings(test_dataset.id, limit=2, offset=0)
    assert len(page1) == 2
    assert page1[0].title == "Finding 4"
    assert page1[1].title == "Finding 3"

    # Pagination: limit=2, offset=2 -> Findings 2, 1
    page2 = await repo.get_dataset_findings(test_dataset.id, limit=2, offset=2)
    assert len(page2) == 2
    assert page2[0].title == "Finding 2"
    assert page2[1].title == "Finding 1"


@pytest.mark.anyio
async def test_pagination_invalid_guards(db_session, test_dataset):
    """Test get_dataset_findings raises ValueError on invalid limit or offset."""
    repo = DiagnosticRepository(db_session)

    with pytest.raises(ValueError, match="limit must be >= 1"):
        await repo.get_dataset_findings(test_dataset.id, limit=0)

    with pytest.raises(ValueError, match="offset must be >= 0"):
        await repo.get_dataset_findings(test_dataset.id, offset=-1)


@pytest.mark.anyio
async def test_get_findings_by_severity(db_session, test_dataset):
    """Test get_findings_by_severity filters findings strictly by severity."""
    repo = DiagnosticRepository(db_session)

    findings = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_DROP,
            severity=FindingSeverity.CRITICAL,
            title="Critical Finding 1",
            description="Desc",
            business_impact="Impact",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_CONCENTRATION,
            severity=FindingSeverity.CRITICAL,
            title="Critical Finding 2",
            description="Desc",
            business_impact="Impact",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.DELIVERY_DELAY,
            severity=FindingSeverity.MEDIUM,
            title="Medium Finding",
            description="Desc",
            business_impact="Impact",
        ),
    ]
    await repo.create_many(findings)

    crit_findings = await repo.get_findings_by_severity(test_dataset.id, FindingSeverity.CRITICAL)
    assert len(crit_findings) == 2
    for f in crit_findings:
        assert f.severity == FindingSeverity.CRITICAL

    high_findings = await repo.get_findings_by_severity(test_dataset.id, FindingSeverity.HIGH)
    assert len(high_findings) == 0


@pytest.mark.anyio
async def test_get_findings_by_type(db_session, test_dataset):
    """Test get_findings_by_type filters findings strictly by finding_type."""
    repo = DiagnosticRepository(db_session)

    findings = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.HIGH_CANCELLATION_RATE,
            severity=FindingSeverity.HIGH,
            title="Cancellation 1",
            description="Desc",
            business_impact="Impact",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.DELIVERY_DELAY,
            severity=FindingSeverity.MEDIUM,
            title="Delay 1",
            description="Desc",
            business_impact="Impact",
        ),
    ]
    await repo.create_many(findings)

    canc_findings = await repo.get_findings_by_type(test_dataset.id, FindingType.HIGH_CANCELLATION_RATE)
    assert len(canc_findings) == 1
    assert canc_findings[0].finding_type == FindingType.HIGH_CANCELLATION_RATE


@pytest.mark.anyio
async def test_get_total_findings_populated_and_empty(db_session, test_dataset):
    """Test get_total_findings accuracy for populated and empty datasets."""
    repo = DiagnosticRepository(db_session)

    # Empty dataset
    assert await repo.get_total_findings(test_dataset.id) == 0

    # Populated
    await repo.create(
        dataset_id=test_dataset.id,
        finding_type=FindingType.DATA_QUALITY_RISK,
        severity=FindingSeverity.LOW,
        title="Quality 1",
        description="Desc",
        business_impact="Impact",
    )
    assert await repo.get_total_findings(test_dataset.id) == 1


@pytest.mark.anyio
async def test_get_severity_counts_populated_and_empty(db_session, test_dataset):
    """Test get_severity_counts returns all 4 severity tiers with zero-fill."""
    repo = DiagnosticRepository(db_session)

    # 1. Empty dataset
    empty_counts = await repo.get_severity_counts(test_dataset.id)
    assert empty_counts == {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    # 2. Add mixed findings
    findings = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_DROP,
            severity=FindingSeverity.CRITICAL,
            title="Crit 1",
            description="Desc",
            business_impact="Impact",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_CONCENTRATION,
            severity=FindingSeverity.CRITICAL,
            title="Crit 2",
            description="Desc",
            business_impact="Impact",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.HIGH_CANCELLATION_RATE,
            severity=FindingSeverity.HIGH,
            title="High 1",
            description="Desc",
            business_impact="Impact",
        ),
    ]
    await repo.create_many(findings)

    counts = await repo.get_severity_counts(test_dataset.id)
    assert counts["CRITICAL"] == 2
    assert counts["HIGH"] == 1
    assert counts["MEDIUM"] == 0
    assert counts["LOW"] == 0


@pytest.mark.anyio
async def test_delete_dataset_findings(db_session, test_dataset):
    """Test delete_dataset_findings deletes records and returns accurate deleted row count."""
    repo = DiagnosticRepository(db_session)

    findings = [
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.REVENUE_DROP,
            severity=FindingSeverity.CRITICAL,
            title="Crit 1",
            description="Desc",
            business_impact="Impact",
        ),
        DiagnosticFinding(
            dataset_id=test_dataset.id,
            finding_type=FindingType.HIGH_CANCELLATION_RATE,
            severity=FindingSeverity.HIGH,
            title="High 1",
            description="Desc",
            business_impact="Impact",
        ),
    ]
    await repo.create_many(findings)
    assert await repo.get_total_findings(test_dataset.id) == 2

    # First delete -> returns 2
    deleted_count = await repo.delete_dataset_findings(test_dataset.id)
    assert deleted_count == 2
    assert await repo.get_total_findings(test_dataset.id) == 0

    # Second delete -> idempotent, returns 0
    second_delete = await repo.delete_dataset_findings(test_dataset.id)
    assert second_delete == 0
