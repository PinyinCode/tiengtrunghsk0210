# -*- coding: utf-8 -*-
r"""
Script sinh mẹo nhớ bằng AI (Qwen-Plus-Character) - TÁCH RIÊNG khỏi thư viện tĩnh.

Cấu trúc repo:
  root/
  ├── data/
  │   ├── tu_vung_hsk.xlsx        ← File từ vựng (input)
  │   └── ai_mnemonics.json       ← File mẹo nhớ (output)
  └── vocab_data/
      └── ai_mnemonic_generator.py  ← File này

Chức năng:
  - Đọc từ vựng từ ../data/tu_vung_hsk.xlsx
  - Gọi API Qwen sinh mẹo nhớ (prompt V3)
  - Lưu vào ../data/ai_mnemonics.json (resume được)

Cách chạy (từ thư mục root):
  python vocab_data/ai_mnemonic_generator.py
"""
import os
import sys
import json
import time
from openai import OpenAI
import openpyxl


# ═══════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════
API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    "https://ws-8lcqaxwxdv0h9xzy.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
)
MODEL_ID = os.getenv("QWEN_MODEL", "qwen-plus-character")

# Đường dẫn: tính từ vị trí file này (vocab_data/), lùi 1 cấp về root, rồi vào data/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../vocab_data
ROOT_DIR = os.path.dirname(BASE_DIR)                            # .../ (root)
DATA_DIR = os.path.join(ROOT_DIR, "data")                       # .../data

EXCEL_FILE = os.path.join(DATA_DIR, "tu_vung_hsk.xlsx")
OUTPUT_FILE = os.path.join(DATA_DIR, "ai_mnemonics.json")

# Số từ xử lý (0 = không giới hạn)
DEMO_LIMIT = int(os.getenv("DEMO_LIMIT", "20"))
DELAY_BETWEEN = float(os.getenv("DELAY_BETWEEN", "2.0"))

# Resume: bỏ qua từ đã có trong output
RESUME = os.getenv("RESUME", "1") == "1"


# ═══════════════════════════════════════════════════════════════════
#  DANH SÁCH NHÂN VẬT ĐA DẠNG
# ═══════════════════════════════════════════════════════════════════
NHAN_VAT = [
    "bà Tư ở quê", "chú Bảy bán hủ tiếu", "cô giáo Hạnh", "em Tí hàng xóm",
    "ông Nội", "chị Mai bán hoa", "bác Sáu đưa đò", "bạn Lan cùng lớp",
    "chú Tư thợ mộc", "bà Cụ đầu ngõ", "anh Hùng bộ đội", "cô Út bán chè",
    "chị Thảo thợ may", "em Bo học sinh", "bác Ba nông dân", "bà Ngoại",
    "chú Nam lái xe", "cô Liên bán sách", "em Na học vẽ", "ông Tám đánh cá",
    "dì Hương bán bánh", "chú Hòa sửa xe", "cô Thắm dạy nhạc", "em Khoa lớp 1",
]


