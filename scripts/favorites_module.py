 # -*- coding: utf-8 -*-
"""
Module FAVORITES — Tính năng Yêu thích câu.

Quy tắc tier:
  - ACTIVE / ADMIN  → dùng đầy đủ (lưu Firebase cloud + cache localStorage)
  - TRIAL / DEMO / EXPIRED → chỉ hiển thị icon khoá 🔒 + tab mờ 🔒
                              bấm vào mở dialog mời đăng nhập / gia hạn

Tính năng chính:
  1. Nút tim trên card câu — đổi màu theo trạng thái yêu thích
  2. Nút tim FLOAT trong Practice Full (góc phải)
  3. Nút toggle "Chỉ câu yêu thích" trong Practice Full (góc trái)
     ★ Khi bật → dropdown "CÂU:" chỉ liệt kê câu yêu thích
  4. Tab Yêu thích + Item Yêu thích trong dropdown bộ dữ liệu
  5. Đồng bộ Firebase real-time + cache localStorage

Tích hợp:
  from favorites_module import build_favorites_css, build_favorites_html, build_favorites_js
"""


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
def build_favorites_css():
    return r"""
/* ═══════════════════════════════════════════════════════════════
   ❤️ FAVORITES — Nút tim trên card
   ═══════════════════════════════════════════════════════════════ */
.fav-btn{
    width:clamp(28px,2.8vw,32px);
    height:clamp(28px,2.8vw,32px);
    border-radius:50%;
    border:none;
    background:var(--surface-2);
    color:var(--text-3);
    cursor:pointer;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    font-size:clamp(.72rem,.9vw,.85rem);
    transition:all .2s cubic-bezier(.34,1.56,.64,1);
    flex-shrink:0;
    position:relative;
}
.fav-btn:hover{
    transform:scale(1.15);
    background:rgba(239,68,68,.12);
    color:#ef4444;
}
.fav-btn:active{transform:scale(.92);}
.fav-btn.active{color:#ef4444;background:rgba(239,68,68,.12);}
.fav-btn.active i{animation:favHeartPop .4s cubic-bezier(.34,1.56,.64,1);}
@keyframes favHeartPop{
    0%{transform:scale(1);}
    40%{transform:scale(1.4);}
    70%{transform:scale(.9);}
    100%{transform:scale(1);}
}
.fav-btn.active::after{
    content:'';position:absolute;inset:-4px;border-radius:50%;
    border:2px solid rgba(239,68,68,.4);
    animation:favRing .5s ease-out;pointer-events:none;
}
@keyframes favRing{
    0%{opacity:1;transform:scale(.8);}
    100%{opacity:0;transform:scale(1.4);}
}
.fav-btn.locked{color:#dc2626;background:rgba(220,38,38,.1);}
.fav-btn.locked:hover{
    transform:scale(1.12);background:rgba(220,38,38,.2);color:#b91c1c;
}
.fav-btn.locked i{font-size:.65rem;}
[data-theme="dark"] .fav-btn.locked{color:#fca5a5;background:rgba(220,38,38,.25);}
[data-theme="dark"] .fav-btn.locked:hover{background:rgba(220,38,38,.4);color:#fecaca;}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Nút tim FLOAT (Practice Full) — góc phải
   ═══════════════════════════════════════════════════════════════ */
.pf-fav-float{
    position:fixed;
    right:clamp(14px,2vw,22px);
    bottom:calc(80px + env(safe-area-inset-bottom));
    display:none;align-items:center;gap:.5rem;
    padding:.65rem 1.1rem .65rem .9rem;
    border-radius:999px;
    border:2px solid rgba(239,68,68,.4);
    background:linear-gradient(135deg,#fef2f2,#fee2e2);
    color:#dc2626;
    font-size:clamp(.85rem,1vw,.95rem);font-weight:800;font-family:inherit;
    cursor:pointer;z-index:2450;
    transition:all .25s cubic-bezier(.34,1.56,.64,1);
    box-shadow:0 8px 24px rgba(239,68,68,.35),0 2px 8px rgba(0,0,0,.1);
    text-transform:uppercase;letter-spacing:.3px;
}
.pf-fav-float.show{display:inline-flex}
.pf-fav-float i{
    font-size:clamp(1.15rem,1.4vw,1.35rem);
    transition:transform .3s cubic-bezier(.34,1.56,.64,1);
}
.pf-fav-float:hover{
    transform:translateY(-3px) scale(1.05);
    border-color:#ef4444;
    box-shadow:0 12px 32px rgba(239,68,68,.5),0 4px 12px rgba(0,0,0,.15);
}
.pf-fav-float:hover i{transform:scale(1.15);}
.pf-fav-float:active{transform:translateY(-1px) scale(1.02);}
.pf-fav-float:not(.active):not(.locked){
    background:linear-gradient(135deg,#fef2f2,#fee2e2);
    color:#dc2626;border-color:rgba(239,68,68,.4);
}
.pf-fav-float.active{
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;border-color:#dc2626;
    box-shadow:0 8px 28px rgba(239,68,68,.6),0 2px 8px rgba(220,38,38,.3);
    animation:pfFavPulse 2s ease-in-out infinite;
}
.pf-fav-float.active i{animation:favHeartPop .5s cubic-bezier(.34,1.56,.64,1);}
.pf-fav-float.active::after{
    content:'';position:absolute;inset:-4px;border-radius:999px;
    border:2px solid rgba(239,68,68,.5);
    animation:favRing 1s ease-out infinite;pointer-events:none;
}
@keyframes pfFavPulse{
    0%,100%{box-shadow:0 8px 28px rgba(239,68,68,.6),0 2px 8px rgba(220,38,38,.3);}
    50%{box-shadow:0 8px 36px rgba(239,68,68,.85),0 4px 12px rgba(220,38,38,.4);}
}
.pf-fav-float.locked{
    background:linear-gradient(135deg,#fef3c7,#fde68a);
    color:#b45309;border-color:rgba(217,119,6,.5);animation:none;
}
.pf-fav-float.locked:hover{
    background:linear-gradient(135deg,#fde68a,#fcd34d);
    color:#92400e;border-color:#d97706;
    transform:translateY(-3px) scale(1.05);
}
.pf-fav-float.locked::after{display:none;}
.pf-fav-float .pf-fav-float-label{display:inline-block;white-space:nowrap;}
[data-theme="dark"] .pf-fav-float{
    background:linear-gradient(135deg,rgba(239,68,68,.2),rgba(220,38,38,.15));
    border-color:rgba(239,68,68,.5);color:#fca5a5;
}
[data-theme="dark"] .pf-fav-float.active{
    background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;
}
[data-theme="dark"] .pf-fav-float.locked{
    background:linear-gradient(135deg,rgba(217,119,6,.25),rgba(180,83,9,.2));
    color:#fcd34d;border-color:rgba(217,119,6,.5);
}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Nút toggle "Chỉ câu yêu thích" (Practice Full) — góc trái
   ═══════════════════════════════════════════════════════════════ */
.pf-fav-only-float{
    position:fixed;
    left:clamp(14px,2vw,22px);
    bottom:calc(80px + env(safe-area-inset-bottom));
    display:none;align-items:center;gap:.5rem;
    padding:.65rem 1.1rem .65rem .9rem;
    border-radius:999px;
    border:2px solid var(--border);
    background:var(--surface);
    color:var(--text-2);
    font-size:clamp(.82rem,.95vw,.92rem);font-weight:800;font-family:inherit;
    cursor:pointer;z-index:2450;
    transition:all .25s cubic-bezier(.34,1.56,.64,1);
    box-shadow:0 4px 14px rgba(0,0,0,.12);
    text-transform:uppercase;letter-spacing:.3px;user-select:none;
}
.pf-fav-only-float.show{display:inline-flex;}
.pf-fav-only-float i{
    font-size:clamp(1rem,1.2vw,1.15rem);
    transition:transform .3s cubic-bezier(.34,1.56,.64,1);
}
.pf-fav-only-float:hover{
    transform:translateY(-3px) scale(1.04);
    border-color:#ef4444;color:#dc2626;
    box-shadow:0 8px 22px rgba(239,68,68,.3);
}
.pf-fav-only-float:active{transform:translateY(-1px) scale(1.01);}
.pf-fav-only-float .pf-fav-only-count{
    min-width:20px;height:20px;padding:0 .4rem;border-radius:50px;
    background:rgba(239,68,68,.15);color:#dc2626;
    font-size:.68rem;font-weight:900;
    display:inline-flex;align-items:center;justify-content:center;
    line-height:1;transition:.2s;
}
.pf-fav-only-float.active{
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;border-color:#dc2626;
    box-shadow:0 8px 24px rgba(239,68,68,.5);
}
.pf-fav-only-float.active i{animation:favHeartPop .4s cubic-bezier(.34,1.56,.64,1);}
.pf-fav-only-float.active .pf-fav-only-count{
    background:rgba(255,255,255,.3);color:#fff;
}
.pf-fav-only-float.locked{
    background:linear-gradient(135deg,#fef3c7,#fde68a);
    color:#b45309;border-color:rgba(217,119,6,.5);
}
.pf-fav-only-float.locked:hover{
    background:linear-gradient(135deg,#fde68a,#fcd34d);
    color:#92400e;border-color:#d97706;
    transform:translateY(-3px) scale(1.04);
}
.pf-fav-only-float.locked .pf-fav-only-count{
    background:rgba(217,119,6,.2);color:#92400e;
}
.pf-fav-only-float.empty{opacity:.55;}
.pf-fav-only-float.empty .pf-fav-only-count{display:none;}
[data-theme="dark"] .pf-fav-only-float{
    background:var(--surface-2);border-color:var(--border);color:var(--text-2);
}
[data-theme="dark"] .pf-fav-only-float.active{
    background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;border-color:#dc2626;
}
[data-theme="dark"] .pf-fav-only-float.locked{
    background:linear-gradient(135deg,rgba(217,119,6,.25),rgba(180,83,9,.2));
    color:#fcd34d;border-color:rgba(217,119,6,.5);
}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Responsive
   ═══════════════════════════════════════════════════════════════ */
@media (max-width:500px){
    .pf-fav-float{
        padding:.55rem .9rem .55rem .75rem;font-size:.78rem;
        bottom:calc(78px + env(safe-area-inset-bottom));
    }
    .pf-fav-float i{font-size:1.05rem;}
    .pf-fav-float .pf-fav-float-label{display:none;}

    .pf-fav-only-float{
        padding:.55rem .9rem .55rem .75rem;font-size:.78rem;
        bottom:calc(78px + env(safe-area-inset-bottom));
    }
    .pf-fav-only-float i{font-size:1rem;}
    .pf-fav-only-float .pf-fav-only-label{display:none;}
}
@media (max-width:400px){
    .pf-fav-float{padding:.5rem;min-width:46px;justify-content:center;}
    .pf-fav-only-float{padding:.5rem;min-width:46px;justify-content:center;}
}
@media (max-height:550px) and (orientation:landscape){
    .pf-fav-float{
        bottom:calc(64px + env(safe-area-inset-bottom));
        transform:scale(.9);transform-origin:right bottom;
    }
    .pf-fav-only-float{
        bottom:calc(64px + env(safe-area-inset-bottom));
        transform:scale(.9);transform-origin:left bottom;
    }
}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Tab trong dataset selector
   ═══════════════════════════════════════════════════════════════ */
.ds-btn[data-dataset-group="favorites"]{position:relative;overflow:visible;}
.ds-btn[data-dataset-group="favorites"] .ds-fav-badge{
    position:absolute;top:-8px;right:-6px;
    min-width:22px;height:22px;padding:0 .4rem;border-radius:50px;
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;font-size:.65rem;font-weight:900;
    display:flex;align-items:center;justify-content:center;
    box-shadow:0 2px 8px rgba(239,68,68,.5),0 0 0 2px var(--surface);
    animation:favBadgePulse 2s ease-in-out infinite;
    z-index:10;line-height:1;
}
.ds-btn[data-dataset-group="favorites"] .ds-fav-badge[data-count="0"]{display:none;}
@keyframes favBadgePulse{
    0%,100%{transform:scale(1);}
    50%{transform:scale(1.1);}
}
.ds-btn[data-dataset-group="favorites"] .ds-fav-lock{
    position:absolute;top:-8px;right:-6px;width:22px;height:22px;border-radius:50%;
    background:linear-gradient(135deg,#dc2626,#b91c1c);
    color:#fff;display:flex;align-items:center;justify-content:center;
    font-size:.62rem;
    box-shadow:0 2px 8px rgba(220,38,38,.55),0 0 0 2px var(--surface);
    z-index:10;
}
.ds-btn[data-dataset-group="favorites"] i:first-child{color:#ef4444;}
.ds-btn[data-dataset-group="favorites"].active i:first-child{color:#fff;}
.ds-btn[data-dataset-group="favorites"].fav-locked{opacity:.65;cursor:pointer;}
.ds-btn[data-dataset-group="favorites"].fav-locked:hover{
    opacity:.85;border-color:#dc2626;background:rgba(220,38,38,.06);
}
.ds-btn[data-dataset-group="favorites"].fav-locked i:first-child{color:#dc2626;}
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"].fav-locked i:first-child{color:#fca5a5;}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Dropdown item (bộ dữ liệu)
   ═══════════════════════════════════════════════════════════════ */
.ds-dropdown-item[data-dataset-group="favorites"]{position:relative;}
.ds-dropdown-item[data-dataset-group="favorites"] .ds-dd-fav-icon{color:#ef4444;}
.ds-dropdown-item[data-dataset-group="favorites"].active .ds-dd-fav-icon{color:#fff;}
.ds-dropdown-item[data-dataset-group="favorites"] .ds-dd-fav-badge{
    margin-left:auto;min-width:20px;height:20px;padding:0 .42rem;border-radius:50px;
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;font-size:.62rem;font-weight:900;
    display:inline-flex;align-items:center;justify-content:center;
    box-shadow:0 2px 6px rgba(239,68,68,.45);line-height:1;
}
.ds-dropdown-item[data-dataset-group="favorites"] .ds-dd-fav-badge[data-count="0"]{display:none;}
.ds-dropdown-item[data-dataset-group="favorites"] .ds-dd-fav-lock{
    margin-left:auto;color:#dc2626;font-size:.7rem;
}
.ds-dropdown-item[data-dataset-group="favorites"].fav-locked{opacity:.7;}
.ds-dropdown-item[data-dataset-group="favorites"].fav-locked .ds-dd-fav-icon{color:#dc2626;}
[data-theme="dark"] .ds-dropdown-item[data-dataset-group="favorites"].fav-locked .ds-dd-fav-icon{
    color:#fca5a5;
}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Empty states
   ═══════════════════════════════════════════════════════════════ */
.fav-empty{
    grid-column:1 / -1;padding:3rem 1.5rem;text-align:center;
    background:linear-gradient(135deg,rgba(239,68,68,.04),rgba(220,38,38,.02));
    border:2px dashed rgba(239,68,68,.25);border-radius:16px;
}
[data-theme="dark"] .fav-empty{
    background:linear-gradient(135deg,rgba(239,68,68,.1),rgba(220,38,38,.05));
    border-color:rgba(239,68,68,.35);
}
.fav-empty .fav-empty-icon{
    width:70px;height:70px;margin:0 auto 1rem;border-radius:50%;
    background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(220,38,38,.1));
    color:#ef4444;display:flex;align-items:center;justify-content:center;
    font-size:1.8rem;animation:favEmptyFloat 3s ease-in-out infinite;
}
@keyframes favEmptyFloat{
    0%,100%{transform:translateY(0) scale(1);}
    50%{transform:translateY(-6px) scale(1.05);}
}
.fav-empty .fav-empty-title{
    font-size:1.05rem;font-weight:800;color:var(--text);margin-bottom:.4rem;
}
.fav-empty .fav-empty-desc{
    font-size:.85rem;color:var(--text-2);line-height:1.5;
    max-width:420px;margin:0 auto;
}
.fav-empty .fav-empty-desc b{color:#dc2626;font-weight:800;}
.fav-locked-empty{
    grid-column:1 / -1;padding:3rem 1.5rem;text-align:center;
    background:linear-gradient(135deg,rgba(220,38,38,.06),rgba(185,28,28,.03));
    border:2px dashed rgba(220,38,38,.35);border-radius:16px;
}
.fav-locked-empty .fav-empty-cta{
    display:inline-flex;align-items:center;gap:.4rem;margin-top:1rem;
    padding:.6rem 1.2rem;border-radius:50px;border:none;
    background:linear-gradient(135deg,#dc2626,#b91c1c);
    color:#fff;font-size:.85rem;font-weight:800;font-family:inherit;
    cursor:pointer;box-shadow:0 6px 18px rgba(220,38,38,.4);
    transition:all .2s;text-transform:uppercase;letter-spacing:.3px;
}
.fav-locked-empty .fav-empty-cta:hover{
    transform:translateY(-2px) scale(1.03);
    box-shadow:0 10px 26px rgba(220,38,38,.6);
}

/* ═══════════════════════════════════════════════════════════════
   ❤️ Toast
   ═══════════════════════════════════════════════════════════════ */
.fav-toast{
    position:fixed;top:80px;left:50%;
    transform:translateX(-50%) translateY(-20px);
    padding:.7rem 1.2rem;border-radius:50px;
    font-size:.85rem;font-weight:800;font-family:inherit;color:#fff;
    z-index:9999;opacity:0;
    transition:opacity .25s ease, transform .3s cubic-bezier(.34,1.56,.64,1);
    pointer-events:none;display:flex;align-items:center;gap:.5rem;
    max-width:90vw;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    box-shadow:0 8px 24px rgba(0,0,0,.25);
}
.fav-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}
.fav-toast.add{background:linear-gradient(135deg,#ef4444,#dc2626);}
.fav-toast.remove{background:linear-gradient(135deg,#64748b,#475569);}
.fav-toast.warn{background:linear-gradient(135deg,#f59e0b,#d97706);}
.fav-toast i{font-size:1rem;}

/* ═══════════════════════════════════════════════════════════════
   ★ FIX 2026-09: KHÔNG ZOOM TO TRÊN MÀN RỘNG
   Khoá kích thước 2 nút float (tim + chỉ câu yêu thích) nhỏ vừa vặn
   ═══════════════════════════════════════════════════════════════ */

/* Khoá kích thước tối đa cho cả 2 nút */
.pf-fav-float,
.pf-fav-only-float {
    max-width: 180px;
    max-height: 44px;
    padding: .55rem .95rem .55rem .8rem;
    font-size: .82rem;
    box-sizing: border-box;
}
.pf-fav-float i,
.pf-fav-only-float i {
    font-size: 1.05rem;
}

/* Màn hình siêu rộng (>= 1600px): giữ nguyên kích thước nhỏ */
@media (min-width: 1600px) {
    .pf-fav-float,
    .pf-fav-only-float {
        max-width: 170px;
        max-height: 42px;
        font-size: .8rem;
        padding: .5rem .85rem .5rem .75rem;
    }
    .pf-fav-float i,
    .pf-fav-only-float i {
        font-size: 1rem;
    }
}

/* Landscape (màn thấp ngang): thu nhỏ nhẹ, KHÔNG phóng to */
@media (max-height: 550px) and (orientation: landscape) {
    .pf-fav-float {
        transform: scale(.9) !important;
        transform-origin: right bottom;
    }
    .pf-fav-only-float {
        transform: scale(.9) !important;
        transform-origin: right bottom;
    }
}
/* ═══════════════════════════════════════════════════════════════
   ★ NÚT TOGGLE "CHỈ CÂU YÊU THÍCH" — TRẠNG THÁI CÂU KHÔNG PHẢI YÊU THÍCH
   Khi câu hiện tại CHƯA like → nút mờ, không kích hoạt được
   ═══════════════════════════════════════════════════════════════ */
.pf-fav-only-float.current-not-fav {
    opacity: 0.5 !important;
    filter: grayscale(0.6);
    cursor: not-allowed;
    pointer-events: auto; /* Vẫn cho phép bấm để hiện cảnh báo */
}

.pf-fav-only-float.current-not-fav:hover {
    transform: none !important;
    border-color: var(--border) !important;
    color: var(--text-2) !important;
    box-shadow: 0 4px 14px rgba(0,0,0,.12) !important;
    opacity: 0.6 !important;
}

.pf-fav-only-float.current-not-fav i {
    animation: none !important;
}

.pf-fav-only-float.current-not-fav .pf-fav-only-count {
    background: rgba(148, 163, 184, 0.2);
    color: var(--text-3);
}

/* Dark mode */
[data-theme="dark"] .pf-fav-only-float.current-not-fav {
    background: var(--surface-2);
    border-color: var(--border);
    color: var(--text-3);
}

[data-theme="dark"] .pf-fav-only-float.current-not-fav:hover {
    background: var(--surface-2) !important;
    border-color: var(--border) !important;
}



/* ═══════════════════════════════════════════════════════════════
   🎯 FAVORITES FILTER — Nút "Lọc"
   ═══════════════════════════════════════════════════════════════ */
.pf-fav-filter-btn{
    display:none;
    align-items:center;
    gap:.35rem;
    padding:.28rem .7rem;
    border-radius:999px;
    border:1.5px solid rgba(239,68,68,.35);
    background:linear-gradient(135deg,#fef2f2,#fee2e2);
    color:#dc2626;
    font-size:clamp(.66rem,.78vw,.74rem);
    font-weight:800;
    font-family:inherit;
    cursor:pointer;
    transition:all .2s cubic-bezier(.34,1.56,.64,1);
    white-space:nowrap;
    flex-shrink:0;
    position:relative;
    margin-left:.35rem;
}
.pf-fav-filter-btn.show{display:inline-flex;}
.pf-fav-filter-btn:hover{
    transform:translateY(-1px);
    border-color:#ef4444;
    box-shadow:0 4px 12px rgba(239,68,68,.3);
}
.pf-fav-filter-btn.active{
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;
    border-color:#dc2626;
}
.pf-fav-filter-btn i:first-child{font-size:.85rem;}
.pf-fav-filter-btn .pf-fav-filter-badge{
    min-width:17px;height:17px;padding:0 .35rem;
    border-radius:50px;
    background:rgba(255,255,255,.3);
    color:#fff;
    font-size:.6rem;
    font-weight:900;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    line-height:1;
}
.pf-fav-filter-btn:not(.active) .pf-fav-filter-badge{
    background:rgba(239,68,68,.15);
    color:#dc2626;
}
[data-theme="dark"] .pf-fav-filter-btn{
    background:linear-gradient(135deg,rgba(239,68,68,.2),rgba(220,38,38,.15));
    border-color:rgba(239,68,68,.5);
    color:#fca5a5;
}
[data-theme="dark"] .pf-fav-filter-btn.active{
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;
}

/* ═══════════════════════════════════════════════════════════════
   🎯 FAVORITES FILTER — Summary bar
   ═══════════════════════════════════════════════════════════════ */
.pf-fav-filter-summary{
    display:none;
    align-items:center;
    gap:.3rem;
    padding:.4rem .85rem .45rem;
    background:linear-gradient(135deg,rgba(239,68,68,.06),rgba(220,38,38,.04));
    border-bottom:1.5px dashed rgba(239,68,68,.25);
    flex-wrap:wrap;
    animation:favSummaryIn .25s ease-out;
}
.pf-fav-filter-summary.show{display:flex;}
@keyframes favSummaryIn{
    from{opacity:0;transform:translateY(-4px);}
    to{opacity:1;transform:translateY(0);}
}
.pf-fav-summary-count{
    display:inline-flex;align-items:center;gap:.3rem;
    padding:.22rem .6rem;
    border-radius:50px;
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;font-size:.68rem;font-weight:800;
    white-space:nowrap;flex-shrink:0;
}
.pf-fav-summary-count b{font-size:1.05em;}
.pf-fav-summary-chip{
    display:inline-flex;align-items:center;gap:.25rem;
    padding:.2rem .5rem .2rem .6rem;
    border-radius:50px;
    background:var(--surface);
    border:1.5px solid rgba(239,68,68,.3);
    color:#dc2626;font-size:.66rem;font-weight:700;
    white-space:nowrap;
    animation:favChipIn .2s ease-out;
}
@keyframes favChipIn{
    from{opacity:0;transform:scale(.85);}
    to{opacity:1;transform:scale(1);}
}
.pf-fav-summary-chip i.fa-times{
    cursor:pointer;font-size:.58rem;padding:1px;
    border-radius:50%;transition:.15s;opacity:.7;
}
.pf-fav-summary-chip i.fa-times:hover{
    opacity:1;background:rgba(220,38,38,.15);transform:scale(1.15);
}
.pf-fav-summary-chip.dataset{
    background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(139,92,246,.08));
    border-color:rgba(139,92,246,.35);color:#6d28d9;
}
.pf-fav-summary-chip.hsk{
    background:linear-gradient(135deg,rgba(59,130,246,.1),rgba(37,99,235,.08));
    border-color:rgba(59,130,246,.35);color:#1d4ed8;
}
.pf-fav-summary-chip.subject{
    background:linear-gradient(135deg,rgba(245,158,11,.1),rgba(217,119,6,.08));
    border-color:rgba(245,158,11,.4);color:#92400e;
}
.pf-fav-summary-clear{
    margin-left:auto;
    padding:.2rem .6rem;
    border-radius:50px;
    border:1.5px solid rgba(220,38,38,.3);
    background:var(--surface);
    color:#dc2626;font-size:.62rem;font-weight:700;
    cursor:pointer;font-family:inherit;
    display:inline-flex;align-items:center;gap:.22rem;
    transition:.15s;
}
.pf-fav-summary-clear:hover{
    background:linear-gradient(135deg,#dc2626,#b91c1c);
    color:#fff;border-color:#dc2626;
}
[data-theme="dark"] .pf-fav-summary-chip{background:var(--surface-2);}

/* ═══════════════════════════════════════════════════════════════
   🎯 FAVORITES FILTER — MODAL
   ═══════════════════════════════════════════════════════════════ */
.fav-filter-modal{
    position:fixed;inset:0;
    background:rgba(15,23,42,.75);
    backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
    z-index:2600;display:none;
    align-items:center;justify-content:center;
    padding:1rem;animation:favModalIn .2s ease-out;
}
.fav-filter-modal.show{display:flex;}
@keyframes favModalIn{from{opacity:0;}to{opacity:1;}}

.fav-filter-box{
    background:var(--surface);border-radius:20px;
    width:100%;max-width:560px;
    max-height:min(85vh,640px);
    display:flex;flex-direction:column;overflow:hidden;
    box-shadow:0 24px 70px rgba(0,0,0,.4),0 0 0 1px rgba(239,68,68,.15);
    animation:favBoxIn .35s cubic-bezier(.34,1.56,.64,1);
}
@keyframes favBoxIn{
    from{transform:translateY(30px) scale(.95);opacity:0;}
    to{transform:translateY(0) scale(1);opacity:1;}
}
.fav-filter-header{
    padding:1.1rem 1.35rem 1rem;
    background:linear-gradient(135deg,rgba(239,68,68,.12),rgba(220,38,38,.08));
    border-bottom:1px solid var(--border);
    display:flex;align-items:center;gap:.65rem;flex-shrink:0;
}
.fav-filter-header-icon{
    width:42px;height:42px;border-radius:12px;
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;display:flex;align-items:center;justify-content:center;
    font-size:1.15rem;flex-shrink:0;
    box-shadow:0 6px 18px rgba(239,68,68,.4);
}
.fav-filter-header-text{flex:1;min-width:0;}
.fav-filter-header-title{
    font-size:1.05rem;font-weight:900;color:var(--text);
    line-height:1.2;margin-bottom:.15rem;
}
.fav-filter-header-sub{
    font-size:.72rem;color:var(--text-3);font-weight:600;
}
.fav-filter-close{
    width:32px;height:32px;border-radius:50%;border:none;
    background:var(--surface-2);color:var(--text-2);
    cursor:pointer;display:flex;align-items:center;justify-content:center;
    flex-shrink:0;transition:.15s;font-family:inherit;
}
.fav-filter-close:hover{
    background:var(--danger-light);color:var(--danger);transform:scale(1.08);
}
.fav-filter-body{
    padding:1.15rem 1.35rem;overflow-y:auto;
    flex:1 1 auto;min-height:0;
    -webkit-overflow-scrolling:touch;scrollbar-width:thin;
}
.fav-filter-body::-webkit-scrollbar{width:6px;}
.fav-filter-body::-webkit-scrollbar-thumb{
    background:var(--border-strong);border-radius:3px;
}
.fav-filter-section{margin-bottom:1.25rem;}
.fav-filter-section:last-child{margin-bottom:0;}
.fav-filter-section-header{
    display:flex;align-items:center;gap:.5rem;
    margin-bottom:.6rem;padding-bottom:.45rem;
    border-bottom:1px dashed var(--border);
}
.fav-filter-section-icon{
    width:24px;height:24px;border-radius:7px;
    display:flex;align-items:center;justify-content:center;
    font-size:.72rem;flex-shrink:0;color:#fff;
}
.fav-filter-section-icon.dataset{background:linear-gradient(135deg,#6366f1,#8b5cf6);}
.fav-filter-section-icon.hsk{background:linear-gradient(135deg,#3b82f6,#2563eb);}
.fav-filter-section-icon.subject{background:linear-gradient(135deg,#f59e0b,#d97706);}
.fav-filter-section-title{
    font-size:.82rem;font-weight:800;color:var(--text);
    flex:1;text-transform:uppercase;letter-spacing:.3px;
}
.fav-filter-section-actions{display:flex;gap:.25rem;}
.fav-filter-section-actions button{
    padding:.2rem .5rem;border-radius:50px;
    border:1px solid var(--border);background:var(--surface);
    color:var(--text-2);font-size:.6rem;font-weight:700;
    cursor:pointer;font-family:inherit;transition:.15s;
}
.fav-filter-section-actions button:hover{
    border-color:#ef4444;color:#dc2626;background:rgba(239,68,68,.06);
}
.fav-filter-options{
    display:flex;flex-wrap:wrap;gap:.35rem;
}
.fav-filter-option{
    display:inline-flex;align-items:center;gap:.32rem;
    padding:.35rem .7rem .37rem;
    border-radius:50px;border:1.5px solid var(--border);
    background:var(--surface);color:var(--text);
    font-size:.72rem;font-weight:700;font-family:inherit;
    cursor:pointer;transition:all .18s ease;
    user-select:none;line-height:1.35;
}
.fav-filter-option:hover{
    border-color:rgba(239,68,68,.5);
    background:rgba(239,68,68,.06);
    transform:translateY(-1px);
}
.fav-filter-option.selected{
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;border-color:#dc2626;
    box-shadow:0 3px 10px rgba(239,68,68,.35);
}
.fav-filter-option.selected::before{
    content:'\2713';
    display:inline-flex;align-items:center;justify-content:center;
    width:14px;height:14px;border-radius:50%;
    background:rgba(255,255,255,.3);
    font-size:.58rem;font-weight:900;flex-shrink:0;
}
.fav-filter-option .fav-opt-count{
    font-size:.6rem;font-weight:700;
    padding:.05rem .35rem;border-radius:50px;
    background:var(--surface-2);color:var(--text-3);line-height:1.4;
}
.fav-filter-option.selected .fav-opt-count{
    background:rgba(255,255,255,.25);color:#fff;
}
.fav-filter-empty{
    padding:1.25rem;text-align:center;
    color:var(--text-3);font-size:.8rem;
}
.fav-filter-footer{
    padding:1rem 1.35rem 1.1rem;
    border-top:1px solid var(--border);
    background:var(--surface);
    display:flex;align-items:center;gap:.55rem;flex-shrink:0;
    box-shadow:0 -4px 12px -8px rgba(15,23,42,.15);
}
[data-theme="dark"] .fav-filter-footer{
    box-shadow:0 -4px 12px -8px rgba(0,0,0,.4);
}
.fav-filter-result{
    flex:1;font-size:.78rem;color:var(--text-2);font-weight:600;
}
.fav-filter-result b{color:#dc2626;font-weight:900;font-size:1.1em;}
.fav-filter-btn-secondary{
    padding:.55rem 1rem;border-radius:12px;
    border:1.5px solid var(--border);background:var(--surface);
    color:var(--text-2);font-size:.78rem;font-weight:700;
    font-family:inherit;cursor:pointer;
    display:inline-flex;align-items:center;gap:.32rem;
    transition:.15s;
}
.fav-filter-btn-secondary:hover{
    background:var(--surface-2);color:var(--danger);
    border-color:rgba(220,38,38,.4);
}
.fav-filter-btn-primary{
    padding:.6rem 1.2rem;border-radius:12px;border:none;
    background:linear-gradient(135deg,#ef4444,#dc2626);
    color:#fff;font-size:.82rem;font-weight:800;
    font-family:inherit;cursor:pointer;
    display:inline-flex;align-items:center;gap:.38rem;
    transition:.2s;box-shadow:0 6px 18px rgba(239,68,68,.4);
}
.fav-filter-btn-primary:hover:not(:disabled){
    transform:translateY(-2px);
    box-shadow:0 10px 26px rgba(239,68,68,.6);
}
.fav-filter-btn-primary:disabled{
    opacity:.5;cursor:not-allowed;transform:none;
    background:linear-gradient(135deg,#94a3b8,#64748b);
    box-shadow:none;
}

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════════════════ */
@media (max-width:500px){
    .pf-fav-filter-btn{font-size:.64rem;padding:.25rem .55rem;}
    .pf-fav-filter-btn i:first-child{font-size:.75rem;}
    .pf-fav-filter-summary{padding:.35rem .6rem .4rem;gap:.25rem;}
    .pf-fav-summary-count{font-size:.62rem;padding:.18rem .48rem;}
    .pf-fav-summary-chip{font-size:.6rem;padding:.15rem .4rem .15rem .5rem;}
    .fav-filter-modal{padding:.5rem;align-items:flex-end;}
    .fav-filter-box{
        max-width:100%;max-height:90vh;
        border-radius:20px 20px 16px 16px;
    }
    .fav-filter-header{padding:.9rem 1rem .8rem;gap:.5rem;}
    .fav-filter-header-icon{width:36px;height:36px;font-size:1rem;}
    .fav-filter-header-title{font-size:.92rem;}
    .fav-filter-header-sub{font-size:.65rem;}
    .fav-filter-body{padding:.9rem 1rem;}
    .fav-filter-section{margin-bottom:1rem;}
    .fav-filter-section-title{font-size:.72rem;}
    .fav-filter-option{font-size:.68rem;padding:.3rem .55rem .32rem;}
    .fav-filter-option .fav-opt-count{font-size:.56rem;}
    .fav-filter-footer{padding:.85rem 1rem .95rem;gap:.4rem;}
    .fav-filter-result{font-size:.7rem;}
    .fav-filter-btn-secondary{padding:.5rem .8rem;font-size:.72rem;}
    .fav-filter-btn-primary{padding:.55rem .95rem;font-size:.75rem;}
}
@media (max-width:380px){
    .fav-filter-section-actions button{font-size:.56rem;padding:.16rem .4rem;}
    .fav-filter-option{font-size:.64rem;padding:.26rem .48rem .28rem;}
}

/* ═══════════════════════════════════════════════════════════════
   Ẩn filter UI khi không ở trong modal Practice Full
   ═══════════════════════════════════════════════════════════════ */
body:not(.practice-full-open) .pf-fav-filter-btn,
body:not(.practice-full-open) .pf-fav-filter-summary{
    display:none !important;
}


/* ═══════════════════════════════════════════════════════════════
   🎯 SUMMARY BAR — 1 DÒNG, CHIP "+N ..." KHI VƯỢT QUÁ
   ═══════════════════════════════════════════════════════════════ */

/* Buộc summary bar chỉ 1 dòng — không wrap */
.pf-fav-filter-summary {
    flex-wrap: nowrap !important;
    overflow: hidden;
    align-items: center;
}

/* Các chip có thể co lại nhưng không xuống dòng */
.pf-fav-filter-summary .pf-fav-summary-chip {
    flex-shrink: 0;
}

/* Chip đếm và nút Xoá không co */
.pf-fav-filter-summary .pf-fav-summary-count,
.pf-fav-filter-summary .pf-fav-summary-clear {
    flex-shrink: 0;
}

/* Chip "+N ..." */
.pf-fav-summary-chip.more {
    background: linear-gradient(135deg, rgba(148,163,184,.15), rgba(100,116,139,.1));
    border-color: rgba(148,163,184,.4);
    color: #475569;
    font-weight: 800;
    cursor: help;
    position: relative;
    padding-right: .65rem;
}
[data-theme="dark"] .pf-fav-summary-chip.more {
    background: linear-gradient(135deg, rgba(148,163,184,.2), rgba(100,116,139,.15));
    color: #cbd5e1;
}

.pf-fav-summary-chip.more:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(100,116,139,.3);
}

/* Tooltip cho chip +N */
.pf-fav-summary-chip.more::after {
    content: attr(data-tooltip);
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    background: #0f172a;
    color: #fff;
    padding: .55rem .75rem;
    border-radius: 10px;
    font-size: .7rem;
    font-weight: 500;
    white-space: pre-line;
    line-height: 1.55;
    width: max-content;
    max-width: min(340px, 85vw);
    box-shadow: 0 10px 30px rgba(0,0,0,.35);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-4px);
    transition: opacity .18s ease, transform .18s ease, visibility .18s;
    z-index: 9999;
    pointer-events: none;
    letter-spacing: 0;
    text-align: left;
}
.pf-fav-summary-chip.more::before {
    content: '';
    position: absolute;
    top: calc(100% + 3px);
    right: 14px;
    border: 6px solid transparent;
    border-bottom-color: #0f172a;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-4px);
    transition: opacity .18s ease, transform .18s ease, visibility .18s;
    z-index: 10000;
    pointer-events: none;
}
.pf-fav-summary-chip.more:hover::after,
.pf-fav-summary-chip.more:hover::before {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

[data-theme="dark"] .pf-fav-summary-chip.more::after {
    background: #1e293b;
    border: 1px solid #334155;
}
[data-theme="dark"] .pf-fav-summary-chip.more::before {
    border-bottom-color: #1e293b;
}

/* Container chip filter có thể bị cắt khi hẹp */
.pf-fav-summary-chips-wrap {
    display: flex;
    align-items: center;
    gap: .3rem;
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
}

/* Mobile: số chip hiển thị ít hơn để đủ chỗ */
@media (max-width: 500px) {
    .pf-fav-filter-summary {
        gap: .25rem;
        padding: .35rem .55rem .4rem;
    }
    .pf-fav-summary-chip.more::after {
        font-size: .68rem;
        max-width: 90vw;
        padding: .5rem .65rem;
    }
}
"""



