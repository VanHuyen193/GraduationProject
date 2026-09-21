from __future__ import annotations

import sys
from docx import Document


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    document = Document(sys.argv[1])
    for index, table in enumerate(document.tables):
        widths = [round(cell.width / 914400, 3) for cell in table.rows[0].cells]
        print(
            f"table={index}; rows={len(table.rows)}; cols={len(table.columns)}; "
            f"autofit={table.autofit}; alignment={table.alignment}; widths_in={widths}"
        )


if __name__ == "__main__":
    main()
