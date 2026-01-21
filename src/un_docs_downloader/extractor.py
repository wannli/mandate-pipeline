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
