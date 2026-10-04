# -*- coding: utf-8 -*-
r"""
patch_buttons.py - Cover CSS nút dataset — TẤT CẢ CÙNG MÀU TÍM.
                    - Ẩn icon vương miện nút Từ vựng
                    - Chữ TRẮNG khi active (không bị đen)
                    - Parse số có chữ K/M (1K+, 1.5K+...)
                    - Giữ HTML gốc cho chuyen-nganh + favorites

Cách dùng:
    python patch_buttons.py
"""
import os
import re
import sys
import unicodedata


# =================================================================
#  CONFIG — NỘI DUNG TỪNG NÚT
# =================================================================
BUTTON_CONFIG = {
    "tonghop": {
        "icon": "fa-book-open",
        "title_html": "<b>1750+</b> Câu phản xạ",
        "sub": "Văn phòng · Công xưởng",
    },
    "tu-vung": {
        "icon": "",
        "title_html": "<b>11000+</b> Từ vựng HSK",
        "sub": "Mẹo nhớ · Bộ thủ",
    },
}

DEFAULT_CONFIG = {
    "icon": "fa-comments",
    "title_template": "<b>{count}</b> {name}",
    "sub_template": "Hội thoại thực tế",
}


# =================================================================
#  CSS — TẤT CẢ NÚT CÙNG MÀU TÍM
# =================================================================
BUTTONS_CSS = r"""
/* ═══════════════════════════════════════════════════════════ */
/* PATCH_BUTTONS: TẤT CẢ NÚT CÙNG MÀU TÍM + ẨN ICON VƯƠNG MIỆN */
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

/* ⭐⭐⭐ ẨN ICON VƯƠNG MIỆN Ở NÚT TỪ VỰNG — MỌI CÁCH ⭐⭐⭐ */
button[data-dataset="tu-vung"] i,
button[data-dataset="tu-vung"] > i,
button[data-dataset="tu-vung"] > i.fas,
button[data-dataset="tu-vung"] > i.far,
button[data-dataset="tu-vung"] > i.fab,
button[data-dataset="tu-vung"] > i[class*="fa-"],
button[data-dataset="tu-vung"] > i[class*="icon"],
button[data-dataset="tu-vung"] .ds-btn-icon,
button[data-dataset="tu-vung"] .vocab-icon,
button[data-dataset="tu-vung"] .vocab-crown,
button[data-dataset="tu-vung"] .crown-icon,
button[data-dataset="tu-vung"] img {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    position: absolute !important;
    left: -9999px !important;
}

/* ⭐ Nút Từ vựng — padding trái bình thường */
button[data-dataset="tu-vung"] {
    padding-left: .85rem !important;
}

/* ── Nút cơ bản — TẤT CẢ NÚT ── */
button[data-dataset="tonghop"],
button[data-dataset="tu-vung"],
button[data-dataset-group="chuyen-nganh"],
button[data-dataset-group="favorites"] {
    display: flex !important;
    align-items: center !important;
    gap: .65rem !important;
    padding: .65rem .85rem !important;
    min-height: 60px !important;
    height: 100% !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family: inherit !important;
    text-align: left !important;
    cursor: pointer !important;
    transition: all .2s ease !important;
    position: relative !important;
    overflow: visible !important;
    pointer-events: auto !important;
    z-index: 1 !important;
}
button[data-dataset="tonghop"]:hover,
button[data-dataset="tu-vung"]:hover,
button[data-dataset-group="chuyen-nganh"]:hover,
button[data-dataset-group="favorites"]:hover {
    border-color: var(--primary) !important;
    background: var(--surface-2) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px -6px rgba(15,23,42,.15) !important;
}

/* ── Icon khối — màu tím ── */
button[data-dataset="tonghop"] > i:first-child,
button[data-dataset-group="chuyen-nganh"] > i:first-child,
button[data-dataset-group="favorites"] > i:first-child,
button[data-dataset="tonghop"] .ds-btn-icon,
button[data-dataset-group="chuyen-nganh"] .ds-btn-icon,
button[data-dataset-group="favorites"] .ds-btn-icon {
    flex-shrink: 0 !important;
    width: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.05rem !important;
    background: linear-gradient(135deg, rgba(99,102,241,.14), rgba(139,92,246,.08)) !important;
    color: var(--primary) !important;
    pointer-events: none !important;
}

/* ── Khối text ── */
button[data-dataset="tonghop"] .ds-btn-text,
button[data-dataset="tu-vung"] .ds-btn-text,
button[data-dataset-group="chuyen-nganh"] .ds-btn-text,
button[data-dataset-group="favorites"] .ds-btn-text {
    flex: 1 !important;
    min-width: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: .12rem !important;
    pointer-events: auto !important;
    z-index: 2 !important;
    position: relative !important;
}
button[data-dataset="tonghop"] .ds-btn-title,
button[data-dataset="tonghop"] .ds-btn-title b,
button[data-dataset="tu-vung"] .ds-btn-title,
button[data-dataset="tu-vung"] .ds-btn-title b,
button[data-dataset-group="chuyen-nganh"] .ds-btn-title,
button[data-dataset-group="chuyen-nganh"] .ds-btn-title b,
button[data-dataset-group="favorites"] .ds-btn-title,
button[data-dataset-group="favorites"] .ds-btn-title b {
    font-size: clamp(.78rem, 1vw, .9rem) !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    letter-spacing: -.01em !important;
}
button[data-dataset="tonghop"] .ds-btn-sub,
button[data-dataset="tu-vung"] .ds-btn-sub,
button[data-dataset-group="chuyen-nganh"] .ds-btn-sub,
button[data-dataset-group="favorites"] .ds-btn-sub {
    font-size: clamp(.62rem, .78vw, .72rem) !important;
    font-weight: 600 !important;
    color: var(--text-3) !important;
    line-height: 1.25 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* ⭐⭐⭐ ACTIVE — CHỮ TRẮNG TRÊN NỀN TÍM ⭐⭐⭐ */
button[data-dataset="tonghop"].active,
button[data-dataset="tu-vung"].active,
button[data-dataset-group="chuyen-nganh"].active,
button[data-dataset-group="favorites"].active {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    border-color: transparent !important;
    box-shadow: 0 6px 18px -4px rgba(124,58,237,.45) !important;
    transform: translateY(-2px) !important;
}
button[data-dataset="tonghop"].active .ds-btn-title,
button[data-dataset="tonghop"].active .ds-btn-title b,
button[data-dataset="tu-vung"].active .ds-btn-title,
button[data-dataset="tu-vung"].active .ds-btn-title b,
button[data-dataset-group="chuyen-nganh"].active .ds-btn-title,
button[data-dataset-group="chuyen-nganh"].active .ds-btn-title b,
button[data-dataset-group="favorites"].active .ds-btn-title,
button[data-dataset-group="favorites"].active .ds-btn-title b {
    color: #ffffff !important;
    text-shadow: 0 1px 2px rgba(0,0,0,.15) !important;
}
button[data-dataset="tonghop"].active .ds-btn-sub,
button[data-dataset="tu-vung"].active .ds-btn-sub,
button[data-dataset-group="chuyen-nganh"].active .ds-btn-sub,
button[data-dataset-group="favorites"].active .ds-btn-sub {
    color: rgba(255,255,255,.85) !important;
}
button[data-dataset="tonghop"].active > i:first-child,
button[data-dataset-group="chuyen-nganh"].active > i:first-child,
button[data-dataset-group="favorites"].active > i:first-child,
button[data-dataset="tonghop"].active .ds-btn-icon,
button[data-dataset-group="chuyen-nganh"].active .ds-btn-icon,
button[data-dataset-group="favorites"].active .ds-btn-icon {
    background: rgba(255,255,255,.25) !important;
    color: #ffffff !important;
}

/* ── Arrow Chuyên ngành ── */
button[data-dataset-group="chuyen-nganh"] {
    padding-right: 2.2rem !important;
}
button[data-dataset-group="chuyen-nganh"] .ds-arrow {
    position: absolute !important;
    right: .75rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    font-size: .7rem !important;
    color: var(--text-3) ! scaleimportant;
    transition: transform .25s !important;
    pointer-events(1: none !important.;
    z-index: 5 !1important;
}
button[data-dataset-group);="chuyen-nganh"].active .ds-arrow {
    transform: translateY(-50%) rotate(180deg) !important;
    color: #ffffff !important;
}

/* ── Badge NEW ── */
button[data-dataset-group="chuyen-nganh"] .ds-new-badge {
    position: absolute !important;
    top: -8px !important;
    right: -8px !important;
    padding: .18rem .55rem !important;
    border-radius: 50px !important;
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: #fff !important;
    font-size: .58rem !important;
    font-weight: 900 !important;
    letter-spacing: .5px !important;
    box-shadow: 0 2px 8px rgba(220,38,38,.5), 0 0 0 2px var(--surface) !important;
    z-index: 100 !important;
    pointer-events: none !important;
    white-space: nowrap !important;
    animation: dsNewPulse 1.6s ease-in-out infinite !important;
}
@keyframes dsNewPulse {
    0%,100% { transform: scale(1); }
    50%     { transform: }
}

/* ── Badge PREMIUM ── */
button[data-dataset="tu-vung"] .ds-vocab-badge,
button[data-dataset="tu-vung"] [class*="vocab-badge"] {
    position: absolute !important;
    top: -8px !important;
    right: -8px !important;
    padding: .18rem .55rem !important;
    border-radius: 50px !important;
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #fff !important;
    font-size: .58rem !important;
    font-weight: 900 !important;
    letter-spacing: .5px !important;
    text-transform: uppercase !important;
    box-shadow: 0 2px 8px rgba(124,58,237,.5), 0 0 0 2px var(--surface) !important;
    pointer-events: none !important;
    white-space: nowrap !important;
    z-index: 100 !important;
}

/* ── DARK MODE ── */
[data-theme="dark"] button[data-dataset="tonghop"],
[data-theme="dark"] button[data-dataset="tu-vung"],
[data-theme="dark"] button[data-dataset-group="chuyen-nganh"],
[data-theme="dark"] button[data-dataset-group="favorites"] {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}
[data-theme="dark"] button[data-dataset="tonghop"] > i:first-child,
[data-theme="dark"] button[data-dataset-group="chuyen-nganh"] > i:first-child,
[data-theme="dark"] button[data-dataset-group="favorites"] > i:first-child {
    background: linear-gradient(135deg, rgba(99,102,241,.28), rgba(139,92,246,.18)) !important;
}
[data-theme="dark"] button[data-dataset="tonghop"].active,
[data-theme="dark"] button[data-dataset="tu-vung"].active,
[data-theme="dark"] button[data-dataset-group="chuyen-nganh"].active,
[data-theme="dark"] button[data-dataset-group="favorites"].active {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
}

/* ── MOBILE ── */
@media (max-width: 500px) {
    button[data-dataset="tonghop"],
    button[data-dataset="tu-vung"],
    button[data-dataset-group="chuyen-nganh"],
    button[data-dataset-group="favorites"] {
        min-height: 56px !important;
        padding: .55rem .7rem !important;
    }
    button[data-dataset="tonghop"] > i:first-child,
    button[data-dataset-group="chuyen-nganh"] > i:first-child,
    button[data-dataset-group="favorites"] > i:first-child {
        width: 32px !important;
        height: 32px !important;
        font-size: .92rem !important;
    }
}

/* ⭐ FIX CLICK */
button[data-dataset-group="chuyen-nganh"],
button[data-dataset-group="favorites"] {
    pointer-events: auto !important;
    cursor: pointer !important;
}
button[data-dataset-group="chuyen-nganh"] > i,
button[data-dataset-group="chuyen-nganh"] > i.fas,
button[data-dataset-group="chuyen-nganh"] > .ds-new-badge,
button[data-dataset-group="favorites"] > i,
button[data-dataset-group="favorites"] > i.fas,
button[data-dataset-group="favorites"] > .ds-fav-badge,
button[data-dataset-group="favorites"] > .ds-fav-lock {
    pointer-events: none !important;
}
"""


