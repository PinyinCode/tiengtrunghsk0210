# -*- coding: utf-8 -*-
r"""
fix.py - Auto-scan data/ và thêm MỌI file Excel thành tab riêng.
+ TỰ ĐỘNG thêm tab TỪ VỰNG PREMIUM từ data/tu_vung_hsk.xlsx
+ COVER LẠI TOÀN BỘ NÚT DATASET SANG LAYOUT 2 HÀNG GỌN
+ ICON WATERMARK CHÌM GÓC PHẢI

Cách chạy:
    python scripts/convert.py
    python fix.py
"""
import json
import os
import re
import sys
import glob
import unicodedata

import openpyxl


# =================================================================
#  CONFIG
# =================================================================
INDEX_HTML = "index.html"
CONFIG_JSON = "config.json"
DATA_DIR = "data"

SKIP_FILES = {"input.xlsx", "input.xls", "input.csv"}

VOCAB_FILE = os.path.join(DATA_DIR, "tu_vung_hsk.xlsx")
VOCAB_ID = "tu-vung"
VOCAB_LABEL = "11000+ Từ vựng HSK"


# =================================================================
#  CSS: BUTTONS 2 ROWS — ICON WATERMARK CHÌM
# =================================================================
BUTTONS_2ROWS_CSS = r"""
/* ═══════════════════════════════════════════════════════════ */
/* FIX.PY: DATASET BUTTONS — 2 HÀNG + ICON WATERMARK CHÌM      */
/* ═══════════════════════════════════════════════════════════ */

.ds-main-row {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: .55rem !important;
    align-items: stretch !important;
}
@media (max-width: 1100px) {
    .ds-main-row { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
}
@media (max-width: 420px) {
    .ds-main-row { grid-template-columns: 1fr !important; }
}

/* ── Nút cơ bản ── */
.ds-btn {
    display: flex !important;
    align-items: center !important;
    gap: 0 !important;
    padding: .65rem .85rem !important;
    min-height: 60px !important;
    height: 100% !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family: inherit !important;
    text-align: left !important;
    cursor: pointer !important;
    transition: all .2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
.ds-btn:hover {
    border-color: var(--primary) !important;
    background: var(--surface-2) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px -6px rgba(15,23,42,.15) !important;
}

/* ICON — WATERMARK CHÌM Ở GÓC PHẢI */
.ds-btn .ds-btn-icon,
.ds-btn > i.ds-btn-icon {
    position: absolute !important;
    right: .5rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 52px !important;
    height: 52px !important;
    border-radius: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 2.6rem !important;
    background: none !important;
    background-color: transparent !important;
    color: currentColor !important;
    opacity: .08 !important;
    pointer-events: none !important;
    z-index: 0 !important;
    transition: opacity .2s !important;
    box-shadow: none !important;
    border: none !important;
}
.ds-btn:hover .ds-btn-icon,
.ds-btn:hover > i.ds-btn-icon {
    opacity: .15 !important;
}

/* KHỐI TEXT — FULL WIDTH */
.ds-btn .ds-btn-text {
    position: relative !important;
    z-index: 1 !important;
    flex: 1 1 auto !important;
    min-width: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: .12rem !important;
    padding-right: 2.6rem !important;
}
.ds-btn .ds-btn-title {
    font-size: clamp(.82rem, 1.05vw, .95rem) !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    letter-spacing: -.01em !important;
    display: block !important;
}
.ds-btn .ds-btn-title b {
    font-weight: 900 !important;
    color: var(--text) !important;
    margin-right: .15rem !important;
}
.ds-btn .ds-btn-sub {
    font-size: clamp(.65rem, .82vw, .75rem) !important;
    font-weight: 600 !important;
    color: var(--text-3) !important;
    line-height: 1.25 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    display: block !important;
    font-style: normal !important;
}

/* ── Active ── */
.ds-btn.active {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    border-color: transparent !important;
    box-shadow: 0 6px 18px -4px rgba(124,58,237,.45) !important;
    transform: translateY(-2px) !important;
}
.ds-btn.active .ds-btn-icon,
.ds-btn.active > i.ds-btn-icon {
    opacity: .18 !important;
    color: #fff !important;
    background: none !important;
}
.ds-btn.active .ds-btn-title,
.ds-btn.active .ds-btn-title b { color: #fff !important; }
.ds-btn.active .ds-btn-sub { color: rgba(255,255,255,.82) !important; }

/* ═══ CHUYÊN NGÀNH ═══ */
.ds-btn[data-dataset-group="chuyen-nganh"] {
    padding-right: 2.2rem !important;
}
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-arrow {
    position: absolute !important;
    right: .75rem !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    font-size: .7rem !important;
    color: var(--text-3) !important;
    transition: transform .25s !important;
    pointer-events: none !important;
    z-index: 2 !important;
}
.ds-btn[data-dataset-group="chuyen-nganh"] .ds-btn-text {
    padding-right: 1.8rem !important;
}
.ds-btn[data-dataset-group="chuyen-nganh"].active .ds-arrow {
    transform: translateY(-50%) rotate(180deg) !important;
    color: #fff !important;
}

.ds-new-badge {
    position: absolute !important;
    top: -7px !important;
    right: -7px !important;
    padding: .15rem .5rem !important;
    border-radius: 50px !important;
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: #fff !important;
    font-size: .56rem !important;
    font-weight: 900 !important;
    letter-spacing: .5px !important;
    box-shadow: 0 2px 8px rgba(220,38,38,.5), 0 0 0 2px var(--surface) !important;
    animation: dsNewPulse 1.6s ease-in-out infinite !important;
    z-index: 10 !important;
    pointer-events: none !important;
}
@keyframes dsNewPulse {
    0%,100% { transform: scale(1); }
    50%     { transform: scale(1.1); }
}

/* ═══ TỪ VỰNG PREMIUM ═══ */
.ds-btn[data-dataset="tu-vung"] {
    background: linear-gradient(135deg, #fffbeb, #fef3c7) !important;
    border-color: rgba(245,158,11,.5) !important;
}
.ds-btn[data-dataset="tu-vung"] .ds-btn-icon,
.ds-btn[data-dataset="tu-vung"] > i.ds-btn-icon {
    color: #d97706 !important;
    opacity: .12 !important;
    background: none !important;
}
.ds-btn[data-dataset="tu-vung"] .ds-btn-title,
.ds-btn[data-dataset="tu-vung"] .ds-btn-title b { color: #92400e !important; }
.ds-btn[data-dataset="tu-vung"] .ds-btn-sub { color: #b45309 !important; }
.ds-btn[data-dataset="tu-vung"]:hover {
    border-color: #f59e0b !important;
    background: linear-gradient(135deg, #fef3c7, #fde68a) !important;
}
.ds-btn[data-dataset="tu-vung"].active {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    border-color: transparent !important;
}
.ds-btn[data-dataset="tu-vung"].active .ds-btn-title,
.ds-btn[data-dataset="tu-vung"].active .ds-btn-title b { color: #fff !important; }
.ds-btn[data-dataset="tu-vung"].active .ds-btn-sub { color: rgba(255,255,255,.85) !important; }
.ds-btn[data-dataset="tu-vung"].active .ds-btn-icon,
.ds-btn[data-dataset="tu-vung"].active > i.ds-btn-icon {
    color: #fff !important;
    opacity: .25 !important;
}

/* ═══ YÊU THÍCH ═══ */
.ds-btn[data-dataset-group="favorites"] {
    background: linear-gradient(135deg, #fef2f2, #fee2e2) !important;
    border-color: rgba(239,68,68,.35) !important;
}
.ds-btn[data-dataset-group="favorites"] .ds-btn-icon,
.ds-btn[data-dataset-group="favorites"] > i.ds-btn-icon {
    color: #ef4444 !important;
    opacity: .12 !important;
    background: none !important;
}
.ds-btn[data-dataset-group="favorites"] .ds-btn-title,
.ds-btn[data-dataset-group="favorites"] .ds-btn-title b { color: #991b1b !important; }
.ds-btn[data-dataset-group="favorites"] .ds-btn-sub { color: #b91c1c !important; }
.ds-btn[data-dataset-group="favorites"].active {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    border-color: transparent !important;
}
.ds-btn[data-dataset-group="favorites"].active .ds-btn-title,
.ds-btn[data-dataset-group="favorites"].active .ds-btn-title b,
.ds-btn[data-dataset-group="favorites"].active .ds-btn-sub { color: #fff !important; }
.ds-btn[data-dataset-group="favorites"].active .ds-btn-icon,
.ds-btn[data-dataset-group="favorites"].active > i.ds-btn-icon {
    color: #fff !important;
    opacity: .25 !important;
}

/* ═══ DARK MODE ═══ */
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] {
    background: linear-gradient(135deg, rgba(245,158,11,.18), rgba(217,119,6,.12)) !important;
    border-color: rgba(245,158,11,.45) !important;
}
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] .ds-btn-title,
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] .ds-btn-title b { color: #fcd34d !important; }
[data-theme="dark"] .ds-btn[data-dataset="tu-vung"] .ds-btn-sub { color: #fbbf24 !important; }
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] {
    background: linear-gradient(135deg, rgba(239,68,68,.18), rgba(220,38,38,.1)) !important;
    border-color: rgba(239,68,68,.4) !important;
}
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] .ds-btn-title,
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] .ds-btn-title b { color: #fca5a5 !important; }
[data-theme="dark"] .ds-btn[data-dataset-group="favorites"] .ds-btn-sub { color: #f87171 !important; }

/* ═══ MOBILE ═══ */
@media (max-width: 500px) {
    .ds-btn {
        min-height: 56px !important;
        padding: .55rem .7rem !important;
    }
    .ds-btn .ds-btn-icon,
    .ds-btn > i.ds-btn-icon {
        width: 44px !important;
        height: 44px !important;
        font-size: 2.2rem !important;
        right: .35rem !important;
    }
    .ds-btn .ds-btn-text {
        padding-right: 2.2rem !important;
    }
    .ds-btn .ds-btn-title { font-size: .78rem !important; }
    .ds-btn .ds-btn-sub   { font-size: .62rem !important; }
}
"""


