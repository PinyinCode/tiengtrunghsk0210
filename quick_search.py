# -*- coding: utf-8 -*-
"""
quick_search.py - O TIM KIEM NHANH CO CHON PHAM VI

- Scope = "current": chi tim trong tab hien tai
- Scope = "all": tim trong TAT CA tab (FIXPY_DATASETS + DATASET_REGISTRY)
- Enter = click nut mui ten
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
    padding:.3rem .35rem .3rem .55rem;
    pointer-events:auto;
}
[data-theme="dark"] .quick-search-panel{
    background:#1e293b;border-color:#334155;
}

.quick-search-scope{
    border:none;outline:none;
    background:transparent;color:#475569;
    font-size:.72rem;font-weight:700;
    font-family:inherit;
    padding:.3rem .2rem;
    cursor:pointer;
    border-right:1px solid #e2e8f0;
    padding-right:.5rem;
    margin-right:.15rem;
    max-width:95px;
    height:30px;
    line-height:1;
}
.quick-search-scope:focus{outline:none;}
[data-theme="dark"] .quick-search-scope{color:#cbd5e1;border-right-color:#334155;}
.quick-search-scope option{background:#fff;color:#0f172a;}
[data-theme="dark"] .quick-search-scope option{background:#1e293b;color:#f1f5f9;}

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

.quick-search-result-header{
    grid-column:1 / -1;
    padding:.7rem 1rem;
    background:linear-gradient(135deg,#0891b2,#0e7490);
    color:#fff;
    border-radius:12px;
    font-size:.85rem;
    font-weight:700;
    display:flex;
    align-items:center;
    gap:.5rem;
    margin-bottom:.5rem;
    flex-wrap:wrap;
}
.quick-search-result-header i{font-size:1rem;}
.quick-search-result-header .qs-dataset-info{
    font-size:.7rem;
    font-weight:500;
    opacity:.85;
    margin-left:.3rem;
}
.quick-search-clear-result{
    margin-left:auto;
    padding:.3rem .7rem;
    border-radius:50px;
    border:none;
    background:rgba(255,255,255,.25);
    color:#fff;
    font-size:.72rem;
    font-weight:700;
    cursor:pointer;
    font-family:inherit;
    display:inline-flex;
    align-items:center;
    gap:.3rem;
}
.quick-search-clear-result:hover{background:rgba(255,255,255,.4);}

.quick-search-dataset-tag{
    position:absolute;
    top:4px;
    right:8px;
    padding:1px 6px;
    background:rgba(8,145,178,.12);
    color:#0891b2;
    border-radius:50px;
    font-size:.6rem;
    font-weight:700;
    z-index:5;
}
[data-theme="dark"] .quick-search-dataset-tag{
    background:rgba(8,145,178,.25);
    color:#67e8f9;
}

@media (max-width:768px){
    #quickSearchRoot{left:12px;bottom:calc(80px + env(safe-area-inset-bottom));}
    body.has-floating-group #quickSearchRoot{
        bottom:calc(240px + env(safe-area-inset-bottom));
    }
    .quick-search-toggle{width:42px;height:42px;font-size:1rem;}
    .quick-search-scope{max-width:80px;font-size:.68rem;}
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

    function escHtml(s){
        if(s == null) return '';
        return String(s)
            .replace(/&/g,'&amp;')
            .replace(/</g,'&lt;')
            .replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;')
            .replace(/'/g,'&#39;');
    }

    (function autoExpose(){
        var tries = 0;
        var timer = setInterval(function(){
            tries++;
            try{
                if(typeof window.RAW_DATA === 'undefined' &&
                   typeof RAW_DATA !== 'undefined' && Array.isArray(RAW_DATA)){
                    window.RAW_DATA = RAW_DATA;
                }
            }catch(e){}
            try{
                if(typeof window.CURRENT_DATASET === 'undefined' &&
                   typeof CURRENT_DATASET !== 'undefined'){
                    window.CURRENT_DATASET = CURRENT_DATASET;
                }
            }catch(e){}
            try{
                if(typeof window.parseSearchQuery !== 'function' &&
                   typeof parseSearchQuery === 'function'){
                    window.parseSearchQuery = parseSearchQuery;
                }
            }catch(e){}
            try{
                if(typeof window.DATASET_REGISTRY === 'undefined' &&
                   typeof DATASET_REGISTRY !== 'undefined' && DATASET_REGISTRY){
                    window.DATASET_REGISTRY = DATASET_REGISTRY;
                }
            }catch(e){}
            if(tries > 80) clearInterval(timer);
        }, 250);
    })();

    function buildDOM(){
        var root = document.createElement('div');
        root.id = QS.MOUNT_ID;
        root.innerHTML =
            '<div class="quick-search-panel" id="quickSearchPanel">' +
                '<select id="quickSearchScope" class="quick-search-scope" title="Pham vi tim kiem">' +
                    '<option value="current">Tab hien tai</option>' +
                    '<option value="all">Tat ca tab</option>' +
                '</select>' +
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

    function getBaseData(){
        var scopeEl = $id('quickSearchScope');
        var scope = scopeEl ? scopeEl.value : 'current';

        if(scope === 'all'){
            var all = [];
            try{
                if(window.FIXPY_DATASETS && typeof window.FIXPY_DATASETS === 'object'){
                    Object.keys(window.FIXPY_DATASETS).forEach(function(id){
                        var ds = window.FIXPY_DATASETS[id];
                        if(ds && Array.isArray(ds.data)){
                            ds.data.forEach(function(r){
                                var c = {};
                                for(var k in r) c[k] = r[k];
                                c._dataset = id;
                                c._datasetName = ds.name || id;
                                all.push(c);
                            });
                        }
                    });
                }
            }catch(e){
                console.warn('[quick-search] Loi FIXPY_DATASETS:', e);
            }
            try{
                if(window.DATASET_REGISTRY && typeof window.DATASET_REGISTRY === 'object'){
                    Object.keys(window.DATASET_REGISTRY).forEach(function(id){
                        if(window.FIXPY_DATASETS && window.FIXPY_DATASETS[id]) return;
                        var ds = window.DATASET_REGISTRY[id];
                        if(ds && Array.isArray(ds.data)){
                            ds.data.forEach(function(r){
                                var c = {};
                                for(var k in r) c[k] = r[k];
                                c._dataset = id;
                                c._datasetName = ds.name || id;
                                all.push(c);
                            });
                        }
                    });
                }
            }catch(e){}
            if(all.length > 0){
                console.log('[quick-search] Scope ALL: ' + all.length + ' cau');
                return all;
            }
        }

        try{
            if(typeof window.RAW_DATA !== 'undefined' && Array.isArray(window.RAW_DATA)){
                return window.RAW_DATA;
            }
            if(typeof RAW_DATA !== 'undefined' && Array.isArray(RAW_DATA)){
                return RAW_DATA;
            }
        }catch(e){}
        return [];
    }

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

    function bindResultEvents(wrapper, result){
        wrapper.querySelectorAll('.qs-card').forEach(function(card){
            var idx = parseInt(card.dataset.qsIdx, 10);
            var r = result[idx];
            if(!r) return;
            card.addEventListener('click', function(e){
                if(e.target.closest('.action-group')) return;
                if(typeof toggleFocus === 'function'){
                    toggleFocus(r.stt, card);
                }
            });
        });
        wrapper.querySelectorAll('.qs-audio-btn').forEach(function(btn){
            btn.addEventListener('click', function(e){
                e.stopPropagation();
                var card = btn.closest('.qs-card');
                if(!card) return;
                var r = result[parseInt(card.dataset.qsIdx, 10)];
                if(!r || !r.zh) return;
                if(typeof speakText === 'function') speakText(r.zh, btn, e);
            });
        });
        wrapper.querySelectorAll('.qs-write-btn').forEach(function(btn){
            btn.addEventListener('click', function(e){
                e.stopPropagation();
                var card = btn.closest('.qs-card');
                if(!card) return;
                var r = result[parseInt(card.dataset.qsIdx, 10)];
                if(!r || !r.zh) return;
                if(typeof openWriter === 'function') openWriter(r.zh, r.vi || '', r.pinyin || '', e);
            });
        });
        wrapper.querySelectorAll('.qs-full-btn').forEach(function(btn){
            btn.addEventListener('click', function(e){
                e.stopPropagation();
                var card = btn.closest('.qs-card');
                if(!card) return;
                var r = result[parseInt(card.dataset.qsIdx, 10)];
                if(!r) return;
                if(typeof openPracticeFull === 'function') openPracticeFull(r.stt, e);
            });
        });
    }

    function renderResults(result, raw, parsed){
        var wrapper = $id('mobileWrapper');
        if(!wrapper){
            console.warn('[quick-search] Khong co #mobileWrapper');
            return false;
        }

        var scopeEl = $id('quickSearchScope');
        var scope = scopeEl ? scopeEl.value : 'current';
        var scopeLabel = (scope === 'all') ? 'Tat ca tab' : 'Tab hien tai';

        var headerHtml = '<div class="quick-search-result-header">' +
            '<i class="fas fa-search"></i>' +
            '<span>Tim thay <b>' + result.length + '</b> ket qua</span>' +
            '<span class="qs-dataset-info">(' + scopeLabel + ')</span>' +
            '<button class="quick-search-clear-result" onclick="window.__quickSearch.clearResult()">' +
                '<i class="fas fa-times"></i> Xoa' +
            '</button>' +
        '</div>';

        var cardsHtml = '';
        var maxShow = Math.min(result.length, 300);
        for(var i = 0; i < maxShow; i++){
            var r = result[i];
            var idx = i;
            var zhHtml = escHtml(r.zh);
            var viHtml = escHtml(r.vi);
            var sttSafe = escHtml(r.stt);

            var topicTag = r.topic ? '<span class="card-tag topic">' + escHtml(r.topic) + '</span>' : '';
            var subjectTag = r.subject ? '<span class="card-tag subject">' + escHtml(r.subject) + '</span>' : '';

            var dsTag = '';
            if(scope === 'all' && r._datasetName){
                dsTag = '<span class="quick-search-dataset-tag">' + escHtml(r._datasetName) + '</span>';
            }

            var favBtn = '';
            if(typeof favBuildFavButton === 'function'){
                try{ favBtn = favBuildFavButton(r.stt); }catch(e){ favBtn = ''; }
            }

            cardsHtml += '<div class="card qs-card" data-qs-idx="' + idx + '" data-hsk="' + escHtml(r.hsk || '') + '" data-stt="' + sttSafe + '" style="position:relative">' +
                dsTag +
                '<div class="card-header">' +
                    '<div class="card-stt">' + sttSafe + '</div>' +
                    '<div class="card-meta">' +
                        (r.hsk ? '<span class="card-tag hsk">' + escHtml(r.hsk) + '</span>' : '') +
                        topicTag +
                        subjectTag +
                    '</div>' +
                    '<div class="action-group">' +
                        '<button class="audio-btn qs-audio-btn" title="Nghe"><i class="fas fa-volume-up"></i></button>' +
                        '<button class="write-btn qs-write-btn" title="Luyen viet"><i class="fas fa-pen-fancy"></i></button>' +
                        '<button class="practice-full-btn qs-full-btn" title="Luyen tap full"><i class="fas fa-expand"></i></button>' +
                        favBtn +
                    '</div>' +
                '</div>' +
                '<div class="card-body">' +
                    (r.vi ? '<div class="card-vi">' + viHtml + '</div>' : '') +
                    '<div class="card-zh">' + zhHtml + '</div>' +
                    (r.pinyin ? '<div class="card-pinyin">' + escHtml(r.pinyin) + '</div>' : '') +
                '</div>' +
            '</div>';
        }

        if(result.length > maxShow){
            cardsHtml += '<div class="end-note">' +
                '<i class="fas fa-info-circle"></i> Hien thi ' + maxShow + '/' + result.length + ' ket qua' +
            '</div>';
        }

        wrapper.innerHTML = headerHtml + cardsHtml;
        bindResultEvents(wrapper, result);

        var mainEl = $id('mainContent');
        if(mainEl){
            var y = mainEl.getBoundingClientRect().top + window.scrollY - 100;
            window.scrollTo({ top:y, behavior:'smooth' });
        }
        return true;
    }

    function clearResult(){
        var si = $id('searchInput');
        if(si) si.value = '';
        try{
            if(typeof window.state !== 'undefined' && window.state){
                window.state.search = '';
                window.state.hsk = '';
                window.state.subject = '';
            }
        }catch(e){}
        try{
            if(typeof window.applyFilter === 'function'){
                window.applyFilter();
                return;
            }
        }catch(e){}
        if(si){
            try{
                si.dispatchEvent(new Event('input', { bubbles: true }));
            }catch(e){
                var ev = document.createEvent('Event');
                ev.initEvent('input', true, true);
                si.dispatchEvent(ev);
            }
        }
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

        var parsed = parseQuery(raw);
        var result = filterData(raw, parsed);

        if(result === null){
            showToast('Chua co du lieu de tim', true);
            return;
        }

        if(result.length === 0){
            var msgs;
            if(parsed){
                if(parsed.startStt === null) msgs = 'Khong co cau nao trong ' + parsed.hsk;
                else if(parsed.startStt === parsed.endStt) msgs = 'Khong co cau ' + parsed.startStt + ' trong ' + parsed.hsk;
                else msgs = 'Khong co cau ' + parsed.startStt + '-' + parsed.endStt + ' trong ' + parsed.hsk;
            } else {
                msgs = 'Khong tim thay: ' + raw;
            }
            showToast(msgs, true);
            return;
        }

        var ok = renderResults(result, raw, parsed);
        if(!ok){
            showToast('Khong render duoc ket qua', true);
            return;
        }

        var si = $id('searchInput');
        if(si){
            si.value = raw;
            try{
                var cb = $id('clearSearchBtn');
                if(cb) cb.classList.add('show');
            }catch(e){}
        }

        var scopeEl = $id('quickSearchScope');
        var scope = scopeEl ? scopeEl.value : 'current';
        var scopeSuffix = (scope === 'all') ? ' (tat ca tab)' : '';

        var msg;
        if(parsed){
            if(parsed.startStt === null) msg = parsed.hsk + ' - ' + result.length + ' cau' + scopeSuffix;
            else if(parsed.startStt === parsed.endStt) msg = parsed.hsk + ' ' + parsed.startStt + ' - ' + result.length + ' ket qua' + scopeSuffix;
            else msg = parsed.hsk + ' ' + parsed.startStt + '-' + parsed.endStt + ' - ' + result.length + ' ket qua' + scopeSuffix;
        } else {
            msg = 'Tim thay ' + result.length + ' cau' + scopeSuffix;
        }
        showToast(msg);

        closePanel();
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
        var scopeEl = $id('quickSearchScope');
        if(!toggle || !panel || !input || !clearB || !goB){
            setTimeout(bind, 300);
            return;
        }
        QS.inited = true;

        goB.addEventListener('click', function(e){
            if(e){ e.stopPropagation(); e.preventDefault(); }
            doSearch();
        });
        clearB.addEventListener('click', function(e){
            if(e){ e.stopPropagation(); e.preventDefault(); }
            clearPanel();
        });
        toggle.addEventListener('click', function(e){
            if(e){ e.stopPropagation(); e.preventDefault(); }
            if(QS.open) closePanel(); else openPanel();
        });

        if(scopeEl){
            try{
                var saved = localStorage.getItem('quickSearchScope');
                if(saved === 'all' || saved === 'current'){
                    scopeEl.value = saved;
                }
            }catch(e){}
            scopeEl.addEventListener('change', function(){
                try{ localStorage.setItem('quickSearchScope', this.value); }catch(e){}
                console.log('[quick-search] Doi scope:', this.value);
            });
        }

        input.addEventListener('input', function(){
            panel.classList.toggle('has-value', !!this.value.trim());
        });

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
        clearResult: clearResult,
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
