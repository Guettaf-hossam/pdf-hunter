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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Keyframes ────────────────────────────────────────── */

@keyframes meshDrift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes heroGlow {
    0%   { background-position: 0% 50%;  filter: brightness(1); }
    50%  { background-position: 100% 50%; filter: brightness(1.18); }
    100% { background-position: 0% 50%;  filter: brightness(1); }
}

@keyframes cardReveal {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pulseRing {
    0%   { box-shadow: 0 0 0 0 rgba(139,92,246,0.35); }
    70%  { box-shadow: 0 0 0 8px rgba(139,92,246,0); }
    100% { box-shadow: 0 0 0 0 rgba(139,92,246,0); }
}

@keyframes borderShimmer {
    0%   { border-color: rgba(139,92,246,0.15); }
    50%  { border-color: rgba(96,165,250,0.3); }
    100% { border-color: rgba(139,92,246,0.15); }
}

/* ── Global ───────────────────────────────────────────── */

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: linear-gradient(
        -45deg,
        #0a0a1a 0%,
        #0d1033 25%,
        #1a0a2e 50%,
        #0a1628 75%,
        #0a0a1a 100%
    );
    background-size: 400% 400%;
    animation: meshDrift 25s ease infinite;
    min-height: 100vh;
}

/* Noise overlay for texture depth */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* ── Hero ─────────────────────────────────────────────── */

.hero-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -1.5px;
    background: linear-gradient(
        135deg,
        #c084fc 0%,
        #818cf8 20%,
        #60a5fa 40%,
        #34d399 60%,
        #a78bfa 80%,
        #c084fc 100%
    );
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: heroGlow 6s ease-in-out infinite;
    margin-bottom: 0.1rem;
    text-shadow: 0 0 80px rgba(139,92,246,0.15);
}

.hero-sub {
    text-align: center;
    color: #64748b;
    font-size: 0.88rem;
    font-weight: 400;
    margin-bottom: 2.2rem;
    line-height: 1.7;
    letter-spacing: 0.2px;
}

/* ── Source Badges ─────────────────────────────────────── */

.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.64rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.4px;
    margin-right: 5px;
    text-transform: uppercase;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    transition: transform 0.15s ease;
}
.badge:hover { transform: scale(1.05); }

.badge-libgen {
    background: rgba(6,78,59,0.6); color: #6ee7b7;
    border: 1px solid rgba(110,231,183,0.2);
}
.badge-zlib {
    background: rgba(30,58,95,0.6); color: #93c5fd;
    border: 1px solid rgba(147,197,253,0.2);
}
.badge-anna {
    background: rgba(76,29,87,0.6); color: #e879f9;
    border: 1px solid rgba(232,121,249,0.2);
}
.badge-openlib {
    background: rgba(120,53,15,0.5); color: #fcd34d;
    border: 1px solid rgba(252,211,77,0.2);
}
.badge-ddg {
    background: rgba(30,41,59,0.6); color: #94a3b8;
    border: 1px solid rgba(148,163,184,0.15);
}

/* ── Doc-Type Badges ──────────────────────────────────── */

.dtype-book {
    background: rgba(69,26,3,0.5); color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.25);
    box-shadow: 0 0 8px rgba(251,191,36,0.08);
}
.dtype-academic {
    background: rgba(2,44,34,0.5); color: #34d399;
    border: 1px solid rgba(52,211,153,0.25);
    box-shadow: 0 0 8px rgba(52,211,153,0.08);
}
.dtype-general {
    background: rgba(30,41,59,0.5); color: #94a3b8;
    border: 1px solid rgba(148,163,184,0.15);
}

/* ── Result Cards ─────────────────────────────────────── */