# =================================================================
#  HTML GENERATOR
# =================================================================
def build_button_html(config_key, extra=None):
    cfg = BUTTON_CONFIG.get(config_key)
    if cfg is None:
        cfg = dict(DEFAULT_CONFIG)
    else:
        cfg = dict(cfg)

    if extra:
        if "title_html" in extra:
            cfg["title_html"] = extra["title_html"]
        if "sub" in extra:
            cfg["sub"] = extra["sub"]
        if "icon" in extra:
            cfg["icon"] = extra["icon"]
        if "dataset_id" in extra:
            cfg["dataset_id"] = extra["dataset_id"]

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

    if "dataset_id" in cfg:
        data_attr = 'data-dataset="' + cfg["dataset_id"] + '"'
    else:
        data_attr = 'data-dataset="' + config_key + '"'

    active_cls = " active" if config_key == "tonghop" else ""

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
#  PATCH CSS
# =================================================================
def patch_css(html):
    """Chèn CSS mới — LUÔN XÓA CSS CŨ TRƯỚC."""
    pat_old = re.compile(
        r'/\* ═+ \*/\s*/\* PATCH_BUTTONS:.*?(?=</style>)',
        re.DOTALL
    )
    html, n_removed = pat_old.subn('', html)
    if n_removed > 0:
        print("   [clean] Da xoa " + str(n_removed) + " block CSS cu")

    pat = re.compile(r'(\s*)(</style>)', re.MULTILINE)
    html, n = pat.subn(
        lambda m: m.group(1) + BUTTONS_CSS + m.group(1) + m.group(2),
        html, count=1
    )
    if n == 0:
        print("   [!] Khong tim thay </style>")
    else:
        print("   [OK CSS] Da chen CSS tat ca nut cung mau tim")
    return html


