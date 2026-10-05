# -*- coding: utf-8 -*-
r"""
quick_search.py — Ô TÌM KIẾM NHANH ĐỘC LẬP, ĐI THEO NÚT CHAT
════════════════════════════════════════════════════════════════════

MODULE NÀY KHÔNG SỬA BẤT KỲ FILE NÀO KHÁC.
Chỉ inject thêm CSS + HTML + JS vào index.html sau khi
tất cả module khác đã build xong (fix.py, chat_support.py, ...).

ĐẶC ĐIỂM:
  • Ô search nhanh riêng, KHÔNG đụng #searchInput chính
  • Vị trí: nằm TRONG #chatFloatWrap (trên nút chat)
    → tự động di chuyển theo nút chat
  • Collapse thành icon 🔍 khi không dùng
  • Hỗ trợ cú pháp: "hsk1", "hsk1 5", "hsk1 5 10", "hsk7-9"
  • Enter / nút → filter bảng câu (tạm thời, ghi đè search chính)
  • Esc / ✕ → reset
  • Toast thông báo kết quả
  • Dark mode + responsive mobile
  • Tự động retry nếu #chatFloatWrap chưa tồn tại

CÁCH DÙNG:
  from quick_search import patch_quick_search
  patch_quick_search("index.html")

HOẶC chạy trực tiếp:
  python quick_search.py
"""

import os
import re
import sys


# ═══════════════════════════════════════════════════════════════
#  ID / MARKER (dùng để tránh inject trùng)
# ═══════════════════════════════════════════════════════════════
MARKER_CSS = "/* ===== QUICK_SEARCH_MODULE_CSS ===== */"
MARKER_JS  = "/* ===== QUICK_SEARCH_MODULE_JS  ===== */"


