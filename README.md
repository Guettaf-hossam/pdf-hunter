# PDF Hunter

A multi-source PDF book search engine with a web interface.

> **⚠️ DISCLAIMER - CYBERSECURITY ACADEMIC RESEARCH ONLY**
> *This project was developed strictly as an academic research tool to study structural vulnerabilities and DRM mechanisms within PDF formats. It is intended for authorized security testing and ethical scraping compliance research. The author assumes no liability for misuse. Do NOT use this tool to bypass intellectual property protections or violate any platform's Terms of Service.*

Search across **LibGen · Z-Library · Anna's Archive · Open Library · DuckDuckGo** simultaneously.

## Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pdf-hunter.streamlit.app)

## Sources

| Source | Notes |
|---|---|
| Library Genesis | Direct `.pdf` links via HTML scrape — 4 auto-failover mirrors |
| Anna's Archive | Largest shadow library aggregator — indexed via DuckDuckGo |
| Z-Library | 11M+ books — indexed via DuckDuckGo site: dork |
| Open Library | Free Internet Archive API — no key needed |
| DuckDuckGo | 5 targeted dork patterns |

## Run Locally

```bash
git clone https://github.com/Guettaf-hossam/pdf-hunter
cd pdf-hunter
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Web interface
streamlit run app.py

# CLI
python pdf_hunter.py "Book Title Author Name"
```

## Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** to `app.py`
5. Click Deploy — your app is live at `https://pdf-hunter.streamlit.app`

No domain purchase needed.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE). This means anyone can copy and modify the code, but they **must** open-source their changes and they cannot use it in proprietary/closed-source commercial projects.
