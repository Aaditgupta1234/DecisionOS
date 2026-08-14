"""Service layer orchestrating Root Cause Analysis execution, synthesis, and persistence."""

import logging
from typing import Dict, List, Optional, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.diagnostics.diagnostic_engine import DiagnosticEngine
from app.models.dataset import Dataset
from app.models.diagnostic_finding import DiagnosticFinding
from app.models.root_cause_analysis import RootCauseAnalysis
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.root_cause_repository import RootCauseRepository
from app.root_cause.engine import RootCauseEngine
from app.root_cause.graph import RootCauseGraph
from app.schemas.diagnostic import DiagnosticFindingResponse
from app.schemas.root_cause import (
    CausalChainEdge,
    CausalChainNode,
    CausalGraphResponse,
    DatasetRootCausesResponse,
    RootCauseAnalysisResponse,
    RootCauseItem,
    RootCauseSummary,
)

logger = logging.getLogger(__name__)


class RootCauseService:
    """
    Business service layer coordinating diagnostic finding evaluation,
    root cause discovery, DAG synthesis, and database transactions.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db
        self.root_cause_repo = RootCauseRepository(db)
        self.diag_repo = DiagnosticRepository(db)
        self.engine = RootCauseEngine()

    def _is_async(self) -> bool:
        return isinstance(self.db, AsyncSession)

    async def _get_dataset_or_404(self, dataset_id: UUID) -> Dataset:
        """Retrieves a dataset or raises 404."""
        from sqlalchemy import select
        stmt = select(Dataset).where(Dataset.id == dataset_id)

        if self._is_async():
            result = await self.db.execute(stmt)
        else:
            result = self.db.execute(stmt)

        dataset = result.scalar_one_or_none()
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{dataset_id}' not found",
            )
        return dataset

    async def generate_root_causes(
        self,
        dataset_id: UUID,
        recalculate_diagnostics: bool = False,
    ) -> DatasetRootCausesResponse:
        """
        Executes root cause discovery for a dataset and persists the results.
        """
        dataset = await self._get_dataset_or_404(dataset_id)

        # 1. Fetch or re-generate diagnostic findings
        findings = await self.diag_repo.get_dataset_findings(dataset_id)

        if recalculate_diagnostics or not findings:
            diag_engine = DiagnosticEngine(self.db)
            if self._is_async():
                findings = await diag_engine.run(dataset_id)
            else:
                findings = await diag_engine.run(dataset_id)

        # 2. Clear previously persisted root cause records for clean idempotency
        await self.root_cause_repo.delete_by_dataset(dataset_id)

        if not findings or len(findings) < 2:
            # Minimal graph with 0 or 1 findings
            graph = RootCauseGraph()
            for f in findings:
                graph.add_node(f)

            return DatasetRootCausesResponse(
                dataset_id=dataset_id,
                total_root_causes=0,
                analyses=[],
                summaries=[],
                graph=self._serialize_graph(graph),
            )

        # 3. Execute RootCauseEngine
        analyses_models, graph = self.engine.analyze(findings, dataset_id=dataset_id)

        # 4. Bulk persist analyses
        persisted_analyses = await self.root_cause_repo.create_many(analyses_models)

        # 5. Build AI-ready RootCauseSummary objects
        summaries = self._build_root_cause_summaries(persisted_analyses, graph, findings)

        # 6. Commit transaction if session is active
        if self._is_async():
            await self.db.commit()
        else:
            self.db.commit()

        # Format response models
        response_analyses = [
            RootCauseAnalysisResponse.model_validate(rca) for rca in persisted_analyses
        ]

        return DatasetRootCausesResponse(
            dataset_id=dataset_id,
            total_root_causes=len(persisted_analyses),
            analyses=response_analyses,
            summaries=summaries,
            graph=self._serialize_graph(graph),
        )

    async def get_dataset_root_causes(
        self,
        dataset_id: UUID,
    ) -> DatasetRootCausesResponse:
        """
        Retrieves existing root cause records for a dataset, or generates them on-demand if missing.
        """
        dataset = await self._get_dataset_or_404(dataset_id)
        analyses = await self.root_cause_repo.get_by_dataset(dataset_id)

        if not analyses:
            # Generate on demand
            return await self.generate_root_causes(dataset_id, recalculate_diagnostics=False)

        # Reconstruct graph from stored analyses and findings
        findings = await self.diag_repo.get_dataset_findings(dataset_id)
        graph = RootCauseGraph()
        for f in findings:
            graph.add_node(f)

        for a in analyses:
            graph.add_edge(
                source_id=str(a.root_cause_finding_id),
                target_id=str(a.primary_finding_id),
                relationship_type=a.relationship_type.value,
                relationship_strength=a.relationship_strength.value,
                confidence_score=a.confidence_score,
                impact_score=a.impact_score,
            )

        summaries = self._build_root_cause_summaries(analyses, graph, findings)

        return DatasetRootCausesResponse(
            dataset_id=dataset_id,
            total_root_causes=len(analyses),
            analyses=[RootCauseAnalysisResponse.model_validate(a) for a in analyses],
            summaries=summaries,
            graph=self._serialize_graph(graph),
        )

    async def get_root_cause_by_id(
        self,
        analysis_id: UUID,
    ) -> RootCauseAnalysisResponse:
        """Retrieves a single RootCauseAnalysis entity by ID."""
        rca = await self.root_cause_repo.get_by_id(analysis_id)
        if not rca:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Root cause analysis '{analysis_id}' not found",
            )
        return RootCauseAnalysisResponse.model_validate(rca)

    def _build_root_cause_summaries(
        self,
        analyses: List[RootCauseAnalysis],
        graph: RootCauseGraph,
        findings: List[DiagnosticFinding],
    ) -> List[RootCauseSummary]:
        """
        Groups analyses by primary symptom/effect to construct AI-ready problem summaries.
        """
        findings_map = {str(f.id): f for f in findings}
        # Group analyses by primary_finding_id
        grouped: Dict[str, List[RootCauseAnalysis]] = {}
        for a in analyses:
            p_id = str(a.primary_finding_id)
            if p_id not in grouped:
                grouped[p_id] = []
            grouped[p_id].append(a)

        summaries: List[RootCauseSummary] = []

        for primary_id_str, rca_list in grouped.items():
            primary_f = findings_map.get(primary_id_str)
            if not primary_f:
                continue

            primary_title = primary_f.title
            primary_sev = primary_f.severity.value if hasattr(primary_f.severity, "value") else str(primary_f.severity)

            root_items: List[RootCauseItem] = []
            for rca in rca_list:
                cause_f = findings_map.get(str(rca.root_cause_finding_id))
                if not cause_f:
                    continue

                cause_sev = cause_f.severity.value if hasattr(cause_f.severity, "value") else str(cause_f.severity)
                cause_cat = cause_f.supporting_data.get("category", "GENERAL") if cause_f.supporting_data else "GENERAL"
                cause_sub = cause_f.supporting_data.get("subtype", cause_f.finding_type.value) if cause_f.supporting_data else cause_f.finding_type.value

                root_items.append(
                    RootCauseItem(
                        finding_id=cause_f.id,
                        title=cause_f.title,
                        category=cause_cat,
                        subtype=cause_sub,
                        severity=cause_sev,
                        relationship_type=rca.relationship_type.value,
                        relationship_strength=rca.relationship_strength.value,
                        confidence_score=rca.confidence_score,
                        impact_score=rca.impact_score,
                        explanation=rca.explanation,
                    )
                )

            # Compute composite summary statistics
            overall_conf = max((rca.confidence_score for rca in rca_list), default=0.5)
            highest_imp = max((rca.impact_score for rca in rca_list), default=0.5)

            # Get human-readable chain paths
            raw_chains = graph.get_causal_chains(primary_id_str)
            readable_chains: List[List[str]] = []
            for path in raw_chains:
                readable_path = [findings_map[node_id].title for node_id in path if node_id in findings_map]
                if len(readable_path) >= 2:
                    readable_chains.append(readable_path)

            summaries.append(
                RootCauseSummary(
                    primary_issue=primary_title,
                    primary_finding_id=primary_f.id,
                    primary_severity=primary_sev,
                    root_causes=root_items,
                    overall_confidence=overall_conf,
                    highest_impact=highest_imp,
                    causal_chains=readable_chains,
                )
            )

        # Sort summaries by highest impact descending
        summaries.sort(key=lambda s: s.highest_impact, reverse=True)
        return summaries

    @staticmethod
    def _serialize_graph(graph: RootCauseGraph) -> CausalGraphResponse:
        """Serializes RootCauseGraph to CausalGraphResponse."""
        nodes = [
            CausalChainNode(
                id=n.id,
                title=n.title,
                category=n.category,
                subtype=n.subtype,
                severity=n.severity,
                confidence_score=n.confidence_score,
            )
            for n in graph.nodes.values()
        ]

        edges = [
            CausalChainEdge(
                source_id=e.source_id,
                target_id=e.target_id,
                relationship_type=e.relationship_type,
                relationship_strength=e.relationship_strength,
                confidence_score=e.confidence_score,
                impact_score=e.impact_score,
            )
            for e in graph.get_edges()
        ]

        return CausalGraphResponse(nodes=nodes, edges=edges)
