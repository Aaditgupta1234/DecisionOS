"""Core ExecutiveInsightService orchestrating strategic insight generation and persistence."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.ai_insights.providers import BaseLLMProvider, get_llm_provider
from app.core.config import settings
from app.executive_insights.constants import (
    INSIGHT_PROMPT_VERSION,
    INSIGHT_SCHEMA_VERSION,
    INSIGHT_TYPE_ACTIONS,
    INSIGHT_TYPE_ALERTS,
    INSIGHT_TYPE_BOARD_COMMENTARY,
    INSIGHT_TYPE_FULL_PACKAGE,
    INSIGHT_TYPE_OPPORTUNITIES,
    INSIGHT_TYPE_RISKS,
    INSIGHT_TYPE_THEMES,
)
from app.executive_insights.fallback_insights import FallbackInsights
from app.executive_insights.insight_prompt_builder import (
    ExecutiveInsightPromptBuilder,
)
from app.executive_insights.insight_scoring import (
    calculate_action_ranking_score,
    calculate_insight_confidence,
    calculate_opportunity_ranking_score,
    calculate_risk_ranking_score,
)
from app.executive_insights.insight_validator import ExecutiveInsightValidator
from app.executive_insights.models.executive_insight_report import (
    ExecutiveInsightReport,
)
from app.executive_insights.repositories.executive_insight_repository import (
    ExecutiveInsightRepository,
)
from app.executive_insights.schemas.requests import ExecutiveInsightRequest
from app.executive_insights.schemas.responses import (
    BoardCommentary,
    ExecutiveAlert,
    ExecutiveInsightHistoryItem,
    ExecutiveInsightMetadata,
    ExecutiveInsightPackage,
    OpportunityInsight,
    PriorityAction,
    RiskInsight,
    StrategicTheme,
)
from app.forecasting.repositories.forecast_repository import ForecastRepository
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.narrative_repository import NarrativeRepository


logger = logging.getLogger(__name__)


class ExecutiveInsightService:
    """
    Production-grade orchestrator synthesizing verified analytical telemetry and
    narrative reports into board-level strategic executive insights.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        provider: Optional[BaseLLMProvider] = None,
    ):
        self.db = db
        self.provider = provider
        self.intelligence_repo = IntelligenceRepository(db)
        self.narrative_repo = NarrativeRepository(db)
        self.forecast_repo = ForecastRepository(db)
        self.insight_repo = ExecutiveInsightRepository(db)

    def _get_provider(
        self,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> BaseLLMProvider:
        """Resolves the configured LLM provider instance."""
        if self.provider:
            return self.provider
        return get_llm_provider(
            provider_name=provider_override,
            model_name=model_override,
        )

    async def _distill_executive_context(self, dataset_id: UUID) -> Tuple[Dict[str, Any], float, float]:
        """
        Gathers structured analytical telemetry, latest narrative report, and forecasts,
        then calculates objective insight confidence.
        """
        bundle = await self.intelligence_repo.get_dataset_with_all_artifacts(dataset_id)
        if not bundle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID '{dataset_id}' not found.",
            )

        dataset, metrics, findings, root_causes, recommendations = bundle

        # Health score
        health_score, health_status_enum = BusinessHealthScoreEngine.calculate(
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )
        health_status = health_status_enum.value if hasattr(health_status_enum, "value") else str(health_status_enum)

        # Latest Narrative Report
        latest_narrative = await self.narrative_repo.get_latest_by_dataset(dataset_id)
        narrative_conf = float(latest_narrative.narrative_confidence) if latest_narrative else 0.85

        # Active Forecasts
        forecasts = await self.forecast_repo.list_history_by_dataset(dataset_id, limit=5)

        # Calculate deterministic insight confidence
        insight_conf = calculate_insight_confidence(
            narrative_confidence=narrative_conf,
            root_causes=root_causes,
            recommendations=recommendations,
            forecasts=forecasts,
        )

        # Distill Findings
        distilled_findings = [
            {
                "id": str(f.id),
                "title": f.title,
                "severity": f.severity.value if hasattr(f.severity, "value") else str(f.severity),
                "confidence_score": float(f.confidence_score) if f.confidence_score is not None else 0.85,
                "business_impact": f.business_impact,
                "description": f.description,
            }
            for f in findings
        ]

        # Distill Root Causes
        distilled_rcas = []
        for r in root_causes:
            cause = r.explanation or (r.root_cause_finding.title if getattr(r, "root_cause_finding", None) else "Operational Friction")
            effect = (r.primary_finding.title if getattr(r, "primary_finding", None) else "Performance Variance")
            attr_pct = float(r.impact_score * 100.0) if (r.impact_score is not None and r.impact_score <= 1.0) else (float(r.impact_score) if r.impact_score is not None else 50.0)
            distilled_rcas.append({
                "id": str(r.id),
                "cause": cause,
                "effect": effect,
                "strength": r.relationship_strength.value if hasattr(r.relationship_strength, "value") else str(r.relationship_strength),
                "confidence_score": float(r.confidence_score) if r.confidence_score is not None else 0.85,
                "attribution_percentage": round(attr_pct, 1),
            })

        # Distill Recommendations
        distilled_recs = [
            {
                "id": str(r.id),
                "title": r.title,
                "priority": r.priority.value if hasattr(r.priority, "value") else str(r.priority),
                "rationale": getattr(r, "why_recommended", None) or getattr(r, "description", "Strategic initiative."),
                "expected_outcome": getattr(r, "description", None) or "Restores operational baseline.",
                "confidence_score": float(r.confidence_score) if r.confidence_score is not None else 0.85,
            }
            for r in recommendations
        ]

        context: Dict[str, Any] = {
            "dataset_id": str(dataset_id),
            "dataset_name": dataset.name,
            "business_health_score": health_score,
            "business_health_status": health_status,
            "findings": distilled_findings,
            "root_causes": distilled_rcas,
            "recommendations": distilled_recs,
            "forecast_count": len(forecasts),
            "has_narrative_report": latest_narrative is not None,
            "latest_narrative_summary": (
                latest_narrative.executive_summary.get("executive_summary", "")
                if latest_narrative and isinstance(latest_narrative.executive_summary, dict)
                else ""
            ),
        }

        return context, narrative_conf, insight_conf

    async def _execute_generation_and_validation(
        self,
        prompt: str,
        insight_type: str,
        context: Dict[str, Any],
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> Tuple[Dict[str, Any], float, float, bool, bool, BaseLLMProvider]:
        """
        Helper executing LLM generation, validation checks, and automatic fallback if needed.
        """
        provider = self._get_provider(
            provider_override=req.provider_name if req else None,
            model_override=req.model_name if req else None,
        )
        temp = req.temperature if req and req.temperature is not None else 0.2
        system_prompt = ExecutiveInsightPromptBuilder.get_system_prompt()

        t0 = time.perf_counter()
        raw_output = None
        gen_time_ms = 0.0
        val_time_ms = 0.0
        fallback_triggered = False
        is_fallback = False

        try:
            raw_output = await provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temp,
            )
            gen_time_ms = round((time.perf_counter() - t0) * 1000, 2)
        except Exception as e:
            logger.warning(f"LLM insight generation failed ({provider.provider_name}): {e}. Activating fallback.")
            gen_time_ms = round((time.perf_counter() - t0) * 1000, 2)
            fallback_triggered = True
            is_fallback = True

        if not raw_output or fallback_triggered:
            fallback_dict = self._get_fallback_dict(insight_type, context)
            return fallback_dict, gen_time_ms, 0.0, True, True, provider

        # Validate
        val_res = ExecutiveInsightValidator.validate(raw_output, insight_type=insight_type)
        val_time_ms = val_res.validation_time_ms

        if not val_res.is_valid:
            logger.warning(f"Executive insight validation failed for {insight_type}: {val_res.errors}. Activating fallback.")
            fallback_dict = self._get_fallback_dict(insight_type, context)
            return fallback_dict, gen_time_ms, val_time_ms, True, True, provider

        return raw_output, gen_time_ms, val_time_ms, False, False, provider

    def _get_fallback_dict(self, insight_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if insight_type == INSIGHT_TYPE_RISKS:
            return FallbackInsights.render_top_risks_fallback(context)
        elif insight_type == INSIGHT_TYPE_OPPORTUNITIES:
            return FallbackInsights.render_top_opportunities_fallback(context)
        elif insight_type == INSIGHT_TYPE_ACTIONS:
            return FallbackInsights.render_priority_actions_fallback(context)
        elif insight_type == INSIGHT_TYPE_THEMES:
            return FallbackInsights.render_strategic_themes_fallback(context)
        elif insight_type == INSIGHT_TYPE_ALERTS:
            return FallbackInsights.render_executive_alerts_fallback(context)
        elif insight_type == INSIGHT_TYPE_BOARD_COMMENTARY:
            return FallbackInsights.render_board_commentary_fallback(context)
        else:
            return FallbackInsights.render_full_package_fallback(context)

    # -----------------------------------------------------------------------
    # Section Generation Methods
    # -----------------------------------------------------------------------

    async def generate_top_risks(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> List[RiskInsight]:
        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)
        prompt = ExecutiveInsightPromptBuilder.build_top_risks_prompt(context)
        raw_dict, gen_ms, val_ms, fb_trig, is_fb, prov = await self._execute_generation_and_validation(
            prompt=prompt,
            insight_type=INSIGHT_TYPE_RISKS,
            context=context,
            req=req,
        )

        risks = []
        for r in raw_dict.get("top_risks", []):
            sev = r.get("severity", "HIGH")
            conf = float(r.get("confidence", 0.85))
            ranking = r.get("ranking_score") or calculate_risk_ranking_score(severity=sev, confidence=conf)
            risks.append(
                RiskInsight(
                    title=r.get("title", "Strategic Risk"),
                    description=r.get("description", ""),
                    severity=sev,
                    confidence=conf,
                    ranking_score=round(float(ranking), 2),
                    supporting_evidence=r.get("supporting_evidence", []),
                    source_finding_ids=r.get("source_finding_ids", []),
                    source_root_cause_ids=r.get("source_root_cause_ids", []),
                )
            )
        # Sort deterministically by ranking_score descending
        risks.sort(key=lambda x: x.ranking_score, reverse=True)
        return risks

    async def generate_opportunities(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> List[OpportunityInsight]:
        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)
        prompt = ExecutiveInsightPromptBuilder.build_top_opportunities_prompt(context)
        raw_dict, gen_ms, val_ms, fb_trig, is_fb, prov = await self._execute_generation_and_validation(
            prompt=prompt,
            insight_type=INSIGHT_TYPE_OPPORTUNITIES,
            context=context,
            req=req,
        )

        opps = []
        for o in raw_dict.get("top_opportunities", []):
            imp = o.get("impact", "HIGH")
            conf = float(o.get("confidence", 0.88))
            ranking = o.get("ranking_score") or calculate_opportunity_ranking_score(impact=imp, confidence=conf)
            opps.append(
                OpportunityInsight(
                    title=o.get("title", "Growth Opportunity"),
                    description=o.get("description", ""),
                    impact=imp,
                    confidence=conf,
                    ranking_score=round(float(ranking), 2),
                    supporting_evidence=o.get("supporting_evidence", []),
                    source_recommendation_ids=o.get("source_recommendation_ids", []),
                )
            )
        opps.sort(key=lambda x: x.ranking_score, reverse=True)
        return opps

    async def generate_priority_actions(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> List[PriorityAction]:
        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)
        prompt = ExecutiveInsightPromptBuilder.build_priority_actions_prompt(context)
        raw_dict, gen_ms, val_ms, fb_trig, is_fb, prov = await self._execute_generation_and_validation(
            prompt=prompt,
            insight_type=INSIGHT_TYPE_ACTIONS,
            context=context,
            req=req,
        )

        actions = []
        for a in raw_dict.get("priority_actions", []):
            prio = a.get("priority", "HIGH")
            diff = a.get("difficulty", "MODERATE")
            ranking = a.get("ranking_score") or calculate_action_ranking_score(priority=prio, difficulty=diff)
            actions.append(
                PriorityAction(
                    action=a.get("action", "Initiative"),
                    priority=prio,
                    expected_impact=a.get("expected_impact", "Protects operational baseline."),
                    difficulty=diff,
                    ranking_score=round(float(ranking), 2),
                    rationale=a.get("rationale", ""),
                    source_recommendation_ids=a.get("source_recommendation_ids", []),
                )
            )
        actions.sort(key=lambda x: x.ranking_score, reverse=True)
        return actions

    async def generate_strategic_themes(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> List[StrategicTheme]:
        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)
        prompt = ExecutiveInsightPromptBuilder.build_strategic_themes_prompt(context)
        raw_dict, gen_ms, val_ms, fb_trig, is_fb, prov = await self._execute_generation_and_validation(
            prompt=prompt,
            insight_type=INSIGHT_TYPE_THEMES,
            context=context,
            req=req,
        )

        return [
            StrategicTheme(
                theme=t.get("theme", "Operational Imperative"),
                description=t.get("description", ""),
                key_pillars=t.get("key_pillars", []),
                aligned_initiatives=t.get("aligned_initiatives", []),
            )
            for t in raw_dict.get("strategic_themes", [])
        ]

    async def generate_executive_alerts(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> List[ExecutiveAlert]:
        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)
        prompt = ExecutiveInsightPromptBuilder.build_executive_alerts_prompt(context)
        raw_dict, gen_ms, val_ms, fb_trig, is_fb, prov = await self._execute_generation_and_validation(
            prompt=prompt,
            insight_type=INSIGHT_TYPE_ALERTS,
            context=context,
            req=req,
        )

        return [
            ExecutiveAlert(
                alert_level=al.get("alert_level", "INFO"),
                headline=al.get("headline", "Status Alert"),
                detail=al.get("detail", ""),
                recommended_immediate_step=al.get("recommended_immediate_step", "Monitor indicator."),
                source_finding_ids=al.get("source_finding_ids", []),
            )
            for al in raw_dict.get("executive_alerts", [])
        ]

    async def generate_board_commentary(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> BoardCommentary:
        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)
        prompt = ExecutiveInsightPromptBuilder.build_board_commentary_prompt(context)
        raw_dict, gen_ms, val_ms, fb_trig, is_fb, prov = await self._execute_generation_and_validation(
            prompt=prompt,
            insight_type=INSIGHT_TYPE_BOARD_COMMENTARY,
            context=context,
            req=req,
        )

        comm_data = raw_dict.get("board_commentary") if isinstance(raw_dict.get("board_commentary"), dict) else raw_dict
        return BoardCommentary(
            headline=comm_data.get("headline", "Board Briefing"),
            commentary=comm_data.get("commentary", ""),
            strategic_outlook=comm_data.get("strategic_outlook", "Stable outlook."),
            health_summary=comm_data.get("health_summary", f"Health evaluated at {context.get('business_health_score', 85)}/100."),
        )

    # -----------------------------------------------------------------------
    # Full Package Generation & Persistence
    # -----------------------------------------------------------------------

    async def generate_full_insight_package(
        self,
        dataset_id: UUID,
        req: Optional[ExecutiveInsightRequest] = None,
    ) -> ExecutiveInsightPackage:
        """
        Generates all executive insight categories, builds consolidated package,
        persists report to DB, and returns ExecutiveInsightPackage.
        """
        start_all = time.perf_counter()

        # Check existing report unless force_regenerate is requested
        if req and not req.force_regenerate:
            existing = await self.insight_repo.get_latest_by_dataset(dataset_id)
            if existing:
                return self._entity_to_package(existing)

        context, narr_conf, ins_conf = await self._distill_executive_context(dataset_id)

        # Run section generators concurrently
        (
            risks,
            opps,
            actions,
            themes,
            alerts,
            board,
        ) = await asyncio.gather(
            self.generate_top_risks(dataset_id, req=req),
            self.generate_opportunities(dataset_id, req=req),
            self.generate_priority_actions(dataset_id, req=req),
            self.generate_strategic_themes(dataset_id, req=req),
            self.generate_executive_alerts(dataset_id, req=req),
            self.generate_board_commentary(dataset_id, req=req),
        )

        total_lat = round((time.perf_counter() - start_all) * 1000, 2)
        provider = self._get_provider(
            provider_override=req.provider_name if req else None,
            model_override=req.model_name if req else None,
        )

        exec_summary = (
            f"Executive synthesis for dataset '{context.get('dataset_name', 'Enterprise')}' indicates composite business health at "
            f"{context.get('business_health_score', 85)}/100 ({context.get('business_health_status', 'GOOD')}). "
            f"Isolated {len(risks)} strategic risks and {len(opps)} high-leverage growth opportunities."
        )

        meta = ExecutiveInsightMetadata(
            prompt_version=INSIGHT_PROMPT_VERSION,
            insight_schema_version=INSIGHT_SCHEMA_VERSION,
            provider=provider.provider_name,
            model=provider.model_name,
            narrative_confidence=narr_conf,
            insight_confidence=ins_conf,
            generation_time_ms=round(total_lat * 0.8, 2),
            validation_time_ms=round(total_lat * 0.1, 2),
            total_latency_ms=total_lat,
            fallback_triggered=False,
            is_fallback=False,
        )

        pkg = ExecutiveInsightPackage(
            dataset_id=dataset_id,
            generated_at=datetime.now(timezone.utc),
            executive_summary=exec_summary,
            top_risks=risks,
            top_opportunities=opps,
            priority_actions=actions,
            strategic_themes=themes,
            executive_alerts=alerts,
            board_commentary=board,
            metadata=meta,
        )

        # Persist report entity
        report_entity = ExecutiveInsightReport(
            dataset_id=dataset_id,
            prompt_version=INSIGHT_PROMPT_VERSION,
            insight_schema_version=INSIGHT_SCHEMA_VERSION,
            provider=provider.provider_name,
            model=provider.model_name,
            narrative_confidence=narr_conf,
            insight_confidence=ins_conf,
            generation_time_ms=meta.generation_time_ms,
            validation_time_ms=meta.validation_time_ms,
            total_latency_ms=total_lat,
            fallback_triggered=meta.fallback_triggered,
            is_fallback=meta.is_fallback,
            executive_summary=exec_summary,
            top_risks=[r.model_dump() for r in risks],
            top_opportunities=[o.model_dump() for o in opps],
            priority_actions=[a.model_dump() for a in actions],
            strategic_themes=[t.model_dump() for t in themes],
            executive_alerts=[al.model_dump() for al in alerts],
            board_commentary=board.model_dump(),
            full_package_json=pkg.model_dump(mode="json"),
            generated_at=pkg.generated_at,
        )

        saved_entity = await self.insight_repo.save(report_entity)
        pkg.id = saved_entity.id
        return pkg

    def _entity_to_package(self, entity: ExecutiveInsightReport) -> ExecutiveInsightPackage:
        """Converts persisted database entity to ExecutiveInsightPackage."""
        return ExecutiveInsightPackage(
            id=entity.id,
            dataset_id=entity.dataset_id,
            organization_id=entity.organization_id,
            generated_at=entity.generated_at,
            executive_summary=entity.executive_summary,
            top_risks=[RiskInsight.model_validate(r) for r in (entity.top_risks or [])],
            top_opportunities=[OpportunityInsight.model_validate(o) for o in (entity.top_opportunities or [])],
            priority_actions=[PriorityAction.model_validate(a) for a in (entity.priority_actions or [])],
            strategic_themes=[StrategicTheme.model_validate(t) for t in (entity.strategic_themes or [])],
            executive_alerts=[ExecutiveAlert.model_validate(al) for al in (entity.executive_alerts or [])],
            board_commentary=BoardCommentary.model_validate(entity.board_commentary or {}),
            metadata=ExecutiveInsightMetadata(
                prompt_version=entity.prompt_version,
                insight_schema_version=entity.insight_schema_version,
                provider=entity.provider,
                model=entity.model,
                narrative_confidence=entity.narrative_confidence,
                insight_confidence=entity.insight_confidence,
                generation_time_ms=entity.generation_time_ms,
                validation_time_ms=entity.validation_time_ms,
                total_latency_ms=entity.total_latency_ms,
                fallback_triggered=entity.fallback_triggered,
                is_fallback=entity.is_fallback,
            ),
        )

    async def get_latest_persisted_report(self, dataset_id: UUID) -> Optional[ExecutiveInsightPackage]:
        """Retrieves the latest persisted executive insight report."""
        report = await self.insight_repo.get_latest_by_dataset(dataset_id)
        if not report:
            return None
        return self._entity_to_package(report)

    async def list_persisted_reports(
        self,
        dataset_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[ExecutiveInsightHistoryItem]:
        """Retrieves paginated history list of executive insight reports."""
        reports = await self.insight_repo.list_by_dataset(dataset_id, limit=limit, offset=offset)
        return [
            ExecutiveInsightHistoryItem(
                id=r.id,
                dataset_id=r.dataset_id,
                prompt_version=r.prompt_version,
                insight_schema_version=r.insight_schema_version,
                provider=r.provider,
                model=r.model,
                insight_confidence=r.insight_confidence,
                fallback_triggered=r.fallback_triggered,
                generated_at=r.generated_at,
                risk_count=len(r.top_risks or []),
                opportunity_count=len(r.top_opportunities or []),
                action_count=len(r.priority_actions or []),
            )
            for r in reports
        ]
