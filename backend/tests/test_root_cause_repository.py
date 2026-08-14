"""Unit tests for the RootCauseRepository layer."""

import uuid
import pytest

from app.core.constants import FindingSeverity, FindingType, RelationshipStrength, RelationshipType
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.repositories.root_cause_repository import RootCauseRepository


@pytest.fixture
def repo_dataset(db_session, admin_user):
    """Creates a basic Dataset fixture."""
    dataset = Dataset(
        name="Repo Test Dataset",
        original_filename="repo_test.csv",
        stored_filename=f"{uuid.uuid4().hex[:12]}_repo.csv",
        file_path="/tmp/repo.csv",
        file_size=1024,
        uploaded_by=admin_user.id,
    )
    db_session.add(dataset)
    db_session.commit()
    db_session.refresh(dataset)
    return dataset


@pytest.fixture
def repo_findings(db_session, repo_dataset):
    """Creates 3 test findings for repository tests."""
    f1 = DiagnosticFinding(
        dataset_id=repo_dataset.id,
        finding_type=FindingType.DELIVERY_DELAY,
        severity=FindingSeverity.HIGH,
        title="Delivery Delays",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )
    f2 = DiagnosticFinding(
        dataset_id=repo_dataset.id,
        finding_type=FindingType.CUSTOMER_CONCENTRATION,
        severity=FindingSeverity.HIGH,
        title="Customer Churn",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )
    f3 = DiagnosticFinding(
        dataset_id=repo_dataset.id,
        finding_type=FindingType.REVENUE_DROP,
        severity=FindingSeverity.CRITICAL,
        title="Revenue Decline",
        description="...",
        business_impact="...",
        confidence_score=0.90,
    )
    db_session.add_all([f1, f2, f3])
    db_session.commit()
    db_session.refresh(f1)
    db_session.refresh(f2)
    db_session.refresh(f3)
    return f1, f2, f3


@pytest.mark.anyio
async def test_repository_crud_and_eager_loading(db_session, repo_dataset, repo_findings):
    """Verifies creating, retrieving with eager loading, and filtering by dataset."""
    f1, f2, f3 = repo_findings
    repo = RootCauseRepository(db_session)

    # 1. Create
    rca1 = await repo.create(
        dataset_id=repo_dataset.id,
        primary_finding_id=f3.id,
        root_cause_finding_id=f2.id,
        relationship_type=RelationshipType.CAUSES,
        relationship_strength=RelationshipStrength.VERY_STRONG,
        confidence_score=0.92,
        impact_score=0.95,
        explanation="Customer churn caused revenue drop.",
    )
    assert rca1.id is not None

    # 2. Get by ID (eager loading)
    fetched = await repo.get_by_id(rca1.id)
    assert fetched is not None
    assert fetched.primary_finding.title == "Revenue Decline"
    assert fetched.root_cause_finding.title == "Customer Churn"

    # 3. Create second record
    rca2 = await repo.create(
        dataset_id=repo_dataset.id,
        primary_finding_id=f2.id,
        root_cause_finding_id=f1.id,
        relationship_type=RelationshipType.AMPLIFIES,
        relationship_strength=RelationshipStrength.STRONG,
        confidence_score=0.85,
        impact_score=0.80,
        explanation="Delivery delays amplified churn.",
    )

    # 4. Get by dataset (ordered by impact desc)
    dataset_records = await repo.get_by_dataset(repo_dataset.id)
    assert len(dataset_records) == 2
    assert dataset_records[0].impact_score >= dataset_records[1].impact_score

    # 5. Count
    total = await repo.count_by_dataset(repo_dataset.id)
    assert total == 2

    # 6. Delete
    deleted = await repo.delete_by_dataset(repo_dataset.id)
    assert deleted == 2
    assert await repo.count_by_dataset(repo_dataset.id) == 0
