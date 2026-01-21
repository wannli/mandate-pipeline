"""Download documents from the UN Official Document System."""

from pathlib import Path

import requests


def download_document(symbol: str, output_dir: Path, language: str = "en") -> Path:
    """
    Download a UN document by its symbol and save it locally.

    Args:
        symbol: UN document symbol (e.g., "A/RES/77/1")
        output_dir: Directory to save the downloaded file
        language: Language code (default: "en")

    Returns:
        Path to the downloaded file
    """
    # Build the download URL (API endpoint that redirects to PDF)
    url = build_download_url(symbol, language)

    # Download the file, following redirects
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()

    # Create safe filename from symbol (replace / with _)
    safe_name = symbol.replace("/", "_")
    output_path = Path(output_dir) / f"{safe_name}.pdf"

    # Save the file
    output_path.write_bytes(response.content)

    return output_path


def build_download_url(symbol: str, language: str = "en") -> str:
    """
    Build the download URL for a UN document.

    Args:
        symbol: UN document symbol (e.g., "A/RES/77/1")
        language: Language code (default: "en")

    Returns:
        URL to download the document PDF
    """
    # Use the UN documents API which redirects to the actual PDF
    return f"https://documents.un.org/api/symbol/access?s={symbol}&l={language}&t=pdf"
