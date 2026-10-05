# -*- coding: utf-8 -*-
"""
quick_search.py - O TIM KIEM NHANH DOC LAP, DI THEO NUT CHAT

Module nay KHONG sua bat ky file nao khac.
Chi inject them CSS + HTML + JS vao index.html sau khi
tat ca module khac da build xong (fix.py, chat_support.py, ...).

DAC DIEM:
  - O search nhanh rieng, KHONG dung #searchInput chinh
  - Vi tri: nam TRONG #chatFloatWrap (tren nut chat)
    -> tu dong di chuyen theo nut chat
  - Collapse thanh icon kinh lup khi khong dung
  - Ho tro cu phap: hsk1, hsk1 5, hsk1 5 10, hsk7-9
  - Enter / nut -> filter bang cau (tam thoi, ghi de search chinh)
  - Esc / X -> reset
  - Toast thong bao ket qua
  - Dark mode + responsive mobile
  - Tu dong retry neu #chatFloatWrap chua ton tai

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


def build_quick_search_js():
    return r"""
/* ===== QUICK_SEARCH_MODULE_JS  ===== */
(function(){
    'use strict';

    var QS = { open:false, inited:false, retries:0 };

    function $id(id){ return document.getElementById(id); }

    function injectDOM(){
        if($id('quickSearchWrap')) return true;

        var wrap = $id('chatFloatWrap');
        if(!wrap){
            QS.retries++;
            if(QS.retries > 60){
                console.warn('[quick-search] chatFloatWrap khong xuat hien sau 60 lan thu');
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
                    'placeholder="hsk1 5 - hsk2 10 20" ' +
                    'autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">' +
                '<button class="quick-search-clear" id="quickSearchClear" type="button" title="Xoa">' +
                    '<i class="fas fa-times"></i>' +
                '</button>' +
                '<button class="quick-search-go" id="quickSearchGo" type="button" title="Tim">' +
                    '<i class="fas fa-arrow-right"></i>' +
                '</button>' +
            '</div>' +
            '<div class="quick-search-hint">' +
                'Cu phap: <kbd>hsk1</kbd> - <kbd>hsk1 5</kbd> - <kbd>hsk1 5 10</kbd> - <kbd>hsk7-9</kbd>' +
            '</div>' +
            '<button class="quick-search-toggle" id="quickSearchToggle" type="button" title="Tim kiem nhanh">' +
                '<i class="fas fa-search"></i>' +
            '</button>';

        wrap.insertBefore(div, wrap.firstChild);
        console.log('[quick-search] Da chen vao chatFloatWrap');
        return true;
    }

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

    function filterData(raw, parsed){
        var baseData = [];
        try{
            if(typeof window.RAW_DATA !== 'undefined' && Array.isArray(window.RAW_DATA)){
                baseData = window.RAW_DATA;
            }
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

    function applyResult(result, raw, parsed){
        if(!result || result.length === 0) return false;

        var si = $id('searchInput');
        if(!si){
            if(typeof window.__applyQuickSearchResult === 'function'){
                try{
                    window.__applyQuickSearchResult(result);
                    return true;
                }catch(e){}
            }
            return false;
        }

        si.value = raw;

        try{
            si.dispatchEvent(new Event('input', { bubbles: true }));
        }catch(e){
            var ev = document.createEvent('Event');
            ev.initEvent('input', true, true);
            si.dispatchEvent(ev);
        }

        return true;
    }

    function showToast(msg, isError){
        var old = $id('quickSearchToast');
        if(old) old.remove();

        var t = document.createElement('div');
        t.id = 'quickSearchToast';
        t.className = 'quick-search-toast' + (isError.classList ? ' error' : '');
        t.textContent =.remove msg;
        document.body.appendChild(t);

('        requestAnimationFrame(function(){ t.classList.add('show'); });

show        setTimeout(function(){
            t');
            setTimeout(function(){ if(t.parentNode) t.remove(); }, 300);
        }, 2400);
    }

    function doSearch(){
        var input = $id('quickSearchInput');
        if(!input) return;
        var raw = input.value.trim();
        if(!raw){
            showToast('Nhap gi do de tim...', true);
            input.focus();
            return;
        }

        var parsed = parseQuery(raw);
        var result = filterData(raw, parsed);

        if(result === null){
            showToast('Chua co du lieu de tim', true);
            return;
        }

        if(result.length === 0){
            var msgs;
            if(parsed){
                if(parsed.startStt === null){
                    msgs = 'Khong co cau nao trong ' + parsed.hsk;
                } else if(parsed.startStt === parsed.endStt){
                    msgs = 'Khong co cau so ' + parsed.startStt + ' trong ' + parsed.hsk;
                } else {
                    msgs = 'Khong co cau ' + parsed.startStt + '-' + parsed.endStt + ' trong ' + parsed.hsk;
                }
            } else {
                msgs = 'Khong tim thay: ' + raw;
            }
            showToast(msgs, true);
            return;
        }

        var ok = applyResult(result, raw, parsed);
        if(!ok){
            showToast('Khong the ap dung ket qua', true);
            return;
        }

        var msg;
        if(parsed){
            if(parsed.startStt === null){
                msg = parsed.hsk + ' - ' + result.length + ' cau';
            } else if(parsed.startStt === parsed.endStt){
                msg = parsed.hsk + ' cau ' + parsed.startStt + ' - ' + result.length + ' ket qua';
            } else {
                msg = parsed.hsk + ' ' + parsed.startStt + '-' + parsed.endStt + ' - ' + result.length + ' ket qua';
            }
        } else {
            msg = 'Tim thay ' + result.length + ' cau';
        }
        showToast(msg);

        closePanel();
        setTimeout(function(){
            var mainEl = $id('mainContent');
            if(mainEl){
                var y = mainEl.getBoundingClientRect().top + window.scrollY - 100;
                window.scrollTo({ top:y, behavior:'smooth' });
            }
        }, 100);
    }

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

        document.addEventListener('click', function(e){
            if(!QS.open) return;
            if(e.target.closest('#quickSearchWrap')) return;
            var i = $id('quickSearchInput');
            if(i && i.value.trim()) return;
            closePanel();
        });

        console.log('[quick-search] Da bind events');
    }

    function init(){
        if(injectDOM()){
            bind();
        } else {
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

    window.__quickSearch = {
        open: openPanel,
        close: closePanel,
        clear: clearPanel,
        do: doSearch,
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
        print("[quick_search] Da chen CSS truoc /style dau tien")
    else:
        pat_head = re.compile(r'(<head[^>]*>)', re.IGNORECASE)
        m2 = pat_head.search(html)
        if m2:
            block = "\n<style>\n" + css + "\n</style>\n"
            html = html[:m2.end()] + block + html[m2.end():]
            print("[quick_search] Da chen CSS trong head")
        else:
            print("[quick_search] Khong tim thay style hoac head - CSS bo qua")

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
    print("[quick_search] Da chen JS truoc /body")

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
