# -*- coding: utf-8 -*-
"""
PATCH: Đổi nút "Gợi ý" → "Chấm điểm" (toggle ON/OFF).
Không sửa ui_template.py — chỉ ghi đè output sau khi build.
"""

import re


# ═══════════════════════════════════════════════════════════════════
#  PATCH HTML
# ═══════════════════════════════════════════════════════════════════
def patch_html(ui_html):
    """Đổi nút Gợi ý → Chấm điểm trong HTML."""
    new_btn = '<button id="pfGradeToggleBtn" type="button"><i class="fas fa-check-double"></i> Chấm điểm</button>'

    # Cách 1: tìm exact match
    old_btn = '<button id="pfHintBtn"><i class="fas fa-lightbulb"></i> Gợi ý</button>'
    if old_btn in ui_html:
        ui_html = ui_html.replace(old_btn, new_btn)
        print("✅ [Patch] Đã đổi nút Gợi ý → Chấm điểm (exact)")
        return ui_html

    # Cách 2: regex (cho whitespace khác)
    pattern = r'<button[^>]*id="pfHintBtn"[^>]*>.*?</button>'
    if re.search(pattern, ui_html, flags=re.DOTALL):
        ui_html = re.sub(pattern, new_btn, ui_html, count=1, flags=re.DOTALL)
        print("✅ [Patch] Đã đổi nút Gợi ý → Chấm điểm (regex)")
    else:
        print("⚠️  [Patch] Không tìm thấy nút pfHintBtn")

    return ui_html


# ═══════════════════════════════════════════════════════════════════
#  PATCH CSS
# ═══════════════════════════════════════════════════════════════════
def patch_css(ui_css):
    """Thêm CSS cho nút toggle mới."""
    extra_css = """

/* ═══════════════════════════════════════════════════════════ */
/* PATCH: Nút toggle Chấm điểm                                  */
/* ═══════════════════════════════════════════════════════════ */
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


# ═══════════════════════════════════════════════════════════════════
#  PATCH JS
# ═══════════════════════════════════════════════════════════════════
def patch_js(ui_js):
    """Ghi đè các hàm liên quan trong JS."""

    # ─── 1. Đổi biến state ───
    if 'var pfHintEnabled = false;' in ui_js:
        ui_js = ui_js.replace(
            'var pfHintEnabled = false;',
            'var pfGradeEnabled = false;'
        )
        print("✅ [Patch] Đã đổi pfHintEnabled → pfGradeEnabled")

    # ─── 2. Thay updateCharPreview — bỏ ghost ───
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

    pattern = r'function updateCharPreview\(\)\s*\{.*?\n\}'
    ui_js_new, n = re.subn(pattern, new_preview, ui_js, count=1, flags=re.DOTALL)
    if n > 0:
        ui_js = ui_js_new
        print("✅ [Patch] Đã thay updateCharPreview (bỏ ghost)")
    else:
        print("⚠️  [Patch] Không tìm thấy updateCharPreview")

    # ─── 3. Thay toggleHint → toggleGrade ───
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

    pattern2 = r'function toggleHint\(\)\s*\{.*?\n\}'
    ui_js_new2, n2 = re.subn(pattern2, new_toggle, ui_js, count=1, flags=re.DOTALL)
    if n2 > 0:
        ui_js = ui_js_new2
        print("✅ [Patch] Đã thay toggleHint → toggleGrade")
    else:
        print("⚠️  [Patch] Không tìm thấy toggleHint")

    # ─── 4. Sửa loadPracticeFull — reset toggle ───
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
        print("✅ [Patch] Đã sửa reset toggle trong loadPracticeFull")
    else:
        # Thử các pattern khác
        old_reset_alt = "pfHintEnabled = false;\n      $('pfHintBtn').classList.remove('active');"
        if old_reset_alt in ui_js:
            ui_js = ui_js.replace(
                "$('pfHintBtn').classList.remove('active');",
                "var gradeBtn = $('pfGradeToggleBtn');\n    if (gradeBtn) gradeBtn.classList.remove('active');"
            )
            print("✅ [Patch] Đã sửa reset toggle (alt)")

    # ─── 5. Đổi listener trong initPracticeFull ───
    old_listener = "$('pfHintBtn').addEventListener('click', toggleHint);"
    new_listener = "$('pfGradeToggleBtn').addEventListener('click', toggleGrade);"
    if old_listener in ui_js:
        ui_js = ui_js.replace(old_listener, new_listener)
        print("✅ [Patch] Đã đổi listener pfHintBtn → pfGradeToggleBtn")

    # ─── 6. Bỏ auto-bật hint trong revealFullAnswer (nếu có) ───
    ui_js = re.sub(
        r"pfHintEnabled\s*=\s*true;\s*\n\s*\$\(\s*['\"]pfHintBtn['\"]\s*\)\.classList\.add\(\s*['\"]active['\"]\s*\);",
        "// (auto-hint removed by patch)",
        ui_js
    )

    # ─── 7. Dọn sạch các tham chiếu còn sót ───
    ui_js = ui_js.replace("$('pfHintBtn')", "$('pfGradeToggleBtn')")
    ui_js = ui_js.replace("toggleHint()", "toggleGrade()")

    return ui_js


# ═══════════════════════════════════════════════════════════════════
#  PATCH GRADING JS
# ═══════════════════════════════════════════════════════════════════
def patch_grading_js(grading_js):
    """Thêm check toggle vào _doCheckFullAnswer."""
    old = """    async function _doCheckFullAnswer() {
        var input = document.getElementById('pfInput');
        var statusEl = document.getElementById('pfStatus');
        if (!input || !statusEl) return;"""

    new = """    async function _doCheckFullAnswer() {
        /* Chỉ chấm khi toggle BẬT */
        if (typeof pfGradeEnabled !== 'undefined' && !pfGradeEnabled) {
            return;
        }

        var input = document.getElementById('pfInput');
        var statusEl = document.getElementById('pfStatus');
        if (!input || !statusEl) return;"""

    if old in grading_js:
        grading_js = grading_js.replace(old, new)
        print("✅ [Patch] Đã thêm check toggle vào _doCheckFullAnswer")
    else:
        print("⚠️  [Patch] Không tìm thấy _doCheckFullAnswer")

    return grading_js
