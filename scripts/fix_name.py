# -*- coding: utf-8 -*-
"""
fix_name.py — Patch SAU KHI build: tên tab xuống dòng thông minh.

KHÔNG đụng vào convert.py, ui_template.py, fix.py.
Chạy SAU KHI convert.py + fix.py đã chạy xong.

QUY TẮC:
  - Dấu "-" trong tên file chia tên thành 2 CỤM
  - VD: "Hành_chính_-_Nhân_sự.xlsx" → "Hành chính" + "Nhân sự"
  - Cụm 1 + cụm 2 cùng dòng nếu đủ chỗ
  - Nếu không đủ → cụm 2 xuống dòng riêng, ẩn dấu "-"

Cách chạy:
    python scripts/convert.py
    python fix.py
    python scripts/fix_name.py
"""
import os
import re
import sys


# =================================================================
#  CONFIG
# =================================================================
INDEX_HTML = "index.html"

# Nếu chạy từ scripts/ → chuyển về root
if not os.path.isfile(INDEX_HTML):
    if os.path.isfile(os.path.join("..", INDEX_HTML)):
        os.chdir("..")
        print("[fix_name.py] Phat hien chay tu scripts/ -> chuyen ve root")
    else:
        print("[X] Khong thay " + INDEX_HTML)
        print("   → Chay convert.py + fix.py truoc")
        sys.exit(1)


# =================================================================
#  CSS PATCH
# =================================================================
PATCH_CSS = r"""

/* ═══════════════════════════════════════════════════════════════
   FIX_NAME.PY — Tên tab xuống dòng thông minh (theo cụm từ)
   ═══════════════════════════════════════════════════════════════ */

.ds-sub-btn .ds-sub-name {
    flex: 1 1 auto;
    min-width: 0;
    display: block;
    line-height: 1.35;
    text-align: left;
    word-break: normal;
    overflow-wrap: anywhere;
}

/* Cụm 1 — có thể chung dòng với cụm 2 */
.ds-sub-btn .ds-sub-name .c1 {
    display: inline;
    white-space: normal;
    word-break: normal;
    overflow-wrap: anywhere;
}

/* Cụm 2 — mặc định inline, khi wrapped → block */
.ds-sub-btn .ds-sub-name .c2 {
    display: inline;
    white-space: normal;
    word-break: normal;
    overflow-wrap: anywhere;
}

/* Dấu gạch ngang giữa 2 cụm */
.ds-sub-btn .ds-sub-name .dash {
    display: inline;
    color: inherit;
    opacity: .75;
    margin: 0 .25em;
}

/* ⭐ KHI WRAP: cụm 1 và cụm 2 mỗi cái 1 dòng riêng */
.ds-sub-btn .ds-sub-name.wrapped .c1 {
    display: block;
    white-space: normal;
}
.ds-sub-btn .ds-sub-name.wrapped .c2 {
    display: block;
    white-space: normal;
}
.ds-sub-btn .ds-sub-name.wrapped .dash {
    display: none;
}

/* Tên không có dấu - (1 cụm duy nhất) */
.ds-sub-btn .ds-sub-name.single {
    display: block;
    white-space: normal;
    overflow-wrap: anywhere;
}
"""


