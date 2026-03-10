from __future__ import annotations

import asyncio
import html
import streamlit.components.v1 as components

import nest_asyncio
import streamlit as st

nest_asyncio.apply()

st.set_page_config(
    page_title="PDF Hunter",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto",
)
def inject_ga_and_nuke_badge():
    # totaniom 
    html_code = (
        "<script async src='https://"
        "www.googletagmanager.com/"
        "gtag/js?id=G-3SP3QLJ9HD'>"
        "</script><script>"
        "window.dataLayer="
        "window.dataLayer||[];"
        "function gtag(){"
        "dataLayer.push(arguments);}"
        "gtag('js',new Date());"
        "gtag('config','G-3SP3QLJ9HD');"
        "const h=()=>{"
        "try{"
        "const p=window.parent.document;"
        "const q='[class*=\"viewerBadge\"],"
        "a[href*=\"streamlit\"],"
        ".stDeployButton';"
        "const targets=p.querySelectorAll(q);"
        "targets.forEach(n=>{"
        "n.style.setProperty("
        "'display','none','important')"
        "});"
        "}catch(e){}"
        "};"
        "h();setInterval(h,2000);"
        "</script>"
    )
    components.html(html_code, height=0, width=0)

inject_ga_and_nuke_badge()






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

/* ── THE ULTIMATE STREAMLIT WATERMARK ANNIHILATOR ── */
#MainMenu, footer { display: none !important; visibility: hidden !important; }
header[data-testid="stHeader"] { background: transparent !important; }

[class^="viewerBadge_"],
[class*=" viewerBadge_"],
[class*="viewerBadge_container"],
a[href*="streamlit.io/cloud"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    position: absolute !important;
    pointer-events: none !important;
}


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

/* ── Sidebar Styling ───────────────────────────────── */

section[data-testid="stSidebar"] {
    background: #0c0c24 !important;
    border-right: 1px solid rgba(139,92,246,0.1) !important;
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #c084fc !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    margin-bottom: 0.4rem !important;
}

section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stCheckbox label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
}

section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
}

section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.82rem !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(139,92,246,0.12) !important;
    margin: 0.8rem 0 !important;
}

.sidebar-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}

.sidebar-subtitle {
    font-size: 0.62rem;
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}

.filter-summary {
    background: rgba(139,92,246,0.06);
    border: 1px solid rgba(139,92,246,0.12);
    border-radius: 8px;
    padding: 8px 12px;
    margin: 0.6rem 0;
    animation: fadeSlideUp 0.3s ease-out both;
}

.filter-summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2px 0;
}

.filter-summary-label {
    font-size: 0.62rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
}

.filter-summary-value {
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: #c084fc;
}

.source-count-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
    margin: 2px 0;
}

.source-count-name {
    font-size: 0.7rem;
    font-weight: 500;
    color: #94a3b8;
}

.source-count-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 1px 8px;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
}

.scn-libgen  { color: #6ee7b7; }
.scn-zlib    { color: #93c5fd; }
.scn-anna    { color: #e879f9; }
.scn-openlib { color: #fcd34d; }
.scn-ddg     { color: #64748b; }

/* ── Download Button ───────────────────────────────── */

section[data-testid="stSidebar"] .stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #0d9488) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.3px;
    width: 100% !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 2px 12px rgba(5,150,105,0.2) !important;
}
section[data-testid="stSidebar"] .stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(5,150,105,0.3) !important;
}

/* ── Active Filters Banner ─────────────────────────── */

.active-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin: 0.5rem 0 1rem;
    animation: fadeSlideUp 0.3s ease-out both;
}

.active-filter-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #c084fc;
    border: 1px solid rgba(139,92,246,0.2);
    background: rgba(139,92,246,0.06);
    border-radius: 4px;
    padding: 2px 8px;
}

/* ── No Results After Filter ───────────────────────── */

.no-filter-results {
    text-align: center;
    padding: 2rem 1rem;
    color: #475569;
    animation: fadeSlideUp 0.4s ease-out both;
}

.no-filter-results .nfr-icon {
    font-size: 2rem;
    display: block;
    margin-bottom: 0.5rem;
    opacity: 0.5;
}

.no-filter-results .nfr-text {
    font-size: 0.82rem;
    font-weight: 500;
}

.no-filter-results .nfr-hint {
    font-size: 0.68rem;
    color: #334155;
    margin-top: 0.3rem;
}

/* ── Pagination ────────────────────────────────────── */

.pagination-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    margin: 1.5rem 0;
    padding: 10px 0;
    animation: fadeSlideUp 0.3s ease-out both;
}

