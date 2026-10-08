import os
import re
import json
import sys
from collections import Counter

MNEMONIC_FILE = "data/ai_mnemonics.json"
FIXPY_FILE = "data/fixpy_datasets.json"

def load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    mnemonics = load_json(MNEMONIC_FILE)
    fixpy = load_json(FIXPY_FILE)
    if not mnemonics or not fixpy:
        print("ERROR: file not found", file=sys.stderr)
        return 1

    vocab = fixpy.get("tu-vung", {}).get("data", [])
    correct = set()
    for r in vocab:
        hsk = str(r.get("hsk", "")).strip()
        stt = str(r.get("stt_original", r.get("stt", ""))).strip()
        zh = str(r.get("zh", "")).strip()
        correct.add(hsk + "|" + stt + "|" + zh)

    print("Tong key JSON: " + str(len(mnemonics)), file=sys.stderr)
    print("Tong key Excel: " + str(len(correct)), file=sys.stderr)

    match = 0
    no_match = 0
    prefix_json = Counter()
    prefix_excel = Counter()

    for key in mnemonics.keys():
        parts = key.split("|")
        p = parts[0].strip() if parts else ""
        prefix_json[p] += 1
        if key in correct:
            match += 1
        else:
            no_match += 1

    for r in vocab:
        hsk = str(r.get("hsk", "")).strip()
        if hsk:
            prefix_excel[hsk] += 1

    print("Match: " + str(match), file=sys.stderr)
    print("No match: " + str(no_match), file=sys.stderr)
    print("", file=sys.stderr)
    print("=== PREFIX TRONG JSON (khong match) ===", file=sys.stderr)
    for p, c in prefix_json.most_common(20):
        print("[" + p + "]: " + str(c), file=sys.stderr)
    print("", file=sys.stderr)
    print("=== PREFIX TRONG EXCEL ===", file=sys.stderr)
    for p, c in prefix_excel.most_common(20):
        print("[" + p + "]: " + str(c), file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
