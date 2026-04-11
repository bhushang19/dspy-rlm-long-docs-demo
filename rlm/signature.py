"""DSPy Signature for Economic Survey field extraction.

Fields are deliberately spread across different chapters so RLM must
iterate across the full document — demonstrating adaptive cross-chapter
reasoning without any pre-chunking.
"""

from __future__ import annotations

import dspy


class ExtractReportFields(dspy.Signature):
    """Extract key macroeconomic indicators from the India Economic Survey document.

    Use the Python REPL to search and slice the document as needed.
    Each field comes from a different chapter — use keyword searches to locate
    the relevant section before extracting the value.
    Only extract values that are explicitly stated in the document.
    Include units where present (e.g. %, Rs lakh crore, US$ billion).
    """

    document: str = dspy.InputField(desc="Full markdown text of the India Economic Survey released in 2025")

    # Cover / overview — should be easy; establishes baseline
    survey_edition: str = dspy.OutputField(desc="Edition of the survey (e.g. Economic Survey 2025-26)")
    survey_period: str = dspy.OutputField(desc="Financial year covered by the survey (e.g. 2025-26)")

    # Chapter 1 / macro overview — in opening chapter summary tables
    real_gdp_growth: str = dspy.OutputField(desc="Real GDP growth rate for the current year as stated in the document (e.g. 6.4%)")

    # Prices chapter — requires searching inflation section
    headline_cpi_inflation: str = dspy.OutputField(desc="Average headline CPI inflation for the year as stated in the document (e.g. 4.9%)")

    # Fiscal chapter — buried in a multi-row budget table
    fiscal_deficit_gdp: str = dspy.OutputField(desc="Central government fiscal deficit as a percentage of GDP as stated in the document (e.g. 4.9% of GDP)")

    # External sector chapter — requires locating forex reserves table
    forex_reserves: str = dspy.OutputField(desc="India's foreign exchange reserves as stated in the document (e.g. US$ 640 billion)")

    # Agriculture chapter — different chapter entirely from macro/fiscal
    agriculture_growth: str = dspy.OutputField(desc="Agriculture and allied sectors GVA growth rate for the year as stated in the document")

    # Services / industry chapters — tests cross-chapter reasoning
    services_sector_growth: str = dspy.OutputField(desc="Services sector GVA growth rate for the year as stated in the document")
