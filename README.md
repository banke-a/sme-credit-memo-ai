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
│   └── rubric_guide.md
├── examples/
├── tests/
├── run.py
├── .env.example
└── requirements.txt
