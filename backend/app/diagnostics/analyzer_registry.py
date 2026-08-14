"""Dynamic analyzer registration catalog and discovery interface for DecisionOS diagnostic engines."""

from typing import Dict, List, Optional, Type
from app.diagnostics.base_analyzer import BaseDiagnosticAnalyzer


class AnalyzerRegistry:
    """
    Central registry managing diagnostic analyzer registrations, instantiations, and pipeline composition.
    """

    _registry: Dict[str, BaseDiagnosticAnalyzer] = {}

    @classmethod
    def register(cls, analyzer: BaseDiagnosticAnalyzer) -> None:
        """
        Registers an initialized analyzer instance in the global catalog.
        
        Args:
            analyzer: An instance of BaseDiagnosticAnalyzer.
        """
        name = analyzer.__class__.__name__
        cls._registry[name] = analyzer

    @classmethod
    def register_class(cls, analyzer_cls: Type[BaseDiagnosticAnalyzer]) -> None:
        """
        Instantiates and registers an analyzer class.
        
        Args:
            analyzer_cls: Class inheriting from BaseDiagnosticAnalyzer.
        """
        instance = analyzer_cls()
        cls.register(instance)

    @classmethod
    def get_analyzers(cls) -> List[BaseDiagnosticAnalyzer]:
        """Returns all currently registered diagnostic analyzer instances."""
        return list(cls._registry.values())

    @classmethod
    def get_analyzer(cls, name: str) -> Optional[BaseDiagnosticAnalyzer]:
        """Finds a registered analyzer by class name."""
        return cls._registry.get(name)

    @classmethod
    def clear(cls) -> None:
        """Clears all registered analyzers (used for test isolation)."""
        cls._registry.clear()

    @classmethod
    def get_default_analyzers(cls) -> List[BaseDiagnosticAnalyzer]:
        """
        Lazily discovers, registers, and returns the standard 4 domain analyzers:
        1. RevenueDiagnosticAnalyzer
        2. CustomerDiagnosticAnalyzer
        3. OperationalDiagnosticAnalyzer
        4. ProductDiagnosticAnalyzer
        """
        # Lazy imports to avoid circular references
        from app.diagnostics.revenue_analyzer import RevenueDiagnosticAnalyzer
        from app.diagnostics.customer_analyzer import CustomerDiagnosticAnalyzer
        from app.diagnostics.operational_analyzer import OperationalDiagnosticAnalyzer
        from app.diagnostics.product_analyzer import ProductDiagnosticAnalyzer

        default_classes = [
            RevenueDiagnosticAnalyzer,
            CustomerDiagnosticAnalyzer,
            OperationalDiagnosticAnalyzer,
            ProductDiagnosticAnalyzer,
        ]

        for analyzer_cls in default_classes:
            name = analyzer_cls.__name__
            if name not in cls._registry:
                cls._registry[name] = analyzer_cls()

        return list(cls._registry.values())

    @classmethod
    def reset_to_defaults(cls) -> None:
        """Resets the registry to contain exclusively the default 4 domain analyzers."""
        cls.clear()
        cls.get_default_analyzers()
