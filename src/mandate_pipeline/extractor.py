"""Extract text from PDF documents."""

import re
from pathlib import Path

import pymupdf


def extract_text(pdf_path: Path) -> str:
    """
    Extract full text from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text as a string
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text_parts = []
    
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())

    return "\n".join(text_parts)


def extract_operative_paragraphs(text: str) -> dict[int, str]:
    """
    Extract operative paragraphs from UN resolution text.

    Operative paragraphs are numbered sequentially (1, 2, 3, etc.)
    and typically start with action verbs like "Calls upon", "Requests",
    "Decides", etc.

    Args:
        text: Full text of the resolution

    Returns:
        Dictionary mapping paragraph numbers to their text content
    """
    paragraphs = {}

    # Pattern: number at start of line, followed by period and text
    # The paragraph continues until the next numbered paragraph or end
    pattern = r"^\s*(\d+)\.\s+(.+?)(?=^\s*\d+\.\s+|\Z)"

    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

    for num_str, content in matches:
        num = int(num_str)
        # Clean up the content: normalize whitespace
        cleaned = " ".join(content.split())
        paragraphs[num] = cleaned

    return paragraphs


def extract_title(text: str) -> str:
    """
    Extract a document title using simple heuristics.

    For resolutions: title is after "Resolution adopted by" with format "80/1. Title"
    For proposals: title is after "draft resolution" line, may span multiple lines.

    Args:
        text: Full text of the document

    Returns:
        Extracted title string or empty string if not found
    """
    lines = text.splitlines()
    stop_indices = []

    for idx, line in enumerate(lines):
        if re.match(r"^\s*\d+\.", line):
            stop_indices.append(idx)
            break

    stop_at = min(stop_indices) if stop_indices else len(lines)

    skip_prefixes = (
        "Distr.",
    )
    skip_regexes = [
        r"^United Nations$",
        r"^General Assembly$",
        r"^Security Council$",
        r"^[A-Z]{1,2}/[A-Z0-9./-]+$",
        r"^Agenda item",
        r"^Item\s+\d+",
        r"^\d{1,2}\s+\w+\s+\d{4}$",
        r"^\d{2}-\d{5}\s+\(E\).*$",
        r"^\*?\d{6,}\*?$",
        r"^Resolution adopted by",
        r"^\w+ session$",
        r"^(First|Second|Third|Fourth|Fifth|Sixth) Committee$",
        r"^A/RES",
        r"^Original:",
        r"^\[on the report of",
        r"^\[without reference to",
    ]

    # Patterns that indicate end of title (start of document body)
    title_end_patterns = [
        r"^The General Assembly",
        r"^The Security Council",
        r"^Recalling",
        r"^Reaffirming",
        r"^Noting",
        r"^Recognizing",
        r"^Welcoming",
        r"^Expressing",
        r"^Bearing in mind",
        r"^Having",
        r"^Mindful",
        r"^Concerned",
        r"^Convinced",
        r"^Guided by",
        r"^Taking note",
        r"^Pursuant to",
    ]

    def is_skip_line(candidate: str) -> bool:
        if candidate.startswith(skip_prefixes):
            return True
        if any(re.match(pattern, candidate) for pattern in skip_regexes):
            return True
        return False

    def is_title_end(candidate: str) -> bool:
        return any(re.match(pattern, candidate) for pattern in title_end_patterns)

    # For resolutions: find title after "Resolution adopted by" line
    # The title format is "80/1. Title..." and may span multiple lines
    resolution_start = None
    for idx, line in enumerate(lines[:stop_at]):
        if re.search(r"Resolution adopted by", line, re.IGNORECASE):
            resolution_start = idx + 1
            break

    if resolution_start is not None:
        # Look for resolution number format (e.g., "80/60. Title...")
        res_title_parts = []
        collecting_res_title = False
        for line in lines[resolution_start:stop_at]:
            candidate = line.strip()

            if re.match(r"^\d+/\d+\.\s+\S", candidate):
                res_title_parts.append(candidate)
                collecting_res_title = True
                continue

            if collecting_res_title:
                # Stop at empty line or body start
                if not candidate or is_title_end(candidate):
                    break
                # Continue collecting title lines
                res_title_parts.append(candidate)

        if res_title_parts:
            return " ".join(res_title_parts)

    # For proposals: find title after "draft resolution" line
    start_at = 0
    for idx, line in enumerate(lines[:stop_at]):
        if re.search(r"draft resolution", line, re.IGNORECASE):
            start_at = idx + 1
            break

    # Collect title parts (may span multiple lines)
    title_parts = []
    collecting = False

    for line in lines[start_at:stop_at]:
        candidate = line.strip()

        # Skip empty lines before title starts
        if not candidate and not collecting:
            continue

        # Check for resolution number format (e.g., "80/60. Title...")
        if re.match(r"^\d+/\d+\.\s+\S", candidate):
            return candidate

        # Skip header lines
        if is_skip_line(candidate):
            continue

        # Stop if we hit the document body
        if is_title_end(candidate):
            break

        # Empty line after title started means title is complete
        if not candidate and collecting:
            break

        # Found a title line
        if candidate:
            title_parts.append(candidate)
            collecting = True

    if title_parts:
        return " ".join(title_parts)

    return ""


def extract_agenda_items(text: str) -> list[str]:
    """
    Extract agenda item references from document text.

    Args:
        text: Full text of the document

    Returns:
        List of agenda item strings, e.g., ["Item 68", "Item 12A"]
    """
    items = []
    patterns = [
        r"\bAgenda item[s]?\s+(\d+[A-Za-z]?)\b",
        r"\bItem\s+(\d+[A-Za-z]?)\b",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            item = f"Item {match.group(1)}"
            if item not in items:
                items.append(item)

    return items


def find_symbol_references(text: str) -> list[str]:
    """
    Find references to A/.../L. symbols in document text.

    Args:
        text: Full text of the document

    Returns:
        List of referenced symbols (unique, in appearance order)
    """
    pattern = r"\bA(?:/[A-Z0-9.]+)+/L\.\d+\b"
    matches = re.finditer(pattern, text, re.IGNORECASE)
    symbols = []
    for match in matches:
        symbol = match.group(0).upper()
        if symbol not in symbols:
            symbols.append(symbol)
    return symbols
