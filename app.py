from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

# --- Page config (must be first Streamlit call) ---
st.set_page_config(
    page_title="PDF Hunter",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Hero title */
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
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* Source badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 6px;
}
.badge-libgen       { background: #064e3b; color: #6ee7b7; }
.badge-zlib         { background: #1e3a5f; color: #93c5fd; }
.badge-anna         { background: #4c1d57; color: #e879f9; }
.badge-openlib      { background: #78350f; color: #fcd34d; }
.badge-ddg          { background: #1e293b; color: #94a3b8; }

/* Result card */
.result-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.result-card:hover {
    border-color: rgba(167,139,250,0.4);
}
.result-card.direct {
    border-left: 3px solid #34d399;
}
.result-card.page {
    border-left: 3px solid #60a5fa;
}

.result-title {
    color: #e2e8f0;
    font-size: 0.92rem;
    font-weight: 500;
    margin-bottom: 4px;
}
.result-link {
    font-size: 0.78rem;
    color: #60a5fa;
    word-break: break-all;
}
.result-link a {
    color: #60a5fa;
    text-decoration: none;
}
.result-link a:hover { text-decoration: underline; }

.pdf-tag {
    color: #34d399;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 6px;
}

/* Stat pills */
.stat-row {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    margin: 1.2rem 0;
}
.stat-pill {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 999px;
    padding: 6px 16px;
    font-size: 0.82rem;
    color: #cbd5e1;
}

.section-header {
    color: #a78bfa;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.4rem 0 0.6rem;
}
</style>
""", unsafe_allow_html=True)


# --- Import search functions ---
try:
    from pdf_hunter import (
        search_duckduckgo,
        search_libgen,
        search_annas_archive,
        search_open_library,
        search_zlibrary,
        BookResult,
    )
    BACKEND_OK = True
except ImportError as e:
    BACKEND_OK = False
    st.error(f"Backend import error: {e}")


SOURCE_BADGE = {
    "LibGen":          ("badge-libgen",  "LibGen"),
    "Z-Library":       ("badge-zlib",    "Z-Library"),
    "Anna's Archive":  ("badge-anna",    "Anna's Archive"),
    "Open Library / IA": ("badge-openlib", "Open Library"),
    "DuckDuckGo":      ("badge-ddg",     "DuckDuckGo"),
}


def render_result(r: "BookResult", idx: int) -> None:
    cls, label = SOURCE_BADGE.get(r.source, ("badge-ddg", r.source))
    card_class = "direct" if r.is_direct_pdf else "page"
    pdf_tag = '<span class="pdf-tag">⬇ PDF</span>' if r.is_direct_pdf else ""
    mirror_html = (
        f'<div class="result-link" style="margin-top:3px">Mirror: '
        f'<a href="{r.mirror}" target="_blank">{r.mirror[:80]}</a></div>'
        if r.mirror else ""
    )
    st.markdown(f"""
    <div class="result-card {card_class}">
        <div>
            <span class="badge {cls}">{label}</span>{pdf_tag}
        </div>
        <div class="result-title">{idx}. {r.title}</div>
        <div class="result-link"><a href="{r.link}" target="_blank">{r.link}</a></div>
        {mirror_html}
    </div>
    """, unsafe_allow_html=True)


def run_search(book_name: str) -> list["BookResult"]:
    sources = {
        "DuckDuckGo":  lambda: search_duckduckgo(book_name, 10),
        "LibGen":      lambda: search_libgen(book_name),
        "Anna's":      lambda: search_annas_archive(book_name),
        "OpenLibrary": lambda: search_open_library(book_name),
        "ZLibrary":    lambda: search_zlibrary(book_name),
    }

    all_results: list[BookResult] = []
    seen: set[str] = set()

    # max_workers=2 — keeps the server-side CPU usage low
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(fn): name for name, fn in sources.items()}
        for future in as_completed(futures):
            try:
                for r in future.result():
                    if r.link not in seen:
                        seen.add(r.link)
                        all_results.append(r)
            except Exception:
                pass

    source_rank = {
        "LibGen": 0, "Z-Library": 1,
        "Open Library / IA": 2, "Anna's Archive": 3, "DuckDuckGo": 4,
    }
    all_results.sort(
        key=lambda r: (not r.is_direct_pdf, source_rank.get(r.source, 9))
    )
    return all_results


# ══════════════════════════════════════════════
# UI Layout
# ══════════════════════════════════════════════

st.markdown('<div class="hero-title">📚 PDF Hunter</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Search across LibGen · Z-Library · Anna\'s Archive · Open Library · DuckDuckGo</div>',
    unsafe_allow_html=True,
)

with st.form("search_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            label="book",
            label_visibility="collapsed",
            placeholder='e.g. "Ouragan Marc Auburn"  or  "Les Misérables Victor Hugo"',
        )
    with col2:
        submitted = st.form_submit_button("🔍 Hunt", use_container_width=True)

if submitted and query.strip() and BACKEND_OK:
    st.markdown('<div class="stat-row">', unsafe_allow_html=True)

    with st.spinner("Scanning all sources…"):
        results = run_search(query.strip())

    direct = [r for r in results if r.is_direct_pdf]
    pages  = [r for r in results if not r.is_direct_pdf]

    # Stats row
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill">🎯 {len(results)} total results</div>
        <div class="stat-pill">⬇ {len(direct)} direct PDFs</div>
        <div class="stat-pill">🔗 {len(pages)} page links</div>
    </div>
    """, unsafe_allow_html=True)

    if not results:
        st.warning("No results found across all sources. Try a shorter or simpler book title.")
    else:
        if direct:
            st.markdown('<div class="section-header">Direct PDF Downloads</div>', unsafe_allow_html=True)
            for i, r in enumerate(direct, 1):
                render_result(r, i)

        if pages:
            st.markdown('<div class="section-header">Page / Metadata Links</div>', unsafe_allow_html=True)
            for i, r in enumerate(pages, 1):
                render_result(r, i)

elif submitted and not query.strip():
    st.warning("Please enter a book name.")

# Footer
st.markdown("""
<hr style="border-color: rgba(255,255,255,0.06); margin-top: 3rem;">
<div style="text-align:center; color:#475569; font-size:0.78rem; padding-bottom:1rem;">
    PDF Hunter — open source · searches public indexes only
</div>
""", unsafe_allow_html=True)