# =================================================================
#  VOCAB WARNING CSS — Banner cảnh báo giới hạn từ vựng
# =================================================================
VOCAB_WARNING_CSS = r"""
/* ═══ BANNER CẢNH BÁO TỪ VỰNG ═══ */
.vocab-warning-banner {
    display: flex; align-items: center; gap: .85rem;
    padding: .85rem 1rem; margin-bottom: 1rem;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(251, 191, 36, .15), rgba(245, 158, 11, .08));
    border: 1.5px solid rgba(245, 158, 11, .45);
    animation: vocabWarnIn .4s cubic-bezier(.34, 1.56, .64, 1);
}
@keyframes vocabWarnIn {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.vocab-warning-banner.tier-trial {
    background: linear-gradient(135deg, rgba(99, 102, 241, .12), rgba(139, 92, 246, .08));
    border-color: rgba(99, 102, 241, .45);
}
.vocab-warning-banner.tier-expired {
    background: linear-gradient(135deg, rgba(220, 38, 38, .12), rgba(251, 146, 60, .08));
    border-color: rgba(220, 38, 38, .5);
}
.vocab-warning-banner.tier-active {
    background: linear-gradient(135deg, rgba(8, 145, 178, .12), rgba(6, 182, 212, .08));
    border-color: rgba(8, 145, 178, .45);
}
.vocab-warning-icon {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #fff; display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(245, 158, 11, .4);
}
.vocab-warning-banner.tier-trial .vocab-warning-icon {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 4px 12px rgba(99, 102, 241, .4);
}
.vocab-warning-banner.tier-expired .vocab-warning-icon {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    box-shadow: 0 4px 12px rgba(220, 38, 38, .4);
}
.vocab-warning-banner.tier-active .vocab-warning-icon {
    background: linear-gradient(135deg, #0891b2, #06b6d4);
    box-shadow: 0 4px 12px rgba(8, 145, 178, .4);
}
.vocab-warning-text { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: .15rem; }
.vocab-warning-text strong { font-size: .92rem; font-weight: 800; color: #92400e; }
.vocab-warning-banner.tier-trial .vocab-warning-text strong { color: #4f46e5; }
.vocab-warning-banner.tier-expired .vocab-warning-text strong { color: #991b1b; }
.vocab-warning-banner.tier-active .vocab-warning-text strong { color: #075985; }
.vocab-warning-text span { font-size: .8rem; color: var(--text-2); line-height: 1.4; }
.vocab-warning-btn {
    padding: .55rem .9rem; border-radius: 10px; border: none;
    background: linear-gradient(135deg, #fbbf24, #f59e0b 50%, #ea580c);
    color: #fff; font-weight: 800; font-size: .8rem;
    font-family: inherit; cursor: pointer;
    display: inline-flex; align-items: center; gap: .35rem;
    box-shadow: 0 4px 12px rgba(245, 158, 11, .4);
    transition: all .2s; white-space: nowrap; flex-shrink: 0;
}
.vocab-warning-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(245, 158, 11, .6);
}
[data-theme="dark"] .vocab-warning-banner {
    background: linear-gradient(135deg, rgba(251, 191, 36, .2), rgba(245, 158, 11, .1));
}
[data-theme="dark"] .vocab-warning-text strong { color: #fcd34d; }
[data-theme="dark"] .vocab-warning-banner.tier-trial .vocab-warning-text strong { color: #c4b5fd; }
[data-theme="dark"] .vocab-warning-banner.tier-expired .vocab-warning-text strong { color: #fca5a5; }
[data-theme="dark"] .vocab-warning-banner.tier-active .vocab-warning-text strong { color: #67e8f9; }
@media (max-width: 600px) {
    .vocab-warning-banner { flex-wrap: wrap; gap: .6rem; padding: .7rem .8rem; }
    .vocab-warning-icon { width: 34px; height: 34px; font-size: .95rem; }
    .vocab-warning-text strong { font-size: .85rem; }
    .vocab-warning-text span { font-size: .74rem; }
}
"""


