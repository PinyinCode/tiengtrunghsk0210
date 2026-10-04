# -*- coding: utf-8 -*-
"""
Chuyển file Excel → HTML tự chứa dữ liệu.
Ghép 6 template: ui + social + accounts (gộp renewal) + intro + favorites + data.

✅ HEADER: Subtitle "Văn phòng & Công xưởng" được thiết kế lại
   thành PILL nổi bật với icon ✦ lấp lánh — không còn mờ.

✅ ĐA DATASET: Tự động quét thư mục `data/`, mỗi file Excel
   → 1 mục "Chuyên ngành" trong dropdown. Thêm file mới = copy
   vào `data/` + chạy lại `python main.py`, không cần sửa code.

✅ ONBOARDING: Demo + Trial được hỏi chọn chủ đề quan tâm
   → tự động filter + chia đều theo HSK.

✅ INTRO: Banner giới thiệu + Modal 6 slide hướng dẫn.

✅ FAVORITES:
   - Tab Yêu thích — 3 tab cùng hàng trên PC (Tổng hợp + Chuyên ngành + Yêu thích)
   - Item Yêu thích trong dropdown bộ dữ liệu
   - Nút tim trên card (đổi màu theo trạng thái)
   - Nút tim FLOAT góc phải (Practice Full)
   - ★ Nút toggle "Chỉ câu yêu thích" góc trái (Practice Full)
     → Khi bật: dropdown "CÂU:" chỉ liệt kê câu yêu thích
   - Chỉ tier ACTIVE/ADMIN dùng được, tier khác hiển thị 🔒

✅ CHAT SUPPORT: Module độc lập (chat_support.py)
   - User ↔ Admin realtime qua Firestore
   - FAB + badge poll 60s
   - Admin panel có tab "Chat hỗ trợ"

✅ RTDB PRESENCE (2026-09):
   - User online tracking qua Firebase Realtime Database
   - KHÔNG tốn Firestore quota
   - onDisconnect tự động xóa khi user tắt tab
   - Admin xem được danh sách user online realtime

✅ FIX (2026-09):
   - Chèn QUOTA DASHBOARD vào Admin Panel (trước đây bị thiếu)
   - Chèn USER ONLINE section vào Admin Panel
   - Escape "</" cho TẤT CẢ JSON blobs

✅ FIX (2026-09-28): TELEGRAM NOTIFY
   - Thêm build_config_js() + build_telegram_notify_js() vào full_js
   - Gửi thông báo Telegram khi user nhắn tin
   - LOẠI BỎ thẻ <script> thừa trong full_js (build_config_js wrap trong
     <script>...</script> → khi nhúng vào HTML_SHELL bị LỒNG 2 thẻ → vỡ HTML).
"""
import json
import os
import sys
import glob
import re
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_loader import load_config, print_banner, CONFIG_FILE
from data_reader import read_excel
from ui_template import build_ui_css, build_ui_html, build_ui_js
from social_template import (
    build_social_css, build_social_html, build_social_js,
    build_tiktok_bar_html
)
from accounts_template import (
    build_accounts_css,
    build_accounts_html,
    build_accounts_js,
    build_all_auth,
)
from intro_template import (
    build_intro_css,
    build_intro_html,
    build_intro_js,
)

# ⬇️⬇️⬇️ Module Favorites
from favorites_module import (
    build_favorites_css,
    build_favorites_html,
    build_favorites_js,
)

# ⬇️⬇️⬇️ Module Chat Support (độc lập) + Quota + Online
from chat_support import (
    build_chat_css,
    build_chat_html,
    build_chat_js,
    build_quota_html,
    build_quota_js,
    build_quota_init_js,
    build_online_section_html,
    build_config_js,              # ⭐ THÊM
    build_telegram_notify_js,     # ⭐ THÊM
)

# ⬇️⬇️⬇️ Module Admin Chat Manager (trình quản lý chat riêng cho admin)
from admin_chat_manager import (
    build_admin_chat_css,
    build_admin_chat_html,
    build_admin_chat_js,
)
from draggable_fab import (
    build_draggable_fab_css,
    build_draggable_fab_js,
)
# ═══════════════════════════════════════════════════════════════════
#  HELPER: escape string an toàn khi nhúng vào JS
# ═══════════════════════════════════════════════════════════════════
def _js_str(s):
    """Escape string để nhúng an toàn vào JS (giữa 2 dấu \")."""
    if s is None:
        return ""
    return (str(s)
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace('\n', '\\n')
            .replace('\r', '\\r')
            .replace('</', '<\\/'))


def _json_blob(obj, compact=True):
    """
    Serialize object → JSON an toàn để nhúng vào <script>.
    Escape "</" → "<\\/" để tránh đóng </script> sớm.
    """
    if compact:
        s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    else:
        s = json.dumps(obj, ensure_ascii=False)
    return s.replace("</", "<\\/")


# ═══════════════════════════════════════════════════════════════════
#  LOAD CONFIG + DATA
# ═══════════════════════════════════════════════════════════════════
CONFIG = load_config()
print_banner(CONFIG)

EXCEL_FILE = CONFIG["excel_file"]
OUTPUT_HTML = CONFIG["output_html"]
SHEET_INDEX = CONFIG["sheet_index"]
DATA_DIR = CONFIG.get("data_dir", "data")

# ─── 1. Đọc dataset gốc ───
data_tonghop = read_excel(EXCEL_FILE, SHEET_INDEX)
print(f"📚 Tổng hợp: {len(data_tonghop)} câu")

