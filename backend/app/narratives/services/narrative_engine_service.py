"""Business service layer for the Phase 9.2 AI Narrative Engine."""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.ai_insights.providers import BaseLLMProvider, get_llm_provider
from app.intelligence.health_score import BusinessHealthScoreEngine
from app.models.narrative_report import NarrativeReport
from app.narratives.builders.narrative_prompt_builder import NarrativePromptBuilder
from app.narratives.constants import (
    DEFAULT_TEMPERATURE,
    NARRATIVE_PROMPT_VERSION,
    NARRATIVE_TYPE_EXECUTIVE,
    NARRATIVE_TYPE_FORECAST,
    NARRATIVE_TYPE_FULL_PACKAGE,
    NARRATIVE_TYPE_KPI,
    NARRATIVE_TYPE_RECOMMENDATION,
    NARRATIVE_TYPE_ROOT_CAUSE,
    NARRATIVE_TYPE_SCENARIO,
)
from app.narratives.schemas.narrative_schema import (
    DatasetNarrativePackageResponse,
    ExecutiveNarrativeResponse,
    ForecastNarrativeRequest,
    ForecastNarrativeResponse,
    KPINarrativeResponse,
    NarrativeGenerateRequest,
    NarrativeMetadata,
    NarrativeReportHistoryItem,
    RecommendationNarrativeResponse,
    RootCauseNarrativeResponse,
    ScenarioNarrativeRequest,
    ScenarioNarrativeResponse,
)
from app.narratives.scoring import calculate_narrative_confidence
from app.narratives.templates.fallback_templates import FallbackTemplates
from app.narratives.validation.narrative_validator import NarrativeValidator, ValidationResult
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.narrative_repository import NarrativeRepository

logger = logging.getLogger(__name__)


