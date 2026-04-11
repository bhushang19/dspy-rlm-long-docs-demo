"""
Convert a PDF file to a Markdown file using docling for high-quality table preservation.

docling uses ML-based layout analysis and table structure recognition, which produces
significantly better results than position-heuristic approaches for complex documents
with multi-column financial/statistical tables.

For large PDFs (100+ pages), this script splits the PDF into chunks and converts
each chunk separately to avoid running out of RAM with the ML layout model.

Usage:
    python convert_pdf_to_md_docling.py <input.pdf> [output.md] [--chunk-size N]

    --chunk-size N   Pages per chunk (default: 5). Reduce if you still get OOM errors.

If output path is omitted, the markdown file is written next to the PDF
with the same stem (e.g. economic_survey.pdf -> economic_survey.md).

The converted file should be placed under the data/ folder before running
program.py, and REPORT_PATH in program.py updated to match its name.

Note: docling downloads ML models on first run (~500 MB). Subsequent runs are fast.

Requires:
    pip install docling pymupdf4llm
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


DEFAULT_CHUNK_SIZE = 5  # Pages per batch; reduce if OOM errors persist


def build_converter():
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
    from docling.datamodel.base_models import InputFormat

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False               # Skip OCR for text-based PDFs (faster)
    pipeline_options.do_table_structure = True     # Enable ML table structure recognition
    pipeline_options.images_scale = 0.25           # Minimal resolution to reduce RAM usage
    pipeline_options.generate_page_images = False  # Do not keep full rasterized page in memory
    pipeline_options.generate_picture_images = False  # Do not extract embedded pictures
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=2,
        device=AcceleratorDevice.CPU,
    )

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def convert(pdf_path: Path, md_path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF is not installed.")
        print("       Run:  pip install pymupdf4llm")
        sys.exit(1)

    try:
        build_converter()  # Validates docling import early
    except ImportError:
        print("ERROR: docling is not installed.")
        print("       Run:  pip install docling")
        sys.exit(1)

    print(f"Converting : {pdf_path}")
    print(f"Output     : {md_path}")
    print("Note: First run will download ML models (~500 MB). Please wait...")

    src_doc = fitz.open(str(pdf_path))
    total_pages = len(src_doc)
    chunks = list(range(0, total_pages, chunk_size))
    print(f"Total pages: {total_pages} | Chunk size: {chunk_size} | Chunks: {len(chunks)}")

    md_parts: list[str] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        converter = build_converter()

        for i, start in enumerate(chunks):
            end = min(start + chunk_size, total_pages)
            print(f"  Processing pages {start + 1}-{end} (chunk {i + 1}/{len(chunks)})...")

            chunk_doc = fitz.open()
            chunk_doc.insert_pdf(src_doc, from_page=start, to_page=end - 1)
            chunk_path = Path(tmp_dir) / f"chunk_{start:04d}_{end:04d}.pdf"
            chunk_doc.save(str(chunk_path))
            chunk_doc.close()

            try:
                result = converter.convert(str(chunk_path))
                md_parts.append(result.document.export_to_markdown())
            except Exception as exc:
                print(f"  WARNING: chunk {i + 1} failed ({exc}), falling back to page-by-page...")
                # Retry each page in the chunk individually so one bad page doesn't lose the whole chunk
                for page_idx in range(start, end):
                    page_doc = fitz.open()
                    page_doc.insert_pdf(src_doc, from_page=page_idx, to_page=page_idx)
                    page_path = Path(tmp_dir) / f"page_{page_idx:04d}.pdf"
                    page_doc.save(str(page_path))
                    page_doc.close()
                    try:
                        page_result = converter.convert(str(page_path))
                        md_parts.append(page_result.document.export_to_markdown())
                    except Exception as page_exc:
                        print(f"    Skipping page {page_idx + 1}: {page_exc}")

    src_doc.close()

    md_text = "\n\n".join(md_parts)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8")

    size_kb = md_path.stat().st_size / 1024
    print(f"Done. Written {len(md_text):,} characters ({size_kb:,.1f} KB) -> {md_path}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chunk_size = DEFAULT_CHUNK_SIZE

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--chunk-size" and i + 2 < len(sys.argv):
            try:
                chunk_size = int(sys.argv[i + 2])
            except ValueError:
                print("ERROR: --chunk-size must be an integer.")
                sys.exit(1)

    if len(args) < 1:
        print("Usage: python convert_pdf_to_md_docling.py <input.pdf> [output.md] [--chunk-size N]")
        sys.exit(1)

    pdf_path = Path(args[0]).resolve()
    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)
    if pdf_path.suffix.lower() != ".pdf":
        print(f"ERROR: Expected a .pdf file, got: {pdf_path.suffix}")
        sys.exit(1)

    md_path = Path(args[1]).resolve() if len(args) >= 2 else pdf_path.with_suffix(".md")

    convert(pdf_path, md_path, chunk_size=chunk_size)


if __name__ == "__main__":
    main()
