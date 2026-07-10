/**
 * Live voting-window countdown — ticks in real time from server-provided endsAt.
 * Mount: any element with data-voting-clock (optional data-compact="1").
 * Seeds from data-ends-at / data-server-now / data-window-id attributes, or
 * fetches /voting-clock once if ends-at is missing.
 */
(function () {
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
    // Accept trailing Z
    var t = Date.parse(iso);
    return isNaN(t) ? null : t;
  }

  function mountEl(el, clock) {
    var endsAtMs = parseIso(clock.endsAt || el.getAttribute("data-ends-at"));
    var serverNowMs = parseIso(clock.serverNow || el.getAttribute("data-server-now")) || Date.now();
    var skew = serverNowMs - Date.now(); // server - client
    var windowId = clock.windowId || el.getAttribute("data-window-id") || "";
    var nextId = clock.nextWindowId || el.getAttribute("data-next-window") || "";
    var isOverride = !!(clock.isOverride || el.getAttribute("data-override") === "1");
    var phase = clock.phase || "";
    var compact = el.getAttribute("data-compact") === "1";

    function tick() {
      var nowApprox = Date.now() + skew;
      var remaining = endsAtMs != null ? Math.max(0, Math.floor((endsAtMs - nowApprox) / 1000)) : null;
      var ended = remaining === 0 && endsAtMs != null;

      var main;
      if (isOverride && !endsAtMs) {
        main = "Operator window " + windowId + " (calendar week still ticks)";
        if (clock.secondsToRealWeekEnd != null) {
          main += " · real week ends in " + formatRemaining(clock.secondsToRealWeekEnd);
        }
      } else if (ended) {
        main = "Window " + windowId + " has ended · next: " + (nextId || "—");
      } else {
        main = compact
          ? formatRemaining(remaining)
          : "Closes in " + formatRemaining(remaining);
      }

      var detail = "";
      if (!compact) {
        detail =
          "Window <strong>" +
          (windowId || "—") +
          "</strong> · UTC · next <strong>" +
          (nextId || "—") +
          "</strong>";
        if (isOverride) detail += " · <em>override active</em>";
      }

      el.innerHTML =
        '<span class="vc-countdown" aria-live="polite">' +
        main +
        "</span>" +
        (detail ? '<span class="vc-detail">' + detail + "</span>" : "");
      el.setAttribute("data-seconds-remaining", remaining != null ? String(remaining) : "");
      el.setAttribute("data-phase", ended ? "ended" : phase || "open");
    }

    tick();
    // Clear previous interval if remounted
    if (el._vcTimer) clearInterval(el._vcTimer);
    el._vcTimer = setInterval(tick, 1000);
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
    // Fetch live clock
    fetch("/voting-clock", { credentials: "same-origin" })
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
