# -*- coding: utf-8 -*-
"""Patch: nút Chấm điểm + Xem đáp án + chi tiết lỗi to rõ."""

import re


def _replace_func(js, func_name, new_body):
    pattern = r'function ' + func_name + r'\(\)\s*\{.*?\n\}'
    match = re.search(pattern, js, flags=re.DOTALL)
    if not match:
        return js, 0
    return js[:match.start()] + new_body + js[match.end():], 1


def patch_html(ui_html):
    new_btn = '<button id="pfGradeToggleBtn" type="button"><i class="fas fa-check-double"></i> Chấm điểm</button>'
    old_btn = '<button id="pfHintBtn"><i class="fas fa-lightbulb"></i> Gợi ý</button>'
    if old_btn in ui_html:
        ui_html = ui_html.replace(old_btn, new_btn)
        print("[Patch] Đổi nút Gợi ý → Chấm điểm (exact)")
        return ui_html
    pattern = r'<button[^>]*id="pfHintBtn"[^>]*>.*?</button>'
    match = re.search(pattern, ui_html, flags=re.DOTALL)
    if match:
        ui_html = ui_html[:match.start()] + new_btn + ui_html[match.end():]
        print("[Patch] Đổi nút Gợi ý → Chấm điểm (regex)")
    else:
        print("[Patch] WARN: không tìm thấy pfHintBtn")
    return ui_html


