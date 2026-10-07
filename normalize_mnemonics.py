# -*- coding: utf-8 -*-
"""
Chuẩn hóa format câu ví dụ trong data/ai_mnemonics.json
Format đích: 📎 Ví dụ: <zh> (<py>) - <vi>
"""

import os
import re
import json
import sys
import shutil
from datetime import datetime


def _clean_punct(s):
    """Xóa dấu câu cuối + space thừa."""
    if not s:
        return ""
    s = str(s).strip()
    s = re.sub(r'[\s,;:.]+$', '', s)
    return s.strip()


def _parse_one_example(part):
    """Parse 1 câu ví dụ - đọc được mọi format."""
    part = part.strip()
    if not part:
        return None

    # Bỏ quote bao quanh
    part = re.sub(r"^['\"'\"'']+|['\"'\"'']+$", '', part).strip()

    # Bước 1: Lấy Hán tự đầu (kèm dấu câu Trung)
    m_zh = re.match(
        r'^([\u4e00-\u9fff，。！？、；：""''（）\u201c\u201d\u2018\u2019'
        r'\uff01\uff1f\uff1b\uff1a\uff08\uff09\s]+?)\s*'
        r'(?=[\(\（A-Za-z]|$)',
        part
    )
    if not m_zh:
        m_zh = re.match(r'^([\u4e00-\u9fff]+)', part)
        if not m_zh:
            return None

    zh = m_zh.group(1).strip()
    # Xóa space trước dấu câu Trung
    zh = re.sub(r'\s+([，。！？、；：""''（）\uff01\uff1f\uff1b\uff1a])', r'\1', zh)

    rest = part[len(m_zh.group(1)):].strip()
    rest = re.sub(r"^['\"'\"'']+|['\"'\"'']+$", '', rest).strip()

    py, vi = "", ""

    # Bước 2: Parse ngoặc ()
    m_paren = re.match(r'^[\(\（]([^\)\）]*)[\)\）]\s*(.*)$', rest, re.DOTALL)
    if m_paren:
        inside = m_paren.group(1).strip()
        after = m_paren.group(2).strip()

        # Trong ngoặc: pinyin + vi
        m_split = re.match(r'^(.+?)\s*[,，;；\-—–=:]\s*(.+)$', inside, re.DOTALL)
        if m_split:
            py = _clean_punct(m_split.group(1))
            vi = _clean_punct(m_split.group(2))
        else:
            py = _clean_punct(inside)

        # Sau ngoặc: vi
        if not vi and after:
            after_clean = after.strip()
            after_clean = re.sub(r'^[\s\-—–,;:=]+', '', after_clean).strip()
            if after_clean:
                first_line = after_clean.split('\n')[0].strip()
                if first_line:
                    vi = _clean_punct(first_line)
    else:
        # Không có ngoặc
        m_py = re.match(
            r'^([A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜÜü\s.,;:\'\-]+?)\s*'
            r'(?=[\-—–,;:=]|[\u4e00-\u9fff]|$)',
            rest
        )
        if m_py:
            py = _clean_punct(m_py.group(1))
            rest2 = rest[len(m_py.group(1)):].strip()
            rest2 = re.sub(r'^[-—–,;:=]\s*', '', rest2).strip()
            if rest2:
                vi = _clean_punct(rest2)
        else:
            rest = re.sub(r'^[-—–,;:=]\s*', '', rest).strip()
            if rest:
                vi = _clean_punct(rest)

    return {"zh": zh, "pinyin": py, "vi": vi}


def _split_outside_parens(text):
    """Tách text theo / hoặc ; ngoài ngoặc."""
    result = []
    depth = 0
    current = []
    for ch in text:
        if ch in '(（':
            depth += 1
            current.append(ch)
        elif ch in ')）':
            depth -= 1
            current.append(ch)
        elif ch in '/;；' and depth == 0:
            result.append(''.join(current))
            current = []
        else:
            current.append(ch)
    if current:
        result.append(''.join(current))
    return result


def normalize_mnemonic(mnemonic):
    """Chuẩn hóa block 📎 Ví dụ: trong mnemonic."""
    if not mnemonic or not isinstance(mnemonic, str):
        return mnemonic

    # Tìm block ví dụ
    m = re.search(
        r'(📎\s*Ví dụ:?\s*)(.*?)(?=\n\s*🔗|\n\s*💡|\n\s*📌|\n\s*🎬|\Z)',
        mnemonic,
        re.DOTALL
    )
    if not m:
        return mnemonic

    prefix = m.group(1)
    block = m.group(2).strip()
    if not block:
        return mnemonic

    # Tách nhiều câu
    parts = _split_outside_parens(block)

    result_items = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        parsed = _parse_one_example(part)
        if parsed and parsed.get("zh"):
            # Format chuẩn
            item = parsed["zh"]
            if parsed["pinyin"]:
                item += " (" + parsed["pinyin"] + ")"
            if parsed["vi"]:
                item += " - " + parsed["vi"]
            result_items.append(item)

    if not result_items:
        return mnemonic

    new_block = " / ".join(result_items)
    new_full = prefix + new_block + "\n"

    # Thay thế
    return mnemonic[:m.start()] + new_full + mnemonic[m.end():]


def main():
    # Tìm file
    candidates = [
        "data/ai_mnemonics.json",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ai_mnemonics.json"),
    ]
    path = None
    for p in candidates:
        if os.path.exists(p):
            path = p
            break

    if not path:
        print("[X] Không tìm thấy data/ai_mnemonics.json")
        sys.exit(1)

    print("=" * 60)
    print("[FILE] " + path)
    print("=" * 60)

    # Đọc
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("[X] Lỗi đọc file: " + str(e))
        sys.exit(1)

    if not isinstance(data, dict):
        print("[X] File JSON phải là dict")
        sys.exit(1)

    print("[OK] Tổng entries: " + str(len(data)))

    # Backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path + ".bak_" + ts
    shutil.copy2(path, backup)
    print("[OK] Backup: " + backup)

    # Chuẩn hóa
    fixed = 0
    samples = []

    for key, value in data.items():
        try:
            new_value = normalize_mnemonic(value)
            if new_value != value:
                data[key] = new_value
                fixed += 1
                if len(samples) < 5:
                    samples.append((key, value, new_value))
        except Exception as e:
            print("[ERR] " + key + ": " + str(e))

    # In mẫu
    if samples:
        print("\n" + "=" * 60)
        print("MẪU THAY ĐỔI:")
        print("=" * 60)
        for key, old, new in samples:
            print("\n🔑 KEY: " + key)
            print("  BEFORE:")
            for line in old.split("\n"):
                if '📎' in line or 'Ví dụ' in line or (line.strip() and not line.strip().startswith(('💡', '🎬', '🔗', '📌'))):
                    print("    " + line[:100])
            print("  AFTER:")
            for line in new.split("\n"):
                if '📎' in line or 'Ví dụ' in line:
                    print("    " + line[:100])

    # Ghi
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("[OK] Đã chuẩn hóa: " + str(fixed) + "/" + str(len(data)) + " entries")
    print("[OK] File đã lưu: " + path)
    print("=" * 60)


if __name__ == "__main__":
    main()
