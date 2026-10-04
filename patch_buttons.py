# -*- coding: utf-8 -*-
r"""
patch_buttons.py - Cover CSS nút dataset trong index.html.
                    CHỈ CHÈN CSS, KHÔNG SỬA HTML.

Fix 4 vấn đề:
  1. Nút Từ vựng: ẩn icon vương miện
  2. Nút Từ vựng: badge PREMIUM nổi rõ
  3. Nút Chuyên ngành: badge NEW nổi rõ
  4. Nút Yêu thích + Chuyên ngành: bấm được

Cách dùng:
    python patch_buttons.py
"""
import os
import re
import sys


# =================================================================
#  CSS DUY NHẤT — CHỈ OVERRIDE, KHÔNG ĐỤNG HTML
# =================================================================
BUTTONS_CSS = r"""
/* ═══════════════════════════════════════════════════════════ */
/* PATCH_BUTTONS: FIX 4 VẤN ĐỀ (CHỈ CSS, KHÔNG SỬA HTML)       */
/* ═══════════════════════════════════════════════════════════ */

/* ⭐ FIX 1: NÚT TỪ VỰNG — ẨN ICON VƯƠNG MIỆN (MỌI LOẠI ICON) */
.ds-btn[data-dataset="tu-vung"] > i,
.ds-btn[data-dataset="tu-vung"] > i.fas,
.ds-btn[data-dataset="tu-vung"] > i.far,
.ds-btn[data-dataset="tu-vung"] > i.fab,
.ds-btn[data-dataset="tu-vung"] > i[class*="fa-"],
.ds-btn[data-dataset="tu-vung"] > i[class*="icon"],
.ds-btn[data-dataset="tu-vung"] .ds-btn-icon,
.ds-btn[data-dataset="tu-vung"] .vocab-icon,
.ds-btn[data-dataset="tu-vung"] .vocab-crown {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Nút Từ vựng — chữ full width (không bị icon chiếm chỗ) */
.ds-btn[data-dataset="tu-vung"] {
    padding-left: 1rem !important;
}
.ds-btn[data-dataset="tu-vung"] > span,
.ds-btn[data-dataset="tu-vung"] .ds-btn-text {
    flex: 1 1 100% !important;
    min-width: 0 !important;
    padding-right: 0 !important;
}

/* ⭐ FIX 2: BADGE PREMIUM Ở NÚT TỪ VỰNG — NỔI RÕ */
.ds-btn[data-dataset="tu-vung"] .ds-vocab-badge,
.ds-btn[data-dataset="tu-vung"] [class*="vocab-badge"],
.ds-btn[data-dataset="tu-vung"] [class*="premium-badge"] {
    position: absolute !important;
    top: -8px !important;
    right: -8px !important;
    z-index: 100 !important;
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #fff !important;
    font-size: .58rem !important;
    font-weight: 900 !important;
    padding: .18rem .55rem !important;
    border-radius: 50px !important;
    letter-spacing: .5px !important;
    text-transform: uppercase !important;
    box-shadow: 0 2px 8px rgba(124,58,237,.5), 0 0 0 2px var(--surface) !important;
    pointer-events: none !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    line-height: 1.4 !important;
}

/* ⭐ FIX 3: BADGE NEW Ở NÚT CHUYÊN NGÀNH — NỔI RÕ */
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-new-badge,
.ds-btn[data-dataset-group="chuyen-nganh"] [class*="new-badge"] {
    position: absolute !important;
    top: -8px !important;
    right: -8px !important;
    z-index: 100 !important;
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: #fff !important;
    font-size: .58rem !important;
    font-weight: 900 !important;
    padding: .18rem .55rem !important;
    border-radius: 50px !important;
    letter-spacing: .5px !important;
    box-shadow: 0 2px 8px rgba(220,38,38,.5), 0 0 0 2px var(--surface) !important;
    pointer-events: none !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    animation: dsNewPulse 1.6s ease-in-out infinite !important;
    line-height: 1.4 !important;
}
@keyframes dsNewPulse {
    0%,100% { transform: scale(1); }
    50%     { transform: scale(1.1); }
}

/* ⭐ FIX 4: ĐẢM BẢO NÚT YÊU THÍCH + CHUYÊN NGÀNH BẤM ĐƯỢC */
.ds-btn[data-dataset-group="favorites"],
.ds-btn[data-dataset-group="chuyen-nganh"] {
    pointer-events: auto !important;
    cursor: pointer !important;
    z-index: 10 !important;
}

/* Text nhận click */
.ds-btn[data-dataset-group="favorites"] > span,
.ds-btn[data-dataset-group="chuyen-nganh"] > span,
.ds-btn[data-dataset-group="favorites"] .ds-btn-text,
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-btn-text {
    pointer-events: auto !important;
    z-index: 20 !important;
    position: relative !important;
}

/* Icon + badge + arrow KHÔNG chặn click */
.ds-btn[data-dataset-group="favorites"] > i,
.ds-btn[data-dataset-group="chuyen-nganh"] > i:not(.ds-arrow),
.ds-btn[data-dataset-group="favorites"] .ds-btn-icon,
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-btn-icon,
.ds-btn[data-dataset-group="favorites"] .ds-fav-badge,
.ds-btn[data-dataset-group="favorites"] .ds-fav-lock,
.ds-btn[data-dataset-group="favorites"]::before,
.ds-btn[data-dataset-group="favorites"]::after,
.ds-btn[data-dataset-group="chuyen-nganh"]::before,
.ds-btn[data-dataset-group="chuyen-nganh"]::after {
    pointer-events: none !important;
}

/* ⭐ FIX 5: NÚT YÊU THÍCH — KHÔNG CẮT CHỮ "Câu đã lưu" */
.ds-btn[data-dataset-group="favorites"] .ds-btn-sub,
.ds-btn[data-dataset-group="favorites"] > span {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    -webkit-line-clamp: unset !important;
    -webkit-box-orient: unset !important;
    display: block !important;
}

/* ⭐ Đảm bảo mọi nút trong .ds-main-row đều bấm được */
.ds-main-row > .ds-btn {
    pointer-events: auto !important;
    cursor: pointer !important;
}
.ds-main-row > .ds-btn > i.ds-btn-icon {
    pointer-events: none !important;
}
"""


