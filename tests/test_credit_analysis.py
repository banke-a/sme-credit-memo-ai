"""
Tests for pipeline/credit_analysis.py
"""

import numpy as np
import pandas as pd
import pytest

from pipeline.credit_analysis import (
    _term_band,
    _guarantee_pct,
    _monthly_payment,
    _industry_risk,
    _risk_band,
    _repayment_flag,
    analyse,
)


class TestTermBand:
    def test_short(self):
        assert _term_band(36) == "Short"

    def test_medium(self):
        assert _term_band(84) == "Medium"

    def test_long(self):
        assert _term_band(240) == "Long"

    def test_boundary_60(self):
        assert _term_band(60) == "Medium"

    def test_boundary_120(self):
        assert _term_band(120) == "Medium"

    def test_null(self):
        assert _term_band(np.nan) == "Unknown"


class TestGuaranteePct:
    def test_standard(self):
        assert _guarantee_pct(75000, 100000) == 75.0

    def test_full_guarantee(self):
        assert _guarantee_pct(100000, 100000) == 100.0

    def test_zero_gross(self):
        assert _guarantee_pct(75000, 0) is None

    def test_null_inputs(self):
        assert _guarantee_pct(None, 100000) is None
        assert _guarantee_pct(75000, None) is None


class TestMonthlyPayment:
    def test_standard(self):
        assert _monthly_payment(120000, 120) == 1000.0

    def test_null_months(self):
        assert _monthly_payment(100000, None) is None

    def test_zero_months(self):
        assert _monthly_payment(100000, 0) is None


class TestIndustryRisk:
    def test_construction_is_high(self):
        _, risk = _industry_risk("236110")
        assert risk == "High"

    def test_finance_is_low(self):
        _, risk = _industry_risk("522110")
        assert risk == "Low"

    def test_retail_is_high(self):
        _, risk = _industry_risk("441110")
        assert risk == "High"

    def test_unknown_naics(self):
        name, risk = _industry_risk(None)
        assert name == "Unknown"


class TestRiskBand:
    def test_charged_off_is_high(self):
        band = _risk_band("Charged Off", 75.0, "Short")
        assert band == "High"

    def test_paid_low_guarantee_high(self):
        band = _risk_band("Paid In Full", 40.0, "Long")
        assert band == "High"

    def test_paid_medium_guarantee_medium(self):
        band = _risk_band("Paid In Full", 60.0, "Long")
        assert band == "Medium"

    def test_paid_high_guarantee_short_is_low(self):
        band = _risk_band("Paid In Full", 85.0, "Short")
        assert band == "Low"


class TestRepaymentFlag:
    def test_charged_off(self):
        assert _repayment_flag("Charged Off") is True

    def test_paid(self):
        assert _repayment_flag("Paid In Full") is False

    def test_null(self):
        assert _repayment_flag(None) is False


class TestAnalyse:
    def test_full_record(self):
        row = pd.Series({
            "GrossApproval": 200000,
            "SBAGuaranteedApproval": 150000,
            "TermInMonths": 120,
            "LoanStatus": "Paid In Full",
            "NaicsCode": "541110",
        })
        result = analyse(row)
        assert result["monthly_payment"] == 1666.67
        assert result["guarantee_pct"] == 75.0
        assert result["term_band"] == "Medium"
        assert result["risk_band"] in ["Low", "Medium", "High"]
        assert result["repayment_flag"] is False