# =================================================================
#  PATCH BUTTONS
# =================================================================
def patch_button_tonghop(html):
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


def patch_button_tu_vung(html):
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


def patch_other_buttons(html):
    """Patch nút giao tiếp + nút khác. SKIP chuyen-nganh + favorites."""
    pat_all = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset="([^"]+)"[^>]*>(.*?)</button>',
        re.MULTILINE | re.DOTALL
    )

    SKIP_IDS = {"tonghop", "tu-vung", "chuyen-nganh", "favorites"}

    def replacer(match):
        ds_id = match.group(1)
        if ds_id in SKIP_IDS:
            return match.group(0)

        inner = match.group(2)
        text = re.sub(r'<[^>]+>', ' ', inner)
        text = re.sub(r'\s+', ' ', text).strip()

        m = re.match(r'^([\d\.]+[KkMm]?\+?)\s+(.+)$', text)
        if m:
            count = m.group(1)
            name = m.group(2)
        else:
            count = ""
            name = text

        if '<br' in inner.lower():
            parts = re.split(r'<br\s*/?>', inner)
            if len(parts) >= 2:
                first = re.sub(r'<[^>]+>', ' ', parts[0]).strip()
                rest = ' '.join(
                    re.sub(r'<[^>]+>', ' ', p).strip()
                    for p in parts[1:]
                )
                m2 = re.match(r'^([\d\.]+[KkMm]?\+?)\s+(.+)$', first)
                if m2:
                    count = m2.group(1)
                    name = m2.group(2)
                sub = re.sub(r'\s+', ' ', rest).strip()
            else:
                sub = DEFAULT_CONFIG["sub_template"]
        else:
            sub = DEFAULT_CONFIG["sub_template"]

        title_html = "<b>" + count + "</b> " + name if count else name

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
    print("[patch_buttons] TAT CA NUT CUNG MAU TIM")
    print("=" * 62)

    if not os.path.isfile(index_path):
        print("[X] Khong thay " + index_path)
        return False

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    print("")
    print("[1/4] Patch CSS...")
    html = patch_css(html)

    print("")
    print("[2/4] Patch nut Tong hop...")
    html = patch_button_tonghop(html)

    print("")
    print("[3/4] Patch nut Tu vung...")
    html = patch_button_tu_vung(html)

    print("")
    print("[4/4] Patch nut khac (KHONG patch chuyen-nganh + favorites)...")
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
