"""
DSPy RLM demo — India Economic Survey field extraction.

The full document is passed to dspy.RLM. The LM uses its built-in Python REPL
to search and slice the document across multiple iterations, then calls SUBMIT()
with the final structured answer. No pre-chunking required — that is RLM's job.

Run:
    python program.py

Fill in .env before running (see .env.example for required variables).
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from rlm.extractor import extract_fields
from rlm.signature import ExtractReportFields  
from utils.io_utils import read_document, save_output_json
from utils.logging_setup import configure_logging

load_dotenv()

REPORT_PATH = Path(__file__).parent / "data" / "document-2.md"
LOGS_DIR = Path(__file__).parent / "logs"
OUTPUTS_DIR = Path(__file__).parent / "outputs"


def main() -> None:
    logger = configure_logging(LOGS_DIR)

    document = read_document(REPORT_PATH, logger)

    logger.info("=" * 60)
    logger.info("DSPy RLM – Economic Survey Field Extraction")
    logger.info("=" * 60)

    # ── Core RLM call ──────────────────────────────────────────────────
    result = extract_fields(document, logger)
    # ──────────────────────────────────────────────────────────────────

    logger.info("=" * 60)
    logger.info("EXTRACTED FIELDS")
    logger.info("=" * 60)
    logger.info("Survey edition        : %s", result.survey_edition)
    logger.info("Survey period         : %s", result.survey_period)
    logger.info("Real GDP growth       : %s", result.real_gdp_growth)
    logger.info("Headline CPI inflation: %s", result.headline_cpi_inflation)
    logger.info("Fiscal deficit/GDP    : %s", result.fiscal_deficit_gdp)
    logger.info("Forex reserves        : %s", result.forex_reserves)
    logger.info("Agriculture growth    : %s", result.agriculture_growth)
    logger.info("Services growth       : %s", result.services_sector_growth)

    logger.info("=" * 60)
    logger.info("RLM TRAJECTORY")
    logger.info("=" * 60)
    for i, step in enumerate(result.trajectory, 1):
        logger.info("--- Step %d ---", i)
        if step.get("reasoning"):
            logger.info("Reasoning : %s", step["reasoning"])
        if step.get("code"):
            logger.info("Code      :\n%s", step["code"])
        if step.get("output"):
            logger.info("Output    :\n%s", step["output"])

    save_output_json(result, REPORT_PATH, OUTPUTS_DIR, logger)


if __name__ == "__main__":
    main()
