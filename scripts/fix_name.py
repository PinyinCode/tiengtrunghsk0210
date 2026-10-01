# -*- coding: utf-8 -*-
"""
fix_name.py — Patch SAU KHI build: sửa tên tab để xuống dòng thông minh.

KHÔNG đụng vào convert.py, ui_template.py, fix.py.
Chỉ chạy SAU KHI cả 2 file trên đã chạy xong.

QUY TẮC TÊN TAB:
  - Dấu "-" (gạch ngang) chia tên thành 2 CỤM
  - Cụm 1 + cụm 2 cùng dòng nếu đủ chỗ
  - Nếu không đủ → cả cụm 2 xuống dòng (không cắt nửa cụm)

VÍ DỤ:
  "Hành chính - Nhân sự" → 
      Dòng 1: Hành chính - Nhân sự     (nếu vừa)
      hoặc
      Dòng 1: Hành chính
      Dòng 2: Nhân sự                  (nếu không vừa)

Cách chạy:
    python scripts/convert.py
    python fix.py
    python scripts/fix_name.py       ← BƯỚC NÀY
"""
import json
import os
import re
import sys
import unicodedata


# =================================================================
#  CONFIG
# =================================================================
INDEX_HTML = "index.html"

# Nếu chạy từ scripts/ → chuyển về root
if not os.path.isfile(INDEX_HTML):
    if os.path.isfile(os.path.join("..", INDEX_HTML)):
        os.chdir("..")
        print("[fix_name.py] Phat hien chay tu scripts/ -> chuyen ve root")


# =================================================================
#  TÁCH TÊN THÀNH 2 CỤM
# =================================================================
def split_name(name):
    """
    Tách tên thành (cụm_1, cụm_2).
    - Ưu tiên tách tại " - " (space-dash-space)
    - Nếu không có → tách tại "-" đầu tiên
    - Nếu không có dấu - → trả về (name, "")
    """
    if not name:
        return ("", "")
    
    # Normalize
    name = unicodedata.normalize("NFC", str(name).strip())
    
    # Thử tách tại " - " trước (ưu tiên)
    for sep in [" - ", " – ", " — "]:
        if sep in name:
            idx = name.find(sep)
            l1 = name[:idx].strip()
            l2 = name[idx + len(sep):].strip()
            if l1 and l2:
                return (l1, l2)
    
    # Fallback: tách tại "-" (không có space)
    for sep in ["-", "–", "—"]:
        if sep in name:
            idx = name.find(sep)
            l1 = name[:idx].strip()
            l2 = name[idx + len(sep):].strip()
            if l1 and l2:
                return (l1, l2)
    
    return (name, "")


# =================================================================
#  PATCH HTML — thay textContent bằng cấu trúc 2 cụm
# =================================================================
def patch_dataset_buttons(html):
    """
    Tìm các button có `data-dataset="..."` trong `ds-sub-grid`.
    Nhưng vì HTML có thể được render động từ JS → cần patch JS.
    
    Thực tế: tên tab được set trong JS qua `textContent`.
    → Cần patch JS trong `initDatasetSelector()`.
    """
    return html


def patch_js_init_dataset(html):
    """
    Patch hàm `initDatasetSelector()` trong JS:
    - Thay vì set textContent = ds.name
    - → Set innerHTML với cấu trúc 2 cụm có data-attr
    """
    
    # Pattern tìm đoạn code render nameSpan trong sub-btn
    # VD: 
    #   var nameSpan = document.createElement('span');
    #   nameSpan.textContent = ds.name.normalize ? ...;
    #   btn.appendChild(nameSpan);
    
    old_pattern = re.compile(
        r"(var\s+nameSpan\s*=\s*document\.createElement\(['\"]span['\"]\);\s*\n\s*nameSpan\.textContent\s*=\s*ds\.name[^;]*;\s*\n\s*btn\.appendChild\(nameSpan\);)".replace(" ", r"\s*"),
        re.MULTILINE
    )
    
    def _repl(match):
        return """var nameSpan = document.createElement('span');
            nameSpan.className = 'ds-sub-name';
            var _rawName = (ds.name && ds.name.normalize) ? ds.name.normalize('NFC') : (ds.name || '');
            nameSpan.setAttribute('data-raw-name', _rawName);
            nameSpan.textContent = _rawName;
            btn.appendChild(nameSpan);"""
    
    new_html, n = old_pattern.subn(_repl, html)
    return new_html, n