def patch_css(ui_css):
    extra_css = """

/* ═══ Nút Chấm điểm + Xem đáp án ═══ */
#pfGradeToggleBtn,
#pfRevealBtn {
    padding: .6rem 1rem !important;
    border-radius: 50px !important;
    font-size: .85rem !important;
    font-weight: 700 !important;
    font-family: inherit !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .4rem !important;
    transition: all .2s ease !important;
    border: 2px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text-2) !important;
    min-width: 0 !important;
    line-height: 1.2 !important;
}
#pfGradeToggleBtn:hover,
#pfRevealBtn:hover {
    border-color: var(--primary) !important;
    color: var(--primary) !important;
    background: var(--primary-light) !important;
    transform: translateY(-1px) !important;
}
#pfGradeToggleBtn i,
#pfRevealBtn i {
    font-size: .9rem !important;
}
#pfGradeToggleBtn.active {
    background: var(--primary) !important;
    color: #fff !important;
    border-color: var(--primary) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, .3) !important;
    transform: none !important;
}
#pfGradeToggleBtn.active:hover {
    background: var(--primary-dark) !important;
    border-color: var(--primary-dark) !important;
    transform: translateY(-1px) !important;
}
#pfGradeToggleBtn.active i {
    animation: favHeartPop .4s cubic-bezier(.34, 1.56, .64, 1);
}
@keyframes favHeartPop {
    0%   { transform: scale(1); }
    40%  { transform: scale(1.4); }
    70%  { transform: scale(.9); }
    100% { transform: scale(1); }
}
#pfRevealBtn.revealed {
    background: var(--success) !important;
    color: #fff !important;
    border-color: var(--success) !important;
    border-style: solid !important;
    box-shadow: 0 4px 12px rgba(22, 163, 74, .3) !important;
}
#pfRevealBtn.revealed:hover {
    filter: brightness(1.1) !important;
}
.reveal-actions {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: .6rem !important;
}
[data-theme="dark"] #pfGradeToggleBtn,
[data-theme="dark"] #pfRevealBtn {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border-color: var(--border-strong) !important;
}
[data-theme="dark"] #pfGradeToggleBtn:hover,
[data-theme="dark"] #pfRevealBtn:hover {
    border-color: var(--primary) !important;
    color: #93c5fd !important;
    background: rgba(59, 130, 246, .15) !important;
}
[data-theme="dark"] #pfGradeToggleBtn.active {
    background: var(--primary) !important;
    color: #fff !important;
    border-color: var(--primary) !important;
}
[data-theme="dark"] #pfRevealBtn.revealed {
    background: var(--success) !important;
    color: #fff !important;
}


/* ═══════════════════════════════════════════════════════════
   Chi tiết lỗi — Container + err-item + highlight
   ═══════════════════════════════════════════════════════════ */

/* Container — flex wrap, mỗi item là 1 khối */
.ai-reason,
.card-check .ai-reason,
.practice-full-status .ai-reason {
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .35rem .5rem !important;
    font-size: .85rem !important;
    color: var(--text) !important;
    font-weight: 700 !important;
    font-style: normal !important;
    margin-top: .5rem !important;
    line-height: 1.6 !important;
    text-align: center !important;
    padding: .6rem .9rem !important;
    background: var(--surface-2) !important;
    border: 1px dashed var(--border-strong) !important;
    border-radius: 10px !important;
}
[data-theme="dark"] .ai-reason {
    background: var(--surface-2) !important;
    border-color: var(--border-strong) !important;
}

/* Mỗi lỗi — 1 khối nhỏ, KHÔNG tách */
.ai-reason .err-item {
    display: inline-flex !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    gap: .3rem !important;
    flex-shrink: 0 !important;
    padding: .25rem .55rem !important;
    border-radius: 6px !important;
    background: var(--surface) !important;
    white-space: nowrap !important;
    transition: background .2s ease !important;
}

/* Xen kẽ nền cho dễ phân biệt */
.ai-reason .err-item:nth-child(even) {
    background: var(--bg) !important;
}

/* Highlight cả khối khi bấm ô đỏ */
.ai-reason .err-item.highlight {
    background: linear-gradient(135deg, #fef3c7, #fde68a) !important;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, .55), 0 4px 12px rgba(245, 158, 11, .3) !important;
    animation: errItemPulse .6s ease-in-out 2 !important;
}
[data-theme="dark"] .ai-reason .err-item.highlight {
    background: linear-gradient(135deg, #78350f, #92400e) !important;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, .5), 0 4px 12px rgba(245, 158, 11, .3) !important;
}
@keyframes errItemPulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.03); }
}

/* Hán tự — TO, ĐẬM */
.ai-reason .err-hanzi {
    font-family: var(--font-zh, 'PingFang SC', 'Microsoft YaHei', sans-serif) !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    line-height: 1.2 !important;
    padding: 0 .15em !important;
    display: inline-block !important;
    vertical-align: middle !important;
}

/* Pinyin — nhỏ, nghiêng, xám nhạt */
.ai-reason .err-pinyin {
    font-size: .72rem !important;
    font-style: italic !important;
    color: var(--text-3) !important;
    font-weight: 500 !important;
    display: inline-block !important;
    vertical-align: middle !important;
    margin-left: .15em !important;
    opacity: .85 !important;
}

/* Mũi tên → */
.ai-reason .err-arrow {
    font-size: 1.1rem !important;
    font-weight: 900 !important;
    color: var(--primary) !important;
    margin: 0 .3rem !important;
    display: inline-block !important;
    vertical-align: middle !important;
}

/* Dấu phân cách · (ẩn đi vì đã dùng err-item) */
.ai-reason .err-sep {
    display: none !important;
}

/* Nhãn "Thiếu" / "Thừa" */
.ai-reason .err-label {
    font-size: .85rem !important;
    font-weight: 700 !important;
    color: var(--text-2) !important;
    display: inline-block !important;
    vertical-align: middle !important;
}

/* Dark mode */
[data-theme="dark"] .ai-reason .err-pinyin {
    color: #94a3b8 !important;
}
[data-theme="dark"] .ai-reason .err-arrow {
    color: #93c5fd !important;
}
[data-theme="dark"] .ai-reason .err-label {
    color: var(--text-3) !important;
}

/* "Đang gõ..." / "Đang chấm..." — không khung */
.practice-full-status .ai-reason:only-child {
    background: transparent !important;
    border: none !important;
    color: var(--text-2) !important;
    font-weight: 600 !important;
    padding: .35rem 0 !important;
}

/* Mobile — mỗi lỗi 1 dòng */
/* ═══════════════════════════════════════════════════════════
   RESPONSIVE — Số cột theo độ rộng màn hình
   ═══════════════════════════════════════════════════════════ */

/* Mobile NHỎ (< 500px) — 1 cột, mỗi lỗi 1 dòng */
@media (max-width: 499px) {
    #pfGradeToggleBtn,
    #pfRevealBtn {
        padding: .55rem .75rem !important;
        font-size: .78rem !important;
    }
    #pfGradeToggleBtn i,
    #pfRevealBtn i {
        font-size: .82rem !important;
    }
    .ai-reason {
        display: grid !important;
        grid-template-columns: 1fr !important;
        gap: .35rem !important;
        align-items: stretch !important;
    }
    .ai-reason .err-item {
        width: 100% !important;
        justify-content: flex-start !important;
        padding: .35rem .6rem !important;
    }
    .ai-reason .err-hanzi {
        font-size: 1.2rem !important;
    }
    .ai-reason .err-pinyin {
        font-size: .68rem !important;
    }
    .ai-reason .err-arrow {
        font-size: 1rem !important;
    }
}

/* Mobile LỚN / Tablet (500px – 899px) — 2 cột */
@media (min-width: 500px) and (max-width: 899px) {
    .ai-reason {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: .35rem .5rem !important;
        align-items: stretch !important;
    }
    .ai-reason .err-item {
        width: 100% !important;
        justify-content: flex-start !important;
        padding: .35rem .6rem !important;
    }
}

/* Desktop (>= 900px) — 3 cột */
@media (min-width: 900px) {
    .ai-reason {
        display: grid !important;
        grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
        gap: .4rem .55rem !important;
        align-items: stretch !important;
    }
    .ai-reason .err-item {
        width: 100% !important;
        justify-content: flex-start !important;
        padding: .35rem .6rem !important;
    }
}

/* ═══════════════════════════════════════════════════════════
   Nút "Xem" bầu dục + Modal mẹo nhớ
   ═══════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════
   Nút "Xem" bầu dục — màu nhạt, dịu mắt
   ═══════════════════════════════════════════════════════════ */
.ai-reason .err-info-btn {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .25rem !important;
    padding: .35rem .7rem !important;
    margin: 0 .35rem !important;
    border: 1.5px solid rgba(239, 68, 68, .4) !important;
    border-radius: 50px !important;
    background: linear-gradient(135deg, #fef2f2, #fee2e2) !important;
    color: #dc2626 !important;
    font-size: .72rem !important;
    font-weight: 700 !important;
    font-family: inherit !important;
    line-height: 1 !important;
    cursor: pointer !important;
    transition: all .2s cubic-bezier(.34, 1.56, .64, 1) !important;
    flex-shrink: 0 !important;
    vertical-align: middle !important;
    box-shadow: 0 1px 3px rgba(220, 38, 38, .1) !important;
    white-space: nowrap !important;
    text-transform: uppercase !important;
    letter-spacing: .3px !important;
    min-width: 58px !important;
    height: 26px !important;
}
.ai-reason .err-info-btn i {
    font-size: .8rem !important;
    line-height: 1 !important;
    color: #ef4444 !important;
}
.ai-reason .err-info-btn:hover {
    background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
    border-color: #ef4444 !important;
    transform: translateY(-1px) scale(1.03) !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, .25) !important;
}
.ai-reason .err-info-btn:active {
    transform: translateY(0) scale(.97) !important;
    box-shadow: 0 1px 3px rgba(220, 38, 38, .15) !important;
}
[data-theme="dark"] .ai-reason .err-info-btn {
    background: linear-gradient(135deg, rgba(239, 68, 68, .15), rgba(220, 38, 38, .1)) !important;
    border-color: rgba(248, 113, 113, .4) !important;
    color: #fca5a5 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .2) !important;
}
[data-theme="dark"] .ai-reason .err-info-btn i {
    color: #fca5a5 !important;
}
[data-theme="dark"] .ai-reason .err-info-btn:hover {
    background: linear-gradient(135deg, rgba(239, 68, 68, .25), rgba(220, 38, 38, .2)) !important;
    border-color: #fca5a5 !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, .35) !important;
}

/* ═══════════════════════════════════════════════════════════
   Modal mẹo nhớ
   ═══════════════════════════════════════════════════════════ */
.mnemonic-modal {
    position: fixed !important;
    inset: 0 !important;
    background: rgba(15, 23, 42, .75) !important;
    backdrop-filter: blur(6px) !important;
    -webkit-backdrop-filter: blur(6px) !important;
    z-index: 9999 !important;
    display: none !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 1rem !important;
    animation: mnemonicFadeIn .2s ease !important;
}
.mnemonic-modal.show {
    display: flex !important;
}

@keyframes mnemonicFadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

.mnemonic-box {
    background: var(--surface, #fff) !important;
    border-radius: 18px !important;
    max-width: 480px !important;
    width: 100% !important;
    max-height: 85vh !important;
    overflow-y: auto !important;
    padding: 1.25rem !important;
    box-shadow: 0 24px 70px rgba(0, 0, 0, .4) !important;
    animation: mnemonicSlideUp .35s cubic-bezier(.34, 1.56, .64, 1) !important;
    position: relative !important;
}

@keyframes mnemonicSlideUp {
    from { transform: translateY(30px) scale(.95); opacity: 0; }
    to   { transform: translateY(0) scale(1); opacity: 1; }
}

.mnemonic-loading {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: .75rem !important;
    padding: 2rem 1rem !important;
    color: var(--text-2, #475569) !important;
    font-size: .9rem !important;
}
.mnemonic-spinner {
    width: 32px !important;
    height: 32px !important;
    border: 3px solid var(--border, #e2e8f0) !important;
    border-top-color: var(--primary, #2563eb) !important;
    border-radius: 50% !important;
    animation: mnemonicSpin .8s linear infinite !important;
}

@keyframes mnemonicSpin {
    to { transform: rotate(360deg); }
}

.mnemonic-header {
    display: flex !important;
    align-items: center !important;
    gap: .75rem !important;
    margin-bottom: 1rem !important;
    padding-bottom: .85rem !important;
    border-bottom: 1px solid var(--border, #e2e8f0) !important;
}
.mnemonic-char {
    font-family: var(--font-zh, 'PingFang SC', 'Microsoft YaHei', sans-serif) !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    color: var(--text, #0f172a) !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
}
.mnemonic-pinyin {
    font-size: 1rem !important;
    font-style: italic !important;
    color: var(--text-3, #94a3b8) !important;
    font-weight: 500 !important;
}
.mnemonic-radical-tag {
    display: inline-flex !important;
    align-items: center !important;
    gap: .2rem !important;
    padding: .2rem .6rem !important;
    background: linear-gradient(135deg, #dbeafe, #bfdbfe) !important;
    color: #1d4ed8 !important;
    font-size: .72rem !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    margin-left: auto !important;
    margin-right: .5rem !important;
    white-space: nowrap !important;
}
[data-theme="dark"] .mnemonic-radical-tag {
    background: linear-gradient(135deg, rgba(59, 130, 246, .3), rgba(37, 99, 235, .25)) !important;
    color: #93c5fd !important;
}
.mnemonic-close {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    border: none !important;
    background: var(--surface-2, #f8fafc) !important;
    color: var(--text-2, #475569) !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: .85rem !important;
    flex-shrink: 0 !important;
    transition: all .15s !important;
}
.mnemonic-close:hover {
    background: var(--danger-light, #fee2e2) !important;
    color: var(--danger, #dc2626) !important;
    transform: rotate(90deg) !important;
}

.mnemonic-body {
    display: flex !important;
    flex-direction: column !important;
    gap: 1rem !important;
}

.mnemonic-section {
    background: var(--surface-2, #f8fafc) !important;
    border-radius: 10rempx !important;
    padding .: .75rem .9rem !important;
65}
.mnemonic-section-title {
   rem font-size: .72rem ! !important;
    font-weight: 800 !importantimportant;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
    color: var(--text-3, #94a3b8) !important;
    margin-bottom: .5rem !important;
    display: flex !important;
    align-items: center !important;
    gap: .35rem !important;
}

/* Bộ thủ */
.mnemonic-radical-row {
    display: flex !important;
    align-items: center !important;
    gap: .75rem !important;
    flex-wrap: wrap !important;
}
.mnemonic-rad-char {
    font-family: var(--font-zh, 'PingFang SC', sans-serif) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1d4ed8 !important;
    line-height: 1 !important;
}
.mnemonic-rad-info {
    display: flex !important;
    flex-direction: column !important;
    gap: .15rem !important;
}
.mnemonic-rad-name {
    font-size: .85rem !important;
    font-weight: 700 !important;
    color: #1d4ed8 !important;
}
[data-theme="dark"] .mnemonic-rad-name,
[data-theme="dark"] .mnemonic-rad-char {
    color: #93c5fd !important;
}
.mnemonic-rad-meaning {
    font-size: .8rem !important;
    color: var(--text-2, #475569) !important;
}

/* Thành phần */
.mnemonic-comp-list {
    display: flex !important;
    flex-direction: column !important;
    gap: .4rem !important;
}
.mnemonic-comp-item {
    display: flex !important;
    align-items: center !important;
    gap: .65rem !important;
    padding: .4rem .5rem !important;
    background: var(--surface, #fff) !important;
    border-radius: 8px !important;
}
.mnemonic-comp-char {
    font-family: var(--font-zh, 'PingFang SC', sans-serif) !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: var(--text, #0f172a) !important;
    line-height: 1 !important;
    min-width: 1.2em !important;
}
.mnemonic-comp-py {
    font-size: .75rem !important;
    font-style: italic !important;
    color: var(--text-3, #94a3b8) !important;
    min-width: 3.5em !important;
}
.mnemonic-comp-meaning {
    font-size: .82rem !important;
    color: var(--text-2, #475569) !important;
    flex: 1 !important;
}

/* Mẹo nhớ */
.mnemonic-text {
    background: linear-gradient(135deg, #fffbeb, #fef3c7) !important;
    border-left: 4px solid #f59e0b !important;
    padding: .75rem .9rem !important;
    border-radius: 8px !important;
    font-size: .88rem !important;
    color: #78350f !important;
    line-height: 1.7 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
}
[data-theme="dark"] .mnemonic-text {
    background: linear-gradient(135deg, rgba(245, 158, 11, .15), rgba(217, 119, 6, .1)) !important;
    color: #fcd34d !important;
}

/* Chữ dễ nhầm */
.mnemonic-similar-cards {
    display: flex !important;
    gap: .5rem !important;
    flex-wrap: wrap !important;
}
.mnemonic-sim-card {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    min-width: 70px !important;
    padding: .5;
    background: linear-gradient(135deg, #fef2f2, #fee2e2) !important;
    border: 2px solid #fecaca !important;
    border-radius: 10px !important;
    gap: .15rem !important;
    transition: all .15s !important;
}
.mnemonic-sim-card:hover {
    transform: translateY(-2px) !important;
    border-color: #ef4444 !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, .2) !important;
}
.mnemonic-sim-char {
    font-family: var(--font-zh, 'PingFang SC', sans-serif) !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
    line-height: 1 !important;
}
.mnemonic-sim-py {
    font-size: .7rem !important;
    font-style: italic !important;
    color: #6b7280 !important;
}
.mnemonic-sim-vi {
    font-size: .7rem !important;
    font-weight: 700 !important;
    color: #b91c1c !important;
    text-align: center !important;
}
[data-theme="dark"] .mnemonic-sim-card {
    background: linear-gradient(135deg, rgba(239, 68, 68, .15), rgba(220, 38, 38, .1)) !important;
    border-color: rgba(248, 113, 113, .4) !important;
}
[data-theme="dark"] .mnemonic-sim-char {
    color: #f1f5f9 !important;
}
[data-theme="dark"] .mnemonic-sim-vi {
    color: #fca5a5 !important;
}

/* Mobile */
@media (max-width: 500px) {
    .ai-reason .err-info-btn {
        padding: .3rem .55rem !important;
        font-size: .68rem !important;
        min-width: 50px !important;
        height: 24px !important;
        gap: .2rem !important;
    }
    .ai-reason .err-info-btn i {
        font-size: .75rem !important;
    }
    .mnemonic-box {
        padding: 1rem !important;
        border-radius: 14px !important;
        max-height: 90vh !important;
    }
    .mnemonic-char {
        font-size: 2rem !important;
    }
    .mnemonic-rad-char {
        font-size: 1.65rem !important;
    }
    .mnemonic-section {
        padding: .6rem .75rem !important;
    }
}
.mnemonic-meaning {
    font-size: .9rem !important;
    font-weight: 700 !important;
    color: #15803d !important;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7) !important;
    padding: .25rem .7rem !important;
    border-radius: 8px !important;
    border: 1.5px solid rgba(22, 163, 74, .4) !important;
    margin-left: .5rem !important;
    white-space: nowrap !important;
}
[data-theme="dark"] .mnemonic-meaning {
    background: linear-gradient(135deg, rgba(22, 163, 74, .25), rgba(21, 128, 61, .15)) !important;
    color: #86efac !important;
    border-color: rgba(34, 197, 94, .5) !important;
}
"""
    return ui_css + extra_css


