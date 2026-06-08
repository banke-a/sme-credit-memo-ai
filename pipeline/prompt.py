"""
Stage 4 — Prompt Construction
Map a cleaned, credit-analysed SBA record to a structured prompt for the Claude API.
"""

import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_PATH = Path("prompts/system_prompt.txt")


def _load_system_prompt() -> str:
    if not SYSTEM_PROMPT_PATH.exists():
        raise FileNotFoundError(f"System prompt not found at {SYSTEM_PROMPT_PATH}")
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def _format_currency(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "Not available"
    return f"${value:,.0f}"


def build_user_message(row: pd.Series) -> str:
    """
    Build the structured JSON user message for a single loan record.

    Args:
        row: A single row from the credit-analysed DataFrame.

    Returns:
        JSON string to send as the user message to Claude.
    """
    payload = {
        "borrower": {
            "name": str(row.get("borrname", "Unknown")),
            "city": str(row.get("borrcity", "Unknown")),
            "state": str(row.get("borrstate", "Unknown")),
            "business_type": str(row.get("businesstype", "Unknown")),
            "industry": str(row.get("naicsdescription", "Unknown")),
            "naics_code": str(row.get("naicscode", "Unknown")),
        },
        "loan": {
            "gross_approval": _format_currency(row.get("grossapproval")),
            "sba_guaranteed": _format_currency(row.get("sbaguaranteedapproval")),
            "term_months": int(row["terminmonths"]) if pd.notna(row.get("terminmonths")) else None,
            "approval_date": str(row["approvaldate"].date()) if pd.notna(row.get("approvaldate")) else None,
            "delivery_method": str(row.get("processingmethod", "Unknown")),
            "lender": str(row.get("bankname", "Unknown")),
            "lender_state": str(row.get("bankstate", "Unknown")),
            "loan_status": str(row.get("loanstatus", "Unknown")),
        },
        "credit_analysis": {
            "monthly_payment": _format_currency(row.get("monthly_payment")),
            "guarantee_coverage_pct": row.get("guarantee_pct"),
            "term_band": str(row.get("term_band", "Unknown")),
            "industry_risk_tier": str(row.get("industry_risk_tier", "Unknown")),
            "risk_band": str(row.get("risk_band", "Unknown")),
            "repayment_flag": bool(row.get("repayment_flag", False)),
        },
    }

    return json.dumps(payload, indent=2, default=str)

def build_prompt(row: pd.Series) -> tuple[str, str]:
    """
    Build the full prompt (system + user) for a single loan record.

    Args:
        row: A single row from the credit-analysed DataFrame.

    Returns:
        Tuple of (system_prompt, user_message).
    """
    system_prompt = _load_system_prompt()
    user_message = build_user_message(row)
    return system_prompt, user_message
