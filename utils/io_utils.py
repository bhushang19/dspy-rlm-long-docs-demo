"""Document I/O and JSON output helpers."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import dspy


def read_document(path: Path, logger: logging.Logger) -> str:
    """Read a text/markdown document and return its contents as a string."""
    logger.info("Reading document: %s", path)
    text = path.read_text(encoding="utf-8", errors="replace")
    logger.info("Document loaded: %d characters", len(text))
    return text


def save_output_json(
    result: dspy.Prediction,
    document_path: Path,
    outputs_dir: Path,
    logger: logging.Logger,
) -> Path:
    """Serialize the RLM Prediction (fields + trajectory) to a timestamped JSON file."""
    outputs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = outputs_dir / f"result_{timestamp}.json"

    payload = {
        "timestamp": datetime.now().isoformat(),
        "document": str(document_path),
        "fields": {
            "survey_edition": result.survey_edition,
            "survey_period": result.survey_period,
            "real_gdp_growth": result.real_gdp_growth,
            "headline_cpi_inflation": result.headline_cpi_inflation,
            "fiscal_deficit_gdp": result.fiscal_deficit_gdp,
            "forex_reserves": result.forex_reserves,
            "agriculture_growth": result.agriculture_growth,
            "services_sector_growth": result.services_sector_growth,
        },
    }

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Output saved: %s", out_path)
    return out_path
