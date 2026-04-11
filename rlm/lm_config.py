"""Azure OpenAI LM factory functions for DSPy."""

from __future__ import annotations

import os

import dspy


def configure_lm() -> dspy.LM:
    """Create and register the main orchestration LM (set as DSPy default)."""
    lm = dspy.LM(
        f"azure/{os.environ['AZURE_OPENAI_DEPLOYMENT']}",
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_base=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        cache=False,
    )
    dspy.configure(lm=lm)
    return lm


def configure_sub_lm() -> dspy.LM:
    """Create the sub-LM used for cheap repetitive extractions inside the REPL loop.

    Uses AZURE_OPENAI_SUB_LM_DEPLOYMENT if set; falls back to the main deployment.
    All other credentials are shared with the main LM.
    """
    sub_deployment = os.environ.get(
        "AZURE_OPENAI_SUB_LM_DEPLOYMENT",
        os.environ["AZURE_OPENAI_DEPLOYMENT"],
    )
    return dspy.LM(
        f"azure/{sub_deployment}",
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_base=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        cache=False,
    )