# ═══════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════
def build_quick_search_css():
    return r"""
/* ===== QUICK_SEARCH_MODULE_CSS ===== */
.quick-search-wrap{
    display:flex;align-items:center;gap:.4rem;
    pointer-events:auto;
    position:relative;
}
.quick-search-toggle{
    width:44px;height:44px;border-radius:50%;
    border:2px solid #fff;
    background:linear-gradient(135deg,#0891b2,#0e7490,#155e75);
    color:#fff;cursor:pointer;
    display:flex;align-items:center;justify-content:center;
    font-size:1.05rem;
    box-shadow:0 8px 24px rgba(14,116,144,.45);
    transition:all .3s cubic-bezier(.34,1.56,.64,1);
    flex-shrink:0;position:relative;
    font-family:inherit;padding:0;
}
.quick-search-toggle:hover{
    transform:scale(1.08);
    box-shadow:0 12px 32px rgba(14,116,144,.65);
}
.quick-search-toggle.active{
    background:linear-gradient(135deg,#dc2626,#991b1b);
    box-shadow:0 8px 24px rgba(220,38,38,.55);
}
.quick-search-toggle i{transition:transform .3s;}
.quick-search-toggle.active i{transform:rotate(90deg);}

.quick-search-panel{
    display:flex;align-items:center;gap:.35rem;
    padding:0;border-radius:999px;
    background:var(--surface,#fff);
    border:2px solid var(--border,#e2e8f0);
    box-shadow:0 8px 24px rgba(15,23,42,.15);
    overflow:hidden;
    max-width:0;opacity:0;transform:translateX(-8px);
    transition:max-width .35s cubic-bezier(.34,1.56,.64,1),
               opacity .25s ease,
               transform .3s ease,
               padding .25s ease;
    pointer-events:none;
}
.quick-search-panel.open{
    max-width:340px;opacity:1;transform:translateX(0);
    padding:.25rem .3rem .25rem .75rem;
    pointer-events:auto;
}
[data-theme="dark"] .quick-search-panel{
    background:#1e293b;border-color:#334155;
}
.quick-search-panel input{
    flex:1;min-width:0;border:none;outline:none;
    background:transparent;color:var(--text,#0f172a);
    font-size:.82rem;font-family:inherit;
    padding:.35rem 0;
}
.quick-search-panel input::placeholder{
    color:var(--text-3,#94a3b8);font-size:.78rem;
}
.quick-search-clear,.quick-search-go{
    width:28px;height:28px;border-radius:50%;
    border:none;cursor:pointer;
    display:none;align-items:center;justify-content:center;
    font-size:.72rem;flex-shrink:0;
    transition:.15s;font-family:inherit;padding:0;
}
.quick-search-clear{
    background:var(--surface-2,#f8fafc);
    color:var(--text-2,#475569);
}
.quick-search-clear:hover{
    background:#fee2e2;color:#dc2626;
}
.quick-search-go{
    background:linear-gradient(135deg,#0891b2,#0e7490);
    color:#fff;
}
.quick-search-go:hover{
    transform:scale(1.08);
    box-shadow:0 4px 12px rgba(14,116,144,.5);
}
.quick-search-panel.has-value .quick-search-clear,
.quick-search-panel.has-value .quick-search-go{display:flex;}

.quick-search-hint{
    position:absolute;top:calc(100% + 6px);left:0;
    padding:.35rem .6rem;
    background:rgba(15,23,42,.92);color:#fff;
    font-size:.68rem;border-radius:8px;line-height:1.35;
    pointer-events:none;
    opacity:0;transform:translateY(-4px);
    transition:opacity .2s,transform .2s;
    white-space:nowrap;
    z-index:10;
}
.quick-search-panel.open:focus-within ~ .quick-search-hint,
.quick-search-panel.open:focus-within .quick-search-hint{
    opacity:1;transform:translateY(0);
}
.quick-search-hint kbd{
    display:inline-block;padding:0 .3rem;
    background:rgba(255,255,255,.15);
    border-radius:3px;font-family:monospace;font-size:.95em;
}

.quick-search-toast{
    position:fixed;top:80px;left:50%;
    transform:translateX(-50%) translateY(-20px);
    padding:.7rem 1.2rem;border-radius:50px;
    font-size:.85rem;font-weight:700;color:#fff;
    background:linear-gradient(135deg,#0891b2,#155e75);
    box-shadow:0 8px 24px rgba(14,116,144,.45);
    z-index:99999;opacity:0;
    transition:opacity .25s,transform .3s cubic-bezier(.34,1.56,.64,1);
    pointer-events:none;max-width:90vw;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.quick-search-toast.show{
    opacity:1;transform:translateX(-50%) translateY(0);
}
.quick-search-toast.error{
    background:linear-gradient(135deg,#dc2626,#991b1b);
    box-shadow:0 8px 24px rgba(220,38,38,.5);
}

/* ─── Khi chat mở → ẩn quick search ─── */
body.chat-is-open .quick-search-wrap{
    opacity:0;pointer-events:none;
    transform:translateY(-8px);
    transition:opacity .2s,transform .2s;
}

@media (max-width:768px){
    .quick-search-toggle{width:42px;height:42px;font-size:1rem;}
    .quick-search-panel.open{max-width:calc(100vw - 90px);}
    .quick-search-hint{font-size:.62rem;white-space:normal;max-width:240px;}
}
@media (max-width:400px){
    .quick-search-toggle{width:40px;height:40px;}
}
"""