# =================================================================
#  VOCAB JS PATCH
# =================================================================
def build_vocab_js_patch():
    """JS phân quyền + giới hạn HSK + số câu + banner cho vocab."""
    return r"""
/* ═══════════════════════════════════════════════════════
   VOCAB PATCH — dùng ONBOARDING_CONFIG để phân quyền
   ═══════════════════════════════════════════════════════ */
(function() {
    'use strict';
    var VOCAB_ID = 'tu-vung';

    function getVocabAccess() {
    var cfg = (typeof ONBOARDING_CONFIG !== 'undefined' && ONBOARDING_CONFIG) || {};

    var appTier = (typeof window.APP_TIER !== 'undefined') ? window.APP_TIER : null;

    var u = null;
    try {
        if (typeof window.currentUser !== 'undefined' && window.currentUser) u = window.currentUser;
        else if (typeof currentUser !== 'undefined' && currentUser) u = currentUser;
    } catch(e) {}

    if (u && u.role === 'admin') {
        return { allowed: true, tier: 'admin',
            hskAllowed: [1,2,3,4,5,6,7,8,9], maxQuestions: -1,
            label: 'Admin — Toàn bộ HSK', warning: null };
    }

    if (u && u.isPermanent === true) {
        return { allowed: true, tier: 'premium',
            hskAllowed: [1,2,3,4,5,6,7,8,9], maxQuestions: -1,
            label: 'Premium — Toàn bộ HSK', warning: null };
    }

    var tier = 'demo';
    if (appTier === 'active') tier = 'active';
    else if (appTier === 'trial') tier = 'trial';
    else if (appTier === 'expired') tier = 'expired';
    else if (appTier === 'demo') tier = 'demo';
    else if (u) {
        if (u.isTrial === true || u.tier === 'trial') tier = 'trial';
        else if (u.isExpiredOnly === true || u.tier === 'expired') tier = 'expired';
        else tier = 'active';
    }

    var tierCfg = cfg[tier] || {};
    var hskArr = tierCfg.hsk_allowed || [];
    var maxQ = (typeof tierCfg.max_questions === 'number') ? tierCfg.max_questions : -1;
    var maxT = (typeof tierCfg.topics_per_user === 'number') ? tierCfg.topics_per_user : -1;
    var isUnlimited = (maxQ === -1 && maxT === -1);

    var hskRange = hskArr.length
        ? 'HSK ' + hskArr[0] + '-' + hskArr[hskArr.length - 1]
        : 'cơ bản';

    if (tier === 'expired') {
        return { allowed: false, tier: 'expired', hskAllowed: [], maxQuestions: 0,
            label: 'Tài khoản hết hạn',
            warning: 'Tài khoản đã hết hạn — gia hạn để tiếp tục dùng Từ vựng HSK.' };
    }

    if (tier === 'demo') {
        return { allowed: true, tier: 'demo', hskAllowed: hskArr, maxQuestions: maxQ,
            label: 'Demo — ' + hskRange,
            warning: 'Bản Demo giới hạn ' + hskRange + ' và tối đa ' +
                     (maxQ > 0 ? maxQ + ' từ' : 'một số từ') +
                     ' — đăng nhập để dùng đầy đủ.' };
    }

    if (tier === 'trial') {
        if (isUnlimited) {
            return { allowed: true, tier: 'trial',
                hskAllowed: hskArr.length ? hskArr : [1,2,3,4,5,6,7,8,9],
                maxQuestions: -1,
                label: 'Trial — ' + hskRange, warning: null };
        }
        return { allowed: true, tier: 'trial', hskAllowed: hskArr, maxQuestions: maxQ,
            label: 'Trial — ' + hskRange,
            warning: 'Bản Trial giới hạn ' + hskRange + ' và ' +
                     (maxQ > 0 ? maxQ + ' từ' : 'một số từ') +
                     ' — nâng cấp Premium để mở toàn bộ.' };
    }

    if (isUnlimited) {
        return { allowed: true, tier: 'active',
            hskAllowed: hskArr.length ? hskArr : [1,2,3,4,5,6,7,8,9],
            maxQuestions: -1,
            label: 'Active — ' + hskRange, warning: null };
    }
    return { allowed: true, tier: 'active', hskAllowed: hskArr, maxQuestions: maxQ,
        label: 'Active — ' + hskRange,
        warning: 'Bản Active giới hạn ' + hskRange + ' và ' +
                 (maxQ > 0 ? maxQ + ' từ' : 'một số từ') +
                 ' — nâng cấp Premium để mở toàn bộ.' };
}
    function applyVocabLimits(list, access) {
        var result = list;
        if (access.hskAllowed && access.hskAllowed.length &&
            access.hskAllowed.length < 9) {
            var allowSet = {};
            access.hskAllowed.forEach(function(h) {
                allowSet['HSK' + h] = true;
                allowSet[String(h)] = true;
            });
            result = result.filter(function(r) {
                var h = (r.hsk || '').toString().toUpperCase().trim();
                if (!h) return true;

                if (h === 'HSK7-9') {
                    return allowSet['HSK7-9'] === true;
                }

                var num = h.replace(/[^0-9]/g, '');
                if (!num) return true;
                return allowSet['HSK' + num] === true || allowSet[num] === true;
            });
        }
        var maxQ = access.maxQuestions;
        if (typeof maxQ === 'number' && maxQ > 0 && result.length > maxQ) {
            result = result.slice(0, maxQ);
        }
        return result;
    }

    function _esc(s) {
        return (typeof escapeHtml === 'function')
            ? escapeHtml(s) : String(s == null ? '' : s);
    }

    function _isVocabMode() {
        return (typeof CURRENT_DATASET !== 'undefined') && CURRENT_DATASET === VOCAB_ID;
    }

    function updateTabLockState() {
        var btn = document.querySelector('.ds-btn[data-dataset="' + VOCAB_ID + '"]');
        if (!btn) return;
        var acc = getVocabAccess();
        var oldLock = btn.querySelector('.vocab-lock-icon');
        if (oldLock) oldLock.remove();
        var badge = btn.querySelector('.ds-vocab-badge');

        if (acc.allowed) {
            btn.classList.remove('vocab-locked');
            btn.classList.add('vocab-unlocked');
            btn.title = acc.label;
            if (badge) {
                badge.textContent = (acc.tier === 'admin' || acc.tier === 'premium')
                    ? 'PREMIUM' : (acc.tier === 'active' ? 'ACTIVE'
                    : (acc.tier === 'trial' ? 'TRIAL' : 'DEMO'));
            }
        } else {
            btn.classList.add('vocab-locked');
            btn.classList.remove('vocab-unlocked');
            btn.title = acc.label;
            var lock = document.createElement('i');
            lock.className = 'fas fa-lock vocab-lock-icon';
            btn.appendChild(lock);
        }
    }

    function injectVocabWarningBanner() {
    if (!_isVocabMode()) {
        var oldOut = document.getElementById('vocabWarningBanner');
        if (oldOut) oldOut.remove();
        return;
    }
        var old = document.getElementById('vocabWarningBanner');
        if (old) old.remove();

        var acc = getVocabAccess();
        if (!acc.warning) return;

        var main = document.getElementById('mainContent');
        if (!main) return;

        var limitedCount = 0, totalCount = 0;
        try {
            if (window.FIXPY_DATASETS && window.FIXPY_DATASETS[VOCAB_ID]) {
                var full = window.FIXPY_DATASETS[VOCAB_ID].data || [];
                totalCount = full.length;
                limitedCount = applyVocabLimits(full, acc).length;
            }
        } catch(e) {}

        var limitInfo = '';
        if (acc.maxQuestions > 0 && limitedCount > 0 && totalCount > limitedCount) {
            limitInfo = ' <span style="opacity:.75">(' +
                        limitedCount + '/' + totalCount + ' từ)</span>';
        }

        var icon = acc.tier === 'expired' ? 'fa-exclamation-triangle'
                 : acc.tier === 'trial' ? 'fa-hourglass-half'
                 : acc.tier === 'demo' ? 'fa-user'
                 : 'fa-info-circle';
        var btnLabel = acc.tier === 'expired' ? 'Gia hạn ngay'
                     : acc.tier === 'demo' ? 'Đăng nhập'
                     : 'Nâng cấp Premium';
        var btnFn = acc.tier === 'demo' ? 'vocabUpgradeLogin()'
                  : 'vocabUpgradeRenew()';

        var banner = document.createElement('div');
        banner.id = 'vocabWarningBanner';
        banner.className = 'vocab-warning-banner tier-' + acc.tier;
        banner.innerHTML =
            '<div class="vocab-warning-icon"><i class="fas ' + icon + '"></i></div>' +
            '<div class="vocab-warning-text">' +
                '<strong>' + _esc(acc.label) + limitInfo + '</strong>' +
                '<span>' + _esc(acc.warning) + '</span>' +
            '</div>' +
            '<button class="vocab-warning-btn" onclick="' + btnFn + '">' +
                '<i class="fas fa-crown"></i> ' + btnLabel +
            '</button>';
        main.insertBefore(banner, main.firstChild);
    }

    function patchSubjectLock() {
        if (window.__vocabSubjectLockPatched) return;
        if (typeof window.buildFilters !== 'function') {
            setTimeout(patchSubjectLock, 200);
            return;
        }
        var orig = window.buildFilters;
        window.buildFilters = function() {
            var result = orig.apply(this, arguments);

            try {
                var sf = document.getElementById('subjectFilter');
                if (!sf) return result;

                if (_isVocabMode()) {
                    sf.disabled = true;
                    sf.value = '';
                    sf.style.opacity = '0.5';
                    sf.style.cursor = 'not-allowed';
                    sf.title = 'Không khả dụng cho Từ vựng';
                } else {
                    sf.disabled = false;
                    sf.style.opacity = '';
                    sf.style.cursor = '';
                    sf.title = '';
                }
            } catch(e) {}

            return result;
        };
        window.__vocabSubjectLockPatched = true;
        console.log('[vocab-patch] subject lock patched');
    }

    function watchVocabMode() {
        var isVocab = (typeof CURRENT_DATASET !== 'undefined') && CURRENT_DATASET === VOCAB_ID;

        if (isVocab) {
            document.body.setAttribute('data-vocab-mode', '1');
        } else {
            document.body.removeAttribute('data-vocab-mode');
        }

        var selects = [
            document.getElementById('subjectFilter'),
            document.getElementById('pfSubjectFilter')
        ];

        selects.forEach(function(sf) {
            if (!sf) return;

            if (isVocab && !sf.disabled) {
                sf.disabled = true;
                sf.value = '';
                sf.style.opacity = '0.5';
                sf.style.cursor = 'not-allowed';
                sf.title = 'Không khả dụng cho Từ vựng';
            } else if (!isVocab && sf.disabled) {
                sf.disabled = false;
                sf.style.opacity = '';
                sf.style.cursor = '';
                sf.title = '';
            }
        });

        var hskSelects = [
            document.getElementById('hskFilter'),
            document.getElementById('pfHskFilter')
        ];

        hskSelects.forEach(function(hf) {
            if (!hf) return;

            var hsk79 = hf.querySelector('option[value="HSK7-9"]');
            var has79 = !!hsk79;

            if (isVocab && !has79) {
                var opt = document.createElement('option');
                opt.value = 'HSK7-9';
                opt.textContent = 'HSK7-9';
                hf.appendChild(opt);
            } else if (!isVocab && has79) {
                if (hf.value === 'HSK7-9') {
                    hf.value = '';
                }
                hsk79.remove();
            }
        });
    }
    window.getVocabAccess = getVocabAccess;
    window.vocabUpdateLockState = updateTabLockState;
    window.vocabInjectWarning = injectVocabWarningBanner;

    function patchLoop() {
        var vocabBtn = document.querySelector('.ds-btn[data-dataset="' + VOCAB_ID + '"]');
        if (!vocabBtn) {
            setTimeout(patchLoop, 300);
            return;
        }

        window.vocabUpdateLockState = updateTabLockState;

        if (!window.__vocabBuildFiltersPatched && typeof window.buildFilters === 'function') {
            window.__vocabBuildFiltersPatched = true;
            var origBuildFilters = window.buildFilters;
            window.buildFilters = function() {
                var result = origBuildFilters.apply(this, arguments);

                if (_isVocabMode()) {
                    var hf = document.getElementById('hskFilter');
                    if (hf && !hf.querySelector('option[value="HSK7-9"]')) {
                        var opt = document.createElement('option');
                        opt.value = 'HSK7-9';
                        opt.textContent = 'HSK7-9';
                        hf.appendChild(opt);
                    }
                }

                return result;
            };
            console.log('[vocab-patch] buildFilters patched');
        }

        if (!window.__vocabPfFilterPatched && typeof window.pfBuildFilterOptions === 'function') {
            window.__vocabPfFilterPatched = true;
            var origPfBuild = window.pfBuildFilterOptions;
            window.pfBuildFilterOptions = function() {
                var result = origPfBuild.apply(this, arguments);

                if (_isVocabMode()) {
                    var pfHf = document.getElementById('pfHskFilter');
                    if (pfHf && !pfHf.querySelector('option[value="HSK7-9"]')) {
                        var opt = document.createElement('option');
                        opt.value = 'HSK7-9';
                        opt.textContent = 'HSK7-9';
                        pfHf.appendChild(opt);
                    }

                    var pfSubj = document.getElementById('pfSubjectFilter');
                    if (pfSubj) {
                        pfSubj.disabled = true;
                        pfSubj.value = '';
                        pfSubj.style.opacity = '0.5';
                        pfSubj.style.cursor = 'not-allowed';
                        pfSubj.title = 'Không khả dụng cho Từ vựng';
                    }
                }

                return result;
            };
            console.log('[vocab-patch] pfBuildFilterOptions patched');
        }

        if (!vocabBtn.__vocabLimitHooked) {
            vocabBtn.__vocabLimitHooked = true;
            vocabBtn.addEventListener('click', function() {
                setTimeout(function() {
                    var acc = getVocabAccess();
                    if (!acc.allowed) return;
                    if (_isVocabMode() && window.FIXPY_DATASETS &&
                        window.FIXPY_DATASETS[VOCAB_ID]) {
                        var full = window.FIXPY_DATASETS[VOCAB_ID].data || [];
                        var limited = applyVocabLimits(full, acc);
                        if (limited.length !== full.length) {
                            RAW_DATA = limited;
                            if (typeof applyFilter === 'function') applyFilter();
                            if (typeof updateResultCount === 'function') updateResultCount();
                        }
                    }
                    updateTabLockState();
                    injectVocabWarningBanner();
                    watchVocabMode();
                }, 500);
            }, false);
        }

        updateTabLockState();

        setInterval(function() {
            updateTabLockState();
            if (_isVocabMode()) injectVocabWarningBanner();
        }, 2000);

        watchVocabMode();
        setInterval(watchVocabMode, 800);

        console.log('[vocab-patch] ready — onboarding-based');
    }
    setTimeout(patchLoop, 800);
})();
"""