# =================================================================
#  PATCH — CHỈ CHÈN CSS
# =================================================================
def patch_css(html):
    """
    Chèn CSS mới — LUÔN XÓA CSS CŨ TRƯỚC (idempotent an toàn).
    """
    # XÓA CSS PATCH_BUTTONS CŨ (nếu có)
    pat_old = re.compile(
        r'/\* ═+ \*/\s*/\* PATCH_BUTTONS:.*?(?=</style>)',
        re.DOTALL
    )
    html, n_removed = pat_old.subn('', html)
    if n_removed > 0:
        print("   [clean] Da xoa " + str(n_removed) + " block CSS cu")

    # CHÈN CSS MỚI
    pat = re.compile(r'(\s*)(</style>)', re.MULTILINE)
    html, n = pat.subn(
        lambda m: m.group(1) + BUTTONS_CSS + m.group(1) + m.group(2),
        html, count=1
    )
    if n == 0:
        print("   [!] Khong tim thay </style>")
    else:
        print("   [OK CSS] Da chen CSS fix 4 van de")
    return html


# =================================================================
#  MAIN
# =================================================================
def patch_all_buttons(index_path="index.html"):
    print("=" * 62)
    print("[patch_buttons] Fix 4 van de (CHI CSS, KHONG SUA HTML)")
    print("=" * 62)

    if not os.path.isfile(index_path):
        print("[X] Khong thay " + index_path)
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    print("")
    print("[1/1] Patch CSS...")
    html = patch_css(html)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(index_path) / 1024
    print("")
    print("=" * 62)
    print("[patch_buttons] HOAN TAT!")
    print("[patch_buttons] File: " + index_path +
          " (" + str(round(size_kb, 1)) + " KB)")
    print("=" * 62)
    return True


if __name__ == "__main__":
    if not os.path.isfile("index.html") and os.path.isfile("../index.html"):
        os.chdir("..")
        print("[patch_buttons] Phat hien chay tu scripts/ -> chdir..")

    ok = patch_all_buttons("index.html")
    sys.exit(0 if ok else 1)
