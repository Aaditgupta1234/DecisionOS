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
from app.notifications.api import notifications_router
from app.audit.api import audit_router
from app.schedules.api import schedules_router
from app.monitoring.api import monitoring_router
from app.admin.api import admin_router
from app.portfolio.api import portfolio_router
from app.execution.api.v1.router import execution_router
from app.simulation.api.endpoints import simulation_router
from app.knowledge_graph.api.endpoints import knowledge_graph_router
from app.ai.api.endpoints import ai_analyst_router

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
api_router.include_router(notifications_router, tags=["Notification Framework"])
api_router.include_router(audit_router, tags=["Audit Center"])
api_router.include_router(schedules_router, tags=["Scheduled Intelligence"])
api_router.include_router(monitoring_router, tags=["Operational Monitoring & Health Center"])
api_router.include_router(admin_router, tags=["Platform Administration & Governance Center"])
api_router.include_router(portfolio_router, tags=["Portfolio Intelligence Foundation"])
api_router.include_router(execution_router, tags=["Strategic Execution Layer"])
api_router.include_router(simulation_router, tags=["Enterprise Simulation & Autonomous Planning"])
api_router.include_router(knowledge_graph_router, tags=["Enterprise Knowledge Graph & Causal Intelligence"])
api_router.include_router(ai_analyst_router, tags=["Explainable AI Business Analyst & Decision Copilot"])






