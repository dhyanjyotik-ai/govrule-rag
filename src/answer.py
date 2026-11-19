import csv
import getpass
import re
import sys
import anthropic
import mysql.connector
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-haiku-5-5"
K = 3  # how many top orders Claude gets to read

SYSTEM = (
    "You answer questions about Government of India Department of Personnel and "
    "Training orders. Use only the orders provided in the user's message. "
    "Give a short, direct answer in one or two sentences. Name the order or orders "
    "you used by their ORDER label. If the orders give different answers, say so "
    "and name each order. If the answer is not in the orders, reply exactly: "
    "Not found in the provided orders. Do not use outside knowledge."
)


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
texts = [r[1] for r in rows]
bm25 = BM25Okapi([tokenize(t) for t in texts])

with open("eval/questions.csv", encoding="utf-8", newline="") as f:
    questions = list(csv.DictReader(f))

out_rows = []
for q in questions:
    scores = bm25.get_scores(tokenize(q["question"]))
    order = sorted(range(len(names)), key=lambda i: scores[i], reverse=True)[:K]
    context = "\n\n".join(f"=== ORDER: {names[i]} ===\n{texts[i]}" for i in order)
    prompt = f"{context}\n\n=== QUESTION ===\n{q['question']}"
    try:
        reply = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = "".join(b.text for b in reply.content if b.type == "text").strip()
        if not answer:
            answer = "ERROR: no text in reply"
    except Exception as error:
        answer = f"ERROR: {error}"
    print(f"{q['id']:>3}  {answer}\n")
    out_rows.append({
        "id": q["id"],
        "type": q["type"],
        "question": q["question"],
        "reference_answer": q["answer"],
        "retrieved_orders": "; ".join(names[i] for i in order),
        "claude_answer": answer,
        "grade": "",
        "note": "",
    })

with open("eval/answers_bm25.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    writer.writeheader()
    writer.writerows(out_rows)
print("Saved eval/answers_bm25.csv")