# -*- coding: utf-8 -*-
r"""
process_mnemonic_issue.py
Xử lý mnemonic từ GitHub Issue Form → update data/ai_mnemonics.json

Chạy bởi GitHub Actions khi có issue labeled 'mnemonic'.

Environment variables:
    ISSUE_BODY: nội dung body của issue
    ISSUE_NUMBER: số issue
    GITHUB_OUTPUT: file output của GitHub Actions
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

    # Split theo "### "
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

        # Bỏ dấu _No response_ của GitHub
        if field_value == '_No response_':
            field_value = ''

        data[field_name] = field_value

    return data


def clean_issue_field(value):
    """Làm sạch giá trị từ issue."""
    if not value:
        return ""
    # Bỏ markdown code block
    value = re.sub(r'^```\w*\n?', '', value)
    value = re.sub(r'\n?```$', '', value)
    return value.strip()


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
        print("⚠️  Load error: " + str(e), file=sys.stderr)
        return {}


def save_mnemonics(data):
    os.makedirs(os.path.dirname(MNEMONIC_FILE), exist_ok=True)
    with open(MNEMONIC_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════
#  GITHUB ACTIONS OUTPUT
# ═══════════════════════════════════════════════════════════════
def set_output(key, value):
    """Ghi output cho GitHub Actions."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            # Escape multiline
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

    # Parse
    fields = parse_issue_body(issue_body)

    # Lấy dữ liệu
    hsk = clean_issue_field(fields.get("HSK", "")).upper()
    stt = clean_issue_field(fields.get("STT", ""))
    zh = clean_issue_field(fields.get("Chữ Hán", ""))
    vi = clean_issue_field(fields.get("Nghĩa", ""))
    pinyin = clean_issue_field(fields.get("Pinyin", ""))
    radical = clean_issue_field(fields.get("Bộ thủ (tùy chọn)", ""))
    mnemonic = clean_issue_field(fields.get("Mẹo nhớ", ""))

    # Validate
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

    # Tạo key
    key = f"{hsk}|{stt}|{zh}"
    print(f"🔑 Key: {key}", file=sys.stderr)

    # Load data cũ
    mnemonics = load_mnemonics()
    old_count = len(mnemonics)

    # Kiểm tra trùng
    is_update = key in mnemonics

    # Update
    mnemonics[key] = mnemonic

    # Save
    save_mnemonics(mnemonics)
    new_count = len(mnemonics)

    # Output
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
