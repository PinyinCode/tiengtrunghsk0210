# -*- coding: utf-8 -*-
r"""
SCANNER TOÀN BỘ ai_mnemonics.json

Chức năng:
  1. Quét tất cả entries
  2. Detect lỗi format câu ví dụ
  3. Chuẩn hóa về format: 📎 Ví dụ: <zh> (<py>) - <vi>
  4. Report chi tiết từng entry bị lỗi
  5. Backup + ghi file

Cách dùng:
    python normalize_mnemonics.py --scan          # Chỉ quét, không sửa
    python normalize_mnemonics.py --dry-run       # Xem trước
    python normalize_mnemonics.py --fix           # Sửa + ghi file
"""

import os
import re
import json
import sys
import shutil
import argparse
from datetime import datetime
from collections import Counter, defaultdict


# =====================================================================
# REGEX PATTERNS
# =====================================================================

RE_HANZI_CHARS = (
    r'\u4e00-\u9fff'
    r'\u3000-\u303f'
    r'\uff00-\uffef'
    r'，。！？、；：""''（）'
    r'\u201c\u201d\u2018\u2019'
)

RE_VI_DU_BLOCK = re.compile(
    r'(📎\s*Ví dụ:?\s*)(.*?)(?=\n\s*🔗|\n\s*💡|\n\s*📌|\n\s*🎬|\Z)',
    re.DOTALL
)

RE_ZH_START = re.compile(
    r'^([' + RE_HANZI_CHARS + r'\s]+?)\s*'
    r'(?=[\(\（A-Za-z]|$)'
)

RE_ZH_FALLBACK = re.compile(r'^([\u4e00-\u9fff]+)')

RE_PAREN = re.compile(r'^[\(\（]([^\)\）]*)[\)\）]\s*(.*)$', re.DOTALL)

RE_INSIDE_SPLIT = re.compile(r'^(.+?)\s*[,，;；\-—–=:]\s*(.+)$', re.DOTALL)

RE_PINYIN_PLAIN = re.compile(
    r'^([A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜÜ\-üĀÁǍÀĒÉĚÈ—ĪÍǏÌŌÓǑÒŪÚ–ǓÙǕǗǙǛ'
,    r'\s.,;:\'\-;]+?)\s*'
    r'(?=[\-—–,;:=]|[\u4e00-\u9fff]|$)'
)

RE_MULTI_EXAMPLE = re.compile(r'\s*[/;；]\s*')


# =====================================================================
# HELPERS
# =====================================================================

def _clean_punct(s):
    if not s:
        return ""
    s = str(s).strip()
    s = re.sub(r'[\s,;:.]+$', '', s)
    return s.strip()


def _split_outside_parens(text):
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


# =====================================================================
# PARSE
# =====================================================================

def _parse_one_example(part):
    part = part.strip()
    if not part:
        return None

    part = re.sub(r"^['\"'\"'']+|['\"'\"'']+$", '', part).strip()

    m_zh = RE_ZH_START.match(part)
    if not m_zh:
        m_zh = RE_ZH_FALLBACK.match(part)
        if not m_zh:
            return None

    zh = m_zh.group(1).strip()

    # Fix dấu câu bị tách
    zh = re.sub(r'\s*[-—–,;:]\s*([，。！？、；：""''（）])', r'\1', zh)
    zh = re.sub(r'\s+([，。！？、；：""''（）])', r'\1', zh)
    zh = re.sub(r'[\s\-—–,;:]+$', '', zh)

    rest = part[len(m_zh.group(1)):].strip()
    rest = re.sub(r"^['\"'\"'']+|['\"'\"'']+$", '', rest).strip()

    py, vi = "", ""

    m_paren = RE_PAREN.match(rest)
    if m_paren:
        inside = m_paren.group(1).strip()
        after = m_paren.group(2).strip()

        m_split = RE_INSIDE_SPLIT.match(inside)
        if m_split:
            py = _clean_punct(m_split.group(1))
            vi = _clean_punct(m_split.group(2))
        else:
            py = _clean_punct(inside)

        if not vi and after:
            after_clean = after.strip()
            after_clean = re.sub(r'^[\s\-—–,;:=]+', '', after_clean).strip()
            if after_clean:
                first_line = after_clean.split('\n')[0].strip()
                if first_line:
                    vi = _clean_punct(first_line)
    else:
        m_py = RE_PINYIN_PLAIN.match(rest)
        if m_py:
            py = _clean_punct(m_py.group(1))
            rest2 = rest[len(m_py.group(1)):].strip()
            rest2 = re.sub(r'^[\s:=]+', '', rest2).strip()
            if rest2:
                vi = _clean_punct(rest2)
        else:
            rest_clean = re.sub(r'^[\s\-—–,;:=]+', '', rest).strip()
            if rest_clean:
                vi = _clean_punct(rest_clean)

    return {"zh": zh, "pinyin": py, "vi": vi}


