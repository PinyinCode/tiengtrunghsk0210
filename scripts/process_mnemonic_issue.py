# -*- coding: utf-8 -*-
r"""
process_mnemonic_issue.py
Xu ly mnemonic tu GitHub Issue Form (5 phan) -> update data/ai_mnemonics.json
"""

import os
import re
import json
import sys


MNEMONIC_FILE = "data/ai_mnemonics.json"


# ⭐ EMOJI CHO TỪNG PHẦN
EMOJI_CHIET_TU = "\U0001F4A1"      # 💡
EMOJI_AM_THANH = "\U0001F4CC"      # 📌
EMOJI_CAU_CHUYEN # = "\U0001F3 🎬AC"   
EMOJI_VI_DU = "\U0001F4CE"         # 📎
EMOJI_LIEN_QUAN = "\U0001F517"     # 🔗


def parse_issue_body(body):
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
    if not value:
        return ""
    value = re.sub(r'^```\w*\n?', '', value)
    value = re.sub(r'\n?```$', '', value)
    return value.strip()


def get_field(fields, *keys):
    for key in keys:
        if key in fields:
            return clean_field(fields[key])
        for fk in fields.keys():
            if key.lower() in fk.lower():
                return clean_field(fields[fk])
    return ""


def normalize_key(hsk, stt, zh):
    hsk_str = str(hsk or "").strip().upper()
    stt_str = str(stt or "").strip()
    zh_str = str(zh or "").strip()

    m79 = re.match(r'^HSK\s*7-9\s*\(\s*([123])\s*\)$', hsk_str, re.IGNORECASE)
    if m79:
        sheet_num = m79.group(1)
        if re.search(r'\(\s+2\s*\)', hsk_str):
            hsk_norm = "HSK 7-9 ( 2)"
        else:
            hsk_norm = "HSK 7-9 (" + sheet_num + ")"
        return hsk_norm + "|" + stt_str + "|" + zh_str

    if re.match(r'^HSK\s*7-9$', hsk_str, re.IGNORECASE):
        return "HSK 7-9|" + stt_str + "|" + zh_str

    m = re.match(r'^(HSK)\s*(\d+)$', hsk_str, re.IGNORECASE)
    if m:
        hsk_norm = m.group(1).upper() + " " + m.group(2)
        return hsk_norm + "|" + stt_str + "|" + zh_str

    return hsk_str + "|" + stt_str + "|" + zh_str


# ═══════════════════════════════════════════════════════════════
#  GHÉP MẸO NHỚ VỚI EMOJI + DẤU
# ═══════════════════════════════════════════════════════════════
def strip_leading_label(text, labels):
    """
    Bỏ label nếu user đã gõ ở đầu (VD: "Chiết tự:", "Chiet tu:", "💡 Chiết tự:")
    """
    for label in labels:
        pattern = r'^\s*' + re.escape(label) + r'\s*:?\s*'
        new_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        if new_text != text:
            return new_text.strip()
    return text.strip()


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
        text = strip_leading_label(chiet_tu, [
            "💡 Chiết tự", "Chiết tự", "Chiet tu", "💡"
        ])
        parts.append(EMOJI_CHIET_TU + " Chiết tự: " + text)

    if am_thanh:
        text = strip_leading_label(am_thanh, [
            "📌 Âm thanh", "Âm thanh", "Am thanh", "📌"
        ])
        parts.append(EMOJI_AM_THANH + " Âm thanh: " + text)

    if cau_chuyen:
        text = strip_leading_label(cau_chuyen, [
            "🎬 Câu chuyện", "Câu chuyện", "Cau chuyen", "🎬"
        ])
        parts.append(EMOJI_CAU_CHUYEN + " Câu chuyện: " + text)

    if vi_du:
        text = strip_leading_label(vi_du, [
            "📎 Ví dụ", "Ví dụ", "Vi du", "📎"
        ])
        parts.append(EMOJI_VI_DU + " Ví dụ: " + text)

    if lien_quan:
        text = strip_leading_label(lien_quan, [
            "🔗 Liên quan", "Liên quan", "Lien quan", "🔗"
        ])
        parts.append(EMOJI_LIEN_QUAN + " Liên quan: " + text)

    return "\n".join(parts)


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
                f.write(key + "<<" + delimiter + "\n" + str(value) + "\n" + delimiter + "\n")
            else:
                f.write(key + "=" + str(value) + "\n")
    print("[OUTPUT] " + key + "=" + str(value), file=sys.stderr)


