from __future__ import annotations

import asyncio
import io
import re
import sys
import unicodedata
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

import aiohttp

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
    ),
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=12)


@dataclass
class BookResult:
    title: str
    link: str
    source: str
    is_direct_pdf: bool = False
    mirror: Optional[str] = None
    doc_type: str = "General PDF"   # "Book" | "Academic" | "General PDF"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "is_direct_pdf": self.is_direct_pdf,
            "mirror": self.mirror,
            "doc_type": self.doc_type,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BookResult":
        return cls(
            title=d["title"],
            link=d["link"],
            source=d["source"],
            is_direct_pdf=d.get("is_direct_pdf", False),
            mirror=d.get("mirror"),
            doc_type=d.get("doc_type", "General PDF"),
        )


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)[:60]


async def _find_fastest_mirror(
    session: aiohttp.ClientSession,
    mirrors: list[tuple[str, str]],
    params: dict,
) -> Optional[tuple[str, str]]:
    """
    Race all mirrors simultaneously — first valid response wins, rest are cancelled.
    This eliminates the sequential per-mirror timeout waterfall (up to 3x faster).
    """
    async def probe(base: str, path: str) -> tuple[str, str]:
        async with session.get(
            f"{base}{path}", params=params, timeout=REQUEST_TIMEOUT
        ) as resp:
            if resp.status != 200:
                raise aiohttp.ClientResponseError(
                    resp.request_info, resp.history, status=resp.status
                )
            text = await resp.text()
            if len(text) < 800:
                raise aiohttp.ClientError("Response too short — likely a block or redirect page")
            return (base, text)

    tasks = {asyncio.create_task(probe(base, path)): base for base, path in mirrors}
    winner: Optional[tuple[str, str]] = None
    pending = set(tasks.keys())

    while pending and winner is None:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            try:
                winner = task.result()
                break
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                print(f"  [mirror] {tasks[task]} failed ({type(exc).__name__})")

    for task in pending:
        task.cancel()

    return winner


async def search_duckduckgo(book_name: str, max_results: int = 10) -> list[BookResult]:
    """
    Runs 8 OSINT dorks concurrently (4 workers) to cover the full search surface:
    books, shadow libraries, academic documents (cours/TD/TP), and open web PDFs.
    Each dork runs in its own thread via ThreadPoolExecutor so DDGS blocking I/O
    does not stall the others — total latency ~= slowest single dork, not sum.
    """
    # (dork_query, source_label, doc_type)
    dorks: list[tuple[str, str, str]] = [
        # Open web / general
        (f'"{book_name}" filetype:pdf',                                           "DuckDuckGo",     "General PDF"),
        (f'"{book_name}" site:archive.org',                                       "DuckDuckGo",     "General PDF"),
        (f'"{book_name}" pdf download',                                           "DuckDuckGo",     "General PDF"),
        # Shadow libraries (indexed via DDG)
        (f'"{book_name}" site:z-lib.fm OR site:z-lib.id',                        "Z-Library",      "Book"),
        (f'"{book_name}" site:annas-archive.gs OR site:annas-archive.org',        "Anna's Archive", "Book"),
        # Academic OSINT
        (f'(cours OR TD OR TP OR syllabus) "{book_name}" filetype:pdf',           "DuckDuckGo",     "Academic"),
        (f'"{book_name}" site:academia.edu OR site:researchgate.net',             "DuckDuckGo",     "Academic"),
        (f'"{book_name}" site:slideshare.net OR site:scribd.com filetype:pdf',    "DuckDuckGo",     "Academic"),
    ]

    def _search_one(dork: str, label: str, dtype: str) -> list[BookResult]:
        """Single DDG dork — runs in its own thread."""
        batch: list[BookResult] = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(dork, max_results=max_results) or []:
                    link = r.get("href", "")
                    if not link:
                        continue
                    batch.append(BookResult(
                        title=r.get("title", "Unknown"),
                        link=link,
                        source=label,
                        is_direct_pdf=link.lower().endswith(".pdf"),
                        doc_type=dtype,
                    ))
        except Exception as exc:
            print(f"  [DDG] dork failed ({type(exc).__name__}): {dork[:60]}")
        return batch

    def _sync_parallel() -> list[BookResult]:
        results: list[BookResult] = []
        seen: set[str] = set()
        # max_workers=4: 4 dorks in flight simultaneously — balanced DDG pressure
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(_search_one, dork, label, dtype): dork
                for dork, label, dtype in dorks
            }
            for future in as_completed(futures):
                for r in future.result():
                    if r.link not in seen:
                        seen.add(r.link)
                        results.append(r)
        return results

    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, _sync_parallel)
    print(f"  [DuckDuckGo] {len(results)} hits found ({len(dorks)} dorks, 4 workers).")
    return results