# ═══════════════════════════════════════════════════════════════
# HTML SNIPPETS
# ═══════════════════════════════════════════════════════════════
def build_favorites_html():
    return {
        # Tab Yêu thích — chèn SAU nút Chuyên ngành
        "dataset_tab":
            '<button class="ds-btn ds-btn-primary" data-dataset-group="favorites" id="dsFavBtn">\n'
            '            <i class="far fa-heart"></i>\n'
            '            <span>Yêu thích</span>\n'
            '            <span class="ds-fav-badge" id="favTabBadge" data-count="0"></span>\n'
            '            <i class="fas fa-lock ds-fav-lock" id="favTabLock" style="display:none;"></i>\n'
            '        </button>',

        # Dropdown item Yêu thích — chèn SAU item Chuyên ngành trong dropdown
        "dataset_dropdown_item":
            '<button class="ds-dropdown-item" data-dataset-group="favorites" id="dsFavDropdownItem" type="button">\n'
            '            <i class="far fa-heart ds-dd-fav-icon"></i>\n'
            '            <span>Yêu thích</span>\n'
            '            <span class="ds-dd-fav-badge" id="favDropdownBadge" data-count="0"></span>\n'
            '            <i class="fas fa-lock ds-dd-fav-lock" id="favDropdownLock" style="display:none;"></i>\n'
            '        </button>',

        # Nút tim FLOAT — góc phải
        "pf_float_btn":
            '<button class="pf-fav-float" id="pfFavBtn" type="button" '
            'title="Thêm vào yêu thích" aria-label="Thêm vào yêu thích">'
            '<i class="far fa-heart"></i>'
            '<span class="pf-fav-float-label">Like</span>'
            '</button>',

        # Nút toggle "Chỉ câu yêu thích" — góc trái
        "pf_fav_only_btn":
            '<button class="pf-fav-only-float" id="pfFavOnlyBtn" type="button" '
            'title="Chỉ luyện câu yêu thích" aria-label="Chỉ luyện câu yêu thích">'
            '<i class="far fa-heart"></i>'
            '<span class="pf-fav-only-label">Favorites Only</span>'
            '<span class="pf-fav-only-count" id="pfFavOnlyCount">0</span>'
            '</button>',
    }


