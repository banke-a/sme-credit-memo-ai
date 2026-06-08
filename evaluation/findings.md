# Evaluation Findings

## Research Question

Can LLMs generate structured SME credit memos that are sufficiently complete, explainable, and consistent to support human credit decision-making?

## Results Summary

| Metric | Result | Threshold | Pass |
|---|---|---|---|
| Mean score | 28.2 / 30 | ≥ 22 / 30 | ✅ |
| Memos scoring ≥ 20/30 | 20 / 20 (100%) | ≥ 80% | ✅ |
| Min score | 26 / 30 | — | — |
| Max score | 30 / 30 | — | — |

Both success thresholds were met. The research question is answered affirmatively.

## Scores by Dimension

| Dimension | Mean Score | Max |
|---|---|---|
| Completeness | 5.00 / 5 | 5 |
| Accuracy to source data | 5.00 / 5 | 5 |
| Explainability | 5.00 / 5 | 5 |
| Recommendation quality | 4.85 / 5 | 5 |
| Credit reasoning | 4.30 / 5 | 5 |
| Risk identification | 4.05 / 5 | 5 |

## What the LLM Did Well

**Completeness and structure were perfect across all 20 memos.** Every required section was present and substantively populated in every document. The prompt architecture — structured JSON input, defined output schema, section-by-section guidance — produced consistent, complete output without exception.

**Accuracy to source data was perfect.** The LLM never fabricated loan amounts, guarantee figures, or loan status information. It correctly interpreted SBA-specific terminology (PIF, CHGOFF, LIQUID, CANCLD, PURCH(NOT C/O)) and applied each appropriately to the memo narrative.

**Explainability was uniformly high.** Every memo was written at a level a loan officer could present to a credit committee without significant editing. The prose was clear, precise, and free of hallucinated content.

**Recommendation quality was strong.** The LLM consistently took defensible positions — approving performing loans, declining charged-off and cancelled loans, and applying Approve with Conditions where sector risk warranted additional scrutiny. The mandatory human sign-off notice appeared in every recommendation section.

**Domain reasoning on complex cases was notable.** Standout examples:
- Correctly identified the counter-cyclical nature of disaster restoration services (Record 9)
- Correctly flagged EV disruption as a medium-term risk for an automotive oil change business (Record 16)
- Correctly distinguished between the 50% Express Programme guarantee and the standard 75% guarantee across multiple records
- Correctly applied franchise model mitigants for Firehouse Subs and Subway without being explicitly instructed to do so

## Where the LLM Struggled

**Risk identification was the weakest dimension (4.05/5).** In two memos (Records 5 and 14), risk analysis was present but insufficiently specific. The most common gap was failure to probe the implications of loan size relative to likely firm scale — a $1M+ loan to a 2-person CPA firm warrants deeper analysis than the memos provided.

**Credit reasoning was occasionally generic (4.30/5).** Where loan status was clearly performing and industry risk was low, the LLM sometimes produced competent but shallow repayment capacity analysis. This is a direct consequence of the SBA dataset's absence of income or cash flow data — the LLM correctly flagged this limitation but could not compensate for it analytically.

**The borrower name bug affected 19 of 20 memos.** Records with null `borrname` fields in the SBA dataset were processed correctly — the LLM identified the correct business name from other fields — but the memo header and filename defaulted to "Record_N". This is a pipeline bug, not an LLM quality issue, and is tracked for fix in the next iteration.

## What Would Improve Performance

1. **Income and cash flow data** — the single biggest gap. Even estimated annual revenue would allow the LLM to produce meaningful DSCR estimates rather than relying on loan status as a proxy for repayment capacity.

2. **Borrower name resolution** — fixing the null `borrname` pipeline bug would improve memo professionalism significantly.

3. **Sector-specific prompt variants** — a restaurant-specific or construction-specific system prompt addendum could push risk identification scores from 4 to 5 for high-risk sectors.

4. **Few-shot examples** — providing one high-quality example memo in the prompt would likely improve credit reasoning depth in edge cases.

## Conclusion

The results demonstrate that an LLM, given structured loan data and pre-calculated credit metrics, can produce credit memos that are complete, accurate, explainable, and recommendation-ready across a diverse range of SME borrower profiles and loan statuses. The mean score of 28.2/30 — well above the 22/30 threshold — and the 100% pass rate at 20/30 provide strong evidence that AI-assisted credit memo generation is a viable tool for supporting human credit decision-making in organisations without specialist credit analysts.

The primary limitation is data availability, not model capability. With richer input data — particularly income, cash flow, and trading history — output quality would improve further.
