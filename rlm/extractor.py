"""RLM extraction runner: wires up dspy.RLM and runs field extraction."""

from __future__ import annotations

import logging
import sys

import dspy

from rlm.lm_config import configure_lm, configure_sub_lm
from rlm.signature import ExtractReportFields
from utils.interpreter import build_windows_interpreter
from utils.logging_setup import _LoggingStream


def extract_fields(document: str, logger: logging.Logger) -> dspy.Prediction:
    """Configure LMs, build the RLM module, and run extraction on *document*.

    The main LM drives strategy — deciding what code to run and what to search for.
    The sub-LM handles the repetitive llm_query() calls inside each REPL iteration,
    keeping costs down on large documents without sacrificing orchestration quality.
    """
    configure_lm()
    sub_lm = configure_sub_lm()
    interpreter = build_windows_interpreter()

    rlm = dspy.RLM(
        ExtractReportFields,
        interpreter=interpreter,
        tools=[],
        sub_lm=sub_lm,
        max_iterations=20, # Budget cap on REPL rounds: each iteration is one Main LM call that writes and executes Python code.
        max_llm_calls=50, # Budget cap on sub-LM (llm_query) calls made from inside the REPL code. Each call reads one snippet semantically.
        verbose=True,
    )

    logger.info("Starting RLM extraction")
    # Redirect stdout so RLM's verbose print() output lands in the log file
    _prev_stdout = sys.stdout
    sys.stdout = _LoggingStream(logger)
    try:
        result = rlm(document=document)
    finally:
        sys.stdout = _prev_stdout
    logger.info("RLM extraction complete")
    return result
