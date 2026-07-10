/**
 * Live voting-window countdown — ticks in real time from server-provided endsAt.
 * Mount: any element with data-voting-clock (optional data-compact="1").
 * Seeds from data-ends-at / data-server-now / data-window-id attributes, or
 * fetches /voting-clock once if ends-at is missing.
 *
 * Real-world ticks: 1s local countdown, resync with /voting-clock every 60s,
 * and a single auto-reload when the window boundary is crossed so the new
 * ISO week (ballot + window id) appears without a manual refresh.
 */
(function () {
  var RESYNC_MS = 60000;
  var RELOAD_KEY = "ip_vc_reloaded_for";

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function formatRemaining(totalSec) {
    if (totalSec == null || isNaN(totalSec)) return "—";
    totalSec = Math.max(0, Math.floor(totalSec));
    var d = Math.floor(totalSec / 86400);
    var h = Math.floor((totalSec % 86400) / 3600);
    var m = Math.floor((totalSec % 3600) / 60);
    var s = totalSec % 60;
    if (d > 0) return d + "d " + pad(h) + "h " + pad(m) + "m " + pad(s) + "s";
    if (h > 0) return pad(h) + "h " + pad(m) + "m " + pad(s) + "s";
    return pad(m) + "m " + pad(s) + "s";
  }

  function parseIso(iso) {
    if (!iso) return null;
    var t = Date.parse(iso);
    return isNaN(t) ? null : t;
  }

  function maybeReloadForNewWeek(windowId, endsAtMs, nowApprox) {
    if (endsAtMs == null || nowApprox < endsAtMs) return;
    var key = windowId + "|" + endsAtMs;
    try {
      if (sessionStorage.getItem(RELOAD_KEY) === key) return;
      sessionStorage.setItem(RELOAD_KEY, key);
    } catch (e) {
      /* private mode — still try one reload */
    }
    // Brief message paint before navigation
    setTimeout(function () {
      window.location.reload();
    }, 800);
  }

  function mountEl(el, clock) {
    var state = {
      endsAtMs: parseIso(clock.endsAt || el.getAttribute("data-ends-at")),
      serverNowMs: parseIso(clock.serverNow || el.getAttribute("data-server-now")) || Date.now(),
      windowId: clock.windowId || el.getAttribute("data-window-id") || "",
      nextId: clock.nextWindowId || el.getAttribute("data-next-window") || "",
      isOverride: !!(clock.isOverride || el.getAttribute("data-override") === "1"),
      phase: clock.phase || "",
      secondsToRealWeekEnd:
        clock.secondsToRealWeekEnd != null
          ? clock.secondsToRealWeekEnd
          : el.getAttribute("data-seconds-real-end")
            ? parseInt(el.getAttribute("data-seconds-real-end"), 10)
            : null,
    };
    state.skew = state.serverNowMs - Date.now();
    var compact = el.getAttribute("data-compact") === "1";
    var sawOpen = false;

    function applyClock(clockIn) {
      if (!clockIn) return;
      state.endsAtMs = parseIso(clockIn.endsAt) != null ? parseIso(clockIn.endsAt) : state.endsAtMs;
      state.serverNowMs = parseIso(clockIn.serverNow) || Date.now();
      state.skew = state.serverNowMs - Date.now();
      if (clockIn.windowId) state.windowId = clockIn.windowId;
      if (clockIn.nextWindowId) state.nextId = clockIn.nextWindowId;
      if (typeof clockIn.isOverride === "boolean") state.isOverride = clockIn.isOverride;
      if (clockIn.phase) state.phase = clockIn.phase;
      if (clockIn.secondsToRealWeekEnd != null) {
        state.secondsToRealWeekEnd = clockIn.secondsToRealWeekEnd;
      }
      // Keep data-* attributes in sync for other scripts (vote.js window id)
      if (state.windowId) el.setAttribute("data-window-id", state.windowId);
      if (clockIn.endsAt) el.setAttribute("data-ends-at", clockIn.endsAt);
      if (clockIn.nextWindowId) el.setAttribute("data-next-window", clockIn.nextWindowId);
    }

    function tick() {
      var nowApprox = Date.now() + state.skew;
      var remaining =
        state.endsAtMs != null ? Math.max(0, Math.floor((state.endsAtMs - nowApprox) / 1000)) : null;
      var ended = remaining === 0 && state.endsAtMs != null;

      if (!ended) sawOpen = true;

      var main;
      if (state.isOverride && !state.endsAtMs) {
        main = "Operator window " + state.windowId + " (calendar week still ticks)";
        if (state.secondsToRealWeekEnd != null) {
          // Approximate remaining real week from last sync
          var realLeft = state.secondsToRealWeekEnd - Math.floor((Date.now() + state.skew - state.serverNowMs) / 1000);
          main += " · real week ends in " + formatRemaining(Math.max(0, realLeft));
        }
      } else if (ended) {
        main =
          "Window " +
          state.windowId +
          " ended · loading " +
          (state.nextId || "next week") +
          "…";
        if (sawOpen) {
          maybeReloadForNewWeek(state.windowId, state.endsAtMs, nowApprox);
        }
      } else {
        main = compact
          ? formatRemaining(remaining)
          : "Closes in " + formatRemaining(remaining);
      }

      var detail = "";
      if (!compact) {
        detail =
          "Window <strong>" +
          (state.windowId || "—") +
          "</strong> · UTC · next <strong>" +
          (state.nextId || "—") +
          "</strong>";
        if (state.isOverride) detail += " · <em>override active</em>";
      }

      el.innerHTML =
        '<span class="vc-countdown" aria-live="polite">' +
        main +
        "</span>" +
        (detail ? '<span class="vc-detail">' + detail + "</span>" : "");
      el.setAttribute("data-seconds-remaining", remaining != null ? String(remaining) : "");
      el.setAttribute("data-phase", ended ? "ended" : state.phase || "open");
    }

    function resync() {
      fetch("/voting-clock", {
        credentials: "same-origin",
        cache: "no-store",
        headers: { Accept: "application/json" },
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (clockIn) {
          applyClock(clockIn);
          tick();
        })
        .catch(function () {
          /* keep ticking from last known endsAt */
        });
    }

    tick();
    if (el._vcTimer) clearInterval(el._vcTimer);
    if (el._vcResync) clearInterval(el._vcResync);
    el._vcTimer = setInterval(tick, 1000);
    el._vcResync = setInterval(resync, RESYNC_MS);

    // Resync when tab becomes visible again (laptop sleep / background tab)
    if (!el._vcVisBound) {
      el._vcVisBound = true;
      document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "visible") resync();
      });
    }
  }

  function bootOne(el) {
    var ends = el.getAttribute("data-ends-at");
    if (ends) {
      mountEl(el, {
        endsAt: ends,
        serverNow: el.getAttribute("data-server-now"),
        windowId: el.getAttribute("data-window-id"),
        nextWindowId: el.getAttribute("data-next-window"),
        isOverride: el.getAttribute("data-override") === "1",
        phase: el.getAttribute("data-phase") || "",
        secondsToRealWeekEnd: el.getAttribute("data-seconds-real-end")
          ? parseInt(el.getAttribute("data-seconds-real-end"), 10)
          : null,
      });
      return;
    }
    fetch("/voting-clock", {
      credentials: "same-origin",
      cache: "no-store",
      headers: { Accept: "application/json" },
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (clock) {
        mountEl(el, clock);
      })
      .catch(function () {
        el.textContent = "Voting clock unavailable";
      });
  }

  function bootAll() {
    var nodes = document.querySelectorAll("[data-voting-clock]");
    for (var i = 0; i < nodes.length; i++) bootOne(nodes[i]);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAll);
  } else {
    bootAll();
  }
})();
