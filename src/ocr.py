import subprocess
import tempfile
from pathlib import Path
import pymupdf

RAW = Path("data/raw")
OUT = Path("data/text")
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

for pdf_path in sorted(RAW.glob("*.pdf")):
    doc = pymupdf.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    if len(text) // max(len(doc), 1) >= 100:
        continue  # has real text, so no OCR needed

    print(f"OCR needed: {pdf_path.name}")
    page_texts = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, page in enumerate(doc):
            img_path = Path(tmp) / f"page{i}.png"
            page.get_pixmap(dpi=300).save(img_path)
            result = subprocess.run(
                [TESS, str(img_path), "stdout", "-l", "eng"],
                capture_output=True, text=True, encoding="utf-8",
            )
            page_texts.append(result.stdout)

    ocr_text = "\n".join(page_texts)
    (OUT / (pdf_path.stem + ".txt")).write_text(ocr_text, encoding="utf-8")
    print(f"  pages: {len(doc)}, characters found: {len(ocr_text)}")