# ─── 2. Map icon + màu cho các chuyên ngành phổ biến ───
ICON_MAP = {
    # ─── Nhân sự / Hành chính ───
    "nhân sự":              "fa-users",
    "hành chính":           "fa-briefcase",
    "hành chính - nhân sự": "fa-briefcase",
    "hành chính nhân sự":   "fa-briefcase",

    # ─── Mua bán / Kho vận ───
    "thu mua":              "fa-shopping-cart",
    "xuất nhập khẩu":       "fa-ship",
    "logistics":            "fa-truck",
    "vận tải":              "fa-truck",
    "kho":                  "fa-warehouse",
    "bán hàng":             "fa-store",
    "kinh doanh":           "fa-chart-line",
    "marketing":            "fa-bullhorn",
    "dịch vụ khách hàng":   "fa-headset",
    "chăm sóc khách hàng":  "fa-headset",

    # ─── Kế toán / Tài chính ───
    "kế toán":              "fa-calculator",
    "tài chính":            "fa-coins",
    "hành chính kế toán":   "fa-file-invoice-dollar",

    # ─── Sản xuất / Kỹ thuật ───
    "sản xuất":             "fa-industry",
    "kế hoạch sản xuất":    "fa-calendar-alt",
    "kỹ thuật":             "fa-tools",
    "bảo trì":              "fa-tools",
    "chất lượng":           "fa-award",
    "qa":                   "fa-award",
    "qc":                   "fa-award",
    "r&d":                  "fa-flask",
    "nghiên cứu":           "fa-flask",

    # ─── Ngành đặc thù ───
    "giày da":              "fa-shoe-prints",
    "may mặc":              "fa-tshirt",
    "dệt may":              "fa-tshirt",
    "thực phẩm":            "fa-utensils",
    "nông nghiệp":          "fa-seedling",

    # ─── IT / Công nghệ ───
    "máy tính & it":        "fa-laptop-code",
    "máy tính":             "fa-laptop-code",
    "công nghệ thông tin":  "fa-laptop-code",
    "it":                   "fa-laptop-code",
}

DEFAULT_ICON_NAME = "fa-folder"
UNIFIED_COLOR = "#7c3aed"


def auto_detect_icon_color(display_name):
    """
    Trả về tuple (icon, color).
    - Icon: RIÊNG cho từng ngành (match theo nhiều cấp)
    - Color: LUÔN = UNIFIED_COLOR → đồng bộ style
    """
    key = display_name.strip().lower()

    # ─── 1. Match CHÍNH XÁC tên ───
    if key in ICON_MAP:
        return (ICON_MAP[key], UNIFIED_COLOR)

    # ─── 2. Match theo TỪ riêng ───
    words = re.split(r'[\s&\-_/,\.]+', key)
    for k in sorted(ICON_MAP.keys(), key=len, reverse=True):
        if k in words:
            return (ICON_MAP[k], UNIFIED_COLOR)

    # ─── 3. Match substring (CHỈ key >= 3 ký tự) ───
    for k in sorted(ICON_MAP.keys(), key=len, reverse=True):
        if len(k) >= 3 and k in key:
            return (ICON_MAP[k], UNIFIED_COLOR)

    return (DEFAULT_ICON_NAME, UNIFIED_COLOR)


def slugify_dataset_id(filename):
    """Tạo id slug từ tên file: 'Nhân_sự.xlsx' → 'nhan-su'."""
    base = filename.rsplit(".", 1)[0]
    base = unicodedata.normalize("NFD", base)
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    base = base.replace("đ", "d").replace("Đ", "D")
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower()
    return base or "dataset"


# ─── 3. Khởi tạo DATASET_REGISTRY ───
DATASET_REGISTRY = {
    "tonghop": {
        "id": "tonghop",
        "name": f"{len(data_tonghop)} câu phản xạ tổng hợp VPCX",
        "icon": "fa-book-open",
        "color": "#4f46e5",
        "data": data_tonghop,
        "count": len(data_tonghop),
        "source": EXCEL_FILE,
    }
}

# ─── 4. Quét thư mục data/ ───
_tonghop_abs = os.path.abspath(EXCEL_FILE)
_chuyen_nganh_count = 0

if os.path.isdir(DATA_DIR):
    excel_files = []
    for ext in ("*.xlsx", "*.xls", "*.csv"):
        excel_files.extend(glob.glob(os.path.join(DATA_DIR, ext)))
    excel_files.sort()

    print(f"\n🔍 Quét thư mục '{DATA_DIR}/' — tìm thấy {len(excel_files)} file Excel")

    for filepath in excel_files:
        filename = os.path.basename(filepath)

        if filename.startswith("~$"):
            continue
        if os.path.abspath(filepath) == _tonghop_abs:
            print(f"⏭️  {filename} — bỏ qua (file tổng hợp)")
            continue

        try:
            sub_data = read_excel(filepath, 0)
            if not sub_data:
                print(f"⚠️  {filename}: file rỗng, bỏ qua")
                continue

            display_name = filename.rsplit(".", 1)[0].replace("_", " ").strip()
            # ⭐ FIX: Normalize NFC để match ICON_MAP (tránh bug NFD từ Linux/macOS)
            display_name = unicodedata.normalize("NFC", display_name)
            if display_name.islower() or display_name.isupper():
                display_name = display_name.title()

            dataset_id = slugify_dataset_id(filename)

            dataset_id = slugify_dataset_id(filename)
            base_id = dataset_id
            counter = 2
            while dataset_id in DATASET_REGISTRY:
                dataset_id = f"{base_id}-{counter}"
                counter += 1

            icon, color = auto_detect_icon_color(display_name)

            DATASET_REGISTRY[dataset_id] = {
                "id": dataset_id,
                "name": display_name,
                "icon": icon,
                "color": color,
                "data": sub_data,
                "count": len(sub_data),
                "source": filename,
            }
            _chuyen_nganh_count += 1
            print(f"🏭 {display_name:25s} ({filename}) — {len(sub_data)} câu")
        except Exception as e:
            print(f"❌ Lỗi đọc {filename}: {e}")
            continue

    if _chuyen_nganh_count == 0:
        print(f"ℹ️  Không có file chuyên ngành nào trong '{DATA_DIR}/'")
        print(f"   (chỉ dùng dataset tổng hợp).")
else:
    print(f"\nℹ️  Chưa có thư mục '{DATA_DIR}/' — chỉ dùng dataset tổng hợp.")
    print(f"   → Tạo thư mục '{DATA_DIR}/' và bỏ file Excel vào để thêm chuyên ngành.")

# ─── 5. Serialize (escape "</" cho TẤT CẢ) ───
dataset_registry_json = _json_blob(DATASET_REGISTRY)
json_data = _json_blob(data_tonghop)
firebase_config_json = _json_blob(CONFIG["firebase_config"])
synonyms_json = _json_blob(CONFIG["synonyms"])
fillers_json = _json_blob(CONFIG["filler_words"])
onboarding_config_json = _json_blob(CONFIG.get("onboarding", {}))