def main():
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")

    print("Xu ly issue #" + str(issue_number), file=sys.stderr)

    if not issue_body:
        set_output("status", "error")
        set_output("message", "Issue body rong")
        return 1

    fields = parse_issue_body(issue_body)

    print("=== FIELDS DETECTED ===", file=sys.stderr)
    for k in fields.keys():
        print("  [" + k + "]", file=sys.stderr)
    print("", file=sys.stderr)

    hsk = clean_field(fields.get("HSK", "")).upper()
    stt = clean_field(fields.get("STT", ""))
    zh = clean_field(fields.get("Chữ Hán", ""))
    pinyin = clean_field(fields.get("Pinyin", ""))
    vi = clean_field(fields.get("Nghĩa tiếng Việt", ""))
    radical = clean_field(fields.get("Bộ thủ (tùy chọn)", ""))

    chiet_tu = get_field(fields, "Chiết tự")
    am_thanh = get_field(fields, "Âm thanh")
    cau_chuyen = get_field(fields, "Câu chuyện")
    vi_du = get_field(fields, "Ví dụ")
    lien_quan = get_field(fields, "Liên quan")

    errors = []
    if not hsk:
        errors.append("Thieu HSK")
    elif not re.match(r'^(HSK\s*[1-6]|HSK\s*7-9(\s*\(\s*[123]\s*\))?|HSK7-9)$', hsk, re.IGNORECASE):
        errors.append("HSK khong hop le: " + hsk)
    if not stt:
        errors.append("Thieu STT")
    if not zh:
        errors.append("Thieu Chu Han")
    if not chiet_tu:
        errors.append("Thieu phan Chiet tu")
    if not am_thanh:
        errors.append("Thieu phan Am thanh")
    if not cau_chuyen:
        errors.append("Thieu phan Cau chuyen")
    if not vi_du:
        errors.append("Thieu phan Vi du")
    if not lien_quan:
        errors.append("Thieu phan Lien quan")

    if errors:
        set_output("status", "error")
        set_output("message", " | ".join(errors))
        print("Validation errors: " + str(errors), file=sys.stderr)
        return 1

    mnemonic = build_mnemonic(chiet_tu, am_thanh, cau_chuyen, vi_du, lien_quan)

    if not mnemonic:
        set_output("status", "error")
        set_output("message", "Khong ghep duoc meo nho")
        return 1

    key = normalize_key(hsk, stt, zh)
    print("Key (normalized): " + key, file=sys.stderr)
    print("Mnemonic preview:", file=sys.stderr)
    print(mnemonic[:400] + "...", file=sys.stderr)

    mnemonics = load_mnemonics()
    old_count = len(mnemonics)

    key_wrong = hsk + "|" + stt + "|" + zh
    if key_wrong in mnemonics and key_wrong != key:
        del mnemonics[key_wrong]
        print("Da xoa key sai: " + key_wrong, file=sys.stderr)

    key_lower = hsk.lower() + "|" + stt + "|" + zh
    if key_lower in mnemonics and key_lower != key:
        del mnemonics[key_lower]
        print("Da xoa key lowercase: " + key_lower, file=sys.stderr)

    is_update = key in mnemonics
    mnemonics[key] = mnemonic
    save_mnemonics(mnemonics)
    new_count = len(mnemonics)

    action = "cap nhat" if is_update else "them moi"
    set_output("status", "success")
    set_output("action", action)
    set_output("key", key)
    set_output("old_count", str(old_count))
    set_output("new_count", str(new_count))
    set_output("total", str(new_count))

    print("Da " + action + ": " + key, file=sys.stderr)
    print("Tong: " + str(old_count) + " -> " + str(new_count), file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
