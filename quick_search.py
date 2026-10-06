# -*- coding: utf-8 -*-
"""
quick_search.py - O TIM KIEM NHANH - CHAP BUT 100% O TIM KIEM TINH

- Chi ghi gia tri vao #searchInput va dispatch event "input"
- O search tinh tu chay applyFilter() -> render -> hien ket qua
- Khong tu loc, khong tu render, khong doc FIXPY_DATASETS
- Giong het o search tinh: cung cu phap, cung ket qua, cung style
"""

import os
import re
import sys


MARKER_CSS = "/* ===== QUICK_SEARCH_MODULE_CSS ===== */"
MARKER_JS  = "/* ===== QUICK_SEARCH_MODULE_JS  ===== */"


def build_quick_search_css():
    return r"""
/* ===== QUICK_SEARCH_MODULE_CSS ===== */
#quickSearchRoot{
    position:fixed;
    left:20px;
    bottom:calc(90px + env(safe-area-inset-bottom));
    z-index:9997;
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    gap:.5rem;
    pointer-events:none;
    transition:bottom .35s cubic-bezier(.34,1.56,.64,1);
}
#quickSearchRoot > *{ pointer-events:auto; }
#quickSearchRoot.hidden{ opacity:0; pointer-events:none; }
body.has-floating-group #quickSearchRoot{
    bottom:calc(260px + env(safe-area-inset-bottom));
}
.quick-search-toggle{
    width:44px;height:44px;border-radius:50%;
    border:2px solid #fff;
    background:linear-gradient(135deg,#0891b2,#0e7490,#155e75);
    color:#fff;cursor:pointer;
    display:flex;align-items:center;justify-content:center;
    font-size:1.05rem;
    box-shadow:0 8px 24px rgba(14,116,144,.55);
    transition:all .3s cubic-bezier(.34,1.56,.64,1);
    flex-shrink:0;
    font-family:inherit;padding:0;
}
.quick-search-toggle:hover{
    transform:scale(1.08);
    box-shadow:0 12px 32px rgba(14,116,144,.75);
}
.quick-search-toggle.active{
    background:linear-gradient(135deg,#dc2626,#991b1b);
    box-shadow:0 8px 24px rgba(220,38,38,.65);
}
.quick-search-toggle i{transition:transform .3s;}
.quick-search-toggle.active i{transform:rotate(90deg);}

.quick-search-panel{
    display:flex;
    align-items:center;
    gap:.35rem;
    padding:0;
    border-radius:999px;
    background:#fff;
    border:2px solid #e2e8f0;
    box-shadow:0 8px 24px rgba(15,23,42,.25);
    overflow:hidden;
    max-width:0;
    opacity:0;
    transform:translateX(-8px);
    transition:max-width .35s cubic-bezier(.34,1.56,.64,1),
               opacity .25s ease,
               transform .3s ease,
               padding .25s ease;
    pointer-events:none;
    position:relative;
}
.quick-search-panel.open{
    max-width:calc(100vw - 90px);
    opacity:1;
    transform:translateX(0);
    padding:.3rem .35rem .3rem .6rem;
    pointer-events:auto;
}
[data-theme="dark"] .quick-search-panel{
    background:#1e293b;border-color:#334155;
}
.quick-search-panel input{
    flex:1;min-width:0;border:none;outline:none;
    background:transparent;color:#0f172a;
    font-size:.85rem;font-family:inherit;
    padding:.4rem 0;
    min-width:150px;
    height:30px;
    line-height:30px;
}
[data-theme="dark"] .quick-search-panel input{color:#f1f5f9;}
.quick-search-panel input::placeholder{
    color:#94a3b8;font-size:.78rem;
}

.quick-search-clear,.quick-search-go{
    width:30px;
    height:30px;
    min-width:30px;
    min-height:30px;
    border-radius:50%;
    border:none;
    cursor:pointer;
    display:none;
    align-items:center;
    justify-content:center;
    flex-shrink:0;
    transition:.15s;
    font-family:inherit;
    padding:0;
    margin:0;
    line-height:1;
    box-sizing:border-box;
}
.quick-search-clear i,
.quick-search-go i{
    display:flex;
    align-items:center;
    justify-content:center;
    line-height:1;
    margin:0;
    padding:0;
    pointer-events:none;
    font-size:.75rem;
}
.quick-search-clear{ background:#f1f5f9;color:#475569; }
.quick-search-clear:hover{background:#fee2e2;color:#dc2626;}
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

@media (max-width:768px){
    #quickSearchRoot{left:12px;bottom:calc(80px + env(safe-area-inset-bottom));}
    body.has-floating-group #quickSearchRoot{
        bottom:calc(240px + env(safe-area-inset-bottom));
    }
    .quick-search-toggle{width:42px;height:42px;font-size:1rem;}
}
@media (max-width:400px){
    #quickSearchRoot{left:10px;}
    .quick-search-toggle{width:40px;height:40px;}
}
"""


