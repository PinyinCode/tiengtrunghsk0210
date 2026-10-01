# -*- coding: utf-8 -*-
"""
fix_name.py — Patch tên tab xuống dòng thông minh.

QUY TẮC:
  - Dấu "-" chia tên thành 2 CỤM
  - VD: "Tổ trưởng - Quản lí sản xuất"
        → cụm 1 = "Tổ trưởng", cụm 2 = "Quản lí sản xuất"
  - Đủ chỗ → 1 dòng: "Tổ trưởng - Quản lí sản xuất"
  - Không đủ → 2 dòng:
        Tổ trưởng -
        Quản lí sản xuất
  - Cụm 2 quá dài → tự thu nhỏ font

Cách chạy:
    python scripts/convert.py
    python fix.py
    python fix_name.py
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


PATCH_CSS = r"""

.ds-sub-btn .ds-sub-name {
    flex: 1 1 auto;
    min-width: 0;
    display: block;
    line-height: 1.35;
    text-align: left;
    overflow-wrap: anywhere;
}

.ds-sub-btn .ds-sub-name .c1 {
    display: inline;
    white-space: nowrap;
}

.ds-sub-btn .ds-sub-name .c2 {
    display: inline;
    white-space: normal;
    overflow-wrap: anywhere;
}

.ds-sub-btn .ds-sub-name .dash {
    display: inline;
    color: inherit;
    opacity: .75;
}

.ds-sub-btn .ds-sub-name.wrapped .c1 {
    display: block;
    white-space: nowrap;
}

.ds-sub-btn .ds-sub-name.wrapped .c2 {
    display: block;
    white-space: normal;
    font-size: 0.94em;
    overflow-wrap: anywhere;
}

.ds-sub-btn .ds-sub-name.wrapped.tight .c2 {
    font-size: 0.85em;
    letter-spacing: -0.01em;
}

