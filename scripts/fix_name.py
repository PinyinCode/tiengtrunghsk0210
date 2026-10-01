# -*- coding: utf-8 -*-
"""
fix_name.py — Patch tên tab xuống dòng + tự thu nhỏ font.

CÁCH HOẠT ĐỘNG:
  1. Patch JS render nameSpan (thêm class ds-sub-name + data-raw-name)
  2. Thêm CSS dùng !important để thắng CSS cũ
  3. Thêm JS ở CUỐI cùng → chạy sau JS cũ, ghi đè

KHÔNG cần xoá CSS/JS cũ — chỉ cần override.
"""
import os
import re
import sys


INDEX_HTML = "index.html"

if not os.path.isfile(INDEX_HTML):
    if os.path.isfile(os.path.join("..", INDEX_HTML)):
        os.chdir("..")
        print("[fix_name.py] Chuyen ve root")
    else:
        print("[X] Khong thay " + INDEX_HTML)
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════
#  CSS — DÙNG !important ĐỂ THẮNG CSS CŨ
# ═══════════════════════════════════════════════════════════════════
PATCH_CSS = r"""

/* ==== FIX_NAME.PY — OVERRIDE CSS CŨ ==== */

.ds-sub-btn .ds-sub-name {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    display: block !important;
    line-height: 1.35 !important;
    text-align: left !important;
}

.ds-sub-btn .ds-sub-name .c1 {
    display: inline !important;
    white-space: nowrap !important;
}

.ds-sub-btn .ds-sub-name .c2 {
    display: inline !important;
    white-space: nowrap !important;
}

.ds-sub-btn .ds-sub-name .dash {
    display: inline !important;
    color: inherit !important;
    opacity: .75 !important;
}

.ds-sub-btn .ds-sub-name.wrapped .c1 {
    display: block !important;
    white-space: nowrap !important;
}

.ds-sub-btn .ds-sub-name.wrapped .c2 {
    display: block !important;
    white-space: nowrap !important;
    font-size: 1em !important;
}

.ds-sub-btn .ds-sub-name.single {
    display: block !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}
"""


# ═══════════════════════════════════════════════════════════════════
#  JS — CHẠY SAU CÙNG, GHI ĐÈ JS CŨ
# ═══════════════════════════════════════════════════════════════════
PATCH_JS = r"""
(function() {
    'use strict';

    var DEBUG = true;

    function splitNameByDash(name) {
        if (!name) return [name || '', ''];
        var seps = [' - ', ' -', '- ', '-'];
        for (var i = 0; i < seps.length; i++) {
            var sep = seps[i];
            var idx = name.indexOf(sep);
            if (idx > 0) {
                var l1 = name.substring(0, idx).trim();
                var l2 = name.substring(idx + sep.length).trim();
                if (l1 && l2) return [l1, l2];
            }
        }
        return [name.trim(), ''];
    }

    function getLineHeightPx(el) {
        var cs = window.getComputedStyle(el);
        var lh = cs.lineHeight;
        if (lh === 'normal') {
            var fs = parseFloat(cs.fontSize) || 14;
            return fs * 1.35;
        }
        return parseFloat(lh) || 20;
    }

    function processNameSpan(spanEl) {
        if (!spanEl) return;

        var raw = spanEl.getAttribute('data-raw-name') || '';
        if (!raw) {
            raw = (spanEl.textContent || '').trim();
            spanEl.setAttribute('data-raw-name', raw);
        }
        if (!raw) return;

        var parts = splitNameByDash(raw);
        var c1 = parts[0];
        var c2 = parts[1];

        if (!c2) {
            spanEl.classList.add('single');
            spanEl.classList.remove('wrapped');
            spanEl.textContent = c1;
            spanEl.__fixNameRendered = 'single';
            return;
        }

        var needRerender = (spanEl.__fixNameRendered !== 'dual');
        if (needRerender) {
            spanEl.innerHTML = '';

            var s1 = document.createElement('span');
            s1.className = 'c1';
            s1.textContent = c1;

            var d = document.createElement('span');
            d.className = 'dash';
            d.textContent = ' -';
            s1.appendChild(d);

            spanEl.appendChild(s1);

            var s2 = document.createElement('span');
            s2.className = 'c2';
            s2.textContent = c2;
            spanEl.appendChild(s2);

            spanEl.__fixNameRendered = 'dual';
        }

        spanEl.classList.remove('wrapped');

        var c2El = spanEl.querySelector('.c2');
        if (c2El) {
            c2El.style.fontSize = '';
            c2El.style.letterSpacing = '';
        }

        void spanEl.offsetHeight;

        var lineH = getLineHeightPx(spanEl);
        var scrollH = spanEl.scrollHeight;
        var isWrapped = (scrollH > lineH * 1.5);

        if (!isWrapped) {
            if (DEBUG) console.log('[fix_name.py] SINGLE:', raw);
            return;
        }

        spanEl.classList.add('wrapped');
        if (DEBUG) console.log('[fix_name.py] WRAP:', raw);

        requestAnimationFrame(function() {
            try {
                var c2b = spanEl.querySelector('.c2');
                var btn = spanEl.closest('.ds-sub-btn');
                if (!c2b || !btn) return;

                var btnRect = btn.getBoundingClientRect();
                var iconEl = btn.querySelector('i:first-child');
                var iconWidth = iconEl ? iconEl.getBoundingClientRect().width : 0;
                var padding = 24;
                var gap = 8;

                var availableWidth = btnRect.width - iconWidth - padding - gap;
                var naturalWidth = c2b.getBoundingClientRect().width;

                if (DEBUG) {
                    console.log('[fix_name.py] c2 measure:',
                                'natural=' + Math.round(naturalWidth),
                                'avail=' + Math.round(availableWidth));
                }

                if (naturalWidth > availableWidth && availableWidth > 0) {
                    var ratio = availableWidth / naturalWidth;
                    var baseFontSize = parseFloat(
                        window.getComputedStyle(btn).fontSize
                    ) || 14;

                    var newSize = baseFontSize * ratio * 0.95;
                    var minSize = 9;
                    if (newSize < minSize) newSize = minSize;

                    c2b.style.fontSize = newSize + 'px';
                    c2b.style.letterSpacing = '-0.02em';

                    if (DEBUG) {
                        console.log('[fix_name.py] SHRINK:',
                                    baseFontSize.toFixed(1) + 'px ->',
                                    newSize.toFixed(1) + 'px');
                    }
                }
            } catch(e) {
                if (DEBUG) console.warn('[fix_name.py] error:', e);
            }
        });
    }

    function processAll() {
        var nodes = document.querySelectorAll('.ds-sub-name');
        if (DEBUG && nodes.length > 0) {
            console.log('[fix_name.py] processing', nodes.length, 'nodes');
        }
        for (var i = 0; i < nodes.length; i++) {
            try {
                processNameSpan(nodes[i]);
            } catch(e) {
                if (DEBUG) console.warn('[fix_name.py] error:', e);
            }
        }
    }

    // Chạy nhiều lần để chắc chắn DOM đã render
    setTimeout(processAll, 200);
    setTimeout(processAll, 600);
    setTimeout(processAll, 1500);

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(processAll, 200);
        });
    }

    // Reset khi click chuyên ngành
    document.addEventListener('click', function(e) {
        var target = e.target;
        if (target && target.closest) {
            if (target.closest('[data-dataset-group="chuyen-nganh"]')) {
                setTimeout(processAll, 300);
                setTimeout(processAll, 800);
            }
        }
    }, true);

    window.addEventListener('resize', function() {
        setTimeout(function() {
            var nodes = document.querySelectorAll('.ds-sub-name');
            for (var i = 0; i < nodes.length; i++) {
                nodes[i].__fixNameRendered = null;
            }
            processAll();
        }, 300);
    });

    console.log('[fix_name.py] JS loaded');
})();
"""


