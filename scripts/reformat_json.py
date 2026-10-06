# -*- coding: utf-8 -*-
"""Re-format JSON: bo indent, nen - KHONG goi API."""
import json
import os


def reformat(path):
    if not os.path.isfile(path):
        print(f"  [SKIP] Khong thay: {path}")
        return False

    old_size = os.path.getsize(path)
    print(f"  Truoc: {old_size/1024/1024:.2f} MB")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [ERROR] Khong doc duoc: {e}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    new_size = os.path.getsize(path)
    print(f"  Sau:   {new_size/1024/1024:.2f} MB")
    print(f"  Giam:  {(old_size - new_size)/1024/1024:.2f} MB")
    return True


if __name__ == "__main__":
    targets = [
        "data/ai_mnemonics.json",
        "data/similar_chars.json",
        "data/fixpy_datasets.json",
        "data/all_datasets.json",
    ]

    print("=" * 50)
    print("REFORMAT JSON - KHONG GOI API")
    print("=" * 50)

    done = 0
    for t in targets:
        if os.path.isfile(t):
            print(f"\n=== {t} ===")
            if reformat(t):
                done += 1

    print("\n" + "=" * 50)
    print(f"Hoan tat: {done} file")
    print("=" * 50)
