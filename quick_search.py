# -*- coding: utf-8 -*-
"""
quick_search.py - O TIM KIEM NHANH DOC LAP, DI THEO NUT CHAT

Module nay KHONG sua bat ky file nao khac.
Mount doc lap vao body, khong phu thuoc chatFloatWrap.
Tu dong phat hien full modal de loc dung ngu canh.

DAC DIEM:
  - O search nhanh rieng, KHONG dung #searchInput chinh
  - Vi tri: goc trai duoi, ngay tren nut chat
  - Enter / nut mui ten -> tim kiem
  - Esc / X -> reset
  - Tu dong loc bang cau chinh HOAC dropdown chon cau (full modal)
  - Tu dong expose window.applyFilter / window.pfApplyFilter / window.RAW_DATA
  - Toast thong bao ket qua
  - Dark mode + responsive mobile

CACH DUNG:
  from quick_search import patch_quick_search
  patch_quick_search("index.html")

HOAC chay truc tiep:
  python quick_search.py
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
    transition:bottom .35s cubic-bezier(.34,1.56,.64,1),
               opacity .25s ease,
               transform .25s ease;
}
#quickSearchRoot > *{ pointer-events:auto; }
#quickSearchRoot.hidden{
    opacity:0;
    transform:translateY(10px);
    pointer-events:none;
}

body.has-floating-group #quickSearchRoot{
    bottom:calc(260px + env(safe-area-inset-bottom));
}

/* Khi full modal mo -> an quick search (vi da co o search trong modal) */
body.practice-full-open #quickSearchRoot{
    opacity:0;
    pointer-events:none;
    transform:translateY(10px);
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
    display:flex;align-items:center;gap:.35rem;
    padding:0;border-radius:999px;
    background:#fff;
    border:2px solid #e2e8f0;
    box-shadow:0 8px 24px rgba(15,23,42,.25);
    overflow:hidden;
    max-width:0;opacity:0;transform:translateX(-8px);
    transition:max-width .35s cubic-bezier(.34,1.56,.64,1),
               opacity .25s ease,
               transform .3s ease,
               padding .25s ease;
    pointer-events:none;
    position:relative;
}
.quick-search-panel.open{
    max-width:calc(100vw - 90px);
    opacity:1;transform:translateX(0);
    padding:.25rem .3rem .25rem .75rem;
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
    min-width:180px;
}
[data-theme="dark"] .quick-search-panel input{color:#f1f5f9;}
.quick-search-panel input::placeholder{
    color:#94a3b8;font-size:.78rem;
}
.quick-search-clear,.quick-search-go{
    width:30px;height:30px;border-radius:50%;
    border:none;cursor:pointer;
    display:none;align-items:center;justify-content:center;
    font-size:.75rem;flex-shrink:0;
    transition:.15s;font-family:inherit;padding:0;
}
.quick-search-clear{
    background:#f1f5f9;color:#475569;
}
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
   .p return r"""
