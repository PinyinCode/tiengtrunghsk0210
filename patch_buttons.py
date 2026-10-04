patch cũ đây # -*- coding: utf-8 -*-
r"""
patch_buttons.py - Cover lại TOÀN BỘ nút dataset trong index.html
                    với layout 2 hàng gọn, đầy đủ nội dung.

Nút được cover:
  1. Tổng hợp      (data-dataset="tonghop")
  2. Chuyên ngành  (data-dataset-group="chuyen-nganh")
  3. Từ vựng HSK   (data-dataset="tu-vung")
  4. Yêu thích     (data-dataset-group="favorites")
  5. 1000+ Câu giao tiếp (data-dataset bất kỳ từ FIXPY_DATASETS)

Cách dùng:
    python patch_buttons.py
Hoặc import:
    from patch_buttons import patch_all_buttons
    patch_all_buttons("index.html")
"""
import os
import re
import sys
import unicodedata


# =================================================================
#  CONFIG — NỘI DUNG TỪNG NÚT
#  Mỗi nút có: icon, hàng 1 (title), hàng 2 (sub), class đặc biệt
# =================================================================
BUTTON_CONFIG = {
    "tonghop": {
        "icon": "fa-book-open",
        "title_html": "<b>1750+</b> Câu phản xạ",
        "sub": "Văn phòng · Công xưởng",
    },
    "chuyen-nganh": {
        "icon": "fa-industry",
        "title_html": "<b>Chuyên ngành</b>",
        "sub": "Theo lĩnh vực",
        "extra_attrs": 'data-dataset-group="chuyen-nganh"',
        "extra_html": (
            '<i class="fas fa-chevron-down ds-arrow"></i>'
            '<span class="ds-new-badge">NEW</span>'
        ),
    },
    "tu-vung": {
        "icon": "",   # ⭐ BỎ ICON VƯƠNG MIỆN
        "title_html": "<b>11000+</b> Từ vựng HSK",
        "sub": "Mẹo nhớ · Bộ thủ",
    },
    "favorites": {
        "icon": "fa-heart",
        "title_html": "<b>Yêu thích</b>",
        "sub": "Câu đã lưu",
        "extra_attrs": 'data-dataset-group="favorites"',
    },
}

# Nút giao tiếp thường đến từ FIXPY_DATASETS → dùng config mặc định
DEFAULT_CONFIG = {
    "icon": "fa-comments",
    "title_template": "<b>{count}</b> {name}",
    "sub_template": "Câu giao tiếp",
}


