"""
Stage 3 — Clean
Standardise formats, handle missing values, coerce types.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardise the validated SBA DataFrame.

    Args:
        df: Validated DataFrame from validate stage.

    Returns:
        Cleaned DataFrame ready for credit analysis.
    """
    logger.info("Cleaning SBA data")
    df = df.copy()

    # Standardise string fields
    for col in ["BorrName", "BorrCity", "BorrState", "BusinessType", "LoanStatus",
                "BankName", "NaicsDescription", "DeliveryMethod"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            df[col] = df[col].replace("Nan", np.nan)

    # Coerce numeric fields
    for col in ["GrossApproval", "SBAGuaranteedApproval", "TermInMonths", "InitialInterestRate"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Parse dates
    for col in ["ApprovalDate", "ChargeOffDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Normalise NAICS code to string
    if "NaicsCode" in df.columns:
        df["NaicsCode"] = df["NaicsCode"].astype(str).str.zfill(6).replace("000000", np.nan)

    # Drop rows with no borrower name or loan amount — unusable records
    before = len(df)
    df = df.dropna(subset=["BorrName", "GrossApproval"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"Dropped {dropped:,} rows missing BorrName or GrossApproval")

    logger.info(f"Clean complete — {len(df):,} records remaining")
    return df