.page-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #64748b;
    letter-spacing: 0.5px;
}

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
import csv
import io as _io


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

ALL_SOURCES = ["LibGen", "Z-Library", "Anna's Archive", "Open Library / IA", "DuckDuckGo"]
ALL_DOC_TYPES = ["Book", "Academic", "General PDF"]

RESULTS_PER_PAGE = 15


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


def results_to_csv(results: list[dict]) -> str:
    buf = _io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["#", "Title", "Source", "Type", "Direct PDF", "Link", "Mirror"])
    for i, r in enumerate(results, 1):
        writer.writerow([
            i, r["title"], r["source"], r.get("doc_type", "General PDF"),
            "Yes" if r["is_direct_pdf"] else "No", r["link"], r.get("mirror", ""),
        ])
    return buf.getvalue()


def apply_filters(raw: list[dict], sources: list[str], doc_types: list[str],
                  direct_only: bool, search_text: str, sort_mode: str) -> list[dict]:
    filtered = raw

    # Source filter
    if sources and set(sources) != set(ALL_SOURCES):
        filtered = [r for r in filtered if r["source"] in sources]

    # Doc type filter
    if doc_types and set(doc_types) != set(ALL_DOC_TYPES):
        filtered = [r for r in filtered if r.get("doc_type", "General PDF") in doc_types]

    # Direct PDF only
    if direct_only:
        filtered = [r for r in filtered if r["is_direct_pdf"]]

    # Search within results
    if search_text.strip():
        q = search_text.strip().lower()
        filtered = [r for r in filtered if q in r["title"].lower() or q in r["link"].lower()]

    # Sorting
    source_rank = {
        "LibGen": 0, "Z-Library": 1,
        "Open Library / IA": 2, "Anna's Archive": 3, "DuckDuckGo": 4,
    }
    if sort_mode == "Relevance (default)":
        filtered.sort(key=lambda r: (not r["is_direct_pdf"], source_rank.get(r["source"], 9)))
    elif sort_mode == "Title A → Z":
        filtered.sort(key=lambda r: r["title"].lower())
    elif sort_mode == "Title Z → A":
        filtered.sort(key=lambda r: r["title"].lower(), reverse=True)
    elif sort_mode == "Source":
        filtered.sort(key=lambda r: source_rank.get(r["source"], 9))
    elif sort_mode == "Direct PDFs first":
        filtered.sort(key=lambda r: (not r["is_direct_pdf"], r["title"].lower()))

    return filtered


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
    st.session_state["last_results"] = raw
    st.session_state["last_query"] = query.strip()
    st.session_state["page"] = 1

elif submitted:
    st.warning("Please enter a search query.")

# ── Sidebar Filters ──────────────────────────────────────────────────────────

raw = st.session_state.get("last_results", [])