# =================================================================
#  CSS MỚI — 2 HÀNG GỌN
# =================================================================
BUTTONS_CSS = r"""
/* ═══════════════════════════════════════════════════════════ */
/* PATCH_BUTTONS: DATASET BUTTONS — 2 HÀNG GỌN                 */
/* ═══════════════════════════════════════════════════════════ */

.ds-main-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: .55rem;
    align-items: stretch;
}
@media (max-width: 1100px) {
    .ds-main-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 420px) {
    .ds-main-row { grid-template-columns: 1fr; }
}

/* ── Nút cơ bản ── */
.ds-btn {
    display: flex;
    align-items: center;
    gap: .65rem;
    padding: .7rem .8rem;
    min-height: 68px;             /* ⭐ TĂNG TỪ 60 → 68 */
    height: 100%;
    border: 1.5px solid var(--border);
    border-radius: 12px;
    background: var(--surface);
    color: var(--text);
    font-family: inherit;
    text-align: left;
    cursor: pointer;
    transition: all .2s ease;
    position: relative;
    overflow: visible;
    pointer-events: auto;
    z-index: 1;
}
.ds-btn:hover {
    border-color: var(--primary);
    background: var(--surface-2);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px -6px rgba(15,23,42,.15);
}

/* ── Icon ── */
.ds-btn .ds-btn-icon {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    background: linear-gradient(135deg, rgba(99,102,241,.14), rgba(139,92,246,.08));
    color: var(--primary);
    transition: all .2s;
    pointer-events: none;
}

/* ── Khối text 2 hàng ── */
.ds-btn .ds-btn-text {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: .18rem;
    pointer-events: auto;
    z-index: 2;
    position: relative;
}

/* ⭐ TITLE — cho phép xuống 2 dòng */
.ds-btn .ds-btn-title {
    font-size: clamp(.78rem, 1vw, .9rem);
    font-weight: 700;
    color: var(--text);
    line-height: 1.2;
    letter-spacing: -.01em;
    /* ⭐ Cho phép 2 dòng */
    white-space: normal;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    text-overflow: ellipsis;
    word-break: break-word;
}
.ds-btn .ds-btn-title b {
    font-weight: 900;
    color: var(--text);
    margin-right: .15rem;
}

/* ⭐ SUB — cũng cho phép 2 dòng */
.ds-btn .ds-btn-sub {
    font-size: clamp(.62rem, .78vw, .72rem);
    font-weight: 600;
    color: var(--text-3);
    line-height: 1.25;
    white-space: normal;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    text-overflow: ellipsis;
    word-break: break-word;
}

/* ── Active ── */
.ds-btn.active {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-color: transparent;
    box-shadow: 0 6px 18px -4px rgba(124,58,237,.45);
    transform: translateY(-2px);
}
.ds-btn.active .ds-btn-icon {
    background: rgba(255,255,255,.2);
    color: #fff;
}
.ds-btn.active .ds-btn-title,
.ds-btn.active .ds-btn-title b { color: #fff; }
.ds-btn.active .ds-btn-sub { color: rgba(255,255,255,.82); }

/* ═══ CHUYÊN NGÀNH ═══ */
.ds-btn[data-dataset-group="chuyen-nganh"] {
    padding-right: 2.2rem;
}
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-arrow {
    position: absolute;
    right: .75rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: .7rem;
    color: var(--text-3);
    transition: transform .25s;
    pointer-events: none;
    z-index: 5;
}
.ds-btn[data-dataset-group="chuyen-nganh"].active .ds-arrow {
    transform: translateY(-50%) rotate(180deg);
    color: #fff;
}

/* ⭐ NÚT CHUYÊN NGÀNH — Badge NEW hiện rõ */
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-new-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    padding: .18rem .55rem;
    border-radius: 50px;
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: #fff;
    font-size: .58rem;
    font-weight: 900;
    letter-spacing: .5px;
    box-shadow: 0 2px 8px rgba(220,38,38,.5), 0 0 0 2px var(--surface);
    animation: dsNewPulse 1.6s ease-in-out infinite;
    z-index: 100;
    pointer-events: none;
    white-space: nowrap;
}
@keyframes dsNewPulse {
    0%,100% { transform: scale(1); }
    50%     { transform: scale(1.1); }
}

/* ═══ TỪ VỰNG PREMIUM ═══ */
.ds-btn[data-dataset="tu-vung"] {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border-color: rgba(245,158,11,.5);
}
.ds-btn[data-dataset="tu-vung"] .ds-btn-title,
.ds-btn[data-dataset="tu-vung"] .ds-btn-title b { color: #92400e; }
.ds-btn[data-dataset="tu-vung"] .ds-btn-sub { color: #b45309; }
.ds-btn[data-dataset="tu-vung"]:hover {
    border-color: #f59e0b;
    background: linear-gradient(135deg, #fef3c7, #fde68a);
}
.ds-btn[data-dataset="tu-vung"].active {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    border-color: transparent;
}
.ds-btn[data-dataset="tu-vung"].active .ds-btn-title,
.ds-btn[data-dataset="tu-vung"].active .ds-btn-title b { color: #fff; }
.ds-btn[data-dataset="tu-vung"].active .ds-btn-sub { color: rgba(255,255,255,.85); }

/* ⭐ NÚT TỪ VỰNG — Ẩn icon vương miện */
.ds-btn[data-dataset="tu-vung"] .ds-btn-icon,
.ds-btn[data-dataset="tu-vung"] > i.ds-btn-icon {
    display: none !important;
}

/* ⭐ NÚT TỪ VỰNG — Badge PREMIUM hiện rõ */
.ds-btn[data-dataset="tu-vung"] .ds-vocab-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    padding: .18rem .55rem;
    border-radius: 50px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #fff;
    font-size: .58rem;
    font-weight: 900;
    letter-spacing: .5px;
    text-transform: uppercase;
    box-shadow: 0 2px 8px rgba(124,58,237,.5), 0 0 0 2px var(--surface);
    pointer-events: none;
    white-space: nowrap;
    z-index: 100;
}

/* ═══ YÊU THÍCH ═══ */
.ds-btn[data-dataset-group="favorites"] {
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    border-color: rgba(239,68,68,.35);
    pointer-events: auto;
    cursor: pointer;
    z-index: 5;
}
.ds-btn[data-dataset-group="favorites"] .ds-btn-icon {
    background: linear-gradient(135deg, rgba(239,68,68,.2), rgba(220,38,38,.1));
    color: #ef4444;
}
.ds-btn[data-dataset-group="favorites"] .ds-btn-title,
.ds-btn[data-dataset-group="favorites"] .ds-btn-title b { color: #991b1b; }
.ds-btn[data-dataset-group="favorites"] .ds-btn-sub { color: #b91c1c; }
.ds-btn[data-dataset-group="favorites"].active {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    border-color: transparent;
}
.ds-btn[data-dataset-group="favorites"].active .ds-btn-title,
.ds-btn[data-dataset-group="favorites"].active .ds-btn-title b,
.ds-btn[data-dataset-group="favorites"].active .ds-btn-sub { color: #fff; }

/* ⭐ NÚT YÊU THÍCH — Đảm bảo click được */
.ds-btn[data-dataset-group="favorites"] > i,
.ds-btn[data-dataset-group="favorites"] .ds-fav-badge,
.ds-btn[data-dataset-group="favorites"] .ds-fav-lock,
.ds-btn[data-dataset-group="favorites"]::before,
.ds-btn[data-dataset-group="favorites"]::after {
    pointer-events: none !important;
}

/* ═══ DARK MODE ═══ */
[data-theme="dark"] .ds-btn .ds-btn-icon {
    background: linear-gradient(135deg, rgba(99,102,241,.28), rgba(139,92,246,.18));
}
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] {
    background: linear-gradient(135deg, rgba(245,158,11,.18), rgba(217,119,6,.12));
    border-color: rgba(245,158,11,.45);
}
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] .ds-btn-title,
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] .ds-btn-title b { color: #fcd34d; }
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] .ds-btn-sub { color: #fbbf24; }
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] {
    background: linear-gradient(135deg, rgba(239,68,68,.18), rgba(220,38,38,.1));
    border-color: rgba(239,68,68,.4);
}
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] .ds-btn-title,
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] .ds-btn-title b { color: #fca5a5; }
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] .ds-btn-sub { color: #f87171; }

/* ═══ MOBILE ═══ */
@media (max-width: 500px) {
    .ds-btn {
        min-height: 64px;
        padding: .6rem .7rem;
        gap: .5rem;
    }
    .ds-btn .ds-btn-icon {
        width: 32px;
        height: 32px;
        font-size: .92rem;
        border-radius: 9px;
    }
    .ds-btn .ds-btn-title { font-size: .76rem; }
    .ds-btn .ds-btn-sub   { font-size: .6rem; }
}
"""


