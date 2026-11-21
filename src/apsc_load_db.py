import csv
import getpass
import re
from datetime import date
from pathlib import Path
import mysql.connector

TEXT = Path("data/apsc/text")
CATALOG = Path("data/apsc/catalog.csv")

password = getpass.getpass("Password for govrule_user: ")
conn = mysql.connector.connect(
    host="localhost", user="govrule_user", password=password, database="govrule"
)
cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS apsc_documents (
        doc_id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(200) NOT NULL UNIQUE,
        advt_no VARCHAR(20) NOT NULL,
        doc_type VARCHAR(20) NOT NULL,
        doc_date DATE NOT NULL,
        date_source VARCHAR(80),
        post VARCHAR(400),
        changes_earlier TEXT,
        full_text LONGTEXT NOT NULL
    ) CHARACTER SET utf8mb4"""
)
cur.execute("TRUNCATE TABLE apsc_documents")  # so re-running never duplicates


def clean(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


with open(CATALOG, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    text = clean((TEXT / (Path(r["file"]).stem + ".txt")).read_text(encoding="utf-8"))
    cur.execute(
        "INSERT INTO apsc_documents "
        "(filename, advt_no, doc_type, doc_date, date_source, post, changes_earlier, full_text) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            r["file"],
            r["advt_no"],
            r["doc_type"],
            date.fromisoformat(r["doc_date"]),
            r["date_source"],
            r["post"],
            r["changes_earlier_notice"] or None,
            text,
        ),
    )
    print(f"loaded {r['file']}")

conn.commit()

cur.execute(
    "SELECT advt_no, COUNT(*) FROM apsc_documents GROUP BY advt_no ORDER BY advt_no"
)
print("\nDocuments per advertisement:")
for advt_no, n in cur.fetchall():
    print(f"  {advt_no}: {n}")
cur.close()
conn.close()