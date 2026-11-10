import csv
import getpass
import re
import mysql.connector
from rank_bm25 import BM25Okapi


def tokenize(text):
    return re.findall(r"\w+", text.lower())


password = getpass.getpass("Password for govrule_user: ")
conn = mysql.connector.connect(
    host="localhost", user="govrule_user", password=password, database="govrule"
)
cur = conn.cursor()
cur.execute("SELECT filename, full_text FROM documents ORDER BY doc_id")
rows = cur.fetchall()
conn.close()

names = [r[0].replace(".txt", "") for r in rows]
bm25 = BM25Okapi([tokenize(r[1]) for r in rows])

with open("eval/questions.csv", encoding="utf-8", newline="") as f:
    questions = list(csv.DictReader(f))

top1_hits = 0
top3_hits = 0
for q in questions:
    scores = bm25.get_scores(tokenize(q["question"]))
    ranked = sorted(zip(names, scores), key=lambda pair: pair[1], reverse=True)
    top3 = [name for name, score in ranked[:3]]
    expected = set(q["expected_docs"].split(";"))
    ok1 = top3[0] in expected
    ok3 = any(name in expected for name in top3)
    top1_hits += ok1
    top3_hits += ok3
    print(f"{q['id']:>3} {q['type']:<9} top1={'OK  ' if ok1 else 'MISS'} top3={'OK  ' if ok3 else 'MISS'} got: {top3[0]}")

total = len(questions)
print(f"\nTop-1: {top1_hits}/{total}   Top-3: {top3_hits}/{total}")