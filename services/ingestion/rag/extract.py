import re
from pathlib import Path

import pymupdf


def extract_pdf(path: str | Path) -> list[str]:
    """Return one text string per page. Plain-text extraction: fine for prose,
    lossy for formulas/figures -- see README for upgrading to Marker/Mathpix."""
    doc = pymupdf.open(str(path))
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return pages


def parse_filename(path: str | Path) -> dict:
    """class10_ch06_triangles.pdf -> {'class_level': 10, 'chapter': 6, 'source': ...}
    NCERT's own filenames (e.g. jemh106.pdf) are cryptic, so rename files to this pattern."""
    name = Path(path).stem
    m = re.search(r"class(\d+)_ch(\d+)", name, re.I)
    return {
        "class_level": int(m.group(1)) if m else -1,
        "chapter": int(m.group(2)) if m else -1,
        "source": Path(path).name,
    }
