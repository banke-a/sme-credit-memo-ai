# AI-Powered SME Credit Memo Generator

## Research Question

Can LLMs generate structured SME credit memos that are sufficiently complete, explainable, and consistent to support human credit decision-making?

---

## The Problem

Traditional credit assessment frameworks are built for borrowers with clean, structured financials — audited accounts, payslips, formal credit history. Many SMEs, particularly those that are early-stage, cash-based, or thin-file, lack this. They have real but hard-to-assess creditworthiness embedded in their trading behaviour rather than their balance sheet.

At the same time, smaller lenders rarely have specialist credit analysts on staff. Credit assessment is done informally, inconsistently, or not at all — leading to either excessive risk or blanket rejection of creditworthy borrowers.

This project asks whether an LLM, given structured loan data and a set of pre-calculated credit metrics, can produce a memo that is good enough to put in front of a loan officer or credit committee.

---

## What This Project Does

A batch pipeline that takes raw SBA 7(a) loan records, runs a set of deterministic credit calculations, and uses the Claude API to generate a structured, formatted credit memo for each borrower.

The pipeline has six stages:

```
SBA 7(a) Loan Data (CSV)
        │
        ▼
   Validate & Clean
        │
        ▼
 Credit Analysis Layer
 (monthly payment, guarantee %, risk band)
        │
        ▼
  Construct Prompt (structured JSON)
        │
        ▼
   Generate Memo (Claude API)
        │
        ▼
  Format to .docx
```

Each generated memo contains:

- Business overview
- Loan structure
- Credit analysis (pre-calculated, not invented by the LLM)
- Repayment capacity narrative
- Risk factors
- Mitigants
- Recommendation — Approve / Decline / Approve with Conditions

The recommendation is framed as decision-support. The LLM states a position with reasoning. Human sign-off is required before any lending decision is made.

---

## Why Credit Calculations Are Separated From the LLM

Deterministic calculations belong in code. The LLM reasons from pre-calculated inputs — it does not invent numbers.

Before the Claude API is called, `credit_analysis.py` computes:

| Calculation | Logic |
|---|---|
| Monthly debt obligation | GrossApproval / TermInMonths |
| SBA guarantee coverage | SBAGuaranteedApproval / GrossApproval |
| Loan term band | Short / Medium / Long |
| Risk rating band | Composite of status, guarantee, term |
| Repayment capacity flag | Elevated if charged off or defaulted |
| Industry risk tier | NAICS code mapped to sector risk |

These are passed to the LLM as structured inputs. The LLM interprets and narrates — it does not calculate.

---

## Evaluation

20 generated memos were scored manually by the author using a structured credit risk evaluation rubric.

**Scoring dimensions (each 1–5, total 30):**

| Dimension | What is evaluated |
|---|---|
| Completeness | All sections present and populated |
| Accuracy to source data | Memo reflects SBA input fields correctly |
| Credit reasoning | Repayment and risk analysis follows sound credit logic |
| Risk identification | Risks are specific and relevant to the borrower |
| Recommendation quality | Recommendation is justified by the preceding analysis |
| Explainability | A loan officer could use this memo with a committee |

**Success threshold:** Mean score ≥ 22/30 across 20 memos, with at least 80% scoring 20/30 or higher.

**Results: Both thresholds met.**

| Metric | Result | Threshold |
|---|---|---|
| Mean score | 28.2 / 30 | ≥ 22 / 30 ✅ |
| Memos scoring ≥ 20/30 | 20 / 20 (100%) | ≥ 80% ✅ |
| Min score | 26 / 30 | — |
| Max score | 30 / 30 | — |

**Scores by dimension:**

| Dimension | Mean |
|---|---|
| Completeness | 5.00 / 5 |
| Accuracy to source data | 5.00 / 5 |
| Explainability | 5.00 / 5 |
| Recommendation quality | 4.85 / 5 |
| Credit reasoning | 4.30 / 5 |
| Risk identification | 4.05 / 5 |

**What worked well:** Completeness, accuracy, and explainability were perfect across all 20 memos. The LLM correctly interpreted SBA loan status codes, applied franchise model mitigants without instruction, identified counter-cyclical industry characteristics, and consistently produced defensible recommendations with human sign-off notices.

