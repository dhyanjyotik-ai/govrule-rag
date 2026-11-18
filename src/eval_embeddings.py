import csv
import getpass
import mysql.connector
from sentence_transformers import SentenceTransformer, util

CHUNK_WORDS = 120   # words in each chunk
STEP = 80           # move forward 80 words, so chunks overlap by 40


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


password = getpass.getpass("Password for govrule_user: ")
conn = mysql.connector.connect(
    host="localhost", user="govrule_user", password=password, database="govrule"
)
cur = conn.cursor()
cur.execute("SELECT filename, full_text FROM documents ORDER BY doc_id")
rows = cur.fetchall()
conn.close()

names = [r[0].replace(".txt", "") for r in rows]

chunk_texts = []
chunk_doc = []
for name, row in zip(names, rows):
    for chunk in make_chunks(row[1]):
        chunk_texts.append(chunk)
        chunk_doc.append(name)
print(f"{len(names)} documents cut into {len(chunk_texts)} chunks")

model = SentenceTransformer("all-MiniLM-L6-v2")
chunk_emb = model.encode(chunk_texts, convert_to_tensor=True, show_progress_bar=True)

with open("eval/questions.csv", encoding="utf-8", newline="") as f:
    questions = list(csv.DictReader(f))

top1_hits = 0
top3_hits = 0
for q in questions:
    q_emb = model.encode(q["question"], convert_to_tensor=True)
    sims = util.cos_sim(q_emb, chunk_emb)[0].tolist()
    best = {}
    for doc, sim in zip(chunk_doc, sims):
        if doc not in best or sim > best[doc]:
            best[doc] = sim
    ranked = sorted(best.items(), key=lambda pair: pair[1], reverse=True)
    top3 = [name for name, score in ranked[:3]]
    expected = set(q["expected_docs"].split(";"))
    ok1 = top3[0] in expected
    ok3 = any(name in expected for name in top3)
    top1_hits += ok1
    top3_hits += ok3
    print(f"{q['id']:>3} {q['type']:<9} top1={'OK  ' if ok1 else 'MISS'} top3={'OK  ' if ok3 else 'MISS'} got: {top3[0]}")

total = len(questions)
print(f"\nTop-1: {top1_hits}/{total}   Top-3: {top3_hits}/{total}")