# =================================================================
#  HTML GENERATOR
# =================================================================
def build_button_html(config_key, extra=None):
    """Sinh HTML cho 1 nút theo config."""
    cfg = BUTTON_CONFIG.get(config_key)
    if cfg is None:
        cfg = dict(DEFAULT_CONFIG)
    else:
        cfg = dict(cfg)

    # Merge extra data (VD: name, count từ FIXPY_DATASETS)
    if extra:
        if "title_html" in extra:
            cfg["title_html"] = extra["title_html"]
        if "sub" in extra:
            cfg["sub"] = extra["sub"]
        if "icon" in extra:
            cfg["icon"] = extra["icon"]
        if "dataset_id" in extra:
            cfg["dataset_id"] = extra["dataset_id"]

    # Nếu dùng template (cho giao tiếp)
    title = cfg.get("title_html")
    if not title and "title_template" in cfg:
        title = cfg["title_template"].format(
            count=(extra or {}).get("count", ""),
            name=(extra or {}).get("name", "")
        )
    if not title:
        title = config_key

    sub = cfg.get("sub")
    if not sub and "sub_template" in cfg:
        sub = cfg["sub_template"]
    if not sub:
        sub = ""

    icon = cfg.get("icon", "")
    extra_attrs = cfg.get("extra_attrs", "")
    extra_html = cfg.get("extra_html", "")

    # Xác định data attribute
    if "dataset_id" in cfg:
        data_attr = 'data-dataset="' + cfg["dataset_id"] + '"'
    elif config_key == "chuyen-nganh":
        data_attr = 'data-dataset-group="chuyen-nganh"'
    elif config_key == "favorites":
        data_attr = 'data-dataset-group="favorites"'
    else:
        data_attr = 'data-dataset="' + config_key + '"'

    # Class active mặc định cho tonghop
    active_cls = " active" if config_key == "tonghop" else ""

    # ⭐ Chỉ render icon nếu có
    icon_html = ''
    if icon:
        icon_html = '            <i class="fas ' + icon + ' ds-btn-icon"></i>\n'

    return (
        '<button class="ds-btn ds-btn-primary' + active_cls + '" '
        + data_attr + ' ' + extra_attrs + '>\n'
        + icon_html +
        '            <span class="ds-btn-text">\n'
        '                <span class="ds-btn-title">' + title + '</span>\n'
        '                <span class="ds-btn-sub">' + sub + '</span>\n'
        '            </span>\n'
        '            ' + extra_html + '\n'
        '        </button>'
    )