telegram_bot_token = CONFIG.get("telegram_bot_token", "")
telegram_chat_id = CONFIG.get("telegram_chat_id", "")


# ═══════════════════════════════════════════════════════════════════
#  BUILD AUTH + CHÈN QUOTA + ONLINE SECTIONS
# ═══════════════════════════════════════════════════════════════════
auth_css, auth_html, auth_js = build_all_auth(CONFIG)

# ⬇️⬇️⬇️ THÊM: Chèn User Online section (RTDB) vào Admin Panel
if '<!-- __ADMIN_ONLINE_SECTION__ -->' in auth_html:
    auth_html = auth_html.replace(
        '<!-- __ADMIN_ONLINE_SECTION__ -->',
        build_online_section_html()
    )
    print("✅ Đã chèn User Online section vào Admin Panel")
else:
    print("⚠️  Không tìm thấy placeholder <!-- __ADMIN_ONLINE_SECTION__ -->")
    print("   → Thêm vào accounts_template.py → build_accounts_html()")
    print("   → TRƯỚC dòng <!-- __ADMIN_QUOTA_SECTION__ -->")

# ⬇️⬇️⬇️ Chèn Quota Dashboard vào Admin Panel (như cũ)
if '<!-- __ADMIN_QUOTA_SECTION__ -->' in auth_html:
    auth_html = auth_html.replace(
        '<!-- __ADMIN_QUOTA_SECTION__ -->',
        build_quota_html()
    )
    print("✅ Đã chèn Quota Dashboard vào Admin Panel")
else:
    print("⚠️  Không tìm thấy placeholder <!-- __ADMIN_QUOTA_SECTION__ -->")
    print("   → Kiểm tra accounts_template.py → build_accounts_html()")