# =================================================================
#  THÊM CSS + JS XỬ LÝ WRAP THÔNG MINH
# =================================================================
PATCH_CSS = r"""
/* ═══════════════════════════════════════════════════════════════
   FIX_NAME.PY: Xử lý tên tab xuống dòng thông minh
   - Tên có dạng "A - B" → tách thành 2 cụm
   - Nếu cụm 1 + cụm 2 vừa 1 dòng → hiển thị "A - B"
   - Nếu không vừa → "A" ⬇ "B" (cả cụm 2 xuống dòng)
   ═══════════════════════════════════════════════════════════════ */

.ds-sub-name {
    flex: 1 1 auto;
    min-width: 0;
    display: inline-flex;
    flex-wrap: wrap;
    align-items: baseline;
    line-height: 1.35;
    white-space: normal;
    overflow-wrap: break-word;
    word-break: normal;
    text-align: left;
}

.ds-sub-name-c1 {
    /* Cụm 1 - không tách */
    white-space: nowrap;
    display: inline-block;
    flex-shrink: 0;
}

.ds-sub-name-c2 {
    /* Cả cụm 2 + dấu - xuống dòng cùng nhau */
    white-space: nowrap;
    display: inline-block;
    flex-shrink: 0;
}

.ds-sub-name-c2 .dash {
    /* Dấu - khi cùng dòng với cụm 1 */
    color: inherit;
    opacity: .7;
    margin: 0 .25em;
}

/* Khi cụm 2 xuống dòng: dấu - có thể ẩn hoặc giữ */
.ds-sub-name.wrapped .ds-sub-name-c2 .dash {
    display: none;
}

/* Fallback cho tên không có dấu - */
.ds-sub-name.single {
    display: block;
    white-space: normal;
    overflow-wrap: break-word;
}
"""