# =================================================================
#  JS PATCH
# =================================================================
PATCH_JS = r"""
/* ═══════════════════════════════════════════════════════════════
   FIX_NAME.PY — Xử lý tên tab: tách cụm + tự động wrap
   ═══════════════════════════════════════════════════════════════ */
(function() {
    'use strict';

    var DEBUG = false;   // Bật true để xem log

    /* ─────────────────────────────────────────────
       Tách tên thành 2 cụm dựa vào dấu "-"
       ───────────────────────────────────────────── */
    function splitNameByDash(name) {
        if (!name) return [name || '', ''];

        // Ưu tiên dấu có khoảng trắng
        var seps = [' - ', ' – ', ' — ', '-', '–', '—'];

        for (var i = 0; i < seps.length; i++) {
            var sep = seps[i];
            var idx = name.indexOf(sep);
            if (idx > 0) {
                var l1 = name.substring(0, idx).trim();
                var l2 = name.substring(idx + sep.length).trim();
                if (l1 && l2) {
                    return [l1, l2];
                }
            }
        }

        return [name.trim(), ''];
    }

    /* ─────────────────────────────────────────────
       Xử lý 1 span: tách cụm + đo wrap
       ───────────────────────────────────────────── */
    function processNameSpan(spanEl) {
        if (!spanEl) return;

        // Lấy tên gốc (chỉ lấy 1 lần)
        var raw = spanEl.getAttribute('data-raw-name') || '';
        if (!raw) {
            raw = (spanEl.textContent || '').trim();
            spanEl.setAttribute('data-raw-name', raw);
        }
        if (!raw) return;

        // Nếu đã xử lý rồi và không có gì đổi → bỏ qua
        // (Nhưng vẫn cho phép re-measure nếu cần)
        var parts = splitNameByDash(raw);
        var c1 = parts[0];
        var c2 = parts[1];

        // ─── Trường hợp: chỉ có 1 cụm ───
        if (!c2) {
            if (spanEl.__fixNameRendered === 'single') return;
            spanEl.classList.add('single');
            spanEl.classList.remove('wrapped');
            spanEl.textContent = c1;
            spanEl.__fixNameRendered = 'single';
            return;
        }

        // ─── Trường hợp: có 2 cụm ───
        // Nếu đã render 2 cụm rồi → chỉ cần re-measure
        var needRerender = (spanEl.__fixNameRendered !== 'dual');
        if (needRerender) {
            spanEl.innerHTML = '';

            var s1 = document.createElement('span');
            s1.className = 'c1';
            s1.textContent = c1;
            spanEl.appendChild(s1);

            var s2 = document.createElement('span');
            s2.className = 'c2';

            var d = document.createElement('span');
            d.className = 'dash';
            d.textContent = ' - ';
            s2.appendChild(d);

            var t2 = document.createElement('span');
            t2.textContent = c2;
            s2.appendChild(t2);

            spanEl.appendChild(s2);

            spanEl.__fixNameRendered = 'dual';
        }

        // ─── Đo để quyết định wrap ───
        // Reset về trạng thái chưa wrap
        spanEl.classList.remove('wrapped');

        // Force reflow để đo chính xác
        void spanEl.offsetHeight;

        // Đo: nếu chiếm >= 2 dòng → cần wrap
        var cs = window.getComputedStyle(spanEl);
        var lineHeightStr = cs.lineHeight;
        var lineHeight;
        if (lineHeightStr === 'normal') {
            var fontSize = parseFloat(cs.fontSize) || 14;
            lineHeight = fontSize * 1.35;
        } else {
            lineHeight = parseFloat(lineHeightStr) || 20;
        }

        var scrollH = spanEl.scrollHeight;
        var clientH = spanEl.clientHeight;

        // Nếu scrollHeight > 1.5 dòng → đã bị wrap
        var isWrapped = (scrollH > lineHeight * 1.5);

        // Hoặc nếu nội dung cao hơn client (bị overflow)
        if (!isWrapped && scrollH > clientH + 1) {
            isWrapped = true;
        }

        if (isWrapped) {
            spanEl.classList.add('wrapped');
            if (DEBUG) {
                console.log('[fix_name.py] WRAP:', raw,
                            'scrollH=' + scrollH, 'lineH=' + lineHeight);
            }
        } else {
            spanEl.classList.remove('wrapped');
        }
    }

    /* ─────────────────────────────────────────────
       Process tất cả .ds-sub-name hiện có
       ───────────────────────────────────────────── */
    function processAll() {
        var nodes = document.querySelectorAll('.ds-sub-name');
        if (!nodes || nodes.length === 0) return;
        for (var i = 0; i < nodes.length; i++) {
            try {
                processNameSpan(nodes[i]);
            } catch(e) {
                if (DEBUG) console.warn('[fix_name.py] error:', e);
            }
        }
    }

    /* ─────────────────────────────────────────────
       Hook vào DOM ready + MutationObserver
       ───────────────────────────────────────────── */
    function scheduleProcess(delay) {
        setTimeout(processAll, delay || 100);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            scheduleProcess(100);
            scheduleProcess(500);
        });
    } else {
        scheduleProcess(100);
        scheduleProcess(500);
    }

    // Re-process khi DOM thay đổi (VD: chuyển dataset, đổi tier)
    var _timer = null;
    if (typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function() {
            clearTimeout(_timer);
            _timer = setTimeout(processAll, 150);
        });
        if (document.body) {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }

    // Re-process khi resize (đổi mobile/desktop → width thay đổi)
    var _resizeTimer = null;
    window.addEventListener('resize', function() {
        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(function() {
            // Reset state để đo lại
            var nodes = document.querySelectorAll('.ds-sub-name');
            for (var i = 0; i < nodes.length; i++) {
                nodes[i].__fixNameRendered = null;
            }
            processAll();
        }, 250);
    });

    // Re-process khi mở dropdown Chuyên ngành
    document.addEventListener('click', function(e) {
        var target = e.target;
        if (!target) return;
        // Nút chuyên ngành
        if (target.closest &&
            target.closest('[data-dataset-group="chuyen-nganh"]')) {
            scheduleProcess(150);
            scheduleProcess(400);
        }
    }, true);

    if (DEBUG) {
        console.log('[fix_name.py] Loaded');
    }
})();
"""