with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Filters</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Refine your results</div>', unsafe_allow_html=True)

    if raw:
        # Source breakdown
        st.markdown("### 📡 Sources")
        source_counts = {}
        for r in raw:
            source_counts[r["source"]] = source_counts.get(r["source"], 0) + 1

        css_map = {"LibGen": "scn-libgen", "Z-Library": "scn-zlib",
                   "Anna's Archive": "scn-anna", "Open Library / IA": "scn-openlib",
                   "DuckDuckGo": "scn-ddg"}
        for src in ALL_SOURCES:
            cnt = source_counts.get(src, 0)
            cls = css_map.get(src, "scn-ddg")
            st.markdown(
                f'<div class="source-count-bar">'
                f'<span class="source-count-name">{src}</span>'
                f'<span class="source-count-num {cls}">{cnt}</span></div>',
                unsafe_allow_html=True,
            )

        available_sources = [s for s in ALL_SOURCES if source_counts.get(s, 0) > 0]
        selected_sources = st.multiselect(
            "Filter by source",
            options=available_sources,
            default=available_sources,
            key="filter_sources",
        )

        st.markdown("---")

        # Doc type filter
        st.markdown("### 📂 Document Type")
        doc_counts = {}
        for r in raw:
            dt = r.get("doc_type", "General PDF")
            doc_counts[dt] = doc_counts.get(dt, 0) + 1

        available_types = [t for t in ALL_DOC_TYPES if doc_counts.get(t, 0) > 0]
        selected_types = st.multiselect(
            "Filter by type",
            options=available_types,
            default=available_types,
            key="filter_types",
        )

        st.markdown("---")

        # Direct PDF toggle
        st.markdown("### ⚡ Quick Access")
        direct_only = st.checkbox("Direct PDF links only", value=False, key="filter_direct")

        st.markdown("---")

        # Search within results
        st.markdown("### 🔎 Search in Results")
        result_search = st.text_input(
            "Filter titles / URLs",
            value="",
            placeholder="Type to filter…",
            key="filter_text",
        )

        st.markdown("---")

        # Sort
        st.markdown("### 📊 Sort Order")
        sort_mode = st.selectbox(
            "Sort results by",
            options=[
                "Relevance (default)",
                "Direct PDFs first",
                "Title A → Z",
                "Title Z → A",
                "Source",
            ],
            index=0,
            key="filter_sort",
        )

        st.markdown("---")

        # Pagination size
        st.markdown("### 📄 Results Per Page")
        per_page = st.select_slider(
            "Show per page",
            options=[5, 10, 15, 25, 50, 100],
            value=15,
            key="per_page",
        )

        st.markdown("---")

        # Export
        st.markdown("### 💾 Export")
    else:
        selected_sources = ALL_SOURCES
        selected_types = ALL_DOC_TYPES
        direct_only = False
        result_search = ""
        sort_mode = "Relevance (default)"
        per_page = RESULTS_PER_PAGE

        st.markdown(
            '<div style="color:#475569;font-size:0.76rem;text-align:center;padding:2rem 0;">'
            '🔍 Search for something first<br>'
            '<span style="font-size:0.65rem;color:#334155;">Filters will appear here</span>'
            '</div>',
            unsafe_allow_html=True,
        )


# ── Display Results ──────────────────────────────────────────────────────────