async def search_libgen(session: aiohttp.ClientSession, book_name: str) -> list[BookResult]:
    """
    Race all 4 LibGen mirrors — first to respond is used for the full query.
    Parses the HTML results table directly (more stable than the JSON ID pipeline).
    """
    mirrors = [
        ("https://libgen.is", "/search.php"),
        ("https://libgen.st", "/search.php"),
        ("https://libgen.rs", "/search.php"),
        ("https://libgen.li", "/index.php"),
    ]
    params = {"req": book_name, "res": "25", "view": "simple", "column": "def"}

    result = await _find_fastest_mirror(session, mirrors, params)
    if result is None:
        print("  [LibGen] All mirrors unreachable.")
        return []

    base, html = result
    soup = BeautifulSoup(html, "html.parser")
    results: list[BookResult] = []

    for row in soup.select("table.c > tbody > tr, #tablelibgen > tbody > tr")[1:16]:
        cells = row.find_all("td")
        if len(cells) < 9:
            continue
        title_link = cells[2].find("a", id=True) or cells[2].find("a")
        if not title_link:
            continue
        title = title_link.get_text(strip=True)[:120]
        href  = title_link.get("href", "")
        ext   = cells[8].get_text(strip=True).lower() if len(cells) > 8 else ""
        if not href or not title:
            continue
        full = href if href.startswith("http") else f"{base}{href}"
        results.append(BookResult(
            title=title, link=full, source="LibGen",
            is_direct_pdf=(ext == "pdf"), doc_type="Book"
        ))

    print(f"  [LibGen] {len(results)} hits found via {base}.")
    return results


