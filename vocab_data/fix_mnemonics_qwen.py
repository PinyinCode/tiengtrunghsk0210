# -*- coding: utf-8 -*-
r"""
fix_mnemonics_qwen.py
Doc ai_mnemonics.json -> tra bo thu dung -> goi Qwen sua -> verify -> luu.
"""

import os
import sys
import json
import time
import shutil
import unicodedata
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_SCRIPT_DIR)

for _p in [_ROOT_DIR, _SCRIPT_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from vocab_data.radical_analyzer import (
        get_radical_for_word,
        normalize_kangxi,
    )
    from vocab_data.radicals_db import get_radical_info
except ImportError:
    try:
        from radical_analyzer import (
            get_radical_for_word,
            normalize_kangxi,
        )
        from radicals_db import get_radical_info
    except ImportError as e:
        print(f"[FIX] Loi load radical: {e}")
        sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("[FIX] Chua cai openai. Chay: pip install openai")
    sys.exit(1)


API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
MODEL_ID = os.getenv("QWEN_MODEL", "qwen-flash")

DELAY = float(os.getenv("DELAY", "2.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
LOG_EVERY = int(os.getenv("LOG_EVERY", "10"))

ONLY_HSK = os.getenv("ONLY_HSK", "").strip()
only_hsk_list = [x.strip() for x in ONLY_HSK.split(",") if x.strip()]

LIMIT = int(os.getenv("LIMIT", "0"))


def find_input_file():
    candidates = [
        os.path.join(_ROOT_DIR, "data", "ai_mnemonics.json"),
        os.path.join(_ROOT_DIR, "vocab_data", "ai_mnemonics.json"),
        os.path.join(_SCRIPT_DIR, "data", "ai_mnemonics.json"),
        os.path.join(_SCRIPT_DIR, "ai_mnemonics.json"),
        "data/ai_mnemonics.json",
        "ai_mnemonics.json",
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


INPUT_FILE = find_input_file()
if not INPUT_FILE:
    print("[FIX] Khong tim thay ai_mnemonics.json")
    sys.exit(1)

DATA_DIR = os.path.dirname(INPUT_FILE)
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_FILE = os.path.join(DATA_DIR, f"ai_mnemonics.backup_{TS}.json")


def parse_key(key):
    parts = key.split("|")
    if len(parts) == 3:
        return {
            "hsk": parts[0].strip(),
            "stt": parts[1].strip(),
            "zh": parts[2].strip(),
        }
    return {"hsk": "?", "stt": "?", "zh": key.strip()}


def extract_vi(mnemonic):
    if not mnemonic:
        return ""

    for line in mnemonic.split("\n"):
        line = line.strip()
        if line.startswith("📎") or line.startswith("Ví dụ"):
            if " - " in line:
                parts = line.rsplit(" - ", 1)
                if len(parts) == 2:
                    vi = parts[1].strip()
                    if vi and not any(c in vi for c in ",.!?;:"):
                        return vi[:60]

    for line in mnemonic.split("\n"):
        line = line.strip()
        for prefix in ["Nghia:", "Nghĩa:", "→", "="]:
            if line.startswith(prefix):
                result = line[len(prefix):].strip()
                if result and 2 <= len(result) <= 60:
                    return result[:60]

    for line in mnemonic.split("\n"):
        line = line.strip()
        if " - " in line and any(c in line for c in "àáảãạăâđêôơư"):
            parts = line.rsplit(" - ", 1)
            if len(parts) == 2:
                vi = parts[1].strip()
                if vi and 2 <= len(vi) <= 60:
                    return vi

    return ""


def get_true_radical(zh):
    if not zh or len(zh) > 3:
        return None

    try:
        rad = get_radical_for_word(zh)
        if not rad or not rad.get("zh"):
            return None

        rad_zh = rad["zh"]
        info = get_radical_info(rad_zh)

        if info:
            return {
                "zh": info.get("zh", rad_zh),
                "base_zh": info.get("base_zh", rad.get("base_zh", "")),
                "pinyin": info.get("pinyin", rad.get("pinyin", "")),
                "meaning": info.get("meaning", rad.get("meaning", "")),
            }

        return {
            "zh": rad_zh,
            "base_zh": rad.get("base_zh", ""),
            "pinyin": rad.get("pinyin", ""),
            "meaning": rad.get("meaning", ""),
        }
    except Exception:
        return None


def mnemonic_has_radical(mnemonic, radical):
    if not mnemonic or not radical:
        return True

    mnemonic_norm = unicodedata.normalize("NFC", mnemonic)
    mnemonic_norm = normalize_kangxi(mnemonic_norm)

    for r in [radical.get("zh", ""), radical.get("base_zh", "")]:
        if not r:
            continue
        r_norm = normalize_kangxi(unicodedata.normalize("NFC", r))
        if r_norm and r_norm in mnemonic_norm:
            return True

    py = radical.get("pinyin", "").strip().lower()
    if len(py) >= 3 and py in mnemonic_norm.lower():
        return True

    meaning = radical.get("meaning", "").strip().lower()
    if meaning:
        meaning_clean = meaning.split("(")[0].strip()

        if len(meaning_clean) >= 3 and meaning_clean in mnemonic_norm.lower():
            return True

        for keyword in meaning_clean.split():
            if len(keyword) >= 3 and keyword in mnemonic_norm.lower():
                return True

    return False


def build_prompt_part1(zh, hsk, vi, radical):
    rad_zh = radical.get("zh", "")
    rad_mean = radical.get("meaning", "")

    return f"""Bạn là giáo viên tiếng Trung. Viết mẹo nhớ cho chữ {zh}.

CHỮ: {zh} ({hsk}) - nghĩa: {vi}
BỘ THỦ: {rad_zh} ({rad_mean})

Viết ĐÚNG 3 dòng, KHÔNG thêm dòng nào khác:

💡 Chiết tự: Liệt kê ĐẦY ĐỦ các thành phần của {zh}. Format: {zh} = [A] + [B] + ... → [nghĩa]
VD: 的 = 白 (bạch) + 勺 (chước) → "cái thìa trắng"

📌 Âm thanh: 2-3 từ gần âm tiếng Việt

🎬 Câu chuyện: 1 CÂU ngắn (tối đa 25 chữ). PHẢI kết bằng "... = {vi.upper()}"

Output (CHỈ 3 dòng, bắt đầu bằng 💡 📌 🎬):"""


def build_prompt_part2(zh, vi, radical):
    rad_zh = radical.get("zh", "")

    return f"""Cho chữ {zh} (nghĩa: {vi}), bộ thủ {rad_zh}.

Viết ĐÚNG 2 dòng, KHÔNG thêm dòng nào khác:

📎 Ví dụ: 1 câu tiếng Trung + pinyin + nghĩa Việt
VD: 这是我的书 (Zhè shì wǒ de shū) - Đây là sách của tôi

🔗 Liên quan: 3-5 từ CÓ CHỨA bộ {rad_zh} trong cấu tạo. Format: 字 (pinyin - nghĩa)
VD với bộ 白: 百 (bǎi - trăm), 拍 (pāi - vỗ), 泊 (bó - đỗ)

Output (CHỈ 2 dòng, bắt đầu bằng 📎 🔗):"""


def clean_mnemonic(mn):
    emojis = ['💡', '📌', '🎬', '📎', '🔗']
    lines = mn.split('\n')
    result = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        for emo in emojis:
            if line.startswith(emo) and emo not in result:
                result[emo] = line
                break

    output = []
    for emo in emojis:
        if emo in result:
            output.append(result[emo])

    return '\n'.join(output)


def has_all_5_lines(mn):
    emojis = ['💡', '📌', '🎬', '📎', '🔗']
    return all(e in mn for e in emojis)


def call_qwen(prompt):
    if not API_KEY:
        return ""

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=700,
            )

            if not resp or not resp.choices:
                time.sleep(2)
                continue

            msg = resp.choices[0].message
            content = msg.content if hasattr(msg, "content") else None

            if content and content.strip():
                return content.strip()

            time.sleep(2)

        except Exception as e:
            err = str(e)

            if "quota" in err.lower() and ("exhaust" in err.lower() or "403" in err):
                print("\nQUOTA HET - DUNG SCRIPT")
                raise RuntimeError("QUOTA")

            if "401" in err or "unauthorized" in err.lower():
                print("\nAPI KEY SAI")
                raise RuntimeError("AUTH")

            if "429" in err:
                wait = 15 * (attempt + 1)
                print(f"      Rate limit, cho {wait}s")
                time.sleep(wait)
            else:
                print(f"      Loi (lan {attempt+1}/3): {err[:200]}")
                time.sleep(3)

    return ""


def fix_one(zh, hsk, vi, radical, old_mnemonic):
    for retry in range(MAX_RETRIES + 1):
        p1 = build_prompt_part1(zh, hsk, vi, radical)
        r1 = call_qwen(p1)

        if not r1:
            time.sleep(2)
            continue

        p2 = build_prompt_part2(zh, vi, radical)
        r2 = call_qwen(p2)

        if not r2:
            time.sleep(2)
            continue

        new_mn = r1.strip() + "\n" + r2.strip()
        new_mn = clean_mnemonic(new_mn)

        if not has_all_5_lines(new_mn):
            missing = [e for e in ['💡', '📌', '🎬', '📎', '🔗'] if e not in new_mn]
            print(f"      Thieu dong (lan {retry+1}): {missing}")
            time.sleep(2)
            continue

        if mnemonic_has_radical(new_mn, radical):
            return new_mn, "ok"
        else:
            print(f"      Verify fail (lan {retry+1}): meo moi khong chua bo {radical['zh']}")
            time.sleep(2)

    return old_mnemonic, "verify_fail"


def main():
    print("=" * 62)
    print("FIX MNEMONICS - QWEN")
    print(f"   Model:     {MODEL_ID}")
    print(f"   Base URL:  {BASE_URL}")
    print(f"   Input:     {INPUT_FILE}")
    print(f"   Backup:    {BACKUP_FILE}")
    print(f"   LIMIT:     {LIMIT}")
    print(f"   ONLY_HSK:  {only_hsk_list or '(tat ca)'}")
    print(f"   DELAY:     {DELAY}s")
    print("=" * 62)

    if not API_KEY:
        print("Chua set DASHSCOPE_API_KEY")
        sys.exit(1)

    print(f"\nDang doc file...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    print(f"Tong: {total} entries")

    shutil.copy(INPUT_FILE, BACKUP_FILE)
    print(f"Backup: {BACKUP_FILE}")

    print(f"\nBuoc 1: Quet tim entries sai...")

    suspects = []
    skip_compound = 0
    skip_no_db = 0

    for idx, (key, mnemonic) in enumerate(data.items(), 1):
        if idx % 500 == 0:
            print(f"   ... {idx}/{total}")

        info = parse_key(key)

        if only_hsk_list and info["hsk"] not in only_hsk_list:
            continue

        zh = info["zh"]
        if len(zh) != 1:
            skip_compound += 1
            continue

        rad = get_true_radical(zh)
        if not rad:
            skip_no_db += 1
            continue

        if not mnemonic_has_radical(mnemonic, rad):
            suspects.append((key, info, rad, mnemonic))

    print(f"\nKet qua:")
    print(f"   Tim thay: {len(suspects)} entries sai")
    print(f"   Bo qua:   {skip_compound} (chu ghep)")
    print(f"   Bo qua:   {skip_no_db} (DB thieu)")

    if not suspects:
        print("\nKhong co entry nao sai")
        return

    if LIMIT > 0:
        suspects = suspects[:LIMIT]
        print(f"   LIMIT: chi fix {LIMIT} entries dau")

    print(f"\n10 entries dau:")
    for key, info, rad, _ in suspects[:10]:
        print(f"   {key} -> bo: {rad['zh']} ({rad.get('meaning', '')[:30]})")

    print(f"\nSe goi Qwen {len(suspects)} lan (~{len(suspects) * 400:,} tokens)")
    print(f"Thoi gian: ~{len(suspects) * (DELAY + 2) // 60} phut")

    if sys.stdin.isatty():
        confirm = input("\nTiep tuc? (y/n): ").strip().lower()
        if confirm != "y":
            print("Huy")
            return
    else:
        print("\n[CI] Tu dong tiep tuc (khong co stdin)")

    print(f"\nBuoc 2: Bat dau fix...")

    ok = 0
    fail_verify = 0
    fail_api = 0

    try:
        for i, (key, info, rad, old_mn) in enumerate(suspects, 1):
            zh = info["zh"]
            vi = extract_vi(old_mn) or "?"

            print(f"\n[{i}/{len(suspects)}] {key}")
            print(f"   Bo dung: {rad['zh']} ({rad.get('meaning', '')})")
            print(f"   Nghia: {vi}")

            try:
                new_mn, status = fix_one(zh, info["hsk"], vi, rad, old_mn)

                if status == "ok":
                    data[key] = new_mn
                    ok += 1
                    print(f"   OK")
                elif status == "verify_fail":
                    fail_verify += 1
                    print(f"   Verify fail -> giu meo cu")
                else:
                    fail_api += 1
                    print(f"   API fail")

            except RuntimeError:
                raise

            if i % LOG_EVERY == 0:
                with open(INPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
                print(f"   Luu tam ({i}/{len(suspects)})")

            time.sleep(DELAY)

    except RuntimeError as e:
        print(f"\nDung do: {e}")

    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print("\n" + "=" * 62)
    print(f"HOAN TAT")
    print(f"   Fix OK:      {ok}")
    print(f"   Verify fail: {fail_verify}")
    print(f"   API fail:    {fail_api}")
    print(f"   Backup:      {BACKUP_FILE}")
    print(f"   Output:      {INPUT_FILE}")
    print("=" * 62)


if __name__ == "__main__":
    main()
