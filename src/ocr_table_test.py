import subprocess
import tempfile
from pathlib import Path

import pymupdf

PDF = Path("data/apsc/raw/advt-22-2025_2026-08-03_notification.pdf")
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
WORDS = ["Mathematics", "Statistics", "Chemistry", "Horticulture"]

doc = pymupdf.open(PDF)
with tempfile.TemporaryDirectory() as tmp:
    for dpi in (300, 400):
        img = Path(tmp) / f"page_{dpi}.png"
        doc[0].get_pixmap(dpi=dpi).save(img)
        for psm in ("3", "4", "6", "11"):
            result = subprocess.run(
                [TESS, str(img), "stdout", "-l", "eng", "--psm", psm],
                capture_output=True, text=True, encoding="utf-8",
            )
            text = result.stdout.lower()
            found = [w for w in WORDS if w.lower() in text]
            print(f"dpi {dpi}, psm {psm}: found {found}")