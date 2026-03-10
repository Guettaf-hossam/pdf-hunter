from __future__ import annotations

import asyncio

import nest_asyncio
import streamlit as st

# Streamlit runs its own event loop — nest_asyncio patches it so asyncio.run()
# can be called from within an already-running loop without raising RuntimeError.
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
    font-size: 1rem;
    margin-bottom: 2rem;
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 6px;
}
.badge-libgen  { background: #064e3b; color: #6ee7b7; }
.badge-zlib    { background: #1e3a5f; color: #93c5fd; }
.badge-anna    { background: #4c1d57; color: #e879f9; }
.badge-openlib { background: #78350f; color: #fcd34d; }
.badge-ddg     { background: #1e293b; color: #94a3b8; }

.result-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.result-card:hover  { border-color: rgba(167,139,250,0.4); }
.result-card.direct { border-left: 3px solid #34d399; }
.result-card.page   { border-left: 3px solid #60a5fa; }

.result-title { color: #e2e8f0; font-size: 0.92rem; font-weight: 500; margin-bottom: 4px; }
.result-link  { font-size: 0.78rem; color: #60a5fa; word-break: break-all; }
.result-link a { color: #60a5fa; text-decoration: none; }
.result-link a:hover { text-decoration: underline; }
.pdf-tag { color: #34d399; font-size: 0.75rem; font-weight: 600; margin-left: 6px; }

.stat-row {
    display: flex; gap: 12px; justify-content: center;
    flex-wrap: wrap; margin: 1.2rem 0;
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
    color: #a78bfa; font-size: 0.85rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px; margin: 1.4rem 0 0.6rem;
}
</style>
""", unsafe_allow_html=True)


from pdf_hunter import BookResult, hunt_for_pdf_async  # noqa: E402


SOURCE_BADGE = {
    "LibGen":            ("badge-libgen",  "LibGen"),
    "Z-Library":         ("badge-zlib",    "Z-Library"),
    "Anna's Archive":    ("badge-anna",    "Anna's Archive"),
    "Open Library / IA": ("badge-openlib", "Open Library"),
    "DuckDuckGo":        ("badge-ddg",     "DuckDuckGo"),
}


@st.cache_data(ttl=86400, show_spinner=False)
def cached_search(book_name: str) -> list[dict]:
    """
    24-hour cache keyed on the search query.
    Prevents hammering the shadow libraries with duplicate requests,
    which would risk IP bans on Streamlit Cloud's shared egress IPs.
    Returns plain dicts so st.cache_data can serialize the result.
    """
    results = asyncio.run(hunt_for_pdf_async(book_name))
    return [r.to_dict() for r in results]


def render_result(r: dict, idx: int) -> None:
    cls, label = SOURCE_BADGE.get(r["source"], ("badge-ddg", r["source"]))
    card_class  = "direct" if r["is_direct_pdf"] else "page"
    pdf_tag     = '<span class="pdf-tag">⬇ PDF</span>' if r["is_direct_pdf"] else ""
    mirror_html = (
        f'<div class="result-link" style="margin-top:3px">Mirror: '
        f'<a href="{r["mirror"]}" target="_blank">{r["mirror"][:80]}</a></div>'
        if r.get("mirror") else ""
    )
    st.markdown(f"""
    <div class="result-card {card_class}">
        <div><span class="badge {cls}">{label}</span>{pdf_tag}</div>
        <div class="result-title">{idx}. {r["title"]}</div>
        <div class="result-link"><a href="{r["link"]}" target="_blank">{r["link"]}</a></div>
        {mirror_html}
    </div>
    """, unsafe_allow_html=True)


# ── UI ──────────────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">📚 PDF Hunter</div>', unsafe_allow_html=True)
st.markdown(
    "<div class=\"hero-sub\">Search across LibGen · Z-Library · Anna's Archive"
    " · Open Library · DuckDuckGo</div>",
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

if submitted and query.strip():
    with st.spinner("Scanning all sources — running concurrently…"):
        raw = cached_search(query.strip())

    direct = [r for r in raw if r["is_direct_pdf"]]
    pages  = [r for r in raw if not r["is_direct_pdf"]]

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill">🎯 {len(raw)} total</div>
        <div class="stat-pill">⬇ {len(direct)} direct PDFs</div>
        <div class="stat-pill">🔗 {len(pages)} page links</div>
    </div>
    """, unsafe_allow_html=True)

    if not raw:
        st.warning("No results found. Try a shorter or differently spelled title.")
    else:
        if direct:
            st.markdown('<div class="section-header">Direct PDF Downloads</div>',
                        unsafe_allow_html=True)
            for i, r in enumerate(direct, 1):
                render_result(r, i)

        if pages:
            st.markdown('<div class="section-header">Page / Metadata Links</div>',
                        unsafe_allow_html=True)
            for i, r in enumerate(pages, 1):
                render_result(r, i)

elif submitted:
    st.warning("Please enter a book name.")

st.markdown("""
<hr style="border-color:rgba(255,255,255,0.06);margin-top:3rem;">
<div style="text-align:center;color:#475569;font-size:0.78rem;padding-bottom:1rem;">
    PDF Hunter — open source &nbsp;·&nbsp; Built by
    <a href="https://github.com/Guettaf-hossam" style="color:#7c3aed;">knight</a>
    &nbsp;·&nbsp; searches public indexes only
</div>
""", unsafe_allow_html=True)
