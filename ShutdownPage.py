"""
Public shut-down surface for The Internet Party.

Looks like a discontinued website: muted chrome, clear “this service has closed”
copy, no invitation to vote/login/draft as if the party were operating.
"""

from __future__ import annotations


def render(user=None, path: str = "/") -> str:
    """Return complete HTML for any former product URL under discontinuation."""
    _ = user  # session ignored — no member surface
    path_display = path or "/"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>The Internet Party — Discontinued</title>
  <style>
    :root {{
      --bg: #1a1a1a;
      --panel: #242424;
      --border: #3a3a3a;
      --text: #c8c8c8;
      --muted: #888;
      --accent: #9a9a9a;
      --warn: #b08d57;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: Georgia, "Times New Roman", serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.55;
    }}
    .wrap {{
      max-width: 40rem;
      margin: 0 auto;
      padding: 2.5rem 1.25rem 4rem;
    }}
    .badge {{
      display: inline-block;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--warn);
      border: 1px solid var(--warn);
      padding: 0.35rem 0.65rem;
      margin-bottom: 1.25rem;
    }}
    h1 {{
      font-size: 1.75rem;
      font-weight: normal;
      color: #e8e8e8;
      margin: 0 0 0.5rem;
    }}
    .subtitle {{
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 0.95rem;
      color: var(--muted);
      margin: 0 0 1.75rem;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-left: 4px solid var(--warn);
      padding: 1.25rem 1.35rem;
      margin-bottom: 1.5rem;
    }}
    .panel h2 {{
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 0.8rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 0.75rem;
      font-weight: 600;
    }}
    p {{ margin: 0 0 1rem; }}
    p:last-child {{ margin-bottom: 0; }}
    ul {{
      margin: 0.5rem 0 0;
      padding-left: 1.2rem;
      color: var(--text);
    }}
    li {{ margin-bottom: 0.45rem; }}
    .path-note {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.8rem;
      color: var(--muted);
      margin-top: 2rem;
      border-top: 1px solid var(--border);
      padding-top: 1rem;
    }}
    a {{ color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }}
    a:hover {{ color: #d0d0d0; }}
    .footer {{
      margin-top: 2rem;
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .strike {{
      text-decoration: line-through;
      color: #666;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="badge" data-shutdown-badge="1">Service discontinued</div>
    <h1 data-shutdown-title="1">The Internet Party has shut down</h1>
    <p class="subtitle">Party No. 3 is abandoned. This website is no longer an operating governance platform.</p>

    <div class="panel" data-shutdown-panel="give-up">
      <h2>Public give-up notice</h2>
      <p>
        This project has been <strong>fully given up</strong>. There is no open membership,
        no weekly ballot, no draft submission, and no operator control surface for a live party.
      </p>
      <p>
        The product presented a parallel process (draft → vote → promote) without parallel power.
        Process without power is a simulation. Software was optional polish on associations people
        can already form in real life. Crowdsourcing does not mint sovereign power from a website,
        and the open internet is not a single demos that would share one “Internet Party.”
      </p>
      <p>
        Continuing would have been cosplay of a legislature next to a constitutional system that
        already has durable pathways from idea to law — without the stakes, identity, or industrial
        party machinery that make real politics binding.
      </p>
    </div>

    <div class="panel" data-shutdown-panel="closed">
      <h2>What is closed</h2>
      <ul>
        <li><span class="strike">Join / register / login as a member</span> — discontinued</li>
        <li><span class="strike">Weekly voting and ballots</span> — discontinued</li>
        <li><span class="strike">Policy and amendment drafts</span> — discontinued</li>
        <li><span class="strike">Operator tools and promotions</span> — discontinued</li>
      </ul>
      <p style="margin-top:1rem">
        Mutating API routes return <strong>HTTP 410 Gone</strong> with a discontinued payload.
        Historical code remains in the repository for archival reference only.
      </p>
    </div>

    <div class="panel" data-shutdown-panel="archive">
      <h2>Where the investigation lives</h2>
      <p>
        The full sociological write-up — societal realizations, key conflicts, and an exploration
        pathway for further thought (not a product roadmap) — is archived in the repository at
        <code>notes/GROK/SOCIETAL_GIVE_UP_INVESTIGATION.md</code>.
      </p>
      <p>
        Sibling research dojo <strong>TheInternet</strong> is abandoned with the same conclusion.
      </p>
    </div>

    <p class="path-note">
      You requested <code data-requested-path="1">{path_display}</code>.
      Every former product URL shows this shut-down page.
    </p>
    <p class="footer">
      theinternetparty.us — discontinued 2026-07-14 · no further participation
    </p>
  </div>
</body>
</html>
"""