class NarrativeEngineService:
    """
    Coordinates analytical context extraction, prompt formulation, LLM execution,
    output validation, fallback activation, and report persistence for executive narratives.
    """

    def __init__(
        self,
        db: Union[AsyncSession, Session],
        provider: Optional[BaseLLMProvider] = None,
    ):
        self.db = db
        self.intel_repo = IntelligenceRepository(db)
        self.narrative_repo = NarrativeRepository(db)
        self._provider = provider

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    def _get_provider(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> BaseLLMProvider:
        """Resolves LLM provider instance from factory or injected provider."""
        if self._provider:
            return self._provider
        return get_llm_provider(provider_name=provider_name, model_name=model_name)

    async def _distill_base_context(
        self,
        dataset_id: uuid.UUID,
    ) -> Tuple[Dict[str, Any], float]:
        """
        Retrieves all computed KPIs, findings, root causes, and recommendations for the dataset,
        computes the health score and deterministic confidence score, and returns a distilled context dict.
        """
        result = await self.intel_repo.get_dataset_with_all_artifacts(dataset_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )

        dataset, metrics, findings, root_causes, recommendations = result

        health_score, health_status = BusinessHealthScoreEngine.calculate(
            findings=findings,
            root_causes=root_causes,
            recommendations=recommendations,
        )

        confidence = calculate_narrative_confidence(
            findings=findings,
            root_causes=root_causes,
            health_score=health_score,
        )

        # Distill Metrics
        distilled_metrics = []
        for m in metrics:
            val = 0.0
            if hasattr(m, "metric_value") and m.metric_value is not None:
                if isinstance(m.metric_value, (int, float)):
                    val = float(m.metric_value)
                elif isinstance(m.metric_value, dict):
                    val = float(m.metric_value.get("current_value") or m.metric_value.get("value") or 0.0)
            elif hasattr(m, "current_value") and m.current_value is not None:
                val = float(m.current_value)

            cat = "OPERATIONAL"
            if hasattr(m, "metric_category") and m.metric_category:
                cat = m.metric_category.value if hasattr(m.metric_category, "value") else str(m.metric_category)
            elif m.metric_definition and hasattr(m.metric_definition, "metric_category"):
                cat = m.metric_definition.metric_category.value if hasattr(m.metric_definition.metric_category, "value") else str(m.metric_definition.metric_category)

            name = getattr(m, "metric_name", None) or (m.metric_definition.name if m.metric_definition else m.metric_key)

            distilled_metrics.append({
                "name": name,
                "metric_key": m.metric_key,
                "category": cat,
                "value": val,
            })


        # Distill Findings
        distilled_findings = [
            {
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
                "cause": cause,
                "effect": effect,
                "strength": r.relationship_strength.value if hasattr(r.relationship_strength, "value") else str(r.relationship_strength),
                "confidence_score": float(r.confidence_score) if r.confidence_score is not None else 0.85,
                "attribution_percentage": round(attr_pct, 1),
            })


        # Distill Recommendations
        distilled_recs = [
            {
                "title": r.title,
                "priority": r.priority.value if hasattr(r.priority, "value") else str(r.priority),
                "rationale": getattr(r, "why_recommended", None) or getattr(r, "description", "Strategic initiative prioritized by rule engine."),
                "expected_outcome": getattr(r, "description", None) or "Restores operational margin and growth.",
            }
            for r in recommendations
        ]


        context: Dict[str, Any] = {
            "dataset_id": str(dataset_id),
            "dataset_name": dataset.name,
            "business_health_score": health_score,
            "business_health_status": health_status.value if hasattr(health_status, "value") else str(health_status),
            "metrics": distilled_metrics,
            "findings": distilled_findings,
            "root_causes": distilled_rcas,
            "recommendations": distilled_recs,
        }

        return context, confidence

    async def _execute_narrative_generation(
        self,
        prompt: str,
        context: Dict[str, Any],
        narrative_type: str,
        confidence: float,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> Tuple[Dict[str, Any], NarrativeMetadata]:
        """
        Executes LLM generation with timing, schema validation, and fallback template activation.
        """
        provider = self._get_provider(provider_name=provider_name, model_name=model_name)
        system_prompt = NarrativePromptBuilder.get_system_prompt()
        temp = temperature if temperature is not None else DEFAULT_TEMPERATURE

        overall_start_ts = time.monotonic()
        gen_start_ts = time.monotonic()
        gen_time_ms = 0.0
        val_time_ms = 0.0
        fallback_triggered = False
        raw_output: Optional[Dict[str, Any]] = None

        logger.info(
            "[NarrativeEngine] Generating %s narrative via provider=%s model=%s",
            narrative_type,
            provider.provider_name,
            provider.model_name,
        )

        try:
            raw_output = await provider.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temp,
            )
            gen_time_ms = round((time.monotonic() - gen_start_ts) * 1000, 2)

            # Validate output
            val_result = NarrativeValidator.validate(
                data=raw_output,
                context=context,
                narrative_type=narrative_type,
            )
            val_time_ms = val_result.validation_time_ms

            if not val_result.is_valid:
                logger.warning(
                    "[NarrativeEngine] Output validation failed for %s: %s. Activating fallback.",
                    narrative_type,
                    val_result.errors,
                )
                fallback_triggered = True

        except Exception as exc:
            gen_time_ms = round((time.monotonic() - gen_start_ts) * 1000, 2)
            logger.error(
                "[NarrativeEngine] LLM generation error on %s: %s. Activating fallback.",
                narrative_type,
                exc,
            )
            fallback_triggered = True

        # Render fallback if needed
        if fallback_triggered or raw_output is None:
            raw_output = self._render_fallback_by_type(narrative_type, context)

        total_latency_ms = round((time.monotonic() - overall_start_ts) * 1000, 2)

        # Compute word count of primary prose
        primary_text = raw_output.get("executive_summary") or raw_output.get("summary") or ""
        word_count = len(str(primary_text).split())

        metadata = NarrativeMetadata(
            prompt_version=NARRATIVE_PROMPT_VERSION,
            provider=provider.provider_name,
            model=provider.model_name,
            narrative_confidence=confidence,
            generation_time_ms=gen_time_ms,
            validation_time_ms=val_time_ms,
            total_latency_ms=total_latency_ms,
            fallback_triggered=fallback_triggered,
            is_fallback=fallback_triggered,
            word_count=word_count,
            generated_at=datetime.now(timezone.utc),
        )

        return raw_output, metadata

    def _render_fallback_by_type(self, narrative_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Routes to the appropriate deterministic fallback renderer."""
        if narrative_type == NARRATIVE_TYPE_EXECUTIVE:
            return FallbackTemplates.render_executive_summary_fallback(context)
        if narrative_type == NARRATIVE_TYPE_KPI:
            return FallbackTemplates.render_kpi_fallback(context)
        if narrative_type == NARRATIVE_TYPE_ROOT_CAUSE:
            return FallbackTemplates.render_root_cause_fallback(context)
        if narrative_type == NARRATIVE_TYPE_RECOMMENDATION:
            return FallbackTemplates.render_recommendation_fallback(context)
        if narrative_type == NARRATIVE_TYPE_FORECAST:
            return FallbackTemplates.render_forecast_fallback(context)
        if narrative_type == NARRATIVE_TYPE_SCENARIO:
            return FallbackTemplates.render_scenario_fallback(context)
        return FallbackTemplates.render_executive_summary_fallback(context)

    # -----------------------------------------------------------------------
    # Public Narrative Methods
    # -----------------------------------------------------------------------

    async def get_executive_narrative(
        self,
        dataset_id: uuid.UUID,
        req: Optional[NarrativeGenerateRequest] = None,
    ) -> ExecutiveNarrativeResponse:
        """Synthesizes executive briefing narrative."""
        context, confidence = await self._distill_base_context(dataset_id)
        if req and req.focus_areas:
            context["focus_areas"] = req.focus_areas

        prompt = NarrativePromptBuilder.build_executive_summary_prompt(context)
        payload, metadata = await self._execute_narrative_generation(
            prompt=prompt,
            context=context,
            narrative_type=NARRATIVE_TYPE_EXECUTIVE,
            confidence=confidence,
            provider_name=req.provider if req else None,
            model_name=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        return ExecutiveNarrativeResponse(
            dataset_id=dataset_id,
            headline=payload.get("headline", "Executive Performance Summary"),
            executive_summary=payload.get("executive_summary", ""),
            health_assessment=payload.get("health_assessment", ""),
            key_takeaways=payload.get("key_takeaways", []),
            primary_risk=payload.get("primary_risk"),
            recommended_focus=payload.get("recommended_focus"),
            metadata=metadata,
        )

    async def get_kpi_narrative(
        self,
        dataset_id: uuid.UUID,
        req: Optional[NarrativeGenerateRequest] = None,
    ) -> KPINarrativeResponse:
        """Synthesizes KPI performance narrative."""
        context, confidence = await self._distill_base_context(dataset_id)
        if req and req.focus_areas:
            context["focus_areas"] = req.focus_areas

        prompt = NarrativePromptBuilder.build_kpi_prompt(context)
        payload, metadata = await self._execute_narrative_generation(
            prompt=prompt,
            context=context,
            narrative_type=NARRATIVE_TYPE_KPI,
            confidence=confidence,
            provider_name=req.provider if req else None,
            model_name=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        return KPINarrativeResponse(
            dataset_id=dataset_id,
            summary=payload.get("summary", ""),
            metric_highlights=payload.get("metric_highlights", []),
            anomaly_commentary=payload.get("anomaly_commentary"),
            stability_assessment=payload.get("stability_assessment", "STABLE"),
            metadata=metadata,
        )

    async def get_root_cause_narrative(
        self,
        dataset_id: uuid.UUID,
        req: Optional[NarrativeGenerateRequest] = None,
    ) -> RootCauseNarrativeResponse:
        """Synthesizes root-cause narrative."""
        context, confidence = await self._distill_base_context(dataset_id)
        if req and req.focus_areas:
            context["focus_areas"] = req.focus_areas

        prompt = NarrativePromptBuilder.build_root_cause_prompt(context)
        payload, metadata = await self._execute_narrative_generation(
            prompt=prompt,
            context=context,
            narrative_type=NARRATIVE_TYPE_ROOT_CAUSE,
            confidence=confidence,
            provider_name=req.provider if req else None,
            model_name=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        return RootCauseNarrativeResponse(
            dataset_id=dataset_id,
            summary=payload.get("summary", ""),
            primary_drivers=payload.get("primary_drivers", []),
            causal_chain_narrative=payload.get("causal_chain_narrative", ""),
            attribution_breakdown=payload.get("attribution_breakdown", []),
            metadata=metadata,
        )

    async def get_recommendation_narrative(
        self,
        dataset_id: uuid.UUID,
        req: Optional[NarrativeGenerateRequest] = None,
    ) -> RecommendationNarrativeResponse:
        """Synthesizes strategic recommendations narrative."""
        context, confidence = await self._distill_base_context(dataset_id)
        if req and req.focus_areas:
            context["focus_areas"] = req.focus_areas

        prompt = NarrativePromptBuilder.build_recommendation_prompt(context)
        payload, metadata = await self._execute_narrative_generation(
            prompt=prompt,
            context=context,
            narrative_type=NARRATIVE_TYPE_RECOMMENDATION,
            confidence=confidence,
            provider_name=req.provider if req else None,
            model_name=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        return RecommendationNarrativeResponse(
            dataset_id=dataset_id,
            summary=payload.get("summary", ""),
            priority_actions=payload.get("priority_actions", []),
            expected_impact_narrative=payload.get("expected_impact_narrative", ""),
            time_to_value_summary=payload.get("time_to_value_summary", ""),
            metadata=metadata,
        )

    async def get_forecast_narrative(
        self,
        dataset_id: uuid.UUID,
        req: Optional[ForecastNarrativeRequest] = None,
    ) -> ForecastNarrativeResponse:
        """Synthesizes time-series forecast explanation narrative."""
        context, confidence = await self._distill_base_context(dataset_id)
        context["metric_key"] = req.metric_key if (req and req.metric_key) else "primary_revenue"
        context["trend_direction"] = "STABLE"
        context["horizon_steps"] = 3

        prompt = NarrativePromptBuilder.build_forecast_prompt(context)
        payload, metadata = await self._execute_narrative_generation(
            prompt=prompt,
            context=context,
            narrative_type=NARRATIVE_TYPE_FORECAST,
            confidence=confidence,
            provider_name=req.provider if req else None,
            model_name=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        return ForecastNarrativeResponse(
            dataset_id=dataset_id,
            forecast_id=req.forecast_id if req else None,
            metric_key=req.metric_key if req else None,
            summary=payload.get("summary", ""),
            trend_direction=payload.get("trend_direction", "STABLE"),
            horizon_commentary=payload.get("horizon_commentary", ""),
            confidence_assessment=payload.get("confidence_assessment", ""),
            risk_warnings=payload.get("risk_warnings", []),
            metadata=metadata,
        )

    async def get_scenario_narrative(
        self,
        dataset_id: uuid.UUID,
        req: Optional[ScenarioNarrativeRequest] = None,
    ) -> ScenarioNarrativeResponse:
        """Synthesizes scenario simulation narrative."""
        context, confidence = await self._distill_base_context(dataset_id)
        context["scenario_name"] = "Target Optimization Scenario"
        context["adjustment_type"] = "PERCENTAGE"
        context["adjustment_value"] = 10.0

        prompt = NarrativePromptBuilder.build_scenario_prompt(context)
        payload, metadata = await self._execute_narrative_generation(
            prompt=prompt,
            context=context,
            narrative_type=NARRATIVE_TYPE_SCENARIO,
            confidence=confidence,
            provider_name=req.provider if req else None,
            model_name=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        return ScenarioNarrativeResponse(
            dataset_id=dataset_id,
            scenario_id=req.scenario_id if req else None,
            summary=payload.get("summary", ""),
            baseline_vs_scenario_comparison=payload.get("baseline_vs_scenario_comparison", ""),
            sensitivity_insights=payload.get("sensitivity_insights", []),
            strategic_implications=payload.get("strategic_implications", ""),
            metadata=metadata,
        )

    # -----------------------------------------------------------------------
    # Consolidated Full Package & Persistence
    # -----------------------------------------------------------------------

    async def generate_and_persist_full_package(
        self,
        dataset_id: uuid.UUID,
        req: Optional[NarrativeGenerateRequest] = None,
    ) -> DatasetNarrativePackageResponse:
        """
        Executes concurrent generation across all narrative perspectives,
        constructs a complete NarrativeReport record, persists it to the database,
        and returns the consolidated package response.
        """
        # 1. Check if cached report exists and force_regenerate is False
        if req and not req.force_regenerate:
            cached = await self.get_latest_persisted_report(dataset_id)
            if cached is not None:
                return cached

        # 2. Execute narrative components concurrently
        start_ts = time.monotonic()
        exec_res, kpi_res, rca_res, rec_res = await asyncio.gather(
            self.get_executive_narrative(dataset_id, req),
            self.get_kpi_narrative(dataset_id, req),
            self.get_root_cause_narrative(dataset_id, req),
            self.get_recommendation_narrative(dataset_id, req),
        )

        forecast_req = ForecastNarrativeRequest(
            provider=req.provider if req else None,
            model=req.model if req else None,
            temperature=req.temperature if req else None,
        )
        scenario_req = ScenarioNarrativeRequest(
            provider=req.provider if req else None,
            model=req.model if req else None,
            temperature=req.temperature if req else None,
        )

        fc_res, sc_res = await asyncio.gather(
            self.get_forecast_narrative(dataset_id, forecast_req),
            self.get_scenario_narrative(dataset_id, scenario_req),
        )

        total_latency = round((time.monotonic() - start_ts) * 1000, 2)
        total_gen_time = round(
            exec_res.metadata.generation_time_ms
            + kpi_res.metadata.generation_time_ms
            + rca_res.metadata.generation_time_ms
            + rec_res.metadata.generation_time_ms,
            2,
        )
        total_val_time = round(
            exec_res.metadata.validation_time_ms
            + kpi_res.metadata.validation_time_ms
            + rca_res.metadata.validation_time_ms
            + rec_res.metadata.validation_time_ms,
            2,
        )
        total_words = (
            exec_res.metadata.word_count
            + kpi_res.metadata.word_count
            + rca_res.metadata.word_count
            + rec_res.metadata.word_count
        )
        any_fallback = (
            exec_res.metadata.is_fallback
            or kpi_res.metadata.is_fallback
            or rca_res.metadata.is_fallback
            or rec_res.metadata.is_fallback
        )

        pkg_metadata = NarrativeMetadata(
            prompt_version=NARRATIVE_PROMPT_VERSION,
            provider=exec_res.metadata.provider,
            model=exec_res.metadata.model,
            narrative_confidence=exec_res.metadata.narrative_confidence,
            generation_time_ms=total_gen_time,
            validation_time_ms=total_val_time,
            total_latency_ms=total_latency,
            fallback_triggered=any_fallback,
            is_fallback=any_fallback,
            word_count=total_words,
            generated_at=datetime.now(timezone.utc),
        )

        report_id = uuid.uuid4()

        # 3. Construct NarrativeReport entity
        report_entity = NarrativeReport(
            id=report_id,
            dataset_id=dataset_id,
            prompt_version=NARRATIVE_PROMPT_VERSION,
            provider=exec_res.metadata.provider,
            model=exec_res.metadata.model,
            narrative_confidence=exec_res.metadata.narrative_confidence,
            generation_time_ms=total_gen_time,
            validation_time_ms=total_val_time,
            total_latency_ms=total_latency,
            fallback_triggered=any_fallback,
            is_fallback=any_fallback,
            executive_summary=exec_res.model_dump(mode="json"),
            kpi_narrative=kpi_res.model_dump(mode="json"),
            root_cause_narrative=rca_res.model_dump(mode="json"),
            recommendation_narrative=rec_res.model_dump(mode="json"),
            forecast_narrative=fc_res.model_dump(mode="json"),
            scenario_narrative=sc_res.model_dump(mode="json"),
            full_package_json={
                "executive_summary": exec_res.model_dump(mode="json"),
                "kpis": kpi_res.model_dump(mode="json"),
                "root_causes": rca_res.model_dump(mode="json"),
                "recommendations": rec_res.model_dump(mode="json"),
                "forecasts": fc_res.model_dump(mode="json"),
                "scenarios": sc_res.model_dump(mode="json"),
            },
            generated_at=datetime.now(timezone.utc),
        )

        # Persist to database
        await self.narrative_repo.save(report_entity)
        logger.info(
            "[NarrativeEngine] Successfully persisted NarrativeReport id=%s for dataset=%s",
            report_id,
            dataset_id,
        )

        return DatasetNarrativePackageResponse(
            id=report_id,
            dataset_id=dataset_id,
            executive_summary=exec_res,
            kpis=kpi_res,
            root_causes=rca_res,
            recommendations=rec_res,
            forecasts=fc_res,
            scenarios=sc_res,
            metadata=pkg_metadata,
        )

    async def get_latest_persisted_report(
        self,
        dataset_id: uuid.UUID,
    ) -> Optional[DatasetNarrativePackageResponse]:
        """Retrieves the latest persisted narrative report for a dataset if available."""
        entity = await self.narrative_repo.get_latest_by_dataset(dataset_id)
        if not entity:
            return None

        pkg = entity.full_package_json or {}
        exec_data = pkg.get("executive_summary") or entity.executive_summary
        kpi_data = pkg.get("kpis") or entity.kpi_narrative
        rca_data = pkg.get("root_causes") or entity.root_cause_narrative
        rec_data = pkg.get("recommendations") or entity.recommendation_narrative
        fc_data = pkg.get("forecasts") or entity.forecast_narrative
        sc_data = pkg.get("scenarios") or entity.scenario_narrative

        metadata = NarrativeMetadata(
            prompt_version=entity.prompt_version,
            provider=entity.provider,
            model=entity.model,
            narrative_confidence=entity.narrative_confidence,
            generation_time_ms=entity.generation_time_ms,
            validation_time_ms=entity.validation_time_ms,
            total_latency_ms=entity.total_latency_ms,
            fallback_triggered=entity.fallback_triggered,
            is_fallback=entity.is_fallback,
            word_count=0,
            generated_at=entity.generated_at,
        )

        return DatasetNarrativePackageResponse(
            id=entity.id,
            dataset_id=entity.dataset_id,
            executive_summary=ExecutiveNarrativeResponse.model_validate(exec_data),
            kpis=KPINarrativeResponse.model_validate(kpi_data),
            root_causes=RootCauseNarrativeResponse.model_validate(rca_data),
            recommendations=RecommendationNarrativeResponse.model_validate(rec_data),
            forecasts=ForecastNarrativeResponse.model_validate(fc_data) if fc_data else None,
            scenarios=ScenarioNarrativeResponse.model_validate(sc_data) if sc_data else None,
            metadata=metadata,
        )

    async def list_persisted_reports(
        self,
        dataset_id: uuid.UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[NarrativeReportHistoryItem]:
        """Retrieves history of persisted narrative reports for a dataset."""
        entities = await self.narrative_repo.list_by_dataset(dataset_id, limit=limit, offset=offset)
        return [
            NarrativeReportHistoryItem(
                id=e.id,
                dataset_id=e.dataset_id,
                prompt_version=e.prompt_version,
                provider=e.provider,
                model=e.model,
                narrative_confidence=e.narrative_confidence,
                total_latency_ms=e.total_latency_ms,
                is_fallback=e.is_fallback,
                created_at=e.created_at,
            )
            for e in entities
        ]
