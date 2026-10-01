# -*- coding: utf-8 -*-
"""
fix_name.py - Patch ten tab xuong dong + tu thu nho font.
"""
import os
import sys


INDEX_HTML = "index.html"

if not os.path.isfile(INDEX_HTML):
    if os.path.isfile(os.path.join("..", INDEX_HTML)):
        os.chdir("..")
    else:
        print("[X] Khong thay " + INDEX_HTML)
        sys.exit(1)


PATCH_CSS = """
/* ==== FIX_NAME.PY OVERRIDE ==== */
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
}
.ds-sub-btn .ds-sub-name.single {
    display: block !important;
    white-space: normal !important;
}
"""


PATCH_JS = """
(function() {
    'use strict';

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
            spanEl.__done = 'single';
            return;
        }

        if (spanEl.__done !== 'dual') {
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

            spanEl.__done = 'dual';
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

        if (!isWrapped) return;

        spanEl.classList.add('wrapped');

        requestAnimationFrame(function() {
            try {
                var c2b = spanEl.querySelector('.c2');
                var btn = spanEl.closest('.ds-sub-btn');
                if (!c2b || !btn) return;

                var btnRect = btn.getBoundingClientRect();
                var iconEl = btn.querySelector('i:first-child');
                var iconWidth = iconEl ? iconEl.getBoundingClientRect().width : 0;
                var availableWidth = btnRect.width - iconWidth - 32;

                var naturalWidth = c2b.getBoundingClientRect().width;

                if (naturalWidth > availableWidth && availableWidth > 0) {
                    var ratio = availableWidth / naturalWidth;
                    var baseFontSize = parseFloat(
                        window.getComputedStyle(btn).fontSize
                    ) || 14;

                    var newSize = baseFontSize * ratio * 0.95;
                    if (newSize < 9) newSize = 9;

                    c2b.style.fontSize = newSize + 'px';
                    c2b.style.letterSpacing = '-0.02em';

                    console.log('[fix_name] SHRINK to ' + newSize.toFixed(1) + 'px');
                }
            } catch(e) {
                console.warn('[fix_name] error:', e);
            }
        });
    }

    function processAll() {
        var nodes = document.querySelectorAll('.ds-sub-name');
        for (var i = 0; i < nodes.length; i++) {
            try {
                processNameSpan(nodes[i]);
            } catch(e) {}
        }
    }

    setTimeout(processAll, 200);
    setTimeout(processAll, 600);
    setTimeout(processAll, 1500);

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
                nodes[i].__done = null;
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

    # Patch nameSpan JS
    if "nameSpan.className = 'ds-sub-name'" not in html:
        old_a = "var nameSpan = document.createElement('span');"
        idx = html.find(old_a)
        if idx >= 0:
            end_a = html.find("btn.appendChild(nameSpan)", idx)
            if end_a >= 0:
                end_a += len("btn.appendChild(nameSpan);")
                new_block = (
                    "var nameSpan = document.createElement('span');\n"
                    "nameSpan.className = 'ds-sub-name';\n"
                    "var _rawName = (ds.name && ds.name.normalize) ? ds.name.normalize('NFC') : (ds.name || '');\n"
                    "nameSpan.setAttribute('data-raw-name', _rawName);\n"
                    "nameSpan.textContent = _rawName;\n"
                    "btn.appendChild(nameSpan);"
                )
                html = html[:idx] + new_block + html[end_a:]
                print("[1] Patched nameSpan")
            else:
                print("[1] Warning: end not found")
        else:
            print("[1] Warning: start not found")
    else:
        print("[1] Already patched")

    # Add CSS
    pos_style = html.rfind("</style>")
    if pos_style >= 0:
        html = html[:pos_style] + PATCH_CSS + html[pos_style:]
        print("[2] Added CSS")
    else:
        print("[2] Warning: no </style>")

    # Add JS
    pos_body = html.rfind("</body>")
    if pos_body >= 0:
        js_block = "<script>" + PATCH_JS + "</script>"
        html = html[:pos_body] + js_block + html[pos_body:]
        print("[3] Added JS")
    else:
        print("[3] Error: no </body>")
        sys.exit(1)

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(INDEX_HTML) / 1024
    print("")
    print("=" * 62)
    print("[fix_name.py] DONE - " + str(round(size_kb, 1)) + " KB")
    print("=" * 62)


if __name__ == "__main__":
    main()
