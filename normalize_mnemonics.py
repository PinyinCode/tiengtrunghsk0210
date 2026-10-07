# -*- coding: utf-8 -*-
r"""
Script chuẩn hóa format câu ví dụ trong data/ai_mnemonics.json

Format chuẩn đầu ra:
    📎 Ví dụ: <câu Hán> (<pinyin>) - <nghĩa Việt>

Xử lý được mọi format đầu vào:
    1. 我家在路口附近 (Wǒ jiā zài lùkǒu fùjìn) - Nhà tôi ở gần ngã tư
    2. 我在路上遇到了她。 (Wǒ zài lùshàng yùdào le ta., Tôi gặp cô ấy trên đường.
    3. 我们去公园吧！ (Wǒmen qù gōngyuán ba!) — Chúng ta đi công viên nhé!
    4. 我们去公园吧 - ! (Wǒmen qù gōngyuán ba!) — Chúng ta đi công viên nhé!
    5. 我的衬衫是白色的 (Wǒ de chènshān shì báisè de) - Áo sơ mi của tôi màu trắng
    6. 我们都喜欢喝茶 。 (Wǒmen dōu xǐhuān hē chá.)\nChúng tôi đều thích uống trà.
    7. 八点 (bā diǎn) - tám giờ
    ...

Cách dùng:
    python normalize_mnemonics.py                  # Chuẩn hóa + ghi file
    python normalize_mnemonics.py --dry-run        # Chỉ xem, không ghi
    python normalize_mnemonics.py --limit 20       # In 20 mẫu (mặc định 10)
"""

import os
import re
import json
import sys
import shutil
import argparse
from datetime import datetime


# =====================================================================
# PATTERNS
# =====================================================================

# Hán tự + dấu câu Trung
RE_HANZI_CHARS = (
    r'\u4e00-\u9fff'                    # Hán tự cơ bản
    r'\u3000-\u303f'                    # CJK punctuation
    r'\uff00-\uffef'                    # Fullwidth forms (！？，。 etc)
    r'，。！？、；：""''（）'           # Dấu câu Trung thông dụng
    r'\u201c\u201d\u2018\u2019'        # Smart quotes
    r'\u3002\uff01\uff1f\u3001\uff1b\uff1a\uff08\uff09'  # 。！？、；：（）
)

# Regex bắt Hán tự đầu câu (non-greedy, dừng trước ngoặc pinyin)
RE_ZH_START = re.compile(
    r'^([' + RE_HANZI_CHARS + r'\s]+?)\s*'
    r'(?=[\(\（A-Za-z]|$)'
)

# Fallback: chỉ Hán tự thuần
RE_ZH_FALLBACK = re.compile(r'^([\u4e00-\u9fff]+)')

# Regex parse ngoặc đơn
RE_PAREN = re.compile(
    r'^[\(\（]([^\)\）]*)[\)\）]\s*(.*)$',
    re.DOTALL
)

# Regex tách pinyin/vi trong ngoặc
RE_INSIDE_SPLIT = re.compile(r'^(.+?)\s*[,，;；\-—–=:]\s*(.+)$', re.DOTALL)

# Regex bắt pinyin trần đầu chuỗi
RE_PINYIN_PLAIN = re.compile(
    r'^([A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜÜüĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙǕǗǙǛ'
    r'\s.,;:\'\-]+?)\s*'
    r'(?=[\-—–,;:=]|[\u4e00-\u9fff]|$)'
)

# Regex tách vi sau dấu phân cách
RE_VI_OUTSIDE = re.compile(r'^[\s\-—–,;:=]+(.+)$', re.DOTALL)

# Regex tìm block ví dụ
RE_VI_DU_BLOCK = re.compile(
    r'(📎\s*Ví dụ:?\s*)(.*?)(?=\n\s*🔗|\n\s*💡|\n\s*📌|\n\s*🎬|\Z)',
    re.DOTALL
)

# Regex tách nhiều câu (dùng / hoặc ;)
RE_MULTI_EXAMPLE = re.compile(r'\s*[/;；]\s*')


# =====================================================================
# HELPERS
# =====================================================================

def _clean(s):
    """Chuẩn hóa whitespace."""
    if s is None:
        return ""
    return re.sub(r'\s+', ' ', str(s).strip())


def _clean_punct(s):
    """Xóa dấu câu cuối + space thừa."""
    if not s:
        return ""
    s = str(s).strip()
    s = re.sub(r'[\s,;:.]+$', '', s)
    return s.strip()


def _split_outside_parens(text):
    """Tách text theo / hoặc ; NHƯNG bỏ qua ký tự trong ngoặc ()."""
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
# CORE — PARSE 1 EXAMPLE
# =====================================================================