# ═══════════════════════════════════════════════════════════════════
#  ★ FULLWIDTH SCALE CSS + HEADER DESIGN ★
# ═══════════════════════════════════════════════════════════════════
FULLWIDTH_CSS = r"""

/* ═══════════════════════════════════════════════════════════════════
   ★ FULL-WIDTH SCALE ★
   ═══════════════════════════════════════════════════════════════════ */

.page-wrap {
    width: 100%;
    max-width: 100%;
    margin: 0 auto;
    overflow-x: hidden;
}

.container {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}

.sticky-top {
    position: relative !important;
    width: 100% !important;
    max-width: 100% !important;
}

.main,
#mainContent {
    width: 100% !important;
    max-width: 100% !important;
}

/* ═══ SEARCH + FILTER ═══ */
.search-bar { width: 100% !important; max-width: 100% !important; }
.search-bar input { width: 100% !important; max-width: 100% !important; }

.filters {
    display: grid !important;
    width: 100% !important;
    max-width: 100% !important;
    grid-template-columns: 1fr 1fr !important;
    gap: .75rem !important;
}
@media (min-width: 1000px) {
    .filters {
        grid-template-columns: 220px 260px !important;
        gap: 1rem !important;
    }
}

.result-count { margin-top: .5rem !important; }

/* ═══ GRID CARDS ═══ */
.mobile-view {
    display: grid !important;
    width: 100% !important;
    max-width: 100% !important;
    margin-left: auto !important;
    margin-right: auto !important;
    gap: 1rem !important;
    grid-template-columns: 1fr !important;
}

@media (min-width: 769px) {
    .mobile-view {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 1.1rem !important;
    }
}

@media (min-width: 1800px) {
    .mobile-view {
        grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
        gap: 1.2rem !important;
    }
}
@media (min-width: 2400px) {
    .mobile-view {
        grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
        gap: 1.3rem !important;
    }
}

/* ═══ Banner full width ═══ */
.demo-banner,
.expiry-banner {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: auto !important;
    margin-right: auto !important;
    margin-bottom: 1rem !important;
}

/* ═══ Container padding co giãn ═══ */
@media (min-width: 1000px) {
    .container { padding-left: 1.5rem !important; padding-right: 1.5rem !important; }
}
@media (min-width: 1400px) {
    .container { padding-left: 2rem !important; padding-right: 2rem !important; }
}
@media (min-width: 1900px) {
    .container { padding-left: 2.5rem !important; padding-right: 2.5rem !important; }
}

/* ═══ MOBILE: thu gọn padding ═══ */
@media (max-width: 768px) {
    .container { padding-left: .7rem !important; padding-right: .7rem !important; }
    .mobile-view { gap: .8rem !important; }
}

/* ═══ CHẾ ĐỘ FULL ═══ */
.practice-full-modal {
    position: fixed !important;
    inset: 0 !important;
    z-index: 2500 !important;
    display: none;
    flex-direction: column !important;
    overflow: hidden !important;
}
.practice-full-modal.show { display: flex !important; }

.practice-full-header,
.pf-filters,
.practice-full-nav {
    flex: 0 0 auto !important;
}

.practice-full-body {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
}

.practice-full-input {
    width: 100% !important;
    text-align: center !important;
    font-size: clamp(1.15rem, 2.2vw, 1.6rem) !important;
}


/* ═══════════════════════════════════════════════════════════════════
   ★★★ FAVORITES TAB — 3 TAB CÙNG HÀNG TRÊN PC ★★★
   ═══════════════════════════════════════════════════════════════════ */

@media (min-width: 769px) {
    .ds-main-row {
        grid-template-columns: 1fr 1fr 1fr !important;
    }
}

@media (max-width: 768px) {
    .ds-main-row {
        grid-template-columns: 1fr 1fr !important;
    }
}

@media (max-width: 500px) {
    .ds-main-row {
        grid-template-columns: 1fr !important;
    }
}


/* ═══════════════════════════════════════════════════════════════════
   ★★★ HEADER DESIGN ★★★
   ═══════════════════════════════════════════════════════════════════ */

.header {
    position: relative;
    padding: .25rem 0;
}

.header-inner {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    gap: 1rem !important;
}

.logo {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: .9rem !important;
}

.logo-icon {
    width: clamp(46px, 4.5vw, 58px) !important;
    height: clamp(46px, 4.5vw, 58px) !important;
    border-radius: clamp(12px, 1.2vw, 16px) !important;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 40%, #d946ef 100%) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: #fff !important;
    font-size: clamp(1.2rem, 1.8vw, 1.6rem) !important;
    flex-shrink: 0 !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow:
        0 6px 20px rgba(139, 92, 246, 0.45),
        0 2px 6px rgba(139, 92, 246, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    transition: transform .35s cubic-bezier(.34,1.56,.64,1),
                box-shadow .35s ease !important;
}

.logo-icon::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
        115deg,
        transparent 30%,
        rgba(255, 255, 255, 0.35) 50%,
        transparent 70%
    );
    transform: translateX(-100%) rotate(25deg);
    transition: transform .8s ease;
    pointer-events: none;
}
.logo-icon:hover::before {
    transform: translateX(100%) rotate(25deg);
}

.logo-icon::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 20%,
        rgba(255, 255, 255, 0.4), transparent 55%);
    pointer-events: none;
}

.logo-icon:hover {
    transform: translateY(-2px) rotate(-4deg) scale(1.04);
    box-shadow:
        0 10px 28px rgba(139, 92, 246, 0.6),
        0 4px 10px rgba(139, 92, 246, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
}

.logo-text {
    display: flex !important;
    flex-direction: column !important;
    line-height: 1.1 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    gap: 4px !important;
}

.logo-text .title {
    font-size: clamp(1.25rem, 1.9vw, 1.7rem) !important;
    font-weight: 900 !important;
    letter-spacing: -0.025em !important;
    line-height: 1.15 !important;
    background: linear-gradient(135deg, #1e293b 0%, #4f46e5 50%, #7c3aed 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    color: transparent !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    position: relative !important;
}
[data-theme="dark"] .logo-text .title {
    background: linear-gradient(135deg, #f1f5f9 0%, #a5b4fc 50%, #c4b5fd 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

.logo-text .subtitle {
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    padding: 0.25rem 0.7rem !important;
    border-radius: 999px !important;

    background: linear-gradient(
        135deg,
        rgba(99, 102, 241, 0.13) 0%,
        rgba(139, 92, 246, 0.13) 50%,
        rgba(217, 70, 239, 0.13) 100%
    ) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;

    color: #5b21b6 !important;
    font-size: clamp(.68rem, .85vw, .78rem) !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;

    margin-top: 3px !important;
    padding-left: 0.6rem !important;

    width: fit-content !important;
    max-width: 100% !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;

    box-shadow:
        0 1px 3px rgba(139, 92, 246, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;

    transition: transform .3s ease, box-shadow .3s ease !important;
}
.logo-text .subtitle:hover {
    transform: translateY(-1px);
    box-shadow:
        0 4px 12px rgba(139, 92, 246, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
}

.logo-text .subtitle::before {
    content: '✦';
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: #d946ef !important;
    font-size: 0.9em !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
    text-shadow:
        0 0 6px rgba(217, 70, 239, 0.7),
        0 0 12px rgba(139, 92, 246, 0.5) !important;
    animation: sparkleSubtitle 2.5s ease-in-out infinite !important;
}
@keyframes sparkleSubtitle {
    0%, 100% {
        opacity: 0.65;
        transform: scale(1) rotate(0deg);
    }
    50% {
        opacity: 1;
        transform: scale(1.2) rotate(18deg);
        text-shadow:
            0 0 10px rgba(217, 70, 239, 0.9),
            0 0 18px rgba(139, 92, 246, 0.7);
    }
}

[data-theme="dark"] .logo-text .subtitle {
    background: linear-gradient(
        135deg,
        rgba(99, 102, 241, 0.28) 0%,
        rgba(139, 92, 246, 0.28) 50%,
        rgba(217, 70, 239, 0.28) 100%
    ) !important;
    border-color: rgba(165, 180, 252, 0.45) !important;
    color: #ddd6fe !important;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}
[data-theme="dark"] .logo-text .subtitle::before {
    color: #f0abfc !important;
    text-shadow:
        0 0 8px rgba(240, 171, 252, 0.9),
        0 0 16px rgba(165, 180, 252, 0.6) !important;
}

.header-actions {
    flex: 0 0 auto !important;
    margin-left: auto !important;
    display: flex !important;
    gap: .5rem !important;
    align-items: center !important;
}

.header-actions .icon-btn {
    width: clamp(34px, 3vw, 40px) !important;
    height: clamp(34px, 3vw, 40px) !important;
    border-radius: 11px !important;
    border: 1.5px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text-2) !important;
    font-size: clamp(.82rem, 1vw, .95rem) !important;
    transition: transform .25s cubic-bezier(.34,1.56,.64,1),
                background .25s ease,
                color .25s ease,
                border-color .25s ease,
                box-shadow .25s ease !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
}
.header-actions .icon-btn:hover {
    background: linear-gradient(135deg, #eff6ff, #ede9fe) !important;
    color: #4f46e5 !important;
    border-color: #a5b4fc !important;
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 6px 16px rgba(139, 92, 246, 0.25) !important;
}
[data-theme="dark"] .header-actions .icon-btn:hover {
    background: linear-gradient(135deg, rgba(59,130,246,.2), rgba(139,92,246,.25)) !important;
    color: #a5b4fc !important;
    border-color: rgba(165, 180, 252, 0.5) !important;
}

.header-actions .trial-badge {
    position: relative !important;
    overflow: hidden !important;
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #ea580c 100%) !important;
    color: #fff !important;
    font-weight: 800 !important;
    letter-spacing: 0.03em !important;
    border: none !important;
    box-shadow:
        0 3px 10px rgba(245, 158, 11, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.15) !important;
}
.header-actions .trial-badge::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.5),
        transparent
    );
    animation: shimmerBadge 2.8s infinite;
    pointer-events: none;
}
@keyframes shimmerBadge {
    0% { left: -100%; }
    60%, 100% { left: 200%; }
}

.header-actions .demo-badge {
    background: linear-gradient(135deg, #fef3c7, #fde68a) !important;
    color: #78350f !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    border: 1.5px solid #f59e0b !important;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.25) !important;
}

@media (max-width: 768px) {
    .logo { gap: .65rem !important; }
    .logo-icon {
        width: 44px !important;
        height: 44px !important;
        border-radius: 11px !important;
        font-size: 1.15rem !important;
    }
    .logo-text { gap: 3px !important; }
    .logo-text .title { font-size: 1.15rem !important; }
    .logo-text .subtitle {
        font-size: .6rem !important;
        padding: 0.2rem 0.55rem !important;
        gap: 0.35rem !important;
    }
    .header-inner { gap: .5rem !important; }
    .header-actions { gap: .35rem !important; }
    .header-actions .icon-btn {
        width: 34px !important;
        height: 34px !important;
        font-size: .82rem !important;
    }
}

@media (max-width: 400px) {
    .logo-text .subtitle {
        display: none !important;
    }
    .logo-icon {
        width: 40px !important;
        height: 40px !important;
        font-size: 1rem !important;
    }
    .logo-text .title { font-size: 1.05rem !important; }
}
"""


