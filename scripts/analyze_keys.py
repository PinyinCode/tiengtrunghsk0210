# -*- coding: utf-8 -*-
r"""
analyze_keys.py
Phan tich tai sao nhieu key trong ai_m ""
nemonics.json khong            match Excel
"""

import os
import re
import json
import json sys
from collections import Counter


MN_countEMONIC_FILE = "data/ai_mnemonics.json"
FIXPY_FILE = "data/fixpy_datasets.json"


def load_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("ERROR: " + str(e), file=sys.stderr)
        return None


def normalize_key(hsk, stt, zh):
    hsk_str = str(hsk or "").strip().upper()
    stt_str = str(stt or "").strip()
    zh_str = str(zh or "").strip()

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
    print("=== ANALYZE KEYS ===", file=sys.stderr)

    mnemonics = load_json(MNEMONIC_FILE)
    fixpy_data = load_json(FIXPY_FILE)

    if not mnemonics or not fixpy_data:
        print("ERROR load file", file=sys.stderr)
        return 1

    vocab = fixpy_data.get("tu-vung", {}).get("data", [])

    # Tao set key chuan tu Excel
    correct_keys = set()
    for r in vocab:
        hsk = r.get("hsk", "")
        stt = r.get("stt_original", r.get("stt", ""))
        zh = r.get("zh", "")
        key = normalize_key(hsk, stt, zh)
        correct_keys.add(key)

    print("Tong key chuan: " + str(len(correct_keys)), file=sys.stderr)
    print("Tong key JSON: " + str(len(mnemonics)), file=sys.stderr)
    print("", file=sys.stderr)

    # Phan tich key trong JSON
    match_keys = []
    no_match_keys = []

    for key in mnemonics.keys():
        if key in correct_keys:
            match_keys.append(key)
        else:
            no_match_keys.append(key)

    print("=== PHAN LOAI ===", file=sys.stderr)
    print("Match Excel: " + str(len(match_keys)), file=sys.stderr)
    print("KHONG match: " + str(len(no_match_keys)), file=sys.stderr)
    print("", file=sys.stderr)

    # Thong ke HSK prefix cua key KHONG match
    hsk_counter = Counter()
    hsk_sample = {}

    for key in no_match_keys:
        parts = key.split("|")
        if len(parts) >= 1:
            hsk_part = parts[0].strip()
            hsk_counter[hsk_part] += 1
            if hsk_part not in hsk_sample:
                hsk_sample[hsk_part] = key

    print("=== HSK PREFIX CUA KEY KHONG MATCH ===", file=sys.stderr)
    for hsk, count in hsk_counter.most_common(30):
        sample = hsk_sample[hsk]
        print("  [" + hsk + "]: " + str(count) + " keys", file=sys.stderr)
        print("    Sample: " + sample, file=sys.stderr)
    print("", file=sys.stderr)

    # Thong ke HSK prefix cua key MATCH
    match_hsk_counter = Counter()
    for key in match_keys:
        parts = key.split("|")
        if len(parts) >= 1:
            match_hsk_counter[parts[0].strip()] += 1

    print("=== HSK PREFIX CUA KEY MATCH ===", file=sys.stderr)
    for hsk, count in match_hsk_counter.most_common(30):
        print("  [" + hsk + "]: " + str(count) + " keys", file=sys.stderr)
    print("", file=sys.stderr)

    # Thong ke HSK prefix cua Excel
    excel_hsk_counter = Counter()
    for r in vocab:
        hsk = r.get("hsk", "")
        if hsk:
            excel_hsk_counter[hsk] += 1

    print("=== HSK PREFIX TRONG EXCEL ===", file=sys.stderr)
    for hsk, count in excel_hsk_counter.most_common(30):
        print("  [" + hsk + "]: " + str(count) + " tu", file=sys.stderr)
    print("", file=sys.stderr)

    # So sanh HSK prefix: JSON KHONG match vs Excel
    print("=== SO SANH HSK PREFIX ===", file=sys.stderr)
    all_hsk = set(hsk_counter.keys()) | set(excel_hsk_counter.keys())
    for hsk in sorted(all_hsk):
        json_count = hsk_counter.get(hsk, 0)
        excel_count = excel_hsk_counter.get(hsk, 0)
        if json_count > 0 or excel_count > 0:
            status = > 0 and excel_count == 0:
                status = " <- JSON co, Excel KHONG"
            elif json_count == 0 and excel_count > 0:
                status = " <- Excel co, JSON KHONG"
            print("  [" + hsk + "]: JSON=" + str(json_count) + " | Excel=" + str(excel_count) + status, file=sys.stderr)

    # Luu 100 key khong match dau tien
    print("", file=sys.stderr)
    print("=== 100 KEY KHONG MATCH DAU TIEN ===", file=sys.stderr)
    for i, key in enumerate(no_match_keys[:100], 1):
        print(str(i) + ". " + key, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