.result-card {
    background: rgba(255,255,255,0.025);
    backdrop-filter: blur(12px) saturate(150%);
    -webkit-backdrop-filter: blur(12px) saturate(150%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 14px 18px;
    margin-bottom: 8px;
    animation: cardReveal 0.4s ease-out both, borderShimmer 4s ease infinite;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

/* Subtle inner glow on hover */
.result-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 14px;
    background: radial-gradient(
        ellipse at var(--x, 50%) var(--y, 50%),
        rgba(139,92,246,0.06) 0%,
        transparent 70%
    );
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}
.result-card:hover::after { opacity: 1; }

.result-card:hover {
    border-color: rgba(139,92,246,0.35);
    transform: translateY(-1px);
    box-shadow:
        0 4px 24px rgba(139,92,246,0.08),
        0 0 1px rgba(139,92,246,0.3);
}

.result-card.direct {
    border-left: 3px solid #34d399;
    box-shadow: inset 3px 0 12px -4px rgba(52,211,153,0.1);
}
.result-card.page {
    border-left: 3px solid rgba(96,165,250,0.6);
    box-shadow: inset 3px 0 12px -4px rgba(96,165,250,0.08);
}

.result-title {
    color: #e2e8f0;
    font-size: 0.88rem;
    font-weight: 500;
    margin: 6px 0 4px;
    line-height: 1.4;
}

.result-link {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: #60a5fa;
    word-break: break-all;
    opacity: 0.8;
    transition: opacity 0.2s;
}
.result-link:hover { opacity: 1; }

.result-link a {
    color: #60a5fa;
    text-decoration: none;
    transition: color 0.2s;
}
.result-link a:hover {
    color: #93c5fd;
    text-decoration: underline;
    text-underline-offset: 3px;
}

.pdf-tag {
    color: #34d399;
    font-size: 0.68rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-left: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    animation: pulseRing 2s ease infinite;
    border-radius: 4px;
    padding: 1px 5px;
    background: rgba(52,211,153,0.08);
}

/* ── Stat Pills ───────────────────────────────────────── */

.stat-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin: 1.4rem 0;
}

.stat-pill {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.78rem;
    font-weight: 500;
    color: #cbd5e1;
    transition: all 0.2s ease;
    cursor: default;
}
.stat-pill:hover {
    background: rgba(139,92,246,0.08);
    border-color: rgba(139,92,246,0.25);
    transform: scale(1.04);
}

/* ── Section Headers ──────────────────────────────────── */

.section-header {
    font-size: 0.72rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.6rem 0 0.7rem;
    padding: 6px 12px;
    border-radius: 6px;
}

.sh-book {
    color: #fbbf24;
    border-left: 3px solid #fbbf24;
    background: linear-gradient(90deg, rgba(251,191,36,0.06) 0%, transparent 100%);
    text-shadow: 0 0 20px rgba(251,191,36,0.15);
}
.sh-academic {
    color: #34d399;
    border-left: 3px solid #34d399;
    background: linear-gradient(90deg, rgba(52,211,153,0.06) 0%, transparent 100%);
    text-shadow: 0 0 20px rgba(52,211,153,0.15);
}
.sh-general {
    color: #94a3b8;
    border-left: 3px solid #64748b;
    background: linear-gradient(90deg, rgba(148,163,184,0.04) 0%, transparent 100%);
}

/* ── Streamlit Overrides (guardrails) ─────────────────── */

/* Hide Streamlit branding */
#MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; height: 0; }

/* Form button */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #7c3aed, #6366f1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.25) !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(124,58,237,0.35) !important;
    background: linear-gradient(135deg, #8b5cf6, #818cf8) !important;
}
.stFormSubmitButton > button:active {
    transform: scale(0.97) !important;
}

/* Text input */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-size: 0.9rem !important;
    padding: 10px 16px !important;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.1) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #475569 !important;
    font-style: italic;
}

