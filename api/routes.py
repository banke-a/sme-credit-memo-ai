"""
api/routes.py — API endpoints
"""

import io
import json
import logging
import os
from pathlib import Path
from functools import lru_cache

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from pipeline import ingest, validate, clean, credit_analysis, prompt, generate, format_doc

logger = logging.getLogger(__name__)
router = APIRouter()

SBA_DATA_PATH = os.getenv("SBA_DATA_PATH", "data/sample/sba_7a_sample.csv")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/memos")
PIN = os.getenv("APP_PIN", "348750")


# ── Data loading ──────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_dataframe() -> pd.DataFrame:
    """Load and process the SBA data once, cache in memory."""
    logger.info("Loading SBA data...")
    df = ingest.load(SBA_DATA_PATH, nrows=5000)  # Load first 5000 for performance
    result = validate.validate(df)
    df = clean.clean(result if isinstance(result, pd.DataFrame) else df)
    df = credit_analysis.analyse_batch(df)
    logger.info(f"Data loaded: {len(df):,} records")
    return df


# ── Request/Response models ───────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    borrower_name: str
    pin: str


class BorrowerRecord(BaseModel):
    borrower_name: str
    city: str
    state: str
    industry: str
    naics_code: str
    business_type: str
    loan_amount: str
    sba_guaranteed: str
    term_months: str
    guarantee_pct: str
    monthly_payment: str
    risk_band: str
    industry_risk_tier: str
    loan_status: str
    lender: str
    approval_date: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/borrowers")
async def get_borrowers():
    """Return list of unique borrower names for the dropdown."""
    try:
        df = get_dataframe()
        names = (
            df["borrname"]
            .dropna()
            .unique()
            .tolist()
        )
        names = sorted([n for n in names if isinstance(n, str) and len(n) > 2])
        return {"borrowers": names[:200]}  # Cap at 200 for UI performance
    except Exception as e:
        logger.error(f"Failed to load borrowers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/borrower/{borrower_name}")
async def get_borrower_record(borrower_name: str):
    """Return record preview for a selected borrower."""
    try:
        df = get_dataframe()
        matches = df[df["borrname"].str.lower() == borrower_name.lower()]

        if matches.empty:
            raise HTTPException(status_code=404, detail="Borrower not found")

        row = matches.iloc[0]

        return BorrowerRecord(
            borrower_name=str(row.get("borrname", "")),
            city=str(row.get("borrcity", "—")),
            state=str(row.get("borrstate", "—")),
            industry=str(row.get("naicsdescription", "—")),
            naics_code=str(row.get("naicscode", "—")),
            business_type=str(row.get("businesstype", "—")),
            loan_amount=f"${row.get('grossapproval', 0):,.0f}" if pd.notna(row.get("grossapproval")) else "—",
            sba_guaranteed=f"${row.get('sbaguaranteedapproval', 0):,.0f}" if pd.notna(row.get("sbaguaranteedapproval")) else "—",
            term_months=f"{int(row['terminmonths'])} months" if pd.notna(row.get("terminmonths")) else "—",
            guarantee_pct=f"{row.get('guarantee_pct', 0):.0f}%" if pd.notna(row.get("guarantee_pct")) else "—",
            monthly_payment=f"${row.get('monthly_payment', 0):,.2f}" if pd.notna(row.get("monthly_payment")) else "—",
            risk_band=str(row.get("risk_band", "—")),
            industry_risk_tier=str(row.get("industry_risk_tier", "—")),
            loan_status=str(row.get("loanstatus", "—")),
            lender=str(row.get("bankname", "—")),
            approval_date=str(row["approvaldate"].date()) if pd.notna(row.get("approvaldate")) else "—",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get borrower record: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_memo(request: GenerateRequest):
    """
    PIN-gated endpoint. Generate a credit memo for the selected borrower.
    Returns structured memo JSON.
    """
    # PIN check
    if request.pin != PIN:
        raise HTTPException(status_code=401, detail="Invalid PIN")

    try:
        df = get_dataframe()
        matches = df[df["borrname"].str.lower() == request.borrower_name.lower()]

        if matches.empty:
            raise HTTPException(status_code=404, detail="Borrower not found")

        row = matches.iloc[0]

        # Build prompt and generate memo
        system_prompt_text, user_message = prompt.build_prompt(row)
        memo = generate.generate(system_prompt_text, user_message)

        # Also save .docx to output directory
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        format_doc.render(
            memo,
            row.get("borrname", "unknown"),
            row.get("approvaldate", "unknown"),
            OUTPUT_DIR
        )

        # Return memo JSON plus credit analysis metrics
        return {
            "borrower_name": str(row.get("borrname", "")),
            "approval_date": str(row["approvaldate"].date()) if pd.notna(row.get("approvaldate")) else "—",
            "credit_metrics": {
                "monthly_payment": f"${row.get('monthly_payment', 0):,.2f}" if pd.notna(row.get("monthly_payment")) else "—",
                "guarantee_pct": f"{row.get('guarantee_pct', 0):.0f}%" if pd.notna(row.get("guarantee_pct")) else "—",
                "risk_band": str(row.get("risk_band", "—")),
                "industry_risk_tier": str(row.get("industry_risk_tier", "—")),
                "term_band": str(row.get("term_band", "—")),
                "repayment_flag": bool(row.get("repayment_flag", False)),
            },
            "memo": memo,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memo generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{borrower_name}")
async def download_memo(borrower_name: str, pin: str):
    """Download the generated .docx memo for a borrower."""
    if pin != PIN:
        raise HTTPException(status_code=401, detail="Invalid PIN")

    # Find the most recent memo for this borrower
    output_dir = Path(OUTPUT_DIR)
    safe_name = "".join(c for c in borrower_name if c.isalnum() or c in " _-").strip().replace(" ", "_")

    matches = list(output_dir.glob(f"credit_memo_{safe_name}*.docx"))
    if not matches:
        raise HTTPException(status_code=404, detail="Memo not found — generate it first")

    memo_path = sorted(matches)[-1]  # Most recent

    return StreamingResponse(
        open(memo_path, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={memo_path.name}"}
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
