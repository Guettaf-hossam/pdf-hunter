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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

.hero-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.hero-sub {
    text-align: center;
    color: #94a3b8;
    font-size: 0.92rem;
    margin-bottom: 2rem;
    line-height: 1.6;
}

/* Source badges */
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 600;
    margin-right: 5px;
}
.badge-libgen  { background: #064e3b; color: #6ee7b7; }
.badge-zlib    { background: #1e3a5f; color: #93c5fd; }
.badge-anna    { background: #4c1d57; color: #e879f9; }
.badge-openlib { background: #78350f; color: #fcd34d; }
.badge-ddg     { background: #1e293b; color: #94a3b8; }

/* Doc-type badges */
.dtype-book     { background: #451a03; color: #fbbf24; border: 1px solid #92400e; }
.dtype-academic { background: #022c22; color: #34d399; border: 1px solid #065f46; }
.dtype-general  { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

.result-card {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 13px 17px;
    margin-bottom: 9px;
    transition: border-color 0.2s;
}
.result-card:hover  { border-color: rgba(167,139,250,0.4); }
.result-card.direct { border-left: 3px solid #34d399; }
.result-card.page   { border-left: 3px solid #60a5fa; }

.result-title { color: #e2e8f0; font-size: 0.9rem; font-weight: 500; margin: 5px 0 4px; }
.result-link  { font-size: 0.76rem; color: #60a5fa; word-break: break-all; }
.result-link a { color: #60a5fa; text-decoration: none; }
.result-link a:hover { text-decoration: underline; }
.pdf-tag { color: #34d399; font-size: 0.72rem; font-weight: 600; margin-left: 5px; }

.stat-row {
    display: flex; gap: 10px; justify-content: center;
    flex-wrap: wrap; margin: 1.2rem 0;
}
.stat-pill {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #cbd5e1;
}
.section-header {
    font-size: 0.8rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 1.4rem 0 0.6rem;
    padding-left: 4px;
}
.sh-book     { color: #fbbf24; border-left: 3px solid #fbbf24; padding-left: 10px; }
.sh-academic { color: #34d399; border-left: 3px solid #34d399; padding-left: 10px; }
.sh-general  { color: #94a3b8; border-left: 3px solid #94a3b8; padding-left: 10px; }
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