# ═══════════════════════════════════════════════════════════════
#  JS
# ═══════════════════════════════════════════════════════════════
def build_quick_search_js():
    return r"""
/* ===== QUICK_SEARCH_MODULE_JS  ===== */
(function(){
    'use strict';

    var QS = { open:false, inited:false, retries:0 };

    function $id(id){ return document.getElementById(id); }
    function esc(s){
        if(s==null) return '';
        return String(s)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
    }

    /* ═══════════════════════════════════════════════════════
       1. INJECT DOM vào #chatFloatWrap
       ═══════════════════════════════════════════════════════ */
    function injectDOM(){
        if($id('quickSearchWrap')) return true;

        var wrap = $id('chatFloatWrap');
        if(!wrap){
            QS.retries++;
            if(QS.retries > 60){
                console.warn('[quick-search] #chatFloatWrap không xuất hiện sau 60 lần thử → bỏ qua');
                return false;
            }
            setTimeout(injectDOM, 500);
            return false;
        }

        var div = document.createElement('div');
        div.id = 'quickSearchWrap';
        div.className = 'quick-search-wrap';
        div.innerHTML =
            '<div class="quick-search-panel" id="quickSearchPanel">' +
                '<i class="fas fa-search" style="color:var(--text-3,#94a3b8);font-size:.78rem;flex-shrink:0"></i>' +
                '<input type="text" id="quickSearchInput" ' +
                    'placeholder="hsk1 5 · hsk2 10 20" ' +
                    'autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">' +
                '<button class="quick-search-clear" id="quickSearchClear" type="button" title="Xoá">' +
                    '<i class="fas fa-times"></i>' +
                '</button>' +
                '<button class="quick-search-go" id="quickSearchGo" type="button" title="Tìm">' +
                    '<i class="fas fa-arrow-right"></i>' +
                '</button>' +
            '</div>' +
            '<div class="quick-search-hint">' +
                'Cú pháp: <kbd>hsk1</kbd> · <kbd>hsk1 5</kbd> · <kbd>hsk1 5 10</kbd> · <kbd>hsk7-9</kbd>' +
            '</div>' +
            '<button class="quick-search-toggle" id="quickSearchToggle" type="button" title="Tìm kiếm nhanh">' +
                '<i class="fas fa-search"></i>' +
            '</button>';

        // ⭐ Chèn vào ĐẦU wrapper (nằm TRÊN nút chat)
        wrap.insertBefore(div, wrap.firstChild);
        console.log('[quick-search] ✅ Đã chèn vào #chatFloatWrap');
        return true;
    }

    /* ═══════════════════════════════════════════════════════
       2. PARSE cú pháp (fallback nếu không có window.parseSearchQuery)
       ═══════════════════════════════════════════════════════ */
    function parseQuery(raw){
        // Ưu tiên dùng parser chính nếu có
        if(typeof window.parseSearchQuery === 'function'){
            try{
                var r = window.parseSearchQuery(raw);
                if(r) return r;
            }catch(e){}
        }
        // Fallback: tự parse
        var q = (raw||'').trim();
        if(!q) return null;
        var m = q.toLowerCase().match(/^hsk\s*(7[-\s]*9|\d+)(?:\s+(\d+)(?:\s+(\d+))?)?$/);
        if(!m) return null;

        var hskRaw = m[1].replace(/\s+/g,'');
        var hskNum = hskRaw;
        if(hskNum === '7' || hskNum === '8' || hskNum === '9' || hskNum === '79'){
            hskNum = '7-9';
        }
        var startStt = m[2] ? parseInt(m[2],10) : null;
        var endStt   = m[3] ? parseInt(m[3],10) : startStt;
        if(startStt !== null && endStt !== null && endStt < startStt){
            var t = startStt; startStt = endStt; endStt = t;
        }
        return {
            type:'hsk_stt',
            hsk:(hskNum === '7-9') ? 'HSK7-9' : ('HSK' + hskNum),
            startStt:startStt,
            endStt:endStt,
            original:q
        };
    }

    /* ═══════════════════════════════════════════════════════
       3. LỌC dữ liệu
       ═══════════════════════════════════════════════════════ */
    function filterData(raw, parsed){
        var baseData = [];
        try{
            // Ưu tiên RAW_DATA của scope chính
            if(typeof window.RAW_DATA !== 'undefined' && Array.isArray(window.RAW_DATA)){
                baseData = window.RAW_DATA;
            }
            // Fallback: thử đọc từ FIXPY_DATASETS
            else if(window.FIXPY_DATASETS){
                var curDs = (typeof window.CURRENT_DATASET !== 'undefined')
                            ? window.CURRENT_DATASET : 'tonghop';
                if(window.FIXPY_DATASETS[curDs]){
                    baseData = window.FIXPY_DATASETS[curDs].data || [];
                }
            }
        }catch(e){}

        if(baseData.length === 0) return null;

        if(parsed && parsed.type === 'hsk_stt'){
            var targetHsk = String(parsed.hsk||'').toUpperCase().replace(/\s+/g,'');
            return baseData.filter(function(r){
                var rHsk = String(r.hsk||'').toUpperCase().replace(/\s+/g,'');
                if(rHsk !== targetHsk) return false;
                if(parsed.startStt === null) return true;
                var sttNum = parseInt(String(r.stt).trim(),10);
                if(isNaN(sttNum)) return false;
                return sttNum >= parsed.startStt && sttNum <= parsed.endStt;
            });
        }

        var s = raw.toLowerCase();
        return baseData.filter(function(r){
            return (r.vi && r.vi.toLowerCase().indexOf(s) !== -1) ||
                   (r.zh && r.zh.toLowerCase().indexOf(s) !== -1) ||
                   (r.pinyin && r.pinyin.toLowerCase().indexOf(s) !== -1) ||
                   (r.topic && r.topic.toLowerCase().indexOf(s) !== -1) ||
                   (r.subject && r.subject.toLowerCase().indexOf(s) !== -1);
        });
    }

    /* ═══════════════════════════════════════════════════════
       4. APPLY kết quả vào bảng câu chính
       ═══════════════════════════════════════════════════════ */
    function applyResult(result, raw, parsed){
        if(!result || result.length === 0) return false;

        // ⭐ CÁCH AN TOÀN NHẤT: ghi vào #searchInput chính rồi trigger
        // → không cần truy cập closure `filtered` / `render`
        // Đây là cách duy nhất KHÔNG ĐỤNG code hiện tại.
        var si = $id('searchInput');
        if(!si){
            // Fallback: dùng bridge nếu được expose
            if(typeof window.__applyQuickSearchResult === 'function'){
                try{
                    window.__applyQuickSearchResult(result);
                    return true;
                }catch(e){}
            }
            return false;
        }

        // Nếu là cú pháp đặc biệt (hskX N) → ghi nguyên chuỗi vào #searchInput
        // → applyFilter() sẽ tự parse (vì đã được patch hỗ trợ)
        if(parsed && parsed.type === 'hsk_stt'){
            si.value = raw;
        } else {
            // Text thường → ghi thẳng
            si.value = raw;
        }

        // ⭐ Trigger input event → applyFilter() chạy tự nhiên
        try{
            si.dispatchEvent(new Event('input', { bubbles: true }));
        }catch(e){
            // IE fallback
            var ev = document.createEvent('Event');
            ev.initEvent('input', true, true);
            si.dispatchEvent(ev);
        }

        return true;
    }

    /* ═══════════════════════════════════════════════════════
       5. TOAST
       ═══════════════════════════════════════════════════════ */
    function showToast(msg, isError){
        var old = $id('quickSearchToast');
        if(old) old.remove();

        var t = document.createElement('div');
        t.id = 'quickSearchToast';
        t.className = 'quick-search-toast' + (isError ? ' error' : '');
        t.textContent = msg;
        document.body.appendChild(t);

        requestAnimationFrame(function(){ t.classList.add('show'); });

        setTimeout(function(){
            t.classList.remove('show');
            setTimeout(function(){ if(t.parentNode) t.remove(); }, 300);
        }, 2400);
    }

    /* ═══════════════════════════════════════════════════════
       6. HÀNH ĐỘNG SEARCH
       ═══════════════════════════════════════════════════════ */
    function doSearch(){
        var input = $id('quickSearchInput');
        if(!input) return;
        var raw = input.value.trim();
        if(!raw){
            showToast('Nhập gì đó để tìm...', true);
            input.focus();
            return;
        }

        var parsed = parseQuery(raw);
        var result = filterData(raw, parsed);

        if(result === null){
            showToast('❌ Chưa có dữ liệu để tìm', true);
            return;
        }

        if(result.length === 0){
            var msgs;
            if(parsed){
                if(parsed.startStt === null){
                    msgs = '❌ Không có câu nào trong ' + parsed.hsk;
                } else if(parsed.startStt === parsed.endStt){
                    msgs = '❌ Không có câu số ' + parsed.startStt + ' trong ' + parsed.hsk;
                } else {
                    msgs = '❌ Không có câu ' + parsed.startStt + '→' + parsed.endStt + ' trong ' + parsed.hsk;
                }
            } else {
                msgs = '❌ Không tìm thấy: "' + raw + '"';
            }
            showToast(msgs, true);
            return;
        }

        var ok = applyResult(result, raw, parsed);
        if(!ok){
            showToast('⚠️ Không thể áp dụng kết quả', true);
            return;
        }

        // ⭐ Thông báo thành công
        var msg;
        if(parsed){
            if(parsed.startStt === null){
                msg = '✅ ' + parsed.hsk + ' · ' + result.length + ' câu';
            } else if(parsed.startStt === parsed.endStt){
                msg = '✅ ' + parsed.hsk + ' câu ' + parsed.startStt + ' · ' + result.length + ' kết quả';
            } else {
                msg = '✅ ' + parsed.hsk + ' ' + parsed.startStt + '→' + parsed.endStt + ' · ' + result.length + ' kết quả';
            }
        } else {
            msg = '🔍 Tìm thấy ' + result.length + ' câu';
        }
        showToast(msg);

        // ⭐ Đóng panel + scroll
        closePanel();
        setTimeout(function(){
            var mainEl = $id('mainContent');
            if(mainEl){
                var y = mainEl.getBoundingClientRect().top + window.scrollY - 100;
                window.scrollTo({ top:y, behavior:'smooth' });
            }
        }, 100);
    }

    /* ═══════════════════════════════════════════════════════
       7. MỞ / ĐÓNG PANEL
       ═══════════════════════════════════════════════════════ */
    function openPanel(){
        QS.open = true;
        var p = $id('quickSearchPanel');
        var t = $id('quickSearchToggle');
        if(p) p.classList.add('open');
        if(t) t.classList.add('active');
        setTimeout(function(){
            var i = $id('quickSearchInput');
            if(i) i.focus();
        }, 200);
    }
    function closePanel(){
        QS.open = false;
        var p = $id('quickSearchPanel');
        var t = $id('quickSearchToggle');
        if(p) p.classList.remove('open');
        if(t) t.classList.remove('active');
    }
    function clearPanel(){
        var p = $id('quickSearchPanel');
        var i = $id('quickSearchInput');
        if(p) p.classList.remove('has-value');
        if(i){ i.value = ''; i.focus(); }
    }

    /* ═══════════════════════════════════════════════════════
       8. BIND EVENTS
       ═══════════════════════════════════════════════════════ */
    function bind(){
        if(QS.inited) return;
        var toggle = $id('quickSearchToggle');
        var panel  = $id('quickSearchPanel');
        var input  = $id('quickSearchInput');
        var clearB = $id('quickSearchClear');
        var goB    = $id('quickSearchGo');
        if(!toggle || !panel || !input || !clearB || !goB) return;
        QS.inited = true;

        toggle.addEventListener('click', function(e){
            e.stopPropagation();
            if(QS.open) closePanel();
            else openPanel();
        });

        input.addEventListener('input', function(){
            var v = this.value.trim();
            panel.classList.toggle('has-value', !!v);
        });

        input.addEventListener('keydown', function(e){
            if(e.key === 'Enter'){
                e.preventDefault();
                doSearch();
            } else if(e.key === 'Escape'){
                e.preventDefault();
                if(this.value.trim()){
                    this.value = '';
                    panel.classList.remove('has-value');
                } else {
                    closePanel();
                }
            }
        });

        clearB.addEventListener('click', function(e){
            e.stopPropagation();
            clearPanel();
        });

        goB.addEventListener('click', function(e){
            e.stopPropagation();
            doSearch();
        });

        // Click ra ngoài → đóng nếu ô trống
        document.addEventListener('click', function(e){
            if(!QS.openPanel) return;
            if(e.target.closest('#quickSearchWrap')) return;
            var i = $id('quickSearchInput');
            if(i && i.value.trim()) return;  // đang có text → không tự đóng
            closePanel();
        });

        console.log('[quick-search] ✅ Đã bind events');
    }

    /* ═══════════════════════════════════════════════════════
       9. INIT (có retry)
       ═══════════════════════════════════════════════════════ */
    function init(){
        if(injectDOM()){
            bind();
        } else {
            // DOM chưa sẵn sàng → retry sau khi injectDOM thành công
            setTimeout(function(){
                if($id('quickSearchWrap')) bind();
            }, 600);
        }
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ⭐ Expose để debug
    window.__quickSearch = {
        open: open,
        close: closePanel,
        clear: clearPanel,
        do: doSearch,
        reinit: function(){ QS.inited = false; QS.retries = 0; init(); }
    };
})();
"""