/* Spinner */
.stSpinner > div { color: #a78bfa !important; }

/* Warning messages */
.stAlert {
    background: rgba(251,191,36,0.06) !important;
    border-color: rgba(251,191,36,0.2) !important;
    border-radius: 10px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(139,92,246,0.25);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(139,92,246,0.4); }

/* ── Mobile ───────────────────────────────────────────── */

@media (max-width: 640px) {
    .hero-title { font-size: 2.2rem; letter-spacing: -1px; }
    .hero-sub   { font-size: 0.8rem; }
    .stat-pill  { font-size: 0.7rem; padding: 4px 10px; }
    .result-card { padding: 10px 13px; }
    .result-title { font-size: 0.82rem; }
    .badge { font-size: 0.58rem; padding: 2px 7px; }
}
</style>
""", unsafe_allow_html=True)


from pdf_hunter import BookResult, hunt_for_pdf_async  # noqa: E402


SOURCE_BADGE = {
    "LibGen":            ("badge-libgen",  "LibGen"),
    "Z-Library":         ("badge-zlib",    "Z-Lib"),
    "Anna's Archive":    ("badge-anna",    "Anna's"),
    "Open Library / IA": ("badge-openlib", "Open Lib"),
    "DuckDuckGo":        ("badge-ddg",     "DDG"),
}

DOCTYPE_BADGE = {
    "Book":        ("dtype-book",     "📖 Book"),
    "Academic":    ("dtype-academic", "🎓 Academic"),
    "General PDF": ("dtype-general",  "📄 PDF"),
}


@st.cache_data(ttl=86400, show_spinner=False)
def cached_search(query: str) -> list[dict]:
    """
    24-hour cache keyed on query string.
    Prevents hammering shadow libraries with duplicate requests
    and reduces Streamlit Cloud egress load significantly.
    """
    results = asyncio.run(hunt_for_pdf_async(query))
    return [r.to_dict() for r in results]


def render_result(r: dict, idx: int) -> None:
    src_cls, src_label = SOURCE_BADGE.get(r["source"], ("badge-ddg", r["source"]))
    dt_cls, dt_label   = DOCTYPE_BADGE.get(r.get("doc_type", "General PDF"), ("dtype-general", "📄 PDF"))
    card_class  = "direct" if r["is_direct_pdf"] else "page"
    pdf_tag     = '<span class="pdf-tag">⬇ PDF</span>' if r["is_direct_pdf"] else ""
    safe_title  = html.escape(r["title"])
    safe_link   = html.escape(r["link"])
    mirror_html = (
        f'<div class="result-link" style="margin-top:3px">Mirror: '
        f'<a href="{html.escape(r["mirror"])}" target="_blank">{html.escape(r["mirror"][:80])}</a></div>'
        if r.get("mirror") else ""
    )
    # HTML must start at column 0 — Markdown treats 4+ leading spaces as a <pre><code> block
    st.markdown(
f"""<div class="result-card {card_class}">
<div><span class="badge {src_cls}">{src_label}</span><span class="badge {dt_cls}">{dt_label}</span>{pdf_tag}</div>
<div class="result-title">{idx}. {safe_title}</div>
<div class="result-link"><a href="{safe_link}" target="_blank">{safe_link}</a></div>
{mirror_html}
</div>""",
        unsafe_allow_html=True,
    )


def section(label: str, css_class: str) -> None:
    st.markdown(f'<div class="section-header {css_class}">{label}</div>', unsafe_allow_html=True)


# ── UI ──────────────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">📚 PDF Hunter</div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-sub">
    Universal PDF Search Engine — books, university cours/TD/TP, research papers &amp; more<br>
    <span style="color:#64748b;font-size:0.82rem;">
        LibGen · Z-Library · Anna's Archive · Open Library · Academia.edu · Open Web
    </span>
</div>
""", unsafe_allow_html=True)

with st.form("search_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            label="query",
            label_visibility="collapsed",
            placeholder='e.g. "Electromagnetism TD", "Python Cheat Sheet", or "Les Misérables"',
        )
    with col2:
        submitted = st.form_submit_button("🔍 Hunt", use_container_width=True)

if submitted and query.strip():
    with st.spinner("Scanning all sources — 8 parallel dorks + 4 shadow libraries…"):
        raw = cached_search(query.strip())

    books    = [r for r in raw if r.get("doc_type") == "Book"]
    academic = [r for r in raw if r.get("doc_type") == "Academic"]
    general  = [r for r in raw if r.get("doc_type", "General PDF") == "General PDF"]

    direct_count = sum(1 for r in raw if r["is_direct_pdf"])

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill">🎯 {len(raw)} total</div>
        <div class="stat-pill">📖 {len(books)} books</div>
        <div class="stat-pill">🎓 {len(academic)} academic</div>
        <div class="stat-pill">📄 {len(general)} general</div>
        <div class="stat-pill">⬇ {direct_count} direct PDFs</div>
    </div>
    """, unsafe_allow_html=True)

    if not raw:
        st.warning("No results found. Try different keywords or a shorter query.")
    else:
        if books:
            section("📖 Books", "sh-book")
            for i, r in enumerate(books, 1):
                render_result(r, i)

        if academic:
            section("🎓 Academic Documents (Cours · TD · TP · Research)", "sh-academic")
            for i, r in enumerate(academic, 1):
                render_result(r, i)

        if general:
            section("📄 General PDFs", "sh-general")
            for i, r in enumerate(general, 1):
                render_result(r, i)

elif submitted:
    st.warning("Please enter a search query.")

st.markdown("""
<hr style="border-color:rgba(255,255,255,0.06);margin-top:3rem;">
<div style="text-align:center;color:#475569;font-size:0.78rem;padding-bottom:1rem;">
    PDF Hunter — open source &nbsp;·&nbsp; Built by
    <a href="https://github.com/Guettaf-hossam" style="color:#7c3aed;">knight</a>
    &nbsp;·&nbsp; searches public indexes only
</div>
""", unsafe_allow_html=True)