PATCH_JS = r"""
/* ═══════════════════════════════════════════════════════════════
   FIX_NAME.PY: Xử lý tên tab xuống dòng thông minh
   - Sau khi DOM render → tìm các .ds-sub-name
   - Tách tên thành 2 cụm (tại " - ")
   - Đo width cụm 1 + cụm 2
   - Nếu vượt container → gắn class "wrapped" để cụm 2 xuống dòng
   ═══════════════════════════════════════════════════════════════ */
(function() {
    'use strict';
    
    function splitNameByDash(name) {
        if (!name) return [name, ''];
        // Ưu tiên " - "
        var seps = [' - ', ' – ', ' — ', '-', '–', '—'];
        for (var i = 0; i < seps.length; i++) {
            var sep = seps[i];
            var idx = name.indexOf(sep);
            if (idx > 0) {
                var l1 = name.substring(0, idx).trim();
                var l2 = name.substring(idx + sep.length).trim();
                if (l1 && l2) return [l1, l2];
            }
        }
        return [name, ''];
    }
    
    function processNameSpan(spanEl) {
        if (spanEl.__fixNameDone) return;
        spanEl.__fixNameDone = true;
        
        var raw = spanEl.getAttribute('data-raw-name')
                  || spanEl.textContent
                  || '';
        raw = raw.trim();
        if (!raw) return;
        
        var parts = splitNameByDash(raw);
        var c1 = parts[0];
        var c2 = parts[1];
        
        // Không có cụm 2 → giữ nguyên
        if (!c2) {
            spanEl.classList.add('single');
            spanEl.textContent = c1;
            return;
        }
        
        // Có 2 cụm → cấu trúc lại
        spanEl.innerHTML = '';
        
        var span1 = document.createElement('span');
        span1.className = 'ds-sub-name-c1';
        span1.textContent = c1;
        spanEl.appendChild(span1);
        
        var span2 = document.createElement('span');
        span2.className = 'ds-sub-name-c2';
        
        var dashEl = document.createElement('span');
        dashEl.className = 'dash';
        dashEl.textContent = ' - ';
        span2.appendChild(dashEl);
        
        var text2 = document.createElement('span');
        text2.textContent = c2;
        span2.appendChild(text2);
        
        spanEl.appendChild(span2);
        
        // Đo và quyết định wrap
        requestAnimationFrame(function() {
            try {
                var btn = spanEl.closest('.ds-sub-btn');
                if (!btn) return;
                
                // Lấy width available cho name span
                var btnRect = btn.getBoundingClientRect();
                var iconEl = btn.querySelector('i:first-child');
                var iconWidth = iconEl ? iconEl.getBoundingClientRect().width : 0;
                var padding = 24; // padding trái phải
                var gap = 8;
                
                var availableWidth = btnRect.width - iconWidth - padding - gap;
                
                // Tính width nếu để 1 dòng
                var span1Width = span1.getBoundingClientRect().width;
                var span2Width = span2.getBoundingClientRect().width;
                var totalWidth = span1Width + span2Width;
                
                if (totalWidth > availableWidth) {
                    // Không đủ 1 dòng → cho cụm 2 xuống dòng
                    spanEl.classList.add('wrapped');
                } else {
                    spanEl.classList.remove('wrapped');
                }
            } catch(e) {
                console.warn('[fix_name.py] error:', e);
            }
        });
    }
    
    function processAll() {
        document.querySelectorAll('.ds-sub-name').forEach(processNameSpan);
    }
    
    // Chạy sau khi DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(processAll, 100);
        });
    } else {
        setTimeout(processAll, 100);
    }
    
    // Re-process khi có DOM thay đổi (VD: chuyển tab)
    var _timer = null;
    var observer = new MutationObserver(function() {
        clearTimeout(_timer);
        _timer = setTimeout(processAll, 150);
    });
    if (document.body) {
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    // Re-process khi resize (đổi mobile/desktop)
    var _resizeTimer = null;
    window.addEventListener('resize', function() {
        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(function() {
            // Reset để tính lại
            document.querySelectorAll('.ds-sub-name').forEach(function(el) {
                el.__fixNameDone = false;
            });
            processAll();
        }, 200);
    });
    
    console.log('[fix_name.py] Loaded — will process .ds-sub-name elements');
})();
"""


