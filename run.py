"""
run.py — Pipeline entry point
Runs the full SME credit memo generation pipeline.

Usage:
    Single record (by index):
        python run.py --record 0

    Batch mode:
        python run.py --batch --n 20

    Batch from specific offset:
        python run.py --batch --n 20 --offset 100
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from pipeline import ingest, validate, clean, credit_analysis, prompt, generate, format_doc

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run")

SBA_DATA_PATH = os.getenv("SBA_DATA_PATH", "data/raw/sba_7a_fy2020_present.csv")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/memos")
LOG_DIR = os.getenv("LOG_DIR", "output/logs")


def run_pipeline(df, idx: int, run_log: dict) -> bool:
    """Run the full pipeline for a single record. Returns True on success."""
    row = df.iloc[idx]
    borrower = row.get("BorrName", f"Record_{idx}")
    approval_date = row.get("ApprovalDate", "unknown")

    try:
        system_prompt, user_message = prompt.build_prompt(row)
        memo = generate.generate(system_prompt, user_message)
        output_path = format_doc.render(memo, borrower, approval_date, OUTPUT_DIR)

        run_log["memos_generated"] += 1
        run_log["records"].append({
            "index": idx,
            "borrower": borrower,
            "status": "success",
            "output": str(output_path),
        })
        logger.info(f"[{idx}] {borrower} — done")
        return True

    except Exception as e:
        run_log["failures"] += 1
        run_log["records"].append({
            "index": idx,
            "borrower": borrower,
            "status": "failed",
            "error": str(e),
        })
        logger.error(f"[{idx}] {borrower} — failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="SME Credit Memo Generator")
    parser.add_argument("--record", type=int, help="Run pipeline for a single record index")
    parser.add_argument("--batch", action="store_true", help="Run batch mode")
    parser.add_argument("--n", type=int, default=20, help="Number of records in batch mode")
    parser.add_argument("--offset", type=int, default=0, help="Starting offset for batch mode")
    parser.add_argument("--nrows", type=int, default=None, help="Limit rows loaded from CSV (development)")
    args = parser.parse_args()

    if not args.record and not args.batch:
        parser.error("Specify --record <index> or --batch")

    start_time = time.time()
    run_log = {
        "run_timestamp": datetime.now().isoformat(),
        "mode": "batch" if args.batch else "single",
        "records_processed": 0,
        "memos_generated": 0,
        "failures": 0,
        "records": [],
    }

    logger.info("Loading and preparing data")
    df = ingest.load(SBA_DATA_PATH, nrows=args.nrows)
    df = validate.validate(df)
    df = clean.clean(df)
    df = credit_analysis.analyse_batch(df)

    if args.record is not None:
        run_log["records_processed"] = 1
        run_pipeline(df, args.record, run_log)

    elif args.batch:
        indices = range(args.offset, min(args.offset + args.n, len(df)))
        run_log["records_processed"] = len(indices)
        logger.info(f"Processing {len(indices)} records (offset={args.offset})")
        for idx in indices:
            run_pipeline(df, idx, run_log)

    run_log["duration_seconds"] = round(time.time() - start_time, 1)

    # Write run log
    log_path = Path(LOG_DIR)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(run_log, indent=2, default=str))

    logger.info(
        f"Done — {run_log['memos_generated']} memos generated, "
        f"{run_log['failures']} failures, "
        f"{run_log['duration_seconds']}s"
    )
    logger.info(f"Run log: {log_file}")


if __name__ == "__main__":
    main()
