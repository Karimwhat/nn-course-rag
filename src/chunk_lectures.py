from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Dict, Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OCR_INPUT_DIR = PROJECT_ROOT / "data" / "ocr_outputs"
CHUNKS_OUTPUT_DIR = PROJECT_ROOT / "data" / "chunks"
CHUNKS_OUTPUT_FILE = CHUNKS_OUTPUT_DIR / "lecture_chunks.json"


PAGE_MARKER_PATTERN = re.compile(r"COMP\s+4107\s+W2026\s+Page\s+(\d+)", re.IGNORECASE)
ALT_PAGE_MARKER_PATTERN = re.compile(
    r"\*\s*.+?\|\s*(\d+)\s*\*",
    re.IGNORECASE
)
TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
DATE_PATTERN = re.compile(
    r"^\*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+20\d{2})\b.*\*$",
    re.MULTILINE
)


def extract_title(text: str, fallback_name: str) -> str:
    match = TITLE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return fallback_name


def extract_date(text: str) -> Optional[str]:
    """
    Looks for the first italicized line near the top, e.g.
    *March 2, 2026 | 8:40 AM*
    """
    match = DATE_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return None


def split_into_pages(text: str) -> List[Dict[str, object]]:
    """
    Splits OCR markdown into page-level chunks using the page marker:
    COMP 4107 W2026 Page X

    Returns a list like:
    [
        {"page_number": 1, "text": "..."},
        {"page_number": 2, "text": "..."},
        ...
    ]
    """
    matches = list(PAGE_MARKER_PATTERN.finditer(text))


    # Try alternate page marker format if primary fails
    if not matches:
        matches = list(ALT_PAGE_MARKER_PATTERN.finditer(text))

    pages: List[Dict[str, object]] = []

    if not matches:
        # Fallback: whole document as one chunk if no page markers found
        cleaned = text.strip()
        if cleaned:
            pages.append({
                "page_number": 1,
                "text": cleaned,
            })
        return pages

    start_idx = 0

    for i, match in enumerate(matches):
        page_number = int(match.group(1))
        marker_start = match.start()

        # Everything before the first page marker belongs to page 1
        if i == 0:
            page_text = text[:match.start()].strip()
            if page_text:
                pages.append({
                    "page_number": page_number,
                    "text": clean_page_text(page_text),
                })
        else:
            prev_match = matches[i - 1]
            prev_page_number = int(prev_match.group(1))
            prev_marker_end = prev_match.end()
            page_text = text[start_idx:marker_start].strip()
            if page_text:
                pages.append({
                    "page_number": prev_page_number,
                    "text": clean_page_text(page_text),
                })

        start_idx = match.end()

    # Add the final page content after the last page marker
    last_match = matches[-1]
    last_page_number = int(last_match.group(1))
    final_text = text[last_match.end():].strip()
    if final_text:
        pages.append({
            "page_number": last_page_number,
            "text": clean_page_text(final_text),
        })

    # Deduplicate any accidental duplicate page entries while preserving order
    deduped_pages: List[Dict[str, object]] = []
    seen = set()

    for page in pages:
        key = (page["page_number"], page["text"])
        if key not in seen:
            seen.add(key)
            deduped_pages.append(page)

    return deduped_pages


def clean_page_text(text: str) -> str:
    """
    Light cleanup only.
    We do NOT want to over-clean and accidentally lose useful structure.
    """
    # Remove trailing separators like --- or ***
    text = re.sub(r"^\s*(---|\*\*\*)\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

chunk_number = 0

def chunk_file(md_path: Path) -> List[Dict[str, object]]:
    raw_text = md_path.read_text(encoding="utf-8")
    lecture_title = extract_title(raw_text, md_path.stem)
    lecture_date = extract_date(raw_text)
    pages = split_into_pages(raw_text)

    chunks: List[Dict[str, object]] = []
    page_counts = {}

    global chunk_number

    for page in pages:
        page_number = int(page["page_number"])
        page_text = str(page["text"]).strip()
        if not page_text:
            continue

        chunk_number += 1
        
        page_counts[page_number] = page_counts.get(page_number, 0) + 1
        within_page_idx = page_counts[page_number]

        chunk = {
            "chunk_id": f"{md_path.stem}_p{page_number}_c{within_page_idx}",
            "source_file": md_path.name,
            "source_path": str(md_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "lecture_title": lecture_title,
            "lecture_date": lecture_date,
            "page_number": page_number,
            "text": page_text,
            "chunk_number": chunk_number
        }
        chunks.append(chunk)

    return chunks


def main() -> None:
    if not OCR_INPUT_DIR.exists():
        raise FileNotFoundError(f"OCR input directory not found: {OCR_INPUT_DIR}")

    CHUNKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(OCR_INPUT_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No markdown files found in: {OCR_INPUT_DIR}")

    all_chunks: List[Dict[str, object]] = []

    for md_file in md_files:
        file_chunks = chunk_file(md_file)
        all_chunks.extend(file_chunks)
        print(f"Processed {md_file.name}: {len(file_chunks)} chunks")

    with CHUNKS_OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_chunks)} total chunks to:")
    print(CHUNKS_OUTPUT_FILE)


if __name__ == "__main__":
    main()