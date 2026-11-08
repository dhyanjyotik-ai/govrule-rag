import getpass
from datetime import date
from pathlib import Path
import mysql.connector

CLEAN = Path("data/clean")
# Files that needed OCR (found on Day 2)
SCANNED = {"2019-06-20_leave-encashment-contract-officers"}

password = getpass.getpass("Password for govrule_user: ")
conn = mysql.connector.connect(
    host="localhost", user="govrule_user", password=password, database="govrule"
)
cur = conn.cursor()
cur.execute("TRUNCATE TABLE documents")  # empty the table so re-running never duplicates

for path in sorted(CLEAN.glob("*.txt")):
    text = path.read_text(encoding="utf-8")
    issue_date = date.fromisoformat(path.name[:10])  # the date at the start of the file name
    ref_no = next((l for l in text.splitlines() if l.startswith("No")), None)
    scanned = path.stem in SCANNED
    method = "tesseract_ocr" if scanned else "pymupdf"
    cur.execute(
        "INSERT INTO documents (filename, ref_no, issue_date, is_scanned, extraction_method, full_text) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (path.name, ref_no[:200] if ref_no else None, issue_date, scanned, method, text),
    )
    print(f"loaded {path.name}")

conn.commit()
cur.close()
conn.close()