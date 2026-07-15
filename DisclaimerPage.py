"""
Forced fair-warning / give-up disclaimer for The Internet Party demo.

Visitors must read the sociological revelations and check every acknowledgment
before the rest of the site unlocks. This is not optional marketing copy.
"""

from __future__ import annotations

import html

from product_status import DISCLAIMER_VERSION


def render(next_path: str = "/", error: str | None = None) -> str:
    next_safe = html.escape(next_path or "/", quote=True)
    err_html = ""
    if error:
        err_html = (
            f'<p class="err" data-disclaimer-error="1" role="alert">'
            f"{html.escape(error)}</p>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex">
  <title>Required disclaimer — The Internet Party (demo)</title>
  <style>
    :root {{
      --bg: #121212;
      --panel: #1e1e1e;
      --border: #3d3d3d;
      --text: #e4e4e4;
      --muted: #9a9a9a;
      --warn: #d4a017;
      --danger: #c45c26;
      --ok: #5a8f5a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }}
    .wrap {{
      max-width: 42rem;
      margin: 0 auto;
      padding: 1.5rem 1.1rem 5rem;
    }}
    .badge {{
      display: inline-block;
      font-family: system-ui, sans-serif;
      font-size: 0.72rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--warn);
      border: 1px solid var(--warn);
      padding: 0.35rem 0.6rem;
      margin-bottom: 1rem;
    }}
    h1 {{
      font-size: 1.65rem;
      font-weight: normal;
      margin: 0 0 0.4rem;
      color: #fff;
    }}
    .lead {{
      font-family: system-ui, sans-serif;
      font-size: 0.95rem;
      color: var(--muted);
      margin: 0 0 1.25rem;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-left: 4px solid var(--warn);
      padding: 1.1rem 1.2rem;
      margin-bottom: 1rem;
    }}
    .panel.danger {{ border-left-color: var(--danger); }}
    .panel h2 {{
      font-family: system-ui, sans-serif;
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 0.65rem;
    }}
    .panel h3 {{
      font-size: 1.05rem;
      margin: 0 0 0.5rem;
      color: #fff;
      font-weight: normal;
    }}
    p {{ margin: 0 0 0.75rem; }}
    p:last-child {{ margin-bottom: 0; }}
    ul {{ margin: 0.4rem 0 0; padding-left: 1.2rem; }}
    li {{ margin-bottom: 0.45rem; }}
    .example {{
      font-family: system-ui, sans-serif;
      font-size: 0.9rem;
      background: #161616;
      border: 1px dashed var(--border);
      padding: 0.75rem 0.9rem;
      margin-top: 0.65rem;
      color: #ccc;
    }}
    .example strong {{ color: var(--warn); }}
    blockquote {{
      margin: 0.6rem 0 0;
      padding: 0.65rem 0.9rem;
      border-left: 3px solid var(--danger);
      background: #1a1512;
      font-style: italic;
      color: #ddd;
    }}
    form {{
      margin-top: 1.5rem;
      background: var(--panel);
      border: 2px solid var(--warn);
      padding: 1.15rem 1.2rem;
    }}
    form h2 {{
      font-family: system-ui, sans-serif;
      font-size: 1rem;
      margin: 0 0 0.75rem;
      color: var(--warn);
    }}
    label.ack {{
      display: flex;
      gap: 0.65rem;
      align-items: flex-start;
      font-family: system-ui, sans-serif;
      font-size: 0.9rem;
      margin-bottom: 0.85rem;
      cursor: pointer;
    }}
    label.ack input {{
      margin-top: 0.25rem;
      width: 1.1rem;
      height: 1.1rem;
      flex-shrink: 0;
    }}
    button[type="submit"] {{
      width: 100%;
      margin-top: 0.5rem;
      padding: 0.9rem 1rem;
      font-family: system-ui, sans-serif;
      font-size: 1rem;
      font-weight: 600;
      background: var(--warn);
      color: #111;
      border: none;
      cursor: pointer;
    }}
    button[type="submit"]:hover {{ filter: brightness(1.08); }}
    button[type="submit"]:disabled {{
      opacity: 0.45;
      cursor: not-allowed;
    }}
    .err {{
      font-family: system-ui, sans-serif;
      color: #f0a0a0;
      background: #2a1515;
      border: 1px solid #804040;
      padding: 0.65rem 0.8rem;
      margin-bottom: 1rem;
    }}
    .footer {{
      margin-top: 1.5rem;
      font-family: system-ui, sans-serif;
      font-size: 0.78rem;
      color: var(--muted);
    }}
    code {{ font-size: 0.85em; color: #bbb; }}
  </style>
</head>
<body>
  <div class="wrap" data-disclaimer-page="1" data-disclaimer-version="{html.escape(DISCLAIMER_VERSION)}">
    <div class="badge">Forced fair warning — read before use</div>
    <h1 data-disclaimer-title="1">This is not a real government. You must read this first.</h1>
    <p class="lead">
      The Internet Party software is available so you can <strong>see the idea and try the mechanics</strong>
      (drafts, weekly ballots, promotion). It is <strong>not</strong> a living national party with power.
      The owner abandoned that mission after a hard conversation about feasibility.
      You cannot skip this page: every box below is required.
    </p>
    {err_html}

    <div class="panel danger" data-disclaimer-panel="context">
      <h2>Where this came from</h2>
      <p>
        This disclaimer is the public form of a private reckoning: wanting to scrap the project
        twice; realizing politics is boring on purpose and people will not “get addicted” to process;
        comparing this stack to a cosplay Constitution next to a system that already has durable
        idea→law pathways; and facing that two industrial parties are more like established businesses
        than a free market of apps.
      </p>
      <blockquote>
        Parallel process without parallel power is a simulation.
      </blockquote>
      <blockquote>
        Software is optional polish on a real association — you can already form parties offline.
      </blockquote>
      <blockquote>
        Power is not crowdsourced from a blank website.
      </blockquote>
    </div>

    <div class="panel" data-disclaimer-panel="revelations">
      <h2>Core revelations (why the mission failed)</h2>

      <h3>1. Process ≠ power</h3>
      <p>
        Draft → canidate → vote → promote is a <em>ledger of process</em>. Power means imposing costs,
        seating offices, taxing, or binding courts and ballots that the wider society recognizes.
        This site has none of that. “We voted yes” here does not change a single statute.
      </p>
      <div class="example">
        <strong>Example of failure:</strong> A thousand members vote to “end a federal agency.”
        Congress does not move. Courts do not notice. The “official policy” list on this site updates.
        That is a simulation finishing a loop — not governance.
      </div>

      <h3>2. Software is optional polish</h3>
      <p>
        Real associations already draft platforms, hold conventions, and vote with email, paper,
        Discord, or a church basement. This app does not unlock a forbidden civic right.
        Without a real group that already has stakes, it is polish with no body.
      </p>
      <div class="example">
        <strong>Example of failure:</strong> Shipping perfect ISO-week timers and MetaPolicy char limits
        while zero candidates, zero local chapters, and zero donors care. The product is “done”;
        the party never existed.
      </div>

      <h3>3. Industrial two-party lock-in</h3>
      <p>
        In plurality systems, two large party firms absorb money, media frames, consultants, and
        ballot access. Third-party and “new platform” projects have failed in many costumes for
        structural reasons — not because the weekly ballot UX was slightly wrong.
      </p>
      <div class="example">
        <strong>Example of failure:</strong> A polished third party gets 2% nationally, spoils a race,
        then fades. The duopoly absorbs the slogan. The website did not break Duverger’s pressure.
      </div>

      <h3>4. Power is not crowdsourced</h3>
      <p>
        Crowds can support power (turnout, strikes, money, attention). They rarely mint durable
        sovereignty from open enrollment and good bylaws alone. “If enough people click, legitimacy
        appears” is the civic-tech fallacy.
      </p>
      <div class="example">
        <strong>Example of failure:</strong> A petition or liquid-democracy demo with viral signups
        and zero enforcement capacity. Numbers look real; nothing binds the state.
      </div>

      <h3>5. There is no single online demos</h3>
      <p>
        “Anyone with internet joins One Party” assumes one moral community. Online, people want
        their own rules and enemies. Universal tooling fragments into many incompatible internet parties.
      </p>
      <div class="example">
        <strong>Example of failure:</strong> Trying to host mutually exclusive movements under one
        binding membership (any extreme to any other). Capture, schism, or mush — not one Party No. 3.
      </div>

      <h3>6. Boredom is structural</h3>
      <p>
        Attention loses to entertainment. Good process is often boring. Chasing “addictive politics”
        would corrupt the design without creating power. Mass disengagement from legislation is not
        fixed by a nicer countdown timer.
      </p>
    </div>

    <div class="panel" data-disclaimer-panel="what-you-get">
      <h2>What you are about to open</h2>
      <ul>
        <li>A <strong>working demo</strong> of weekly ballots, drafts, and operator-style tools.</li>
        <li><strong>Not</strong> a claim of parallel sovereignty or a replacement for the Constitution.</li>
        <li><strong>Not</strong> a promise that votes here matter outside this sandbox.</li>
        <li>Full write-up in the repo: <code>notes/GROK/SOCIETAL_GIVE_UP_INVESTIGATION.md</code></li>
      </ul>
    </div>

    <form method="POST" action="/accept-disclaimer" id="disclaimer-form" data-disclaimer-form="1">
      <input type="hidden" name="next" value="{next_safe}">
      <input type="hidden" name="version" value="{html.escape(DISCLAIMER_VERSION)}">
      <h2>Required acknowledgments — all boxes must be checked</h2>

      <label class="ack">
        <input type="checkbox" name="ack_simulation" value="1" required data-ack="simulation">
        <span>I understand <strong>parallel process without parallel power is a simulation</strong> — votes here do not make law.</span>
      </label>
      <label class="ack">
        <input type="checkbox" name="ack_polish" value="1" required data-ack="polish">
        <span>I understand <strong>this software is optional polish</strong> on associations people can form without it.</span>
      </label>
      <label class="ack">
        <input type="checkbox" name="ack_lockin" value="1" required data-ack="lockin">
        <span>I understand <strong>industrial two-party structure</strong> is a structural barrier that an app does not repeal.</span>
      </label>
      <label class="ack">
        <input type="checkbox" name="ack_crowdsource" value="1" required data-ack="crowdsource">
        <span>I understand <strong>power is not crowdsourced</strong> from a website full of good intentions.</span>
      </label>
      <label class="ack">
        <input type="checkbox" name="ack_demos" value="1" required data-ack="demos">
        <span>I understand the <strong>open internet is not one demos</strong> and a universal party would fragment.</span>
      </label>
      <label class="ack">
        <input type="checkbox" name="ack_demo_only" value="1" required data-ack="demo_only">
        <span>I am entering a <strong>demo of an abandoned mission</strong> — I will not treat this site as a real national party or substitute legislature.</span>
      </label>

      <button type="submit" data-disclaimer-submit="1">
        I have read this. Show me the system.
      </button>
    </form>

    <p class="footer">
      Disclaimer version {html.escape(DISCLAIMER_VERSION)} · Party No. 3 mission given up · Demo retained for inspection
    </p>
  </div>
  <script>
    (function () {{
      var form = document.getElementById("disclaimer-form");
      if (!form) return;
      var boxes = form.querySelectorAll('input[type="checkbox"][required]');
      var btn = form.querySelector('[data-disclaimer-submit]');
      function sync() {{
        var ok = true;
        boxes.forEach(function (b) {{ if (!b.checked) ok = false; }});
        if (btn) btn.disabled = !ok;
      }}
      boxes.forEach(function (b) {{ b.addEventListener("change", sync); }});
      sync();
    }})();
  </script>
</body>
</html>
"""


def banner_html() -> str:
    """Sticky reminder after accept — injected into HTML responses."""
    return """
<div id="give-up-demo-banner" data-give-up-banner="1" style="
  position:sticky;top:0;z-index:99999;background:#2a2110;color:#f0e6c8;
  border-bottom:2px solid #d4a017;padding:0.55rem 1rem;font-family:system-ui,sans-serif;
  font-size:0.85rem;line-height:1.4;text-align:center;">
  <strong>Demo of an abandoned mission.</strong>
  Process without power is a simulation · power is not crowdsourced · not a real government.
  <a href="/disclaimer" style="color:#ffd666;margin-left:0.5rem;">Re-read disclaimer</a>
</div>
"""
