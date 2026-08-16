"""Outcome and Benefits Realization Service for Phase 12.6."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.execution.constants import (
    ExecutionEventType,
    OutcomeCriticality,
    OutcomeMetricType,
    OutcomeStatus,
    TargetDateStatus,
)
from app.execution.event_dispatcher import ExecutionEventDispatcher
from app.execution.models.outcome import (
    InitiativeBenefitRealization,
    InitiativeOutcomeMeasurement,
)
from app.execution.repositories.benefit_repository import (
    BenefitRealizationRepository,
)
from app.execution.repositories.initiative_repository import InitiativeRepository
from app.execution.repositories.outcome_repository import (
    OutcomeMeasurementRepository,
)
from app.execution.repositories.program_repository import ProgramRepository
from app.execution.schemas.outcomes import (
    BenefitRealizationCreate,
    BenefitRealizationListResponse,
    BenefitRealizationResponse,
    BenefitRealizationUpdate,
    InitiativeOutcomeSummary,
    OutcomeMeasurementCreate,
    OutcomeMeasurementListResponse,
    OutcomeMeasurementResponse,
    OutcomeMeasurementUpdate,
    PortfolioBenefitsSummary,
    ProgramOutcomeSummary,
    ROIMetrics,
)
from app.execution.services.benefits_engine import BenefitsRealizationEngine
from app.execution.services.outcome_engine import OutcomeAchievementEngine
from app.execution.services.portfolio_benefits_engine import (
    PortfolioBenefitsEngine,
)
from app.execution.services.roi_engine import ROIIntelligenceEngine


class OutcomeService:
    """
    Comprehensive business service orchestrating multi-tenant CRUD, deterministic intelligence
    calculation, audit event logging, and executive summaries for outcomes and benefits.
    """

    def __init__(self, db: Union[AsyncSession, Session]) -> None:
        self.db = db
        self.is_async = isinstance(db, AsyncSession)
        self.outcome_repo = OutcomeMeasurementRepository(db)
        self.benefit_repo = BenefitRealizationRepository(db)
        self.initiative_repo = InitiativeRepository(db)
        self.program_repo = ProgramRepository(db)
        self.event_dispatcher = ExecutionEventDispatcher(db)

    # ---------------------------------------------------------
    # 1. OUTCOME MEASUREMENTS CRUD
    # ---------------------------------------------------------

    async def record_outcome(
        self,
        organization_id: uuid.UUID,
        payload: OutcomeMeasurementCreate,
        actor_name: str = "System",
        actor_id: Optional[uuid.UUID] = None,
    ) -> OutcomeMeasurementResponse:
        """Records a new quantitative outcome measurement for an initiative."""
        initiative = await self.initiative_repo.get_by_id(payload.initiative_id, organization_id)
        if not initiative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative {payload.initiative_id} not found in this organization",
            )

        metric_name = payload.metric_name or payload.target_metric
        now = datetime.now(timezone.utc)
        m_date = payload.measurement_date or now

        # Historical measurements for volatility
        existing_outcomes = await self.outcome_repo.list_outcomes(
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            limit=50,
        )
        hist_values = [o.actual_value for o in existing_outcomes if o.target_metric == metric_name]
        hist_values.append(payload.actual_value)

        metrics = OutcomeAchievementEngine.calculate_achievement(
            actual=payload.actual_value,
            target=payload.target_value,
            baseline=payload.baseline_value,
            metric_type=payload.metric_type,
            criticality=payload.criticality,
            confidence_score=payload.confidence_score,
            historical_values=hist_values,
            measurement_date=m_date,
            target_achievement_date=payload.target_achievement_date,
            created_at=initiative.created_at,
            dependent_initiatives_count=1,
            measurement_version=1,
            measurement_frequency=payload.measurement_frequency,
        )

        outcome = InitiativeOutcomeMeasurement(
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            target_metric=metric_name,
            metric_type=payload.metric_type,
            criticality=payload.criticality,
            baseline_value=payload.baseline_value,
            target_value=payload.target_value,
            actual_value=payload.actual_value,
            measurement_date=m_date,
            target_achievement_date=payload.target_achievement_date,
            days_until_target=metrics["days_until_target"],
            target_date_status=metrics["target_date_status"],
            realization_delay_days=metrics["realization_delay_days"],
            measurement_version=1,
            measurement_frequency=payload.measurement_frequency,
            status=metrics["status"],
            achievement_percentage=metrics["achievement_percentage"],
            target_variance=metrics["target_variance"],
            improvement_amount=metrics["improvement_amount"],
            confidence_level=metrics["confidence_level"],
            confidence_score=metrics["confidence_score"],
            confidence_trend=metrics["confidence_trend"],
            measurement_stability=metrics["measurement_stability"],
            measurement_stability_score=metrics["measurement_stability_score"],
            measurement_volatility=metrics["measurement_volatility"],
            measurement_quality=metrics["measurement_quality"],
            measurement_reliability_score=metrics["measurement_reliability_score"],
            outcome_data_reliability_score=metrics["outcome_data_reliability_score"],
            measurement_recency=metrics["measurement_recency"],
            measurement_completeness_score=metrics["measurement_completeness_score"],
            outcome_predictability_score=metrics["outcome_predictability_score"],
            outcome_health=metrics["outcome_health"],
            execution_status=metrics["execution_status"],
            owner_id=payload.owner_id,
            owner_name=payload.owner_name,
            verdict_summary=payload.verdict_summary,
            created_by=actor_id,
            updated_by=actor_id,
        )

        saved = await self.outcome_repo.create(outcome)

        # Dispatch Audit Events
        await self.event_dispatcher.dispatch_event(
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            event_type=ExecutionEventType.OUTCOME_CREATED,
            title=f"Outcome Recorded: {metric_name}",
            description=f"Outcome measurement recorded at {metrics['achievement_percentage']:.1f}% achievement ({metrics['status'].value}).",
            actor_name=actor_name,
            actor_id=actor_id,
            new_value=str(payload.actual_value),
            metadata_payload=metrics,
        )

        if metrics["status"] == OutcomeStatus.ACHIEVED:
            await self.event_dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=payload.initiative_id,
                event_type=ExecutionEventType.OUTCOME_ACHIEVED,
                title=f"Target Achieved: {metric_name}",
                description=f"Outcome target achieved with {metrics['achievement_percentage']:.1f}% realization.",
                actor_name=actor_name,
                actor_id=actor_id,
                metadata_payload=metrics,
            )

        return OutcomeMeasurementResponse.model_validate(saved)

    async def update_outcome(
        self,
        organization_id: uuid.UUID,
        outcome_id: uuid.UUID,
        payload: OutcomeMeasurementUpdate,
        actor_name: str = "System",
        actor_id: Optional[uuid.UUID] = None,
    ) -> OutcomeMeasurementResponse:
        """Updates an outcome measurement and auto-increments its measurement version."""
        outcome = await self.outcome_repo.get_by_id(outcome_id, organization_id)
        if not outcome:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outcome measurement {outcome_id} not found in this organization",
            )

        prev_actual = outcome.actual_value
        prev_status = outcome.status
        prev_conf = outcome.confidence_score

        metric_name = payload.metric_name or payload.target_metric or outcome.target_metric
        actual_val = payload.actual_value if payload.actual_value is not None else outcome.actual_value
        target_val = payload.target_value if payload.target_value is not None else outcome.target_value
        baseline_val = payload.baseline_value if payload.baseline_value is not None else outcome.baseline_value
        metric_type = payload.metric_type if payload.metric_type is not None else outcome.metric_type
        criticality = payload.criticality if payload.criticality is not None else outcome.criticality
        conf_score = payload.confidence_score if payload.confidence_score is not None else outcome.confidence_score
        target_ach_date = payload.target_achievement_date if payload.target_achievement_date is not None else outcome.target_achievement_date
        m_date = payload.measurement_date if payload.measurement_date is not None else datetime.now(timezone.utc)
        m_freq = payload.measurement_frequency if payload.measurement_frequency is not None else outcome.measurement_frequency

        # Historical values
        existing_outcomes = await self.outcome_repo.list_outcomes(
            organization_id=organization_id,
            initiative_id=outcome.initiative_id,
            limit=50,
        )
        hist_values = [o.actual_value for o in existing_outcomes if o.target_metric == metric_name and o.id != outcome.id]
        hist_values.append(actual_val)

        new_version = outcome.measurement_version + 1

        metrics = OutcomeAchievementEngine.calculate_achievement(
            actual=actual_val,
            target=target_val,
            baseline=baseline_val,
            metric_type=metric_type,
            criticality=criticality,
            confidence_score=conf_score,
            previous_confidence_score=prev_conf,
            historical_values=hist_values,
            measurement_date=m_date,
            target_achievement_date=target_ach_date,
            created_at=outcome.created_at,
            dependent_initiatives_count=1,
            measurement_version=new_version,
            measurement_frequency=m_freq,
        )

        outcome.target_metric = metric_name
        outcome.metric_type = metric_type
        outcome.criticality = criticality
        outcome.baseline_value = baseline_val
        outcome.target_value = target_val
        outcome.actual_value = actual_val
        outcome.measurement_date = m_date
        outcome.target_achievement_date = target_ach_date
        outcome.days_until_target = metrics["days_until_target"]
        outcome.target_date_status = metrics["target_date_status"]
        outcome.realization_delay_days = metrics["realization_delay_days"]
        outcome.measurement_version = new_version
        outcome.measurement_frequency = m_freq
        outcome.status = metrics["status"]
        outcome.achievement_percentage = metrics["achievement_percentage"]
        outcome.target_variance = metrics["target_variance"]
        outcome.improvement_amount = metrics["improvement_amount"]
        outcome.confidence_level = metrics["confidence_level"]
        outcome.confidence_score = metrics["confidence_score"]
        outcome.confidence_trend = metrics["confidence_trend"]
        outcome.measurement_stability = metrics["measurement_stability"]
        outcome.measurement_stability_score = metrics["measurement_stability_score"]
        outcome.measurement_volatility = metrics["measurement_volatility"]
        outcome.measurement_quality = metrics["measurement_quality"]
        outcome.measurement_reliability_score = metrics["measurement_reliability_score"]
        outcome.outcome_data_reliability_score = metrics["outcome_data_reliability_score"]
        outcome.measurement_recency = metrics["measurement_recency"]
        outcome.measurement_completeness_score = metrics["measurement_completeness_score"]
        outcome.outcome_predictability_score = metrics["outcome_predictability_score"]
        outcome.outcome_health = metrics["outcome_health"]
        outcome.execution_status = metrics["execution_status"]
        if payload.owner_id is not None:
            outcome.owner_id = payload.owner_id
        if payload.owner_name is not None:
            outcome.owner_name = payload.owner_name
        if payload.verdict_summary is not None:
            outcome.verdict_summary = payload.verdict_summary
        outcome.updated_by = actor_id

        updated = await self.outcome_repo.update(outcome)

        # Dispatch Audit Events
        await self.event_dispatcher.dispatch_event(
            organization_id=organization_id,
            initiative_id=outcome.initiative_id,
            event_type=ExecutionEventType.OUTCOME_UPDATED,
            title=f"Outcome Updated: {metric_name} (v{new_version})",
            description=f"Measurement updated from {prev_actual} to {actual_val} ({metrics['achievement_percentage']:.1f}%).",
            actor_name=actor_name,
            actor_id=actor_id,
            previous_value=str(prev_actual),
            new_value=str(actual_val),
            metadata_payload=metrics,
        )

        if metrics["status"] == OutcomeStatus.ACHIEVED and prev_status != OutcomeStatus.ACHIEVED:
            await self.event_dispatcher.dispatch_event(
                organization_id=organization_id,
                initiative_id=outcome.initiative_id,
                event_type=ExecutionEventType.OUTCOME_ACHIEVED,
                title=f"Target Achieved: {metric_name}",
                description=f"Outcome reached 100%+ target realization at {metrics['achievement_percentage']:.1f}%.",
                actor_name=actor_name,
                actor_id=actor_id,
                metadata_payload=metrics,
            )

        return OutcomeMeasurementResponse.model_validate(updated)

    async def get_outcome(
        self,
        organization_id: uuid.UUID,
        outcome_id: uuid.UUID,
    ) -> OutcomeMeasurementResponse:
        """Retrieves a single outcome measurement."""
        outcome = await self.outcome_repo.get_by_id(outcome_id, organization_id)
        if not outcome:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outcome measurement {outcome_id} not found",
            )
        return OutcomeMeasurementResponse.model_validate(outcome)

    async def list_outcomes(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        status_filter: Optional[OutcomeStatus] = None,
        metric_type: Optional[OutcomeMetricType] = None,
        criticality: Optional[OutcomeCriticality] = None,
        target_date_status: Optional[TargetDateStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> OutcomeMeasurementListResponse:
        """Lists outcome measurements with count rollups."""
        items = await self.outcome_repo.list_outcomes(
            organization_id=organization_id,
            initiative_id=initiative_id,
            status=status_filter,
            metric_type=metric_type,
            criticality=criticality,
            target_date_status=target_date_status,
            limit=limit,
            offset=offset,
        )
        total = await self.outcome_repo.count_outcomes(
            organization_id=organization_id,
            initiative_id=initiative_id,
            status=status_filter,
        )

        achieved_cnt = sum(1 for o in items if o.status == OutcomeStatus.ACHIEVED)
        partial_cnt = sum(1 for o in items if o.status == OutcomeStatus.PARTIALLY_ACHIEVED)
        missed_cnt = sum(1 for o in items if o.status == OutcomeStatus.MISSED)

        return OutcomeMeasurementListResponse(
            total=total,
            achieved_count=achieved_cnt,
            partially_achieved_count=partial_cnt,
            missed_count=missed_cnt,
            items=[OutcomeMeasurementResponse.model_validate(o) for o in items],
        )

    async def delete_outcome(
        self,
        organization_id: uuid.UUID,
        outcome_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Deletes an outcome measurement."""
        outcome = await self.outcome_repo.get_by_id(outcome_id, organization_id)
        if not outcome:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outcome measurement {outcome_id} not found",
            )
        await self.outcome_repo.delete(outcome)
        return {"status": "deleted", "id": str(outcome_id)}

    # ---------------------------------------------------------
    # 2. BENEFIT REALIZATIONS CRUD
    # ---------------------------------------------------------

    async def record_benefit(
        self,
        organization_id: uuid.UUID,
        payload: BenefitRealizationCreate,
        actor_name: str = "System",
        actor_id: Optional[uuid.UUID] = None,
    ) -> BenefitRealizationResponse:
        """Records a new benefit realization benchmark for an initiative."""
        initiative = await self.initiative_repo.get_by_id(payload.initiative_id, organization_id)
        if not initiative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative {payload.initiative_id} not found in this organization",
            )

        now = datetime.now(timezone.utc)
        m_date = payload.measured_at or now

        # Calculate metrics
        metrics = BenefitsRealizationEngine.calculate_benefit_realization(
            expected_value=payload.expected_value,
            realized_value=payload.realized_value,
            health_score=initiative.execution_health_score,
            achievement_pct=initiative.completion_percentage,
            confidence_score=payload.confidence_score,
            investment_cost=payload.investment_cost,
        )

        benefit = InitiativeBenefitRealization(
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            benefit_type=payload.benefit_type,
            expected_value=payload.expected_value,
            realized_value=payload.realized_value,
            realization_percentage=metrics["realization_percentage"],
            realization_status=metrics["realization_status"],
            realization_gap=metrics["realization_gap"],
            benefit_score=metrics["benefit_score"],
            value_classification=metrics["value_classification"],
            confidence_score=payload.confidence_score,
            confidence_level=metrics["confidence_level"],
            confidence_trend=metrics["confidence_trend"],
            benefit_trend=metrics["benefit_trend"],
            investment_cost=payload.investment_cost,
            currency=payload.currency,
            measured_at=m_date,
            notes=payload.notes,
            created_by=actor_id,
            updated_by=actor_id,
        )

        saved = await self.benefit_repo.create(benefit)

        # Dispatch Audit Event
        await self.event_dispatcher.dispatch_event(
            organization_id=organization_id,
            initiative_id=payload.initiative_id,
            event_type=ExecutionEventType.BENEFIT_REALIZED,
            title=f"Benefit Realization Recorded: {payload.benefit_type.value}",
            description=f"Realized {payload.currency} {payload.realized_value:,.2f} of {payload.expected_value:,.2f} ({metrics['realization_percentage']:.1f}%).",
            actor_name=actor_name,
            actor_id=actor_id,
            new_value=str(payload.realized_value),
            metadata_payload=metrics,
        )

        return BenefitRealizationResponse.model_validate(saved)

    async def update_benefit(
        self,
        organization_id: uuid.UUID,
        benefit_id: uuid.UUID,
        payload: BenefitRealizationUpdate,
        actor_name: str = "System",
        actor_id: Optional[uuid.UUID] = None,
    ) -> BenefitRealizationResponse:
        """Updates an existing benefit realization record."""
        benefit = await self.benefit_repo.get_by_id(benefit_id, organization_id)
        if not benefit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benefit realization record {benefit_id} not found in this organization",
            )

        prev_realized = benefit.realized_value
        prev_conf = benefit.confidence_score

        exp_val = payload.expected_value if payload.expected_value is not None else benefit.expected_value
        real_val = payload.realized_value if payload.realized_value is not None else benefit.realized_value
        b_type = payload.benefit_type if payload.benefit_type is not None else benefit.benefit_type
        conf_score = payload.confidence_score if payload.confidence_score is not None else benefit.confidence_score
        inv_cost = payload.investment_cost if payload.investment_cost is not None else benefit.investment_cost
        curr = payload.currency if payload.currency is not None else benefit.currency
        m_date = payload.measured_at if payload.measured_at is not None else datetime.now(timezone.utc)
        notes = payload.notes if payload.notes is not None else benefit.notes

        metrics = BenefitsRealizationEngine.calculate_benefit_realization(
            expected_value=exp_val,
            realized_value=real_val,
            confidence_score=conf_score,
            previous_realization=prev_realized,
            previous_confidence_score=prev_conf,
            investment_cost=inv_cost,
        )

        benefit.benefit_type = b_type
        benefit.expected_value = exp_val
        benefit.realized_value = real_val
        benefit.realization_percentage = metrics["realization_percentage"]
        benefit.realization_status = metrics["realization_status"]
        benefit.realization_gap = metrics["realization_gap"]
        benefit.benefit_score = metrics["benefit_score"]
        benefit.value_classification = metrics["value_classification"]
        benefit.confidence_score = conf_score
        benefit.confidence_level = metrics["confidence_level"]
        benefit.confidence_trend = metrics["confidence_trend"]
        benefit.benefit_trend = metrics["benefit_trend"]
        benefit.investment_cost = inv_cost
        benefit.currency = curr
        benefit.measured_at = m_date
        benefit.notes = notes
        benefit.updated_by = actor_id

        updated = await self.benefit_repo.update(benefit)

        # Dispatch Audit Event
        await self.event_dispatcher.dispatch_event(
            organization_id=organization_id,
            initiative_id=benefit.initiative_id,
            event_type=ExecutionEventType.BENEFIT_REALIZED,
            title=f"Benefit Realization Updated: {b_type.value}",
            description=f"Realized value updated from {prev_realized:,.2f} to {real_val:,.2f} ({metrics['realization_percentage']:.1f}%).",
            actor_name=actor_name,
            actor_id=actor_id,
            previous_value=str(prev_realized),
            new_value=str(real_val),
            metadata_payload=metrics,
        )

        return BenefitRealizationResponse.model_validate(updated)

    async def get_benefit(
        self,
        organization_id: uuid.UUID,
        benefit_id: uuid.UUID,
    ) -> BenefitRealizationResponse:
        """Retrieves a single benefit realization record."""
        benefit = await self.benefit_repo.get_by_id(benefit_id, organization_id)
        if not benefit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benefit realization record {benefit_id} not found",
            )
        return BenefitRealizationResponse.model_validate(benefit)

    async def list_benefits(
        self,
        organization_id: uuid.UUID,
        initiative_id: Optional[uuid.UUID] = None,
        benefit_type: Optional[Any] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> BenefitRealizationListResponse:
        """Lists benefit realization records."""
        items = await self.benefit_repo.list_benefits(
            organization_id=organization_id,
            initiative_id=initiative_id,
            benefit_type=benefit_type,
            limit=limit,
            offset=offset,
        )
        total = await self.benefit_repo.count_benefits(
            organization_id=organization_id,
            initiative_id=initiative_id,
            benefit_type=benefit_type,
        )

        total_exp = sum(b.expected_value for b in items)
        total_real = sum(b.realized_value for b in items)
        total_gap = sum(b.realization_gap for b in items)
        port_pct = (total_real / total_exp * 100.0) if total_exp > 0 else (100.0 if total_real > 0 else 0.0)

        return BenefitRealizationListResponse(
            total=total,
            total_expected_value=round(total_exp, 2),
            total_realized_value=round(total_real, 2),
            total_realization_gap=round(total_gap, 2),
            portfolio_realization_percentage=round(min(200.0, max(0.0, port_pct)), 2),
            items=[BenefitRealizationResponse.model_validate(b) for b in items],
        )

    async def delete_benefit(
        self,
        organization_id: uuid.UUID,
        benefit_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Deletes a benefit realization record."""
        benefit = await self.benefit_repo.get_by_id(benefit_id, organization_id)
        if not benefit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benefit realization record {benefit_id} not found",
            )
        await self.benefit_repo.delete(benefit)
        return {"status": "deleted", "id": str(benefit_id)}

    # ---------------------------------------------------------
    # 3. EXECUTIVE SUMMARIES & ROI INTELLIGENCE
    # ---------------------------------------------------------

    async def get_initiative_outcome_summary(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
    ) -> InitiativeOutcomeSummary:
        """Synthesizes outcome achievement and benefits realization profile for an initiative."""
        initiative = await self.initiative_repo.get_by_id(initiative_id, organization_id)
        if not initiative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative {initiative_id} not found",
            )

        outcomes = await self.outcome_repo.list_outcomes(
            organization_id=organization_id,
            initiative_id=initiative_id,
            limit=100,
        )
        benefits = await self.benefit_repo.list_benefits(
            organization_id=organization_id,
            initiative_id=initiative_id,
            limit=100,
        )

        # Average achievement %
        avg_ach = (
            sum(o.achievement_percentage for o in outcomes) / len(outcomes)
            if outcomes else initiative.completion_percentage
        )
        total_exp = sum(b.expected_value for b in benefits)
        total_real = sum(b.realized_value for b in benefits)
        total_gap = sum(b.realization_gap for b in benefits)
        value_at_risk = round(max(0.0, total_exp - total_real), 2)
        overall_real_pct = (total_real / total_exp * 100.0) if total_exp > 0 else (100.0 if total_real > 0 else 0.0)

        # Benefit score
        avg_benefit_score = (
            sum(b.benefit_score for b in benefits) / len(benefits)
            if benefits else 0.0
        )

        # ROI
        cost = initiative.budget_spent if initiative.budget_spent > 0 else initiative.budget_allocated
        roi_res = ROIIntelligenceEngine.calculate_roi(
            realized_value=total_real,
            investment_cost=cost,
            benefit_confidence=(sum(b.confidence_score for b in benefits) / len(benefits)) if benefits else 100.0,
            outcome_confidence=(sum(o.confidence_score for o in outcomes) / len(outcomes)) if outcomes else 100.0,
        )

        # Aggregated outcome metrics
        avg_stability = sum(o.measurement_stability_score for o in outcomes) / max(1, len(outcomes)) if outcomes else 100.0
        avg_reliability = sum(o.measurement_reliability_score for o in outcomes) / max(1, len(outcomes)) if outcomes else 100.0
        avg_data_reliability = sum(o.outcome_data_reliability_score for o in outcomes) / max(1, len(outcomes)) if outcomes else 100.0
        avg_predictability = sum(o.outcome_predictability_score for o in outcomes) / max(1, len(outcomes)) if outcomes else 100.0
        avg_completeness = sum(o.measurement_completeness_score for o in outcomes) / max(1, len(outcomes)) if outcomes else 100.0

        qual = outcomes[0].measurement_quality if outcomes else outcomes[0].measurement_quality if outcomes else outcomes
        # Determine dominant quality
        qual_val = outcomes[0].measurement_quality if outcomes else outcomes
        from app.execution.constants import (
            MeasurementQuality,
            MeasurementRecency,
            OutcomeExecutionStatus,
            OutcomeHealth,
        )
        dom_qual = outcomes[0].measurement_quality if outcomes else MeasurementQuality.HIGH
        dom_rec = outcomes[0].measurement_recency if outcomes else MeasurementRecency.CURRENT
        dom_health = outcomes[0].outcome_health if outcomes else OutcomeHealth.HEALTHY
        dom_exec_status = outcomes[0].execution_status if outcomes else OutcomeExecutionStatus.ON_TRACK
        avg_velocity = sum(o.achievement_percentage / max(1, (datetime.now(timezone.utc).date() - (o.created_at or datetime.now(timezone.utc)).date()).days) for o in outcomes) / max(1, len(outcomes)) if outcomes else 0.0

        return InitiativeOutcomeSummary(
            initiative_id=initiative_id,
            initiative_title=initiative.title,
            outcomes_count=len(outcomes),
            benefits_count=len(benefits),
            overall_achievement_percentage=round(avg_ach, 2),
            overall_realization_percentage=round(min(200.0, max(0.0, overall_real_pct)), 2),
            total_expected_benefits=round(total_exp, 2),
            total_realized_benefits=round(total_real, 2),
            total_realization_gap=round(total_gap, 2),
            value_at_risk=value_at_risk,
            benefit_score=round(avg_benefit_score, 2),
            roi_percentage=roi_res["roi_percentage"],
            roi_classification=roi_res["roi_classification"],
            roi_confidence_score=roi_res["roi_confidence_score"],
            roi_trend=roi_res["roi_trend"],
            forecast_ready=len(outcomes) >= 3,
            measurement_stability_score=round(avg_stability, 2),
            measurement_quality=dom_qual,
            measurement_reliability_score=round(avg_reliability, 2),
            outcome_data_reliability_score=round(avg_data_reliability, 2),
            measurement_recency=dom_rec,
            measurement_completeness_score=round(avg_completeness, 2),
            outcome_predictability_score=round(avg_predictability, 2),
            outcome_health=dom_health,
            execution_status=dom_exec_status,
            realization_velocity=round(avg_velocity, 4),
            dependent_initiatives_count=1,
            owner_id=initiative.owner_id,
            owner_name=initiative.owner,
            outcomes=[OutcomeMeasurementResponse.model_validate(o) for o in outcomes],
            benefits=[BenefitRealizationResponse.model_validate(b) for b in benefits],
        )

    async def get_program_outcome_summary(
        self,
        organization_id: uuid.UUID,
        program_id: uuid.UUID,
    ) -> ProgramOutcomeSummary:
        """Aggregates outcome profiles across all initiatives within a program."""
        program = await self.program_repo.get_by_id(program_id, organization_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic program {program_id} not found",
            )

        initiatives = await self.initiative_repo.list_by_program(program_id, organization_id)
        summaries: List[InitiativeOutcomeSummary] = []
        for init in initiatives:
            summary = await self.get_initiative_outcome_summary(organization_id, init.id)
            summaries.append(summary)

        tot_outcomes = sum(s.outcomes_count for s in summaries)
        tot_benefits = sum(s.benefits_count for s in summaries)
        tot_exp = sum(s.total_expected_benefits for s in summaries)
        tot_real = sum(s.total_realized_benefits for s in summaries)
        tot_gap = sum(s.total_realization_gap for s in summaries)
        val_at_risk = round(max(0.0, tot_exp - tot_real), 2)

        prog_ach = (sum(s.overall_achievement_percentage for s in summaries) / len(summaries)) if summaries else 0.0
        prog_real = (tot_real / tot_exp * 100.0) if tot_exp > 0 else (100.0 if tot_real > 0 else 0.0)

        # Program ROI
        prog_cost = sum(i.budget_spent if i.budget_spent > 0 else i.budget_allocated for i in initiatives)
        roi_res = ROIIntelligenceEngine.calculate_roi(
            realized_value=tot_real,
            investment_cost=prog_cost,
        )

        # Attainment
        achieved_cnt = sum(
            sum(1 for o in s.outcomes if o.status == OutcomeStatus.ACHIEVED)
            for s in summaries
        )
        attainment = (achieved_cnt / tot_outcomes * 100.0) if tot_outcomes > 0 else 0.0

        return ProgramOutcomeSummary(
            program_id=program_id,
            program_title=program.title,
            initiatives_count=len(initiatives),
            outcomes_count=tot_outcomes,
            benefits_count=tot_benefits,
            program_achievement_percentage=round(prog_ach, 2),
            program_realization_percentage=round(min(200.0, max(0.0, prog_real)), 2),
            total_expected_benefits=round(tot_exp, 2),
            total_realized_benefits=round(tot_real, 2),
            total_realization_gap=round(tot_gap, 2),
            value_at_risk=val_at_risk,
            program_roi=roi_res["roi_percentage"],
            program_roi_classification=roi_res["roi_classification"],
            confidence_coverage_score=100.0,
            attainment_rate=round(attainment, 2),
            initiatives_summaries=summaries,
        )

    async def get_initiative_roi(
        self,
        organization_id: uuid.UUID,
        initiative_id: uuid.UUID,
    ) -> ROIMetrics:
        """Computes ROI intelligence for an initiative."""
        initiative = await self.initiative_repo.get_by_id(initiative_id, organization_id)
        if not initiative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategic initiative {initiative_id} not found",
            )

        benefits = await self.benefit_repo.list_benefits(
            organization_id=organization_id,
            initiative_id=initiative_id,
        )
        outcomes = await self.outcome_repo.list_outcomes(
            organization_id=organization_id,
            initiative_id=initiative_id,
        )

        realized_val = sum(b.realized_value for b in benefits)
        cost = initiative.budget_spent if initiative.budget_spent > 0 else initiative.budget_allocated
        b_conf = (sum(b.confidence_score for b in benefits) / len(benefits)) if benefits else 100.0
        o_conf = (sum(o.confidence_score for o in outcomes) / len(outcomes)) if outcomes else 100.0

        res = ROIIntelligenceEngine.calculate_roi(
            realized_value=realized_val,
            investment_cost=cost,
            benefit_confidence=b_conf,
            outcome_confidence=o_conf,
        )
        return ROIMetrics.model_validate(res)

    async def get_portfolio_benefits_summary(
        self,
        organization_id: uuid.UUID,
    ) -> PortfolioBenefitsSummary:
        """Aggregates portfolio-wide strategic benefits, ROI distributions, and outcome health."""
        outcomes = await self.outcome_repo.list_outcomes(
            organization_id=organization_id,
            limit=500,
        )
        benefits = await self.benefit_repo.list_benefits(
            organization_id=organization_id,
            limit=500,
        )

        # Convert ORM to dicts for engine
        outcomes_dicts = [
            {
                "id": o.id,
                "status": o.status,
                "target_metric": o.target_metric,
                "target_value": o.target_value,
                "actual_value": o.actual_value,
                "achievement_percentage": o.achievement_percentage,
                "confidence_level": o.confidence_level,
                "confidence_score": o.confidence_score,
                "measurement_stability_score": o.measurement_stability_score,
                "measurement_quality": o.measurement_quality,
                "measurement_reliability_score": o.measurement_reliability_score,
                "outcome_data_reliability_score": o.outcome_data_reliability_score,
                "measurement_recency": o.measurement_recency,
                "measurement_completeness_score": o.measurement_completeness_score,
                "outcome_predictability_score": o.outcome_predictability_score,
                "outcome_health": o.outcome_health,
                "execution_status": o.execution_status,
                "target_date_status": o.target_date_status,
                "days_until_target": o.days_until_target,
                "realization_delay_days": o.realization_delay_days,
                "measurement_age_days": max(0, (datetime.now(timezone.utc).date() - o.measurement_date.date()).days),
                "outcome_age_days": max(0, (datetime.now(timezone.utc).date() - o.created_at.date()).days) if o.created_at else 0,
                "realization_velocity": o.achievement_percentage / max(1, (datetime.now(timezone.utc).date() - (o.created_at or datetime.now(timezone.utc)).date()).days),
                "dependent_initiatives_count": 1,
            }
            for o in outcomes
        ]

        benefits_dicts = [
            {
                "id": b.id,
                "benefit_type": b.benefit_type,
                "expected_value": b.expected_value,
                "realized_value": b.realized_value,
                "realization_percentage": b.realization_percentage,
                "realization_status": b.realization_status,
                "realization_gap": b.realization_gap,
                "benefit_score": b.benefit_score,
                "value_classification": b.value_classification,
                "confidence_score": b.confidence_score,
                "confidence_level": b.confidence_level,
                "investment_cost": b.investment_cost,
            }
            for b in benefits
        ]

        res = PortfolioBenefitsEngine.calculate_portfolio_summary(
            outcomes=outcomes_dicts,
            benefits=benefits_dicts,
        )
        return PortfolioBenefitsSummary.model_validate(res)
