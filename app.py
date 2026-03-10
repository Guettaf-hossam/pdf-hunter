from __future__ import annotations

import asyncio
import html

import nest_asyncio
import streamlit as st

nest_asyncio.apply()

st.set_page_config(
    page_title="PDF Hunter",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# All animations use transform/opacity ONLY — these are GPU-composited and
# never trigger layout recalculation. No backdrop-filter, no SVG filters,
# no blur(), no infinite background-position animations on large surfaces.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Keyframes (GPU-only: transform + opacity) ──────── */

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes heroFade {
    from { opacity: 0; transform: scale(0.96); }
    to   { opacity: 1; transform: scale(1); }
}

@keyframes glowPulse {
    0%, 100% { opacity: 0.6; }
    50%      { opacity: 1; }
}

@keyframes orb1 {
    0%   { transform: translate(0, 0) scale(1); }
    33%  { transform: translate(30px, -40px) scale(1.1); }
    66%  { transform: translate(-20px, 20px) scale(0.95); }
    100% { transform: translate(0, 0) scale(1); }
}

@keyframes orb2 {
    0%   { transform: translate(0, 0) scale(1); }
    33%  { transform: translate(-40px, 30px) scale(1.05); }
    66%  { transform: translate(25px, -15px) scale(0.98); }
    100% { transform: translate(0, 0) scale(1); }
}

/* ── Global ─────────────────────────────────────────── */

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: #08081a;
    min-height: 100vh;
    overflow-x: hidden;
}

/* Floating orbs — GPU transform only, no filter/blur */
.orb {
    position: fixed;
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    will-change: transform;
}
.orb-1 {
    width: 500px; height: 500px;
    top: -10%; left: -10%;
    background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%);
    animation: orb1 20s ease-in-out infinite;
}
.orb-2 {
    width: 400px; height: 400px;
    bottom: -5%; right: -8%;
    background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%);
    animation: orb2 25s ease-in-out infinite;
}
.orb-3 {
    width: 300px; height: 300px;
    top: 40%; right: 20%;
    background: radial-gradient(circle, rgba(52,211,153,0.07) 0%, transparent 70%);
    animation: orb1 30s ease-in-out infinite reverse;
}

/* ── Hero ───────────────────────────────────────────── */

.hero-wrap {
    animation: heroFade 0.8s ease-out both;
    text-align: center;
    padding-top: 1rem;
}

.hero-title {
    font-size: 3.4rem;
    font-weight: 900;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #c084fc, #818cf8, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1.1;
}

.hero-icon {
    font-size: 2.8rem;
    display: block;
    margin-bottom: 0.3rem;
    animation: glowPulse 3s ease-in-out infinite;
}

.hero-sub {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 400;
    margin-top: 0.6rem;
    margin-bottom: 2rem;
    line-height: 1.6;
    letter-spacing: 0.2px;
}

.hero-sources {
    display: flex;
    justify-content: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 0.7rem;
}

.hero-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #475569;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 4px;
    padding: 2px 8px;
    transition: color 0.2s, border-color 0.2s;
}
.hero-chip:hover {
    color: #94a3b8;
    border-color: rgba(255,255,255,0.15);
}

/* ── Source Badges ──────────────────────────────────── */

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.6rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
    margin-right: 4px;
    text-transform: uppercase;
    vertical-align: middle;
}

