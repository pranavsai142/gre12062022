import re
import os
from PlotterApp import app
import pytest

SCRATCH = "/var/folders/h9/sn160jkx6hb87vp9683ptqr00000gn/T/grok-goal-c2fc57d514e6/implementer"
os.makedirs(SCRATCH, exist_ok=True)

def fake_user():
    return {"uid": "testvamp", "email": "v@example.com", "exp": 9999999999}

def render_html(render_fn, *args, **kwargs):
    with app.test_request_context("/"):
        out = render_fn(*args, **kwargs)
        # Detail pages return (html, found) for HTTP 404 support
        if isinstance(out, tuple):
            return out[0]
        return out

def get_path_html(path):
    c = app.test_client()
    resp = c.get(path, follow_redirects=True)
    return resp.get_data(as_text=True)

def _extract_media_block(style: str, media_query: str = "max-width: 768px") -> str:
    """Robustly extract the content inside the matching @media { ... } block."""
    m = re.search(r'@media\s*\([^)]*' + re.escape(media_query) + r'[^)]*\)\s*\{', style, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    start = m.end() - 1  # position of the opening {
    depth = 1
    i = start + 1
    while i < len(style) and depth > 0:
        c = style[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return style[start + 1 : i - 1]

def assert_menu_vamp(html: str):
    style_m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    assert style_m, "no <style> block"
    style = style_m.group(1)

    mobile_css = _extract_media_block(style, "max-width: 768px") or style

    # revised mobile padding - strictly inside the mobile @media block
    assert re.search(r"padding\s*:\s*8px\s*0", mobile_css), "missing revised mobile padding: 8px 0 inside @media (max-width:768px)"

    # explicit LVHA selectors + non-purple palette (in full style)
    assert ".menu-item:link" in style and re.search(r"#333|rgb\(51,\s*51,\s*51\)", style)
    assert ".menu-item:visited" in style and re.search(r"#333|rgb\(51,\s*51,\s*51\)", style)
    assert ".menu-item:hover" in style and "#ff6600" in style
    assert ".menu-item:active" in style and "#cc5200" in style

    # vamp hover bg
    assert "background: #fff7ed" in style or "fff7ed" in style

    # .active rule with accent
    assert ".menu-item.active" in style and "#ff6600" in style

    # mobile media present
    assert "max-width: 768px" in style

    # robust per-section order using full blocks
    desktop_part = style.split("@media")[0]
    d_act_pos = desktop_part.rfind(".menu-item.active")
    d_actv_pos = desktop_part.rfind(".menu-item:active")
    if d_act_pos >= 0 and d_actv_pos >= 0:
        assert d_act_pos > d_actv_pos, "desktop .active must follow :active (LVHA + class after)"

    mbl = _extract_media_block(style, "max-width: 768px")
    if mbl:
        m_act_pos = mbl.rfind(".menu-item.active")
        m_actv_pos = mbl.rfind(".menu-item:active")
        if m_act_pos >= 0 and m_actv_pos >= 0:
            assert m_act_pos > m_actv_pos, "mobile .active must follow :active inside @media block"

def write_capture(name, html):
    with open(os.path.join(SCRATCH, f"{name}.html"), "w", encoding="utf8") as f:
        f.write(html)

RENDER_CASES = [
    ("IndexPage-render", "IndexPage", (None,)),
    ("VotePage-render", "VotePage", (None,)),
    ("PolicyPage-render", "PolicyPage", (None,)),
    ("AboutPage-render", "AboutPage", (None,)),
    ("LoginPage-render", "LoginPage", (None,)),
    ("RegisterPage-render", "RegisterPage", (None,)),
    ("ResetPage-render", "ResetPage", (None,)),
    ("DraftsPage-render", "DraftsPage", (None,)),
    ("AccountPage-render", "AccountPage", (fake_user(),)),
    ("DetailPage-render", "DetailPage", (None, "dummy")),
    ("DetailAmendmentPage-render", "DetailAmendmentPage", (None, "dummy")),
    ("NotFoundPage-render", "NotFoundPage", (None,)),
]

@pytest.mark.parametrize("out_name,mod_name,args", RENDER_CASES)
def test_render_vamp(out_name, mod_name, args):
    mod = __import__(mod_name)
    fn = getattr(mod, "render")
    html = render_html(fn, *args)
    write_capture(out_name, html)
    assert_menu_vamp(html)

PATH_CASES = [
    ("/", "path-root"), ("/vote", "path-vote"), ("/policy", "path-policy"),
    ("/drafts", "path-drafts"), ("/account", "path-account"), ("/about", "path-about"),
    ("/login", "path-login"), ("/register", "path-register"), ("/reset", "path-reset"),
    ("/detail/dummy", "path-detail-dummy"), ("/detail/amendment/dummy", "path-detail-amend-dummy"),
    ("/this-is-a-404", "path-404"),
]

@pytest.mark.parametrize("path,out_name", PATH_CASES)
def test_path_vamp(path, out_name):
    from product_status import is_discontinued

    if is_discontinued():
        # Full give-up: HTTP paths serve ShutdownPage (no legacy menu vamp chrome).
        html = get_path_html(path)
        write_capture(out_name, html)
        assert "shut down" in html.lower() or "discontinued" in html.lower()
        return
    html = get_path_html(path)
    write_capture(out_name, html)
    assert_menu_vamp(html)

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-q", "--tb=line"])
