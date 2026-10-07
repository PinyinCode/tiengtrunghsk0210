# -*- coding: utf-8 -*-
"""Re-format JSON: nen file + don newline thua - KHONG goi API."""
import json
import os
import re
import shutil
import sys
from datetime import datetime


def find_file(name):
    candidates = [
        "data/" + name,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", name),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def clean_newlines(s):
    """Don newline thua + space/tab thua trong string."""
    if not isinstance(s, str):
        return s

    # Gop 3+ newline thanh 2 newline
    s = re.sub(r'\n{3,}', '\n\n', s)

    # Xoa space/tab truoc \n
    s = re.sub(r'[ \t]+\n', '\n', s)

    # Xoa space/tab sau \n
    s = re.sub(r'\n[ \t]+', '\n', s)

    # Xoa space cuoi string
    s = s.rstrip()

    return s


def reformat(path, clean_nl=True):
    if not os.path.isfile(path):
        print("  [SKIP] Khong thay: " + path)
        return False

    old_size = os.path.getsize(path)
    print("  Truoc: " + str(round(old_size / 1024 / 1024, 2)) + " MB")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("  [ERROR] Khong doc duoc: " + str(e))
        return False

    # Dem so entry bi sua newline
    fixed_nl = 0
    if clean_nl and isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                new_v = clean_newlines(v)
                if new_v != v:
                    data[k] = new_v
                    fixed_nl += 1

    # Backup truoc khi ghi
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path + ".bak_" + ts
    try:
        shutil.copy2(path, backup)
        print("  Backup: " + os.path.basename(backup))
    except Exception as e:
        print("  [WARN] Khong backup duoc: " + str(e))

    # Ghi file nen
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    new_size = os.path.getsize(path)
    print("  Sau:   " + str(round(new_size / 1024 / 1024, 2)) + " MB")
    print("  Giam:  " + str(round((old_size - new_size) / 1024 / 1024, 2)) + " MB")

    if clean_nl:
        print("  Clean newline: " + str(fixed_nl) + " entries")

    return True


def main():
    targets = [
        "ai_mnemonics.json",
        "similar_chars.json",
        "fixpy_datasets.json",
        "all_datasets.json",
    ]

    print("=" * 60)
    print("REFORMAT JSON - NEN + DON NEWLINE")
    print("=" * 60)

    done = 0
    for name in targets:
        path = find_file(name)
        if not path:
            print("")
            print("=== " + name + " ===")
            print("  [SKIP] Khong tim thay file")
            continue

        print("")
        print("=== " + path + " ===")
        if reformat(path, clean_nl=True):
            done += 1

    print("")
    print("=" * 60)
    print("Hoan tat: " + str(done) + " file")
    print("=" * 60)


if __name__ == "__main__":
    main()