# ═══════════════════════════════════════════════════════════════════
#  GHÉP CSS
# ═══════════════════════════════════════════════════════════════════
full_css = (
    build_ui_css()
    + "\n/* ==== SOCIAL CSS ==== */\n" + build_social_css()
    + "\n/* ==== ACCOUNTS + RENEWAL CSS ==== */\n" + auth_css
    + "\n/* ==== INTRO CSS ==== */\n" + build_intro_css()
    + "\n/* ==== ❤️ FAVORITES CSS ==== */\n" + build_favorites_css()
    + "\n/* ==== 💬 CHAT SUPPORT CSS ==== */\n" + build_chat_css()
    + "\n/* ==== 📋 ADMIN CHAT MANAGER CSS ==== */\n" + build_admin_chat_css()
    + "\n/* ==== 🎯 DRAGGABLE FAB CSS ==== */\n" + build_draggable_fab_css()
    + "\n/* ==== FULLWIDTH SCALE + HEADER DESIGN (override cuối) ==== */\n" + FULLWIDTH_CSS
)

# ═══════════════════════════════════════════════════════════════════
#  GHÉP HTML BODY
# ═══════════════════════════════════════════════════════════════════
ui_html = build_ui_html()
ui_html = ui_html.replace("<!-- __TIKTOK_BAR__ -->", build_tiktok_bar_html())
ui_html = ui_html.replace("<!-- __QUICK_INTRO_BANNER__ -->", build_intro_html())

# ⬇️⬇️⬇️ Chèn snippet Favorites vào HTML
_fav_html = build_favorites_html()

# ═══ 1. Tab Yêu thích — chèn TRỰC TIẾP vào ds-main-row ═══
ui_html = ui_html.replace(
    '<!-- __FAV_DATASET_TAB__ -->',
    _fav_html["dataset_tab"]
)
if 'data-dataset-group="favorites"' not in ui_html:
    print("⚠️  Chưa chèn được tab Yêu thích — kiểm tra placeholder")
    print("   <!-- __FAV_DATASET_TAB__ --> trong ui_template.py")
else:
    print("✅ Đã chèn tab Yêu thích vào ds-main-row")

# ═══ 2. HAI NÚT FLOAT trong Practice Full ═══
_pf_buttons = _fav_html["pf_float_btn"] + '\n' + _fav_html["pf_fav_only_btn"]

ui_html = ui_html.replace(
    '<a class="pf-tiktok-float" id="pfTiktokFloat"',
    _pf_buttons + '\n<a class="pf-tiktok-float" id="pfTiktokFloat"'
)

# ═══ 3. Dropdown item Yêu thích ═══
_dd_patterns = [
    r'(<button[^>]*class="[^"]*ds-dropdown-item[^"]*"[^>]*data-dataset-group="chuyen-nganh"[^>]*>.*?</button>)',
    r'(<button[^>]*id="dsChuyenNganhDropdownItem"[^>]*>.*?</button>)',
    r'(<a[^>]*class="[^"]*ds-dropdown-item[^"]*"[^>]*data-dataset-group="chuyen-nganh"[^>]*>.*?</a>)',
]

_dd_inserted = False
for _pat in _dd_patterns:
    if _dd_inserted:
        break
    _new, _n = re.subn(
        _pat,
        r'\1\n            ' + _fav_html["dataset_dropdown_item"],
        ui_html,
        count=1,
        flags=re.DOTALL
    )
    if _n > 0:
        ui_html = _new
        _dd_inserted = True
        print("✅ Đã chèn 'Yêu thích' vào dropdown bộ dữ liệu")

if not _dd_inserted:
    print("⚠️  Chưa tìm thấy item Chuyên ngành trong dropdown.")
    print("   → Kiểm tra lại class/id của dropdown item trong ui_template.py")
    print("   → Hoặc chèn thủ công snippet 'dataset_dropdown_item' vào đúng vị trí")

social_html = build_social_html()
ui_html = ui_html.replace(
    '<div class="writer-modal" id="writerModal">',
    social_html + '\n<div class="writer-modal" id="writerModal">'
)