if raw:
    filtered = apply_filters(raw, selected_sources, selected_types, direct_only, result_search, sort_mode)

    books    = [r for r in filtered if r.get("doc_type") == "Book"]
    academic = [r for r in filtered if r.get("doc_type") == "Academic"]
    general  = [r for r in filtered if r.get("doc_type", "General PDF") == "General PDF"]
    direct_count = sum(1 for r in filtered if r["is_direct_pdf"])

    # Active filters banner
    active_chips = []
    if set(selected_sources) != set(ALL_SOURCES) and selected_sources:
        for s in selected_sources:
            active_chips.append(s)
    if set(selected_types) != set(ALL_DOC_TYPES) and selected_types:
        for t in selected_types:
            active_chips.append(t)
    if direct_only:
        active_chips.append("Direct PDF only")
    if result_search.strip():
        active_chips.append(f'"{result_search.strip()}"')
    if sort_mode != "Relevance (default)":
        active_chips.append(f"Sort: {sort_mode}")

    if active_chips:
        chips_html = " ".join(
            f'<span class="active-filter-chip">{html.escape(c)}</span>' for c in active_chips
        )
        st.markdown(
            f'<div class="active-filters">🎯 {chips_html}</div>',
            unsafe_allow_html=True,
        )

    # Stat bar
    st.markdown(
f"""<div class="stat-bar">
<div class="stat-cell"><span class="stat-num clr-total">{len(filtered)}</span><span class="stat-label">Filtered</span></div>
<div class="stat-cell"><span class="stat-num clr-books">{len(books)}</span><span class="stat-label">Books</span></div>
<div class="stat-cell"><span class="stat-num clr-academic">{len(academic)}</span><span class="stat-label">Academic</span></div>
<div class="stat-cell"><span class="stat-num clr-general">{len(general)}</span><span class="stat-label">General</span></div>
<div class="stat-cell"><span class="stat-num clr-direct">{direct_count}</span><span class="stat-label">Direct</span></div>
</div>""",
        unsafe_allow_html=True,
    )

    # Out of total info
    if len(filtered) != len(raw):
        st.markdown(
            f'<div style="text-align:center;font-size:0.65rem;color:#475569;'
            f'font-family:JetBrains Mono,monospace;margin-top:-0.5rem;margin-bottom:1rem;">'
            f'Showing {len(filtered)} of {len(raw)} total results</div>',
            unsafe_allow_html=True,
        )

    if not filtered:
        st.markdown(
            '<div class="no-filter-results">'
            '<span class="nfr-icon">🔍</span>'
            '<div class="nfr-text">No results match your filters</div>'
            '<div class="nfr-hint">Try adjusting your filter settings in the sidebar</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        # Pagination
        page = st.session_state.get("page", 1)
        total_pages = max(1, -(-len(filtered) // per_page))  # ceil div
        if page > total_pages:
            page = total_pages
            st.session_state["page"] = page

        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(filtered))
        page_results = filtered[start_idx:end_idx]

        # Categorize page results
        page_books = [r for r in page_results if r.get("doc_type") == "Book"]
        page_academic = [r for r in page_results if r.get("doc_type") == "Academic"]
        page_general = [r for r in page_results if r.get("doc_type", "General PDF") == "General PDF"]

        counter = start_idx + 1

        if page_books:
            section("📖 Books", "sh-book")
            for r in page_books:
                render_result(r, counter)
                counter += 1

        if page_academic:
            section("🎓 Academic — Cours · TD · TP · Research", "sh-academic")
            for r in page_academic:
                render_result(r, counter)
                counter += 1

        if page_general:
            section("📄 General PDFs", "sh-general")
            for r in page_general:
                render_result(r, counter)
                counter += 1

        # Pagination controls
        if total_pages > 1:
            st.markdown(
                f'<div class="pagination-bar">'
                f'<span class="page-info">Page {page} of {total_pages} · '
                f'{start_idx + 1}–{end_idx} of {len(filtered)} results</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
            with pcol1:
                if page > 1:
                    if st.button("← Previous", key="prev_page", use_container_width=True):
                        st.session_state["page"] = page - 1
                        st.rerun()
            with pcol3:
                if page < total_pages:
                    if st.button("Next →", key="next_page", use_container_width=True):
                        st.session_state["page"] = page + 1
                        st.rerun()

    # Export in sidebar (only when results exist)
    with st.sidebar:
        if filtered:
            csv_data = results_to_csv(filtered)
            st.download_button(
                label=f"📥 Download CSV ({len(filtered)} results)",
                data=csv_data,
                file_name=f"pdf_hunter_{st.session_state.get('last_query', 'results')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Filter summary
        if raw:
            st.markdown(
                f'<div class="filter-summary">'
                f'<div class="filter-summary-row">'
                f'<span class="filter-summary-label">Total found</span>'
                f'<span class="filter-summary-value">{len(raw)}</span></div>'
                f'<div class="filter-summary-row">'
                f'<span class="filter-summary-label">After filters</span>'
                f'<span class="filter-summary-value">{len(filtered)}</span></div>'
                f'<div class="filter-summary-row">'
                f'<span class="filter-summary-label">Hidden</span>'
                f'<span class="filter-summary-value">{len(raw) - len(filtered)}</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

st.markdown("""
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.04);margin-top:3rem;">
<div style="text-align:center;padding:1.2rem 0 1rem;animation:fadeSlideUp 0.5s ease-out both;">
    <div style="font-size:0.7rem;color:#334155;letter-spacing:1px;text-transform:uppercase;font-family:'JetBrains Mono',monospace;">
        Built by
        <a href="https://github.com/Guettaf-hossam" style="color:#7c3aed;text-decoration:none;font-weight:600;">Houssem Eddine Guettaf</a>
    </div>
    <div style="font-size:0.6rem;color:#1e293b;margin-top:4px;">
        PDF Hunter — open source · searches public indexes only
    </div>
</div>
""", unsafe_allow_html=True)