# =================================================================
#  PATCHERS
# =================================================================
def patch_css(html):
    """Chèn CSS mới vào trước </style> (idempotent)."""
    MARKER = "/* PATCH_BUTTONS: DATASET BUTTONS — 2 HÀNG GỌN"

    if MARKER in html:
        print("   [skip CSS] Da co patch_buttons CSS")
        return html

    pat = re.compile(r'(\s*)(</style>)', re.MULTILINE)
    html, n = pat.subn(
        lambda m: m.group(1) + BUTTONS_CSS + m.group(1) + m.group(2),
        html, count=1
    )
    if n == 0:
        print("   [!] Khong tim thay </style>")
    else:
        print("   [OK CSS] Da chen CSS 2 hang gon")
    return html


def patch_button_tonghop(html):
    """Thay nút Tổng hợp."""
    pat = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset="tonghop"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    new_html = build_button_html("tonghop")
    html, n = pat.subn(new_html, html, count=1)
    if n:
        print("   [OK] Patch nut Tong hop")
    else:
        print("   [!] Khong tim thay nut Tong hop")
    return html


def patch_button_chuyen_nganh(html):
    """Thay nút Chuyên ngành."""
    pat = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset-group="chuyen-nganh"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    new_html = build_button_html("chuyen-nganh")
    html, n = pat.subn(new_html, html, count=1)
    if n:
        print("   [OK] Patch nut Chuyen nganh")
    else:
        print("   [!] Khong tim thay nut Chuyen nganh")
    return html


def patch_button_tu_vung(html):
    """Thay nút Từ vựng (nếu tồn tại)."""
    pat = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset="tu-vung"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    if not pat.search(html):
        print("   [skip] Khong co nut Tu vung")
        return html
    new_html = build_button_html("tu-vung")
    html, n = pat.subn(new_html, html, count=1)
    if n:
        print("   [OK] Patch nut Tu vung")
    return html


