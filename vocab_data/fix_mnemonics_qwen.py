# -*- coding: utf-8 -*-
"""
fix_mnemonics_qwen.py
Doc ai_mnemonics.json, tra bo thu, goi Qwen sua, verify, luu.
Uu tien lay nghia tu file Excel tu_vung_hsk.xlsx.
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
        print("[FIX] Loi load radical: " + str(e))
        sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("[FIX] Chua cai openai")
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
BACKUP_FILE = os.path.join(DATA_DIR, "ai_mnemonics.backup_" + TS + ".json")


def parse_key(key):
    parts = key.split("|")
    if len(parts) == 3:
        return {
            "hsk": parts[0].strip(),
            "stt": parts[1].strip(),
            "zh": parts[2].strip(),
        }
    return {"hsk": "?", "stt": "?", "zh": key.strip()}


def load_vietnamese_meaning_from_excel():
    """
    Doc nghia tieng Viet tu file Excel.
    Doc TAT CA sheets, chữ Han luon o cot 1 (B), 
    nghia o cot 5 (F) cho HSK 1-6, cot 4 (E) cho HSK 7-9.
    """
    try:
        import openpyxl
    except ImportError:
        print("[EXCEL] Chua cai openpyxl")
        return {}

    candidates = [
        os.path.join(_ROOT_DIR, "data", "tu_vung_hsk.xlsx"),
        os.path.join(_ROOT_DIR, "tu_vung_hsk.xlsx"),
        "data/tu_vung_hsk.xlsx",
        "tu_vung_hsk.xlsx",
    ]
    excel_path = None
    for p in candidates:
        if os.path.exists(p):
            excel_path = os.path.abspath(p)
            break

    if not excel_path:
        print("[EXCEL] Khong tim thay tu_vung_hsk.xlsx")
        return {}

    print("[EXCEL] Doc: " + excel_path)

    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True, read_only=True)
    except Exception as e:
        print("[EXCEL] Loi mo Excel: " + str(e))
        return {}

    result = {}
    COL_ZH = 1

    for sheet_name in wb.sheetnames:
        try:
            ws = wb[sheet_name]
        except Exception as e:
            print("[EXCEL] Loi sheet " + sheet_name + ": " + str(e))
            continue

        # Doc 5 dong dau de tim header
        first_rows = []
        try:
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                first_rows.append(row)
                if i >= 4:
                    break
        except Exception:
            pass

        # Tim dong header (dong co nhieu text nhat, chua "Nghia" hoac "意思")
        header_idx = 0
        col_vi = None
        for i, row in enumerate(first_rows):
            if not row:
                continue
            header_str = " ".join([str(c).lower() if c else "" for c in row])
            # HSK 1-6: header chua "nghia tieng viet"
            if "nghia" in header_str or "nghĩa" in header_str:
                header_idx = i
                # Tim cot "nghia tieng viet"
                for j, c in enumerate(row):
                    if c and ("nghia" in str(c).lower() or "nghĩa" in str(c).lower()):
                        col_vi = j
                        break
                break
            # HSK 7-9: header chua "意思"
            if "意思" in header_str:
                header_idx = i
                for j, c in enumerate(row):
                    if c and "意思" in str(c):
                        col_vi = j
                        break
                break

        # Fallback: neu khong tim thay header
        if col_vi is None:
            # Doan theo sheet
            if "7-9" in sheet_name:
                col_vi = 4  # cot E
            else:
                col_vi = 5  # cot F
            header_idx = 0

        # Data bat dau tu dong sau header + 1 (bo 1 dong trong)
        data_start = header_idx + 2

        sheet_count = 0
        sheet_skip = 0

        try:
            for row in ws.iter_rows(min_row=data_start, values_only=True):
                if not row:
                    sheet_skip += 1
                    continue

                if len(row) <= max(COL_ZH, col_vi):
                    sheet_skip += 1
                    continue

                zh = row[COL_ZH]
                vi = row[col_vi]

                if not zh or not vi:
                    sheet_skip += 1
                    continue

                zh_str = str(zh).strip()
                vi_str = str(vi).strip()

                if zh_str and vi_str:
                    result[zh_str] = vi_str
                    sheet_count += 1
                else:
                    sheet_skip += 1

        except Exception as e:
            print("[EXCEL] Loi doc sheet " + sheet_name + ": " + str(e))

        print("[EXCEL] Sheet " + sheet_name + ": nghia cot " + str(col_vi) + " -> " + str(sheet_count) + " entries (bo qua " + str(sheet_skip) + ")")

    try:
        wb.close()
    except Exception:
        pass

    print("[EXCEL] TONG: " + str(len(result)) + " entries")
    return result


def extract_vi(mnemonic):
    """Fallback: lay nghia tu mnemonic cu (chi lay dong Vi du)."""
    if not mnemonic:
        return ""

    for line in mnemonic.split("\n"):
        line = line.strip()
        if line.startswith("Vi du") or line.startswith("Ví dụ"):
            if " - " in line:
                parts = line.rsplit(" - ", 1)
                if len(parts) == 2:
                    vi = parts[1].strip()
                    while vi and vi[-1] in ".!?,;:":
                        vi = vi[:-1].strip()
                    bad = False
                    for c in ",;:()":
                        if c in vi:
                            bad = True
                            break
                    if vi and not bad and 2 <= len(vi) <= 60:
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

    e1 = "\U0001F4A1"  # 💡
    e2 = "\U0001F4CC"  # 📌
    e3 = "\U0001F3AC"  # 🎬

    lines = []
    lines.append("Ban la giao vien tieng Trung. Viet meo nho cho chu " + zh + ".")
    lines.append("")
    lines.append("CHU: " + zh + " (" + hsk + ") - nghia: " + vi)
    lines.append("BO THU: " + rad_zh + " (" + rad_mean + ")")
    lines.append("")
    lines.append("Viet DUNG 3 dong, BAT DAU bang emoji nhu sau:")
    lines.append("")
    lines.append(e1 + " Chiet tu: Liet ke DAY DU cac thanh phan cua " + zh + ". Format: " + zh + " = [A] + [B] + ... => [nghia]")
    lines.append(e2 + " Am thanh: 2-3 tu gan am tieng Viet")
    lines.append(e3 + " Cau chuyen: 1 CAU ngan (toi da 25 chu). PHAI ket bang: ... = " + vi.upper())
    lines.append("")
    lines.append("Output (CHI 3 dong, moi dong BAT DAU bang emoji " + e1 + " " + e2 + " " + e3 + "):")

    return "\n".join(lines)


def build_prompt_part2(zh, vi, radical):
    rad_zh = radical.get("zh", "")

    e4 = "\U0001F4CE"  # 📎
    e5 = "\U0001F517"  # 🔗

    lines = []
    lines.append("Cho chu " + zh + " (nghia: " + vi + "), bo thu " + rad_zh + ".")
    lines.append("")
    lines.append("Viet DUNG 2 dong, BAT DAU bang emoji nhu sau:")
    lines.append("")
    lines.append(e4 + " Vi du: 1 cau tieng Trung + pinyin + nghia Viet")
    lines.append(e5 + " Lien quan: 3-5 tu CO CHUA bo " + rad_zh + " trong cau tao. Format: chu (pinyin - nghia)")
    lines.append("")
    lines.append("Output (CHI 2 dong, moi dong BAT DAU bang emoji " + e4 + " " + e5 + "):")

    return "\n".join(lines)


def clean_mnemonic(mn):
    emojis = ["\U0001F4A1", "\U0001F4CC", "\U0001F3AC", "\U0001F4CE", "\U0001F517"]
    lines = mn.split("\n")
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

    return "\n".join(output)


def has_all_5_lines(mn):
    emojis = ["\U0001F4A1", "\U0001F4CC", "\U0001F3AC", "\U0001F4CE", "\U0001F517"]
    for e in emojis:
        if e not in mn:
            return False
    return True


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
            content = None
            if hasattr(msg, "content"):
                content = msg.content

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
                print("      Rate limit, cho " + str(wait) + "s")
                time.sleep(wait)
            else:
                print("      Loi (lan " + str(attempt + 1) + "/3): " + err[:200])
                time.sleep(3)

    return ""


def fix_one(zh, hsk, vi, radical, old_mnemonic):
    # Lam sach nghia: bo dau ; () ... de Qwen de hieu
    vi_clean = vi
    if vi_clean:
        vi_clean = vi_clean.split(";")[0].strip()
        vi_clean = vi_clean.split("(")[0].strip()
        vi_clean = vi_clean.split("（")[0].strip()
        if not vi_clean:
            vi_clean = vi

    for retry in range(MAX_RETRIES + 1):
        p1 = build_prompt_part1(zh, hsk, vi_clean, radical)
        r1 = call_qwen(p1)

        if not r1:
            time.sleep(2)
            continue

        p2 = build_prompt_part2(zh, vi_clean, radical)
        r2 = call_qwen(p2)

        if not r2:
            time.sleep(2)
            continue

        # DEBUG: in raw output
        print("      [DEBUG] r1: " + r1[:150].replace("\n", " | "))
        print("      [DEBUG] r2: " + r2[:150].replace("\n", " | "))

        new_mn = r1.strip() + "\n" + r2.strip()
        new_mn = clean_mnemonic(new_mn)

        # DEBUG: in sau clean
        print("      [DEBUG] cleaned: " + new_mn[:250].replace("\n", " | "))

        # Kiem tra 3 dong chinh (khong bat buoc 5 dong)
        emojis_main = ["\U0001F4A1", "\U0001F4CC", "\U0001F3AC"]  # 💡 📌 🎬
        missing_main = []
        for e in emojis_main:
            if e not in new_mn:
                missing_main.append(e)

        if missing_main:
            print("      Thieu 3 dong chinh (lan " + str(retry+1) + "): " + str(missing_main))
            time.sleep(2)
            continue

        if mnemonic_has_radical(new_mn, radical):
            return new_mn, "ok"
        else:
            print("      Verify fail (lan " + str(retry+1) + "): meo moi khong chua bo " + radical["zh"])
            time.sleep(2)

    return old_mnemonic, "verify_fail"

def main():
    print("=" * 62)
    print("FIX MNEMONICS - QWEN")
    print("   Model:     " + MODEL_ID)
    print("   Input:     " + INPUT_FILE)
    print("   Backup:    " + BACKUP_FILE)
    print("   LIMIT:     " + str(LIMIT))
    print("   DELAY:     " + str(DELAY) + "s")
    print("=" * 62)

    if not API_KEY:
        print("Chua set DASHSCOPE_API_KEY")
        sys.exit(1)

    print("\nDang doc file...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    print("Tong: " + str(total) + " entries")

    shutil.copy(INPUT_FILE, BACKUP_FILE)
    print("Backup: " + BACKUP_FILE)

    print("\nBuoc 0: Load nghia tieng Viet tu Excel...")
    vi_dict = load_vietnamese_meaning_from_excel()

    print("\nBuoc 1: Quet tim entries sai...")

    suspects = []
    skip_compound = 0
    skip_no_db = 0
    skip_no_vi = 0
    from_excel = 0
    from_mnemonic = 0

    for idx, (key, mnemonic) in enumerate(data.items(), 1):
        if idx % 500 == 0:
            print("   ... " + str(idx) + "/" + str(total))

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
            vi = vi_dict.get(zh, "")

            if vi:
                from_excel += 1
            else:
                vi = extract_vi(mnemonic)
                if vi:
                    from_mnemonic += 1

            if not vi:
                skip_no_vi += 1
                continue

            suspects.append((key, info, rad, mnemonic, vi))

    print("\nKet qua:")
    print("   Tim thay: " + str(len(suspects)) + " entries sai")
    print("   Bo qua:   " + str(skip_compound) + " (chu ghep)")
    print("   Bo qua:   " + str(skip_no_db) + " (DB thieu)")
    print("   Bo qua:   " + str(skip_no_vi) + " (khong co nghia)")
    print("   Nghia tu Excel:    " + str(from_excel))
    print("   Nghia tu mnemonic: " + str(from_mnemonic))

    if not suspects:
        print("\nKhong co entry nao fix duoc")
        return

    if LIMIT > 0:
        suspects = suspects[:LIMIT]
        print("   LIMIT: chi fix " + str(LIMIT) + " entries dau")

    print("\n10 entries dau:")
    for key, info, rad, _, vi in suspects[:10]:
        print("   " + key + " -> bo: " + rad["zh"] + " | nghia: " + vi[:30])

    print("\nSe goi Qwen " + str(len(suspects)) + " lan")

    if sys.stdin.isatty():
        confirm = input("\nTiep tuc? (y/n): ").strip().lower()
        if confirm != "y":
            print("Huy")
            return
    else:
        print("\n[CI] Tu dong tiep tuc")

    print("\nBuoc 2: Bat dau fix...")

    ok = 0
    fail_verify = 0
    fail_api = 0

    try:
        for i, (key, info, rad, old_mn, vi) in enumerate(suspects, 1):
            zh = info["zh"]

            print("\n[" + str(i) + "/" + str(len(suspects)) + "] " + key)
            print("   Bo dung: " + rad["zh"])
            print("   Nghia: " + vi)

            try:
                new_mn, status = fix_one(zh, info["hsk"], vi, rad, old_mn)

                if status == "ok":
                    data[key] = new_mn
                    ok += 1
                    print("   OK")
                elif status == "verify_fail":
                    fail_verify += 1
                    print("   Verify fail")
                else:
                    fail_api += 1
                    print("   API fail")

            except RuntimeError:
                raise

            if i % LOG_EVERY == 0:
                with open(INPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
                print("   Luu tam (" + str(i) + "/" + str(len(suspects)) + ")")

            time.sleep(DELAY)

    except RuntimeError as e:
        print("\nDung do: " + str(e))

    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print("\n" + "=" * 62)
    print("HOAN TAT")
    print("   Fix OK:      " + str(ok))
    print("   Verify fail: " + str(fail_verify))
    print("   API fail:    " + str(fail_api))
    print("   Backup:      " + BACKUP_FILE)
    print("   Output:      " + INPUT_FILE)
    print("=" * 62)


if __name__ == "__main__":
    main()
