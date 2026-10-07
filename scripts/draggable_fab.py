# -*- coding: utf-8 -*-
"""Draggable FAB"""


def build_draggable_fab_css():
    return r"""
.acm-fab.dragging,
.chat-float-btn.dragging{
    transition:none !important;
    cursor:grabbing !important;
}
.acm-fab[data-draggable="1"],
.chat-float-btn[data-draggable="1"]{
    cursor:grab;
    touch-action:none;
    -webkit-user-select:none;
    user-select:none;
    -webkit-touch-callout:none;
}
.acm-fab[data-draggable="1"]:active,
.chat-float-btn[data-draggable="1"]:active{
    cursor:grabbing;
}
.fab-toast{
    position:fixed;
    bottom:120px;
    left:50%;
    transform:translateX(-50%) translateY(20px);
    background:rgba(15,23,42,.95);
    color:#fff;
    padding:.7rem 1.2rem;
    border-radius:50px;
    font-size:.85rem;
    font-weight:600;
    z-index:99999;
    opacity:0;
    transition:opacity .3s, transform .3s;
    pointer-events:none;
    box-shadow:0 8px 24px rgba(0,0,0,.3);
    max-width:80vw;
    text-align:center;
}
.fab-toast.show{
    opacity:1;
    transform:translateX(-50%) translateY(0);
}
"""


