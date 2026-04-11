"""
Convert a PDF file to a Markdown file for use with the DSPy RLM demo.

Usage:
    python convert_pdf_to_md.py <input.pdf> [output.md]

If output path is omitted, the markdown file is written next to the PDF
with the same stem (e.g. economic_survey.pdf -> economic_survey.md).

The converted file should be placed under the data/ folder before running
program.py, and REPORT_PATH in program.py updated to match its name.

Requires:
    pip install pymupdf4llm
"""

from __future__ import annotations

import sys
from pathlib import Path


def convert(pdf_path: Path, md_path: Path) -> None:
    try:
        import pymupdf4llm
    except ImportError:
        print("ERROR: pymupdf4llm is not installed.")
        print("       Run:  pip install pymupdf4llm")
        sys.exit(1)

    print(f"Converting : {pdf_path}")
    print(f"Output     : {md_path}")

    md_text = pymupdf4llm.to_markdown(str(pdf_path))

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8")

    size_kb = md_path.stat().st_size / 1024
    print(f"Done. Written {len(md_text):,} characters ({size_kb:,.1f} KB) -> {md_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python convert_pdf_to_md.py <input.pdf> [output.md]")
        sys.exit(1)

    pdf_path = Path(sys.argv[1]).resolve()
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"ERROR: Expected a .pdf file, got: {pdf_path.suffix}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        md_path = Path(sys.argv[2]).resolve()
    else:
        md_path = pdf_path.with_suffix(".md")

    convert(pdf_path, md_path)


if __name__ == "__main__":
    main()