def patch_js(ui_js):

    if 'var pfHintEnabled = false;' in ui_js:
        ui_js = ui_js.replace(
            'var pfHintEnabled = false;',
            'var pfGradeEnabled = false;'
        )
        print("[Patch] Đổi pfHintEnabled → pfGradeEnabled")

    new_preview = '''function updateCharPreview() {
    var input = $('pfInput');
    var preview = $('pfPreview');
    var userVal = input.value;
    var cleanUser = userVal.replace(/\\s+/g, '');
    var cleanAnswer = pfCurrentAnswer.replace(/\\s+/g, '');

    if (!cleanUser) { preview.innerHTML = ''; return; }

    var html = '';
    var maxLen = cleanUser.length;

    for (var i = 0; i < maxLen; i++) {
        var userChar = cleanUser[i] || '';
        var answerChar = cleanAnswer[i] || '';

        var cls = 'char-slot';
        var display = userChar;
        var clickable = false;

        if (answerChar) {
            if (userChar === answerChar) {
                cls += ' correct';
            } else {
                cls += ' wrong';
                clickable = true;
            }
        } else {
            cls += ' extra';
            clickable = true;
        }

        if (clickable) {
            html += '<span class="' + cls + '" data-idx="' + i + '" onclick="fixCharAt(' + i + ', this)">' +
                    escapeHtml(display) + '</span>';
        } else {
            html += '<span class="' + cls + '">' + escapeHtml(display) + '</span>';
        }
    }
    preview.innerHTML = html;
}'''

    ui_js, n1 = _replace_func(ui_js, 'updateCharPreview', new_preview)
    if n1:
        print("[Patch] Thay updateCharPreview")
    else:
        print("[Patch] WARN: không tìm thấy updateCharPreview")

    new_toggle = '''function toggleGrade() {
    pfGradeEnabled = !pfGradeEnabled;
    var btn = $('pfGradeToggleBtn');

    if (pfGradeEnabled) {
        btn.classList.add('active');
        btn.innerHTML = '<i class="fas fa-check-double"></i> Đang chấm';

        var input = $('pfInput');
        if (input && input.value.trim()) {
            checkFullAnswer();
        }
    } else {
        btn.classList.remove('active');
        btn.innerHTML = '<i class="fas fa-check-double"></i> Chấm điểm';

        var statusEl = $('pfStatus');
        if (statusEl) {
            statusEl.innerHTML = '';
            statusEl.className = 'practice-full-status';
        }
    }
}'''

    ui_js, n2 = _replace_func(ui_js, 'toggleHint', new_toggle)
    if n2:
        print("[Patch] Thay toggleHint → toggleGrade")
    else:
        print("[Patch] WARN: không tìm thấy toggleHint")

    old_reset = "pfHintEnabled = false;\n    $('pfHintBtn').classList.remove('active');\n    updateCharPreview();"
    new_reset = "/* Giữ nguyên toggle khi đổi câu */\n    updateCharPreview();"
    if old_reset in ui_js:
        ui_js = ui_js.replace(old_reset, new_reset)
        print("[Patch] Giữ nguyên toggle khi đổi câu")

    old_listener = "$('pfHintBtn').addEventListener('click', toggleHint);"
    new_listener = "$('pfGradeToggleBtn').addEventListener('click', toggleGrade);"
    if old_listener in ui_js:
        ui_js = ui_js.replace(old_listener, new_listener)
        print("[Patch] Đổi listener pfHintBtn → pfGradeToggleBtn")

    ui_js = re.sub(
        r"pfHintEnabled\s*=\s*true;\s*\n\s*\$\(\s*['\"]pfHintBtn['\"]\s*\)\.classList\.add\(\s*['\"]active['\"]\s*\);",
        "// auto-hint removed",
        ui_js
    )

    ui_js = ui_js.replace("$('pfHintBtn')", "$('pfGradeToggleBtn')")
    ui_js = ui_js.replace("toggleHint()", "toggleGrade()")

    return ui_js


def patch_grading_js(grading_js):
    old = """    async function _doCheckFullAnswer() {
        var input = document.getElementById('pfInput');
        var statusEl = document.getElementById('pfStatus');
        if (!input || !statusEl) return;"""

    new = """    async function _doCheckFullAnswer() {
        if (typeof pfGradeEnabled !== 'undefined' && !pfGradeEnabled) {
            return;
        }

        var input = document.getElementById('pfInput');
        var statusEl = document.getElementById('pfStatus');
        if (!input || !statusEl) return;"""

    if old in grading_js:
        grading_js = grading_js.replace(old, new)
        print("[Patch] Thêm check toggle vào _doCheckFullAnswer")
    else:
        print("[Patch] WARN: không tìm thấy _doCheckFullAnswer")

    return grading_js
