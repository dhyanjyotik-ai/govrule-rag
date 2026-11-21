import subprocess
import tempfile
from pathlib import Path

import pymupdf

RAW = Path("data/apsc/raw")
OUT = Path("data/apsc/text_psm4")
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
OUT.mkdir(parents=True, exist_ok=True)

for pdf_path in sorted(RAW.glob("*.pdf")):
    out_path = OUT / (pdf_path.stem + ".txt")
    if out_path.exists():
        print(f"skip (already done): {pdf_path.name}")
        continue
    doc = pymupdf.open(pdf_path)
    page_texts = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, page in enumerate(doc):
            img_path = Path(tmp) / f"page{i}.png"
            page.get_pixmap(dpi=300).save(img_path)
            result = subprocess.run(
                [TESS, str(img_path), "stdout", "-l", "eng", "--psm", "4"],
                capture_output=True, text=True, encoding="utf-8",
            )
            page_texts.append(result.stdout)
    ocr_text = "\n".join(page_texts)
    out_path.write_text(ocr_text, encoding="utf-8")
    print(f"{pdf_path.name}: {len(doc)} pages, {len(ocr_text)} characters")