from pathlib import Path
import fitz  # this is PyMuPDF

RAW = Path("data/raw")
OUT = Path("data/text")
OUT.mkdir(parents=True, exist_ok=True)

print(f"{'file':<62}{'pages':>6}{'chars':>9}{'per page':>10}  type")

for pdf_path in sorted(RAW.glob("*.pdf")):
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    text = "\n".join(pages)
    (OUT / (pdf_path.stem + ".txt")).write_text(text, encoding="utf-8")

    n_pages = len(doc)
    n_chars = len(text)
    per_page = n_chars // max(n_pages, 1)
    kind = "SCANNED?" if per_page < 100 else "digital"
    print(f"{pdf_path.name:<62}{n_pages:>6}{n_chars:>9}{per_page:>10}  {kind}")