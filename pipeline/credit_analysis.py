"""
Credit Analysis Layer
Deterministic credit calculations performed before the LLM is called.
The LLM reasons from these inputs — it does not invent them.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# NAICS sector risk mapping — first two digits of NAICS code
# Higher tier = higher risk
NAICS_RISK_TIERS = {
    "11": ("Agriculture", "Medium"),
    "21": ("Mining", "Medium"),
    "22": ("Utilities", "Low"),
    "23": ("Construction", "High"),
    "31": ("Manufacturing", "Medium"),
    "32": ("Manufacturing", "Medium"),
    "33": ("Manufacturing", "Medium"),
    "42": ("Wholesale Trade", "Low"),
    "44": ("Retail Trade", "High"),
    "45": ("Retail Trade", "High"),
    "48": ("Transportation", "Medium"),
    "49": ("Transportation", "Medium"),
    "51": ("Information", "Medium"),
    "52": ("Finance & Insurance", "Low"),
    "53": ("Real Estate", "Medium"),
    "54": ("Professional Services", "Low"),
    "55": ("Management", "Low"),
    "56": ("Administrative Services", "Medium"),
    "61": ("Education", "Low"),
    "62": ("Healthcare", "Low"),
    "71": ("Arts & Entertainment", "High"),
    "72": ("Accommodation & Food", "High"),
    "81": ("Other Services", "Medium"),
    "92": ("Public Administration", "Low"),
}


def _term_band(months: float) -> str:
    if pd.isna(months):
        return "Unknown"
    if months < 60:
        return "Short"
    if months <= 120:
        return "Medium"
    return "Long"


def _guarantee_pct(guaranteed: float, gross: float) -> float | None:
    if pd.isna(guaranteed) or pd.isna(gross) or gross == 0:
        return None
    return round((guaranteed / gross) * 100, 1)


def _monthly_payment(gross: float, months: float) -> float | None:
    if pd.isna(gross) or pd.isna(months) or months == 0:
        return None
    return round(gross / months, 2)


def _industry_risk(naics_code: str) -> tuple[str, str]:
    if pd.isna(naics_code) or naics_code == "nan":
        return ("Unknown", "Unknown")
    prefix = str(naics_code)[:2]
    return NAICS_RISK_TIERS.get(prefix, ("Other", "Medium"))


def _risk_band(loan_status: str, guarantee_pct: float | None, term_band: str) -> str:
    """
    Composite risk band: Low / Medium / High.
    Combines loan status history, guarantee coverage, and term length.
    Charged off or defaulted loans are always High regardless of other factors.
    """
    # Hard override — any default or charge-off is immediately High
    if isinstance(loan_status, str):
        status = loan_status.lower()
        if any(w in status for w in ["charged off", "default", "dbnc"]):
            return "High"

    score = 0

    # Guarantee coverage — lower coverage = higher risk
    if guarantee_pct is not None:
        if guarantee_pct >= 75:
            score += 0
        elif guarantee_pct >= 50:
            score += 1
        else:
            score += 2

    # Term length — longer term = more exposure
    if term_band == "Long":
        score += 1

    if score <= 1:
        return "Low"
    if score <= 2:
        return "Medium"
    return "High"

def _repayment_flag(loan_status: str) -> bool:
    if not isinstance(loan_status, str):
        return False
    status = loan_status.lower()
    return any(w in status for w in ["charged off", "default", "dbnc"])


def analyse(row: pd.Series) -> dict:
    """
    Run all credit calculations for a single SBA loan record.

    Args:
        row: A single row from the cleaned SBA DataFrame.

    Returns:
        Dictionary of calculated credit metrics to pass to the LLM prompt.
    """
    monthly_payment = _monthly_payment(row.get("GrossApproval"), row.get("TermInMonths"))
    guarantee_pct = _guarantee_pct(row.get("SBAGuaranteedApproval"), row.get("GrossApproval"))
    term_band = _term_band(row.get("TermInMonths"))
    industry_name, industry_risk = _industry_risk(row.get("NaicsCode"))
    risk_band = _risk_band(row.get("LoanStatus"), guarantee_pct, term_band)
    repayment_flag = _repayment_flag(row.get("LoanStatus"))

    return {
        "monthly_payment": monthly_payment,
        "guarantee_pct": guarantee_pct,
        "term_band": term_band,
        "industry_name": industry_name,
        "industry_risk_tier": industry_risk,
        "risk_band": risk_band,
        "repayment_flag": repayment_flag,
    }


def analyse_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run credit analysis across all records in a DataFrame.
    Attaches results as new columns.

    Args:
        df: Cleaned SBA DataFrame.

    Returns:
        DataFrame with credit analysis columns appended.
    """
    logger.info(f"Running credit analysis on {len(df):,} records")
    results = df.apply(analyse, axis=1, result_type="expand")
    df = pd.concat([df, results], axis=1)
    logger.info("Credit analysis complete")
    return df