async def search_annas_archive(book_name: str) -> list[BookResult]:
    """Launches headless Chromium via nodriver to solve the Cloudflare JS
    challenge natively with Premium Proxy Integration."""
    try:
        import nodriver as uc
    except ImportError:
        print("  [Anna's] nodriver not installed — skipping.")
        return []

    base = "https://annas-archive.gl"
    browser = None

    import os
    from dotenv import load_dotenv
    load_dotenv()

    PROXY_HOST = os.getenv("PROXY_HOST")
    PROXY_PORT = int(os.getenv("PROXY_PORT", "1080")) if os.getenv("PROXY_PORT") else 1080
    PROXY_USER = os.getenv("PROXY_USER")
    PROXY_PASS = os.getenv("PROXY_PASS")
    
    import socket
    import base64
    
    # Tiny async local HTTP proxy that injects AnyIP credentials
    async def proxy_relay_handler(reader, writer):
        try:
            remote_reader, remote_writer = await asyncio.open_connection(PROXY_HOST, PROXY_PORT)
            auth = base64.b64encode(f"{PROXY_USER}:{PROXY_PASS}".encode()).decode()
            
            async def forward(src, dst, inject_auth=False):
                try:
                    while True:
                        data = await src.read(8192)
                        if not data: break
                        if inject_auth:
                            # Inject Proxy-Authorization for HTTP CONNECT or plain GET
                            lines = data.split(b"\r\n")
                            if len(lines) > 0 and (lines[0].startswith(b"CONNECT") or lines[0].startswith(b"GET") or lines[0].startswith(b"POST")):
                                data = data.replace(b"\r\n\r\n", f"\r\nProxy-Authorization: Basic {auth}\r\n\r\n".encode(), 1)
                            inject_auth = False
                        dst.write(data)
                        await dst.drain()
                except:
                    pass
                finally:
                    dst.close()
            
            asyncio.create_task(forward(reader, remote_writer, inject_auth=True))
            asyncio.create_task(forward(remote_reader, writer))
        except Exception as e:
            writer.close()

    # Find a free local port
    s = socket.socket()
    s.bind(('', 0))
    local_proxy_port = s.getsockname()[1]
    s.close()

    relay_server = await asyncio.start_server(proxy_relay_handler, '127.0.0.1', local_proxy_port)
    local_proxy = f"http://127.0.0.1:{local_proxy_port}"

    try:
        browser = await uc.start(
            headless=False,
            browser_args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-background-networking",
                "--disable-sync",
                "--disable-translate",
                "--metrics-recording-only",
                "--no-first-run",
                "--js-flags=--max-old-space-size=128",
                "--ignore-certificate-errors",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--window-size=1920,1080",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                f"--proxy-server={local_proxy}",
            ],
        )

        page = await browser.get("about:blank")

        # IP identity probe to verify the proxy extension is working
        ip_page = await browser.get("https://api.ipify.org")
        await asyncio.sleep(2)
        ip_html = await ip_page.get_content()
        import re as _re
        ip_match = _re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", ip_html)
        ip_result = ip_match.group(1) if ip_match else f"(raw: {ip_html[:80]})"
        print(f"\n  [DEBUG] IP seen by the website: {ip_result}\n")

        # 5. الخدعة الأكبر: الذهاب للصفحة الرئيسية أولاً للحصول على ملفات تعريف الارتباط (Cookies)
        await page.get(f"{base}/")
        print("  [Anna's] Warming up connection and solving JS challenge...")
        await asyncio.sleep(8) # انتظار أطول قليلاً ليحل التحدي

        # 6. ثم الانتقال لصفحة البحث المطلوبة
        encoded = urllib.parse.quote(book_name)
        await page.get(f"{base}/search?q={encoded}&ext=pdf")
        await asyncio.sleep(5)

        # Cloudflare JS challenge can take longer for some residential IPs
        for _ in range(25):
            title = await page.evaluate("document.title")
            if title and "Just a moment" not in title and "Verify" not in title and "Attention" not in title:
                break
            await asyncio.sleep(1)
            
        await asyncio.sleep(3) # Give DOM time to fully render after CF redirect
        html_content = await page.get_content()
        final_title = await page.evaluate("document.title")
        print(f"  [DEBUG] Final Title: {final_title}")
        
        with open("debug_anna.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        if len(html_content) <= 500:
            print(f"  [Anna's] Challenge page persisted (body={len(html_content)} bytes)")
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        results: list[BookResult] = []

        for item in soup.select("a[href^='/md5/']")[:15]:
            href = item.get("href", "")
            if not href:
                continue
            title_el = item.select_one("h3") or item.select_one(".text-xs") or item
            title    = title_el.get_text(separator=" ", strip=True)[:120]
            results.append(BookResult(
                title=title or "Unknown",
                link=f"{base}{href}",
                source="Anna's Archive",
                is_direct_pdf=False,
                doc_type="Book",
            ))

        print(f"  [Anna's] {len(results)} hits found via {base}.")
        return results

    except Exception as exc:
        print(f"  [Anna's] nodriver error ({type(exc).__name__}): {exc}")
        return []
    finally:
        if browser is not None:
            try:
                browser.stop()
            except Exception:
                pass


async def search_open_library(session: aiohttp.ClientSession, book_name: str) -> list[BookResult]:
    """
    Internet Archive Open Library JSON API — free, no key, high uptime.
    Only returns entries that have a confirmed full-text IA identifier.
    """
    params = {
        "q": book_name,
        "fields": "key,title,author_name,ia,has_fulltext",
        "limit": "10",
    }
    try:
        async with session.get(
            "https://openlibrary.org/search.json",
            params=params,
            timeout=REQUEST_TIMEOUT,
        ) as resp:
            if resp.status != 200:
                raise aiohttp.ClientResponseError(
                    resp.request_info, resp.history, status=resp.status
                )
            data = await resp.json(content_type=None)
    except aiohttp.ClientResponseError as exc:
        print(f"  [OpenLibrary] HTTP {exc.status}")
        return []
    except asyncio.TimeoutError:
        print("  [OpenLibrary] Timed out")
        return []
    except aiohttp.ClientError as exc:
        print(f"  [OpenLibrary] Connection error ({type(exc).__name__})")
        return []

    results: list[BookResult] = []
    for doc in data.get("docs", []):
        ia_ids = doc.get("ia", [])
        if not ia_ids or not doc.get("has_fulltext"):
            continue
        ia_id = ia_ids[0]
        title = doc.get("title", "Unknown")[:120]
        results.append(BookResult(
            title=title,
            link=f"https://archive.org/download/{ia_id}/{ia_id}.pdf",
            source="Open Library / IA",
            is_direct_pdf=True,
            mirror=f"https://archive.org/details/{ia_id}",
            doc_type="Book",
        ))

    print(f"  [OpenLibrary] {len(results)} hits found.")
    return results


async def search_zlibrary(session: aiohttp.ClientSession, book_name: str) -> list[BookResult]:
    """
    Z-Library direct scrape — z-lib.fm confirmed reachable.
    Note: site renders many results via JS — this catches any static-HTML results
    that are present. The DuckDuckGo site: dork in search_duckduckgo() is the
    primary channel for Z-Library discovery.
    """
    encoded = urllib.parse.quote(book_name)
    try:
        async with session.get(
            f"https://z-lib.fm/s/{encoded}",
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        ) as resp:
            if resp.status != 200:
                raise aiohttp.ClientResponseError(
                    resp.request_info, resp.history, status=resp.status
                )
            html = await resp.text()
    except aiohttp.ClientResponseError as exc:
        print(f"  [ZLibrary] HTTP {exc.status}")
        return []
    except asyncio.TimeoutError:
        print("  [ZLibrary] Timed out")
        return []
    except aiohttp.ClientError as exc:
        print(f"  [ZLibrary] Connection error ({type(exc).__name__})")
        return []

    soup       = BeautifulSoup(html, "html.parser")
    book_links = soup.select("a[href*='/book/']")[:15]
    if not book_links:
        book_links = soup.select(".z-bookItem a, .resItemBox a, h3 a")[:15]

    results: list[BookResult] = []
    seen: set[str] = set()

    for a in book_links:
        href  = a.get("href", "")
        title = a.get_text(separator=" ", strip=True)[:120]
        if not href or not title or len(title) < 4:
            continue
        full = href if href.startswith("http") else f"https://z-lib.fm{href}"
        if full not in seen:
            seen.add(full)
            results.append(BookResult(
                title=title, link=full, source="Z-Library",
                is_direct_pdf=False, doc_type="Book"
            ))

    print(f"  [ZLibrary] {len(results)} hits found.")
    return results


async def hunt_for_pdf_async(book_name: str) -> list[BookResult]:
    """
    Async orchestrator — all 5 sources run concurrently via asyncio.gather().
    return_exceptions=True ensures a single module failure does not abort others.
    """
    print(f"\n[*] TARGET : {book_name}")
    print("[*] SOURCES: DuckDuckGo | LibGen | Anna's Archive | Open Library | Z-Library")
    print("-" * 70)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        raw = await asyncio.gather(
            search_duckduckgo(book_name),
            search_libgen(session, book_name),
            search_annas_archive(book_name),
            search_open_library(session, book_name),
            search_zlibrary(session, book_name),
            return_exceptions=True,
        )

    all_results: list[BookResult] = []
    seen: set[str] = set()

    for batch in raw:
        if isinstance(batch, Exception):
            print(f"  [!] Module error ({type(batch).__name__}): {batch}")
            continue
        for r in batch:
            if r.link not in seen:
                seen.add(r.link)
                all_results.append(r)

    source_rank = {
        "LibGen": 0, "Z-Library": 1,
        "Open Library / IA": 2, "Anna's Archive": 3, "DuckDuckGo": 4,
    }
    all_results.sort(key=lambda r: (not r.is_direct_pdf, source_rank.get(r.source, 9)))
    return all_results


def hunt_for_pdf(book_name: str, save_output: bool = True) -> None:
    """CLI sync entry point — wraps the async orchestrator with asyncio.run()."""
    results = asyncio.run(hunt_for_pdf_async(book_name))
    direct  = [r for r in results if r.is_direct_pdf]
    pages   = [r for r in results if not r.is_direct_pdf]

    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {len(results)} total | {len(direct)} direct PDFs | {len(pages)} page links")
    print(f"{'=' * 70}\n")

    for i, r in enumerate(results, 1):
        kind = "PDF " if r.is_direct_pdf else "PAGE"
        print(f"  {i:>2}. [{kind}] [{r.source}] {r.title}")
        print(f"      {r.link}")
        if r.mirror:
            print(f"      [MIRROR] {r.mirror}")

    if save_output and results:
        slug        = _slugify(book_name)
        output_file = f"results_{slug}.txt"
        with open(output_file, "w", encoding="utf-8-sig") as f:
            f.write(f"Search: {book_name}\n{'=' * 65}\n\n")
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
    import sys as _sys
    import warnings
    warnings.filterwarnings("ignore", message=".*I/O operation on closed pipe.*")
    target = " ".join(_sys.argv[1:]) if len(_sys.argv) > 1 else input("Enter book name: ").strip()
    if not target:
        print("[-] No input. Exiting.")
        _sys.exit(1)
    hunt_for_pdf(target)