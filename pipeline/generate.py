"""
Stage 5 — Generate
Call the Claude API and parse the structured JSON memo response.
"""

import json
import logging
import os

import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

REQUIRED_SECTIONS = [
    "business_overview",
    "loan_structure",
    "credit_analysis",
    "repayment_capacity",
    "risk_factors",
    "mitigants",
    "recommendation",
]


def _parse_response(text: str) -> dict:
    """
    Parse the JSON response from Claude.
    Strips markdown fences if present.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)


def _validate_sections(memo: dict) -> list[str]:
    """Return list of any required sections missing from the memo."""
    return [s for s in REQUIRED_SECTIONS if s not in memo]


def generate(system_prompt: str, user_message: str) -> dict:
    """
    Call Claude API and return parsed memo JSON.

    Args:
        system_prompt: Credit analyst persona and instructions.
        user_message: Structured JSON loan record.

    Returns:
        Parsed memo as a dictionary with all required sections.

    Raises:
        ValueError: If required sections are missing from the response.
        json.JSONDecodeError: If the response is not valid JSON.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    logger.info("Calling Claude API")
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw_text = response.content[0].text
    logger.info(f"Received response — {response.usage.output_tokens} tokens")

    memo = _parse_response(raw_text)
    missing = _validate_sections(memo)
    if missing:
        raise ValueError(f"Generated memo missing required sections: {missing}")

    return memo
