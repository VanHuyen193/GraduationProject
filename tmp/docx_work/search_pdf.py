from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pdf_path = Path(sys.argv[1])
    terms = sys.argv[2:]
    reader = PdfReader(pdf_path)
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").replace("\u00a0", " ")
        folded = text.casefold()
        hits = [term for term in terms if term.casefold() in folded]
        if hits:
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            printed = next((line for line in reversed(lines) if line.isdigit()), "?")
            print(f"PDF_PAGE={index}; PRINTED={printed}; HITS={hits}")
            for line in lines[:12]:
                print(f"  {line}")


if __name__ == "__main__":
    main()