/* ===== QUICKf_SEARCH_MODULE_JS  =====Apply */
(function(){
    'use strict';

    varFilter QS = { open:false, in !==ited:false, retries:0, ' MOUNT_ID:'quickSearchRoot' };

    function $id(id){ return document.getElementById(id); }

    /* ═══════════════════════════════════════════════════════
       0. TU DONG EXPOSE CAC HAM PRIVATE RA WINDOW
       (applyFilter, pfApplyFilter, RAW_DATA)
       ═══════════════════════════════════════════════════════ */
    (function autoExpose(){
        var tries = 0;
        var timer = setInterval(function(){
            tries++;
            try{
                if(typeof window.applyFilter !== 'function' &&
                   typeof applyFilter === 'function'){
                    window.applyFilter = applyFilter;
                }
            }catch(e){}
            try{
                if(typeof windowfunction' &&
                   typeof pfApplyFilter === 'function'){
                    window.pfApplyFilter = pfApplyFilter;
                }
            }catch(e){}
            try{
                if(typeof window.RAW_DATA === 'undefined' &&
                   typeof RAW_DATA !== 'undefined'){
                    window.RAW_DATA = RAW_DATA;
                }
            }catch(e){}
            try{
                if(typeof window.pfBuildQuickNav !== 'function' &&
                   typeof pfBuildQuickNav === 'function'){
                    window.pfBuildQuickNav = pfBuildQuickNav;
                }
            }catch(e){}
            if(tries > 40) clearInterval(timer);
        }, 250);
    })();

    /* ═══════════════════════════════════════════════════════
       1. MOUNT DOM
       ═══════════════════════════════════════════════════════ */
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
        console.log('[quick-search] Mount vao body thanh cong');
        return true;
    }

    /* ═══════════════════════════════════════════════════════
       2. PARSE cu phap
       ═══════════════════════════════════════════════════════ */
    function parseQuery(raw){
        if(typeof window.parseSearchQuery === 'function'){
            try{
                var r = window.parseSearchQuery(raw);
                if(r) return r;
            }catch(e){}
        }
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
       3. LAY DU LIEU GOC
       ═══════════════════════════════════════════════════════ */
    function getBaseData(){
        try{
            if(typeof window.RAW_DATA !== 'undefined' && Array.isArray(window.RAW_DATA)){
                return window.RAW_DATA;
            }
            if(window.FIXPY_DATASETS){
                var curDs = (typeof window.CURRENT_DATASET !== 'undefined')
                            ? window.CURRENT_DATASET : 'tonghop';
                if(window.FIXPY_DATASETS[curDs]){
                    return window.FIXPY_DATASETS[curDs].data || [];
                }
            }
        }catch(e){}
        return [];
    }

    /* ═══════════════════════════════════════════════════════
       4. LOC DU LIEU
       ═══════════════════════════════════════════════════════ */
    function filterData(raw, parsed){
        var baseData = getBaseData();
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
       5. KIEM TRA DANG O FULL MODAL
       ═══════════════════════════════════════════════════════ */
    function isFullModalOpen(){
        var pfModal = $id('practiceFullModal');
        return pfModal && pfModal.classList.contains('show');
    }

    /* ═══════════════════════════════════════════════════════
       6. AP DUNG KET QUA (trang chinh HOAC full modal)
       ═══════════════════════════════════════════════════════ */
    function applyResult(result, raw, parsed){
        if(!result || result.length === 0) return false;

        var inFullModal = isFullModalOpen();

        if(inFullModal){
            /* ─── Truong hop 1: Dang o full modal ─── */
            var pfInput = $id('pfSearchInput');
            if(pfInput){
                pfInput.value = raw;
            }

            /* Dong bo ra search chinh de khi dong modal van giu */
            var siMain = $id('searchInput');
            if(siMain) siMain.value = raw;

            var pfCalled = false;
            try{
                if(typeof window.pfApplyFilter === 'function'){
                    window.pfApplyFilter();
                    pfCalled = true;
                }
            }catch(e){
                console.warn('[quick-search] pfApplyFilter error:', e);
            }

            /* Fallback: dispatch input event tren pfSearchInput */
            if(!pfCalled && pfInput){
                try{
                    pfInput.dispatchEvent(new Event('input', { bubbles: true }));
                }catch(e){
                    var ev1 = document.createEvent('Event');
                    ev1.initEvent('input', true, true);
                    pfInput.dispatchEvent(ev1);
                }
            }

            /* Hien nut clear cua pfSearchInput */
            try{
                var pfClear = $id('pfClearSearchBtn');
                if(pfClear) pfClear.classList.add('show');
            }catch(e){}

            return true;
        }

        /* ─── Truong hop 2: Trang chinh ─── */
        var si = $id('searchInput');
        if(!si) return false;

        si.value = raw;

        var filterCalled = false;
        try{
            if(typeof window.applyFilter === 'function'){
                window.applyFilter();
                filterCalled = true;
            }
        }catch(e){}

        if(!filterCalled){
            try{
                si.dispatchEvent(new Event('input', { bubbles: true }));
            }catch(e){
                var ev2 = document.createEvent('Event');
                ev2.initEvent('input', true, true);
                si.dispatchEvent(ev2);
            }
        }

        try{
            var cb = $id('clearSearchBtn');
            if(cb) cb.classList.add('show');
        }catch(e){}

        return true;
    }

    /* ═══════════════════════════════════════════════════════
       7. TOAST
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
       8. HANH DONG TIM KIEM
       ═══════════════════════════════════════════════════════ */
    function doSearch(){
        var input = $id('quickSearchInput');
        if(!input) return;
        var raw = input.value.trim();
        if(!raw){ showToast('Nhap gi do de tim...', true); input.focus(); return; }

        var parsed = parseQuery(raw);
        var result = filterData(raw, parsed);
        if(result === null){ showToast('Chua co du lieu de tim', true); return; }
        if(result.length === 0){
            var msgs;
            if(parsed){
                if(parsed.startStt === null) msgs = 'Khong co cau nao trong ' + parsed.hsk;
                else if(parsed.startStt === parsed.endStt) msgs = 'Khong co cau ' + parsed.startStt + ' trong ' + parsed.hsk;
                else msgs = 'Khong co cau ' + parsed.startStt + '-' + parsed.endStt + ' trong ' + parsed.hsk;
            } else msgs = 'Khong tim thay: ' + raw;
            showToast(msgs, true);
            return;
        }

        var ok = applyResult(result, raw, parsed);
        if(!ok){ showToast('Khong the ap dung ket qua', true); return; }

        var msg;
        if(parsed){
            if(parsed.startStt === null) msg = parsed.hsk + ' - ' + result.length + ' cau';
            else if(parsed.startStt === parsed.endStt) msg = parsed.hsk + ' ' + parsed.startStt + ' - ' + result.length + ' ket qua';
            else msg = parsed.hsk + ' ' + parsed.startStt + '-' + parsed.endStt + ' - ' + result.length + ' ket qua';
        } else msg = 'Tim thay ' + result.length + ' cau';
        showToast(msg);

        closePanel();

        /* Chi scroll khi o trang chinh (khong phai full modal) */
        if(!isFullModalOpen()){
            setTimeout(function(){
                var mainEl = $id('mainContent');
                if(mainEl){
                    var y = mainEl.getBoundingClientRect().top + window.scrollY - 100;
                    window.scrollTo({ top:y, behavior:'smooth' });
                }
            }, 100);
        }
    }

    /* ═══════════════════════════════════════════════════════
       9. MO / DONG PANEL
       ═══════════════════════════════════════════════════════ */
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

    /* ═══════════════════════════════════════════════════════
       10. BIND EVENTS
       ═══════════════════════════════════════════════════════ */
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

        /* Nut toggle: mo/dong panel */
        toggle.addEventListener('click', function(e){
            e.stopPropagation();
            e.preventDefault();
            if(QS.open) closePanel(); else openPanel();
        });

        /* Input: hien nut clear/go khi co chu */
        input.addEventListener('input', function(){
            panel.classList.toggle('has-value', !!this.value.trim());
        });

        /* ENTER = TIM, ESC = XOA/DONG */
        input.addEventListener('keydown', function(e){
            if(e.key === 'Enter' || e.keyCode === 13){
                e.preventDefault();
                e.stopPropagation();
                doSearch();
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

        /* Nut X: xoa input */
        clearB.addEventListener('click', function(e){
            e.stopPropagation();
            e.preventDefault();
            clearPanel();
        });

        /* Nut mui ten: TIM (giong Enter) */
        goB.addEventListener('click', function(e){
            e.stopPropagation();
            e.preventDefault();
            doSearch();
        });

        /* Click ra ngoai: dong panel neu input trong */
        document.addEventListener('click', function(e){
            if(!QS.open) return;
            if(e.target.closest('#' + QS.MOUNT_ID)) return;
            var i = $id('quickSearchInput');
            if(i && i.value.trim()) return;
            closePanel();
        });

        /* ESC cap document */
        document.addEventListener('keydown', function(e){
            if(!QS.open) return;
            if(e.key === 'Escape' || e.keyCode === 27){
                closePanel();
            }
        });

        console.log('[quick-search] Da bind events');
    }

    /* ═══════════════════════════════════════════════════════
       11. INIT
       ═══════════════════════════════════════════════════════ */
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

    /* Expose de debug */
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
    n = 0
    def _repl(m):
        nonlocal n
        n += 1
        return m.group(1) + js_block + m.group(1) + m.group(2)
    html = pat_body.sub(_repl, html, count=1)

    if n == 0:
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
