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
   Chi tiết lỗi — Hán tự TO, pinyin nhỏ dễ nhìn
   ═══════════════════════════════════════════════════════════ */
.ai-reason,
.card-check .ai-reason,
.practice-full-status .ai-reason {
    display: flex !important;
    flex-wrap: wrap !important;
    justify-content: center !important;
    align-items: center !important;
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

/* Dấu phân cách · */
.ai-reason .err-sep {
    color: var(--text-3) !important;
    font-size: 1rem !important;
    margin: 0 .35rem !important;
    opacity: .6 !important;
    display: inline-block !important;
    vertical-align: middle !important;
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

/* Mobile */
@media (max-width: 500px) {
    #pfGradeToggleBtn,
    #pfRevealBtn {
        padding: .55rem .75rem !important;
        font-size: .78rem !important;
    }
    #pfGradeToggleBtn i,
    #pfRevealBtn i {
        font-size: .82rem !important;
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

    # KHÔNG reset toggle khi đổi câu
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
