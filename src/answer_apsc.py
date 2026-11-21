import csv
import re
import sys
from pathlib import Path

import anthropic
from rank_bm25 import BM25Okapi

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MODEL = "claude-haiku-5-5"
K = 3
TEXT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/apsc/text")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("eval/apsc_answers.csv")
QUESTIONS = Path("eval/apsc_questions.csv")

BASE_RULES = (
    "You answer questions about public notices of the Assam Public Service "
    "Commission. Answer only from the notices given. Say which notice "
    "(by its number in the list) your answer comes from. If the notices do "
    "not contain the answer, reply exactly: Not found in the provided notices."
)
AMEND_RULES = (
    " The notices are listed in date order, oldest first, with their dates. "
    "When a later notice changes something stated in an earlier notice "
    "(a date, a number of posts, a stay), the later notice is the one that "
    "counts. Give the current fact and, if useful, mention what it replaced."
)


def clean(text):
    return text.replace("\xa0", " ")


def tokens(text):
    return re.findall(r"[a-z0-9]+", clean(text).lower())


def parse_name(name):
    m = re.match(r"advt-(\d+)-(\d{4})_(\d{4}-\d{2}-\d{2})_(\w+)", name)
    return f"{m.group(1)}/{m.group(2)}", m.group(3), m.group(4)


names, texts, corpus = [], [], []
for path in sorted(TEXT.glob("*.txt")):
    names.append(path.stem)
    t = clean(path.read_text(encoding="utf-8"))
    texts.append(t)
    corpus.append(tokens(t))
bm25 = BM25Okapi(corpus)
client = anthropic.Anthropic()


def ask(system, notices, question):
    blocks = []
    for n, (label, body) in enumerate(notices, start=1):
        blocks.append(f"=== Notice {n}{label} ===\n{body}")
    user = "\n\n".join(blocks) + f"\n\nQuestion: {question}"
    reply = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in reply.content if b.type == "text").strip()


rows = list(csv.DictReader(open(QUESTIONS, encoding="utf-8-sig")))
out_rows = []

for row in rows:
    q = row["question"]
    scores = bm25.get_scores(tokens(q))
    ranking = sorted(range(len(names)), key=lambda i: scores[i], reverse=True)
    top = ranking[:K]

    # Plain mode: the top 3 in search order, no dates added.
    plain = [("", texts[i]) for i in top]
    plain_names = [names[i] for i in top]
    plain_answer = ask(BASE_RULES, plain, q)

    # Amendment-aware mode: add every notice of the same advertisements, oldest first.
    adverts = {parse_name(names[i])[0] for i in top}
    group = [i for i in range(len(names)) if parse_name(names[i])[0] in adverts]
    group.sort(key=lambda i: (parse_name(names[i])[0], parse_name(names[i])[1]))
    amend = [
        (f" (Advt. {parse_name(names[i])[0]}, dated {parse_name(names[i])[1]})", texts[i])
        for i in group
    ]
    amend_names = [names[i] for i in group]
    amend_answer = ask(BASE_RULES + AMEND_RULES, amend, q)

    for mode, given, ans in (
        ("plain", plain_names, plain_answer),
        ("amendment", amend_names, amend_answer),
    ):
        out_rows.append(
            {
                "id": row["id"],
                "type": row["type"],
                "question": q,
                "reference_answer": row["reference_answer"],
                "mode": mode,
                "notices_given": " | ".join(given),
                "claude_answer": ans,
                "grade": "",
                "note": "",
            }
        )
    print(f"Q{row['id']} done")

with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)
print(f"Saved {len(out_rows)} answers to {OUT}")