# =================================================================
#  MAIN
# =================================================================
def main():
    print("=" * 62)
    print("[fix_name.py] Patch ten tab -> xuong dong thong minh")
    print("=" * 62)
    
    if not os.path.isfile(INDEX_HTML):
        print("[X] Khong thay " + INDEX_HTML + ". Chay convert.py + fix.py truoc.")
        sys.exit(1)
    
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Kiểm tra đã patch chưa
    if "FIX_NAME.PY" in html and "ds-sub-name" in html:
        print("[!] Da patch truoc do — kiem tra lai")
        # Vẫn tiếp tục để đảm bảo patch mới nhất
    
    # ─── BƯỚC 1: Patch JS để thêm class `ds-sub-name` + data-raw-name ───
    print("")
    print("[BƯỚC 1] Patch JS render nameSpan...")
    
    # Tìm và thay thế đoạn:
    #   var nameSpan = document.createElement('span');
    #   nameSpan.textContent = ds.name.normalize ? ds.name.normalize('NFC') : ds.name;
    #   btn.appendChild(nameSpan);
    
    # Pattern linh hoạt (dùng DOTALL)
    pat1 = re.compile(
        r"var\s+nameSpan\s*=\s*document\.createElement\(\s*['\"]span['\"]\s*\)\s*;"
        r"\s*nameSpan\.textContent\s*=\s*ds\.name[^;]*;"
        r"\s*btn\.appendChild\(\s*nameSpan\s*\)\s*;",
        re.MULTILINE | re.DOTALL
    )
    
    replacement1 = (
        "var nameSpan = document.createElement('span');\n"
        "            nameSpan.className = 'ds-sub-name';\n"
        "            var _rawName = (ds.name && ds.name.normalize) ? ds.name.normalize('NFC') : (ds.name || '');\n"
        "            nameSpan.setAttribute('data-raw-name', _rawName);\n"
        "            nameSpan.textContent = _rawName;\n"
        "            btn.appendChild(nameSpan);"
    )
    
    html, n1 = pat1.subn(replacement1, html, count=1)
    if n1 > 0:
        print("   [OK] Da patch JS render nameSpan (case 1)")
    else:
        print("   [!] Khong tim thay pattern nameSpan")
        print("   → Co the ui_template.py da thay doi. Kiem tra thu cong.")
        
        # Thử pattern khác (nếu có sẵn code đã sửa)
        pat1b = re.compile(
            r"var\s+nameSpan\s*=\s*document\.createElement\(\s*['\"]span['\"]\s*\)\s*;"
            r"(?:(?!btn\.appendChild).)*?"
            r"btn\.appendChild\(\s*nameSpan\s*\)\s*;",
            re.MULTILINE | re.DOTALL
        )
        html, n1b = pat1b.subn(replacement1, html, count=1)
        if n1b > 0:
            print("   [OK] Da patch JS render nameSpan (case fallback)")
    
    # ─── BƯỚC 2: Thêm CSS ───
    print("")
    print("[BƯỚC 2] Them CSS xu ly wrap...")
    
    if "FIX_NAME.PY: Xử lý tên tab" in html:
        print("   [skip] CSS da co san")
    else:
        # Chèn trước </style> cuối cùng
        pat_style = re.compile(r"(\s*)(</style>)", re.MULTILINE)
        html, n2 = pat_style.subn(r"\1" + PATCH_CSS + r"\1\2", html, count=1)
        if n2 > 0:
            print("   [OK] Da them CSS")
        else:
            print("   [!] Khong tim thay </style>")
    
    # ─── BƯỚC 3: Thêm JS wrap logic ───
    print("")
    print("[BƯỚC 3] Them JS xu ly do width...")
    
    if "FIX_NAME.PY: Xử lý tên tab" in html and "processNameSpan" in html:
        print("   [skip] JS da co san")
    else:
        # Chèn trước </body>
        js_block = "\n<script>\n" + PATCH_JS + "\n</script>\n"
        pat_body = re.compile(r"(\s*)(</body>)", re.MULTILINE)
        html, n3 = pat_body.subn(r"\1" + js_block + r"\1\2", html, count=1)
        if n3 > 0:
            print("   [OK] Da them JS")
        else:
            print("   [X] Khong tim thay </body>")
            sys.exit(1)
    
    # ─── GHI FILE ───
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    
    size_kb = os.path.getsize(INDEX_HTML) / 1024
    print("")
    print("=" * 62)
    print("[fix_name.py] HOAN TAT! Da patch " + INDEX_HTML)
    print("[fix_name.py] Kich thuoc: " + str(round(size_kb, 1)) + " KB")
    print("[fix_name.py] Ten tab gio se tu dong xuong dong:")
    print("   - 'Hanh chinh - Nhan su' -> 'Hanh chinh' + 'Nhan su' (2 dong)")
    print("   - Tu dong do width -> quyet dinh 1 hay 2 dong")
    print("=" * 62)


if __name__ == "__main__":
    main()