full_body = (
    '<div class="page-wrap">\n'
    + ui_html
    + "\n" + auth_html
    + "\n" + build_chat_html()
    + "\n" + build_admin_chat_html()
    + '\n</div>'
)
def _build_grading_js():
    return r"""
var GRADING_API_URL = 'https://chinese-grading.onrender.com/check';

var _GRADING_FALLBACK_MESSAGES = {
    'correct': 'Dung hoan toan',
    'partial': 'Gan dung',
    'wrong':   'Sai'
};

var _VIETNAMESE_DIACRITICS_REGEX = /[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]/i;

function _normalizeGradingMessage(result) {
    if (!result) return 'Sai';
    var serverMsg = (result.message || '').trim();
    var status = result.status || 'wrong';
    var fallback = _GRADING_FALLBACK_MESSAGES[status] || 'Sai';
    if (!serverMsg) return fallback;
    if (_VIETNAMESE_DIACRITICS_REGEX.test(serverMsg)) return serverMsg;
    return fallback;
}

function _formatGradingErrors(errors) {
    if (!errors || !errors.length) return '';
    return errors.map(function(e) {
        if (!e) return '';
        if (e.type === 'wrong')   return '"' + (e.user || '') + '" thanh "' + (e.correct || '') + '"';
        if (e.type === 'missing') return 'Thieu "' + (e.correct || '') + '"';
        if (e.type === 'extra')   return 'Thua "' + (e.user || '') + '"';
        return '';
    }).filter(Boolean).join(' . ');
}

async function gradeWithAPI(userAnswer, correctAnswer) {
    try {
        var controller = new AbortController();
        var timeoutId = setTimeout(function() { controller.abort(); }, 15000);
        var res = await fetch(GRADING_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_answer: userAnswer,
                correct_answer: correctAnswer
            }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (!res.ok) return null;
        return await res.json();
    } catch(e) {
        console.warn('[Grading] API error:', e);
        return null;
    }
}
window.gradeWithAPI = gradeWithAPI;

(function() {
    var _origCheckInput = window.checkInput;
    window.checkInput = async function(input) {
        var answer = input.dataset.answer;
        var val = input.value.trim();
        if (typeof updateInlinePreview === 'function') updateInlinePreview(input, answer);
        var wrap = input.closest('.card-practice');
        var btn = wrap ? wrap.querySelector('.toggle-check-btn') : null;
        var isVisible = btn && btn.dataset.visible === '1';
        if (!isVisible) return;
        if (!val) {
            var stt0 = input.dataset.stt;
            document.querySelectorAll('[data-check-stt="' + stt0 + '"]').forEach(function(c) { c.innerHTML = ''; });
            return;
        }
        var stt = input.dataset.stt;
        var cells = document.querySelectorAll('[data-check-stt="' + stt + '"]');
        cells.forEach(function(c) { c.innerHTML = '<span class="ai-reason">Dang cham...</span>'; });
        var result = await gradeWithAPI(val, answer);
        if (!result) {
            if (typeof _origCheckInput === 'function') return _origCheckInput.call(this, input);
            return;
        }
        var msg = _normalizeGradingMessage(result);
        var html = '';
        if (result.status === 'correct') {
            html = '<span class="ai-correct">' + msg + '</span>';
        } else if (result.status === 'partial') {
            var pct = result.score ? ' (' + result.score + '%)' : '';
            html = '<span class="ai-partial">' + msg + pct + '</span>';
        } else {
            html = '<span class="ai-wrong">' + msg + '</span>';
        }
        var detail = _formatGradingErrors(result.errors);
        if (detail) html += '<span class="ai-reason">' + detail + '</span>';
        var answerHtml = '<div class="answer-inline-display">' +
            '<span class="answer-inline-label"><i class="fas fa-check-circle"></i> Dap an:</span>' +
            '<span class="answer-inline-text">' + escapeHtml(answer) + '</span>' +
            '</div>';
        cells.forEach(function(c) { c.innerHTML = html + answerHtml; });
    };
    console.log('[Grading] checkInput da override');
})();

(function() {
    var _origCheckFullAnswer = window.checkFullAnswer;
    var _pfGradeToken = 0;
    var _pfDebounceTimer = null;
    window.checkFullAnswer = function() {
        clearTimeout(_pfDebounceTimer);
        _pfDebounceTimer = setTimeout(function() { _doCheckFullAnswer(); }, 400);
    };
    async function _doCheckFullAnswer() {
        var input = document.getElementById('pfInput');
        var statusEl = document.getElementById('pfStatus');
        if (!input || !statusEl) return;
        var val = input.value.trim();
        if (!val) {
            statusEl.innerHTML = '';
            statusEl.className = 'practice-full-status';
            return;
        }
        var answer = (typeof pfCurrentAnswer !== 'undefined') ? pfCurrentAnswer : '';
        if (!answer) return;
        var myToken = ++_pfGradeToken;
        statusEl.innerHTML = '<span class="ai-reason">Dang cham...</span>';
        statusEl.className = 'practice-full-status';
        var result = await gradeWithAPI(val, answer);
        if (myToken !== _pfGradeToken) return;
        if (input.value.trim() !== val) return;
        if (!result) {
            if (typeof _origCheckFullAnswer === 'function') return _origCheckFullAnswer.apply(this, arguments);
            return;
        }
        var msg = _normalizeGradingMessage(result);
        var html = '';
        if (result.status === 'correct') {
            html = '<span class="ai-correct">' + msg + '</span>';
            statusEl.className = 'practice-full-status correct';
        } else if (result.status === 'partial') {
            var pct = result.score ? ' (' + result.score + '%)' : '';
            html = '<span class="ai-partial">' + msg + pct + '</span>';
            statusEl.className = 'practice-full-status partial';
        } else {
            html = '<span class="ai-wrong">' + msg + '</span>';
            statusEl.className = 'practice-full-status wrong';
        }
        var detail = _formatGradingErrors(result.errors);
        if (detail) html += '<span class="ai-reason">' + detail + '</span>';
        statusEl.innerHTML = html;
    }
    console.log('[Grading] checkFullAnswer da override');
})();
"""
# ═══════════════════════════════════════════════════════════════════
#  GHÉP JS
# ═══════════════════════════════════════════════════════════════════
full_js = (
    # ⭐ 1. Config — PHẢI CHÈN ĐẦU TIÊN (inject window.TELEGRAM_*, ZALO_*, SITE_NAME)
    build_config_js(CONFIG)
    # ⭐ 2. Telegram notify module — định nghĩa window.__sendTelegramNotify()
    + "\n/* ==== 📨 TELEGRAM NOTIFY ==== */\n" + build_telegram_notify_js()
    # 3. Các module còn lại
    + "\n/* ==== UI JS ==== */\n" + build_ui_js()
    + "\n/* ==== SOCIAL JS ==== */\n" + build_social_js()
    + "\n/* ==== ACCOUNTS + RENEWAL JS ==== */\n" + auth_js
    + "\n/* ==== INTRO JS ==== */\n" + build_intro_js()
    + "\n/* ==== ❤️ FAVORITES JS ==== */\n" + build_favorites_js()
    + "\n/* ==== 💬 CHAT SUPPORT JS ==== */\n" + build_chat_js()
    + "\n/* ==== 📋 ADMIN CHAT MANAGER JS ==== */\n" + build_admin_chat_js()
    + "\n/* ==== 🎯 DRAGGABLE FAB JS ==== */\n" + build_draggable_fab_js()
    + "\n/* ==== 📊 QUOTA JS ==== */\n" + build_quota_js()
    + "\n/* ==== 📊 QUOTA INIT (bind buttons) ==== */\n" + build_quota_init_js()
    + "\n/* ==== 🎯 GRADING API ==== */\n" + _build_grading_js()
)

