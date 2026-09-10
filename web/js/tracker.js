/**
 * Invest Dictionary — 行为追踪器 (tracker.js)
 * 零依赖 · 声明式绑定 · localStorage 持久化
 *
 * 事件：page_view / landing_view / word_lookup / search_submit / hot_click /
 *       subscribe_click / footer_click / nav_click / share_click
 *
 * 公共属性（OPA 事实标准）：
 *   page_referrer  来源页面路径（同源）
 *   utm_source / utm_medium / utm_campaign / utm_term / utm_content
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'invest_dictionary_events';
  var DEBOUNCE_MS = 500;
  var MAX_EVENTS = 1000;
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

  var writeTimer = null;
  var pendingWrite = null;

  function loadEvents() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveEvents(events) {
    try {
      var trimmed = events.slice(-MAX_EVENTS);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (e) {
      /* localStorage 满则静默失败 */
    }
  }

  function debouncedSave(events) {
    pendingWrite = events;
    if (writeTimer) return;
    writeTimer = setTimeout(function () {
      writeTimer = null;
      if (pendingWrite) {
        saveEvents(pendingWrite);
        pendingWrite = null;
      }
    }, DEBOUNCE_MS);
  }

  function parseUrl(s) {
    try { return new URL(s); } catch (e) { return null; }
  }

  function readCommon() {
    var out = {};
    try {
      var ref = document.referrer;
      if (ref) {
        var u = parseUrl(ref);
        if (u && u.origin === location.origin) {
          out.page_referrer = u.pathname;
        }
      }
      var pageUrl = parseUrl(location.href);
      if (pageUrl) {
        for (var i = 0; i < UTM_KEYS.length; i++) {
          var key = UTM_KEYS[i];
          var v = pageUrl.searchParams.get(key);
          if (v) out[key] = v;
        }
      }
    } catch (e) {
      /* ignore */
    }
    return out;
  }

  function pushEvent(eventName, params) {
    var events = loadEvents();
    var common = readCommon();
    var merged = {};
    var k;
    for (k in common) merged[k] = common[k];
    if (params) for (k in params) merged[k] = params[k];
    events.push({
      event: eventName,
      params: merged,
      timestamp: Date.now(),
      page: location.pathname
    });
    debouncedSave(events);
  }

  /* === 公开 API === */

  window.track = function (eventName, params) {
    pushEvent(eventName, params);
  };

  var durationStart = {};
  window.recordDuration = function (label) {
    durationStart[label] = Date.now();
  };
  window.endDuration = function (label) {
    var start = durationStart[label];
    if (!start) return;
    var durationSec = Math.round((Date.now() - start) / 1000);
    pushEvent(label, { duration_sec: durationSec });
    delete durationStart[label];
  };

  /* === 声明式绑定 === */

  function bindDataTrack() {
    var elements = document.querySelectorAll('[data-track]');
    for (var i = 0; i < elements.length; i++) {
      var el = elements[i];
      (function (el) {
        var eventName = el.getAttribute('data-track');
        el.addEventListener('click', function () {
          var paramsStr = el.getAttribute('data-track-params');
          var params = {};
          if (paramsStr) {
            try { params = JSON.parse(paramsStr); } catch (e) { /* ignore */ }
          }
          pushEvent(eventName, params);
        });
      })(el);
    }
  }

  /* === 页面追踪 === */

  function trackPageView() {
    pushEvent('page_view', {
      page_title: document.title,
      page_location: location.href
    });
    if (location.pathname === '/' || location.pathname.endsWith('/index.html')) {
      pushEvent('landing_view', { scroll_depth: 0 });
    }
  }

  /* 滚动深度追踪 */
  var maxScrollDepth = 0;
  var scrollTimer = null;

  function trackScroll() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight <= 0) return;
    var depth = Math.round((scrollTop / docHeight) * 100);
    depth = Math.min(100, Math.max(0, depth));
    if (depth > maxScrollDepth) {
      maxScrollDepth = depth;
      clearTimeout(scrollTimer);
      scrollTimer = setTimeout(function () {
        pushEvent('landing_view', { scroll_depth: maxScrollDepth });
      }, 500);
    }
  }

  /* === 初始化 === */

  function init() {
    bindDataTrack();
    trackPageView();

    if (location.pathname === '/' || location.pathname.endsWith('/index.html')) {
      window.addEventListener('scroll', trackScroll, { passive: true });
    }

    window.addEventListener('beforeunload', function () {
      if (writeTimer) {
        clearTimeout(writeTimer);
        if (pendingWrite) saveEvents(pendingWrite);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
