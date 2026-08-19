"""
Phase 8.5: Scheduled Delivery API Endpoints
"""
from fastapi import APIRouter
from app.delivery.services.delivery_engine import ScheduledDeliveryEngine

router = APIRouter(prefix="/delivery", tags=["Scheduled Delivery"])


@router.get("/schedules")
def get_schedules():
    return {"schedules": ScheduledDeliveryEngine.get_all_schedules()}


@router.post("/schedules/{schedule_id}/test")
def test_delivery(schedule_id: str):
    return ScheduledDeliveryEngine.trigger_test_delivery(schedule_id)
