# -*- coding: utf-8 -*-
r"""
SCANNER TOÀN BỘ ai_mnemonics.json
"""

import os
import re
import json
import sys
import shutil
import argparse
from datetime import datetime
from collections import Counter


# =====================================================================
# REGEX PATTERNS
# =====================================================================

# Hán tự + dấu câu Trung (dùng \uXXXX tường minh)
RE_HANZI_CHARS = (
    r'\u4e00-\u9fff'                    # Hán tự cơ bản
    r'\u3000-\u303f'                    # CJK punctuation
    r'\uff00-\uffef'                    # Fullwidth forms
    r'\u201c-\u201d'                    # " "
    r'\u2018-\u2019'                    # ' '
    r'\u3002\uff01\uff1f\u3001\uff1b\uff1a'  # 。！？、；：
    r'\uff08\uff09'                     # （）
    r'\u300a\u300b'                     # 《》
    r'\u300c\u300d'                     # 「」
)

RE_VI_DU_BLOCK = re.compile(
    r'(\U0001f4ce\s*Ví dụ:?\s*)(.*?)(?=\n\s*\U0001f517|\n\s*\U0001f4a1|\n\s*\U0001f4cc|\n\s*\U0001f3ac|\Z)',
    re.DOTALL
)

RE_ZH_START = re.compile(
    r'^([' + RE_HANZI_CHARS + r'\s]+?)\s*'
    r'(?=[\(\（A-Za-z]|$)'
)

RE_ZH_FALLBACK = re.compile(r'^([\u4e00-\u9fff]+)')

RE_PAREN = re.compile(r'^[\(\（]([^\)\）]*)[\)\）]\s*(.*)$', re.DOTALL)

RE_INSIDE_SPLIT = re.compile(r'^(.+?)\s*[,\uFF0C;\uFF1B\-\u2014\u2013=:]\s*(.+)$', re.DOTALL)

RE_PINYIN_PLAIN = re.compile(
    r'^([A-Za-z\u0101\u00e1\u01ce\u00e0\u0113\u00e9\u011b\u00e8'
    r'\u012b\u00ed\u01d0\u00ec\u014d\u00f3\u01d2\u00f2\u016b\u00fa\u01d4\u00f9'
    r'\u00fc\u01d6\u01d8\u01da\u01dc\u00dc\u00fc'
    r'\s.,;:\'\-]+?)\s*'
    r'(?=[\-\u2014\u2013,;:=]|[\u4e00-\u9fff]|$)'
)


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

    # Bỏ quote bao quanh
    part = re.sub(r"^['\"\u2018\u2019\u201c\u201d]+|['\"\u2018\u2019\u201c\u201d]+$", '', part).strip()

    m_zh = RE_ZH_START.match(part)
    if not m_zh:
        m_zh = RE_ZH_FALLBACK.match(part)
        if not m_zh:
            return None

    zh = m_zh.group(1).strip()

    # Fix dấu câu bị tách
    zh = re.sub(r'\s*[-\u2014\u2013,;:]\s*([\uFF0C\u3002\uFF01\uFF1F\u3001\uFF1B\uFF1A\u201c\u201d\u2018\u2019\uFF08\uFF09])', r'\1', zh)
    zh = re.sub(r'\s+([\uFF0C\u3002\uFF01\uFF1F\u3001\uFF1B\uFF1A\u201c\u201d\u2018\u2019\uFF08\uFF09])', r'\1', zh)
    zh = re =.sub(r'[\s\-\u2014\u2013,;:]+$', '', zh)

    rest = part[len(m_zh.group(1)):].strip()
    rest = re.sub(r"^['\"\u2018\u2019\u201c\u201d]+|['\"\u2018\u2019\u201c\u201d]+$", '', rest).strip()

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
            after_clean = re.sub(r'^[\s\-\u2014\u2013,;:=]+', '', after_clean).strip()
            if after_clean:
                first_line = after_clean.split('\n')[0].strip()
                if first_line:
                    vi = _clean_punct(first_line)
    else:
        m_py = RE_PINYIN_PLAIN.match(rest)
        if m_py:
            py = _clean_punct(m_py.group(1))
            rest2 = rest[len(m_py.group(1)):].strip()
            rest2 = re.sub(r'^[\s\-\u2014\u2013,;:=]+', '', rest2).strip()
            if rest2:
                vi = _clean_punct(rest2)
        else:
            rest_clean = re.sub(r'^[\s\-\u2014\u2013,;:=]+', '', rest).strip()
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
# SCANNER
# =====================================================================