def _parse_one_example(part):
    """
    Parse 1 câu ví dụ → dict {zh, pinyin, vi}.
    Hỗ trợ mọi format.
    """
    part = part.strip()
    if not part:
        return None

    # Bước 1: Bỏ quote bao quanh
    part = re.sub(r"^['\"'\"'']+|['\"'\"'']+$", '', part).strip()

    # Bước 2: Lấy Hán tự đầu (kèm dấu câu Trung + space)
    m_zh = RE_ZH_START.match(part)
    if not m_zh:
        m_zh = RE_ZH_FALLBACK.match(part)
        if not m_zh:
            return None

    zh = m_zh.group(1).strip()

    # BƯỚC QUAN TRỌNG: Xóa space + dấu phân cách trước dấu câu Trung
    # Vd: "吧 - !" → "吧！"
    #      "吧—！" → "吧！"
    zh = re.sub(r'\s*[-—–,;:]\s*([，。！？、；：""''（）])', r'\1', zh)
    # Xóa space trước dấu câu Trung
    zh = re.sub(r'\s+([，。！？、；：""''（）])', r'\1', zh)
    # Bỏ dấu phân cách + space cuối
    zh = re.sub(r'[\s\-—–,;:]+$', '', zh)

    # Bước 3: Lấy rest = phần còn lại
    rest = part[len(m_zh.group(1)):].strip()
    rest = re.sub(r"^['\"'\"'']+|['\"'\"'']+$", '', rest).strip()

    py, vi = "", ""

    # Bước 4: Parse ngoặc ()
    m_paren = RE_PAREN.match(rest)
    if m_paren:
        inside = m_paren.group(1).strip()
        after = m_paren.group(2).strip()

        # Trong ngoặc: pinyin + vi (ngăn bằng , ; -)
        m_split = RE_INSIDE_SPLIT.match(inside)
        if m_split:
            py = _clean_punct(m_split.group(1))
            vi = _clean_punct(m_split.group(2))
        else:
            py = _clean_punct(inside)

        # Sau ngoặc: vi (có thể có dấu - hoặc xuống dòng)
        if not vi and after:
            after_clean = after.strip()
            # Bỏ dấu phân cách đầu
            after_clean = re.sub(r'^[\s\-—–,;:=]+', '', after_clean).strip()
            if after_clean:
                # Chỉ lấy dòng đầu tiên
                first_line = after_clean.split('\n')[0].strip()
                if first_line:
                    vi = _clean_punct(first_line)
    else:
        # Bước 5: Không có ngoặc → tách pinyin/vi thô
        m_py = RE_PINYIN_PLAIN.match(rest)
        if m_py:
            py = _clean_punct(m_py.group(1))
            rest2 = rest[len(m_py.group(1)):].strip()
            rest2 = re.sub(r'^[\s\-—–,;:=]+', '', rest2).strip()
            if rest2:
                vi = _clean_punct(rest2)
        else:
            rest_clean = re.sub(r'^[\s\-—–,;:=]+', '', rest).strip()
            if rest_clean:
                vi = _clean_punct(rest_clean)

    return {"zh": zh, "pinyin": py, "vi": vi}


def _format_example(ex):
    """Format dict → string chuẩn."""
    if not ex or not ex.get("zh"):
        return ""

    parts = [ex["zh"]]
    if ex.get("pinyin"):
        parts.append("(" + ex["pinyin"] + ")")
    if ex.get("vi"):
        parts.append("- " + ex["vi"])

    return " ".join(parts)


def normalize_mnemonic(mnemonic):
    """Chuẩn hóa block 📎 Ví dụ: trong mnemonic."""
    if not mnemonic or not isinstance(mnemonic, str):
        return mnemonic

    def _replace(m):
        prefix = m.group(1)
        block = m.group(2).strip()
        if not block:
            return m.group(0)

        # Tách nhiều câu
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
# MAIN
# =====================================================================

def find_file():
    """Tìm file ai_mnemonics.json."""
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
        description="Chuẩn hóa câu ví dụ trong ai_mnemonics.json"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Chỉ xem, không ghi file")
    parser.add_argument("--no-backup", action="store_true",
                        help="Không tạo backup")
    parser.add_argument("--limit", type=int, default=10,
                        help="Số mẫu hiển thị (mặc định 10)")
    args = parser.parse_args()

    path = find_file()
    if not path:
        print("[X] Không tìm thấy data/ai_mnemonics.json")
        sys.exit(1)

    print("=" * 70)
    print("[FILE] " + path)
    print("=" * 70)

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
    if not args.dry_run and not args.no_backup:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = path + ".bak_" + ts
        try:
            shutil.copy2(path, backup)
            print("[OK] Backup: " + backup)
        except Exception as e:
            print("[WARN] Không backup được: " + str(e))

    # Chuẩn hóa
    fixed = 0
    unchanged = 0
    errors = 0
    samples = []

    for key, value in data.items():
        try:
            new_value = normalize_mnemonic(value)
            if new_value != value:
                data[key] = new_value
                fixed += 1
                if len(samples) < args.limit:
                    samples.append((key, value, new_value))
            else:
                unchanged += 1
        except Exception as e:
            errors += 1
            print("[ERR] " + key + ": " + str(e))

    # In mẫu
    if samples:
        print("\n" + "=" * 70)
        print("MẪU THAY ĐỔI (tối đa " + str(args.limit) + "):")
        print("=" * 70)
        for key, old, new in samples:
            print("\n🔑 KEY: " + key)

            old_vidu = ""
            for line in old.split("\n"):
                if '📎' in line or 'Ví dụ' in line:
                    old_vidu = line
                    break
            print("  BEFORE: " + old_vidu[:120])

            new_vidu = ""
            for line in new.split("\n"):
                if '📎' in line or 'Ví dụ' in line:
                    new_vidu = line
                    break
            print("  AFTER:  " + new_vidu[:120])

    # Thống kê
    print("\n" + "=" * 70)
    print("KẾT QUẢ:")
    print("  Đã sửa:    " + str(fixed))
    print("  Không đổi: " + str(unchanged))
    print("  Lỗi:       " + str(errors))
    print("=" * 70)

    # Ghi
    if args.dry_run:
        print("[DRY-RUN] Không ghi file.")
        return

    if fixed == 0:
        print("[INFO] Không có gì để ghi.")
        return

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[OK] Đã ghi: " + path)
    except Exception as e:
        print("[X] Lỗi ghi file: " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
