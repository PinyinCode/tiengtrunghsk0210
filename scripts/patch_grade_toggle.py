# -*- coding: utf-8 -*-
"""Patch: đổi nút Gợi ý thành nút Chấm điểm (toggle ON/OFF)."""

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

#pfGradeToggleBtn.active {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: #fff !important;
    border-color: transparent !important;
    border-style: solid !important;
    box-shadow: 0 6px 18px rgba(124, 58, 237, .4) !important;
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
    new_reset = (
        "pfGradeEnabled = false;\n"
        "    var gradeBtn = $('pfGradeToggleBtn');\n"
        "    if (gradeBtn) {\n"
        "        gradeBtn.classList.remove('active');\n"
        "        gradeBtn.innerHTML = '<i class=\"fas fa-check-double\"></i> Chấm điểm';\n"
        "    }\n"
        "    updateCharPreview();"
    )
    if old_reset in ui_js:
        ui_js = ui_js.replace(old_reset, new_reset)
        print("[Patch] Reset toggle trong loadPracticeFull")

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