def build_draggable_fab_js():
    return r"""
(function() {
    'use strict';

    var DRAG_THRESHOLD = 5;
    var STORAGE_PREFIX = 'fab_pos_';
    var FIRESTORE_COLLECTION = 'user_prefs';
    var FIRESTORE_FIELD_PREFIX = 'fab_pos_';
    var DESKTOP_RESIZE_MIN = 100;

    var _lastWidth = window.innerWidth;
    var _lastHeight = window.innerHeight;
    var _resizeTimer = null;

    function isMobileDevice() {
        try {
            return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
                   (window.matchMedia && window.matchMedia('(pointer: coarse)').matches);
        } catch(e) {
            return false;
        }
    }

    function getUser() {
        try { return window.currentUser || null; }
        catch(e) { return null; }
    }
    function getUserEmail() {
        var u = getUser();
        return (u && u.email) ? u.email : null;
    }
    function getUserKey(baseKey) {
        var email = getUserEmail();
        return baseKey + '_' + (email || 'guest');
    }

    function showToast(msg) {
        var t = document.getElementById('fabToast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'fabToast';
            t.className = 'fab-toast';
            document.body.appendChild(t);
        }
        t.textContent = msg;
        t.classList.add('show');
        clearTimeout(t._timer);
        t._timer = setTimeout(function() { t.classList.remove('show'); }, 2000);
    }

    function clearSavedPosition(baseStorageKey) {
        var storageKey = getUserKey(baseStorageKey);
        try {
            localStorage.removeItem(STORAGE_PREFIX + storageKey);
        } catch(e) {}

        var email = getUserEmail();
        var db = window.db;
        if (email && db) {
            var fieldName = FIRESTORE_FIELD_PREFIX + baseStorageKey;
            var update = {};
            try {
                update[fieldName] = firebase.firestore.FieldValue.delete();
                db.collection(FIRESTORE_COLLECTION).doc(email)
                    .update(update)
                    .catch(function() {});
            } catch(e) {}
        }
    }

    function resetElementToDefault(el) {
        el.style.left = '';
        el.style.top = '';
        el.style.right = '';
        el.style.bottom = '';
        el.style.transform = '';
        el.style.transition = '';
        el.style.zIndex = '';
        el.removeAttribute('data-draggable');
        el.classList.remove('dragging');
        el.__draggable = false;
        el.__storageKey = null;
        el.__suppressClick = false;
    }

    function handleRealResize() {
        var newW = window.innerWidth;
        var newH = window.innerHeight;
        var dw = Math.abs(newW - _lastWidth);
        var dh = Math.abs(newH - _lastHeight);

        var shouldReset;
        if (isMobileDevice()) {
            shouldReset = (newW !== _lastWidth);
        } else {
            shouldReset = (dw > DESKTOP_RESIZE_MIN || dh > DESKTOP_RESIZE_MIN);
        }

        if (!shouldReset) {
            _lastHeight = newH;
            return;
        }

        _lastWidth = newW;
        _lastHeight = newH;

        var chatEl = document.getElementById('chatFloatWrap');

        if (chatEl && chatEl.__draggable) {
            clearSavedPosition('chat');
            resetElementToDefault(chatEl);
        }

        setTimeout(function() {
            if (typeof initChatFab === 'function') initChatFab();
        }, 200);
    }

    window.__resetFabPosition = function(baseKey) {
        var email = getUserEmail();
        var storageKey = getUserKey(baseKey);
        try { localStorage.removeItem(STORAGE_PREFIX + storageKey); } catch(e) {}
        if (email && window.db) {
            var fieldName = FIRESTORE_FIELD_PREFIX + baseKey;
            var update = {};
            try {
                update[fieldName] = firebase.firestore.FieldValue.delete();
                window.db.collection(FIRESTORE_COLLECTION).doc(email)
                    .update(update).catch(function() {});
            } catch(e) {}
        }
        showToast('Da reset vi tri nut');
        setTimeout(function() { location.reload(); }, 600);
    };

    function initChatFab() {
        var el = document.getElementById('chatFloatWrap');
        if (!el) return;

        var storageKey = getUserKey('chat');

        if (el.__draggable && el.__storageKey !== storageKey) {
            resetElementToDefault(el);
        }

        if (el.__draggable) return;
        el.__draggable = true;
        el.__storageKey = storageKey;
        el.setAttribute('data-draggable', '1');

        var btn = document.getElementById('chatFloatBtn');
        if (!btn) return;

        var isDragging = false;
        var hasMoved = false;
        var startX = 0, startY = 0;
        var elStartX = 0, elStartY = 0;

        function applyPosition(x, y) {
            var rect = el.getBoundingClientRect();
            var maxX = window.innerWidth - rect.width - 4;
            var maxY = window.innerHeight - rect.height - 4;
            x = Math.max(4, Math.min(x, maxX));
            y = Math.max(4, Math.min(y, maxY));
            el.style.left = x + 'px';
            el.style.top = y + 'px';
            el.style.right = 'auto';
            el.style.bottom = 'auto';
        }

        function getCurrentPosition() {
            var rect = el.getBoundingClientRect();
            return { x: Math.round(rect.left), y: Math.round(rect.top) };
        }

        function fromLocalStorage() {
            try {
                var saved = localStorage.getItem(STORAGE_PREFIX + storageKey);
                if (saved) {
                    var pos = JSON.parse(saved);
                    if (pos && typeof pos.x === 'number') {
                        applyPosition(pos.x, pos.y);
                        return true;
                    }
                }
            } catch(e) {}
            return false;
        }

        function loadPosition() {
            var email = getUserEmail();
            var db = window.db;
            if (!email || !db) {
                fromLocalStorage();
                return;
            }
            db.collection(FIRESTORE_COLLECTION).doc(email).get()
                .then(function(doc) {
                    if (doc.exists) {
                        var data = doc.data();
                        var pos = data['fab_pos_chat'];
                        if (pos && typeof pos.x === 'number') {
                            applyPosition(pos.x, pos.y);
                            try {
                                localStorage.setItem(
                                    STORAGE_PREFIX + storageKey,
                                    JSON.stringify({ x: pos.x, y: pos.y })
                                );
                            } catch(e) {}
                            return;
                        }
                    }
                    fromLocalStorage();
                })
                .catch(function() {
                    fromLocalStorage();
                });
        }

        function savePosition() {
            var pos = getCurrentPosition();
            try {
                localStorage.setItem(
                    STORAGE_PREFIX + storageKey,
                    JSON.stringify(pos)
                );
            } catch(e) {}
            var email = getUserEmail();
            var db = window.db;
            if (email && db) {
                var update = {};
                update['fab_pos_chat'] = pos;
                db.collection(FIRESTORE_COLLECTION).doc(email)
                    .set(update, { merge: true })
                    .catch(function() {});
            }
        }

        function getPoint(e) {
            if (e.touches && e.touches.length) {
                return { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
            if (e.changedTouches && e.changedTouches.length) {
                return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY };
            }
            return { x: e.clientX, y: e.clientY };
        }

        function onPointerDown(e) {
            if (e.type === 'mousedown' && e.button !== 0) return;
            if (typeof window.__closeFloatMenu === 'function') {
                window.__closeFloatMenu();
            }
            var point = getPoint(e);
            startX = point.x;
            startY = point.y;
            var rect = el.getBoundingClientRect();
            elStartX = rect.left;
            elStartY = rect.top;
            isDragging = true;
            hasMoved = false;
            el.style.transition = 'none';
            el.classList.add('dragging');
            el.style.zIndex = '99999';
        }

        function onPointerMove(e) {
            if (!isDragging) return;
            var point = getPoint(e);
            var dx = point.x - startX;
            var dy = point.y - startY;
            if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
                hasMoved = true;
            }
            if (!hasMoved) return;
            var newX = elStartX + dx;
            var newY = elStartY + dy;
            applyPosition(newX, newY);
            if (e.cancelable) e.preventDefault();
        }

        function onPointerUp(e) {
            if (!isDragging) return;
            isDragging = false;
            el.style.transition = '';
            el.classList.remove('dragging');
            el.style.zIndex = '';
            if (hasMoved) {
                savePosition();
                btn.__suppressClick = true;
                setTimeout(function() { btn.__suppressClick = false; }, 150);
            }
        }

        btn.addEventListener('click', function(e) {
            if (btn.__suppressClick) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }, true);

        btn.addEventListener('mousedown', onPointerDown);
        btn.addEventListener('touchstart', onPointerDown, { passive: true });

        document.addEventListener('mousemove', onPointerMove);
        document.addEventListener('mouseup', onPointerUp);
        document.addEventListener('touchmove', onPointerMove, { passive: false });
        document.addEventListener('touchend', onPointerUp);
        document.addEventListener('touchcancel', onPointerUp);

        loadPosition();

        el.__isDraggingFn = function() { return isDragging; };
    }

    function autoInit() {
        initChatFab();
    }

    var _lastEmail = null;
    setInterval(function() {
        try {
            var u = getUser();
            var email = u ? u.email : null;

            if (email === _lastEmail) return;
            _lastEmail = email;

            var el = document.getElementById('chatFloatWrap');
            if (el) resetElementToDefault(el);

            setTimeout(autoInit, 300);
        } catch(e) {}
    }, 2000);

    window.addEventListener('resize', function() {
        var chatEl = document.getElementById('chatFloatWrap');
        var isDragging = (chatEl && chatEl.__isDraggingFn && chatEl.__isDraggingFn());
        if (isDragging) return;

        clearTimeout(_resizeTimer);
        _resizeTimer = setTimeout(handleRealResize, 300);
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoInit);
    } else {
        autoInit();
    }
    setTimeout(autoInit, 1000);
    setTimeout(autoInit, 3000);
})();
"""
