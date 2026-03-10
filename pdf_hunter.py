from __future__ import annotations

import io
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

# Fix Windows cp1252 terminal only when running as CLI — Streamlit manages its own I/O
if hasattr(sys.stdout, "buffer") and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 12  # seconds — safe for slow connections
INTER_REQUEST_DELAY = 0.5


@dataclass
class BookResult:
    """Represents a single search hit from any source."""
    title: str
    link: str
    source: str
    is_direct_pdf: bool = False
    mirror: Optional[str] = None

    def display(self, index: int) -> None:
        tag = "[PDF]" if self.is_direct_pdf else "[PAGE]"
        print(f"  {index:>2}. {tag} [{self.source}] {self.title}")
        print(f"      {self.link}")
        if self.mirror:
            print(f"      [MIRROR] {self.mirror}")


def _slugify(text: str) -> str:
    """Convert book name to a safe filename slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "_", text)[:60]


def search_duckduckgo(book_name: str, max_results: int = 10) -> list[BookResult]:
    """
    Multi-dork DuckDuckGo search.
    Also covers Z-Library and Anna's Archive via site: dorks —
    both sites render results with JavaScript so direct scraping returns empty HTML.
    DuckDuckGo indexes their cached static pages, making this the only reliable method.
    """
    dorks = [
        (f'"{book_name}" filetype:pdf',                            "DuckDuckGo"),
        (f'"{book_name}" site:archive.org',                        "DuckDuckGo"),
        (f'"{book_name}" pdf download',                            "DuckDuckGo"),
        (f'"{book_name}" site:z-lib.fm OR site:z-lib.id',         "Z-Library"),
        (f'"{book_name}" site:annas-archive.gs OR site:annas-archive.org', "Anna's Archive"),
    ]

    results: list[BookResult] = []
    seen: set[str] = set()

    for dork, source_label in dorks:
        try:
            with DDGS() as ddgs:
                hits = ddgs.text(dork, max_results=max_results) or []
                for r in hits:
                    link = r.get("href", "")
                    if not link or link in seen:
                        continue
                    seen.add(link)
                    is_pdf = link.lower().endswith(".pdf")
                    results.append(BookResult(
                        title=r.get("title", "Unknown"),
                        link=link,
                        source=source_label,
                        is_direct_pdf=is_pdf,
                    ))
                time.sleep(INTER_REQUEST_DELAY)
        except Exception as exc:
            print(f"  [DDG] Error on dork '{dork}': {exc}")

    return results



def search_libgen(book_name: str) -> list[BookResult]:
    """
    Query Library Genesis JSON API directly.
    libgen.is/json.php returns structured metadata including direct MD5-based
    download links — the most reliable source for direct PDF retrieval.
    """
    # Try multiple mirrors — libgen rotates domains frequently
    # Each entry is (base_url, search_path_format)
    mirrors = [
        ("https://libgen.is",  "/search.php"),
        ("https://libgen.st",  "/search.php"),
        ("https://libgen.rs",  "/search.php"),
        ("https://libgen.li",  "/index.php"),
    ]

    search_url: Optional[str] = None
    search_path: str = "/search.php"
    for mirror_base, mirror_path in mirrors:
        try:
            probe = requests.get(mirror_base, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if probe.status_code == 200:
                search_url = mirror_base
                search_path = mirror_path
                break
        except Exception:
            continue

    if not search_url:
        print("  [LibGen] All mirrors unreachable.")
        return []

    results: list[BookResult] = []

    # Step 1: search endpoint returns list of IDs
    try:
        search_resp = requests.get(
            f"{search_url}{search_path}",
            params={"req": book_name, "res": 25, "view": "simple", "phrase": 1, "column": "def"},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        search_resp.raise_for_status()
    except Exception as exc:
        print(f"  [LibGen] Search failed: {exc}")
        return []

    soup = BeautifulSoup(search_resp.text, "lxml")

    # The results table has id="searchresults" or is the 3rd table on the page
    table = soup.find("table", {"id": "searchresults"})
    if not table:
        # Fallback: grab any table with more than 2 rows
        tables = soup.find_all("table")
        table = next((t for t in tables if len(t.find_all("tr")) > 2), None)

    if not table:
        print("  [LibGen] No results table found.")
        return []

    rows = table.find_all("tr")[1:]  # skip header row
    for row in rows[:15]:
        cells = row.find_all("td")
        if len(cells) < 9:
            continue

        # Column layout: ID | Author | Title | Publisher | Year | Pages | Lang | Size | Ext | ...
        title   = cells[2].get_text(strip=True)
        ext     = cells[8].get_text(strip=True).lower() if len(cells) > 8 else ""
        lang    = cells[6].get_text(strip=True) if len(cells) > 6 else ""

        # Extract the MD5 link from the title cell
        link_tag = cells[2].find("a", href=True)
        if not link_tag:
            continue

        detail_href = link_tag["href"]
        if not detail_href.startswith("http"):
            detail_href = f"{search_url}/{detail_href.lstrip('/')}"

        is_pdf = ext == "pdf"
        results.append(BookResult(
            title=f"{title} [{lang}] [{ext.upper()}]" if ext else title,
            link=detail_href,
            source="LibGen",
            is_direct_pdf=is_pdf,
            mirror=f"{search_url}/get.php?md5=" + (detail_href.split("md5=")[-1] if "md5=" in detail_href else ""),
        ))

    return results


def search_annas_archive(book_name: str) -> list[BookResult]:
    """
    Scrape Anna's Archive — the largest shadow library aggregator.
    Indexes LibGen, Z-Lib, Sci-Hub, and more under one search.
    Uses a cloudscraper session to handle Cloudflare protection.
    """
    try:
        import cloudscraper
        session = cloudscraper.create_scraper()
    except Exception:
        session = requests.Session()

    # Anna's Archive rotates domains to evade DNS blocks
    # Order based on live connectivity test — .gs confirmed reachable
    aa_mirrors = [
        "https://annas-archive.gs",
        "https://annas-archive.se",
        "https://annas-archive.li",
        "https://annas-archive.org",
    ]

    resp = None
    base = ""
    for mirror in aa_mirrors:
        try:
            r = session.get(
                f"{mirror}/search",
                params={"q": book_name, "ext": "pdf"},
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            if r.status_code == 200:
                resp = r
                base = mirror
                break
        except Exception:
            continue

    if resp is None:
        print("  [Anna's] All mirrors unreachable.")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results: list[BookResult] = []

    # Each result is a div with a link to /md5/<hash>
    for item in soup.select("a[href^='/md5/']")[:15]:
        href = item.get("href", "")
        if not href:
            continue

        # Grab the closest text block as title
        title_el = item.select_one("h3") or item.select_one(".text-xs") or item
        title = title_el.get_text(separator=" ", strip=True)[:120]

        full_link = f"{base}{href}"
        results.append(BookResult(
            title=title or "Unknown",
            link=full_link,
            source="Anna's Archive",
            is_direct_pdf=False,  # link goes to metadata page, not direct .pdf
        ))

    return results


def search_open_library(book_name: str) -> list[BookResult]:
    """
    Query the Open Library JSON API — free, no key, maintained by Internet Archive.
    Returns works that have readable/downloadable editions on archive.org.
    """
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": book_name, "limit": 10, "fields": "title,author_name,key,ia,lending_edition_s"},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"  [OpenLibrary] Request failed: {exc}")
        return []

    results: list[BookResult] = []

    for doc in data.get("docs", []):
        title   = doc.get("title", "Unknown")
        authors = ", ".join(doc.get("author_name", [])[:2])
        ia_ids  = doc.get("ia", [])

        if not ia_ids:
            # No Internet Archive copy — skip
            continue

        # Prefer the lending_edition if available, else take first IA ID
        ia_id = doc.get("lending_edition_s") or ia_ids[0]
        link  = f"https://archive.org/details/{ia_id}"
        # Try to build a direct PDF link — works for many IA items
        pdf_link = f"https://archive.org/download/{ia_id}/{ia_id}.pdf"

        results.append(BookResult(
            title=f"{title} — {authors}" if authors else title,
            link=pdf_link,
            source="Open Library / IA",
            is_direct_pdf=True,
            mirror=link,
        ))

    return results


def search_zlibrary(book_name: str) -> list[BookResult]:
    """
    Search Z-Library via its open static mirrors.
    Z-Library is the largest book shadow library (11M+ books).
    These mirrors expose a searchable HTML interface without login.
    """
    # z-lib.fm confirmed reachable — it uses /s/<query> for search
    # z-lib.id is down, 1lib.sk returns 503
    mirrors = [
        ("https://z-lib.fm",  "/s/"),
        ("https://1lib.sk",   "/s/"),
    ]

    resp = None
    base = ""
    for mirror_url, search_path in mirrors:
        try:
            r = requests.get(
                f"{mirror_url}{search_path}{requests.utils.quote(book_name)}",
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if r.status_code == 200 and len(r.text) > 1000:
                resp = r
                base = mirror_url
                break
        except Exception:
            continue

    if resp is None:
        print("  [Z-Library] All mirrors unreachable.")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    results: list[BookResult] = []

    # Primary: links whose path contains /book/ — stable Z-Library URL pattern
    # [:15] slices the RESULTS LIST, not the CSS selector string
    book_links = soup.select("a[href*='/book/']")[:15]

    # Fallback if primary returns nothing — Z-Lib occasionally restructures layout
    if not book_links:
        book_links = soup.select(".z-bookItem a, .resItemBox a, h3 a")[:15]

    for a in book_links:
        href  = a.get("href", "")
        title = a.get_text(separator=" ", strip=True)[:120]

        if not href or not title or len(title) < 4:
            continue

        if href.startswith("http"):
            full = href
        elif href.startswith("/"):
            full = f"{base}{href}"
        else:
            full = f"{base}/{href}"

        results.append(BookResult(
            title=title,
            link=full,
            source="Z-Library",
            is_direct_pdf=False,
        ))

    seen: set[str] = set()
    unique = []
    for r in results:
        if r.link not in seen:
            seen.add(r.link)
            unique.append(r)

    return unique



def hunt_for_pdf(book_name: str, max_results: int = 10, save_output: bool = True) -> None:
    """
    Orchestrator: runs all 4 sources concurrently (max 2 threads to stay CPU-safe),
    deduplicates by URL, and prints a ranked output table.
    """
    print(f"\n[*] TARGET : {book_name}")
    print(f"[*] SOURCES: DuckDuckGo | LibGen | Anna's Archive | Open Library | Z-Library")
    print("-" * 70)

    sources = {
        "DuckDuckGo":  lambda: search_duckduckgo(book_name, max_results),
        "LibGen":      lambda: search_libgen(book_name),
        "Anna's":      lambda: search_annas_archive(book_name),
        "OpenLibrary": lambda: search_open_library(book_name),
        "ZLibrary":    lambda: search_zlibrary(book_name),
    }

    all_results: list[BookResult] = []
    seen_links: set[str] = set()

    # max_workers=2 — safe for dual-core Pentium B960, avoids 100% CPU spike
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(fn): name for name, fn in sources.items()}
        for future in as_completed(futures):
            source_name = futures[future]
            try:
                hits = future.result()
                print(f"  [{source_name}] {len(hits)} hits found.")
                for r in hits:
                    if r.link not in seen_links:
                        seen_links.add(r.link)
                        all_results.append(r)
            except Exception as exc:
                print(f"  [{source_name}] FAILED: {exc}")

    # Rank: direct PDFs first, then by source priority
    source_rank = {"LibGen": 0, "Z-Library": 1, "Open Library / IA": 2, "Anna's Archive": 3, "DuckDuckGo": 4}
    all_results.sort(key=lambda r: (not r.is_direct_pdf, source_rank.get(r.source, 9)))

    print("\n" + "=" * 70)
    print(f"  SCAN COMPLETE — {len(all_results)} unique results")
    print("=" * 70)

    if not all_results:
        print("  No results found across all sources.")
        return

    direct = [r for r in all_results if r.is_direct_pdf]
    pages  = [r for r in all_results if not r.is_direct_pdf]

    if direct:
        print(f"\n  DIRECT PDF LINKS ({len(direct)}):\n")
        for i, r in enumerate(direct, 1):
            r.display(i)

    if pages:
        print(f"\n  PAGE / METADATA LINKS ({len(pages)}):\n")
        for i, r in enumerate(pages, 1):
            r.display(i)

    # Save to file for later reference
    if save_output:
        slug = _slugify(book_name)
        output_file = f"results_{slug}.txt"
        # utf-8-sig adds BOM so Windows Notepad/Explorer displays French chars correctly
        with open(output_file, "w", encoding="utf-8-sig") as f:
            f.write(f"Search: {book_name}\n")
            f.write("=" * 65 + "\n\n")
            f.write(f"DIRECT PDFs ({len(direct)}):\n")
            for r in direct:
                f.write(f"  [{r.source}] {r.title}\n  {r.link}\n")
                if r.mirror:
                    f.write(f"  [MIRROR] {r.mirror}\n")
                f.write("\n")
            f.write(f"\nPAGE LINKS ({len(pages)}):\n")
            for r in pages:
                f.write(f"  [{r.source}] {r.title}\n  {r.link}\n\n")
        print(f"\n  [*] Results saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = " ".join(sys.argv[1:])
    else:
        target = input("Enter book name: ").strip()

    if not target:
        print("[-] No input. Exiting.")
        sys.exit(1)

    hunt_for_pdf(target)