"""
Stage 1 — Ingest
Load the SBA 7(a) FOIA CSV and return a filtered DataFrame of relevant columns.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Columns required from the SBA dataset
SBA_COLUMNS = [
    "borrname",
    "borrcity",
    "borrstate",
    "borrzip",
    "naicscode",
    "naicsdescription",
    "businesstype",
    "loanstatus",
    "chargeoffdate",
    "grossapproval",
    "sbaguaranteedapproval",
    "terminmonths",
    "processingmethod",
    "bankname",
    "bankstate",
    "approvaldate",
    "approvalfy",
    "businessage",
    "initialinterestrate",
    "subprogram",
]


def load(path: str | Path, nrows: int | None = None) -> pd.DataFrame:
    """
    Load the SBA 7(a) CSV from disk.

    Args:
        path: Path to the SBA CSV file.
        nrows: Optional row limit — useful for development and testing.

    Returns:
        DataFrame containing only the relevant SBA columns.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"SBA data file not found at {path}. "
            "Download from https://data.sba.gov/dataset/7-a-504-foia "
            "and place at data/raw/sba_7a_fy2020_present.csv"
        )

    logger.info(f"Loading SBA data from {path}")
    df = pd.read_csv(
        path,
        usecols=lambda c: c in SBA_COLUMNS,
        nrows=nrows,
        low_memory=False,
        encoding="latin-1",
    )

    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    missing = [c for c in SBA_COLUMNS if c not in df.columns]
    if missing:
        logger.warning(f"Expected columns not found in dataset: {missing}")

    return df