**Where it struggled:** Risk identification was the weakest dimension — occasionally thin on firm-specific analysis, particularly for larger loans relative to likely firm scale. Credit reasoning depth was limited by the SBA dataset's absence of income and cash flow data, a data gap the LLM correctly flagged but could not compensate for analytically.

**What would improve it:** Income and cash flow data (the single biggest gap), sector-specific prompt variants for high-risk industries, and few-shot examples in the prompt for edge cases.

See `/evaluation/rubric_scores.csv` for individual scores and `/evaluation/findings.md` for the full findings report.

---

## Data Source

**SBA 7(a) FOIA Loan Data** — US Small Business Administration
Public domain, available at [data.sba.gov](https://data.sba.gov/dataset/7-a-504-foia)

Download the FY2020–Present CSV and place it in `data/raw/`. The file is gitignored.

No proprietary data is used in this project.

---

## How to Run

**1. Clone the repo and install dependencies**

```bash
git clone https://github.com/banke-a/sme-credit-memo-ai.git
cd sme-credit-memo-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Set up your API key**

```bash
cp .env.example .env
# Add your Anthropic API key to .env
```

**3. Download SBA data**

Download the FY2020–Present 7(a) file from data.sba.gov and place it at:

```
data/raw/foia-7a-fy2020-present-asof-XXXXXX.csv
```

Update `SBA_DATA_PATH` in your `.env` file to match the filename.

**4. Run the pipeline**

Single record:
```bash
python run.py --record 0
```

Batch mode (20 records):
```bash
python run.py --batch --n 20
```

Output memos are written to `/output/memos/`. Run logs are written to `/output/logs/`.

**API costs:** Each memo requires one Claude API call. Generating 20 memos costs approximately $0.50 at current Sonnet pricing. You will need your own Anthropic API key.

---

## Design Decisions

| Decision | Rationale |
|---|---|
| AI engineering, not ML | Clients want AI-powered automation, not model training |
| Credit calculations in Python | Deterministic logic belongs in code, not in a prompt |
| Structured JSON output | Consistent, parseable, testable — more reliable than prose parsing |
| Decision-support framing | LLM recommends, human decides — more defensible and realistic |
| Manual evaluation | Human scoring by a domain expert is more credible than automated grading |
| Alternative data deferred | Credit analysis layer and evaluation are the stronger v1 signals |
| Single repo | One URL, full story visible, folder structure shows separation of concerns |

---

## Future Work

- Alternative data layer — transaction volume, years trading, cash flow regularity, digital payment signals
- Broader dataset support — non-US SME lending data, open banking exports, accounting platform datasets
- FastAPI serving layer — expose memo generation as a REST endpoint
- Provider abstraction layer — LangChain or lightweight adapter to support OpenAI, Gemini, and other LLM providers
- Multi-language output — generate memos in additional languages for non-English speaking lender contexts

---

## Project Structure

```
sme-credit-memo-ai/
├── data/
│   └── raw/                     # SBA 7(a) CSV (gitignored)
├── output/
│   ├── memos/                   # Generated .docx credit memos
│   └── logs/                    # Batch run logs (JSON)
├── pipeline/
│   ├── ingest.py                # Stage 1: Load SBA data
│   ├── validate.py              # Stage 2: Schema + quality checks
│   ├── clean.py                 # Stage 3: Standardise and coerce
│   ├── credit_analysis.py       # Credit calculations before LLM call
│   ├── prompt.py                # Stage 4: Prompt construction
│   ├── generate.py              # Stage 5: Claude API call + parse
│   └── format_doc.py            # Stage 6: python-docx rendering
├── prompts/
│   ├── system_prompt.txt
│   └── output_schema.json
├── evaluation/
│   ├── rubric_scores.csv
│   ├── rubric_guide.md
│   └── findings.md
├── examples/                    # Sample memos — high and low scoring
├── tests/
├── run.py
├── .env.example
└── requirements.txt
```

---

*This project is a portfolio piece demonstrating AI engineering applied to SME credit assessment. Generated memos are for demonstration purposes only and do not constitute financial advice or credit decisions.*
