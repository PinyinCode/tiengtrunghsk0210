# -*- coding: utf-8 -*-
r"""
process_mnemonic_issue.py
Xử lý mnemonic từ GitHub Issue Form → update data/ai_mnemonics.json

Chạy bởi GitHub Actions khi có issue labeled 'mnemonic'.

Environment variables:
    ISSUE_BODY: nội dung body của issue
    ISSUE_NUMBER: số issue
    GITHUB_OUTPUT: file output của GitHub Actions

FIX (2026-10):
- Chuẩn hóa key có space: "HSK1" → "HSK 1"
- Match format key cũ trong file ai_mnemonics.json
"""

import os
import re
import json
import sys


MNEMONIC_FILE = "data/ai_mnemonics.json"


# ═══════════════════════════════════════════════════════════════
#  PARSE ISSUE BODY
# ═══════════════════════════════════════════════════════════════
def parse_issue_body(body):
    """
    Parse GitHub Issue Form. Format:
    ### Field Name
    value
    ### Field Name 2
    value 2
    """
    if not body:
        return {}

    sections = re.split(r'^###\s+', body, flags=re.MULTILINE)
    data = {}

    for section in sections:
        if not section.strip():
            continue

        lines = section.split('\n', 1)
        if len(lines) < 2:
            continue

        field_name = lines[0].strip()
        field_value = lines[1].strip()

        if field_value == '_No response_':
            field_value = ''

        data[field_name] = field_value

    return data


def clean_issue_field(value):
    """Làm sạch giá trị từ issue."""
    if not value:
        return ""
    value = re.sub(r'^```\w*\n?', '', value)
    value = re.sub(r'\n?```$', '', value)
    return value.strip()


# ═══════════════════════════════════════════════════════════════
#  CHUẨN HÓA KEY
# ═══════════════════════════════════════════════════════════════
def normalize_key(hsk, stt, zh):
    """
    Chuẩn hóa key có space format giống file cũ:
    "HSK1" → "HSK 1"
    "HSK7-9" → "HSK 7-9"
    
    Kết quả: "HSK 1|4|爸爸"
    """
    hsk_str = str(hsk or "").strip().upper()
    stt_str = str(stt or "").strip()
    zh_str = str(zh or "").strip()

    # Tách HSK và số
    m = re.match(r'^(HSK)\s*(\d+.*)$', hsk_str, re.IGNORECASE)
    if m:
        hsk_norm = m.group(1).upper() + " " + m.group(2).strip()
    else:
        hsk_norm = hsk_str

    return f"{hsk_norm}|{stt_str}|{zh_str}"


# ═══════════════════════════════════════════════════════════════
#  LOAD / SAVE JSON
# ═══════════════════════════════════════════════════════════════
def load_mnemonics():
    if not os.path.isfile(MNEMONIC_FILE):
        return {}
    try:
        with open(MNEMONIC_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print("WARN Load error: " + str(e), file=sys.stderr)
        return {}


def save_mnemonics(data):
    os.makedirs(os.path.dirname(MNEMONIC_FILE), exist_ok=True)
    with open(MNEMONIC_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════
#  GITHUB ACTIONS OUTPUT
# ═══════════════════════════════════════════════════════════════
def set_output(key, value):
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            if "\n" in str(value):
                delimiter = "EOF_MARKER"
                f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                f.write(f"{key}={value}\n")
    print(f"[OUTPUT] {key}={value}", file=sys.stderr)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")

    print(f"📥 Xử lý issue #{issue_number}", file=sys.stderr)

    if not issue_body:
        set_output("status", "error")
        set_output("message", "Issue body rỗng")
        return 1

    fields = parse_issue_body(issue_body)

    hsk = clean_issue_field(fields.get("HSK", "")).upper()
    stt = clean_issue_field(fields.get("STT", ""))
    zh = clean_issue_field(fields.get("Chữ Hán", ""))
    vi = clean_issue_field(fields.get("Nghĩa", ""))
    pinyin = clean_issue_field(fields.get("Pinyin", ""))
    radical = clean_issue_field(fields.get("Bộ thủ (tùy chọn)", ""))
    mnemonic = clean_issue_field(fields.get("Mẹo nhớ", ""))

    errors = []
    if not hsk:
        errors.append("Thiếu HSK")
    elif not re.match(r'^HSK[1-9]$|^HSK[7-9]-[7-9]$|^HSK7-9$', hsk):
        errors.append(f"HSK không hợp lệ: {hsk}")
    if not stt:
        errors.append("Thiếu STT")
    if not zh:
        errors.append("Thiếu Chữ Hán")
    if not mnemonic:
        errors.append("Thiếu Mẹo nhớ")

    if errors:
        set_output("status", "error")
        set_output("message", " | ".join(errors))
        print(f"❌ Validation errors: {errors}", file=sys.stderr)
        return 1

    # ⭐ TẠO KEY CÓ SPACE
    key = normalize_key(hsk, stt, zh)
    print(f"🔑 Key (normalized): {key}", file=sys.stderr)

    mnemonics = load_mnemonics()
    old_count = len(mnemonics)

    # ⭐ XÓA KEY SAI FORMAT NẾU CÓ (không space)
    key_wrong = f"{hsk}|{stt}|{zh}"  # "HSK1|4|爸爸"
    if key_wrong in mnemonics and key_wrong != key:
        del mnemonics[key_wrong]
        print(f"🗑️ Đã xóa key sai format: {key_wrong}", file=sys.stderr)

    # ⭐ XÓA KEY CÓ SPACE KHÁC NẾU CÓ (lowercase)
    key_lower_wrong = f"{hsk.lower()}|{stt}|{zh}"
    if key_lower_wrong in mnemonics and key_lower_wrong != key:
        del mnemonics[key_lower_wrong]
        print(f"🗑️ Đã xóa key lowercase: {key_lower_wrong}", file=sys.stderr)

    is_update = key in mnemonics

    # Update
    mnemonics[key] = mnemonic

    save_mnemonics(mnemonics)
    new_count = len(mnemonics)

    action = "cập nhật" if is_update else "thêm mới"
    set_output("status", "success")
    set_output("action", action)
    set_output("key", key)
    set_output("old_count", str(old_count))
    set_output("new_count", str(new_count))
    set_output("total", str(new_count))

    print(f"✅ Đã {action}: {key}", file=sys.stderr)
    print(f"📊 Tổng: {old_count} → {new_count}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
