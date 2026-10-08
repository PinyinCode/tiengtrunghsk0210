# -*- coding: utf-8 -*-
r"""
process_mnemonic_issue.py
Xử lý mnemonic từ GitHub Issue Form (5 phần) → update data/ai_mnemonics.json

FIX (2026-10):
- Nhận 5 phần riêng (Chiết tự, Âm thanh, Câu chuyện, Ví dụ, Liên quan)
- Tự ghép thành mẹo nhớ đúng format với emoji
- Chuẩn hóa key có space: "HSK1" → "HSK 1"
- Hỗ trợ HSK 7-9 (1)/(2)/(3)
- Tự động xóa key sai format cũ
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


def clean_field(value):
    """Làm sạch giá trị field."""
    if not value:
        return ""
    value = re.sub(r'^```\w*\n?', '', value)
    value = re.sub(r'\n?```$', '', value)
    return value.strip()


def get_field(fields, *keys):
    """Lấy field theo nhiều key có thể (dùng cho field có emoji)."""
    for key in keys:
        if key in fields:
            return clean_field(fields[key])
        # Thử match không dấu
        for fk in fields.keys():
            if key.lower() in fk.lower():
                return clean_field(fields[fk])
    return ""


# ═══════════════════════════════════════════════════════════════
#  CHUẨN HÓA KEY
# ═══════════════════════════════════════════════════════════════
def normalize_key(hsk, stt, zh):
    """
    Chuẩn hóa key có space:
    "HSK1" → "HSK 1"
    "HSK 7-9 (1)" → "HSK 7-9 (1)"
    "HSK 7-9 ( 2)" → "HSK 7-9 ( 2)"
    "HSK 7-9 (3)" → "HSK 7-9 (3)"
    """
    hsk_str = str(hsk or "").strip().upper()
    stt_str = str(stt or "").strip()
    zh_str = str(zh or "").strip()

    # HSK 7-9 với sheet number
    m79 = re.match(r'^HSK\s*7-9\s*\(\s*([123])\s*\)$', hsk_str, re.IGNORECASE)
    if m79:
        sheet_num = m79.group(1)
        if re.search(r'\(\s+2\s*\)', hsk_str):
            hsk_norm = "HSK 7-9 ( 2)"
        else:
            hsk_norm = "HSK 7-9 (" + sheet_num + ")"
        return f"{hsk_norm}|{stt_str}|{zh_str}"

    # HSK 7-9 không sheet
    if re.match(r'^HSK\s*7-9$', hsk_str, re.IGNORECASE):
        return f"HSK 7-9|{stt_str}|{zh_str}"

    # HSK 1-6
    m = re.match(r'^(HSK)\s*(\d+)$', hsk_str, re.IGNORECASE)
    if m:
        hsk_norm = m.group(1).upper() + " " + m.group(2)
        return f"{hsk_norm}|{stt_str}|{zh_str}"

    return f"{hsk_str}|{stt_str}|{zh_str}"


# ═══════════════════════════════════════════════════════════════
#  GHÉP MẸO NHỚ TỪ 5 PHẦN
# ═══════════════════════════════════════════════════════════════
def build_mnemonic(chiet_tu, am_thanh, cau_chuyen, vi_du, lien_quan):
    """
    Ghép 5 phần thành mẹo nhớ đúng format flashcard.

    Kết quả:
        💡 Chiết tự: ...
        📌 Âm thanh: ...
        🎬 Câu chuyện: ...
        📎 Ví dụ: ...
        🔗 Liên quan: ...
    """
    parts = []

    if chiet_tu:
        # Bỏ emoji nếu user đã gõ
        text = re.sub(r'^💡\s*Chiết tự\s*:?\s*', '', chiet_tu, flags=re.IGNORECASE)
        parts.append(f"💡 Chiết tự: {text.strip()}")

    if am_thanh:
        text = re.sub(r'^📌\s*Âm thanh\s*:?\s*', '', am_thanh, flags=re.IGNORECASE)
        parts.append(f"📌 Âm thanh: {text.strip()}")

    if cau_chuyen:
        text = re.sub(r'^🎬\s*Câu chuyện\s*:?\s*', '', cau_chuyen, flags=re.IGNORECASE)
        parts.append(f"🎬 Câu chuyện: {text.strip()}")

    if vi_du:
        text = re.sub(r'^📎\s*Ví dụ\s*:?\s*', '', vi_du, flags=re.IGNORECASE)
        parts.append(f"📎 Ví dụ: {text.strip()}")

    if lien_quan:
        text = re.sub(r'^🔗\s*Liên quan\s*:?\s*', '', lien_quan, flags=re.IGNORECASE)
        parts.append(f"🔗 Liên quan: {text.strip()}")

    return "\n".join(parts)


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

    # Debug: in ra tất cả field name để dễ kiểm tra
    print("=== FIELDS DETECTED ===", file=sys.stderr)
    for k in fields.keys():
        print(f"  [{k}]", file=sys.stderr)
    print("", file=sys.stderr)

    # Lấy dữ liệu cơ bản
    hsk = clean_field(fields.get("sysHSK", "")).upper()
    stt.st = clean_field(fields.get("STTderr", ""))
    zh = clean_field(fields)

.get("Chữ Hán   ", ""))
    pinyin = clean key_field(fields.get("Pinyin", ""))
    vi = clean_field(fields.get("Nghĩa tiếng Việt", ""))
    radical = clean_field(fields.get("Bộ thủ (tùy chọn)", ""))

    # Lấy 5 phần (có thể có emoji trong tên field)
    chiet_tu = get_field(fields, "💡 Chiết tự", "Chiết tự")
    am_thanh = get_field(fields, "📌 Âm thanh", "Âm thanh")
    cau_chuyen = get_field(fields, "🎬 Câu chuyện", "Câu chuyện")
    vi_du = get_field(fields, "📎 Ví dụ", "Ví dụ")
    lien_quan = get_field(fields, "🔗 Liên quan", "Liên quan")

    # Validation
    errors = []
    if not hsk:
        errors.append("Thiếu HSK")
    elif not re.match(
        r'^(HSK\s*[1-6]|HSK\s*7-9(\s*\(\s*[123]\s*\))?|HSK7-9)$',
        hsk,
        re.IGNORECASE
    ):
        errors.append(f"HSK không hợp lệ: {hsk}")
    if not stt:
        errors.append("Thiếu STT")
    if not zh:
        errors.append("Thiếu Chữ Hán")
    if not chiet_tu:
        errors.append("Thiếu phần Chiết tự")
    if not am_thanh:
        errors.append("Thiếu phần Âm thanh")
    if not cau_chuyen:
        errors.append("Thiếu phần Câu chuyện")
    if not vi_du:
        errors.append("Thiếu phần Ví dụ")
    if not lien_quan:
        errors.append("Thiếu phần Liên quan")

    if errors:
        set_output("status", "error")
        set_output("message", " | ".join(errors))
        print(f"❌ Validation errors: {errors}", file=sys.stderr)
        return 1

    # Ghép mẹo nhớ từ 5 phần
    mnemonic = build_mnemonic(chiet_tu, am_thanh, cau_chuyen, vi_du, lien_quan)

    if not mnemonic:
        set_output("status", "error")
        set_output("message", "Không ghép được mẹo nhớ")
        return 1

    # Tạo key có space
    key = normalize_key(hsk, stt, zh)
    print(f"🔑 Key (normalized): {key}", file=sys.stderr)
    print(f"📝 Mnemonic preview:", file=sys.stderr)
    print(mnemonic[:300] + "...", file=sys.stderr)

    mnemonics = load_mnemonics()
    old_count = len(mnemonics)

    # Xóa key SAI format
    key_wrong = f"{hsk}|{stt}|{zh}"
    if key_wrong in mnemonics and key_wrong != key:
        del mnemonics[key_wrong]
        print(f"🗑️ Đã xóa key sai: {key_wrong}", file=_lower = f"{hsk.lower()}|{stt}|{zh}"
    if key_lower in mnemonics and key_lower != key:
        del mnemonics[key_lower]
        print(f"🗑️ Đã xóa key lowercase: {key_lower}", file=sys.stderr)

    is_update = key in mnemonics
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