def patch_button_favorites(html):
    """Thay nút Yêu thích (nếu tồn tại)."""
    pat = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset-group="favorites"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    if not pat.search(html):
        print("   [skip] Khong co nut Yeu thich")
        return html
    new_html = build_button_html("favorites")
    html, n = pat.subn(new_html, html, count=1)
    if n:
        print("   [OK] Patch nut Yeu thich")
    return html


def patch_other_buttons(html):
    """
    Thay các nút .ds-btn[data-dataset="..."] còn lại (không phải tonghop/tu-vung)
    → chủ yếu là nút "1000+ Câu giao tiếp" từ FIXPY_DATASETS.
    """
    pat_all = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset="([^"]+)"[^>]*>(.*?)</button>',
        re.MULTILINE | re.DOTALL
    )

    SKIP_IDS = {"tonghop", "tu-vung"}

    def replacer(match):
        ds_id = match.group(1)
        if ds_id in SKIP_IDS:
            return match.group(0)

        inner = match.group(2)
        text = re.sub(r'<[^>]+>', ' ', inner)
        text = re.sub(r'\s+', ' ', text).strip()

        m = re.match(r'^(\d+\+?)\s+(.+)$', text)
        if m:
            count = m.group(1)
            name = m.group(2)
        else:
            count = ""
            name = text

        # ⭐ Rút gọn tên: bỏ chữ "Câu" ở đầu nếu có
        # VD: "Câu giao tiếp" → "Giao tiếp"
        short_name = name
        if short_name.lower().startswith("câu "):
            short_name = short_name[4:].strip()
        # Capitalize chữ đầu
        if short_name:
            short_name = short_name[0].upper() + short_name[1:]

        # ⭐ Nếu có <br> → lấy phần đầu làm title, phần sau làm sub
        if '<br' in inner.lower():
            parts = re.split(r'<br\s*/?>', inner)
            if len(parts) >= 2:
                first = re.sub(r'<[^>]+>', ' ', parts[0]).strip()
                rest = ' '.join(
                    re.sub(r'<[^>]+>', ' ', p).strip()
                    for p in parts[1:]
                )
                m2 = re.match(r'^([\d\+]+)\s+(.+)$', first)
                if m2:
                    count = m2.group(1)
                    name_part = m2.group(2)
                    # Rút gọn tên
                    short_name = name_part
                    if short_name.lower().startswith("câu "):
                        short_name = short_name[4:].strip()
                    if short_name:
                        short_name = short_name[0].upper() + short_name[1:]
                sub = re.sub(r'\s+', ' ', rest).strip()
            else:
                sub = DEFAULT_CONFIG["sub_template"]
        else:
            sub = DEFAULT_CONFIG["sub_template"]

        # ⭐ Title rút gọn: "<b>1000+</b> Giao tiếp"
        title_html = "<b>" + count + "</b> " + short_name if count else short_name

        return build_button_html(
            "giao-tiep",
            extra={
                "dataset_id": ds_id,
                "title_html": title_html,
                "sub": sub,
                "icon": "fa-comments",
            }
        )

    html, n = pat_all.subn(replacer, html)
    if n:
        print("   [OK] Patch " + str(n) + " nut khac (giao tiep...)")
    return html


# =================================================================
#  MAIN
# =================================================================
def patch_all_buttons(index_path="index.html"):
    print("=" * 62)
    print("[patch_buttons] Cover toan bo nut dataset")
    print("=" * 62)

    if not os.path.isfile(index_path):
        print("[X] Khong thay " + index_path)
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    print("")
    print("[1/5] Patch CSS...")
    html = patch_css(html)

    print("")
    print("[2/5] Patch nut Tong hop...")
    html = patch_button_tonghop(html)

    print("")
    print("[3/5] Patch nut Chuyen nganh...")
    html = patch_button_chuyen_nganh(html)

    print("")
    print("[4/5] Patch nut Tu vung...")
    html = patch_button_tu_vung(html)

    print("")
    print("[5/5] Patch nut Yeu thich + cac nut khac...")
    html = patch_button_favorites(html)
    html = patch_other_buttons(html)

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
