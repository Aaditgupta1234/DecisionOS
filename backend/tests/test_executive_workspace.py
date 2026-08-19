"""Unit tests for Phase 6.1 Executive Intelligence Workspace & Enterprise UX Platform."""

import uuid
import pytest
from app.workspace.services.enterprise_search_engine import EnterpriseSearchEngine
from app.workspace.services.activity_feed_engine import ActivityFeedEngine
from app.workspace.services.report_export_engine import ReportExportEngine
from app.workspace.schemas.workspace_schemas import ReportExportRequest


def test_enterprise_search_engine():
    """Test universal cross-module search across multiple entity types."""
    res = EnterpriseSearchEngine.search("Retention")
    assert res.total_results >= 1
    assert any("Retention" in r.title for r in res.results)

    # Search for an initiative
    init_res = EnterpriseSearchEngine.search("INIT-2026-001")
    assert init_res.total_results >= 1
    assert init_res.results[0].entity_type == "INITIATIVE"
    assert init_res.results[0].deep_link == "/execution"

    # Empty search returns full catalogue
    all_res = EnterpriseSearchEngine.search("")
    assert all_res.total_results == len(EnterpriseSearchEngine.CATALOG)


def test_activity_feed_engine():
    """Test real-time live enterprise event feed generation."""
    portfolio_id = uuid.uuid4()
    feed = ActivityFeedEngine.get_live_feed(portfolio_id)

    assert feed.portfolio_id == portfolio_id
    assert feed.total_events == 5
    assert len(feed.events) == 5

    event_types = {e.event_type for e in feed.events}
    assert "ALERT_TRIGGERED" in event_types
    assert "SIMULATION_COMPLETED" in event_types
    assert "DECISION_APPROVED" in event_types


def test_report_export_engine():
    """Test multi-format boardroom report export job creation."""
    portfolio_id = uuid.uuid4()

    for fmt in ["PDF", "PPTX", "JSON", "CSV"]:
        req = ReportExportRequest(
            portfolio_id=portfolio_id,
            report_type="BOARD_REPORT",
            export_format=fmt,
        )
        job = ReportExportEngine.create_export_job(req)

        assert job.portfolio_id == portfolio_id
        assert job.export_format == fmt
        assert job.export_status == "COMPLETED"
        assert f".{fmt.lower()}" in job.download_url
