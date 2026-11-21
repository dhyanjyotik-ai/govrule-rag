import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# A pattern that matches order numbers such as 14028/1/2019-Estt or 11022/01/2021-AIS
PATTERN = re.compile(r"\d{1,6}/\d{1,4}/\d{2,4}-[A-Za-z]+")

docs = {}
for path in sorted(glob.glob("data/clean/*.txt")):
    name = os.path.basename(path).replace(".txt", "")
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    head = "\n".join(lines[:30])
    own = PATTERN.search(head)
    cited = set(PATTERN.findall("\n".join(lines)))
    docs[name] = (own.group(0) if own else None, cited)

print("OWN NUMBERS")
for name, (own, cited) in docs.items():
    print(f"  {name}: {own}  (cites {len(cited)} order numbers)")

print("\nLINKS BETWEEN THESE 12 ORDERS")
found = False
for a, (own_a, cited_a) in docs.items():
    for b, (own_b, cited_b) in docs.items():
        if a != b and own_b and own_b in cited_a:
            print(f"  {a} cites {b}  ({own_b})")
            found = True
if not found:
    print("  none found")