# ═══════════════════════════════════════════════════════════════════
#  PROMPT V3
# ═══════════════════════════════════════════════════════════════════
def build_prompt(zh, pinyin, vi, hsk, nhan_vat):
    return f"""Bạn là giáo viên tiếng Trung nổi tiếng, chuyên tạo mẹo nhớ khiến học trò Việt Nam "một lần nghe là nhớ mãi".

Từ cần nhớ: **{zh}** (pinyin: {pinyin}) - nghĩa: {vi} - HSK{hsk}

Nhân vật gợi ý cho câu chuyện: **{nhan_vat}**

Hãy viết mẹo nhớ theo ĐÚNG định dạng 5 dòng sau (mỗi dòng 1 emoji):

💡 Chiết tự: [Phân tích bộ thủ CHÍNH XÁC. Nếu không chắc chắn về một bộ thủ, hãy nói rõ "theo cách hiểu thông dụng" thay vì bịa. Nếu từ ghép, phân tích từng chữ]
📌 Âm thanh: [Tìm âm Hán-Việt, so sánh với từ tiếng Việt gần âm. Ưu tiên tìm 2-3 từ đồng âm/gần âm. Nếu không có, tạo câu vè]
🎬 Câu chuyện: [Câu chuyện 2-3 câu với nhân vật đã gợi ý, bối cảnh cụ thể, có cảm xúc. Phải liên kết với bộ thủ và nghĩa của từ]
📎 Ví dụ: [Câu tiếng Trung ngắn + pinyin + nghĩa Việt]
🔗 Liên quan: [3-5 từ cùng bộ thủ, cùng âm, hoặc cùng chủ đề, kèm nghĩa]

QUY TẮC BẮT BUỘC:
- Giữ ĐÚNG 5 dòng
- Chiết tự phải CHÍNH XÁC, không bịa. Nếu không chắc, ghi rõ "theo cách hiểu thông dụng"
- Nhân vật trong câu chuyện phải là: {nhan_vat}
- Câu chuyện phải có CẢM XÚC (vui, buồn, ngạc nhiên, xúc động)
- Âm thanh phải ưu tiên tìm 2-3 từ đồng âm tiếng Việt trước khi tạo câu vè

Ví dụ mẫu cho 菜 (cài - món ăn):
💡 Chiết tự: 艹 (bộ thảo - cỏ, rau) + 采 (bộ thủ - hái, ngắt) → Hái cỏ/rau về = MÓN ĂN (菜)
📌 Âm thanh: "cài" ≈ "cải" (rau cải), "cài" ≈ "cái" (cái bát). Câu vè: "Rau cải, rau cài, hái về nấu món ăn"
🎬 Câu chuyện: Bà Tư ở quê sáng sớm ra vườn, cúi xuống hái (采) những ngọn rau cỏ (艹) còn đọng sương. Bà mang về chế biến thành món ăn (菜) dâng lên bàn thờ tổ tiên ngày giỗ.
📎 Ví dụ: 这道菜很好吃 (Zhè dào cài hěn hǎo chī) - Món này rất ngon
🔗 Liên quan: 采 (cǎi - hái), 彩 (cǎi - màu sắc), 青菜 (qīngcài - rau xanh), 菜单 (càidān - thực đơn)

Bây giờ sinh mẹo cho: {zh}
Output (đúng 5 dòng):"""


# ═══════════════════════════════════════════════════════════════════
#  GỌI API
# ═══════════════════════════════════════════════════════════════════
def generate_one(zh, pinyin, vi, hsk, nhan_vat):
    if not API_KEY:
        return ""

    prompt = build_prompt(zh, pinyin, vi, hsk, nhan_vat)
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1000,
            )
            if not response or not response.choices:
                print(f"      ⚠️ Response rỗng (lần {attempt+1})")
                time.sleep(3)
                continue

            msg = response.choices[0].message
            content = msg.content if hasattr(msg, "content") else None
            if content and isinstance(content, str) and content.strip():
                return content.strip()

            print(f"      ⚠️ Content rỗng (lần {attempt+1})")
            time.sleep(3)

        except Exception as e:
            err = str(e)

            # ⭐ PHÁT HIỆN QUOTA EXHAUSTED → DỪNG HẲN
            if "quota" in err.lower() and ("exhaust" in err.lower() or "403" in err):
                print("\n" + "=" * 62)
                print("🛑 QUOTA ĐÃ HẾT — DỪNG SCRIPT")
                print(f"   Model: {MODEL_ID}")
                print(f"   Vào Model Studio để nạp thêm tiền hoặc đổi model.")
                print("=" * 62 + "\n")
                raise RuntimeError("QUOTA_EXHAUSTED")

            # ⭐ LỖI 401/403 KHÁC (API key sai) → DỪNG LUÔN
            if "401" in err or "invalid_api_key" in err.lower() or "unauthorized" in err.lower():
                print("\n" + "=" * 62)
                print("🛑 API KEY KHÔNG HỢP LỆ — DỪNG SCRIPT")
                print(f"   Kiểm tra secret DASHSCOPE_API_KEY trên GitHub.")
                print("=" * 62 + "\n")
                raise RuntimeError("INVALID_API_KEY")

            # ⭐ 429 rate limit → chờ rồi thử lại
            if "429" in err or "rate" in err.lower():
                wait = 15 * (attempt + 1)
                print(f"      ⏳ Rate limit, chờ {wait}s...")
                time.sleep(wait)
            else:
                print(f"      ⚠️ Lỗi API (lần {attempt+1}/3): {err[:200]}")
                time.sleep(3)

    return ""

