from pathlib import Path
from pypdf import PdfReader
from docx import Document as WordDocument
from openpyxl import load_workbook
import pytesseract
from PIL import Image

def extract_document(path: str, filename: str):
    ext = Path(filename).suffix.lower()
    pages = []
    if ext == ".pdf":
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages, 1):
            txt = page.extract_text() or ""
            # OCR scanned/image-only pages when normal PDF text extraction returns nothing.
            if not txt.strip():
                try:
                    from pdf2image import convert_from_path
                    image = convert_from_path(path, first_page=i, last_page=i, dpi=200)[0]
                    txt = pytesseract.image_to_string(image)
                except Exception as exc:
                    # Keep the page record and allow the worker to index other readable pages.
                    txt = ""
            pages.append({"page": i, "text": txt})
    elif ext == ".docx":
        doc = WordDocument(path)
        txt = "\n".join(p.text for p in doc.paragraphs)
        for table in doc.tables:
            txt += "\n" + "\n".join(" | ".join(c.text for c in row.cells) for row in table.rows)
        pages = [{"page": 1, "text": txt}]
    elif ext == ".xlsx":
        wb = load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            lines = []
            for row in ws.iter_rows(values_only=True):
                vals = [str(v) for v in row if v is not None]
                if vals: lines.append(" | ".join(vals))
            pages.append({"page": len(pages)+1, "text": f"Sheet: {ws.title}\n" + "\n".join(lines)})
    elif ext in {".txt", ".md", ".csv"}:
        pages = [{"page": 1, "text": Path(path).read_text(encoding="utf-8", errors="ignore")}]
    elif ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
        pages = [{"page": 1, "text": pytesseract.image_to_string(Image.open(path))}]
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    return pages
