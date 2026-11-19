import csv
import getpass
import sys
import mysql.connector
from sentence_transformers import SentenceTransformer, util

CHUNK_WORDS = 120
STEP = 80


def make_chunks(text):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + CHUNK_WORDS]))
        if start + CHUNK_WORDS >= len(words):
            break
        start += STEP
    return chunks


qid = sys.argv[1]
password = getpass.getpass("Password for govrule_user: ")
conn = mysql.connector.connect(
    host="localhost", user="govrule_user", password=password, database="govrule"
)
cur = conn.cursor()
cur.execute("SELECT filename, full_text FROM documents ORDER BY doc_id")
rows = cur.fetchall()
conn.close()

chunk_texts = []
chunk_doc = []
for filename, text in rows:
    for chunk in make_chunks(text):
        chunk_texts.append(chunk)
        chunk_doc.append(filename.replace(".txt", ""))

with open("eval/questions.csv", encoding="utf-8", newline="") as f:
    q = [row for row in csv.DictReader(f) if row["id"] == qid][0]
expected = q["expected_docs"].split(";")
print("QUESTION:", q["question"])

model = SentenceTransformer("all-MiniLM-L6-v2")
chunk_emb = model.encode(chunk_texts, convert_to_tensor=True)
q_emb = model.encode(q["question"], convert_to_tensor=True)
sims = util.cos_sim(q_emb, chunk_emb)[0].tolist()
ranked = sorted(zip(sims, chunk_doc, chunk_texts), key=lambda t: t[0], reverse=True)

print("\nTOP 5 CHUNKS FOUND")
for sim, doc, text in ranked[:5]:
    print(f"{sim:.3f}  {doc}\n    {text[:250]}\n")

print("BEST CHUNK OF EACH EXPECTED ORDER")
for exp in expected:
    for pos, (sim, doc, text) in enumerate(ranked, start=1):
        if doc == exp:
            print(f"rank {pos} of {len(ranked)}  {sim:.3f}  {doc}\n    {text[:250]}\n")
            break