# ═══════════════════════════════════════════════════════════════════
#  LOAD EXCEL
# ═══════════════════════════════════════════════════════════════════
def load_vocab(limit=0):
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Không có file Excel: {EXCEL_FILE}")
        return []

    print(f"📖 Đang đọc: {EXCEL_FILE}")
    wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True, read_only=True)
    samples = []

    for sheet_name in wb.sheetnames:
        if limit > 0 and len(samples) >= limit:
            break
        if not sheet_name.strip().upper().startswith("HSK"):
            continue

        ws = wb[sheet_name]
        is_hsk79 = "7-9" in sheet_name

        for row in ws.iter_rows(min_row=2, values_only=True):
            if limit > 0 and len(samples) >= limit:
                break
            if not row or len(row) < 3:
                continue

            stt = str(row[0] or "").strip()
            zh = str(row[1] or "").strip()
            pinyin = str(row[2] or "").strip()
            vi_idx = 4 if is_hsk79 else 5
            vi = str(row[vi_idx] or "").strip() if len(row) > vi_idx else ""

            if not zh or not vi or len(zh) > 3:
                continue

            samples.append({
                "stt": stt,
                "zh": zh,
                "pinyin": pinyin,
                "vi": vi,
                "hsk": sheet_name.strip(),
                "key": f"{sheet_name.strip()}|{stt}|{zh}",
            })

    wb.close()
    return samples if limit == 0 else samples[:limit]


# ═══════════════════════════════════════════════════════════════════
#  LOAD / SAVE OUTPUT
# ═══════════════════════════════════════════════════════════════════
def load_existing():
    if not RESUME or not os.path.exists(OUTPUT_FILE):
        return {}
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"📦 Đã load {len(data)} từ từ output cũ (resume mode)")
        return data
    except Exception as e:
        print(f"⚠️ Không load được output cũ: {e}")
        return {}


def save_output(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════
def main():
    print("=" * 62)
    print("🎬 AI MNEMONIC GENERATOR — QWEN (ALIBABA SINGAPORE)")
    print(f"   Model: {MODEL_ID}")
    print(f"   Root:  {ROOT_DIR}")
    print(f"   Input: {EXCEL_FILE}")
    print(f"   Output:{OUTPUT_FILE}")
    print(f"   Số từ: {'ALL' if DEMO_LIMIT == 0 else DEMO_LIMIT}")
    print(f"   Resume:{'ON' if RESUME else 'OFF'}")
    print("=" * 62)

    if not API_KEY:
        print("❌ Chưa set DASHSCOPE_API_KEY")
        sys.exit(1)

    samples = load_vocab(limit=DEMO_LIMIT)
    if not samples:
        print("❌ Không có từ nào để xử lý")
        sys.exit(1)

    print(f"\n📚 Đã load {len(samples)} từ từ Excel\n")

    results = load_existing()
    success = 0
    skipped = 0
    failed = 0

    try:
        for i, w in enumerate(samples, 1):
            key = w["key"]

            if RESUME and key in results and results[key]:
                skipped += 1
                print(f"[{i}/{len(samples)}] {w['zh']} ({w['pinyin']}) — ⏭️  SKIP")
                continue

            nhan_vat = NHAN_VAT[(i - 1) % len(NHAN_VAT)]
            preview = w["vi"][:40] + ("..." if len(w["vi"]) > 40 else "")
            print(f"[{i}/{len(samples)}] {w['zh']} ({w['pinyin']}) - {preview}")
            print(f"      👤 Nhân vật: {nhan_vat}")

            mnemonic = generate_one(w["zh"], w["pinyin"], w["vi"], w["hsk"], nhan_vat)

            if mnemonic:
                results[key] = mnemonic
                success += 1
                print(f"      ✅ OK")
            else:
                failed += 1
                print(f"      ❌ FAIL")

            save_output(results)
            time.sleep(DELAY_BETWEEN)

    except RuntimeError as e:
        print(f"\n⚠️ Dừng do: {e}")
        print(f"   Đã lưu {len(results)} từ vào output.")

    print("\n" + "=" * 62)
    print(f"✅ HOÀN TẤT")
    print(f"   Mới sinh:    {success} từ")
    print(f"   Bỏ qua:      {skipped} từ")
    print(f"   Thất bại:    {failed} từ")
    print(f"   Tổng output: {len(results)} từ")
    print(f"📁 File: {OUTPUT_FILE}")
    print("=" * 62)

if __name__ == "__main__":
    main()
