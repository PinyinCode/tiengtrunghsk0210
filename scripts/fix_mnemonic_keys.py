# -*- coding: utf-8 -*-
r"""
fix_mnemonic_keys.py
Quet ai_mnemonics.json, tim key SAI FORMAT, so sanh voi Excel, fix lai.
"""

import os
import re
import json
import sys


MNEMONIC_FILE = "data/ai_mnemonics.json"
FIXPY_FILE = "data/fixpy_datasets.json"


def load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("ERROR load " + path + ": " + str(e), file=sys.stderr)
        return None


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_key(hsk, stt, zh):
    """Tao key chuan co space: HSK 1|4|爸爸 | 爸"""
    hsk_str = str(hsk or "").strip().upper()
    stt_str = str(stt or "").strip()
    zh_str = str(zh or "").strip()

    # HSK 7-9 voi sheet
    m79 = re.match(r'^HSK\s*7-9\s*\(\s*([123])\s*\)$', hsk_str, re.IGNORECASE)
    if m79:
        num = m79.group(1)
        if re.search(r'\(\s+2\s*\)', hsk_str):
            hsk_norm = "HSK 7-9 ( 2)"
        else:
            hsk_norm = "HSK 7-9 (" + num + ")"
        return hsk_norm + "|" + stt_str + "|" + zh_str

    if re.match(r'^HSK\s*7-9$', hsk_str, re.IGNORECASE):
        return "HSK 7-9|" + stt_str + "|" + zh_str

    m = re.match(r'^(HSK)\s*(\d+)$', hsk_str, re.IGNORECASE)
    if m:
        hsk_norm = m.group(1).upper() + " " + m.group(2)
        return hsk_norm + "|" + stt_str + "|" + zh_str

    return hsk_str + "|" + stt_str + "|" + zh_str


def main():
    print("=== FIX MNEMONIC KEYS ===", file=sys.stderr)

    mnemonics = load_json(MNEMONIC_FILE)
    if not mnemonics:
        print("ERROR: Khong doc duoc " + MNEMONIC_FILE, file=sys.stderr)
        return 1

    fixpy_data = load_json(FIXPY_FILE)
    if not fixpy_data:
        print("ERROR: Khong doc duoc " + FIXPY_FILE, file=sys.stderr)
        return 1

    print("Tong entries trong JSON: " + str(len(mnemonics)), file=sys.stderr)

    # Lay danh sach tu vung tu Excel (da doc sang fixpy)
    vocab = fixpy_data.get("tu-vung", {}).get("data", [])
    print("Tong tu vung trong Excel: " + str(len(vocab)), file=sys.stderr)

    # Tao dict: key_chuan -> record
    correct_keys = {}
    for r in vocab:
        hsk = r.get("hsk", "")
        stt = r.get("stt_original", r.get("stt", ""))
        zh = r.get("zh", "")
        key = normalize_key(hsk, stt, zh)
        correct_keys[key] = r

    print("Tong key chuan: " + str(len(correct_keys)), file=sys.stderr)
    print("", file=sys.stderr)

    # Tim key trong JSON sai format
    fixed_keys = {}
    wrong_keys = []
    ok_count = 0
    fixed_count = 0

    for old_key, mnemonic in mnemonics.items():
        # Kiem tra key nay co dung format chuan khong
        if old_key in correct_keys:
            # Dung format
            fixed_keys[old_key] = mnemonic
            ok_count += 1
            continue

        # Key sai format -> thu doan
        parts = old_key.split("|")
        if len(parts) != 3:
            # Key hoan toan sai -> giu nguyen
            fixed_keys[old_key] = mnemonic
            continue

        hsk_part = parts[0].strip()
        stt_part = parts[1].strip()
        zh_part = parts[2].strip()

        # Chuan hoa lai key
        new_key = normalize_key(hsk_part, stt_part, zh_part)

        if new_key != old_key:
            # Key sai -> fix
            fixed_keys[new_key] = mnemonic
            wrong_keys.append({
                "old": old_key,
                "new": new_key,
                "match_excel": new_key in correct_keys
            })
            fixed_count += 1
        else:
            # Key dung format nhung khong co trong Excel (co the la tu cu)
            fixed_keys[old_key] = mnemonic

    print("=== KET QUA ===", file=sys.stderr)
    print("Key dung format: " + str(ok_count), file=sys.stderr)
    print("Key sai format da fix: " + str(fixed_count), file=sys.stderr)
    print("", file=sys.stderr)

    # In 20 key sai dau tien
    if wrong_keys:
        print("=== 20 KEY SAI DAU TIEN ===", file=sys.stderr)
        for i, item in enumerate(wrong_keys[:20], 1):
            match_status = "MATCH Excel" if item["match_excel"] else "KHONG co trong Excel"
            print(str(i) + ". [" + item["old"] + "]", file=sys.stderr)
            print("   -> [" + item["new"] + "] (" + match_status + ")", file=sys.stderr)

    # Luu file moi
    save_json(MNEMONIC_FILE, fixed_keys)

    print("", file=sys.stderr)
    print("Da luu " + MNEMONIC_FILE + " (" + str(len(fixed_keys)) + " entries)", file=sys.stderr)

    # Ghi output cho GitHub Actions
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("total=" + str(len(mnemonics)) + "\n")
            f.write("ok=" + str(ok_count) + "\n")
            f.write("fixed=" + str(fixed_count) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
