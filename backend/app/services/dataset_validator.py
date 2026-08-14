"""Dataset validation engine using Pandas for file inspection and structural integrity checks."""

import math
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
from app.core.logging import logger


@dataclass
class ValidationResult:
    """Dataclass encapsulating comprehensive dataset validation outputs."""
    is_valid: bool
    errors: List[Dict[str, str]] = field(default_factory=list)
    record_count: int = 0
    column_count: int = 0
    columns: List[str] = field(default_factory=list)
    dtypes: Dict[str, str] = field(default_factory=dict)
    sample_values: Dict[str, str] = field(default_factory=dict)
    preview_rows: List[Dict[str, Any]] = field(default_factory=list)


def clean_val_for_json(val: Any) -> Any:
    """Sanitizes floats/NaN/NaT values so they can be serialized to clean JSON."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return val


class DatasetValidator:
    """Validates CSV format, encoding, headers, row counts, and duplicate columns."""

    def validate_file(self, file_path: str, original_filename: str) -> ValidationResult:
        """Executes full validation pipeline on a saved dataset file."""
        errors: List[Dict[str, str]] = []

        # 1. Check file extension
        ext = os.path.splitext(original_filename)[1].lower()
        if ext != ".csv":
            errors.append({
                "type": "INVALID_FILE_TYPE",
                "message": f"Unsupported file extension '{ext}'. Only '.csv' files are supported.",
            })
            return ValidationResult(is_valid=False, errors=errors)

        # 2. Check file existence and non-zero size
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            errors.append({
                "type": "EMPTY_FILE",
                "message": "The uploaded file is empty (0 bytes).",
            })
            return ValidationResult(is_valid=False, errors=errors)

        # 3. Attempt parsing with Pandas
        df: Optional[pd.DataFrame] = None
        for encoding in ["utf-8", "utf-8-sig", "latin1", "cp1252"]:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except pd.errors.EmptyDataError:
                errors.append({
                    "type": "EMPTY_DATASET",
                    "message": "The CSV file contains no readable data or headers.",
                })
                return ValidationResult(is_valid=False, errors=errors)
            except Exception as e:
                logger.error(f"Pandas CSV parsing error: {e}")
                errors.append({
                    "type": "PARSING_ERROR",
                    "message": f"Could not parse CSV content: {str(e)}",
                })
                return ValidationResult(is_valid=False, errors=errors)

        if df is None:
            errors.append({
                "type": "INVALID_ENCODING",
                "message": "File encoding could not be determined. Please upload a UTF-8 encoded CSV.",
            })
            return ValidationResult(is_valid=False, errors=errors)

        # 4. Check for headers and duplicate column names from raw first line
        try:
            import csv
            with open(file_path, "r", encoding=encoding or "utf-8", errors="ignore") as f:
                header_line = f.readline()
                reader = csv.reader([header_line])
                raw_headers = next(reader, [])
        except Exception:
            raw_headers = [str(c) for c in df.columns]

        if not raw_headers:
            errors.append({
                "type": "MISSING_HEADERS",
                "message": "Dataset does not contain any header columns.",
            })
            return ValidationResult(is_valid=False, errors=errors)

        seen_cols = set()
        duplicates = set()
        for col in raw_headers:
            clean_col = col.strip()
            if clean_col in seen_cols:
                duplicates.add(clean_col)
            seen_cols.add(clean_col)

        if duplicates:
            errors.append({
                "type": "DUPLICATE_COLUMNS",
                "message": f"Duplicate column headers detected: {', '.join(sorted(duplicates))}.",
            })

        raw_columns = [str(c) for c in raw_headers]

        # 5. Check for minimum record count (at least 1 row)
        record_count = len(df)
        if record_count == 0:
            errors.append({
                "type": "NO_RECORDS",
                "message": "The dataset has headers but contains zero data rows.",
            })

        if errors:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                record_count=record_count,
                column_count=len(raw_columns),
                columns=raw_columns,
            )

        # 7. Extract column dtypes and first non-null sample values
        dtypes: Dict[str, str] = {}
        sample_values: Dict[str, str] = {}
        for col in df.columns:
            col_name = str(col)
            dtypes[col_name] = str(df[col].dtype)
            non_null_series = df[col].dropna()
            if len(non_null_series) > 0:
                first_val = non_null_series.iloc[0]
                sample_values[col_name] = str(first_val)[:500]
            else:
                sample_values[col_name] = ""

        # 8. Create sanitized JSON preview rows (first 20 rows)
        preview_df = df.head(20)
        preview_rows: List[Dict[str, Any]] = []
        for row in preview_df.to_dict(orient="records"):
            clean_row = {k: clean_val_for_json(v) for k, v in row.items()}
            preview_rows.append(clean_row)

        return ValidationResult(
            is_valid=True,
            errors=[],
            record_count=record_count,
            column_count=len(raw_columns),
            columns=raw_columns,
            dtypes=dtypes,
            sample_values=sample_values,
            preview_rows=preview_rows,
        )


validator = DatasetValidator()