def _format_example(ex):
    if not ex or not ex.get("zh"):
        return ""
    parts = [ex["zh"]]
    if ex.get("pinyin"):
        parts.append("(" + ex["pinyin"] + ")")
    if ex.get("vi"):
        parts.append("- " + ex["vi"])
    return " ".join(parts)


def normalize_mnemonic(mnemonic):
    if not mnemonic or not isinstance(mnemonic, str):
        return mnemonic

    def _replace(m):
        prefix = m.group(1)
        block = m.group(2).strip()
        if not block:
            return m.group(0)

        parts = _split_outside_parens(block)
        result_items = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            parsed = _parse_one_example(part)
            if parsed and parsed.get("zh"):
                formatted = _format_example(parsed)
                if formatted:
                    result_items.append(formatted)

        if not result_items:
            return m.group(0)

        new_block = " / ".join(result_items)
        return prefix + new_block + "\n"

    return RE_VI_DU_BLOCK.sub(_replace, mnemonic)


# =====================================================================
# SCANNER — Detect lỗi
# =====================================================================

def _analyze_entry(key, value):
    """
    Phân tích 1 entry, trả về dict lỗi (nếu có).
    """
    issues = []
    info = {
        "key": key,
        "has_vi_du": False,
        "format": "unknown",
        "issues": [],
        "old_vidu": "",
        "new_vidu": "",
    }

    if not isinstance(value, str):
        issues.append("value_not_string")
        info["issues"] = issues
        return info

    # Check có 📎 Ví dụ: không
    if "📎" not in value and "Ví dụ" not in value:
        info["format"] = "no_example"
        info["issues"] = issues
        return info

    info["has_vi_du"] = True

    # Lấy block ví dụ hiện tại
    m = RE_VI_DU_BLOCK.search(value)
    if not m:
        issues.append("cant_extract_block")
        info["format"] = "cant_extract"
        info["issues"] = issues
        return info

    block = m.group(2).strip()
    info["old_vidu"] = "📎 Ví dụ: " + block[:120]

    # Check có dấu em dash không
    if '—' in block or '–' in block:
        issues.append("has_em_dash")

    # Check có dấu câu tách biệt không (吧 - ! hoặc 吧—！)
    if re.search(r'[\s\-—–]+\s*[！？，。、；：""''（）]', block):
        issues.append("punct_separated")

    # Check có space trước dấu câu Trung
    if re.search(r'\s+[，。！？、；：""''（）]', block):
        issues.append("space_before_punct")

    # Check ngoặc trước câu Hán
    if re.match(r'^[\s]*[\(\（]', block):
        issues.append("paren_before_zh")

    # Thử normalize
    new_value = normalize_mnemonic(value)
    new_m = RE_VI_DU_BLOCK.search(new_value)
    if new_m:
        new_block = new_m.group(2).strip()
        info["new_vidu"] = "📎 Ví dụ: " + new_block[:120]

    if new_value != value:
        issues.append("format_changed")

    # Đánh giá format
    if "has_em_dash" in issues:
        info["format"] = "em_dash"
    elif "punct_separated" in issues:
        info["format"] = "punct_separated"
    elif "space_before_punct" in issues:
        info["format"] = "space_before_punct"
    elif "format_changed" in issues:
        info["format"] = "changed_by_normalize"
    else:
        info["format"] = "ok"

    info["issues"] = issues
    return info


# =====================================================================
# MAIN
# =====================================================================

