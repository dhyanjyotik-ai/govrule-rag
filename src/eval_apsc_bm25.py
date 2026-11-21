import csv
import re
from pathlib import Path
from rank_bm25 import BM25Okapi

TEXT = Path("data/apsc/text")
QUESTIONS = Path("eval/apsc_questions.csv")
OUT = Path("eval/apsc_retrieval_bm25.csv")


def clean(text):
    return text.replace("\xa0", " ").lower()


def tokens(text):
    return re.findall(r"[a-z0-9]+", clean(text))


# Load every notice: the file name without .pdf is the notice name.
names = []
corpus = []
for path in sorted(TEXT.glob("*.txt")):
    names.append(path.stem)
    corpus.append(tokens(path.read_text(encoding="utf-8")))

bm25 = BM25Okapi(corpus)

rows = list(csv.DictReader(open(QUESTIONS, encoding="utf-8-sig")))
results = []
top1 = top3 = counted = strict1 = 0

for row in rows:
    wanted = [s.strip() for s in row["source_files"].split(";")]
    if wanted == ["(none)"]:
        print(f"Q{row['id']}: no right notice exists (skipped)")
        continue
    scores = bm25.get_scores(tokens(row["question"]))
    ranking = sorted(range(len(names)), key=lambda i: scores[i], reverse=True)
    top_names = [names[i] for i in ranking[:3]]
    best_rank = next(
        (r + 1 for r, i in enumerate(ranking) if names[i] in wanted), None
    )
    counted += 1
    main_rank = next(
        (r + 1 for r, i in enumerate(ranking) if names[i] == wanted[0]), None
    )
    if main_rank == 1:
        strict1 += 1
    if best_rank == 1:
        top1 += 1
    if best_rank is not None and best_rank <= 3:
        top3 += 1
    print(f"Q{row['id']} ({row['type']}): any right notice at rank {best_rank}; main notice at rank {main_rank}")
    print(f"    top 3: {top_names}")
    results.append(
        {
            "id": row["id"],
            "type": row["type"],
            "best_rank": best_rank,
            "top3": " | ".join(top_names),
        }
    )

print()
print(f"Questions scored: {counted}")
print(f"Top-1: {top1} of {counted}")
print(f"Top-3: {top3} of {counted}")
print(f"Main notice first: {strict1} of {counted}")

with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["id", "type", "best_rank", "top3"])
    w.writeheader()
    w.writerows(results)