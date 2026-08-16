"""Central APIRouter aggregating all v1 sub-routers."""

from fastapi import APIRouter
from app.ai_insights.api import router as ai_insights_router
from app.chat_analyst.api import chat_router
from app.api.v1.endpoints import ai, auth, datasets, health, intelligence, metrics, organizations, recommendations, root_cause
from app.executive_insights.api import executive_insight_router
from app.forecasting.api import router as forecast_router
from app.narratives.api import narrative_router
from app.scenario_simulation.api import router as scenario_router
from app.strategy_planner.api import router as strategy_router
from app.reporting.api import report_router
from app.dashboard.api import dashboard_router
from app.jobs.api import jobs_router

api_router = APIRouter()

# Include endpoints
api_router.include_router(health.router)
api_router.include_router(ai.router, prefix="/ai", tags=["AI Provider Layer"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations & SaaS Tenancy"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(metrics.router, prefix="/datasets", tags=["Metrics"])
api_router.include_router(root_cause.router, tags=["Root Cause Analysis"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(intelligence.router, tags=["Intelligence Layer"])
api_router.include_router(narrative_router, tags=["AI Narrative Engine"])
api_router.include_router(executive_insight_router, tags=["Executive Insights Engine"])
api_router.include_router(ai_insights_router, tags=["AI Insights & Executive Narrative"])
api_router.include_router(chat_router, tags=["AI Chat Analyst"])
api_router.include_router(strategy_router, tags=["AI Strategy Planner"])
api_router.include_router(scenario_router, tags=["Scenario Simulation Engine"])
api_router.include_router(forecast_router, tags=["Forecasting Engine"])
api_router.include_router(report_router, tags=["Executive Report Generation & PDF Export Engine"])
api_router.include_router(dashboard_router, tags=["Executive Dashboard & Intelligence Workspace"])
api_router.include_router(jobs_router, tags=["Background Job Infrastructure"])