# ═══════════════════════════════════════════════════════════════════
#  ⭐⭐⭐ FIX (2026-09-28): LOẠI BỎ THẺ <script> THỪA TRONG full_js ⭐⭐⭐
#  Lý do: build_config_js() và build_telegram_notify_js() trả về chuỗi
#         CÓ WRAP trong '<script>...</script>' → khi nhúng vào HTML_SHELL
#         (đã có sẵn <script>__JS__</script>) → LỒNG 2 THẺ SCRIPT
#         → trình duyệt đóng thẻ script sớm → TRANG TRẮNG, code rò rỉ.
#  Giải pháp: strip TẤT CẢ thẻ <script> và </script> khỏi full_js.
# ═══════════════════════════════════════════════════════════════════
full_js = full_js.replace('<script>', '').replace('</script>', '')
full_js = full_js.replace('<SCRIPT>', '').replace('</SCRIPT>', '')
# Fallback: nếu vẫn còn dạng escape '<\/script>' → giữ nguyên an toàn
# (không replace vì đã an toàn)


# ═══════════════════════════════════════════════════════════════════
#  HTML SHELL
# ═══════════════════════════════════════════════════════════════════
HTML_SHELL = r'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, viewport-fit=cover">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<title>Học tiếng Trung · Văn phòng &amp; Công xưởng</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-database-compat.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.5.0/dist/hanzi-writer.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<style>
__CSS__
</style>
</head>
<body>

__BODY__

<script>
/* ============ DỮ LIỆU + CONFIG ============ */
var RAW_DATA = __DATA__;
var DATASET_REGISTRY = __DATASET_REGISTRY__;
var CURRENT_DATASET = 'tonghop';

var FIREBASE_CONFIG = __FIREBASE_CONFIG__;

var DEMO_LIMIT = __DEMO_LIMIT__;
var DEMO_DAILY_LIMIT = __DEMO_DAILY_LIMIT__;
var DEMO_HSK_MAX = __DEMO_HSK_MAX__;

var TRIAL_MAX_QUESTIONS = __TRIAL_MAX_QUESTIONS__;
var TRIAL_MAX_HSK = __TRIAL_MAX_HSK__;
var TRIAL_UNLIMITED_WRITING = __TRIAL_UNLIMITED_WRITING__;

var TARGET_ADMINS = __TARGET_ADMINS__;
var SUPER_ADMIN = "__SUPER_ADMIN__";
var ZALO_PHONE = "__ZALO_PHONE__";
var ZALO_NAME = "__ZALO_NAME__";
var TIKTOK_USERNAME = "__TIKTOK_USERNAME__";
var TIKTOK_NICKNAME = "__TIKTOK_NICKNAME__";
var TIKTOK_AVATAR = "__TIKTOK_AVATAR__";
var TIKTOK_URL = "__TIKTOK_URL__";
var SYNONYMS = __SYNONYMS__;
var FILLER_WORDS = __FILLER_WORDS__;
var ONBOARDING_CONFIG = __ONBOARDING_CONFIG__;

var $ = function(id) { return document.getElementById(id); };

__JS__

/* ============ ĐỒNG BỘ RAW_DATA KHI ĐỔI DATASET ============ */
window.__switchRawData = function(datasetId) {
    if (!DATASET_REGISTRY || !DATASET_REGISTRY[datasetId]) return false;
    RAW_DATA = DATASET_REGISTRY[datasetId].data || [];
    CURRENT_DATASET = datasetId;
    return true;
};
</script>

