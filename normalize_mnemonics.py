# -*- coding: utf-8 -*-
import os
import re
import json
import sys
import shutil
from datetime import datetime


RE_HANZI_CHARS = (
    r'\u4e00-\u9fff'
    r'\u3000-\u303f'
    r'\uff00-\uffef'
    '，。！？、；：""''（）《》「」'
)

PUNCT_CN = '，。！？、；：""''（）'

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

RE_INSIDE_SPLIT = re.compile(
    r'^(.+?)\s*[,' + PUNCT_CN + r'\-\—\–=:]\s*(.+)$',
    re.DOTALL
)

RE_PINYIN_PLAIN = re.compile(
    r'^([A-Za-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩị'
    r'òóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
    r'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊ'
    r'ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ'
    r'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü'
    r'\s.,;:\'\-]+?)\s*'
    r'(?=[\-\—\–,;:=]|[\u4e00-\u9fff]|$)'
)


def _clean_punct(s):
    if not s:
        return ""
    s = str(s).strip()
    s = re.sub(r'^[\s\-\u2014\u2013,;:=]+', '', s)
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


def _parse_one_example(part):
    part = part.strip()
    if not part:
        return None

    part = re.sub(
        r"^['\"\u2018\u2019\u201c\u201d]+|['\"\u2018\u2019\u201c\u201d]+$",
        '', part
    ).strip()

    m_zh = RE_ZH_START.match(part)
    if not m_zh:
        m_zh = RE_ZH_FALLBACK.match(part)
        if not m_zh:
            return None

    zh = m_zh.group(1).strip()

    zh = re.sub(
        r'\s*[-\u2014\u2013,;:!?.,]+\s*'
        r'([!?.,;:\uFF0C\u3002\uFF01\uFF1F\u3001\uFF1B\uFF1A'
        r'\u201c\u201d\u2018\u2019\uFF08\uFF09])',
        r'\1', zh
    )
    zh = re.sub(
        r'\s+([\uFF0C\u3002\uFF01\uFF1F\u3001\uFF1B\uFF1A'
        r'\u201c\u201d\u2018\u2019\uFF08\uFF09])',
        r'\1', zh
    )
    zh = re.sub(r'[\s\-\u2014\u2013,;:!?.,]+$', '', zh)

    rest = part[len(m_zh.group(1)):].strip()
    rest = re.sub(
        r"^['\"\u2018\u2019\u201c\u201d]+|['\"\u2018\u2019\u201c\u201d]+$",
        '', rest
    ).strip()

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
            after_clean = re.sub(
                r'^[\s\-\u2014\u2013,;:=!?]+', '', after_clean
            ).strip()
            if after_clean:
                first_line = after_clean.split('\n')[0].strip()
                if first_line:
                    vi = _clean_punct(first_line)
    else:
        m_py = RE_PINYIN_PLAIN.match(rest)
        if m_py:
            py = _clean_punct(m_py.group(1))
            rest2 = rest[len(m_py.group(1)):].strip()
            rest2 = re.sub(r'^[\s\-\u2014\u2013,;:=!?]+', '', rest2).strip()
            if rest2:
                vi = _clean_punct(rest2)
        else:
            rest_clean = re.sub(
                r'^[\s\-\u2014\u2013,;:=!?]+', '', rest
            ).strip()
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
        block_with_ws = m.group(2)
        block = block_with_ws.strip()

        if not block:
            return m.group(0)

        leading_ws = block_with_ws[:len(block_with_ws) - len(block_with_ws.lstrip())]
        trailing_ws = block_with_ws[len(block_with_ws.rstrip()):]

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
        return prefix + leading_ws + new_block + trailing_ws

    return RE_VI_DU_BLOCK.sub(_replace, mnemonic)


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
    path = find_file()
    if not path:
        print("Khong tim thay data/ai_mnemonics.json")
        sys.exit(1)

    print("=" * 60)
    print("Normalize: " + path)
    print("=" * 60)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Tong entries: " + str(len(data)))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path + ".bak_" + ts
    shutil.copy2(path, backup)
    print("Backup: " + backup)

    fixed = 0
    samples = []

    for key, value in data.items():
        try:
            new_value = normalize_mnemonic(value)
            if new_value != value:
                data[key] = new_value
                fixed += 1
                if len(samples) < 15:
                    samples.append((key, value, new_value))
        except Exception as e:
            print("ERR " + key + ": " + str(e))

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if samples:
        print("=" * 60)
        print("Mau thay doi:")
        print("=" * 60)

        for key, old, new in samples:
            old_line = ""
            for line in old.split("\n"):
                if "Ví dụ" in line:
                    old_line = line
                    break

            new_line = ""
            for line in new.split("\n"):
                if "Ví dụ" in line:
                    new_line = line
                    break

            print("")
            print("KEY: " + key)
            print("  OLD: " + old_line[:110])
            print("  NEW: " + new_line[:110])

    print("")
    print("=" * 60)
    print("Da sua: " + str(fixed) + " / " + str(len(data)) + " entries")
    print("File:   " + path)
    print("=" * 60)


if __name__ == "__main__":
    main()
