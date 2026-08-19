"""
Phase 8.1: Boardroom Intelligence API Endpoints
"""
from fastapi import APIRouter, Query
from app.boardroom.services.executive_briefing_engine import ExecutiveBriefingEngine
from app.boardroom.services.board_report_generator import BoardReportGenerator, NarrativeSynthesisEngine

router = APIRouter(prefix="/boardroom", tags=["Boardroom Intelligence"])


@router.get("/briefing")
def get_executive_briefing(period: str = Query("Q1 2026")):
    return ExecutiveBriefingEngine.generate_executive_briefing(period)


@router.get("/board-pack")
def get_board_pack(quarter: str = Query("Q1 2026")):
    return BoardReportGenerator.generate_board_pack(quarter)


@router.get("/narrative")
def get_executive_narrative(topic: str = Query("RETENTION_AND_GROWTH")):
    return NarrativeSynthesisEngine.synthesize_narrative(topic)