def build_quick_search_js():
    return r"""
/* ===== QUICK_SEARCH_MODULE_JS  ===== */
(function(){
    'use strict';

    var QS = { open:false, inited:false, retries:0, MOUNT_ID:'quickSearchRoot' };

    function $id(id){ return document.getElementById(id); }

    function buildDOM(){
        var root = document.createElement('div');
        root.id = QS.MOUNT_ID;
        root.innerHTML =
            '<div class="quick-search-panel" id="quickSearchPanel">' +
                '<input type="text" id="quickSearchInput" ' +
                    'placeholder="hsk1 5 - hsk2 10 20" ' +
                    'autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">' +
                '<button class="quick-search-clear" id="quickSearchClear" type="button" title="Xoa">' +
                    '<i class="fas fa-times"></i>' +
                '</button>' +
                '<button class="quick-search-go" id="quickSearchGo" type="button" title="Tim">' +
                    '<i class="fas fa-arrow-right"></i>' +
                '</button>' +
            '</div>' +
            '<button class="quick-search-toggle" id="quickSearchToggle" type="button" title="Tim kiem nhanh">' +
                '<i class="fas fa-search"></i>' +
            '</button>';
        return root;
    }

    function mount(){
        if($id(QS.MOUNT_ID)) return true;
        if(!document.body){
            QS.retries++;
            if(QS.retries > 60) return false;
            setTimeout(mount, 300);
            return false;
        }
        var root = buildDOM();
        document.body.appendChild(root);
        console.log('[quick-search] Mount OK');
        return true;
    }

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

    function doSearch(){
        var input = $id('quickSearchInput');
        if(!input) return;
        var raw = input.value.trim();
        if(!raw){ showToast('Nhap gi do de tim...', true); input.focus(); return; }

        // ⭐ Kiem tra dang o Practice Full khong
        var pfModal = $id('practiceFullModal');
        var isPFOpen = pfModal && pfModal.classList.contains('show');

        if(isPFOpen){
            // ⭐ DANG O FULL -> ghi vao pfSearchInput
            var pfsi = $id('pfSearchInput');
            if(!pfsi){
                showToast('Khong co o search Full', true);
                return;
            }
            pfsi.value = raw;
            try{
                pfsi.dispatchEvent(new Event('input', { bubbles: true }));
            }catch(e){
                var ev2 = document.createEvent('Event');
                ev2.initEvent('input', true, true);
                pfsi.dispatchEvent(ev2);
            }
            var pfcb = $id('pfClearSearchBtn');
            if(pfcb) pfcb.classList.add('show');
        } else {
            // ⭐ O TRANG CHU -> ghi vao searchInput (nhu cu)
            var si = $id('searchInput');
            if(!si){
                showToast('Khong co o search chinh', true);
                return;
            }
            si.value = raw;
            try{
                si.dispatchEvent(new Event('input', { bubbles: true }));
            }catch(e){
                var ev = document.createEvent('Event');
                ev.initEvent('input', true, true);
                si.dispatchEvent(ev);
            }
            var cb = $id('clearSearchBtn');
            if(cb) cb.classList.add('show');
        }

        // ⭐ Dong panel
        closePanel();

        setTimeout(function(){
            var mainEl = $id('mainContent');
            if(mainEl){
                var y = mainEl.getBoundingClientRect().top + window.scrollY - 100;
                window.scrollTo({ top:y, behavior:'smooth' });
            }
        }, 100);

        showToast('Da tim: ' + raw);
    }
    function openPanel(){
        QS.open = true;
        var p = $id('quickSearchPanel');
        var t = $id('quickSearchToggle');
        if(p) p.classList.add('open');
        if(t) t.classList.add('active');
        setTimeout(function(){ var i = $id('quickSearchInput'); if(i) i.focus(); }, 200);
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

    function bind(){
        if(QS.inited) return;
        var toggle = $id('quickSearchToggle');
        var panel  = $id('quickSearchPanel');
        var input  = $id('quickSearchInput');
        var clearB = $id('quickSearchClear');
        var goB    = $id('quickSearchGo');
        if(!toggle || !panel || !input || !clearB || !goB){
            setTimeout(bind, 300);
            return;
        }
        QS.inited = true;

        // ⭐ Nut mui ten = TIM
        goB.addEventListener('click', function(e){
            if(e){ e.stopPropagation(); e.preventDefault(); }
            doSearch();
        });

        // ⭐ Nut X = XOA input
        clearB.addEventListener('click', function(e){
            if(e){ e.stopPropagation(); e.preventDefault(); }
            clearPanel();
        });

        // ⭐ Nut toggle = MO/DONG panel
        toggle.addEventListener('click', function(e){
            if(e){ e.stopPropagation(); e.preventDefault(); }
            if(QS.open) closePanel(); else openPanel();
        });

        // ⭐ Input events
        input.addEventListener('input', function(){
            panel.classList.toggle('has-value', !!this.value.trim());
        });

        // ⭐ ENTER = click nut mui ten, ESC = xoa/dong
        input.addEventListener('keydown', function(e){
            if(e.key === 'Enter' || e.keyCode === 13){
                e.preventDefault();
                e.stopPropagation();
                var g = $id('quickSearchGo');
                if(g){ g.click(); } else { doSearch(); }
                return false;
            }
            if(e.key === 'Escape' || e.keyCode === 27){
                e.preventDefault();
                if(this.value.trim()){
                    this.value = '';
                    panel.classList.remove('has-value');
                } else {
                    closePanel();
                }
                return false;
            }
        });

        // ⭐ Click ra ngoai = dong panel
        document.addEventListener('click', function(e){
            if(!QS.open) return;
            if(e.target.closest('#' + QS.MOUNT_ID)) return;
            var i = $id('quickSearchInput');
            if(i && i.value.trim()) return;
            closePanel();
        });

        console.log('[quick-search] Bind OK');
    }

    function init(){
        if(mount()){
            bind();
        } else {
            setTimeout(function(){
                if($id(QS.MOUNT_ID)) bind();
            }, 600);
        }
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.__quickSearch = {
        open: openPanel,
        close: closePanel,
        clear: clearPanel,
        do: doSearch,
        mount: mount,
        reinit: function(){ QS.inited = false; QS.retries = 0; init(); }
    };
})();
"""