def main():
    print("=" * 62)
    print("[fix_name.py] Patch ten tab")
    print("=" * 62)

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # ─── BƯỚC 1: Patch JS render nameSpan ───
    print("")
    print("[1] Patch JS render nameSpan...")

    if "nameSpan.className = 'ds-sub-name'" in html:
        print("   [skip] Da patch")
    else:
        pat1 = re.compile(
            r"var\s+nameSpan\s*=\s*document\.createElement\(\s*['\"]span['\"]\s*\)\s*;"
            r"(?:(?!btn\.appendChild).)*?"
            r"btn\.appendChild\(\s*nameSpan\s*\)\s*;",
            re.MULTILINE | re.DOTALL
        )

        replacement1 = (
            "var nameSpan = document.createElement('span');\n"
            "            nameSpan.className = 'ds-sub-name';\n"
            "            var _rawName = (ds.name && ds.name.normalize)\n"
            "                           ? ds.name.normalize('NFC')\n"
            "                           : (ds.name || '');\n"
            "            nameSpan.setAttribute('data-raw-name', _rawName);\n"
            "            nameSpan.textContent = _rawName;\n"
            "            btn.appendChild(nameSpan);"
        )

        html, n1 = pat1.subn(replacement1, html, count=1)

        if n1 > 0:
            print("   [OK] Patched")
        else:
            print("   [!] Khong tim thay pattern")

    # ─── BƯỚC 2: Thêm CSS ───
    them print("")
    print("[2] Them JS CSS override...")

    pat_style = re.compile(r")
"(\s*)(</style>)",    re.MULTILINE)
    html, n2 = pat_style.subn(r"\1" + PATCH_CSS + r"\ else:
1\2", html, count=1)
    if n2 > 0:
        print("   [OK] Da them CSS")
    else:
        print("   [!] Khong tim thay </style>")

    # ─── BƯỚC 3: Thêm JS ở CUỐI body ───
    print("")
    print("[3] Them JS o cuoi body...")

    js_block = "\n<script>\n" + PATCH_JS + "\n</script>\n"
    pat_body = re.compile(r"(\s*)(</body>)", re.MULTILINE)
    html, n3 = pat_body.subn(r"\1" + js_block + r"\1\2", html, count=1)
    if n3 > 0:
        print("   [OK] Da        print("   [X] Khong tim thay </body>")
        sys.exit(1)

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(INDEX_HTML) / 1024

    print("")
    print("=" * 62)
    print("[fix_name.py] HOAN TAT!")
    print("[fix_name.py] File: " + INDEX_HTML + " (" + str(round(size_kb, 1)) + " KB)")
    print("=" * 62)


if __name__ == "__main__":
    main()
