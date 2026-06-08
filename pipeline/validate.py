"""
Stage 2 — Validate
Schema and quality checks on the raw SBA DataFrame using Pandera.
Fails fast on critical violations. Logs warnings on soft failures.
"""

import logging

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

logger = logging.getLogger(__name__)

sba_schema = DataFrameSchema(
    columns={
        "borrname": Column(str, nullable=True),  # clean.py drops nulls downstream
        "borrstate": Column(str, nullable=True),
        "grossapproval": Column(float, checks=Check.greater_than(0), nullable=False),
        "sbaguaranteedapproval": Column(float, checks=Check.greater_than_or_equal_to(0), nullable=True),
        "terminmonths": Column(float, checks=Check.greater_than_or_equal_to(0), nullable=True),  # 0 handled in clean
        "loanstatus": Column(str, nullable=True),
        "naicscode": Column(object, nullable=True),
    },
    coerce=True,
    strict=False,
)


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run schema validation on the SBA DataFrame.

    Args:
        df: Raw DataFrame from ingest stage.

    Returns:
        Validated DataFrame (unchanged if passing).

    Raises:
        pandera.errors.SchemaError: On critical schema violations.
    """
    logger.info("Running schema validation")

    try:
        validated = sba_schema.validate(df, lazy=True)
        logger.info("Schema validation passed")
        return validated
    except pa.errors.SchemaErrors as e:
        logger.error(f"Schema validation failed:\n{e.failure_cases}")
        raise