def _analyze_entry(key, value):
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

    if "\U0001f4ce" not in value and "Ví dụ" not in value:
        info["format"] = "no_example"
        info["issues"] = issues
        return info

    info["has_vi_du"] True

    m = RE_VI_DU_BLOCK.search(value)
    if not m:
        issues.append("cant_extract_block")
        info["format"] = "cant_extract"
        info["issues"] = issues
        return info

    block = m.group(2).strip()
    info["old_vidu"] = "\U0001f4ce Ví dụ: " + block[:120]

    if '\u2014' in block or '\u2013' in block:
        issues.append("has_em_dash")

    if re.search(r'[\s\-\u2014\u2013]+\s*[\uFF01\uFF1F\uFF0C\u3002\u3001\uFF1B\uFF1A]', block):
        issues.append("punct_separated")

    if re.search(r'\s+[\uFF0C\u3002\uFF01\uFF1F\u3001\uFF1B\uFF1A\u201c\u201d\u2018\u2019\uFF08\uFF09]', block):
        issues.append("space_before_punct")

    if re.match(r'^[\s]*[\(\uFF08]', block):
        issues.append("paren_before_zh")

    new_value = normalize_mnemonic(value)
    new_m = RE_VI_DU_BLOCK.search(new_value)
    if new_m:
        new_block = new_m.group(2).strip()
        info["new_vidu"] = "\U0001f4ce Ví dụ: " + new_block[:120]

    if new_value != value:
        issues.append("format_changed")

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--show-ok", action="store_true")
    parser.add_argument("--limit", type=int, default=30)
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

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("[OK] Tổng entries: " + str(len(data)))

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

    need_fix = [r for r in results if r["format"] not in ("ok", "no_example")]
    ok_count = format_counter.get("ok", 0)
    no_example = format_counter.get("no_example", 0)

    print("\n" + "=" * 70)
    print("TỔNG KẾT:")
    print("=" * 70)
    print("  OK (không cần sửa):    " + str(ok_count))
    print("  Không có ví dụ:        " + str(no_example))
    print("  Cần sửa:               " + str(len(need_fix)))
    print("=" * 70)

    display = results if args.show_ok else need_fix

    if display:
        print("\n" + "=" * 70)
        print("MẪU (tối đa " + str(args.limit) + "):")
        print("=" * 70)

        for info in display[:args.limit]:
            if info["format"] == "ok" and not args.show_ok:
                continue
            print("\n\U0001f511 " + info["key"])
            print("   Format: " + info["format"])
            print("   Issues: " + ", ".join(info["issues"]))
            if info["old_vidu"]:
                print("   OLD:    " + info["old_vidu"][:120])
            if info["new_vidu"]:
                print("   NEW:    " + info["new_vidu"][:120])

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
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = path + ".bak_" + ts
        shutil.copy2(path, backup)
        print("\n[OK] Backup: " + backup)

        fixed = 0
        for key, value in data.items():
            new_value = normalize_mnemonic(value)
            if new_value != value:
                data[key] = new_value
                fixed += 1

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("[OK] Đã sửa: " + str(fixed) + " / " + str(len(data)) + " entries")
        print("[OK] Đã ghi: " + path)


if __name__ == "__main__":
    main()