def find_file():
    candidates = [
        "data/ai_mnemonics.json",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "data", "ai_mnemonics.json"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Scan và chuẩn hóa ai_mnemonics.json"
    )
    parser.add_argument("--scan", action="store_true",
                        help="Chỉ quét, không sửa")
    parser.add_argument("--dry-run", action="store_true",
                        help="Xem trước thay đổi")
    parser.add_argument("--fix", action="store_true",
                        help="Sửa + ghi file")
    parser.add_argument("--show-ok", action="store_true",
                        help="Hiển thị cả entries OK")
    parser.add_argument("--limit", type=int, default=30,
                        help="Số mẫu hiển thị (mặc định 30)")
    args = parser.parse_args()

    if not (args.scan or args.dry_run or args.fix):
        parser.print_help()
        print("\n[!] Cần chọn --scan, --dry-run, hoặc --fix")
        sys.exit(1)

    path = find_file()
    if not path:
        print("[X] Không tìm thấy data/ai_mnemonics.json")
        sys.exit(1)

    print("=" * 70)
    print("SCANNER: " + path)
    print("=" * 70)

    # Đọc
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("[OK] Tổng entries: " + str(len(data)))

    # Quét
    print("\n[SCAN] Đang quét toàn bộ...")
    results = []
    format_counter = Counter()
    issue_counter = Counter()

    for key, value in data.items():
        info = _analyze_entry(key, value)
        results.append(info)
        format_counter[info["format"]] += 1
        for iss in info["issues"]:
            issue_counter[iss] += 1

    # Báo cáo format
    print("\n" + "=" * 70)
    print("PHÂN LOẠI FORMAT:")
    print("=" * 70)
    for fmt, count in format_counter.most_common():
        pct = count * 100.0 / len(data)
        print("  {:<25} {:>6} ({:.1f}%)".format(fmt, count, pct))

    print("\n" + "=" * 70)
    print("LỖI PHÁT HIỆN:")
    print("=" * 70)
    for iss, count in issue_counter.most_common():
        pct = count * 100.0 / len(data)
        print("  {:<25} {:>6} ({:.1f}%)".format(iss, count, pct))

    # Đếm entries cần sửa
    need_fix = [r for r in results if r["format"] != "ok" and r["format"] != "no_example"]
    ok_count = format_counter.get("ok", 0)
    no_example = format_counter.get("no_example", 0)

    print("\n" + "=" * 70)
    print("TỔNG KẾT:")
    print("=" * 70)
    print("  OK (không cần sửa):    " + str(ok_count))
    print("  Không có ví dụ:        " + str(no_example))
    print("  Cần sửa:               " + str(len(need_fix)))
    print("=" * 70)

    # Hiển thị mẫu
    if args.show_ok:
        display = results
    else:
        display = need_fix

    if display:
        print("\n" + "=" * 70)
        print("MẪU CẦN SỬA (tối đa " + str(args.limit) + "):")
        print("=" * 70)

        for info in display[:args.limit]:
            if info["format"] == "ok" and not args.show_ok:
                continue
            print("\n🔑 " + info["key"])
            print("   Format: " + info["format"])
            print("   Issues: " + ", ".join(info["issues"]))
            if info["old_vidu"]:
                print("   OLD:    " + info["old_vidu"][:120])
            if info["new_vidu"]:
                print("   NEW:    " + info["new_vidu"][:120])

    # Dry-run hoặc Fix
    if args.scan:
        print("\n[SCAN ONLY] Không sửa gì.")
        return

    if not need_fix:
        print("\n[OK] Không có gì cần sửa!")
        return

    if args.dry_run:
        print("\n[DRY-RUN] Không ghi file. Chạy --fix để sửa thật.")
        return

    if args.fix:
        # Backup
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = path + ".bak_" + ts
        shutil.copy2(path, backup)
        print("\n[OK] Backup: " + backup)

        # Sửa
        fixed = 0
        for key, value in data.items():
            new_value = normalize_mnemonic(value)
            if new_value != value:
                data[key] = new_value
                fixed += 1

        # Ghi
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("[OK] Đã sửa: " + str(fixed) + " / " + str(len(data)) + " entries")
        print("[OK] Đã ghi: " + path)


if __name__ == "__main__":
    main()