.ds-sub-btn .ds-sub-name.single {
    display: block;
    white-space: normal;
    overflow-wrap: anywhere;
}
"""


PATCH_JS = r"""
(function() {
    'use strict';

    var DEBUG = false;

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
            if (spanEl.__fixNameRendered === 'single') return;
            spanEl.classList.add('single');
            spanEl.classList.remove('wrapped', 'tight');
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

        spanEl.classList.remove('wrapped', 'tight');

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
            if (DEBUG) console.log('[fix_name.py] SINGLE LINE:', raw);
            return;
        }

        spanEl.classList.add('wrapped');
        if (DEBUG) console.log('[fix_name.py] WRAP:',. raw);

        requestAnimationFrame(function() {
            try {
                var c2b = spanEl.querySelector('.c2');
                if (!c2b) return;

                var c2LineH = getLineHeightPx(c2b);
                var c2ScrollH = c2b.scrollHeight;

                if (c2ScrollH > c2LineH * 1.5) {
                    spanEl.classList.add('tight');
                    if (DEBUG) console.log('[fix_name.py] TIGHT:', raw);

                    setTimeout(function() {
                        var c2LineH2 = getLineHeightPx(c2b);
                        var c2ScrollH2 = c2b.scrollHeight;
                        if (c2ScrollH2 > c2LineH2 * 1.5) {
                            c2b.style.fontSize = '0.8em';
                            c2b.styleletterSpacing = '-0.02em';
                            if (DEBUG) console.log('[fix_name.py] FORCE TIGHT:', raw);
                        }
                    }, 60);
                } else {
                    spanEl.classList.remove('tight');
                }
            } catch(e) {
                if (DEBUG) console.warn('[fix_name.py] measure c2:', e);
            }
        });
    }

    function processAll() {
        var nodes = document.querySelectorAll('.ds-sub-name');
        for (var i = 0; i < nodes.length; i++) {
            try {
                processNameSpan(nodes[i]);
            } catch(e) {
                if (DEBUG) console.warn('[fix_name.py] error:', e);
            }
        }
    }

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

    var _timer = null;
    if (typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function() {
            clearTimeout(_timer);
            _timer = setTimeout(processAll, 150);
        });
        if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    var _resizeTimer = null;
    window.addEventListener('resize', function() {
        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(function() {
            var nodes = document.querySelectorAll('.ds-sub-name');
            for (var i = 0; i < nodes.length; i++) {
                nodes[i].__fixNameRendered = null;
            }
            processAll();
        }, 250);
    });

    document.addEventListener('click', function(e) {
        var target = e.target;
        if (!target) return;
        if (target.closest &&
            target.closest('[data-dataset-group="chuyen-nganh"]')) {
            scheduleProcess(150);
            scheduleProcess(400);
        }
    }, true);

    if (DEBUG) console.log('[fix_name.py] Loaded');
})();
"""


def main():
    print("=" * 62)
    print("[fix_name.py] Patch ten tab -> xuong dong thong minh")
    print("=" * 62)

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    print("")
    print("[BUOC 1] Xoa patch cu (neu co)...")

    html = html.replace(
        "nameSpan.className = 'ds-sub-name';",
        "nameSpan.className = 'ds-sub-name';"
    )

    print("")
    print("[BUOC 2] Patch JS render nameSpan...")

    if "nameSpan.className = 'ds-sub-name'" in html:
        print("   [skip] Da patch truoc do (JS render)")
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
            print("   [OK] Da patch JS render nameSpan")
        else:
            print("   [!] Khong tim thay pattern 'nameSpan'")

    print("")
    print("[BUOC 3] Xoa CSS cu + them CSS moi...")

    css_old_patterns = [
        r"\.ds-sub-btn \.ds-sub-name \.c1\s*\{[^}]*\}",
        r"\.ds-sub-btn \.ds-sub-name \.c2\s*\{[^}]*\}",
        r"\.ds-sub-btn \.ds-sub-name \.dash\s*\{[^}]*\}",
        r"\.ds-sub-btn \.ds-sub-name\.wrapped \.c1\s*\{[^}]*\}",
        r"\.ds-sub-btn \.ds-sub-name\.wrapped \.c2\s*\{[^}]*\}",
        r"\.ds-sub-btn \.ds-sub-name\.wrapped\.tight \.c2\s*\{[^}]*\}",
        r"\.ds-sub-btn \.ds-sub-name\.single\s*\{[^}]*\}",
    ]
    for pat in css_old_patterns:
        html = re.sub(pat, "", html)

    pat_style = re.compile(r"(\s*)(</style>)", re.MULTILINE)
    html, n2 = pat_style.subn(r"\1" + PATCH_CSS + r"\1\2", html, count=1)
    if n2 > 0:
        print("   [OK] Da them CSS moi")
    else:
        print("   [!] Khong tim thay </style>")

    print("")
    print("[BUOC 4] Xoa JS cu + them JS moi...")

    html = re.sub(
        r"<script>\s*/\*\s*═+\s*FIX_NAME\.PY[\s\S]*?</script>",
        "",
        html
    )
    html = re.sub(
        r"<script>\s*\(function\(\)\s*\{\s*'use strict';\s*var DEBUG[\s\S]*?\}\)\(\);\s*</script>",
        "",
        html
    )

    js_block = "\n<script>\n" + PATCH_JS + "\n</script>\n"
    pat_body = re.compile(r"(\s*)(</body>)", re.MULTILINE)
    html, n3 = pat_body.subn(r"\1" + js_block + r"\1\2", html, count=1)
    if n3 > 0:
        print("   [OK] Da them JS moi")
    else:
        print("   [X] Khong tim thay </body>")
        sys.exit(1)

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(INDEX_HTML) / 1024

    print("")
    print("=" * 62)
    print("[fix_name.py] HOAN TAT!")
    print("[fix_name.py] File: " + INDEX_HTML + " (" + str(round(size_kb, 1)) + " KB)")
    print("[fix_name.py] Ten tab se hien thi:")
    print("   - Du cho: 'To truong - Quan li san xuat' (1 dong)")
    print("   - Khong du:")
    print("        To truong -")
    print("        Quan li san xuat")
    print("=" * 62)


if __name__ == "__main__":
    main()
