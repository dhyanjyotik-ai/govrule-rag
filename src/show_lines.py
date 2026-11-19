import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
path, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
with open(path, encoding="utf-8") as f:
    for number, line in enumerate(f, start=1):
        if start <= number <= end:
            print(number, line.rstrip().replace("\xa0", " "))