# ═══════════════════════════════════════════════════════════════
# JS — Toàn bộ logic
# ═══════════════════════════════════════════════════════════════
def build_favorites_js():
    return r"""
/* ═══════════════════════════════════════════════════════════════
   ❤️ FAVORITES — Module quản lý câu yêu thích
   KEY = datasetId + "_" + stt  (VD: "tonghop_1", "ketoan_5")
   ═══════════════════════════════════════════════════════════════ */

/* ============ STATE ============ */
var favState = {
    items: {},
    loaded: false,
    loading: false,
    sortMode: 'recent',
    listener: null,
    currentView: false,
    filteringOnly: false,
    pfOnlyFav: false,
    __renderTimer: null
};

/* ============ TIER CHECK ============ */
function favCanUse() {
    if (typeof window.APP_TIER === 'undefined') return false;
    return window.APP_TIER === 'active';
}

function favIsLoggedIn() {
    return typeof currentUser !== 'undefined' && currentUser !== null;
}

function favGetCurrentEmail() {
    if (favIsLoggedIn() && currentUser.email) return currentUser.email.toLowerCase();
    return null;
}

function favGetStorageKey() {
    var email = favGetCurrentEmail();
    return email ? ('favorites_cache_' + email) : 'favorites_guest';
}

/* ═══════════════════════════════════════════════════════════════
   ⭐ KEY BUILDER — datasetId + "_" + stt
   ═══════════════════════════════════════════════════════════════ */
function favBuildKey(stt, datasetId) {
    if (stt === null || stt === undefined) return null;
    var ds = datasetId;
    if (!ds) {
        ds = (typeof CURRENT_DATASET !== 'undefined' && CURRENT_DATASET)
             ? CURRENT_DATASET
             : 'tonghop';
    }
    return String(ds) + '_' + String(stt);
}

function favParseKey(key) {
    if (!key) return null;
    var str = String(key);
    var idx = str.indexOf('_');
    if (idx === -1) {
        return { datasetId: 'tonghop', stt: str };
    }
    return {
        datasetId: str.substring(0, idx),
        stt: str.substring(idx + 1)
    };
}

function favGetCurrentDsId() {
    return (typeof CURRENT_DATASET !== 'undefined' && CURRENT_DATASET)
           ? CURRENT_DATASET
           : 'tonghop';
}
/* ═══════════════════════════════════════════════════════════════
   ⭐ SWITCH DATASET ĐẦY ĐỦ — cover hết UI + data + filter
   Dùng khi cần đổi dataset từ bất kỳ ngữ cảnh nào (dropdown fav, v.v.)
   ═══════════════════════════════════════════════════════════════ */
function favSwitchDatasetFull(targetDs) {
    if (!targetDs) return false;

    console.log('[Favorites] favSwitchDatasetFull → ' + targetDs);

    /* ═══ 1. Đổi data + CURRENT_DATASET ═══ */
    var switched = false;

    if (typeof window.__switchRawData === 'function') {
        try {
            switched = window.__switchRawData(targetDs);
        } catch(e) {
            console.warn('[Favorites] __switchRawData error:', e);
        }
    }

    if (!switched) {
        console.warn('[Favorites] __switchRawData failed for: ' + targetDs);
        return false;
    }

    /* ═══ 2. Đổi active state UI ═══ */
    document.querySelectorAll('.ds-btn, .ds-sub-btn').forEach(function(b) {
        b.classList.remove('active');
    });

    /* Ưu tiên: tìm ds-btn trước (cho tab chính) */
    var targetBtn = document.querySelector('.ds-btn[data-dataset="' + targetDs + '"]');

    /* Nếu không có, tìm ds-sub-btn (chuyên ngành) */
    if (!targetBtn) {
        targetBtn = document.querySelector('.ds-sub-btn[data-dataset="' + targetDs + '"]');
        /* Nếu là sub-btn → active luôn nút Chuyên ngành cha */
        if (targetBtn) {
            var cnBtn = document.querySelector('.ds-btn[data-dataset-group="chuyen-nganh"]');
            if (cnBtn) cnBtn.classList.add('active');
        }
    }

    if (targetBtn) targetBtn.classList.add('active');

    /* ═══ 3. Ẩn sub-wrap nếu không phải chuyên ngành ═══ */
    var subWrap = document.getElementById('dsSubWrap');
    if (subWrap) {
        var isChuyenNganh = (targetDs !== 'tonghop')
                         && !document.querySelector('.ds-btn[data-dataset="' + targetDs + '"]');
        /* Nếu là ds-btn chính → ẩn sub-wrap */
        if (!isChuyenNganh) {
            subWrap.style.display = 'none';
        }
    }

    /* ═══ 4. Clear onboarding override ═══ */
    window.__onboardingOverride = null;
    window.__onboardingAutoPicked = false;

    /* ═══ 5. Rebuild filters (HSK options + subject options) ═══ */
    try {
        if (typeof buildFilters === 'function') buildFilters();
    } catch(e) {}

    /* ═══ 6. Apply filter → rebuild filtered ═══ */
    try {
        if (typeof applyFilter === 'function') applyFilter();
        if (typeof updateResultCount === 'function') updateResultCount();
    } catch(e) {}

    /* ═══ 7. Đồng bộ #pfDatasetSelect trong Full mode ═══ */
    var dsSel = document.getElementById('pfDatasetSelect');
    if (dsSel) {
        /* Set giá trị nếu option tồn tại */
        for (var i = 0; i < dsSel.options.length; i++) {
            if (dsSel.options[i].value === targetDs) {
                dsSel.value = targetDs;
                break;
            }
        }
    }

    /* ═══ 8. Rebuild filter options trong Full mode ═══ */
    try {
        if (typeof pfBuildFilterOptions === 'function') pfBuildFilterOptions();
    } catch(e) {}

    try {
        if (typeof pfBuildDatasetSelect === 'function') pfBuildDatasetSelect();
    } catch(e) {}

    /* ═══ 9. Trigger watchers (vocab lock, subject lock) ═══ */
    setTimeout(function() {
        /* Watch dataset nav (ẩn nav-back-btn nếu rời vocab) */
        if (typeof watchDatasetNav === 'function') {
            try { watchDatasetNav(); } catch(e) {}
        }

        /* Sync vocab mode (lock subject, thêm HSK7-9) */
        var isVocab = (targetDs === 'tu-vung');

        var body = document.body;
        if (isVocab) {
            body.setAttribute('data-vocab-mode', '1');
        } else {
            body.removeAttribute('data-vocab-mode');
        }

        /* Update subject filter disabled state */
        var subjSelects = [
            document.getElementById('subjectFilter'),
            document.getElementById('pfSubjectFilter')
        ];
        subjSelects.forEach(function(sf) {
            if (!sf) return;
            if (isVocab) {
                sf.disabled = true;
                sf.value = '';
                sf.style.opacity = '0.5';
                sf.style.cursor = 'not-allowed';
            } else {
                sf.disabled = false;
                sf.style.opacity = '';
                sf.style.cursor = '';
            }
        });
    }, 50);

    console.log('[Favorites] favSwitchDatasetFull done → ' + targetDs);
    return true;
}

window.favSwitchDatasetFull = favSwitchDatasetFull;

/* ============ LOCK DIALOG ============ */
function favShowLockDialog() {
    if (!favIsLoggedIn()) {
        if (confirm('❤️ Yêu thích câu\n\n' +
                    'Bạn cần ĐĂNG NHẬP và GIA HẠN để dùng tính năng này.\n\n' +
                    'Đăng nhập ngay?')) {
            if (typeof showLoginModal === 'function') showLoginModal();
        }
        return;
    }
    var tier = (typeof window.APP_TIER !== 'undefined') ? window.APP_TIER : 'demo';
    if (tier === 'demo' || tier === 'trial' || tier === 'expired') {
        if (confirm('❤️ Yêu thích câu\n\n' +
                    'Chỉ tài khoản ĐÃ GIA HẠN mới dùng được tính năng này.\n\n' +
                    'Gia hạn ngay để lưu câu yêu thích?')) {
            if (typeof openRenewalModal === 'function') openRenewalModal();
        }
        return;
    }
}

/* ═══════════════════════════════════════════════════════════════
   LOAD / SAVE LOCAL — Migration key cũ → key mới
   ═══════════════════════════════════════════════════════════════ */
function favLoadFromLocal() {
    try {
        var key = favGetStorageKey();
        var cached = JSON.parse(localStorage.getItem(key) || 'null');
        if (cached && cached.items && typeof cached.items === 'object') {

            var rawItems = cached.items;
            var migrated = {};
            var needResave = false;

            Object.keys(rawItems).forEach(function(k) {
                var item = rawItems[k];
                if (!item || typeof item !== 'object') {
                    needResave = true;
                    return;
                }

                var parsed = favParseKey(k);
                var ds = item.datasetId || parsed.datasetId || 'tonghop';
                var stt = item.stt || parsed.stt;

                var newKey = favBuildKey(stt, ds);
                if (newKey !== k) needResave = true;

                migrated[newKey] = {
                    stt: String(stt),
                    datasetId: ds,
                    addedAt: item.addedAt || Date.now(),
                    hsk: item.hsk || '',
                    subject: item.subject || ''
                };
            });

            favState.items = migrated;

            if (needResave) {
                favSaveToLocal();
                if (typeof favMigrateLocalToCloud === 'function') {
                    favMigrateLocalToCloud();
                }
            }

            return true;
        }
    } catch(e) {
        console.warn('[Favorites] Load local error:', e);
    }
    return false;
}

function favSaveToLocal() {
    try {
        var key = favGetStorageKey();
        localStorage.setItem(key, JSON.stringify({
            items: favState.items,
            savedAt: Date.now()
        }));
    } catch(e) {
        console.warn('[Favorites] Save local error:', e);
    }
}

/* ═══════════════════════════════════════════════════════════════
   LOAD FROM CLOUD — Doc ID = key mới
   ═══════════════════════════════════════════════════════════════ */
async function favLoadFromCloud() {
    if (!favCanUse()) return;
    var email = favGetCurrentEmail();
    if (!email || typeof db === 'undefined' || !db) return;
    if (favState.loading) return;
    favState.loading = true;

    try {
        var snap = await db.collection('favorites').doc(email)
            .collection('items').get();

        var items = {};
        var needMigration = false;

        snap.forEach(function(doc) {
            var d = doc.data() || {};
            var docId = String(doc.id);

            var parsed = favParseKey(docId);
            var ds = d.datasetId || parsed.datasetId || 'tonghop';
            var stt = d.stt || parsed.stt;

            var newKey = favBuildKey(stt, ds);
            if (newKey !== docId) needMigration = true;

            items[newKey] = {
                stt: String(stt),
                datasetId: ds,
                addedAt: d.addedAt
                    ? (d.addedAt.toMillis ? d.addedAt.toMillis() : d.addedAt)
                    : Date.now(),
                hsk: d.hsk || '',
                subject: d.subject || ''
            };
        });

        favState.items = items;
        favState.loaded = true;
        favSaveToLocal();
        favNotifyChanged();
        favListenCloud();

        if (needMigration && typeof favMigrateLocalToCloud === 'function') {
            favMigrateLocalToCloud();
        }

    } catch(e) {
        console.warn('[Favorites] Load cloud error:', e);
    } finally {
        favState.loading = false;
    }
}

/* ═══════════════════════════════════════════════════════════════
   LISTEN CLOUD — Realtime
   ═══════════════════════════════════════════════════════════════ */
function favListenCloud() {
    if (!favCanUse()) return;
    var email = favGetCurrentEmail();
    if (!email || typeof db === 'undefined' || !db) return;

    if (favState.listener) {
        try { favState.listener(); } catch(e) {}
        favState.listener = null;
    }

    favState.listener = db.collection('favorites').doc(email)
        .collection('items')
        .onSnapshot(function(snap) {

            var items = {};
            var needMigration = false;

            snap.forEach(function(doc) {
                var d = doc.data() || {};
                var docId = String(doc.id);

                var parsed = favParseKey(docId);
                var ds = d.datasetId || parsed.datasetId || 'tonghop';
                var stt = d.stt || parsed.stt;

                var newKey = favBuildKey(stt, ds);
                if (newKey !== docId) needMigration = true;

                items[newKey] = {
                    stt: String(stt),
                    datasetId: ds,
                    addedAt: d.addedAt
                        ? (d.addedAt.toMillis ? d.addedAt.toMillis() : d.addedAt)
                        : Date.now(),
                    hsk: d.hsk || '',
                    subject: d.subject || ''
                };
            });

            favState.items = items;
            favState.loaded = true;
            favSaveToLocal();
            favNotifyChanged();

            if (needMigration && typeof favMigrateLocalToCloud === 'function') {
                favMigrateLocalToCloud();
            }

        }, function(err) {
            console.warn('[Favorites] Listener error:', err);
        });
}

/* ═══════════════════════════════════════════════════════════════
   ⭐ MIGRATION CLOUD
   ═══════════════════════════════════════════════════════════════ */
var _favMigrating = false;

async function favMigrateLocalToCloud() {
    if (_favMigrating) return;
    if (!favCanUse()) return;

    var email = favGetCurrentEmail();
    if (!email || typeof db === 'undefined' || !db) return;

    _favMigrating = true;

    try {
        var snap = await db.collection('favorites').doc(email)
            .collection('items').get();

        var toDelete = [];
        var toCreate = [];

        snap.forEach(function(doc) {
            var d = doc.data() || {};
            var docId = String(doc.id);

            var parsed = favParseKey(docId);
            var ds = d.datasetId || parsed.datasetId || 'tonghop';
            var stt = d.stt || parsed.stt;

            var newKey = favBuildKey(stt, ds);

            if (newKey !== docId) {
                toCreate.push({
                    ref: db.collection('favorites').doc(email)
                        .collection('items').doc(newKey),
                    data: {
                        stt: String(stt),
                        datasetId: ds,
                        hsk: d.hsk || '',
                        subject: d.subject || '',
                        addedAt: d.addedAt || firebase.firestore.FieldValue.serverTimestamp()
                    }
                });
                toDelete.push(doc.ref);
            } else if (!d.datasetId) {
                toCreate.push({
                    ref: doc.ref,
                    data: { datasetId: ds },
                    isUpdate: true
                });
            }
        });

        if (toCreate.length === 0 && toDelete.length === 0) {
            _favMigrating = false;
            return;
        }

        var BATCH_SIZE = 400;
        for (var i = 0; i < toCreate.length; i += BATCH_SIZE) {
            var batch = db.batch();
            var chunk = toCreate.slice(i, i + BATCH_SIZE);
            chunk.forEach(function(entry) {
                if (entry.isUpdate) {
                    batch.update(entry.ref, entry.data);
                } else {
                    batch.set(entry.ref, entry.data);
                }
            });
            await batch.commit();
        }

        for (var j = 0; j < toDelete.length; j += BATCH_SIZE) {
            var delBatch = db.batch();
            var delChunk = toDelete.slice(j, j + BATCH_SIZE);
            delChunk.forEach(function(ref) {
                delBatch.delete(ref);
            });
            await delBatch.commit();
        }

        console.log('[Favorites] Migrated: +' + toCreate.length + ' / -' + toDelete.length);

    } catch(e) {
        console.warn('[Favorites] Migration error:', e);
    } finally {
        _favMigrating = false;
    }
}

/* ═══════════════════════════════════════════════════════════════
   ADD / REMOVE / TOGGLE
   ═══════════════════════════════════════════════════════════════ */
async function favAdd(stt, record, datasetId) {
    if (!favCanUse()) { favShowLockDialog(); return false; }
    var email = favGetCurrentEmail();
    if (!email) { favShowLockDialog(); return false; }

    stt = String(stt);
    var currentDsId = datasetId || favGetCurrentDsId();
    var key = favBuildKey(stt, currentDsId);

    var isAdmin = (typeof currentUser !== 'undefined'
                   && currentUser
                   && currentUser.role === 'admin');

    var MAX_PER_DAY = 500;
    var today = new Date().toDateString();

    if (!isAdmin) {
        var dayKey = 'fav_daily_' + email;
        var daily = { date: today, count: 0 };
        try {
            var saved = JSON.parse(localStorage.getItem(dayKey) || 'null');
            if (saved && saved.date === today) {
                daily = saved;
            }
        } catch(e) {}

        if (daily.count >= MAX_PER_DAY) {
            var tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setHours(0, 0, 0, 0);
            var hoursLeft = Math.ceil((tomorrow - Date.now()) / 3600000);
            favShowToast('Đã đạt giới hạn ' + MAX_PER_DAY + ' tim hôm nay. Còn ' + hoursLeft + 'h nữa!', 'warn');
            return false;
        }

        daily.count++;
        daily.date = today;
        try { localStorage.setItem(dayKey, JSON.stringify(daily)); } catch(e) {}
    }

    favState.items[key] = {
        stt: stt,
        datasetId: currentDsId,
        addedAt: Date.now(),
        hsk: record && record.hsk ? record.hsk : '',
        subject: record && record.subject ? record.subject : ''
    };
    favSaveToLocal();
    favNotifyChanged();

    if (typeof db !== 'undefined' && db) {
        try {
            await db.collection('favorites').doc(email)
                .collection('items').doc(key).set({
                    stt: stt,
                    datasetId: currentDsId,
                    hsk: favState.items[key].hsk,
                    subject: favState.items[key].subject,
                    addedAt: firebase.firestore.FieldValue.serverTimestamp()
                });
        } catch(e) {
            console.warn('[Favorites] Add cloud error:', e);
            delete favState.items[key];
            favSaveToLocal();
            favNotifyChanged();

            if (!isAdmin) {
                try {
                    var dayKey2 = 'fav_daily_' + email;
                    var d2 = JSON.parse(localStorage.getItem(dayKey2) || 'null');
                    if (d2 && d2.date === today && d2.count > 0) {
                        d2.count--;
                        localStorage.setItem(dayKey2, JSON.stringify(d2));
                    }
                } catch(e2) {}
            }

            favShowToast('Lỗi lưu! Thử lại sau', 'warn');
            return false;
        }
    }
    return true;
}

async function favRemove(stt, datasetId) {
    if (!favCanUse()) { favShowLockDialog(); return false; }
    var email = favGetCurrentEmail();
    if (!email) return false;

    stt = String(stt);
    var targetDs = datasetId || favGetCurrentDsId();
    var key = favBuildKey(stt, targetDs);

    var backup = favState.items[key];
    if (!backup) {
        if (favState.items[stt]) {
            key = stt;
            backup = favState.items[key];
        }
    }
    if (!backup) return true;

    delete favState.items[key];
    favSaveToLocal();
    favNotifyChanged();

    if (typeof db !== 'undefined' && db) {
        try {
            await db.collection('favorites').doc(email)
                .collection('items').doc(key).delete();
        } catch(e) {
            console.warn('[Favorites] Remove cloud error:', e);
            favState.items[key] = backup;
            favSaveToLocal();
            favNotifyChanged();
            return false;
        }
    }
    return true;
}

async function favToggle(stt, record, datasetId) {
    if (!favCanUse()) { favShowLockDialog(); return; }
    stt = String(stt);

    var dsId = datasetId || favGetCurrentDsId();

    if (favHas(stt, dsId)) {
        var ok = await favRemove(stt, dsId);
        if (ok) favShowToast('Đã xoá khỏi yêu thích', 'remove');
    } else {
        var ok2 = await favAdd(stt, record, dsId);
        if (ok2) favShowToast('Đã thêm vào yêu thích', 'add');
    }
}

async function favClearAll() {
    if (!favCanUse()) { favShowLockDialog(); return; }
    var email = favGetCurrentEmail();
    if (!email) return;

    var count = favCount();
    if (count === 0) {
        favShowToast('Chưa có câu yêu thích nào', 'warn');
        return;
    }

    if (!confirm('Xoá TẤT CẢ ' + count + ' câu yêu thích?\n\nKhông thể hoàn tác!')) return;

    var backup = favState.items;
    favState.items = {};
    favSaveToLocal();
    favNotifyChanged();

    if (typeof db !== 'undefined' && db) {
        try {
            var snap = await db.collection('favorites').doc(email)
                .collection('items').get();

            if (snap.size === 0) return;

            var BATCH_SIZE = 450;
            var docs = [];
            snap.forEach(function(doc) { docs.push(doc.ref); });

            for (var i = 0; i < docs.length; i += BATCH_SIZE) {
                var batch = db.batch();
                var chunk = docs.slice(i, i + BATCH_SIZE);
                chunk.forEach(function(ref) { batch.delete(ref); });
                await batch.commit();
            }
        } catch(e) {
            console.warn('[Favorites] Clear cloud error:', e);
            favState.items = backup;
            favSaveToLocal();
            favNotifyChanged();
            favShowToast('Lỗi! Thử lại sau', 'warn');
            return;
        }
    }
    favShowToast('Đã xoá tất cả yêu thích', 'remove');
}

/* ═══════════════════════════════════════════════════════════════
   CHECK / COUNT
   ═══════════════════════════════════════════════════════════════ */
function favHas(stt, datasetId) {
    if (stt === null || stt === undefined) return false;

    var targetDs = datasetId || favGetCurrentDsId();

    var key = favBuildKey(stt, targetDs);
    if (favState.items[key]) return true;

    var oldItem = favState.items[String(stt)];
    if (oldItem) {
        var itemDs = oldItem.datasetId || 'tonghop';
        return itemDs === targetDs;
    }

    return false;
}

function favCount() {
    return Object.keys(favState.items).length;
}

function favCountInCurrentDataset() {
    var currentDs = favGetCurrentDsId();
    var count = 0;
    Object.keys(favState.items).forEach(function(k) {
        var item = favState.items[k];
        if (!item) return;
        var parsed = favParseKey(k);
        var ds = item.datasetId || (parsed && parsed.datasetId) || 'tonghop';
        if (ds === currentDs) count++;
    });
    return count;
}

function favGetDailyRemaining() {
    var email = favGetCurrentEmail();
    if (!email) return 0;

    var isAdmin = (typeof currentUser !== 'undefined'
                   && currentUser
                   && currentUser.role === 'admin');
    if (isAdmin) return Infinity;

    var MAX_PER_DAY = 500;
    var today = new Date().toDateString();

    try {
        var saved = JSON.parse(localStorage.getItem('fav_daily_' + email) || 'null');
        if (saved && saved.date === today) {
            return Math.max(0, MAX_PER_DAY - saved.count);
        }
    } catch(e) {}

    return MAX_PER_DAY;
}

function favGetDailyUsed() {
    var email = favGetCurrentEmail();
    if (!email) return 0;

    var today = new Date().toDateString();
    try {
        var saved = JSON.parse(localStorage.getItem('fav_daily_' + email) || 'null');
        if (saved && saved.date === today) {
            return saved.count;
        }
    } catch(e) {}
    return 0;
}

/* ═══════════════════════════════════════════════════════════════
   FIND RECORD
   ═══════════════════════════════════════════════════════════════ */
function favFindRecordInDataset(dsId, stt) {
    if (!dsId || stt === null || stt === undefined) return null;
    stt = String(stt);

    /* ═══ 1. Tìm trong DATASET_REGISTRY (tổng hợp + chuyên ngành) ═══ */
    if (typeof DATASET_REGISTRY !== 'undefined' && DATASET_REGISTRY) {
        var ds = DATASET_REGISTRY[dsId];
        if (ds && Array.isArray(ds.data)) {
            for (var i = 0; i < ds.data.length; i++) {
                if (String(ds.data[i].stt) === stt) return ds.data[i];
            }
        }
    }

    /* ═══════════════════════════════════════════════════════════
       ⭐ 2. Tìm trong FIXPY_DATASETS (từ vựng + tab tự động từ data/)
       Đây là FIX cho tab Từ vựng HSK
       ═══════════════════════════════════════════════════════════ */
    if (typeof window.FIXPY_DATASETS !== 'undefined'
        && window.FIXPY_DATASETS
        && window.FIXPY_DATASETS[dsId]) {
        var fixpyDs = window.FIXPY_DATASETS[dsId];
        if (fixpyDs && Array.isArray(fixpyDs.data)) {
            for (var k = 0; k < fixpyDs.data.length; k++) {
                if (String(fixpyDs.data[k].stt) === stt) return fixpyDs.data[k];
            }
        }
    }

    /* ═══ 3. Fallback: tonghop → RAW_DATA ═══ */
    if (dsId === 'tonghop' && typeof RAW_DATA !== 'undefined' && RAW_DATA) {
        for (var j = 0; j < RAW_DATA.length; j++) {
            if (String(RAW_DATA[j].stt) === stt) return RAW_DATA[j];
        }
    }

    /* ═══ 4. Fallback: RAW_DATA hiện tại (khi __switchRawData đã chạy) ═══ */
    if (typeof RAW_DATA !== 'undefined' && RAW_DATA) {
        for (var m = 0; m < RAW_DATA.length; m++) {
            if (String(RAW_DATA[m].stt) === stt) return RAW_DATA[m];
        }
    }

    return null;
}
function favFindRecordAnywhere(stt) {
    if (stt === null || stt === undefined) return null;
    stt = String(stt);

    /* ═══ 1. Tìm trong DATASET_REGISTRY ═══ */
    if (typeof DATASET_REGISTRY !== 'undefined' && DATASET_REGISTRY) {
        var keys = Object.keys(DATASET_REGISTRY);
        for (var k = 0; k < keys.length; k++) {
            var ds = DATASET_REGISTRY[keys[k]];
            if (ds && Array.isArray(ds.data)) {
                for (var i = 0; i < ds.data.length; i++) {
                    if (String(ds.data[i].stt) === stt) return ds.data[i];
                }
            }
        }
    }

    /* ═══════════════════════════════════════════════════════════
       ⭐ 2. FIX: Tìm trong FIXPY_DATASETS (từ vựng + tab auto)
       ═══════════════════════════════════════════════════════════ */
    if (typeof window.FIXPY_DATASETS !== 'undefined'
        && window.FIXPY_DATASETS) {
        var fixpyKeys = Object.keys(window.FIXPY_DATASETS);
        for (var f = 0; f < fixpyKeys.length; f++) {
            var fixpyDs = window.FIXPY_DATASETS[fixpyKeys[f]];
            if (fixpyDs && Array.isArray(fixpyDs.data)) {
                for (var g = 0; g < fixpyDs.data.length; g++) {
                    if (String(fixpyDs.data[g].stt) === stt) {
                        return fixpyDs.data[g];
                    }
                }
            }
        }
    }

    /* ═══ 3. Fallback RAW_DATA ═══ */
    if (typeof RAW_DATA !== 'undefined' && RAW_DATA) {
        for (var j = 0; j < RAW_DATA.length; j++) {
            if (String(RAW_DATA[j].stt) === stt) return RAW_DATA[j];
        }
    }

    return null;
}
/* ═══════════════════════════════════════════════════════════════
   ⭐ LẤY TẤT CẢ RECORD YÊU THÍCH (không phân biệt dataset)
   ═══════════════════════════════════════════════════════════════ */
function favGetRecords() {
    var out = [];
    var seen = {};

    Object.keys(favState.items).forEach(function(key) {
        var item = favState.items[key];
        if (!item) return;

        var parsed = favParseKey(key);
        if (!parsed) return;

        var itemDs = item.datasetId || parsed.datasetId || 'tonghop';
        var itemStt = item.stt || parsed.stt;

        var record = null;
        if (typeof favFindRecordInDataset === 'function') {
            record = favFindRecordInDataset(itemDs, itemStt);
        }
        if (!record && typeof favFindRecordAnywhere === 'function') {
            record = favFindRecordAnywhere(itemStt);
        }

        var seenKey = itemDs + '_' + itemStt;
        if (record && !seen[seenKey]) {
            seen[seenKey] = true;

            /* Clone record để không làm hỏng object gốc */
            var cloned = {};
            Object.keys(record).forEach(function(k) {
                cloned[k] = record[k];
            });

            cloned.__favDatasetId = itemDs;
            cloned.__favKey = key;
            cloned.__favAddedAt = item.addedAt || 0;

            out.push(cloned);
        }
    });

    return out;
}

function favIsFavoriteRecord(r) {
    if (!r) return false;
    return favHas(r.stt);
}

/* ============ SORT ============ */
function favGetSortedList() {
    var items = Object.keys(favState.items).map(function(k) { return favState.items[k]; });
    var mode = favState.sortMode;

    if (mode === 'oldest') {
        items.sort(function(a, b) { return (a.addedAt || 0) - (b.addedAt || 0); });
    } else if (mode === 'stt') {
        items.sort(function(a, b) {
            var na = parseInt(a.stt) || 0;
            var nb = parseInt(b.stt) || 0;
            return na - nb;
        });
    } else {
        items.sort(function(a, b) { return (b.addedAt || 0) - (a.addedAt || 0); });
    }
    return items;
}

/* ═══════════════════════════════════════════════════════════════
   DROPDOWN "CÂU:"
   ═══════════════════════════════════════════════════════════════ */
function favGetQuestionsForDropdown() {
    /* ═══════════════════════════════════════════════════════════
       ⭐ KHI BẬT TOGGLE: Trả về TẤT CẢ câu yêu thích
       (không filter theo dataset hiện tại)
       ═══════════════════════════════════════════════════════════ */
    if (favState.pfOnlyFav && favCanUse()) {
        return favGetRecords();   /* Đã có __favDatasetId trong mỗi record */
    }

    /* ═══ KHI TẮT TOGGLE: Trả về RAW_DATA hiện tại ═══ */
    if (typeof RAW_DATA === 'undefined' || !RAW_DATA) return [];
    return RAW_DATA;
}
function favRefreshQuestionDropdown() {
    var fns = [
        'renderQuestionSelect',
        'buildQuestionDropdown',
        'updateQuestionList',
        'renderQuestionList',
        'buildQuestionSelect',
        'renderPfQuestionSelect',
        'renderQuestionPicker',
        'updateQuestionPicker',
        'refreshQuestionDropdown',
        'populateQuestionSelect',
        'renderPfQSelect'
    ];
    for (var i = 0; i < fns.length; i++) {
        if (typeof window[fns[i]] === 'function') {
            try {
                window[fns[i]]();
                return true;
            } catch(e) {
                console.warn('[Favorites] ' + fns[i] + '() error:', e);
            }
        }
    }

    var sel = document.getElementById('pfQuestionSelect')
           || document.getElementById('questionSelect')
           || document.getElementById('pfQuestionDropdown')
           || document.getElementById('questionPicker')
           || document.querySelector('.pf-question-select select')
           || document.querySelector('#pfQuestionPicker');
    if (!sel) return false;

    try {
        var list = favGetQuestionsForDropdown();
        var curStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt) ? String(pfCurrentStt) : '';
        var html = '';
        for (var j = 0; j < list.length; j++) {
            var r = list[j];
            var sel2 = (String(r.stt) === curStt) ? ' selected' : '';
            html += '<option value="' + r.stt + '"' + sel2 + '>'
                  + '#' + r.stt + ' · ' + (r.vi || '')
                  + '</option>';
        }
        sel.innerHTML = html;
        return true;
    } catch(e) {
        console.warn('[Favorites] Fallback dropdown error:', e);
        return false;
    }
}
/* ═══════════════════════════════════════════════════════════════
   ⭐ REBUILD dropdown "CÂU:" từ danh sách record ĐÃ FILTER
   - Dùng khi toggle bật + có favFilters
   - Gọi từ: favRefreshQuestionDropdown, pfApplyFilter, pfBuildQuickNav
   ═══════════════════════════════════════════════════════════════ */
function favRebuildQuickNavForFav(records) {
    var sel = document.getElementById('pfQuickNav');
    if (!sel) return;

    var list = records || favGetRecords();
    var curStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                 ? String(pfCurrentStt)
                 : '';
    var curDs = favGetCurrentDsId();

    var html = '<option value="">-- Chọn câu yêu thích (' + list.length + ') --</option>';

    /* ⭐ Track selected index */
    var foundSelectedIndex = -1;

    for (var j = 0; j < list.length; j++) {
        var r = list[j];
        var vi = (r.vi || '').substring(0, 45);
        var sttRaw = (r.stt !== undefined && r.stt !== null && String(r.stt).trim() !== '')
                     ? '#' + String(r.stt).trim() + ' · '
                     : '';
        var itemDs = r.__favDatasetId || 'tonghop';
        var dsTag = (itemDs !== curDs)
                    ? '[' + itemDs + '] '
                    : '';
        var label = dsTag + sttRaw + 'Câu ' + (j + 1) + ': ' + vi;

        /* ⭐ UNIQUE KEY = datasetId + '::' + stt */
        var uniqueKey = itemDs + '::' + String(r.stt);

        /* ⭐ Check match: CẢ stt + datasetId */
        var isCurrent = (String(r.stt) === curStt && itemDs === curDs);
        if (isCurrent) {
            foundSelectedIndex = j + 1;   /* +1 vì có option "-- Chọn --" ở đầu */
        }

        var selected = isCurrent ? ' selected' : '';

        html += '<option value="' + escapeHtml(uniqueKey) + '"' +
                ' data-dataset-id="' + escapeHtml(itemDs) + '"' +
                ' data-stt="' + escapeHtml(String(r.stt)) + '"' +
                selected + '>' +
                escapeHtml(label) + '</option>';
    }

    sel.innerHTML = html;

    /* ⭐ Set selectedIndex (CHÍNH XÁC hơn set value) */
    if (foundSelectedIndex >= 0) {
        sel.selectedIndex = foundSelectedIndex;
    } else if (curStt) {
        /* Fallback: tìm option có data-stt khớp (khi dataset lệch) */
        var opts = sel.options;
        for (var k = 0; k < opts.length; k++) {
            if (opts[k].dataset && opts[k].dataset.stt === curStt) {
                sel.selectedIndex = k;
                break;
            }
        }
    }
}

window.favRebuildQuickNavForFav = favRebuildQuickNavForFav;
/* ═══════════════════════════════════════════════════════════════
   NÚT TIM FLOAT
   ═══════════════════════════════════════════════════════════════ */
function favUpdatePfFloatBtn() {
    var pfBtn = document.getElementById('pfFavBtn');
    if (!pfBtn) return;

    var icon = pfBtn.querySelector('i');
    var label = pfBtn.querySelector('.pf-fav-float-label');
    var can = favCanUse();
    var stt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt) ? String(pfCurrentStt) : null;
    var currentDsId = favGetCurrentDsId();

    if (!can) {
        pfBtn.classList.add('locked');
        pfBtn.classList.remove('active');
        if (icon) icon.className = 'fas fa-lock';
        if (label) label.textContent = 'Khoá';
        pfBtn.title = 'Cần gia hạn để dùng Yêu thích';
        return;
    }

    pfBtn.classList.remove('locked');
    var active = stt ? favHas(stt, currentDsId) : false;
    pfBtn.classList.toggle('active', active);
    if (icon) icon.className = active ? 'fas fa-heart' : 'far fa-heart';
    if (label) label.textContent = 'Like';
    pfBtn.title = active ? 'Xoá khỏi yêu thích' : 'Thêm vào yêu thích';
}

/* ═══════════════════════════════════════════════════════════════
   NÚT TOGGLE "CHỈ CÂU YÊU THÍCH"
   ═══════════════════════════════════════════════════════════════ */
function favUpdatePfOnlyFavBtn() {
    var btn = document.getElementById('pfFavOnlyBtn');
    if (!btn) return;

    var icon = btn.querySelector('i');
    var countEl = document.getElementById('pfFavOnlyCount');
    var can = favCanUse();
    var count = favCount();   /* ⭐ Đếm TỔNG */

    /* ═══ 1. CHƯA ĐỦ QUYỀN ═══ */
    if (!can) {
        btn.classList.add('locked');
        btn.classList.remove('active', 'empty', 'current-not-fav');
        if (icon) icon.className = 'fas fa-lock';
        btn.title = 'Cần gia hạn để dùng Yêu thích';
        if (countEl) countEl.textContent = '0';
        return;
    }

    btn.classList.remove('locked', 'current-not-fav');
    if (countEl) countEl.textContent = count;

    /* ═══ 2. CHƯA CÓ CÂU YÊU THÍCH NÀO ═══ */
    if (count === 0) {
        btn.classList.add('empty');
        btn.classList.remove('active');
        if (icon) icon.className = 'far fa-heart';
        btn.title = 'Chưa có câu yêu thích nào';
        if (favState.pfOnlyFav) favState.pfOnlyFav = false;
        return;
    }

    btn.classList.remove('empty');

    /* ═══ 3. CẬP NHẬT THEO TRẠNG THÁI TOGGLE ═══ */
    if (favState.pfOnlyFav) {
        btn.classList.add('active');
        if (icon) icon.className = 'fas fa-heart';
        btn.title = 'Đang chỉ luyện câu yêu thích — bấm để tắt';
    } else {
        btn.classList.remove('active');
        if (icon) icon.className = 'far fa-heart';
        btn.title = 'Chỉ luyện câu yêu thích';
    }
}

function favTogglePfOnlyFav() {
    if (!favCanUse()) { favShowLockDialog(); return; }

    var currentDsId = favGetCurrentDsId();
    var totalCount = favCount();

    /* ═══════════════════════════════════════════════════════════
       ⭐ TRƯỜNG HỢP 1: ĐANG BẬT → TẮT
       ═══════════════════════════════════════════════════════════ */
    if (favState.pfOnlyFav) {
        favState.pfOnlyFav = false;
        favUpdatePfOnlyFavBtn();
        favRefreshQuestionDropdown();

        if (typeof pfBuildQuickNav === 'function') {
            try { pfBuildQuickNav(); } catch(e) {}
        }

        favShowToast('Luyện tất cả câu', 'remove');
        return;
    }

    /* ═══════════════════════════════════════════════════════════
       ⭐ TRƯỜNG HỢP 2: ĐANG TẮT → BẬT
       ═══════════════════════════════════════════════════════════ */
    if (totalCount === 0) {
        favShowToast('Chưa có câu yêu thích nào', 'warn');
        return;
    }

    favState.pfOnlyFav = true;
    favUpdatePfOnlyFavBtn();
    favRefreshQuestionDropdown();

    /* ⭐ Nếu câu hiện tại KHÔNG phải yêu thích → tự nhảy sang fav đầu tiên */
    var currentStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                     ? String(pfCurrentStt)
                     : null;
    var currentIsFav = currentStt ? favHas(currentStt, currentDsId) : false;

    if (!currentIsFav) {
        var favList = favGetRecords();
        if (favList.length > 0) {
            var firstFavStt = String(favList[0].stt);
            if (typeof loadPracticeFull === 'function') {
                loadPracticeFull(firstFavStt);
            }
        }
    }

    favShowToast('Chỉ luyện ' + totalCount + ' câu yêu thích', 'add');
}

/* ═══════════════════════════════════════════════════════════════
   SCAN ALL HEART BUTTONS
   ═══════════════════════════════════════════════════════════════ */
function favScanAllHeartButtons() {
    var can = (typeof favCanUse === 'function') ? favCanUse() : false;
    var currentDsId = favGetCurrentDsId();

    document.querySelectorAll('.fav-btn[data-stt]').forEach(function(btn) {
        var stt = btn.dataset.stt;
        if (!stt) return;

        var btnDsId = btn.dataset.datasetId || currentDsId;
        var active = (typeof favHas === 'function') ? favHas(stt, btnDsId) : false;
        var icon = btn.querySelector('i');

        if (!can) {
            btn.classList.add('locked');
            btn.classList.remove('active');
            if (icon) icon.className = 'fas fa-lock';
            btn.title = 'Cần gia hạn để dùng Yêu thích';
            return;
        }

        btn.classList.remove('locked');
        btn.classList.toggle('active', active);
        if (icon) {
            icon.className = active ? 'fas fa-heart' : 'far fa-heart';
        }
        btn.title = active ? 'Xoá khỏi yêu thích' : 'Thêm vào yêu thích';
    });

    if (typeof favUpdatePfFloatBtn === 'function') {
        favUpdatePfFloatBtn();
    }
    if (typeof favUpdatePfOnlyFavBtn === 'function') {
        favUpdatePfOnlyFavBtn();
    }
}

/* ═══════════════════════════════════════════════════════════════
   NOTIFY CHANGES
   ═══════════════════════════════════════════════════════════════ */
function favNotifyChanged() {
    /* ⭐ Quét lại tất cả nút tim */
    if (typeof favScanAllHeartButtons === 'function') {
        favScanAllHeartButtons();
    }

    /* ⭐ Cập nhật badge trên tab + dropdown */
    var count = favCount();
    ['favTabBadge', 'favDropdownBadge'].forEach(function(id) {
        var badge = document.getElementById(id);
        if (badge) {
            badge.textContent = count;
            badge.dataset.count = count;
        }
    });

    /* ⭐⭐ CẬP NHẬT HEADER COUNT ngay (không cần chờ render) */
    var headerCountEl = document.querySelector('.fav-header .fav-count-text');
    if (headerCountEl) {
        headerCountEl.textContent = count + ' câu';
    }

    /* ⭐⭐⭐ Nếu đang ở tab Yêu thích → render lại NGAY */
    if (favState.currentView && favState.filteringOnly) {
        if (typeof window.render === 'function') {
            clearTimeout(favState.__renderTimer);
            favState.__renderTimer = setTimeout(function() {
                window.render();
                /* Backup: cập nhật lại header sau khi render */
                setTimeout(function() {
                    var el = document.querySelector('.fav-header .fav-count-text');
                    if (el) el.textContent = favCount() + ' câu';
                }, 20);
            }, 80);
        } else {
            favRenderCurrentTab();
            setTimeout(function() {
                var el = document.querySelector('.fav-header .fav-count-text');
                if (el) el.textContent = favCount() + ' câu';
            }, 20);
        }
    }
}
/* ═══════════════════════════════════════════════════════════════
   UPDATE LOCK STATE
   ═══════════════════════════════════════════════════════════════ */
function favUpdateLockState() {
    var can = favCanUse();

    var favTab = document.getElementById('dsFavBtn');
    if (favTab) {
        favTab.classList.toggle('fav-locked', !can);
        var lockEl = document.getElementById('favTabLock');
        var badgeEl = document.getElementById('favTabBadge');
        if (can) {
            if (lockEl) lockEl.style.display = 'none';
            if (badgeEl) badgeEl.style.display = '';
        } else {
            if (lockEl) lockEl.style.display = 'flex';
            if (badgeEl) badgeEl.style.display = 'none';
        }
    }

    var favDd = document.getElementById('dsFavDropdownItem');
    if (favDd) {
        favDd.classList.toggle('fav-locked', !can);
        var ddLock = document.getElementById('favDropdownLock');
        var ddBadge = document.getElementById('favDropdownBadge');
        if (can) {
            if (ddLock) ddLock.style.display = 'none';
            if (ddBadge) ddBadge.style.display = '';
        } else {
            if (ddLock) ddLock.style.display = 'inline-flex';
            if (ddBadge) ddBadge.style.display = 'none';
        }
    }

    var currentDsId = favGetCurrentDsId();
    document.querySelectorAll('.fav-btn[data-stt]').forEach(function(btn) {
        var icon = btn.querySelector('i');
        var btnDsId = btn.dataset.datasetId || currentDsId;
        if (can) {
            btn.classList.remove('locked');
            var active = favHas(btn.dataset.stt, btnDsId);
            btn.classList.toggle('active', active);
            if (icon) {
                icon.className = active ? 'fas fa-heart' : 'far fa-heart';
            }
            btn.title = active ? 'Xoá khỏi yêu thích' : 'Thêm vào yêu thích';
        } else {
            btn.classList.add('locked');
            btn.classList.remove('active');
            if (icon) icon.className = 'fas fa-lock';
            btn.title = 'Cần gia hạn để dùng Yêu thích';
        }
    });

    favUpdatePfFloatBtn();
    favUpdatePfOnlyFavBtn();

    if (!can && favState.currentView) {
        favExitFilterMode();
        if (typeof switchDataset === 'function') switchDataset('tonghop');
        if (typeof markCurrentDatasetActive === 'function') markCurrentDatasetActive();
    }
}

/* ═══════════════════════════════════════════════════════════════
   TOAST
   ═══════════════════════════════════════════════════════════════ */
function favShowToast(message, type) {
    var old = document.getElementById('favToast');
    if (old) old.remove();

    var toast = document.createElement('div');
    toast.id = 'favToast';
    toast.className = 'fav-toast ' + (type || 'add');

    var iconClass = 'fa-heart';
    if (type === 'remove') iconClass = 'fa-heart-broken';
    if (type === 'warn') iconClass = 'fa-info-circle';

    toast.innerHTML = '<i class="fas ' + iconClass + '"></i><span>' + message + '</span>';
    document.body.appendChild(toast);

    requestAnimationFrame(function() { toast.classList.add('show'); });
    setTimeout(function() {
        toast.classList.remove('show');
        setTimeout(function() { if (toast.parentNode) toast.remove(); }, 300);
    }, 1800);
}

/* ═══════════════════════════════════════════════════════════════
   RENDER TAB YÊU THÍCH
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   RENDER TAB YÊU THÍCH
   - Đếm đúng số câu (allFavRecords.length)
   - Header có class "fav-count-text" để update trực tiếp
   - Empty state khi hết câu
   ═══════════════════════════════════════════════════════════════ */
function favRenderCurrentTab() {
    if (!favState.currentView) return;
    if (typeof mobileWrapper === 'undefined' || !mobileWrapper) return;
    if (typeof RAW_DATA === 'undefined' || !RAW_DATA) return;

    var can = favCanUse();

    /* ═══ 1. KHÔNG CÓ QUYỀN → LOCK STATE ═══ */
    if (!can) {
        mobileWrapper.innerHTML = '<div class="fav-locked-empty">' +
            '<div style="width:70px;height:70px;margin:0 auto 1rem;border-radius:50%;' +
            'background:linear-gradient(135deg,#dc2626,#b91c1c);color:#fff;' +
            'display:flex;align-items:center;justify-content:center;font-size:1.8rem;">' +
                '<i class="fas fa-lock"></i>' +
            '</div>' +
            '<div style="font-size:1.05rem;font-weight:800;margin-bottom:.4rem;color:#dc2626;">' +
                'Tính năng Yêu thích đang bị khoá' +
            '</div>' +
            '<div style="font-size:.85rem;color:var(--text-2);line-height:1.5;max-width:420px;margin:0 auto;">' +
                (favIsLoggedIn()
                    ? 'Chỉ tài khoản <b>đã gia hạn</b> mới lưu được câu yêu thích và đồng bộ trên mọi thiết bị.'
                    : 'Vui lòng <b>đăng nhập</b> và <b>gia hạn</b> để dùng tính năng này.') +
            '</div>' +
            '<button style="margin-top:1rem;padding:.6rem 1.2rem;border-radius:50px;border:none;' +
            'background:linear-gradient(135deg,#dc2626,#b91c1c);color:#fff;font-weight:800;cursor:pointer;' +
            'font-family:inherit;text-transform:uppercase;letter-spacing:.3px;" ' +
            'onclick="favShowLockDialog()">' +
                '<i class="fas ' + (favIsLoggedIn() ? 'fa-gem' : 'fa-sign-in-alt') + '"></i>' +
                (favIsLoggedIn() ? ' Gia hạn ngay' : ' Đăng nhập ngay') +
            '</button>' +
        '</div>';
        return;
    }

    /* ═══════════════════════════════════════════════════════════
       ⭐ 2. LẤY TẤT CẢ CÂU YÊU THÍCH — KHÔNG FILTER DATASET
       ═══════════════════════════════════════════════════════════ */
    var allFavRecords = favGetRecords();

    /* ═══ 3. EMPTY STATE — Không còn câu nào ═══ */
    if (allFavRecords.length === 0) {
        mobileWrapper.innerHTML = '<div class="fav-empty">' +
            '<div class="fav-empty-icon"><i class="far fa-heart"></i></div>' +
            '<div class="fav-empty-title">Chưa có câu yêu thích nào</div>' +
            '<div class="fav-empty-desc">' +
                'Bấm vào biểu tượng <b>❤️ trái tim</b> trên mỗi câu để lưu lại. ' +
                'Các câu yêu thích sẽ được đồng bộ trên mọi thiết bị khi bạn đăng nhập.' +
            '</div>' +
        '</div>';

        /* ⭐ Cập nhật badge = 0 ngay */
        ['favTabBadge', 'favDropdownBadge'].forEach(function(id) {
            var b = document.getElementById(id);
            if (b) { b.textContent = '0'; b.dataset.count = '0'; }
        });

        return;
    }

    /* ═══ 4. COUNTER + HEADER ═══ */
    var isAdminUser = (typeof currentUser !== 'undefined'
                       && currentUser
                       && currentUser.role === 'admin');
    var counterHtml = '';

    if (isAdminUser) {
        counterHtml = '<span style="font-size:.7rem;font-weight:700;color:#7c3aed;' +
                      'padding:.15rem .55rem;background:rgba(124,58,237,.12);border-radius:50px;' +
                      'display:inline-flex;align-items:center;gap:.25rem;">' +
                      '<i class="fas fa-infinity"></i> Admin không giới hạn</span>';
    } else {
        var used = (typeof favGetDailyUsed === 'function') ? favGetDailyUsed() : 0;
        var MAX_PER_DAY = 500;
        var color = used >= 450 ? '#dc2626' : (used >= 350 ? '#f59e0b' : '#16a34a');
        var bgColor = used >= 450 ? 'rgba(220,38,38,.15)' :
                      used >= 350 ? 'rgba(245,158,11,.15)' : 'rgba(22,163,74,.12)';
        counterHtml = '<span style="font-size:.7rem;font-weight:700;color:' + color + ';' +
                      'padding:.15rem .55rem;background:' + bgColor + ';border-radius:50px;' +
                      'display:inline-flex;align-items:center;gap:.25rem;">' +
                      '<i class="fas fa-calendar-day"></i> ' + used + '/' + MAX_PER_DAY + ' hôm nay</span>';
    }

    /* ⭐ Header — dùng class "fav-count-text" để có thể update trực tiếp */
    var headerHtml = '<div class="fav-header" style="grid-column:1 / -1;' +
        'display:flex;align-items:center;gap:.5rem;padding:.65rem .85rem;' +
        'background:linear-gradient(135deg,rgba(239,68,68,.08),rgba(220,38,38,.04));' +
        'border:1.5px solid rgba(239,68,68,.25);border-radius:12px;margin-bottom:.75rem;flex-wrap:wrap;">' +
        '<div style="display:flex;align-items:center;gap:.45rem;font-size:.88rem;font-weight:800;flex:1 1 auto;flex-wrap:wrap;">' +
            '<i class="fas fa-heart" style="color:#ef4444;"></i>' +
            '<span>Yêu thích</span>' +
            '<span class="fav-count-text" style="font-size:.72rem;font-weight:700;color:#dc2626;' +
            'background:rgba(239,68,68,.15);padding:.15rem .55rem;border-radius:50px;">' +
                allFavRecords.length + ' câu</span>' +
            counterHtml +
        '</div>' +
        '<select onchange="favOnSortChange(this.value)" ' +
        'style="padding:.35rem 1.8rem .35rem .7rem;border-radius:50px;border:1.5px solid var(--border);' +
        'background:var(--surface);color:var(--text);font-size:.72rem;font-weight:700;cursor:pointer;' +
        'font-family:inherit;outline:none;">' +
            '<option value="recent"' + (favState.sortMode === 'recent' ? ' selected' : '') + '>Mới nhất</option>' +
            '<option value="oldest"' + (favState.sortMode === 'oldest' ? ' selected' : '') + '>Cũ nhất</option>' +
            '<option value="stt"' + (favState.sortMode === 'stt' ? ' selected' : '') + '>Theo STT</option>' +
        '</select>' +
        '<button onclick="favClearAll()" ' +
        'style="padding:.35rem .75rem;border-radius:50px;border:1.5px solid rgba(220,38,38,.35);' +
        'background:var(--surface);color:#dc2626;font-size:.72rem;font-weight:700;cursor:pointer;' +
        'font-family:inherit;display:inline-flex;align-items:center;gap:.3rem;">' +
            '<i class="fas fa-trash-alt"></i> Xoá hết' +
        '</button>' +
    '</div>';

    /* ═══ 5. FILTER theo search / hsk / subject ═══ */
    var filteredFav = allFavRecords.filter(function(r) {
        if (typeof state !== 'undefined') {
            if (state.search) {
                var s = state.search;
                var inVi = (r.vi || '').toLowerCase().indexOf(s) !== -1;
                var inZh = (r.zh || '').toLowerCase().indexOf(s) !== -1;
                var inPinyin = (r.pinyin || '').toLowerCase().indexOf(s) !== -1;
                var inTopic = (r.topic || '').toLowerCase().indexOf(s) !== -1;
                var inSubject = (r.subject || '').toLowerCase().indexOf(s) !== -1;
                if (!inVi && !inZh && !inPinyin && !inTopic && !inSubject) return false;
            }
            if (state.hsk && r.hsk !== state.hsk) return false;
            if (state.subject && r.subject !== state.subject) return false;
        }
        return true;
    });

    /* ═══ 6. SORT ═══ */
    var sortMode = favState.sortMode || 'recent';
    if (sortMode === 'oldest') {
        filteredFav.sort(function(a, b) {
            return (a.__favAddedAt || 0) - (b.__favAddedAt || 0);
        });
    } else if (sortMode === 'stt') {
        filteredFav.sort(function(a, b) {
            var na = parseInt(a.stt) || 0;
            var nb = parseInt(b.stt) || 0;
            return na - nb;
        });
    } else {
        /* recent */
        filteredFav.sort(function(a, b) {
            return (b.__favAddedAt || 0) - (a.__favAddedAt || 0);
        });
    }

    /* ═══ 7. RENDER ═══ */
    var cardsHtml = headerHtml;

    if (filteredFav.length === 0) {
        cardsHtml += '<div class="no-data" style="grid-column:1 / -1;">' +
            '<i class="fas fa-search"></i>Không tìm thấy câu yêu thích nào khớp bộ lọc' +
            '</div>';
    } else {
        filteredFav.forEach(function(r) {
            cardsHtml += favBuildCardHtml(r);
        });
    }

    mobileWrapper.innerHTML = cardsHtml;

    /* ═══ 8. UPDATE LOCK STATE + SYNC HEADER + BADGE ═══ */
    setTimeout(function() {
        if (typeof favUpdateLockState === 'function') favUpdateLockState();

        /* ⭐ Sync lại header count sau render (chống race condition) */
        var headerCountEl = document.querySelector('.fav-header .fav-count-text');
        if (headerCountEl) {
            headerCountEl.textContent = favCount() + ' câu';
        }

        /* ⭐ Sync badge */
        var total = favCount();
        ['favTabBadge', 'favDropdownBadge'].forEach(function(id) {
            var b = document.getElementById(id);
            if (b) {
                b.textContent = total;
                b.dataset.count = total;
            }
        });
    }, 50);
}
function favBuildCardHtml(r) {
    var zhJs = escapeJs(r.zh);
    var viJs = escapeJs(r.vi);
    var pinyinJs = escapeJs(r.pinyin);
    var zhHtml = escapeHtml(r.zh);
    var viHtml = escapeHtml(r.vi);
    var sttSafe = escapeHtml(r.stt);
    var sttJs = escapeJs(r.stt);

    var itemDsId = r.__favDatasetId
                   || (typeof CURRENT_DATASET !== 'undefined' && CURRENT_DATASET)
                   || 'tonghop';
    var dsSafe = escapeHtml(itemDsId);

    var audio = r.zh ? '<button class="audio-btn" onclick="speakText(\'' + zhJs + '\', this, event)" title="Nghe"><i class="fas fa-volume-up"></i></button>' : '';
    var writeBtn = '';
    if (r.zh) {
        writeBtn = '<button class="write-btn" onclick="openWriter(\'' + zhJs + '\', \'' + viJs + '\', \'' + pinyinJs + '\', event)" title="Luyện viết"><i class="fas fa-pen-fancy"></i></button>';
    }
    var fullBtn = '';
    if (r.zh) {
        fullBtn = '<button class="practice-full-btn" onclick="openPracticeFull(\'' + sttJs + '\', event)" title="Luyện tập full màn hình"><i class="fas fa-expand"></i></button>';
    }

    var can = favCanUse();
    var active = favHas(r.stt, itemDsId);

    var favBtn = '<button class="fav-btn' +
        (active ? ' active' : '') +
        (!can ? ' locked' : '') +
        '" data-stt="' + sttSafe + '" ' +
        'data-dataset-id="' + dsSafe + '" ' +
        'onclick="favOnCardBtnClick(event, \'' + sttJs + '\')" ' +
        'title="' + (active ? 'Xoá khỏi yêu thích' : 'Thêm vào yêu thích') + '">' +
        '<i class="' + (!can ? 'fas fa-lock' : (active ? 'fas fa-heart' : 'far fa-heart')) + '"></i>' +
    '</button>';

    var practiceInput = '<input type="text" class="practice-input" placeholder="Gõ tiếng Trung..." data-answer="' + zhHtml + '" data-stt="' + sttSafe + '" oninput="checkInput(this)" autocomplete="off">';

    return '<div class="card" data-hsk="' + (r.hsk || '') + '" onclick="toggleFocus(\'' + sttJs + '\', this)" data-stt="' + sttSafe + '">' +
        '<div class="card-header">' +
            '<div class="card-stt">' + sttSafe + '</div>' +
            '<div class="card-meta">' +
                (r.hsk ? '<span class="card-tag hsk">' + escapeHtml(r.hsk) + '</span>' : '') +
            '</div>' +
            '<div onclick="event.stopPropagation()" class="action-group">' +
                audio + writeBtn + fullBtn + favBtn +
            '</div>' +
        '</div>' +
        '<div class="card-body">' +
            (r.vi ? '<div class="card-vi">' + viHtml + '</div>' : '') +
            '<div class="card-zh">' + zhHtml + '</div>' +
            (r.pinyin ? '<div class="card-pinyin">' + escapeHtml(r.pinyin) + '</div>' : '') +
        '</div>' +
        '<div class="card-practice" onclick="event.stopPropagation()">' +
            practiceInput +
        '</div>' +
    '</div>';
}

/* ═══════════════════════════════════════════════════════════════
   EVENT HANDLERS
   ═══════════════════════════════════════════════════════════════ */
window.favOnCardBtnClick = function(evt, stt) {
    evt.stopPropagation();
    if (evt.preventDefault) evt.preventDefault();

    if (!favCanUse()) { favShowLockDialog(); return; }

    var btnDsId = null;
    if (evt && evt.currentTarget) {
        btnDsId = evt.currentTarget.dataset.datasetId || null;
    }

    var currentDsId = btnDsId || favGetCurrentDsId();

    var record = null;
    if (typeof favFindRecordInDataset === 'function') {
        record = favFindRecordInDataset(currentDsId, stt);
    }
    if (!record && typeof favFindRecordAnywhere === 'function') {
        record = favFindRecordAnywhere(stt);
    }

    favToggle(stt, record, currentDsId);
};

window.favOnPfBtnClick = function(evt) {
    if (evt) { evt.stopPropagation(); if (evt.preventDefault) evt.preventDefault(); }
    if (typeof pfCurrentStt === 'undefined' || !pfCurrentStt) return;
    if (!favCanUse()) { favShowLockDialog(); return; }

    var stt = String(pfCurrentStt);
    var currentDsId = favGetCurrentDsId();

    var record = null;
    if (typeof favFindRecordInDataset === 'function') {
        record = favFindRecordInDataset(currentDsId, stt);
    }
    if (!record && typeof favFindRecordAnywhere === 'function') {
        record = favFindRecordAnywhere(stt);
    }

    favToggle(stt, record, currentDsId).then(function() {
        favUpdatePfFloatBtn();
    });
};

window.favTogglePfOnlyFav = favTogglePfOnlyFav;

window.favOnSortChange = function(mode) {
    favState.sortMode = mode || 'recent';
    try { localStorage.setItem('favSortMode', favState.sortMode); } catch(e) {}
    if (typeof window.render === 'function') window.render();
    else favRenderCurrentTab();
};

/* ═══════════════════════════════════════════════════════════════
   CLICK TAB YÊU THÍCH
   ═══════════════════════════════════════════════════════════════ */
function favOnTabClick(evt) {
    if (evt) { evt.stopPropagation(); if (evt.preventDefault) evt.preventDefault(); }

    if (!favCanUse()) { favShowLockDialog(); return; }

    document.querySelectorAll('.ds-btn').forEach(function(b) { b.classList.remove('active'); });
    document.querySelectorAll('.ds-sub-btn').forEach(function(b) { b.classList.remove('active'); });
    document.querySelectorAll('.ds-dropdown-item').forEach(function(b) { b.classList.remove('active'); });

    var tabBtn = document.getElementById('dsFavBtn');
    if (tabBtn) tabBtn.classList.add('active');
    var ddBtn = document.getElementById('dsFavDropdownItem');
    if (ddBtn) ddBtn.classList.add('active');

    var subWrap = document.getElementById('dsSubWrap');
    if (subWrap) subWrap.style.display = 'none';

    favState.currentView = true;
    favState.filteringOnly = true;

    if (typeof state !== 'undefined') {
        state.search = '';
        state.hsk = '';
        state.subject = '';
    }
    try {
        var si = document.getElementById('searchInput');
        if (si) si.value = '';
        var hf = document.getElementById('hskFilter');
        if (hf) hf.value = '';
        var sf = document.getElementById('subjectFilter');
        if (sf) sf.value = '';
        var cb = document.getElementById('clearSearchBtn');
        if (cb) cb.classList.remove('show');
    } catch(e) {}
    if (typeof updateFilterUI === 'function') updateFilterUI();

    window.__onboardingOverride = null;
    var obBanner = document.getElementById('onboardingActiveBanner');
    if (obBanner) obBanner.style.display = 'none';

    var favRecords = favGetRecords();

    try {
        filtered = favRecords;
    } catch(e1) {
        try { window.filtered = favRecords; } catch(e2) {}
    }
    try { window.filtered = favRecords; } catch(e) {}

    try { renderedCount = 0; } catch(e) { try { window.renderedCount = 0; } catch(e2) {} }

    if (typeof favRenderCurrentTab === 'function') {
        favRenderCurrentTab();
    } else if (typeof window.render === 'function') {
        window.render(true);
    }

    setTimeout(function() {
        var mainEl = document.getElementById('mainContent');
        if (mainEl) {
            var yOffset = mainEl.getBoundingClientRect().top + window.scrollY - 100;
            window.scrollTo({ top: yOffset, behavior: 'smooth' });
        }
    }, 150);

    if (favCanUse() && !favState.loaded) {
        favLoadFromCloud();
    }
}

function favExitFilterMode() {
    if (!favState.filteringOnly) return;
    favState.filteringOnly = false;
    favState.currentView = false;
    favState.pfOnlyFav = false;
    var tabBtn = document.getElementById('dsFavBtn');
    if (tabBtn) tabBtn.classList.remove('active');
    var ddBtn = document.getElementById('dsFavDropdownItem');
    if (ddBtn) ddBtn.classList.remove('active');
    if (typeof favUpdatePfOnlyFavBtn === 'function') favUpdatePfOnlyFavBtn();
}

/* ═══════════════════════════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════════════════════════ */
function initFavorites() {
    try {
        var savedSort = localStorage.getItem('favSortMode');
        if (savedSort) favState.sortMode = savedSort;
    } catch(e) {}

    favLoadFromLocal();

    var pfBtn = document.getElementById('pfFavBtn');
    if (pfBtn && !pfBtn.__favBound) {
        pfBtn.__favBound = true;
        pfBtn.addEventListener('click', window.favOnPfBtnClick);
    }

    var pfOnlyBtn = document.getElementById('pfFavOnlyBtn');
    if (pfOnlyBtn && !pfOnlyBtn.__favBound) {
        pfOnlyBtn.__favBound = true;
        pfOnlyBtn.addEventListener('click', function(evt) {
            evt.stopPropagation();
            if (evt.preventDefault) evt.preventDefault();
            favTogglePfOnlyFav();
        });
    }

    var favTab = document.getElementById('dsFavBtn');
    if (favTab && !favTab.__favBound) {
        favTab.__favBound = true;
        favTab.addEventListener('click', favOnTabClick);
    }

    var favDd = document.getElementById('dsFavDropdownItem');
    if (favDd && !favDd.__favBound) {
        favDd.__favBound = true;
        favDd.addEventListener('click', function(evt) {
            if (evt) { evt.stopPropagation(); if (evt.preventDefault) evt.preventDefault(); }
            var dd = favDd.closest('.ds-dropdown, .dataset-dropdown, [class*="dropdown"]');
            if (dd) dd.classList.remove('show', 'open');
            favOnTabClick(evt);
        });
    }

    favUpdateLockState();
    if (favCanUse()) favLoadFromCloud();
    favNotifyChanged();
    favSyncFloatVisibility();
}

/* ═══════════════════════════════════════════════════════════════
   FLOAT VISIBILITY
   ═══════════════════════════════════════════════════════════════ */
function favSyncFloatVisibility() {
    var pfModal = document.getElementById('practiceFullModal');
    var pfFavFloat = document.getElementById('pfFavBtn');
    var pfOnlyFloat = document.getElementById('pfFavOnlyBtn');

    var isOpen = pfModal && pfModal.classList.contains('show');

    if (isOpen) {
        if (pfFavFloat) {
            pfFavFloat.classList.add('show');
            pfFavFloat.style.display = 'inline-flex';
        }
        if (pfOnlyFloat) {
            pfOnlyFloat.classList.add('show');
            pfOnlyFloat.style.display = 'inline-flex';
        }

        favUpdatePfFloatBtn();
        favUpdatePfOnlyFavBtn();

        setTimeout(function() {
            favRefreshQuestionDropdown();
        }, 80);

        /* ⭐ Nếu toggle BẬT + câu hiện tại KHÔNG phải fav → tự nhảy fav đầu */
        if (favState.pfOnlyFav && favCanUse()) {
            setTimeout(function() {
                var curStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                             ? String(pfCurrentStt)
                             : null;
                if (!curStt) return;

                var curDs = favGetCurrentDsId();
                var isFav = favHas(curStt, curDs);

                if (!isFav) {
                    var favList = favGetRecords();
                    if (favList.length > 0) {
                        var firstFavStt = String(favList[0].stt);
                        if (firstFavStt !== curStt && !window.__favRedirecting) {
                            window.__favRedirecting = true;
                            setTimeout(function() {
                                if (typeof loadPracticeFull === 'function') {
                                    loadPracticeFull(firstFavStt);
                                }
                                window.__favRedirecting = false;
                            }, 30);
                        }
                    }
                }
            }, 120);
        }

    } else {
        if (pfFavFloat) {
            pfFavFloat.classList.remove('show');
            pfFavFloat.style.display = 'none';
        }
        if (pfOnlyFloat) {
            pfOnlyFloat.classList.remove('show');
            pfOnlyFloat.style.display = 'none';
        }
    }
}

/* ═══════════════════════════════════════════════════════════════
   WATCH PRACTICE FULL MODAL
   ═══════════════════════════════════════════════════════════════ */

/* [PHẦN TRƯỚC GIỮ NGUYÊN — từ đầu file đến hết favSyncFloatVisibility] */

/* ═══════════════════════════════════════════════════════════════
   WATCH PRACTICE FULL MODAL
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   WATCH PRACTICE FULL MODAL
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function attach() {
        var pfModal = document.getElementById('practiceFullModal');
        if (!pfModal) return false;
        if (pfModal.__favObserved) return true;
        pfModal.__favObserved = true;

        var obs = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                if (m.attributeName === 'class') {
                    if (typeof favSyncFloatVisibility === 'function') {
                        favSyncFloatVisibility();
                    }
                }
            });
        });
        obs.observe(pfModal, { attributes: true });
        return true;
    }

    if (!attach()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (attach() || _tries > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   THEO DÕI pfCurrentStt — KHÔNG tự tắt toggle
   ═══════════════════════════════════════════════════════════════ */
(function() {
    var _lastPfStt = null;

    function syncPfState() {
        var cur = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                  ? String(pfCurrentStt)
                  : null;
        if (cur === _lastPfStt) return;
        _lastPfStt = cur;
        if (!cur) return;

        if (typeof favUpdatePfFloatBtn === 'function') {
            favUpdatePfFloatBtn();
        }
        if (typeof favUpdatePfOnlyFavBtn === 'function') {
            favUpdatePfOnlyFavBtn();
        }
        if (typeof favScanAllHeartButtons === 'function') {
            favScanAllHeartButtons();
        }
    }

    setInterval(syncPfState, 250);
})();

/* ═══════════════════════════════════════════════════════════════
   PATCH render()
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.render !== 'function') return false;
        if (window.render.__favScanPatched) return true;

        var _origRender = window.render;
        window.render = function() {
            var result = _origRender.apply(this, arguments);
            setTimeout(function() {
                if (typeof favScanAllHeartButtons === 'function') {
                    favScanAllHeartButtons();
                }
            }, 10);
            return result;
        };
        window.render.__favScanPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (tryPatch() || _tries > 40) clearInterval(_iv);
        }, 100);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   PATCH switchDataset()
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH loadPracticeFull
   - KHÔNG auto-nhảy khi user chủ động chọn câu từ dropdown
   - Skip hoàn toàn nếu __favManualNav (user bấm trực tiếp)
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.loadPracticeFull !== 'function') return false;
        if (window.loadPracticeFull.__favUnifiedPatched) return true;

        var _origLoadPF = window.loadPracticeFull;
        window.loadPracticeFull = function(stt) {
            var result = _origLoadPF.apply(this, arguments);

            setTimeout(function() {
                var newStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                             ? String(pfCurrentStt)
                             : null;
                if (!newStt) return;

                if (typeof favScanAllHeartButtons === 'function') {
                    favScanAllHeartButtons();
                }
                if (typeof favUpdatePfOnlyFavBtn === 'function') {
                    favUpdatePfOnlyFavBtn();
                }

                /* ═══ ⭐ BỎ QUA AUTO-NHẢY khi user chủ động ═══ */
                if (window.__favManualNav) {
                    console.log('[Favorites] Manual nav — bỏ qua auto-nhảy');
                    if (typeof favRefreshQuestionDropdown === 'function') {
                        favRefreshQuestionDropdown();
                    }
                    return;
                }

                /* ═══ Đang redirect → bỏ qua ═══ */
                if (window.__favRedirecting) {
                    if (typeof favRefreshQuestionDropdown === 'function') {
                        favRefreshQuestionDropdown();
                    }
                    return;
                }

                /* ═══ Toggle bật + câu mới không phải fav → nhảy fav đầu ═══ */
                if (favState.pfOnlyFav && favCanUse()) {
                    var curDs = favGetCurrentDsId();
                    var isNewFav = favHas(newStt, curDs);

                    if (!isNewFav) {
                        var favList = favFilterRecords(favGetRecords());
                        if (favList.length > 0) {
                            var firstFavStt = String(favList[0].stt);

                            if (firstFavStt !== newStt) {
                                window.__favRedirecting = true;
                                setTimeout(function() {
                                    if (typeof loadPracticeFull === 'function') {
                                        loadPracticeFull(firstFavStt);
                                    }
                                    setTimeout(function() {
                                        window.__favRedirecting = false;
                                    }, 150);
                                }, 30);
                            }
                        }
                    }
                }

                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
            }, 50);

            return result;
        };
        window.loadPracticeFull.__favUnifiedPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (tryPatch() || _tries > 40) clearInterval(_iv);
        }, 100);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH pfBuildQuickNav — Build dropdown "CÂU:"
   - BẬT toggle: hiện TẤT CẢ câu yêu thích (mọi dataset) kèm data-dataset-id
   - TẮT toggle: gọi hàm gốc (dataset hiện tại)
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.pfBuildQuickNav !== 'function') return false;
        if (window.pfBuildQuickNav.__favPatched) return true;

        var _origBuildQuickNav = window.pfBuildQuickNav;
        window.pfBuildQuickNav = function() {
            var sel = document.getElementById('pfQuickNav');
            if (!sel) {
                return _origBuildQuickNav.apply(this, arguments);
            }

            /* ═══ KHÔNG BẬT TOGGLE → gọi hàm gốc ═══ */
            if (!favState.pfOnlyFav || !favCanUse()) {
                return _origBuildQuickNav.apply(this, arguments);
            }

            /* ═══════════════════════════════════════════════════════
               BẬT TOGGLE → Build dropdown từ TẤT CẢ câu yêu thích
               ═══════════════════════════════════════════════════════ */
            var favRecords = favGetRecords();
            var curStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                         ? String(pfCurrentStt)
                         : '';
            var curDs = favGetCurrentDsId();

            var html = '<option value="">-- Chọn câu yêu thích (' + favRecords.length + ') --</option>';

            for (var j = 0; j < favRecords.length; j++) {
                var r = favRecords[j];
                var vi = (r.vi || '').substring(0, 45);
                var sttRaw = (r.stt !== undefined && r.stt !== null && String(r.stt).trim() !== '')
                             ? '#' + String(r.stt).trim() + ' · '
                             : '';
                var dsTag = r.__favDatasetId && r.__favDatasetId !== curDs
                            ? '[' + r.__favDatasetId + '] '
                            : '';
                var label = dsTag + sttRaw + 'Câu ' + (j + 1) + ': ' + vi;

                var selected = (String(r.stt) === curStt && r.__favDatasetId === curDs)
                               ? ' selected'
                               : '';

                html += '<option value="' + String(r.stt) + '"' +
                        ' data-dataset-id="' + escapeHtml(r.__favDatasetId || '') + '"' +
                        selected + '>' +
                        escapeHtml(label) + '</option>';
            }

            sel.innerHTML = html;
            if (curStt) sel.value = curStt;
        };
        window.pfBuildQuickNav.__favPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (tryPatch() || _tries > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   ⭐ LISTENER pfQuickNav CHANGE — Tự chuyển dataset khi chọn câu
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   ⭐ LISTENER pfQuickNav CHANGE — Tự chuyển dataset khi chọn câu
   FIX: Dùng data-stt thay vì value, set __favManualNav chặn auto-redirect
   ═══════════════════════════════════════════════════════════════ */
(function() {
    var _navChanging = false;

    function attachListener() {
        var sel = document.getElementById('pfQuickNav');
        if (!sel) return false;
        if (sel.__favNavBound) return true;

        sel.__favNavBound = true;

        sel.addEventListener('change', function(evt) {
            if (!favState.pfOnlyFav || !favCanUse()) return;
            if (_navChanging) return;
            _navChanging = true;

            var opt = sel.options[sel.selectedIndex];
            if (!opt) { _navChanging = false; return; }

            /* ⭐ FIX: Đọc stt từ data-stt (chính xác) */
            var stt = opt.dataset.stt || '';
            var targetDs = opt.dataset.datasetId || null;

            /* Fallback: parse từ value "datasetId::stt" */
            if (!stt && opt.value && opt.value.indexOf('::') !== -1) {
                var parts = opt.value.split('::');
                targetDs = targetDs || parts[0];
                stt = parts[1];
            }

            if (!stt) { _navChanging = false; return; }

            var curDs = favGetCurrentDsId();

            /* ⭐⭐⭐ SET 2 CỜ: manual nav + redirecting */
            window.__favManualNav = true;
            window.__favRedirecting = true;

            /* ═══ Đổi dataset nếu cần ═══ */
            /* ═══ Đổi dataset nếu cần ═══ */
if (targetDs && targetDs !== curDs) {
    console.log('[Favorites] Đổi dataset: ' + curDs + ' → ' + targetDs);

    evt.stopPropagation();

    /* ⭐ DÙNG HÀM ĐẦY ĐỦ */
    if (typeof favSwitchDatasetFull === 'function') {
        favSwitchDatasetFull(targetDs);
    } else {
        /* Fallback */
        if (typeof window.__switchRawData === 'function') {
            try { window.__switchRawData(targetDs); } catch(e) {}
        }
    }

    setTimeout(function() {
        if (typeof loadPracticeFull === 'function') {
            loadPracticeFull(String(stt));
        }
        setTimeout(function() {
            window.__favRedirecting = false;
            window.__favManualNav = false;
            if (typeof favRefreshQuestionDropdown === 'function') {
                favRefreshQuestionDropdown();
            }
            _navChanging = false;
        }, 400);
    }, 120);
    return;
}

            /* ═══ Cùng dataset → load luôn ═══ */
            if (typeof loadPracticeFull === 'function') {
                loadPracticeFull(String(stt));
            }

            setTimeout(function() {
                window.__favRedirecting = false;
                window.__favManualNav = false;
                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
                _navChanging = false;
            }, 400);
        });

        console.log('✅ [Favorites] Đã gắn listener cho #pfQuickNav');
        return true;
    }

    if (!attachListener()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (attachListener() || _tries > 60) clearInterval(_iv);
        }, 200);
    }
})();
/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH __switchRawData — Không reset toggle khi tự đổi
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.__switchRawData !== 'function') return false;
        if (window.__switchRawData.__favPatched) return true;

        var _origSwitch = window.__switchRawData;
        window.__switchRawData = function(dsId) {
            var wasPfOnlyFav = favState.pfOnlyFav;

            var result = _origSwitch.apply(this, arguments);

            if (wasPfOnlyFav && favCanUse()) {
                favState.pfOnlyFav = true;
            }

            return result;
        };
        window.__switchRawData.__favPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (tryPatch() || _tries > 40) clearInterval(_iv);
        }, 100);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   PATCH các hàm build dropdown "CÂU:" khác (fallback)
   ═══════════════════════════════════════════════════════════════ */
(function() {
    var CANDIDATES = [
        'renderQuestionSelect',
        'buildQuestionDropdown',
        'updateQuestionList',
        'renderQuestionList',
        'buildQuestionSelect',
        'renderPfQuestionSelect',
        'renderQuestionPicker',
        'updateQuestionPicker',
        'refreshQuestionDropdown',
        'populateQuestionSelect',
        'renderPfQSelect'
    ];

    function patchFn(name) {
        if (typeof window[name] !== 'function') return false;
        if (window[name].__favDropdownPatched) return true;

        var _orig = window[name];
        window[name] = function() {
            if (!favState.pfOnlyFav || !favCanUse()) {
                return _orig.apply(this, arguments);
            }

            var _origRaw = (typeof RAW_DATA !== 'undefined') ? RAW_DATA : null;
            if (!_origRaw) return _orig.apply(this, arguments);

            try {
                var favRecords = favGetQuestionsForDropdown();
                window.__favOrigRawDataDD = _origRaw;
                try { RAW_DATA = favRecords; } catch(e) {}

                var result = _orig.apply(this, arguments);

                try { RAW_DATA = window.__favOrigRawDataDD; } catch(e) {}
                delete window.__favOrigRawDataDD;
                return result;
            } catch(e) {
                console.warn('[Favorites] ' + name + ' patch error:', e);
                try {
                    if (window.__favOrigRawDataDD) RAW_DATA = window.__favOrigRawDataDD;
                } catch(err) {}
                return _orig.apply(this, arguments);
            }
        };
        window[name].__favDropdownPatched = true;
        return true;
    }

    var _tries = 0;
    var _iv = setInterval(function() {
        _tries++;
        CANDIDATES.forEach(patchFn);
        if (_tries > 40) clearInterval(_iv);
    }, 150);
})();

/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH openPracticeFull
   - Auto-bật toggle khi mở từ tab Yêu thích
   - Bỏ filter khi đang __favRedirecting
   - Đổi dataset nếu fav đầu thuộc dataset khác
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.openPracticeFull !== 'function') return false;
        if (window.openPracticeFull.__favFilterPatched) return true;

        var _origOpenPF = window.openPracticeFull;
        window.openPracticeFull = function(stt, evt) {
            /* ⭐ AUTO-BẬT toggle khi mở từ tab Yêu thích */
            if (favCanUse() && favState.currentView && !favState.pfOnlyFav) {
                favState.pfOnlyFav = true;
            }

            /* ⭐ Nếu toggle bật + KHÔNG đang redirect → filter stt */
            if (favState.pfOnlyFav && favCanUse() && !window.__favRedirecting) {
                var favList = favGetRecords();
                if (favList.length === 0) {
                    favShowToast('Chưa có câu yêu thích nào', 'warn');
                    return;
                }

                var targetStt = String(stt);
                var curDs = favGetCurrentDsId();

                var isFav = favList.some(function(r) {
                    return String(r.stt) === targetStt &&
                           r.__favDatasetId === curDs;
                });

                if (!isFav) {
                    stt = String(favList[0].stt);

                    var firstDs = favList[0].__favDatasetId;
                    if (firstDs && firstDs !== curDs) {
                        window.__favRedirecting = true;
                        if (typeof window.__switchRawData === 'function') {
                            try { window.__switchRawData(firstDs); } catch(e) {}
                        }
                        var dsSel = document.getElementById('pfDatasetSelect');
                        if (dsSel) dsSel.value = firstDs;
                        if (typeof pfBuildFilterOptions === 'function') pfBuildFilterOptions();
                        if (typeof pfBuildDatasetSelect === 'function') pfBuildDatasetSelect();
                        setTimeout(function() {
                            window.__favRedirecting = false;
                        }, 150);
                    }
                }
            }

            var result = _origOpenPF.apply(this, arguments);

            setTimeout(function() {
                if (typeof favScanAllHeartButtons === 'function') {
                    favScanAllHeartButtons();
                }
                if (typeof favUpdatePfOnlyFavBtn === 'function') {
                    favUpdatePfOnlyFavBtn();
                }
                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
            }, 30);
            setTimeout(function() {
                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
            }, 200);

            return result;
        };
        window.openPracticeFull.__favFilterPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (tryPatch() || _tries > 40) clearInterval(_iv);
        }, 100);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH loadPracticeFull
   - KHÔNG tự tắt toggle
   - Bỏ auto-nhảy khi __favRedirecting
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH loadPracticeFull
   - BỎ QUA auto-nhảy nếu __favManualNav (user chủ động Next/Prev/dropdown)
   - BỎ QUA auto-nhảy nếu __favRedirecting (đang đổi dataset)
   - CHỈ auto-nhảy khi câu mới thực sự KHÔNG phải fav + có cờ cho phép
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.loadPracticeFull !== 'function') return false;
        if (window.loadPracticeFull.__favUnifiedPatched) return true;

        var _origLoadPF = window.loadPracticeFull;
        window.loadPracticeFull = function(stt) {
            var result = _origLoadPF.apply(this, arguments);

            setTimeout(function() {
                var newStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                             ? String(pfCurrentStt)
                             : null;
                if (!newStt) return;

                if (typeof favScanAllHeartButtons === 'function') {
                    favScanAllHeartButtons();
                }
                if (typeof favUpdatePfOnlyFavBtn === 'function') {
                    favUpdatePfOnlyFavBtn();
                }

                /* ═══════════════════════════════════════════════════
                   ⭐ FIX 1: BỎ QUA nếu user chủ động (Next/Prev/dropdown)
                   ═══════════════════════════════════════════════════ */
                if (window.__favManualNav) {
                    console.log('[Favorites] Manual nav — bỏ qua auto-nhảy');
                    if (typeof favRefreshQuestionDropdown === 'function') {
                        favRefreshQuestionDropdown();
                    }
                    return;
                }

                /* ═══════════════════════════════════════════════════
                   ⭐ FIX 2: BỎ QUA nếu đang redirect (đổi dataset)
                   ═══════════════════════════════════════════════════ */
                if (window.__favRedirecting) {
                    if (typeof favRefreshQuestionDropdown === 'function') {
                        favRefreshQuestionDropdown();
                    }
                    return;
                }

                /* ═══════════════════════════════════════════════════
                   ⭐ FIX 3: Chỉ auto-nhảy khi câu mới THỰC SỰ không phải fav
                   - Dùng favFilterRecords để check theo danh sách đã lọc
                   ═══════════════════════════════════════════════════ */
                if (favState.pfOnlyFav && favCanUse()) {
                    var curDs = favGetCurrentDsId();
                    var allFav = favGetRecords();
                    var filtered = favFilterRecords(allFav);

                    /* Câu mới có trong danh sách đã lọc không? */
                    var isInFiltered = false;
                    for (var i = 0; i < filtered.length; i++) {
                        if (String(filtered[i].stt) === newStt) {
                            isInFiltered = true;
                            break;
                        }
                    }

                    /* Nếu câu mới KHÔNG có trong list đã lọc → nhảy câu đầu */
                    if (!isInFiltered && filtered.length > 0) {
                        var firstFavStt = String(filtered[0].stt);

                        if (firstFavStt !== newStt) {
                            console.log('[Favorites] Auto-nhảy về câu đầu tiên của danh sách lọc');

                            window.__favRedirecting = true;

                            var firstDs = filtered[0].__favDatasetId;
                            if (firstDs && firstDs !== curDs) {
                                if (typeof window.__switchRawData === 'function') {
                                    try { window.__switchRawData(firstDs); } catch(e) {}
                                }
                                var dsSel = document.getElementById('pfDatasetSelect');
                                if (dsSel) dsSel.value = firstDs;
                                if (typeof pfBuildFilterOptions === 'function') pfBuildFilterOptions();
                                if (typeof pfBuildDatasetSelect === 'function') pfBuildDatasetSelect();
                            }

                            setTimeout(function() {
                                if (typeof loadPracticeFull === 'function') {
                                    loadPracticeFull(firstFavStt);
                                }
                                setTimeout(function() {
                                    window.__favRedirecting = false;
                                }, 150);
                            }, 30);
                        }
                    }
                }

                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
            }, 50);

            return result;
        };
        window.loadPracticeFull.__favUnifiedPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (tryPatch() || _tries > 40) clearInterval(_iv);
        }, 100);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   PATCH: ĐỔI BỘ DỮ LIỆU (#pfDatasetSelect.change)
   ═══════════════════════════════════════════════════════════════ */
(function() {
    'use strict';

    var _datasetChangeTimer = null;

    function handleDatasetChange() {
        console.log('[Favorites] Đổi bộ dữ liệu → đồng bộ');

        /* ⭐ Nếu đang redirect thì bỏ qua */
        if (window.__favRedirecting) {
            console.log('[Favorites] Đang redirect — bỏ qua handleDatasetChange');
            return;
        }

        if (typeof favState !== 'undefined') {
            favState.pfOnlyFav = false;
        }

        if (typeof favUpdatePfOnlyFavBtn === 'function') {
            favUpdatePfOnlyFavBtn();
        }

        if (typeof favRefreshQuestionDropdown === 'function') {
            favRefreshQuestionDropdown();
        }

        setTimeout(function() {
            if (typeof favScanAllHeartButtons === 'function') {
                favScanAllHeartButtons();
            }

            var newStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                         ? String(pfCurrentStt)
                         : null;
            var curDs = favGetCurrentDsId();
            var isNewFav = newStt && typeof favHas === 'function' ? favHas(newStt, curDs) : false;
            console.log('[Favorites] Câu mới #' + newStt + ' | ds: ' + curDs + ' | liked: ' + isNewFav);

        }, 100);
    }

    function attachListener() {
        var sel = document.getElementById('pfDatasetSelect');
        if (!sel) return false;
        if (sel.__favDatasetBound) return true;

        sel.__favDatasetBound = true;

        sel.addEventListener('change', function() {
            console.log('[Favorites] #pfDatasetSelect change fired');

            if (_datasetChangeTimer) clearTimeout(_datasetChangeTimer);
            _datasetChangeTimer = setTimeout(function() {
                handleDatasetChange();
                setTimeout(function() {
                    if (typeof favScanAllHeartButtons === 'function') {
                        favScanAllHeartButtons();
                    }
                }, 500);
            }, 250);
        });

        console.log('✅ [Favorites] Đã gắn listener cho #pfDatasetSelect');
        return true;
    }

    if (!attachListener()) {
        var _tries = 0;
        var _iv = setInterval(function() {
            _tries++;
            if (attachListener() || _tries > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH next/prev — Dùng loadPracticeFull + tự đổi dataset
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH next/prev — Điều hướng trong DANH SÁCH ĐÃ LỌC
   - Toggle BẬT: điều hướng trong favFilterRecords() (đã lọc)
   - Toggle TẮT: gọi hàm gốc
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   ⭐ PATCH next/prev — Điều hướng trong DANH SÁCH ĐÃ LỌC
   FIX: 
   - Dùng favFilterRecords() (đã lọc) thay vì favGetRecords()
   - Fallback tìm câu bất kể dataset
   - Set __favManualNav để chặn patch loadPracticeFull can thiệp
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function patchNavigateFn(fnName) {
        if (typeof window[fnName] !== 'function') return false;
        if (window[fnName].__favFilterPatched) return true;

        var _orig = window[fnName];

        window[fnName] = function() {
            /* ═══ KHÔNG BẬT TOGGLE → gọi hàm gốc ═══ */
            if (!favState.pfOnlyFav || !favCanUse()) {
                var res = _orig.apply(this, arguments);
                setTimeout(function() {
                    if (typeof favScanAllHeartButtons === 'function') {
                        favScanAllHeartButtons();
                    }
                }, 30);
                return res;
            }

            /* ═══════════════════════════════════════════════════════
               ⭐ BẬT TOGGLE → điều hướng trong DANH SÁCH ĐÃ LỌC
               ═══════════════════════════════════════════════════════ */
            var allFav = favGetRecords();
            var favList = favFilterRecords(allFav);

            console.log('[Fav Nav] ' + fnName + ' | Tổng fav: ' + allFav.length
                        + ' | Sau lọc: ' + favList.length);

            if (favList.length === 0) {
                if (typeof favShowToast === 'function') {
                    favShowToast('Không có câu nào khớp bộ lọc', 'warn');
                }
                return;
            }

            var direction = (fnName.toLowerCase().indexOf('prev') !== -1) ? -1 : 1;

            var curStt = (typeof pfCurrentStt !== 'undefined' && pfCurrentStt)
                         ? String(pfCurrentStt)
                         : null;
            var curDs = favGetCurrentDsId();
            var curIdx = -1;

            /* Tìm vị trí câu hiện tại */
            for (var i = 0; i < favList.length; i++) {
                if (String(favList[i].stt) === curStt &&
                    favList[i].__favDatasetId === curDs) {
                    curIdx = i;
                    break;
                }
            }

            /* ⭐⭐⭐ FIX: Nếu câu hiện tại không có trong list (đúng dataset)
               → Thử tìm bất kể dataset
               → Nếu vẫn không → nhảy về câu đầu */
            if (curIdx === -1) {
                console.log('[Fav Nav] Câu hiện tại không trong list — thử tìm bất kể dataset');

                for (var j = 0; j < favList.length; j++) {
                    if (String(favList[j].stt) === curStt) {
                        curIdx = j;
                        console.log('[Fav Nav] Tìm thấy ở dataset khác: ' + favList[j].__favDatasetId);
                        break;
                    }
                }
            }

            var nextIdx;
            if (curIdx === -1) {
                console.log('[Fav Nav] Hoàn toàn không có → câu đầu tiên');
                nextIdx = 0;
            } else {
                nextIdx = curIdx + direction;
                if (nextIdx < 0) nextIdx = favList.length - 1;
                if (nextIdx >= favList.length) nextIdx = 0;
            }

            var nextItem = favList[nextIdx];
            var nextStt = String(nextItem.stt);
            var nextDs = nextItem.__favDatasetId || curDs;

            console.log('[Fav Nav] curIdx=' + curIdx + ' → nextIdx=' + nextIdx
                        + ' | next STT=' + nextStt + ' | next DS=' + nextDs);

            /* ⭐⭐⭐ SET CỜ MANUAL NAV — chặn patch loadPracticeFull auto-nhảy */
            window.__favManualNav = true;
            window.__favRedirecting = true;

            /* ═══ Nếu câu kế thuộc dataset khác → chuyển dataset ═══ */
            if (nextDs !== curDs) {
                console.log('[Fav Nav] Đổi dataset: ' + curDs + ' → ' + nextDs);

                if (typeof window.__switchRawData === 'function') {
                    try {
                        window.__switchRawData(nextDs);
                    } catch(e) {
                        console.warn('[Favorites] __switchRawData error:', e);
                    }
                }

                var dsSel = document.getElementById('pfDatasetSelect');
                if (dsSel) dsSel.value = nextDs;

                if (typeof pfBuildFilterOptions === 'function') {
                    pfBuildFilterOptions();
                }
                if (typeof pfBuildDatasetSelect === 'function') {
                    pfBuildDatasetSelect();
                }

                setTimeout(function() {
                    if (typeof loadPracticeFull === 'function') {
                        loadPracticeFull(nextStt);
                    }
                    setTimeout(function() {
                        window.__favRedirecting = false;
                        window.__favManualNav = false;
                        if (typeof favRefreshQuestionDropdown === 'function') {
                            favRefreshQuestionDropdown();
                        }
                    }, 300);
                }, 100);

                return;
            }

            /* ═══ Cùng dataset → load trực tiếp ═══ */
            if (typeof loadPracticeFull === 'function') {
                loadPracticeFull(nextStt);
            }

            setTimeout(function() {
                window.__favRedirecting = false;
                window.__favManualNav = false;
                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
            }, 300);
        };

        window[fnName].__favFilterPatched = true;
        return true;
    }

    var fns = ['pfNavigate', 'pfNext', 'pfPrev', 'practiceNext', 'practicePrev',
               'nextPractice', 'prevPractice'];
    var _tries = 0;
    var _iv = setInterval(function() {
        _tries++;
        fns.forEach(function(fn) {
            if (typeof window[fn] === 'function' && !window[fn].__favFilterPatched) {
                patchNavigateFn(fn);
            }
        });
        if (_tries > 40) clearInterval(_iv);
    }, 200);
})();
/* ═══════════════════════════════════════════════════════════════
   PUBLIC API
   ═══════════════════════════════════════════════════════════════ */
window.favUpdateLockState = favUpdateLockState;
window.favNotifyChanged = favNotifyChanged;
window.favSyncFloatVisibility = favSyncFloatVisibility;
window.favUpdatePfFloatBtn = favUpdatePfFloatBtn;
window.favUpdatePfOnlyFavBtn = favUpdatePfOnlyFavBtn;
window.favGetRecords = favGetRecords;
window.favGetQuestionsForDropdown = favGetQuestionsForDropdown;
window.favRefreshQuestionDropdown = favRefreshQuestionDropdown;
window.favHas = favHas;
window.favCount = favCount;
window.favCountInCurrentDataset = favCountInCurrentDataset;
window.favExitFilterMode = favExitFilterMode;
window.favState = favState;
window.favBuildKey = favBuildKey;
window.favParseKey = favParseKey;
window.favMigrateLocalToCloud = favMigrateLocalToCloud;

window.favRefreshUI = function() {
    favUpdateLockState();
    favNotifyChanged();
    if (favCanUse() && !favState.loaded) {
        favLoadFromCloud();
    }
    if (!favIsLoggedIn()) {
        favState.items = {};
        favState.loaded = false;
        if (favState.listener) {
            try { favState.listener(); } catch(e) {}
            favState.listener = null;
        }
        favUpdateLockState();
    }
};

/* ═══════════════════════════════════════════════════════════════
   AUTO-INIT
   ═══════════════════════════════════════════════════════════════ */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof initFavorites === 'function') initFavorites();
        setTimeout(function() {
            if (typeof favSyncFloatVisibility === 'function') favSyncFloatVisibility();
        }, 100);
    });
} else {
    setTimeout(function() {
        if (typeof initFavorites === 'function') initFavorites();
        if (typeof favSyncFloatVisibility === 'function') favSyncFloatVisibility();
    }, 0);
}

/* Auto-refresh khi tier thay đổi */
(function() {
    var _lastTier = null;
    setInterval(function() {
        var t = (typeof window.APP_TIER !== 'undefined') ? window.APP_TIER : null;
        if (t !== _lastTier) {
            _lastTier = t;
            if (typeof window.favRefreshUI === 'function') window.favRefreshUI();
        }
    }, 800);
})();

/* ═══════════════════════════════════════════════════════════════
   FIX: Dời nút toggle sang góc phải, TRÊN nút tim
   ═══════════════════════════════════════════════════════════════ */
(function() {
    function injectCSS() {
        if (document.getElementById('favOnlyFloatFix')) return;
        var style = document.createElement('style');
        style.id = 'favOnlyFloatFix';
        style.textContent = [
            '/* Fix: nút toggle chỉ câu yêu thích — góc PHẢI, TRÊN nút tim */',
            '.pf-fav-only-float {',
            '    left: auto !important;',
            '    right: clamp(14px, 2vw, 22px) !important;',
            '    bottom: calc(140px + env(safe-area-inset-bottom)) !important;',
            '}',
            '@media (max-width:500px) {',
            '    .pf-fav-only-float {',
            '        bottom: calc(130px + env(safe-area-inset-bottom)) !important;',
            '    }',
            '}',
            '@media (max-height:550px) and (orientation:landscape) {',
            '    .pf-fav-only-float {',
            '        bottom: calc(114px + env(safe-area-inset-bottom)) !important;',
            '        transform-origin: right bottom !important;',
            '    }',
            '}'
        ].join('\n');
        document.head.appendChild(style);
    }
    if (document.head) injectCSS();
    else document.addEventListener('DOMContentLoaded', injectCSS);
})();

/* ═══════════════════════════════════════════════════════════════
   FIX: favRefreshQuestionDropdown — ưu tiên pfBuildQuickNav
   ═══════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════
   FIX: favRefreshQuestionDropdown — ưu tiên pfBuildQuickNav
   FIX 2: Nếu đang bật fav only → gọi favRebuildQuickNavForFav với list đã lọc
   ═══════════════════════════════════════════════════════════════ */
(function() {
    if (typeof window.favRefreshQuestionDropdown !== 'function') return;
    if (window.favRefreshQuestionDropdown.__favFixed2) return;

    var _origRefresh = window.favRefreshQuestionDropdown;
    window.favRefreshQuestionDropdown = function() {
        /* ⭐ Nếu đang bật toggle → dùng favRebuildQuickNavForFav với list đã lọc */
        if (favState.pfOnlyFav && favCanUse()) {
            try {
                var allFav = favGetRecords();
                var filteredList = (typeof favFilterRecords === 'function')
                                   ? favFilterRecords(allFav)
                                   : allFav;

                if (typeof favRebuildQuickNavForFav === 'function') {
                    favRebuildQuickNavForFav(filteredList);
                    return true;
                }
            } catch(e) {
                console.warn('[Favorites] favRebuildQuickNavForFav error:', e);
            }
        }

        /* ⭐ Fallback: gọi pfBuildQuickNav */
        if (typeof window.pfBuildQuickNav === 'function') {
            try {
                window.pfBuildQuickNav();
                return true;
            } catch(e) {
                console.warn('[Favorites] pfBuildQuickNav error:', e);
            }
        }

        return _origRefresh.apply(this, arguments);
    };
    window.favRefreshQuestionDropdown.__favFixed2 = true;
})();



/* ═══════════════════════════════════════════════════════════════════════════
   🎯 FAVORITES FILTER — MULTI-SELECT PANEL
   Tự inject UI vào pf-dataset-row, không cần sửa file chính
   ═══════════════════════════════════════════════════════════════════════════ */

/* ═══ STATE ═══ */
favState.favFilters = {
    datasets: [],
    hsk: [],
    subjects: [],
    search: ''
};
favState.favFilterDraft = null;
favState.__favFilterBound = false;

/* ═══════════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════════ */
function favFilterIsEmpty(f) {
    if (!f) return true;
    return (f.datasets || []).length === 0
        && (f.hsk || []).length === 0
        && (f.subjects || []).length === 0
        && !f.search;
}

function favFilterCount() {
    var f = favState.favFilters;
    if (!f) return 0;
    return (f.datasets || []).length
         + (f.hsk || []).length
         + (f.subjects || []).length
         + (f.search ? 1 : 0);
}

function favFilterClone(f) {
    return {
        datasets: (f.datasets || []).slice(),
        hsk: (f.hsk || []).slice(),
        subjects: (f.subjects || []).slice(),
        search: f.search || ''
    };
}

/* ⭐ Hàm lọc CHÍNH */
function favFilterRecords(records, filter) {
    var f = filter || favState.favFilters;
    if (!f || favFilterIsEmpty(f)) return (records || []).slice();

    return (records || []).filter(function(r) {
        if (f.datasets.length > 0) {
            var ds = r.__favDatasetId || 'tonghop';
            if (f.datasets.indexOf(ds) === -1) return false;
        }
        if (f.hsk.length > 0) {
            if (f.hsk.indexOf(r.hsk) === -1) return false;
        }
        if (f.subjects.length > 0) {
            if (f.subjects.indexOf(r.subject) === -1) return false;
        }
        if (f.search) {
            var s = f.search.toLowerCase();
            var inVi = (r.vi || '').toLowerCase().indexOf(s) !== -1;
            var inZh = (r.zh || '').toLowerCase().indexOf(s) !== -1;
            var inPy = (r.pinyin || '').toLowerCase().indexOf(s) !== -1;
            if (!inVi && !inZh && !inPy) return false;
        }
        return true;
    });
}

function favFilterBuildCounts(records) {
    var dsCounts = {}, hskCounts = {}, subjCounts = {};
    (records || []).forEach(function(r) {
        var ds = r.__favDatasetId || 'tonghop';
        dsCounts[ds] = (dsCounts[ds] || 0) + 1;
        if (r.hsk) hskCounts[r.hsk] = (hskCounts[r.hsk] || 0) + 1;
        if (r.subject) subjCounts[r.subject] = (subjCounts[r.subject] || 0) + 1;
    });
    return { dsCounts: dsCounts, hskCounts: hskCounts, subjCounts: subjCounts };
}

function favFilterGetDatasetName(dsId) {
    if (typeof DATASET_REGISTRY !== 'undefined' && DATASET_REGISTRY[dsId]) {
        var n = DATASET_REGISTRY[dsId].name || dsId;
        return n.normalize ? n.normalize('NFC') : n;
    }
    return dsId;
}

/* ═══════════════════════════════════════════════════════════════════════════
   INJECT UI — Tự chèn nút + summary + modal vào DOM
   ═══════════════════════════════════════════════════════════════════════════ */
function favInjectFilterUI() {
    /* ═══ 1. Chèn nút "Lọc" vào pf-quick-nav ═══ */
    var quickNav = document.getElementById('pfQuickNavWrap');
    if (quickNav && !document.getElementById('pfFavFilterBtn')) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.id = 'pfFavFilterBtn';
        btn.className = 'pf-fav-filter-btn';
        btn.title = 'Lọc câu yêu thích';
        btn.innerHTML = '<i class="fas fa-filter"></i>' +
                       '<span class="pf-fav-filter-label">Lọc</span>' +
                       '<span class="pf-fav-filter-badge" id="pfFavFilterBadge" style="display:none;">0</span>';
        quickNav.appendChild(btn);
    }

    /* ═══ 2. Chèn Summary bar sau pf-dataset-row ═══ */
    var datasetRow = document.getElementById('pfDatasetRow');
    if (datasetRow && !document.getElementById('pfFavFilterSummary')) {
        var summary = document.createElement('div');
        summary.id = 'pfFavFilterSummary';
        summary.className = 'pf-fav-filter-summary';
        datasetRow.parentNode.insertBefore(summary, datasetRow.nextSibling);
    }

    /* ═══ 3. Chèn Modal vào body ═══ */
    if (!document.getElementById('favFilterModal')) {
        var modal = document.createElement('div');
        modal.id = 'favFilterModal';
        modal.className = 'fav-filter-modal';
        modal.innerHTML =
            '<div class="fav-filter-box">' +
                '<div class="fav-filter-header">' +
                    '<div class="fav-filter-header-icon"><i class="fas fa-filter"></i></div>' +
                    '<div class="fav-filter-header-text">' +
                        '<div class="fav-filter-header-title">Lọc câu yêu thích</div>' +
                        '<div class="fav-filter-header-sub" id="favFilterSubtitle">Chọn tiêu chí để thu hẹp danh sách</div>' +
                    '</div>' +
                    '<button class="fav-filter-close" id="favFilterClose" type="button" aria-label="Đóng">' +
                        '<i class="fas fa-times"></i>' +
                    '</button>' +
                '</div>' +
                '<div class="fav-filter-body" id="favFilterBody"></div>' +
                '<div class="fav-filter-footer">' +
                    '<div class="fav-filter-result" id="favFilterResult">' +
                        'Đã lọc: <b id="favFilterResultNum">0</b>/<span id="favFilterResultTotal">0</span> câu' +
                    '</div>' +
                    '<button class="fav-filter-btn-secondary" id="favFilterReset" type="button">' +
                        '<i class="fas fa-undo-alt"></i> Xoá hết' +
                    '</button>' +
                    '<button class="fav-filter-btn-primary" id="favFilterApply" type="button">' +
                        '<i class="fas fa-check"></i> Áp dụng' +
                    '</button>' +
                '</div>' +
            '</div>';
        document.body.appendChild(modal);
    }

    /* ═══ 4. Bind events (chỉ 1 lần) ═══ */
    favBindFilterEvents();
}

function favBindFilterEvents() {
    if (favState.__favFilterBound) return;
    favState.__favFilterBound = true;

    var btnFilter = document.getElementById('pfFavFilterBtn');
    if (btnFilter && !btnFilter.__bound) {
        btnFilter.__bound = true;
        btnFilter.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            favOpenFilterModal();
        });
    }

    var closeBtn = document.getElementById('favFilterClose');
    if (closeBtn && !closeBtn.__bound) {
        closeBtn.__bound = true;
        closeBtn.addEventListener('click', favCloseFilterModal);
    }

    var modal = document.getElementById('favFilterModal');
    if (modal && !modal.__bound) {
        modal.__bound = true;
        modal.addEventListener('click', function(e) {
            if (e.target === modal) favCloseFilterModal();
        });
    }

    var resetBtn = document.getElementById('favFilterReset');
    if (resetBtn && !resetBtn.__bound) {
        resetBtn.__bound = true;
        resetBtn.addEventListener('click', function() {
            favState.favFilterDraft = {
                datasets: [], hsk: [], subjects: [], search: ''
            };
            favRenderFilterModalBody();
        });
    }

    var applyBtn = document.getElementById('favFilterApply');
    if (applyBtn && !applyBtn.__bound) {
        applyBtn.__bound = true;
        applyBtn.addEventListener('click', favApplyFilterDraft);
    }

    /* ESC để đóng */
    if (!window.__favFilterEscBound) {
        window.__favFilterEscBound = true;
        document.addEventListener('keydown', function(e) {
            if (e.key !== 'Escape') return;
            var m = document.getElementById('favFilterModal');
            if (m && m.classList.contains('show')) favCloseFilterModal();
        });
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
   MODAL LOGIC
   ═══════════════════════════════════════════════════════════════════════════ */
function favOpenFilterModal() {
    if (!favCanUse() || !favState.pfOnlyFav) {
        favShowToast('Bật chế độ "Chỉ câu yêu thích" trước', 'warn');
        return;
    }

    /* Copy filter hiện tại vào draft */
    favState.favFilterDraft = favFilterClone(favState.favFilters);

    favRenderFilterModalBody();

    var modal = document.getElementById('favFilterModal');
    if (modal) modal.classList.add('show');
}

function favCloseFilterModal() {
    var modal = document.getElementById('favFilterModal');
    if (modal) modal.classList.remove('show');
    favState.favFilterDraft = null;
}

function favRenderFilterModalBody() {
    var body = document.getElementById('favFilterBody');
    var subtitle = document.getElementById('favFilterSubtitle');
    var draft = favState.favFilterDraft;
    if (!body || !draft) return;

    var allFav = favGetRecords();

    if (allFav.length === 0) {
        body.innerHTML = '<div class="fav-filter-empty">' +
            '<i class="fas fa-inbox" style="font-size:2rem;opacity:.4;display:block;margin-bottom:.5rem;"></i>' +
            'Chưa có câu yêu thích nào' +
        '</div>';
        if (subtitle) subtitle.textContent = 'Chưa có câu yêu thích';
        favUpdateFilterModalFooter();
        return;
    }

    /* Đếm theo từng giá trị */
    var counts = favFilterBuildCounts(allFav);

    /* Danh sách options */
    var dsList = Object.keys(counts.dsCounts).sort();
    var hskList = Object.keys(counts.hskCounts).sort();
    var subjList = Object.keys(counts.subjCounts).sort();

    var html = '';

    /* ═══ SECTION 1: BỘ DỮ LIỆU ═══ */
    html += '<div class="fav-filter-section">' +
        '<div class="fav-filter-section-header">' +
            '<div class="fav-filter-section-icon dataset"><i class="fas fa-layer-group"></i></div>' +
            '<div class="fav-filter-section-title">Bộ dữ liệu</div>' +
            '<div class="fav-filter-section-actions">' +
                '<button type="button" onclick="favFilterToggleAll(\'datasets\')">Tất cả</button>' +
                '<button type="button" onclick="favFilterToggleNone(\'datasets\')">Bỏ chọn</button>' +
            '</div>' +
        '</div>' +
        '<div class="fav-filter-options">';

    if (dsList.length === 0) {
        html += '<div class="fav-filter-empty" style="padding:.5rem;font-size:.72rem;">Không có dữ liệu</div>';
    } else {
        dsList.forEach(function(ds) {
            var sel = draft.datasets.indexOf(ds) !== -1 ? ' selected' : '';
            var label = favFilterGetDatasetName(ds);
            html += '<button type="button" class="fav-filter-option' + sel + '" ' +
                'onclick="favFilterToggleOption(\'datasets\',\'' + escapeJs(ds) + '\')">' +
                escapeHtml(label) +
                '<span class="fav-opt-count">' + counts.dsCounts[ds] + '</span>' +
            '</button>';
        });
    }
    html += '</div></div>';

    /* ═══ SECTION 2: HSK ═══ */
    html += '<div class="fav-filter-section">' +
        '<div class="fav-filter-section-header">' +
            '<div class="fav-filter-section-icon hsk"><i class="fas fa-signal"></i></div>' +
            '<div class="fav-filter-section-title">Trình độ HSK</div>' +
            '<div class="fav-filter-section-actions">' +
                '<button type="button" onclick="favFilterToggleAll(\'hsk\')">Tất cả</button>' +
                '<button type="button" onclick="favFilterToggleNone(\'hsk\')">Bỏ chọn</button>' +
            '</div>' +
        '</div>' +
        '<div class="fav-filter-options">';

    if (hskList.length === 0) {
        html += '<div class="fav-filter-empty" style="padding:.5rem;font-size:.72rem;">Không có HSK</div>';
    } else {
        hskList.forEach(function(h) {
            var sel = draft.hsk.indexOf(h) !== -1 ? ' selected' : '';
            html += '<button type="button" class="fav-filter-option' + sel + '" ' +
                'onclick="favFilterToggleOption(\'hsk\',\'' + escapeJs(h) + '\')">' +
                escapeHtml(h) +
                '<span class="fav-opt-count">' + counts.hskCounts[h] + '</span>' +
            '</button>';
        });
    }
    html += '</div></div>';

    /* ═══ SECTION 3: CHỦ ĐỀ ═══ */
    html += '<div class="fav-filter-section">' +
        '<div class="fav-filter-section-header">' +
            '<div class="fav-filter-section-icon subject"><i class="fas fa-tag"></i></div>' +
            '<div class="fav-filter-section-title">Chủ đề</div>' +
            '<div class="fav-filter-section-actions">' +
                '<button type="button" onclick="favFilterToggleAll(\'subjects\')">Tất cả</button>' +
                '<button type="button" onclick="favFilterToggleNone(\'subjects\')">Bỏ chọn</button>' +
            '</div>' +
        '</div>' +
        '<div class="fav-filter-options">';

    if (subjList.length === 0) {
        html += '<div class="fav-filter-empty" style="padding:.5rem;font-size:.72rem;">Không có chủ đề</div>';
    } else {
        subjList.forEach(function(s) {
            var sel = draft.subjects.indexOf(s) !== -1 ? ' selected' : '';
            html += '<button type="button" class="fav-filter-option' + sel + '" ' +
                'onclick="favFilterToggleOption(\'subjects\',\'' + escapeJs(s) + '\')" ' +
                'title="' + escapeHtml(s) + '">' +
                escapeHtml(s) +
                '<span class="fav-opt-count">' + counts.subjCounts[s] + '</span>' +
            '</button>';
        });
    }
    html += '</div></div>';

    body.innerHTML = html;

    if (subtitle) {
        subtitle.textContent = allFav.length + ' câu yêu thích';
    }

    favUpdateFilterModalFooter();
}

function favUpdateFilterModalFooter() {
    var draft = favState.favFilterDraft;
    if (!draft) return;

    var allFav = favGetRecords();
    var filtered = favFilterRecords(allFav, draft);

    var numEl = document.getElementById('favFilterResultNum');
    var totalEl = document.getElementById('favFilterResultTotal');
    var applyBtn = document.getElementById('favFilterApply');

    if (numEl) numEl.textContent = filtered.length;
    if (totalEl) totalEl.textContent = allFav.length;

    if (applyBtn) {
        applyBtn.disabled = filtered.length === 0;
        applyBtn.innerHTML = '<i class="fas fa-check"></i> Áp dụng (' + filtered.length + ')';
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
   TOGGLE HANDLERS
   ═══════════════════════════════════════════════════════════════════════════ */
window.favFilterToggleOption = function(field, value) {
    var draft = favState.favFilterDraft;
    if (!draft || !draft[field]) return;

    var idx = draft[field].indexOf(value);
    if (idx === -1) draft[field].push(value);
    else draft[field].splice(idx, 1);

    favRenderFilterModalBody();
};

window.favFilterToggleAll = function(field) {
    var draft = favState.favFilterDraft;
    if (!draft) return;

    var allFav = favGetRecords();
    var counts = favFilterBuildCounts(allFav);
    var list = [];

    if (field === 'datasets') list = Object.keys(counts.dsCounts);
    else if (field === 'hsk') list = Object.keys(counts.hskCounts);
    else if (field === 'subjects') list = Object.keys(counts.subjCounts);

    draft[field] = list.slice();
    favRenderFilterModalBody();
};

window.favFilterToggleNone = function(field) {
    var draft = favState.favFilterDraft;
    if (!draft) return;
    draft[field] = [];
    favRenderFilterModalBody();
};

/* ═══════════════════════════════════════════════════════════════════════════
   APPLY / REMOVE / CLEAR
   ═══════════════════════════════════════════════════════════════════════════ */
function favApplyFilterDraft() {
    if (!favState.favFilterDraft) return;

    favState.favFilters = favFilterClone(favState.favFilterDraft);

    favCloseFilterModal();
    favApplyFilterChanges();
}

function favApplyFilterChanges() {
    /* Render lại summary bar */
    favRenderFilterSummary();

    /* Rebuild dropdown "CÂU:" */
    if (typeof favRefreshQuestionDropdown === 'function') {
        favRefreshQuestionDropdown();
    }

    /* Nhảy về câu đầu tiên hợp lệ */
    var allFav = favGetRecords();
    var filtered = favFilterRecords(allFav);

    if (filtered.length > 0) {
        var first = filtered[0];
        var firstStt = String(first.stt);
        var firstDs = first.__favDatasetId;
        var curDs = favGetCurrentDsId();

        /* Nếu câu đầu thuộc dataset khác → đổi dataset */
        if (firstDs && firstDs !== curDs) {
            window.__favRedirecting = true;

            if (typeof window.__switchRawData === 'function') {
                try { window.__switchRawData(firstDs); } catch(e) {}
            }
            var dsSel = document.getElementById('pfDatasetSelect');
            if (dsSel) dsSel.value = firstDs;

            if (typeof pfBuildFilterOptions === 'function') pfBuildFilterOptions();
            if (typeof pfBuildDatasetSelect === 'function') pfBuildDatasetSelect();

            setTimeout(function() {
                if (typeof loadPracticeFull === 'function') {
                    loadPracticeFull(firstStt);
                }
                setTimeout(function() {
                    window.__favRedirecting = false;
                    if (typeof favRefreshQuestionDropdown === 'function') {
                        favRefreshQuestionDropdown();
                    }
                }, 150);
            }, 60);
        } else {
            /* Cùng dataset → load luôn */
            window.__favRedirecting = true;

            if (typeof loadPracticeFull === 'function') {
                loadPracticeFull(firstStt);
            }

            setTimeout(function() {
                window.__favRedirecting = false;
                if (typeof favRefreshQuestionDropdown === 'function') {
                    favRefreshQuestionDropdown();
                }
            }, 120);
        }
    } else {
        favShowToast('Không có câu nào khớp bộ lọc', 'warn');
    }
}

/* ⭐ Xoá 1 filter từ chip summary */
window.favFilterRemove = function(field, value) {
    var arr = favState.favFilters[field];
    if (!arr) return;
    var idx = arr.indexOf(value);
    if (idx === -1) return;
    arr.splice(idx, 1);
    favApplyFilterChanges();
};

/* ⭐ Xoá hết filter */
window.favFilterClearAll = function() {
    favState.favFilters = {
        datasets: [], hsk: [], subjects: [], search: ''
    };
    favApplyFilterChanges();
};

/* ═══════════════════════════════════════════════════════════════════════════
   RENDER SUMMARY BAR
   ═══════════════════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════════════════
   🎯 RENDER SUMMARY BAR — 1 DÒNG, GỘP CHIP THÀNH "+N ..."
   ═══════════════════════════════════════════════════════════════════════════ */

/* Số chip filter tối đa hiển thị (không tính chip đếm ❤️ và nút Xoá) */
var FAV_SUMMARY_MAX_CHIPS = 3;

function favRenderFilterSummary() {
    var summary = document.getElementById('pfFavFilterSummary');
    if (!summary) return;

    /* ═══ 1. KHÔNG BẬT TOGGLE → ẨN ═══ */
    if (!favState.pfOnlyFav || !favCanUse()) {
        summary.classList.remove('show');
        summary.innerHTML = '';
        favUpdateFilterBtnVisibility();
        return;
    }

    var f = favState.favFilters;
    var totalFav = favCount();
    var filteredList = favFilterRecords(favGetRecords());
    var filteredCount = filteredList.length;
    var hasFilter = !favFilterIsEmpty(f);

    summary.classList.add('show');

    /* ═══ 2. GOM TẤT CẢ CHIP FILTER ACTIVE VÀO 1 MẢNG ═══ */
    var allChips = [];

    /* Chip datasets */
    (f.datasets || []).forEach(function(ds) {
        allChips.push({
            type: 'dataset',
            icon: 'fa-layer-group',
            label: favFilterGetDatasetName(ds),
            value: ds,
            field: 'datasets'
        });
    });

    /* Chip HSK */
    (f.hsk || []).forEach(function(h) {
        allChips.push({
            type: 'hsk',
            icon: 'fa-signal',
            label: h,
            value: h,
            field: 'hsk'
        });
    });

    /* Chip subjects */
    (f.subjects || []).forEach(function(s) {
        allChips.push({
            type: 'subject',
            icon: 'fa-tag',
            label: s,
            value: s,
            field: 'subjects'
        });
    });

    /* ═══ 3. BUILD HTML ═══ */
    var html = '';

    /* Chip đếm */
    if (hasFilter) {
        html += '<span class="pf-fav-summary-count">' +
            '<i class="fas fa-filter"></i>' +
            '<b>' + filteredCount + '</b>/' + totalFav +
        '</span>';
    } else {
        html += '<span class="pf-fav-summary-count">' +
            '<i class="fas fa-heart"></i>' +
            '<b>' + totalFav + '</b> câu' +
        '</span>';
    }

    /* Wrap chứa chip filter */
    html += '<div class="pf-fav-summary-chips-wrap">';

    if (allChips.length > 0) {
        var visibleChips = allChips.slice(0, FAV_SUMMARY_MAX_CHIPS);
        var hiddenChips = allChips.slice(FAV_SUMMARY_MAX_CHIPS);

        visibleChips.forEach(function(c) {
            html += favBuildSummaryChip(c);
        });

        /* Chip "+N ..." nếu có chip bị ẩn */
        if (hiddenChips.length > 0) {
            var tooltipLines = hiddenChips.map(function(c) {
                return '• ' + c.label;
            }).join('\n');

            html += '<span class="pf-fav-summary-chip more" ' +
                'data-tooltip="' + escapeHtml(tooltipLines) + '" ' +
                'title="">' +
                '+' + hiddenChips.length + ' …' +
            '</span>';
        }
    }
    html += '</div>';

    /* Nút Xoá lọc — luôn bên phải */
    if (hasFilter) {
        html += '<button class="pf-fav-summary-clear" onclick="favFilterClearAll()">' +
            '<i class="fas fa-times-circle"></i> Xoá' +
        '</button>';
    }

    summary.innerHTML = html;

    favUpdateFilterBtnVisibility();
    favUpdateFilterBtnBadge();
}

/* Helper build 1 chip */
function favBuildSummaryChip(c) {
    var label = c.label;
    var displayLabel = label.length > 20 ? label.substring(0, 20) + '…' : label;

    return '<span class="pf-fav-summary-chip ' + c.type + '" ' +
        'title="' + escapeHtml(label) + '">' +
        '<i class="fas ' + c.icon + '"></i>' +
        escapeHtml(displayLabel) +
        '<i class="fas fa-times" ' +
        'onclick="favFilterRemove(\'' + c.field + '\',\'' + escapeJs(c.value) + '\')">' +
        '</i>' +
    '</span>';
}
function favUpdateFilterBtnVisibility() {
    var btn = document.getElementById('pfFavFilterBtn');
    if (!btn) return;
    if (favState.pfOnlyFav && favCanUse()) {
        btn.classList.add('show');
    } else {
        btn.classList.remove('show');
    }
}

function favUpdateFilterBtnBadge() {
    var btn = document.getElementById('pfFavFilterBtn');
    var badge = document.getElementById('pfFavFilterBadge');
    if (!btn || !badge) return;

    var count = favFilterCount();
    if (count > 0) {
        badge.textContent = count;
        badge.style.display = 'inline-flex';
        btn.classList.add('active');
        btn.title = 'Đang lọc: ' + count + ' tiêu chí';
    } else {
        badge.style.display = 'none';
        btn.classList.remove('active');
        btn.title = 'Lọc câu yêu thích';
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK vào favTogglePfOnlyFav
   ═══════════════════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════════════════
   🎯 ẨN/HIỆN 3 FILTER CŨ KHI BẬT/TẮT FAVORITES ONLY
   - Khi bật: ẩn Bộ dữ liệu / HSK / Chủ đề, chỉ giữ nút Lọc + dropdown Câu
   - Khi tắt: hiện lại bình thường
   - Sync class .fav-only-active trên <body>
   ═══════════════════════════════════════════════════════════════════════════ */
function favToggleOldFilters(active) {
    if (active) {
        document.body.classList.add('fav-only-active');
    } else {
        document.body.classList.remove('fav-only-active');
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK 1: favTogglePfOnlyFav — Khi user bật/tắt toggle
   - BẬT: inject UI + render summary + ẩn 3 filter cũ
   - TẮT: clear filter + ẩn UI + hiện lại 3 filter cũ
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryHook() {
        if (typeof window.favTogglePfOnlyFav !== 'function') return false;
        if (window.favTogglePfOnlyFav.__favFilterHooked) return true;

        var _orig = window.favTogglePfOnlyFav;
        window.favTogglePfOnlyFav = function() {
            var wasActive = favState.pfOnlyFav;

            var result = _orig.apply(this, arguments);

            setTimeout(function() {
                if (favState.pfOnlyFav) {
                    /* ═══ BẬT ═══ */
                    favInjectFilterUI();
                    favRenderFilterSummary();
                    favUpdateFilterBtnVisibility();

                    /* Ẩn 3 filter cũ */
                    favToggleOldFilters(true);
                } else {
                    /* ═══ TẮT ═══ */
                    favState.favFilters = {
                        datasets: [], hsk: [], subjects: [], search: ''
                    };
                    favRenderFilterSummary();

                    var summary = document.getElementById('pfFavFilterSummary');
                    if (summary) {
                        summary.classList.remove('show');
                        summary.innerHTML = '';
                    }

                    /* Hiện lại 3 filter cũ */
                    favToggleOldFilters(false);
                }
            }, 50);

            return result;
        };
        window.favTogglePfOnlyFav.__favFilterHooked = true;
        return true;
    }

    if (!tryHook()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryHook() || _t > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK 2: favRefreshQuestionDropdown — Filter theo favFilters
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryHook() {
        if (typeof window.favRefreshQuestionDropdown !== 'function') return false;
        if (window.favRefreshQuestionDropdown.__favFilterHooked) return true;

        var _orig = window.favRefreshQuestionDropdown;
        window.favRefreshQuestionDropdown = function() {
            if (favState.pfOnlyFav && favCanUse()) {
                var allFav = favGetRecords();
                var filtered = favFilterRecords(allFav);

                if (typeof favRebuildQuickNavForFav === 'function') {
                    favRebuildQuickNavForFav(filtered);
                    return true;
                }
            }
            return _orig.apply(this, arguments);
        };
        window.favRefreshQuestionDropdown.__favFilterHooked = true;
        return true;
    }

    if (!tryHook()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryHook() || _t > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK 3: pfBuildQuickNav — Fallback khi hàm này gọi trực tiếp
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    var _hooked = false;
    setInterval(function() {
        if (_hooked) return;
        if (typeof window.pfBuildQuickNav !== 'function') return;
        if (window.pfBuildQuickNav.__favFilterPanelHooked) { _hooked = true; return; }

        var _orig = window.pfBuildQuickNav;
        window.pfBuildQuickNav = function() {
            if (favState.pfOnlyFav && favCanUse()) {
                var allFav = favGetRecords();
                var filtered = favFilterRecords(allFav);
                if (typeof favRebuildQuickNavForFav === 'function') {
                    favRebuildQuickNavForFav(filtered);
                    return;
                }
            }
            return _orig.apply(this, arguments);
        };
        window.pfBuildQuickNav.__favFilterPanelHooked = true;
        _hooked = true;
    }, 1500);
})();

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK 4: favSyncFloatVisibility — Inject UI + sync class khi mở modal
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryHook() {
        if (typeof window.favSyncFloatVisibility !== 'function') return false;
        if (window.favSyncFloatVisibility.__favFilterHooked) return true;

        var _orig = window.favSyncFloatVisibility;
        window.favSyncFloatVisibility = function() {
            var result = _orig.apply(this, arguments);

            setTimeout(function() {
                favInjectFilterUI();

                var modal = document.getElementById('practiceFullModal');
                var isOpen = modal && modal.classList.contains('show');

                /* ⭐ Sync class fav-only-active */
                if (isOpen && favState.pfOnlyFav && favCanUse()) {
                    favToggleOldFilters(true);
                    favRenderFilterSummary();
                    favUpdateFilterBtnVisibility();
                } else {
                    favToggleOldFilters(false);

                    var summary = document.getElementById('pfFavFilterSummary');
                    if (summary) summary.classList.remove('show');
                    var btn = document.getElementById('pfFavFilterBtn');
                    if (btn) btn.classList.remove('show');
                }
            }, 30);

            return result;
        };
        window.favSyncFloatVisibility.__favFilterHooked = true;
        return true;
    }

    if (!tryHook()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryHook() || _t > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK 5: favUpdateLockState — Tắt filter khi mất quyền/logout
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryHook() {
        if (typeof window.favUpdateLockState !== 'function') return false;
        if (window.favUpdateLockState.__favOldFiltersHooked) return true;

        var _orig = window.favUpdateLockState;
        window.favUpdateLockState = function() {
            var result = _orig.apply(this, arguments);

            setTimeout(function() {
                if (!favCanUse() || !favState.pfOnlyFav) {
                    favToggleOldFilters(false);
                }
            }, 20);

            return result;
        };
        window.favUpdateLockState.__favOldFiltersHooked = true;
        return true;
    }

    if (!tryHook()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryHook() || _t > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════════════════
   🎯 PATCH pfApplyFilter — Dùng favFilters khi toggle BẬT
   - Khi ẩn 3 filter cũ: bỏ qua giá trị của select HSK/Chủ đề
   - Chỉ dùng favFilters (từ panel Lọc)
   ═══════════════════════════════════════════════════════════════════════════ */
/* ═══════════════════════════════════════════════════════════════════════════
   🎯 PATCH pfApplyFilter — Dùng favFilters khi toggle BẬT
   - Khi ẩn 3 filter cũ: bỏ qua giá trị của select HSK/Chủ đề
   - Chỉ dùng favFilters (từ panel Lọc)
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.pfApplyFilter !== 'function') return false;
        if (window.pfApplyFilter.__favFilterPanelPatched) return true;

        var _orig = window.pfApplyFilter;

        window.pfApplyFilter = function() {
            /* ═══════════════════════════════════════════════════════
               KHÔNG BẬT TOGGLE → gọi hàm gốc
               ═══════════════════════════════════════════════════════ */
            if (!favState.pfOnlyFav || !favCanUse()) {
                return _orig.apply(this, arguments);
            }

            /* ═══════════════════════════════════════════════════════
               1. ĐỌC FILTER TỪ UI
               - Nếu filter cũ đang bị ẨN (.fav-only-active):
                 → BỎ QUA giá trị của #pfHskFilter / #pfSubjectFilter
                 → Chỉ dùng favState.favFilters (từ panel Lọc)
               ═══════════════════════════════════════════════════════ */
            var oldFiltersHidden = document.body.classList.contains('fav-only-active');

            var searchInput = document.getElementById('pfSearchInput');
            var hskSel = document.getElementById('pfHskFilter');
            var subjSel = document.getElementById('pfSubjectFilter');

            var searchVal = searchInput ? searchInput.value.trim().toLowerCase() : '';
            var hskVal = oldFiltersHidden ? '' : (hskSel ? hskSel.value : '');
            var subjVal = oldFiltersHidden ? '' : (subjSel ? subjSel.value : '');

            /* ═══════════════════════════════════════════════════════
               2. ĐỒNG BỘ FILTER → favFilters
               ═══════════════════════════════════════════════════════ */
            var f = favState.favFilters;
            f.search = searchVal;

            if (!oldFiltersHidden) {
                if (hskVal) {
                    if (f.hsk.indexOf(hskVal) === -1) f.hsk = [hskVal];
                } else {
                    f.hsk = [];
                }
                if (subjVal) {
                    if (f.subjects.indexOf(subjVal) === -1) f.subjects = [subjVal];
                } else {
                    f.subjects = [];
                }
            }

            /* ═══════════════════════════════════════════════════════
               3. ĐỒNG BỘ VỀ MAIN PAGE
               ═══════════════════════════════════════════════════════ */
            var mainSearch = document.getElementById('searchInput');
            var mainHsk = document.getElementById('hskFilter');
            var mainSubj = document.getElementById('subjectFilter');
            if (mainSearch) mainSearch.value = searchInput ? searchInput.value : '';
            if (mainHsk) mainHsk.value = hskVal;
            if (mainSubj) mainSubj.value = subjVal;

            if (typeof state !== 'undefined') {
                state.search = searchVal;
                state.hsk = hskVal;
                state.subject = subjVal;
            }

            /* ═══════════════════════════════════════════════════════
               4. FILTER RECORDS theo favFilters
               ═══════════════════════════════════════════════════════ */
            var filteredFav = favFilterRecords(favGetRecords());

            try {
                filtered = filteredFav;
            } catch(e) {
                try { window.filtered = filteredFav; } catch(e2) {}
            }

            if (typeof pfUpdateFilterUI === 'function') pfUpdateFilterUI();
            if (typeof updateFilterUI === 'function') updateFilterUI();

            /* ═══════════════════════════════════════════════════════
               5. REBUILD dropdown "CÂU:"
               ═══════════════════════════════════════════════════════ */
            if (typeof favRebuildQuickNavForFav === 'function') {
                favRebuildQuickNavForFav(filteredFav);
            } else if (typeof favRefreshQuestionDropdown === 'function') {
                favRefreshQuestionDropdown();
            }

            /* ═══════════════════════════════════════════════════════
               6. RENDER MAIN PAGE
               ═══════════════════════════════════════════════════════ */
            if (typeof render === 'function') render(true);

            /* ═══════════════════════════════════════════════════════
               7. NHẢY VỀ CÂU ĐẦU TIÊN HỢP LỆ
               ═══════════════════════════════════════════════════════ */
            if (filteredFav.length > 0) {
                var first = filteredFav[0];
                var firstStt = String(first.stt);
                var firstDs = first.__favDatasetId;
                var curDs = favGetCurrentDsId();

                if (firstDs && firstDs !== curDs) {
                    /* ─── Cần đổi dataset ─── */
                    window.__favRedirecting = true;

                    if (typeof window.__switchRawData === 'function') {
                        try { window.__switchRawData(firstDs); } catch(e) {}
                    }

                    var dsSel = document.getElementById('pfDatasetSelect');
                    if (dsSel) dsSel.value = firstDs;

                    if (typeof pfBuildFilterOptions === 'function') {
                        pfBuildFilterOptions();
                    }
                    if (typeof pfBuildDatasetSelect === 'function') {
                        pfBuildDatasetSelect();
                    }

                    setTimeout(function() {
                        if (typeof loadPracticeFull === 'function') {
                            loadPracticeFull(firstStt);
                        }
                        setTimeout(function() {
                            window.__favRedirecting = false;
                            if (typeof favRefreshQuestionDropdown === 'function') {
                                favRefreshQuestionDropdown();
                            }
                        }, 150);
                    }, 60);

                } else {
                    /* ─── Cùng dataset → load luôn ─── */
                    window.__favRedirecting = true;

                    if (typeof loadPracticeFull === 'function') {
                        loadPracticeFull(firstStt);
                    }

                    setTimeout(function() {
                        window.__favRedirecting = false;
                        if (typeof favRefreshQuestionDropdown === 'function') {
                            favRefreshQuestionDropdown();
                        }
                    }, 120);
                }
            } else {
                if (typeof favShowToast === 'function') {
                    favShowToast('Không có câu nào khớp bộ lọc', 'warn');
                }
            }

            /* ═══════════════════════════════════════════════════════
               8. UPDATE SUMMARY BAR
               ═══════════════════════════════════════════════════════ */
            favRenderFilterSummary();
        };

        window.pfApplyFilter.__favFilterPanelPatched = true;
        return true;
    }

    if (!tryPatch()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryPatch() || _t > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════════════════
   HOOK 6: openPracticeFull — Inject UI + sync class khi mở modal
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryPatch() {
        if (typeof window.openPracticeFull !== 'function') return false;
        if (window.openPracticeFull.__favFilterUIInjected) return true;

        var _orig = window.openPracticeFull;
        window.openPracticeFull = function() {
            /* Inject UI trước khi mở */
            setTimeout(favInjectFilterUI, 0);

            var result = _orig.apply(this, arguments);

            setTimeout(function() {
                favInjectFilterUI();
                if (favState.pfOnlyFav && favCanUse()) {
                    favToggleOldFilters(true);
                    favRenderFilterSummary();
                    favUpdateFilterBtnVisibility();
                } else {
                    favToggleOldFilters(false);
                }
            }, 30);

            setTimeout(function() {
                favInjectFilterUI();
            }, 200);

            return result;
        };
        window.openPracticeFull.__favFilterUIInjected = true;
        return true;
    }

    if (!tryPatch()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryPatch() || _t > 60) clearInterval(_iv);
        }, 200);
    }
})();

/* ═══════════════════════════════════════════════════════════════════════════
   INIT — Inject UI khi app khởi động xong
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    function tryInject() {
        var pfModal = document.getElementById('practiceFullModal');
        if (!pfModal) return false;
        favInjectFilterUI();
        return true;
    }

    if (!tryInject()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryInject() || _t > 60) clearInterval(_iv);
        }, 250);
    }

    /* Retry định kỳ để đảm bảo UI tồn tại (chống DOM bị reset) */
    setInterval(function() {
        if (!document.getElementById('pfFavFilterBtn')) {
            favInjectFilterUI();
        }
    }, 3000);
})();

/* ═══════════════════════════════════════════════════════════════════════════
   🔧 FIX CUỐI — Đảm bảo class .fav-only-active LUÔN sync đúng
   Chạy định kỳ để bắt kịp mọi thay đổi state
   ═══════════════════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════════════════
   EXPORT
   ═══════════════════════════════════════════════════════════════════════════ */
window.favToggleOldFilters = favToggleOldFilters;
/* ═══════════════════════════════════════════════════════════════════════════
   EXPORT PUBLIC API
   ═══════════════════════════════════════════════════════════════════════════ */
window.favOpenFilterModal = favOpenFilterModal;
window.favCloseFilterModal = favCloseFilterModal;
window.favFilterRecords = favFilterRecords;
window.favRenderFilterSummary = favRenderFilterSummary;
window.favFilterIsEmpty = favFilterIsEmpty;
window.favFilterCount = favFilterCount;
/* ═══════════════════════════════════════════════════════════════════════════
   🔧 FIX: K đềHI ĐÓNG FULL MODE → TỰ)

 ĐỘNG RESET "CHỈ C2. User đÂU YÊU THÍCH"
   Đảm bảo rằng sau khi đóng full mode:
   1. Toggle "Chỉ câu yêu thích" tự tắt
   2. Bộ lọc yêu thích (datasets/hsk/subjects/search) tự xóa
   3. class "fav-only-active" trên <body> được remove
   4. Filter cũ (HSK/Chủ đề/Dataset) hiện lại bình thường
   5. Nút "Lọc" ẩn đi
   6. Summary bar ẩn đi
   7. Câu không phải yêu thích có thể mở bình thường
   ═══════════════════════════════════════════════════════════════════════════ */
(function() {
    'use strict';

    /* ═══════════════════════════════════════════════════════════
       HÀM RESET TOÀN BỘ FAV STATE
       ═══════════════════════════════════════════════════════════ */
    function favResetOnFullClose() {
        /* ═══ 1. Tắt toggle ═══ */
        var wasActive = favState.pfOnlyFav;
        favState.pfOnlyFav = false;

        /* ═══ 2. Xóa filters ═══ */
        favState.favFilters = {
            datasets: [],
            hsk: [],
            subjects: [],
            search: ''
        };
        favState.favFilterDraft = null;

        /* ═══ 3. Xóa class fav-only-active trên body ═══ */
        document.body.classList.remove('fav-only-active');

        /* ═══ 4. Cập nhật nút toggle float ═══ */
        if (typeof favUpdatePfOnlyFavBtn === 'function') {
            favUpdatePfOnlyFavBtn();
        }

        /* ═══ 5. Ẩn summary bar ═══ */
        var summary = document.getElementById('pfFavFilterSummary');
        if (summary) {
            summary.classList.remove('show');
            summary.innerHTML = '';
        }

        /* ═══ 6. Ẩn nút Lọc ═══ */
        var btn = document.getElementById('pfFavFilterBtn');
        if (btn) {
            btn.classList.remove('show', 'active');
        }

        /* ═══ 7. Đóng modal filter nếu đang mở ═══ */
        var filterModal = document.getElementById('favFilterModal');
        if (filterModal && filterModal.classList.contains('show')) {
            filterModal.classList.remove('show');
        }

        /* ═══ 8. Clear filter trong main page (nếu có) ═══ */
        try {
            if (typeof state !== 'undefined' && state) {
                state.search = '';
                state.hsk = '';
                state.subject = '';
            }

            var si = document.getElementById('searchInput');
            var hf = document.getElementById('hskFilter');
            var sf = document.getElementById('subjectFilter');
            if (si) si.value = '';
            if (hf) hf.value = '';
            if (sf) sf.value = '';

            var cb = document.getElementById('clearSearchBtn');
            if (cb) cb.classList.remove('show');
        } catch(e) {}

        /* ═══ 9. Clear flags ═══ */
        window.__favRedirecting = false;
        window.__favManualNav = false;

        /* ═══ 10. Log ═══ */
        if (wasActive) {
            console.log('✅ [Favorites] Đã reset "Chỉ câu yêu thích" khi đóng Full Mode');
        }
    }

    /* ═══════════════════════════════════════════════════════════
       HOOK VÀO closePracticeFull
       ═══════════════════════════════════════════════════════════ */
    function tryHookClosePF() {
        if (typeof window.closePracticeFull !== 'function') return false;
        if (window.closePracticeFull.__favResetHooked) return true;

        var _origClose = window.closePracticeFull;
        window.closePracticeFull = function() {
            /* ⭐ RESET TRƯỚC KHI ĐÓNG */
            if (favState.pfOnlyFav) {
                favResetOnFullClose();
            }

            return _origClose.apply(this, arguments);
        };
        window.closePracticeFull.__favResetHooked = true;
        console.log('✅ [Favorites] Hooked closePracticeFull — auto-reset toggle');
        return true;
    }

    if (!tryHookClosePF()) {
        var _t = 0;
        var _iv = setInterval(function() {
            _t++;
            if (tryHookClosePF() || _t > 60) clearInterval(_iv);
        }, 200);
    }

    /* ═══════════════════════════════════════════════════════════
       FALLBACK: MutationObserver — phát hiện modal đóng
       (phòng khi closePracticeFull bị override bởi module khác)
       ═══════════════════════════════════════════════════════════ */
    function attachModalObserver() {
        var pfModal = document.getElementById('practiceFullModal');
        if (!pfModal) return false;
        if (pfModal.__favResetObserved) return true;
        pfModal.__favResetObserved = true;

        var wasOpen = pfModal.classList.contains('show');

        var obs = new MutationObserver(function() {
            var isOpen = pfModal.classList.contains('show');

            /* ⭐ Modal ĐÓNG (true → false) + toggle đang bật → reset */
            if (wasOpen && !isOpen && favState.pfOnlyFav) {
                favResetOnFullClose();
            }
            wasOpen = isOpen;
        });

        obs.observe(pfModal, { attributes: true, attributeFilter: ['class'] });
        return true;
    }

    if (!attachModalObserver()) {
        var _t2 = 0;
        var _iv2 = setInterval(function() {
            _t2++;
            if (attachModalObserver() || _t2 > 60) clearInterval(_iv2);
        }, 200);
    }

    /* ═══════════════════════════════════════════════════════════
       EXPORT
       ═══════════════════════════════════════════════════════════ */
    window.favResetOnFullClose = favResetOnFullClose;

})();
"""