if not os.path.isfile(CONFIG_JSON) and os.path.isfile(os.path.join("..", CONFIG_JSON)):
    os.chdir("..")
    print("[fix.py] Phat hien chay tu scripts/ -> chuyen ve root")

TAB_ICONS = [
    "fa-comments", "fa-file-alt", "fa-book", "fa-graduation-cap",
    "fa-star", "fa-fire", "fa-bolt", "fa-rocket",
]
TAB_COLORS = [
    "#0891b2", "#dc2626", "#059669", "#d97706",
    "#7c3aed", "#db2777", "#0284c7", "#65a30d",
]


# =================================================================
#  IMPORT MODULE TỪ VỰNG PREMIUM
# =================================================================
try:
    from vocab_premium import (
        read_vocab_excel,
        build_vocab_css,
        build_vocab_tab_html,
        build_vocab_modal_html,
        build_vocab_js_override,
    )
    HAS_VOCAB_MODULE = True
    print("[fix.py] OK - Da load module vocab_premium")
except ImportError as e:
    HAS_VOCAB_MODULE = False
    print("[fix.py] WARN - Khong load duoc vocab_premium: " + str(e))


# =================================================================
#  CHUYEN SO A RAP -> SO HAN
# =================================================================
try:
    import cn2an
    HAS_CN2AN = True
except ImportError:
    HAS_CN2AN = False
    print("[fix.py] Khong co cn2an - dung bo dich so du phong")

_CN_DIGITS = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
_CN_UNITS = ['', '十', '百', '千']


def _num_to_chinese_basic(num):
    if num == 0:
        return '零'
    if num < 0:
        return '负' + _num_to_chinese_basic(-num)
    result = ''
    unit_idx = 0
    n = num
    while n > 0:
        digit = n % 10
        if digit != 0:
            if not (unit_idx == 1 and digit == 1 and n < 20 and result == ''):
                result = _CN_DIGITS[digit] + _CN_UNITS[unit_idx] + result
            else:
                result = _CN_UNITS[unit_idx] + result
        else:
            if result and not result.startswith('零'):
                result = '零' + result
        n //= 10
        unit_idx += 1
    if result.startswith('一十'):
        result = result[1:]
    return result


def _num_to_chinese(num):
    if HAS_CN2AN:
        try:
            return cn2an.an2cn(num)
        except Exception:
            pass
    return _num_to_chinese_basic(num)


def _digits_to_chinese(digits_str):
    return ''.join([_CN_DIGITS[int(d)] for d in digits_str])


def convert_arabic_to_chinese(text):
    if not text or not isinstance(text, str):
        return text

    def replace_percent(match):
        num_str = match.group(1)
        if '.' in num_str:
            parts = num_str.split('.')
            int_part = _num_to_chinese(int(parts[0]))
            dec_part = _digits_to_chinese(parts[1])
            return '百分之' + int_part + '点' + dec_part
        return '百分之' + _num_to_chinese(int(num_str))

    text = re.sub(r'(\d+(?:\.\d+)?)%', replace_percent, text)

    def replace_decimal(match):
        num_str = match.group(0)
        parts = num_str.split('.')
        int_part = _num_to_chinese(int(parts[0]))
        dec_part = _digits_to_chinese(parts[1])
        return int_part + '点' + dec_part

    text = re.sub(
        r'(?<![A-Za-z\-\.])\d+\.\d+(?![A-Za-z])',
        replace_decimal, text
    )

    def replace_int(match):
        return _num_to_chinese(int(match.group(0)))

    text = re.sub(
        r'(?<![A-Za-z\-\.])\d+(?![A-Za-z]|\.\d)',
        replace_int, text
    )

    return text


def _clean(s):
    if s is None:
        return ""
    return (str(s).replace('\n', ' ').replace('\r', ' ')
            .replace('\t', ' ').replace('\\', '\\\\'))


# =================================================================
#  HELPERS
# =================================================================
def _slugify(filename):
    base = filename.rsplit(".", 1)[0]
    base = unicodedata.normalize("NFD", base)
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    base = base.replace("đ", "d").replace("Đ", "D")
    return re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower() or "dataset"


def _display_name(filename):
    name = filename.rsplit(".", 1)[0].replace("_", " ").strip()
    name = unicodedata.normalize("NFC", name)
    if name.islower() or name.isupper():
        name = name.title()
    return name


