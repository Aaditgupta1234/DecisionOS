"""Schema mapping engine providing automated field normalization and confidence-scored mapping suggestions."""

import re
from typing import List, Optional, Tuple
from app.core.constants import STANDARD_BUSINESS_FIELDS
from app.schemas.dataset import MappingSuggestion


def normalize_column_name(name: str) -> str:
    """Normalizes raw header names to clean lowercase snake_case strings."""
    s = name.strip().lower()
    # Replace non-alphanumeric characters with underscores
    s = re.sub(r"[^\w\s]", "_", s)
    # Replace spaces or multiple underscores with a single underscore
    s = re.sub(r"[\s_]+", "_", s)
    return s.strip("_")


class SchemaMapper:
    """Intelligent schema mapping engine with exact, synonym, and fuzzy pattern matching."""

    def match_column(self, raw_column: str) -> Tuple[Optional[str], float]:
        """Calculates the best canonical business field match and confidence score for a column."""
        normalized = normalize_column_name(raw_column)

        # 1. Exact Match against canonical standard field names (Confidence: 1.0)
        if normalized in STANDARD_BUSINESS_FIELDS:
            return normalized, 1.0

        # 2. Synonym Exact Match against known industry aliases (Confidence: 0.9)
        for std_field, synonyms in STANDARD_BUSINESS_FIELDS.items():
            if normalized in synonyms or raw_column.lower().strip() in synonyms:
                return std_field, 0.9

        # 3. Partial Substring Match (Confidence: 0.7)
        for std_field, synonyms in STANDARD_BUSINESS_FIELDS.items():
            for syn in synonyms:
                # Check if synonym is a substantial substring of normalized name or vice-versa
                if (len(syn) >= 4 and syn in normalized) or (len(normalized) >= 4 and normalized in syn):
                    return std_field, 0.7

        return None, 0.0

    def suggest_mappings(self, columns: List[str]) -> List[MappingSuggestion]:
        """Generates mapping suggestions for all provided raw column names."""
        suggestions: List[MappingSuggestion] = []
        for col in columns:
            suggested_field, confidence = self.match_column(col)
            suggestions.append(
                MappingSuggestion(
                    original_column=col,
                    suggested_field=suggested_field,
                    confidence=confidence,
                )
            )
        return suggestions


schema_mapper = SchemaMapper()
