# Evaluation Rubric — Scoring Guide

**Project:** AI-Powered SME Credit Memo Generator  
**Evaluator:** Author  
**Method:** Manual scoring using structured credit risk evaluation rubric  
**Sample size:** 20 generated memos  

---

## Scoring Scale

Each dimension is scored 1–5.  
Total score per memo: 6–30.

---

## Dimensions

### 1. Completeness (1–5)
Are all required memo sections present and substantively populated?

| Score | Criteria |
|---|---|
| 1 | One or more sections missing entirely |
| 2 | All sections present but two or more are superficial (one sentence or less) |
| 3 | All sections present; one is thin but acceptable |
| 4 | All sections present and adequately populated |
| 5 | All sections fully populated with specific, relevant content |

---

### 2. Accuracy to Source Data (1–5)
Does the memo correctly reflect the SBA input fields — loan amount, term, business type, industry, guarantee coverage?

| Score | Criteria |
|---|---|
| 1 | Material factual errors (wrong loan amount, wrong status etc.) |
| 2 | Minor errors that would require correction before use |
| 3 | Broadly accurate with one small discrepancy |
| 4 | Accurate with negligible rounding or wording differences |
| 5 | Fully accurate to all source fields |

---

### 3. Credit Reasoning (1–5)
Does the repayment capacity and risk band analysis follow sound credit logic?

| Score | Criteria |
|---|---|
| 1 | Reasoning absent, contradictory, or clearly flawed |
| 2 | Some reasoning present but it does not follow from the data |
| 3 | Reasoning is present and broadly sound but generic |
| 4 | Reasoning is specific to this borrower and logically consistent |
| 5 | Reasoning is specific, well-structured, and would satisfy a credit committee |

---

### 4. Risk Identification (1–5)
Are the key risk factors identified and relevant to this specific borrower?

| Score | Criteria |
|---|---|
| 1 | No meaningful risks identified |
| 2 | Only generic risks stated (e.g. "economic conditions may affect repayment") |
| 3 | One or two specific risks identified |
| 4 | Three or more specific risks with brief context |
| 5 | Comprehensive, specific, prioritised risk identification with context |

---

### 5. Recommendation Quality (1–5)
Is the recommendation (Approve / Decline / Approve with Conditions) justified by the preceding analysis?

| Score | Criteria |
|---|---|
| 1 | Recommendation stated with no supporting reasoning |
| 2 | Recommendation loosely connected to analysis |
| 3 | Recommendation follows from analysis but reasoning is brief |
| 4 | Recommendation clearly evidenced with specific reference to the analysis |
| 5 | Recommendation is fully justified, balanced, and includes the human sign-off notice |

---

### 6. Explainability (1–5)
Could a loan officer use this memo to explain the decision to a borrower or credit committee?

| Score | Criteria |
|---|---|
| 1 | Not usable as-is — requires full rewrite |
| 2 | Usable only with significant editing |
| 3 | Usable with moderate editing |
| 4 | Usable with minor edits |
| 5 | Ready to use with minimal or no editing |

---

## Success Threshold

The research question is answered affirmatively if:
- **Mean score ≥ 22/30** across all 20 memos, AND
- **At least 80% of memos** achieve a score of **20/30 or higher**

---

## Notes for Scoring

- Score each memo independently — do not adjust scores relative to other memos
- A memo that is technically accurate but analytically shallow should not score above 3 on Credit Reasoning
- The human sign-off notice must be present in the recommendation section to score 5 on Recommendation Quality
- If a section is present but contains fabricated data not present in the source, cap Accuracy at 2
