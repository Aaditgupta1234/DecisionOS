"""Abstract base class contract for all diagnostic anomaly and root-cause analyzers."""

from abc import ABC, abstractmethod

from app.models.dataset import Dataset
from app.models.dataset_metric import DatasetMetric
from app.models.diagnostic_finding import DiagnosticFinding


class BaseDiagnosticAnalyzer(ABC):
    """
    Standard interface for diagnostic analyzers in the DecisionOS Root Cause Engine.
    
    Each domain analyzer (Revenue, Customer, Orders, Delivery, Reviews, Quality)
    implements this contract to produce business findings.
    """

    @abstractmethod
    async def analyze(
        self,
        dataset: Dataset,
        metrics: list[DatasetMetric],
    ) -> list[DiagnosticFinding]:
        """
        Execute diagnostic analysis on a dataset and its computed metrics.
        
        Args:
            dataset: The target Dataset model instance.
            metrics: List of pre-computed DatasetMetric records for the dataset.
            
        Returns:
            A list of DiagnosticFinding entity instances (empty list if no anomalies detected).
        """
        pass