# =================================================================
#  MAIN
# =================================================================
def main():
    print("=" * 62)
    print("[fix_name.py] Patch ten tab -> xuong dong thong minh")
    print("=" * 62)

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # ─────────────────────────────────────────────
    #  BƯỚC 1: Patch JS render nameSpan
    #  Thêm class ds-sub-name + data-raw-name
    # ─────────────────────────────────────────────
    print("")
    print("[BUOC 1] Patch JS render nameSpan...")

    if "nameSpan.className = 'ds-sub-name'" in html:
        print("   [skip] Da patch truoc do")
    else:
        # Pattern linh hoạt: bắt cả textContent = ds.name...
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
            print("   [OK] Da patch JS render nameSpan")
        else:
            print("   [!] Khong tim thay pattern 'nameSpan'")
            print("   → Kiem tra lai ui_template.py")

    # ─────────────────────────────────────────────
    #  BƯỚC 2: Thêm CSS
    # ─────────────────────────────────────────────
    print("")
    print("[BUOC 2] Them CSS...")

    if "FIX_NAME.PY — Tên tab" in html or "FIX_NAME.PY" in html and ".ds-sub-name" in html:
        print("   [skip] CSS da co san")
    else:
        # Chèn trước </style> cuối cùng
        pat_style = re.compile(r"(\s*)(</style>)", re.MULTILINE)
        html, n2 = pat_style.subn(r"\1" + PATCH_CSS + r"\1\2", html, count=1)
        if n2 > 0:
            print("   [OK] Da them CSS")
        else:
            print("   [!] Khong tim thay </style>")

    # ─────────────────────────────────────────────
    #  BƯỚC 3: Thêm JS xử lý wrap
    # ─────────────────────────────────────────────
    print("")
    print("[BUOC 3] Them JS xu ly wrap...")

    if "FIX_NAME.PY — Xử lý tên tab" in html or "processNameSpan" in html:
        print("   [skip] JS da co san")
    else:
        js_block = "\n<script>\n" + PATCH_JS + "\n</script>\n"
        pat_body = re.compile(r"(\s*)(</body>)", re.MULTILINE)
        html, n3 = pat_body.subn(r"\1" + js_block + r"\1\2", html, count=1)
        if n3 > 0:
            print("   [OK] Da them JS")
        else:
            print("   [X] Khong tim thay </body>")
            sys.exit(1)

    # ─────────────────────────────────────────────
    #  GHI FILE
    # ─────────────────────────────────────────────
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(INDEX_HTML) / 1024

    print("")
    print("=" * 62)
    print("[fix_name.py] HOAN TAT!")
    print("[fix_name.py] File: " + INDEX_HTML + " (" + str(round(size_kb, 1)) + " KB)")
    print("[fix_name.py] Ten tab se tu dong:")
    print("   - Tach 2 cum theo dau '-'")
    print("   - Du cho -> 1 dong: 'Hanh chinh - Nhan su'")
    print("   - Khong du -> 2 dong: 'Hanh chinh' / 'Nhan su'")
    print("=" * 62)


if __name__ == "__main__":
    main()