.badge-libgen  { background: #064e3b; color: #6ee7b7; }
.badge-zlib    { background: #1e3a5f; color: #93c5fd; }
.badge-anna    { background: #4c1d57; color: #e879f9; }
.badge-openlib { background: #78350f; color: #fcd34d; }
.badge-ddg     { background: #1e293b; color: #64748b; }

.dtype-book     { background: #451a03; color: #fbbf24; }
.dtype-academic { background: #022c22; color: #34d399; }
.dtype-general  { background: #0f172a; color: #64748b; }

/* ── Result Cards ──────────────────────────────────── */

.result-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    animation: fadeSlideUp 0.35s ease-out both;
    position: relative;
}

.result-card:hover {
    transform: translateY(-2px);
    border-color: rgba(139,92,246,0.3);
    box-shadow: 0 8px 32px rgba(139,92,246,0.06);
}

.result-card.direct {
    border-left: 3px solid #34d399;
}
.result-card.direct:hover {
    border-color: #34d399;
    box-shadow: 0 8px 32px rgba(52,211,153,0.08);
}

.result-card.page {
    border-left: 3px solid rgba(96,165,250,0.5);
}

.badge-row {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 4px;
}

.result-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    color: #334155;
    margin-right: 4px;
    min-width: 20px;
}

.result-title {
    color: #e2e8f0;
    font-size: 0.86rem;
    font-weight: 500;
    line-height: 1.4;
    margin: 2px 0 4px;
}

.result-link {
    font-size: 0.68rem;
    font-family: 'JetBrains Mono', monospace;
    word-break: break-all;
}
.result-link a {
    color: #475569;
    text-decoration: none;
    transition: color 0.15s;
}
.result-link a:hover {
    color: #60a5fa;
}

.pdf-tag {
    display: inline-block;
    color: #34d399;
    font-size: 0.6rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 1px 6px;
    border-radius: 3px;
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.15);
    margin-left: 4px;
    animation: glowPulse 2.5s ease-in-out infinite;
}

/* ── Stat Bar ──────────────────────────────────────── */

.stat-bar {
    display: flex;
    justify-content: center;
    gap: 0;
    margin: 1.4rem auto;
    max-width: 500px;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

.stat-cell {
    flex: 1;
    text-align: center;
    padding: 10px 8px;
    background: rgba(255,255,255,0.02);
    border-right: 1px solid rgba(255,255,255,0.04);
    transition: background 0.2s;
}
.stat-cell:last-child { border-right: none; }
.stat-cell:hover { background: rgba(255,255,255,0.04); }

.stat-num {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
}
.stat-label {
    display: block;
    font-size: 0.58rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #475569;
    margin-top: 3px;
}

.stat-num.clr-total    { color: #a78bfa; }
.stat-num.clr-books    { color: #fbbf24; }
.stat-num.clr-academic { color: #34d399; }
.stat-num.clr-general  { color: #64748b; }
.stat-num.clr-direct   { color: #34d399; }

/* ── Section Headers ───────────────────────────────── */

.section-header {
    font-size: 0.68rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.8rem 0 0.8rem;
    padding: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.08) 0%, transparent 100%);
}

.sh-book     { color: #fbbf24; }
.sh-academic { color: #34d399; }
.sh-general  { color: #475569; }

/* ── Streamlit Overrides ───────────────────────────── */

#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.2) !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(124,58,237,0.3) !important;
}
.stFormSubmitButton > button:active {
    transform: scale(0.97) !important;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    padding: 10px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(139,92,246,0.4) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.08) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #334155 !important;
    font-style: italic;
}

.stSpinner > div { color: #a78bfa !important; }

.stAlert {
    background: rgba(251,191,36,0.04) !important;
    border-color: rgba(251,191,36,0.15) !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.35); }

/* ── Mobile ────────────────────────────────────────── */

@media (max-width: 640px) {
    .hero-title { font-size: 2.4rem; letter-spacing: -1px; }
    .hero-sub   { font-size: 0.78rem; }
    .stat-num   { font-size: 1rem; }
    .stat-label { font-size: 0.5rem; }
    .result-card { padding: 11px 13px; }
    .result-title { font-size: 0.82rem; }
    .badge { font-size: 0.55rem; padding: 2px 6px; }
    .orb { display: none; }
}
</style>
""", unsafe_allow_html=True)

# Floating orbs (GPU transform-only, no filter)
st.markdown("""
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
""", unsafe_allow_html=True)


from pdf_hunter import BookResult, hunt_for_pdf_async  # noqa: E402


SOURCE_BADGE = {
    "LibGen":            ("badge-libgen",  "LIBGEN"),
    "Z-Library":         ("badge-zlib",    "Z-LIB"),
    "Anna's Archive":    ("badge-anna",    "ANNA'S"),
    "Open Library / IA": ("badge-openlib", "OPENLIB"),
    "DuckDuckGo":        ("badge-ddg",     "WEB"),
}

DOCTYPE_BADGE = {
    "Book":        ("dtype-book",     "BOOK"),
    "Academic":    ("dtype-academic", "ACADEMIC"),
    "General PDF": ("dtype-general",  "PDF"),
}


@st.cache_data(ttl=86400, show_spinner=False)
def cached_search(query: str) -> list[dict]:
    results = asyncio.run(hunt_for_pdf_async(query))
    return [r.to_dict() for r in results]


def render_result(r: dict, idx: int) -> None:
    src_cls, src_label = SOURCE_BADGE.get(r["source"], ("badge-ddg", "WEB"))
    dt_cls, dt_label   = DOCTYPE_BADGE.get(r.get("doc_type", "General PDF"), ("dtype-general", "PDF"))
    card_class  = "direct" if r["is_direct_pdf"] else "page"
    pdf_tag     = '<span class="pdf-tag">DIRECT PDF</span>' if r["is_direct_pdf"] else ""
    safe_title  = html.escape(r["title"])
    safe_link   = html.escape(r["link"])
    mirror_line = ""
    if r.get("mirror"):
        safe_mirror = html.escape(r["mirror"])
        mirror_line = (
            f'<div class="result-link" style="margin-top:2px;">'
            f'<a href="{safe_mirror}" target="_blank">alt: {html.escape(r["mirror"][:70])}</a></div>'
        )

    st.markdown(
f"""<div class="result-card {card_class}" style="animation-delay:{idx * 0.04}s">
<div class="badge-row">
<span class="result-num">#{idx:02d}</span>
<span class="badge {src_cls}">{src_label}</span>
<span class="badge {dt_cls}">{dt_label}</span>
{pdf_tag}
</div>
<div class="result-title">{safe_title}</div>
<div class="result-link"><a href="{safe_link}" target="_blank">{safe_link}</a></div>
{mirror_line}
</div>""",
        unsafe_allow_html=True,
    )


def section(label: str, css_class: str) -> None:
    st.markdown(
f'<div class="section-header {css_class}">{label}</div>',
        unsafe_allow_html=True,
    )


# ── UI ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-wrap">
    <span class="hero-icon">📚</span>
    <div class="hero-title">PDF Hunter</div>
    <div class="hero-sub">
        Universal PDF Search Engine<br>
        Books · University Cours / TD / TP · Research Papers · Open Web
        <div class="hero-sources">
            <span class="hero-chip">LibGen</span>
            <span class="hero-chip">Z-Library</span>
            <span class="hero-chip">Anna's Archive</span>
            <span class="hero-chip">Open Library</span>
            <span class="hero-chip">Academia.edu</span>
            <span class="hero-chip">DuckDuckGo</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.form("search_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            label="query",
            label_visibility="collapsed",
            placeholder='e.g. "Electromagnetism TD",  "Python Cheat Sheet",  "Les Miserables"',
        )
    with col2:
        submitted = st.form_submit_button("🔍 Hunt", use_container_width=True)

if submitted and query.strip():
    with st.spinner("Scanning 6 sources with 8 parallel dorks…"):
        raw = cached_search(query.strip())

    books    = [r for r in raw if r.get("doc_type") == "Book"]
    academic = [r for r in raw if r.get("doc_type") == "Academic"]
    general  = [r for r in raw if r.get("doc_type", "General PDF") == "General PDF"]
    direct_count = sum(1 for r in raw if r["is_direct_pdf"])

    # Stat bar — single unified component
    st.markdown(
f"""<div class="stat-bar">
<div class="stat-cell"><span class="stat-num clr-total">{len(raw)}</span><span class="stat-label">Total</span></div>
<div class="stat-cell"><span class="stat-num clr-books">{len(books)}</span><span class="stat-label">Books</span></div>
<div class="stat-cell"><span class="stat-num clr-academic">{len(academic)}</span><span class="stat-label">Academic</span></div>
<div class="stat-cell"><span class="stat-num clr-general">{len(general)}</span><span class="stat-label">General</span></div>
<div class="stat-cell"><span class="stat-num clr-direct">{direct_count}</span><span class="stat-label">Direct</span></div>
</div>""",
        unsafe_allow_html=True,
    )

    if not raw:
        st.warning("No results found. Try different keywords or a shorter query.")
    else:
        counter = 1

        if books:
            section("📖 Books", "sh-book")
            for r in books:
                render_result(r, counter)
                counter += 1

        if academic:
            section("🎓 Academic — Cours · TD · TP · Research", "sh-academic")
            for r in academic:
                render_result(r, counter)
                counter += 1

        if general:
            section("📄 General PDFs", "sh-general")
            for r in general:
                render_result(r, counter)
                counter += 1

elif submitted:
    st.warning("Please enter a search query.")

st.markdown("""
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.04);margin-top:3rem;">
<div style="text-align:center;padding:1.2rem 0 1rem;animation:fadeSlideUp 0.5s ease-out both;">
    <div style="font-size:0.7rem;color:#334155;letter-spacing:1px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
        Built by
        <a href="https://github.com/Guettaf-hossam" style="color:#7c3aed;text-decoration:none;font-weight:600;">knight</a>
    </div>
    <div style="font-size:0.6rem;color:#1e293b;margin-top:4px;">
        PDF Hunter — open source · searches public indexes only
    </div>
</div>
""", unsafe_allow_html=True)