def patch_quick_search(html_path="index.html"):
    if not os.path.isfile(html_path):
        print("[quick_search] Khong tim thay: " + html_path)
        return False

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    if MARKER_JS in html:
        print("[quick_search] Da co san trong HTML - bo qua")
        return False

    css = build_quick_search_css()
    js  = build_quick_search_js()

    pat_style = re.compile(r'(\s*)(</style>)', re.MULTILINE)
    m = pat_style.search(html)
    if m:
        html = html[:m.start(2)] + "\n" + css + "\n" + html[m.start(2):]
        print("[quick_search] Da chen CSS")
    else:
        pat_head = re.compile(r'(<head[^>]*>)', re.IGNORECASE)
        m2 = pat_head.search(html)
        if m2:
            html = html[:m2.end()] + "\n<style>\n" + css + "\n</style>\n" + html[m2.end():]
            print("[quick_search] Da chen CSS vao head")

    js_block = "\n<script>\n" + js + "\n</script>\n"
    pat_body = re.compile(r'(\s*)(</body>)', re.MULTILINE)
    n = [0]
    def _repl(m):
        n[0] += 1
        return m.group(1) + js_block + m.group(1) + m.group(2)
    html = pat_body.sub(_repl, html, count=1)

    if n[0] == 0:
        print("[quick_search] Khong tim thay body - bo qua")
        return False

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(html_path) / 1024
    print("[quick_search] HOAN TAT - " + html_path + " (" + str(round(size_kb, 1)) + " KB)")
    return True


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    print("=" * 60)
    print("[quick_search] Patch: " + target)
    print("=" * 60)
    ok = patch_quick_search(target)
    sys.exit(0 if ok else 1)