<script>
(function() {
    'use strict';
    try {
        var _TG_TOKEN = "__TELEGRAM_BOT_TOKEN__";
        var _TG_CHAT = "__TELEGRAM_CHAT_ID__";

        console.log('📲 Telegram module init:', {
            hasToken: _TG_TOKEN && _TG_TOKEN.indexOf('__') !== 0 && _TG_TOKEN.length > 20,
            tokenPreview: (_TG_TOKEN && _TG_TOKEN.length > 15)
                ? _TG_TOKEN.substring(0, 15) + '...'
                : '(empty)',
            chatId: _TG_CHAT || '(empty)'
        });

        window.sendTelegramMessage = function(text) {
            try {
                if (!_TG_TOKEN || !_TG_CHAT || _TG_TOKEN.indexOf('__') === 0 || _TG_TOKEN.length < 20) {
                    console.log('⚠️ Telegram chưa cấu hình — bỏ qua');
                    return;
                }
                fetch('https://api.telegram.org/bot' + _TG_TOKEN + '/sendMessage', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chat_id: _TG_CHAT,
                        text: text,
                        parse_mode: 'HTML',
                        disable_web_page_preview: true
                    })
                })
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    if (d.ok) console.log('✅ Telegram sent OK');
                    else console.warn('⚠️ Telegram error:', d.description);
                })
                .catch(function(e) { console.warn('❌ Telegram fetch:', e); });
            } catch(e) { console.warn('sendTelegramMessage:', e); }
        };

        window.notifyTelegramUserPaid = function(reqData) {
            try {
                var msg = '🔔 <b>CÓ YÊU CẦU GIA HẠN MỚI</b>\n';
                msg += '━━━━━━━━━━━━━━━━━━━━\n';
                msg += '👤 <b>' + (reqData.name || reqData.email) + '</b>\n';
                msg += '📧 <code>' + reqData.email + '</code>\n';
                msg += '💰 <b>' + (reqData.amount || 0).toLocaleString('vi-VN') + 'đ</b>\n';
                msg += '📦 ' + (reqData.packageLabel || reqData.package || '');
                if (reqData.isPermanent) msg += ' 💎 <b>VĨNH VIỄN</b>';
                msg += '\n';
                msg += '⏱ ' + (reqData.isPermanent ? 'Mãi mãi' : (reqData.days || 0) + ' ngày') + '\n';
                msg += '🔑 <code>' + (reqData.transferCode || '') + '</code>\n';
                msg += '⚡ <b>Vào Admin Panel xác nhận!</b>';
                window.sendTelegramMessage(msg);
            } catch(e) { console.warn('notifyTelegramUserPaid:', e); }
        };

        window.notifyTelegramAdminConfirmed = function(reqData, newExpiry) {
            try {
                var msg = '✅ <b>ĐÃ XÁC NHẬN GIA HẠN</b>\n';
                msg += '━━━━━━━━━━━━━━━━━━━━\n';
                msg += '👤 <b>' + (reqData.name || reqData.email) + '</b>\n';
                msg += '📧 <code>' + reqData.email + '</code>\n';
                msg += '💰 <b>' + (reqData.amount || 0).toLocaleString('vi-VN') + 'đ</b>\n';
                if (reqData.isPermanent) msg += '💎 <b>Đã kích hoạt VĨNH VIỄN</b>\n';
                else if (newExpiry) msg += '📅 Hạn mới: <b>' + newExpiry + '</b>\n';
                msg += '🕐 ' + new Date().toLocaleString('vi-VN');
                window.sendTelegramMessage(msg);
            } catch(e) { console.warn('notifyTelegramAdminConfirmed:', e); }
        };

        console.log('✅ Telegram module loaded');
    } catch(e) {
        console.error('❌ Telegram module failed (KHÔNG ảnh hưởng app):', e);
    }
})();
</script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════
#  RENDER + GHI FILE
# ═══════════════════════════════════════════════════════════════════
html_output = (HTML_SHELL
    # 1. Nhúng khối lớn
    .replace("__CSS__",  full_css)
    .replace("__BODY__", full_body)
    .replace("__JS__",   full_js)

    # 2. Data blobs (đã escape "</" qua _json_blob)
    .replace("__DATA__",              json_data)
    .replace("__DATASET_REGISTRY__",  dataset_registry_json)
    .replace("__FIREBASE_CONFIG__",   firebase_config_json)
    .replace("__SYNONYMS__",          synonyms_json)
    .replace("__FILLER_WORDS__",      fillers_json)
    .replace("__ONBOARDING_CONFIG__", onboarding_config_json)

    # 3. Numeric configs
    .replace("__DEMO_LIMIT__",            str(int(CONFIG["demo_limit"])))
    .replace("__DEMO_DAILY_LIMIT__",      str(int(CONFIG["demo_daily_limit"])))
    .replace("__DEMO_HSK_MAX__",          str(int(CONFIG["demo_hsk_max"])))
    .replace("__TRIAL_MAX_QUESTIONS__",   str(int(CONFIG.get("trial_max_questions", 50))))
    .replace("__TRIAL_MAX_HSK__",         str(int(CONFIG.get("trial_max_hsk", 5))))
    .replace("__TRIAL_UNLIMITED_WRITING__",
             "true" if CONFIG.get("trial_unlimited_writing", True) else "false")
    .replace("__TARGET_ADMINS__",         str(int(CONFIG["target_admins"])))

    # 4. String configs
    .replace("__SUPER_ADMIN__",        _js_str(CONFIG["super_admin"]))
    .replace("__ZALO_PHONE__",         _js_str(CONFIG["zalo_phone"]))
    .replace("__ZALO_NAME__",          _js_str(CONFIG["zalo_name"]))
    .replace("__TIKTOK_USERNAME__",    _js_str(CONFIG["tiktok_username"]))
    .replace("__TIKTOK_NICKNAME__",    _js_str(CONFIG["tiktok_nickname"]))
    .replace("__TIKTOK_AVATAR__",      _js_str(CONFIG["tiktok_avatar"]))
    .replace("__TIKTOK_URL__",         _js_str(CONFIG["tiktok_url"]))
    .replace("__TELEGRAM_BOT_TOKEN__", _js_str(telegram_bot_token))
    .replace("__TELEGRAM_CHAT_ID__",   _js_str(telegram_chat_id))
)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_output)

size_kb = os.path.getsize(OUTPUT_HTML) / 1024
total_datasets = len(DATASET_REGISTRY)
total_questions = sum(ds["count"] for ds in DATASET_REGISTRY.values())

print(f"\n🎉 Đã tạo: {OUTPUT_HTML}")
print(f"📦 Kích thước: {size_kb:.1f} KB")
print(f"📚 Tổng số bộ dữ liệu: {total_datasets} (1 tổng hợp + {_chuyen_nganh_count} chuyên ngành)")
print(f"📝 Tổng số câu hỏi: {total_questions}")
print(f"❤️  Yêu thích: 3 tab cùng hàng (PC) + dropdown + 2 nút float")
print(f"✅ Subtitle đã đổi thành PILL nổi bật với icon ✦")
print(f"✅ Đã thêm Dataset Selector 2 cấp + badge NEW cho Chuyên ngành")
print(f"✅ Đã thêm Intro banner + Modal 6 slide hướng dẫn")
print(f"💬 Chat Support: đã thêm (user ↔ admin)")
print(f"📊 Quota Dashboard: đã thêm vào Admin Panel")
print(f"👥 User Online (RTDB): đã thêm section vào Admin Panel")

# ─── Onboarding info ───
_onb = CONFIG.get("onboarding", {})
if _onb.get("demo", {}).get("enabled"):
    _d = _onb["demo"]
    print(f"✅ Onboarding Demo: {_d.get('max_questions', 0)} câu, "
          f"HSK {_d.get('hsk_allowed', [])}, "
          f"tối đa {_d.get('topics_per_user', 3)} chủ đề")
if _onb.get("trial", {}).get("enabled"):
    _t = _onb["trial"]
    print(f"✅ Onboarding Trial: {_t.get('max_questions', 0)} câu, "
          f"HSK {_t.get('hsk_allowed', [])}, "
          f"tối đa {_t.get('topics_per_user', 5)} chủ đề")
