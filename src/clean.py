import re
from pathlib import Path

IN = Path("data/text")
OUT = Path("data/clean")
OUT.mkdir(parents=True, exist_ok=True)

# Browser print header, e.g. "11/4/26, 11:44 AM" (maybe with more text after it)
DATE_HEADER = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[AP]M\s*(.*)$")
# Browser footer, e.g. "about:blank 3/13"
FOOTER = re.compile(r"about:blank\s*\d+/\d+")


def clean(text):
    kept = []
    skip_next = False
    for line in text.splitlines():
        if skip_next:  # the title line that follows a lone date header
            skip_next = False
            continue
        match = DATE_HEADER.match(line.strip())
        if match:
            if match.group(1) == "":  # header was alone, so the next line is the repeated title
                skip_next = True
            continue
        line = FOOTER.sub("", line).strip()
        if line == "about:blank":
            continue
        if re.fullmatch(r"\d+/\d+", line):  # a page number alone on its line
            continue
        kept.append(line)
    result = "\n".join(kept)
    return re.sub(r"\n{3,}", "\n\n", result).strip() + "\n"  # squash big blank gaps


for path in sorted(IN.glob("*.txt")):
    raw = path.read_text(encoding="utf-8")
    cleaned = clean(raw)
    (OUT / path.name).write_text(cleaned, encoding="utf-8")
    print(f"{path.name:<62}{len(raw):>8} -> {len(cleaned):>8}")