def _escape_json_for_script(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/")


def _js_str(s):
    if s is None:
        return ""
    return (str(s)
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("</", "<\\/"))


def _html_escape(s):
    """Escape cho HTML text (khác _js_str)."""
    if s is None:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _find_file_safe(filepath):
    if os.path.isfile(filepath):
        return filepath
    dirname = os.path.dirname(filepath) or "."
    basename = os.path.basename(filepath)
    if not os.path.isdir(dirname):
        return None
    variants = set()
    variants.add(basename)
    variants.add(unicodedata.normalize("NFC", basename))
    variants.add(unicodedata.normalize("NFD", basename))
    try:
        for fname in os.listdir(dirname):
            fname_nfc = unicodedata.normalize("NFC", fname)
            fname_nfd = unicodedata.normalize("NFD", fname)
            for variant in variants:
                if (fname == variant
                        or fname_nfc == unicodedata.normalize("NFC", variant)
                        or fname_nfd == unicodedata.normalize("NFD", variant)):
                    return os.path.join(dirname, fname)
    except Exception:
        pass
    return None


def _read_excel_rows(filepath):
    real_path = _find_file_safe(filepath)
    if not real_path:
        print("      [X] Khong tim thay file: " + os.path.basename(filepath))
        return []

    try:
        wb = openpyxl.load_workbook(real_path, data_only=True)
    except Exception as e:
        print("      [X] Loi load: " + type(e).__name__ + ": " + str(e))
        return []

    try:
        ws = wb.worksheets[0]
    except Exception as e:
        print("      [X] Loi sheet: " + str(e))
        return []

    print("      Sheet: " + ws.title
          + " - " + str(ws.max_row) + " dong, "
          + str(ws.max_column) + " cot")

    COL_STT = 0
    COL_HSK = 1
    COL_TOPIC = 2
    COL_SUBJECT = 3
    COL_VI = 4
    COL_ZH = 5
    COL_PINYIN = 6
    DATA_START = 2

    rows = []
    converted_count = 0
    skipped_empty = 0

    for row in ws.iter_rows(min_row=DATA_START, values_only=True):
        if not row or len(row) <= max(COL_VI, COL_ZH):
            skipped_empty += 1
            continue

        stt_val = row[COL_STT] if COL_STT < len(row) and row[COL_STT] is not None else ""
        hsk = _clean(row[COL_HSK]) if COL_HSK < len(row) else ""
        topic = _clean(row[COL_TOPIC]) if COL_TOPIC < len(row) else ""
        subject = _clean(row[COL_SUBJECT]) if COL_SUBJECT < len(row) else ""
        vi = _clean(row[COL_VI]) if COL_VI < len(row) else ""
        zh = _clean(row[COL_ZH]) if COL_ZH < len(row) else ""
        pinyin = _clean(row[COL_PINYIN]) if COL_PINYIN < len(row) else ""

        if not vi and not zh:
            skipped_empty += 1
            continue

        zh_original = zh
        zh = convert_arabic_to_chinese(zh)
        if zh != zh_original:
            converted_count += 1

        rows.append({
            "stt": str(stt_val),
            "hsk": hsk,
            "topic": topic,
            "subject": subject,
            "vi": vi,
            "zh": zh,
            "pinyin": pinyin,
        })

    print("      [OK] " + str(len(rows)) + " cau (bo qua "
          + str(skipped_empty) + " dong rong)")
    if converted_count > 0:
        print("      [OK] Chuyen so A Rap -> Han: " + str(converted_count) + " cau")

    return rows


# =================================================================
#  SCAN data/
# =================================================================
def scan_data_dir():
    if not os.path.isdir(DATA_DIR):
        print("[fix.py] Khong thay thu muc '" + DATA_DIR + "/' - bo qua.")
        return []

    files = []
    for ext in ("*.xlsx", "*.xls", "*.csv"):
        files.extend(glob.glob(os.path.join(DATA_DIR, ext)))
    files = sorted(set(files))

    if not files:
        print("[fix.py] Khong co file Excel trong '" + DATA_DIR + "/'")
        return []

    print("")
    print("[fix.py] Quet '" + DATA_DIR + "/' - " + str(len(files)) + " file")

    datasets = []
    used_ids = set()

    vocab_basename = os.path.basename(VOCAB_FILE).lower()

    for filepath in files:
        fname = os.path.basename(filepath)

        if fname.startswith("~$"):
            print("   [skip] " + fname + " - file tam")
            continue

        if fname.lower() in SKIP_FILES:
            print("   [skip] " + fname + " - da la tab Tong hop")
            continue

        if fname.lower() == vocab_basename:
            print("   [skip] " + fname + " - se tao tab Tu vung Premium rieng")
            continue

        print("   [file] " + fname)
        rows = _read_excel_rows(filepath)
        if not rows:
            print("   [!] " + fname + " - rong hoac loi, bo qua")
            continue

        base_id = _slugify(fname)
        dataset_id = base_id
        counter = 2
        while dataset_id in used_ids:
            dataset_id = base_id + "-" + str(counter)
            counter += 1
        used_ids.add(dataset_id)

        idx = len(datasets)
        icon = TAB_ICONS[idx % len(TAB_ICONS)]
        color = TAB_COLORS[idx % len(TAB_COLORS)]

        display = _display_name(fname)
        datasets.append({
            "id": dataset_id,
            "name": display,
            "icon": icon,
            "color": color,
            "data": rows,
            "count": len(rows),
            "source": fname,
            "type": "main",
            "group": "fixpy",
        })
        print("   [OK] " + fname + " -> tab '" + display
              + "' (" + str(len(rows)) + " cau)")

    return datasets


# =================================================================
#  BUILD JS OVERRIDE
# =================================================================
def build_js_override(ids_js, datasets_json):
    L = []
    add = L.append

    add("")
    add("<script>")
    add("/* FIX.PY OVERRIDE - Bind tab moi + TIER LOCK + ONBOARDING */")
    add("(function() {")
    add("    'use strict';")
    add("    var NEW_IDS = " + ids_js + ";")
    add("")

    add("    window.FIXPY_DATASETS = " + datasets_json + ";")
    add("")

    add("    function patchSwitchRawData() {")
    add("        if (window.__fixPySwitchPatched) return;")
    add("        var origSwitch = window.__switchRawData;")
    add("        if (typeof origSwitch !== 'function') {")
    add("            setTimeout(patchSwitchRawData, 100);")
    add("            return;")
    add("        }")
    add("        window.__switchRawData = function(datasetId) {")
    add("            if (window.FIXPY_DATASETS && window.FIXPY_DATASETS[datasetId]) {")
    add("                RAW_DATA = window.FIXPY_DATASETS[datasetId].data || [];")
    add("                CURRENT_DATASET = datasetId;")
    add("                console.log('[fix.py] switch FIXPY_DATASET:',")
    add("                            datasetId, '->', RAW_DATA.length, 'cau');")
    add("                return true;")
    add("            }")
    add("            return origSwitch.apply(this, arguments);")
    add("        };")
    add("        window.__fixPySwitchPatched = true;")
    add("    }")
    add("    patchSwitchRawData();")
    add("")

    add("    function patchMarkActive() {")
    add("        if (window.__fixPyMarkPatched) return;")
    add("        window.markCurrentDatasetActive = function() {")
    add("            var cur = (typeof CURRENT_DATASET !== 'undefined')")
    add("                      ? CURRENT_DATASET : 'tonghop';")
    add("            document.querySelectorAll('.ds-btn, .ds-sub-btn').forEach(function(b) {")
    add("                b.classList.remove('active');")
    add("            });")
    add("            if (cur === 'tonghop') {")
    add("                var tonghopBtn = document.querySelector('.ds-btn[data-dataset=\"tonghop\"]');")
    add("                if (tonghopBtn) tonghopBtn.classList.add('active');")
    add("                return;")
    add("            }")
    add("            if (window.FIXPY_DATASETS && window.FIXPY_DATASETS[cur]) {")
    add("                var fxBtn = document.querySelector('.ds-btn[data-dataset=\"' + cur + '\"]');")
    add("                if (fxBtn) fxBtn.classList.add('active');")
    add("                return;")
    add("            }")
    add("            var subBtn = document.querySelector('.ds-sub-btn[data-dataset=\"' + cur + '\"]');")
    add("            if (subBtn) subBtn.classList.add('active');")
    add("            var cnBtn = document.querySelector('.ds-btn[data-dataset-group=\"chuyen-nganh\"]');")
    add("            if (cnBtn && subBtn) cnBtn.classList.add('active');")
    add("        };")
    add("        window.__fixPyMarkPatched = true;")
    add("    }")
    add("")

    add("    function patchGetLimitedData() {")
    add("        if (window.__fixPyLimitedPatched) return;")
    add("        var origGet = window.getLimitedData")
    add("                    || (typeof getLimitedData !== 'undefined' ? getLimitedData : null);")
    add("        if (typeof origGet !== 'function') return;")
    add("        window.getLimitedData = function() {")
    add("            var currentDs = (typeof CURRENT_DATASET !== 'undefined')")
    add("                            ? CURRENT_DATASET : 'tonghop';")
    add("            if (currentDs === 'tonghop') {")
    add("                return origGet.apply(this, arguments);")
    add("            }")
    add("            if (!window.FIXPY_DATASETS || !window.FIXPY_DATASETS[currentDs]) {")
    add("                return origGet.apply(this, arguments);")
    add("            }")
    add("            var info = (typeof getTierInfo === 'function')")
    add("                       ? getTierInfo() : {};")
    add("            if (info.tier === 'active') {")
    add("                return RAW_DATA;")
    add("            }")
    add("            var override = window.__onboardingOverride;")
    add("            if (override && Array.isArray(override) && override.length > 0")
    add("                && typeof state !== 'undefined' && state")
    add("                && !state.search && !state.hsk && !state.subject) {")
    add("                var currentStts = {};")
    add("                RAW_DATA.forEach(function(r) { currentStts[r.stt] = true; });")
    add("                var filtered = override.filter(function(r) {")
    add("                    return currentStts[r.stt];")
    add("                });")
    add("                if (filtered.length > 0) {")
    add("                    var max = info.maxQuestions || 60;")
    add("                    return filtered.slice(0, max);")
    add("                }")
    add("            }")
    add("            var max2 = info.maxQuestions || 60;")
    add("            return RAW_DATA.slice(0, max2);")
    add("        };")
    add("        window.__fixPyLimitedPatched = true;")
    add("    }")
    add("")

    add("    function bindTab(dsId) {")
    add("        var btn = document.querySelector('.ds-btn[data-dataset=\"' + dsId + '\"]');")
    add("        if (!btn) return;")
    add("        if (btn.__fixPyBound) return;")
    add("        var cloned = btn.cloneNode(true);")
    add("        btn.parentNode.replaceChild(cloned, btn);")
    add("        cloned.__fixPyBound = true;")
    add("        cloned.addEventListener('click', function(e) {")
    add("            e.stopImmediatePropagation();")
    add("            e.stopPropagation();")
    add("            e.preventDefault();")
    add("            console.log('[fix.py] click tab ' + dsId);")
    add("            var sub = document.getElementById('dsSubWrap');")
    add("            if (sub) sub.style.display = 'none';")
    add("            document.querySelectorAll('.ds-btn, .ds-sub-btn').forEach(function(b) {")
    add("                b.classList.remove('active');")
    add("            });")
    add("            this.classList.add('active');")
    add("            if (typeof window.__switchRawData === 'function') {")
    add("                window.__switchRawData(dsId);")
    add("            }")
    add("            if (typeof state !== 'undefined' && state) {")
    add("                state.search = '';")
    add("                state.hsk = '';")
    add("                state.subject = '';")
    add("            }")
    add("            try {")
    add("                var si = document.getElementById('searchInput');")
    add("                var hf = document.getElementById('hskFilter');")
    add("                var sf = document.getElementById('subjectFilter');")
    add("                if (si) si.value = '';")
    add("                if (hf) hf.value = '';")
    add("                if (sf) sf.value = '';")
    add("                var cb = document.getElementById('clearSearchBtn');")
    add("                if (cb) cb.classList.remove('show');")
    add("            } catch(err) {}")
    add("            var savedTopics = null;")
    add("            if (typeof loadOnboardingSelection === 'function') {")
    add("                try {")
    add("                    var saved = loadOnboardingSelection();")
    add("                    if (saved && saved.topics && saved.topics.length > 0) {")
    add("                        savedTopics = saved.topics;")
    add("                    }")
    add("                } catch(e) {}")
    add("            }")
    add("            try {")
    add("                if (typeof buildFilters === 'function') buildFilters();")
    add("                if (typeof applyFilter === 'function') applyFilter();")
    add("                if (typeof updateResultCount === 'function') updateResultCount();")
    add("                if (savedTopics && savedTopics.length > 0")
    add("                    && typeof applyOnboardingSelection === 'function') {")
    add("                    try {")
    add("                        var cfg = (typeof getOnboardingConfig === 'function')")
    add("                                  ? getOnboardingConfig() : null;")
    add("                        if (cfg) {")
    add("                            var saved2 = loadOnboardingSelection();")
    add("                            window.__onboardingAutoPicked = saved2 ? !!saved2.auto_picked : false;")
    add("                            applyOnboardingSelection(savedTopics, false);")
    add("                        }")
    add("                    } catch(e2) {")
    add("                        console.warn('[fix.py] applyOnboarding error:', e2);")
    add("                    }")
    add("                }")
    add("                document.querySelectorAll('.ds-btn, .ds-sub-btn').forEach(function(b) {")
    add("                    b.classList.remove('active');")
    add("                });")
    add("                this.classList.add('active');")
    add("            } catch(err) {")
    add("                console.warn('[fix.py] re-render error:', err);")
    add("            }")
    add("            setTimeout(function() {")
    add("                var mainEl = document.getElementById('mainContent');")
    add("                if (mainEl) {")
    add("                    var yOffset = mainEl.getBoundingClientRect().top")
    add("                                + window.scrollY - 100;")
    add("                    window.scrollTo({ top: yOffset, behavior: 'smooth' });")
    add("                }")
    add("            }, 100);")
    add("        }, true);")
    add("    }")
    add("")

    add("    function patchApplyOnboarding() {")
    add("        if (window.__fixPyApplyOnbPatched) return;")
    add("        var origApply = window.applyOnboardingSelection")
    add("                      || (typeof applyOnboardingSelection !== 'undefined'")
    add("                          ? applyOnboardingSelection : null);")
    add("        if (typeof origApply !== 'function') return;")
    add("        window.applyOnboardingSelection = function(topics, scrollTop) {")
    add("            var currentDs = (typeof CURRENT_DATASET !== 'undefined')")
    add("                            ? CURRENT_DATASET : 'tonghop';")
    add("            if (!window.FIXPY_DATASETS || !window.FIXPY_DATASETS[currentDs]) {")
    add("                return origApply.apply(this, arguments);")
    add("            }")
    add("            var cfg = (typeof getOnboardingConfig === 'function')")
    add("                      ? getOnboardingConfig() : null;")
    add("            if (!cfg) return;")
    add("            var maxQ = cfg.max_questions;")
    add("            var isUnlimitedQ = (maxQ === -1 || maxQ === Infinity);")
    add("            var allowedHsk;")
    add("            if (cfg.hsk_allowed && Array.isArray(cfg.hsk_allowed) && cfg.hsk_allowed.length > 0) {")
    add("                allowedHsk = cfg.hsk_allowed.map(function(n) { return 'HSK' + n; });")
    add("            } else {")
    add("                allowedHsk = (typeof getAllowedHskList === 'function')")
    add("                             ? getAllowedHskList()")
    add("                             : ['HSK1','HSK2','HSK3','HSK4','HSK5','HSK6'];")
    add("            }")
    add("            var pool = RAW_DATA.filter(function(r) {")
    add("                if (allowedHsk.indexOf(r.hsk) === -1) return false;")
    add("                var s = (r.subject || '').trim();")
    add("                return topics.indexOf(s) !== -1;")
    add("            });")
    add("            pool.sort(function(a, b) {")
    add("                return (parseInt(a.stt) || 0) - (parseInt(b.stt) || 0);")
    add("            });")
    add("            var final = [];")
    add("            if (isUnlimitedQ) {")
    add("                final = pool.slice();")
    add("            } else {")
    add("                var maxPerTopic = (typeof getMaxPerTopic === 'function')")
    add("                                 ? getMaxPerTopic(maxQ, RAW_DATA)")
    add("                                 : Math.max(1, Math.ceil(maxQ / Math.max(1, topics.length)));")
    add("                var topicCount = {};")
    add("                var perHsk = Math.ceil(maxQ / allowedHsk.length);")
    add("                var hskCount = {};")
    add("                allowedHsk.forEach(function(h) { hskCount[h] = 0; });")
    add("                for (var i = 0; i < pool.length && final.length < maxQ; i++) {")
    add("                    var r = pool[i];")
    add("                    var s = (r.subject || '').trim() || '__no_subject__';")
    add("                    if ((topicCount[s] || 0) >= maxPerTopic) continue;")
    add("                    if (r.hsk && hskCount[r.hsk] !== undefined && hskCount[r.hsk] >= perHsk) continue;")
    add("                    final.push(r);")
    add("                    topicCount[s] = (topicCount[s] || 0) + 1;")
    add("                    if (r.hsk && hskCount[r.hsk] !== undefined) hskCount[r.hsk]++;")
    add("                }")
    add("                if (final.length < maxQ) {")
    add("                    var usedIds = {};")
    add("                    final.forEach(function(r) { usedIds[r.stt] = true; });")
    add("                    for (var p = 0; p < pool.length && final.length < maxQ; p++) {")
    add("                        var rp = pool[p];")
    add("                        if (usedIds[rp.stt]) continue;")
    add("                        var sp = (rp.subject || '').trim() || '__no_subject__';")
    add("                        if ((topicCount[sp] || 0) >= maxPerTopic) continue;")
    add("                        final.push(rp);")
    add("                        usedIds[rp.stt] = true;")
    add("                        topicCount[sp] = (topicCount[sp] || 0) + 1;")
    add("                    }")
    add("                }")
    add("                if (final.length > maxQ) final = final.slice(0, maxQ);")
    add("            }")
    add("            final.sort(function(a, b) {")
    add("                return (parseInt(a.stt) || 0) - (parseInt(b.stt) || 0);")
    add("            });")
    add("            window.__onboardingOverride = final;")
    add("            if (typeof state !== 'undefined' && state) {")
    add("                state.search = '';")
    add("                state.hsk = '';")
    add("                state.subject = '';")
    add("            }")
    add("            try {")
    add("                var si = document.getElementById('searchInput');")
    add("                if (si) si.value = '';")
    add("                var cb = document.getElementById('clearSearchBtn');")
    add("                if (cb) cb.classList.remove('show');")
    add("            } catch(e) {}")
    add("            if (typeof applyFilter === 'function') applyFilter();")
    add("            if (typeof updateResultCount === 'function') updateResultCount();")
    add("            if (typeof showOnboardingActiveBanner === 'function') {")
    add("                showOnboardingActiveBanner(topics, final.length);")
    add("            }")
    add("            if (scrollTop) {")
    add("                setTimeout(function() {")
    add("                    var mainEl = document.getElementById('mainContent');")
    add("                    if (mainEl) {")
    add("                        var yOffset = mainEl.getBoundingClientRect().top")
    add("                                    + window.scrollY - 100;")
    add("                        window.scrollTo({ top: yOffset, behavior: 'smooth' });")
    add("                    }")
    add("                }, 200);")
    add("            }")
    add("        };")
    add("        window.__fixPyApplyOnbPatched = true;")
    add("    }")
    add("")

    add("    function bindAll() {")
    add("        patchSwitchRawData();")
    add("        patchGetLimitedData();")
    add("        patchApplyOnboarding();")
    add("        NEW_IDS.forEach(bindTab);")
    add("        patchMarkActive();")
    add("    }")
    add("")
    add("    if (document.readyState === 'loading') {")
    add("        document.addEventListener('DOMContentLoaded', bindAll);")
    add("    } else {")
    add("        bindAll();")
    add("    }")
    add("")
    add("    var _timer = null;")
    add("    var observer = new MutationObserver(function() {")
    add("        clearTimeout(_timer);")
    add("        _timer = setTimeout(bindAll, 200);")
    add("    });")
    add("    if (document.body) {")
    add("        observer.observe(document.body, { childList: true, subtree: true });")
    add("    }")
    add("")
    add("    console.log('[fix.py] Da bind ' + NEW_IDS.length + ' tab:', NEW_IDS);")
    add("})();")
    add("</script>")

    return "\n".join(L)


# =================================================================
#  BUILD HTML BUTTON 2-ROWS
# =================================================================
def _build_button_2rows(data_attr, icon, title_html, sub,
                        extra_cls="", extra_html="", extra_attrs=""):
    """Sinh HTML nút 2 hàng: icon | (title + sub)."""
    return (
        '<button class="ds-btn ds-btn-primary' + extra_cls + '" '
        + data_attr + ' ' + extra_attrs + '>\n'
        '            <i class="fas ' + icon + ' ds-btn-icon"></i>\n'
        '            <span class="ds-btn-text">\n'
        '                <span class="ds-btn-title">' + title_html + '</span>\n'
        '                <span class="ds-btn-sub">' + sub + '</span>\n'
        '            </span>\n'
        '            ' + extra_html + '\n'
        '        </button>'
    )


# =================================================================
#  BUILD CSS LAYOUT
# =================================================================
def build_layout_css(new_datasets, add_vocab):
    css_lines = []

    # CSS BUTTONS 2 HÀNG (COVER TOÀN BỘ NÚT)
    css_lines.append(BUTTONS_2ROWS_CSS)

    # GRID cho CHUYÊN NGÀNH sub-buttons
    css_lines.append("")
    css_lines.append("/* GRID DEU CHO TAB CON CHUYEN NGANH */")
    css_lines.append(".ds-sub-grid {")
    css_lines.append("    display: grid !important;")
    css_lines.append("    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;")
    css_lines.append("    gap: .55rem !important;")
    css_lines.append("    align-items: stretch !important;")
    css_lines.append("}")
    css_lines.append("@media (min-width: 600px) {")
    css_lines.append("    .ds-sub-grid { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }")
    css_lines.append("}")
    css_lines.append("@media (min-width: 900px) {")
    css_lines.append("    .ds-sub-grid { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }")
    css_lines.append("}")
    css_lines.append(".ds-sub-btn {")
    css_lines.append("    width: 100% !important;")
    css_lines.append("    min-width: 0 !important;")
    css_lines.append("    max-width: 100% !important;")
    css_lines.append("    height: 100% !important;")
    css_lines.append("    min-height: 44px !important;")
    css_lines.append("    padding: .55rem .7rem !important;")
    css_lines.append("    justify-content: flex-start !important;")
    css_lines.append("    border-radius: 12px !important;")
    css_lines.append("    font-size: clamp(.68rem, 1.9vw, .82rem) !important;")
    css_lines.append("    white-space: normal !important;")
    css_lines.append("    word-break: break-word !important;")
    css_lines.append("    overflow-wrap: anywhere !important;")
    css_lines.append("    line-height: 1.25 !important;")
    css_lines.append("    text-align: left !important;")
    css_lines.append("}")
    css_lines.append(".ds-sub-btn span {")
    css_lines.append("    flex: 1 1 auto !important;")
    css_lines.append("    min-width: 0 !important;")
    css_lines.append("    display: -webkit-box !important;")
    css_lines.append("    -webkit-line-clamp: 2 !important;")
    css_lines.append("    -webkit-box-orient: vertical !important;")
    css_lines.append("    overflow: hidden !important;")
    css_lines.append("}")

    # Style riêng cho tab mới sinh
    for ds in new_datasets:
        i = ds["id"]
        sel = '.ds-btn[data-dataset="' + i + '"]'
        css_lines.append("")
        css_lines.append("/* Style cho tab " + i + " */")
        css_lines.append(sel + ".active {")
        css_lines.append("    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;")
        css_lines.append("    color: #fff !important;")
        css_lines.append("    border-color: transparent !important;")
        css_lines.append("    box-shadow: 0 4px 12px rgba(124, 58, 237, .35) !important;")
        css_lines.append("}")

    # VOCAB CSS + WARNING BANNER
    if add_vocab:
        css_lines.append("")
        css_lines.append("/* VOCAB PREMIUM CSS */")
        css_lines.append(build_vocab_css(VOCAB_ID))
        css_lines.append(VOCAB_WARNING_CSS)

    return "\n".join(css_lines) + "\n"


# =================================================================
#  PATCH BUTTONS — REWRITE CÁC NÚT CỨNG SANG 2 HÀNG
# =================================================================
def patch_existing_buttons(html):
    """Rewrite 3 nút cứng (tonghop, chuyen-nganh, favorites) sang 2 hàng."""
    print("")
    print("[PATCH 2.5] Rewrite nut co san -> layout 2 hang gon...")

    # Nút TỔNG HỢP
    new_tonghop = _build_button_2rows(
        data_attr='data-dataset="tonghop"',
        icon="fa-book-open",
        title_html="<b>1750+</b> Câu phản xạ",
        sub="Văn phòng · Công xưởng",
        extra_cls=" active",
    )
    pat_th = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset="tonghop"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    html, n = pat_th.subn(new_tonghop, html, count=1)
    if n:
        print("   [OK] Rewrite nut Tong hop")

    # Nút CHUYÊN NGÀNH
    new_cn = _build_button_2rows(
        data_attr='data-dataset-group="chuyen-nganh"',
        icon="fa-industry",
        title_html="<b>Chuyên ngành</b>",
        sub="Theo lĩnh vực",
        extra_html=(
            '<i class="fas fa-chevron-down ds-arrow"></i>\n'
            '            <span class="ds-new-badge" id="dsNewBadge">NEW</span>'
        ),
        extra_attrs='id="dsChuyenNganhBtn"',
    )
    pat_cn = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset-group="chuyen-nganh"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    html, n = pat_cn.subn(new_cn, html, count=1)
    if n:
        print("   [OK] Rewrite nut Chuyen nganh")

    # Nút YÊU THÍCH (nếu có)
    new_fav = _build_button_2rows(
        data_attr='data-dataset-group="favorites"',
        icon="fa-heart",
        title_html="<b>Yêu thích</b>",
        sub="Câu đã lưu",
    )
    pat_fav = re.compile(
        r'<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset-group="favorites"[^>]*>.*?</button>',
        re.MULTILINE | re.DOTALL
    )
    if pat_fav.search(html):
        html, n = pat_fav.subn(new_fav, html, count=1)
        if n:
            print("   [OK] Rewrite nut Yeu thich")
    else:
        print("   [skip] Khong co nut Yeu thich")

    return html


# =================================================================
#  MAIN
# =================================================================
def main():
    print("=" * 62)
    print("[fix.py] Auto-scan data/ -> them tab rieng cho moi file")
    print("=" * 62)

    if not os.path.isfile(INDEX_HTML):
        print("[X] Khong thay " + INDEX_HTML + ". Chay convert.py truoc.")
        sys.exit(1)

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # SCAN tab thường
    datasets = scan_data_dir()

    # ĐỌC FILE TỪ VỰNG PREMIUM
    vocab_data = []
    vocab_real_path = None
    if HAS_VOCAB_MODULE:
        print("")
        print("[VOCAB] Kiem tra file tu vung: " + VOCAB_FILE)
        vocab_real_path = _find_file_safe(VOCAB_FILE)
        if vocab_real_path:
            print("[VOCAB] Tim thay: " + os.path.basename(vocab_real_path))
            vocab_data = read_vocab_excel(vocab_real_path)
            if not vocab_data:
                print("[VOCAB] [!] File rong hoac loi")
        else:
            print("[VOCAB] Khong co file tu vung - bo qua")

    # KIỂM TRA CÓ GÌ MỚI
    all_new = []
    for ds in datasets:
        marker = 'data-dataset="' + ds["id"] + '"'
        if marker not in html:
            all_new.append(ds)
        else:
            print("   [skip] '" + ds["id"] + "' da co trong HTML")

    vocab_exists_in_html = 'data-dataset="' + VOCAB_ID + '"' in html
    add_vocab = bool(vocab_data) and not vocab_exists_in_html

    # =============================================================
    #  PATCH 2: BUTTONS MỚI (2 HÀNG)
    # =============================================================
    print("")
    print("[PATCH 2] Them button tabs moi (2 hang gon)...")
    new_btns = ""
    for ds in all_new:
        label = ds["name"]
        count = ds["count"]

        m = re.match(r'^(\d+\+?)\s+(.+)$', label)
        if m:
            title_html = '<b>' + m.group(1) + '</b> ' + _html_escape(m.group(2))
            sub = "Câu giao tiếp"
        else:
            title_html = '<b>' + str(count) + '</b> ' + _html_escape(label)
            sub = "Bộ dữ liệu"

        new_btns += (
            '\n        <button class="ds-btn ds-btn-primary" '
            'data-dataset="' + ds["id"] + '">\n'
            '            <i class="fas ' + ds["icon"] + ' ds-btn-icon"></i>\n'
            '            <span class="ds-btn-text">\n'
            '                <span class="ds-btn-title">' + title_html + '</span>\n'
            '                <span class="ds-btn-sub">' + sub + '</span>\n'
            '            </span>\n'
            '        </button>'
        )

    if add_vocab:
        new_btns += build_vocab_tab_html(VOCAB_ID, VOCAB_LABEL)

    if new_btns:
        pat_after_tonghop = re.compile(
            r'(<button[^>]*class="[^"]*ds-btn[^"]*"[^>]*data-dataset="tonghop"[^>]*>.*?</button>)',
            re.MULTILINE | re.DOTALL
        )
        html, n = pat_after_tonghop.subn(
            lambda m: m.group(1) + new_btns,
            html, count=1
        )

        if n > 0:
            print("   [OK] Da chen button moi (sau 'Tong hop')")
        else:
            print("   [!] Khong thay nut 'tonghop' -> fallback truoc 'chuyen-nganh'")
            pat_before_cn = re.compile(
                r'(\s*)(<button\s+class="[^"]*ds-btn[^"]*"\s+[^>]*data-dataset-group="chuyen-nganh")',
                re.MULTILINE
            )
            html, n = pat_before_cn.subn(
                lambda m: m.group(1) + new_btns + '\n        ' + m.group(2),
                html, count=1
            )
            if n == 0:
                print("[X] Khong tim thay ca nut 'tonghop' lan 'chuyen-nganh'")
                sys.exit(1)
            print("   [OK] Da chen button moi (fallback)")
    else:
        print("   [skip] Khong co nut moi can them")

    # =============================================================
    #  PATCH 2.5: REWRITE NÚT CỨNG SANG 2 HÀNG
    # =============================================================
    html = patch_existing_buttons(html)

    # =============================================================
    #  PATCH 3: CSS
    # =============================================================
    print("")
    print("[PATCH 3] CSS layout + buttons 2 hang...")

    css = build_layout_css(all_new, add_vocab)

    pat_style = re.compile(r'(\s*)(</style>)', re.MULTILINE)
    html, n = pat_style.subn(
        lambda m: m.group(1) + css + m.group(1) + m.group(2),
        html, count=1
    )
    if n == 0:
        print("   [!] Khong tim thay </style>")
    else:
        print("   [OK] Da inject CSS")

    # =============================================================
    #  PATCH 4: JS
    # =============================================================
    print("")
    print("[PATCH 4] JS binding...")

    ids_js = json.dumps([ds["id"] for ds in all_new])

    datasets_dict = {}
    for ds in all_new:
        datasets_dict[ds["id"]] = ds

    if add_vocab:
        datasets_dict[VOCAB_ID] = {
            "id": VOCAB_ID,
            "name": VOCAB_LABEL,
            "icon": "fa-book",
            "color": "#f59e0b",
            "data": vocab_data,
            "count": len(vocab_data),
            "source": os.path.basename(vocab_real_path),
            "type": "premium",
            "group": "fixpy",
        }

    datasets_json = _escape_json_for_script(datasets_dict)

    js = build_js_override(ids_js, datasets_json)

    if add_vocab:
        js += '\n<script>\n'
        js += build_vocab_js_override(VOCAB_ID)
        js += '\n' + build_vocab_js_patch()
        js += '\n</script>\n'

    modal_html = ""
    if add_vocab:
        modal_html = build_vocab_modal_html()

    pat_body = re.compile(r'(\s*)(</body>)', re.MULTILINE)
    html, n = pat_body.subn(
        lambda m: m.group(1) + modal_html + '\n' + js + m.group(1) + m.group(2),
        html, count=1
    )
    if n == 0:
        print("[X] Khong tim thay </body>")
        sys.exit(1)
    print("   [OK] Da inject JS + modal")

    # GHI FILE
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(INDEX_HTML) / 1024

    print("")
    print("=" * 62)
    print("[fix.py] HOAN TAT! Da patch " + INDEX_HTML)
    print("[fix.py] Kich thuoc: " + str(round(size_kb, 1)) + " KB")

    if all_new:
        print("[fix.py] Tab thuong da them:")
        for ds in all_new:
            print("   - " + ds["name"] + " (" + str(ds["count"]) + " cau)")

    if add_vocab:
        print("[fix.py] Tab Tu vung PREMIUM: " + str(len(vocab_data)) + " tu")
        print("[fix.py]    (chi Admin + Premium moi mo duoc)")

    print("[fix.py] Layout: PC 4 cot - Mobile 2 cot")
    print("[fix.py] Buttons: 2 hang + icon watermark chim")
    print("[fix.py] CHI 1 TAB ACTIVE tai mot thoi diem")
    print("=" * 62)


if __name__ == "__main__":
    main()