# ═══════════════════════════════════════════════════════════════
#  INJECT VÀO index.html
# ═══════════════════════════════════════════════════════════════
def patch_quick_search(html_path="index.html"):
    """
    Inject CSS + JS quick search vào index.html.
    KHÔNG sửa bất kỳ file nào khác.

    Trả về True nếu inject thành công, False nếu bỏ qua (đã có sẵn).
    """
    if not os.path.isfile(html_path):
        print("[quick_search] ❌ Không tìm thấy: " + html_path)
        return False

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # ═══ Đã inject rồi? ═══
    if MARKER_JS in html:
        print("[quick_search] ℹ️  Đã có sẵn trong HTML — bỏ qua")
        return False

    css = build_quick_search_css()
    js  = build_quick_search_js()

    # ═══ Chèn CSS trước </style> đầu tiên (nếu có) ═══
    css_injected = False
    pat_style = re.compile(r'(\s*)(</style>)', re.MULTILINE)
    m = pat_style.search(html)
    if m:
        html = html[:m.start(2)] + "\n" + css + "\n" + html[m.start(2):]
        css_injected = True
        print("[quick_search] ✅ Đã chèn CSS (trước </style> đầu tiên)")
    else:
        # Fallback: chèn vào <head>
        pat_head = re.compile(r'(<head[^>]*>)', re.IGNORECASE)
        m2 = pat_head.search(html)
        if m2:
            block = "\n<style>\n" + css + "\n</style>\n"
            html = html[:m2.end()] + block + html[m2.end():]
            css_injected = True
            print("[quick_search] ✅ Đã chèn CSS (trong <head>)")
        else:
            print("[quick_search] ⚠️  Không tìm thấy </style> hoặc <head> → CSS bỏ qua")

    # ═══ Chèn JS trước </body> ═══
    js_block = "\n<script>\n" + js + "\n</script>\n"
    pat_body = re.compile(r'(\s*)(</body>)', re.MULTILINE)
    n = 0
    def _repl(m):
        nonlocal n
        n += 1
        return m.group(1) + js


_block + m.group(1) +# m.group(2)
    html = pat_body.sub(_repl, html, count=1)

    if n == 0:
        print("[quick_search] ❌ Không tìm thấy </body> → bỏ qua")
        return False
    print("[quick_search] ✅ Đã chèn JS (trước </body>)")

    # ═══ Ghi lại ═══
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(html_path) / 1024
    print("[quick_search] ✅ HOÀN TẤT — " + html_path +
          " (" + str(round(size_kb, 1)) + " KB)")
    return True ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    print("=" * 62)
    print("[quick_search] Patch: " + target)
    print("=" * 62)
    ok = patch_quick_search(target)
    sys.exit(0 if ok else 1)
