from asyncio import gather, create_task
from re import search, match, sub
from urllib.parse import urlparse
from bs4 import BeautifulSoup, NavigableString, Tag

from FZBypass import Config
from FZBypass.bypass.ddl import transcript
from FZBypass.core.exceptions import DDLException
from FZBypass.core.http_client import get_http_session, new_scraper, run_sync


async def sharespark(url: str) -> str:
    def _fetch():
        scraper = new_scraper()
        res = scraper.get("?action=printpage;".join(url.split("?")), timeout=Config.BYPASS_TIMEOUT)
        soup = BeautifulSoup(res.text, "lxml")
        gd_txt = ""
        for br in soup.find_all("br"):
            next_s = br.next_sibling
            if not (next_s and isinstance(next_s, NavigableString)):
                continue
            next2_s = next_s.next_sibling
            if (
                next2_s
                and isinstance(next2_s, Tag)
                and next2_s.name == "br"
                and str(next_s).strip()
            ):
                if match(r"^(480p|720p|1080p)(.+)? Links:\Z", next_s):
                    gd_txt += f'<b>{next_s.replace("Links:", "GDToT Links :")}</b>\n\n'
                for s in next_s.split():
                    ns = sub(r"\(|\)", "", s)
                    if match(r"https?://.+\.gdtot\.\S+", ns):
                        gsoup = BeautifulSoup(
                            scraper.get(ns, timeout=Config.BYPASS_TIMEOUT).text, "lxml"
                        )
                        meta = gsoup.select('meta[property^="og:description"]')
                        if meta and meta[0].get("content"):
                            parse_data = (
                                meta[0]["content"]
                                .replace("Download ", "")
                                .rsplit("-", maxsplit=1)
                            )
                            gd_txt += (
                                f"┎ <b>Name :</b> {parse_data[0]}\n"
                                f"┠ <b>Size :</b> {parse_data[-1]}\n"
                                f"┖ <b>GDToT :</b> {ns}\n\n"
                            )
                    elif match(r"https?://pastetot\.\S+", ns):
                        nxt = sub(r"\(|\)|(https?://pastetot\.\S+)", "", next_s)
                        gd_txt += f"\n<b>{nxt}</b>\n┖ {ns}\n"
            if len(gd_txt) > 3800:
                return gd_txt
        return gd_txt

    gd_txt = await run_sync(_fetch)
    if not gd_txt:
        raise DDLException("No ShareSpark links found")
    return gd_txt


async def skymovieshd(url: str) -> str:
    session = await get_http_session()
    async with session.get(url, allow_redirects=False) as resp:
        html = await resp.text()
    soup = BeautifulSoup(html, "lxml")
    t = soup.select('div[class^="Robiul"]')
    header = t[-1].get_text(strip=True).replace("Download ", "") if t else "SkyMoviesHD"
    gd_txt = f"<i>{header}</i>"
    _cache = set()
    for link in soup.select('a[href*="howblogs.xyz"]'):
        href = link.get("href")
        if not href or href in _cache:
            continue
        _cache.add(href)
        gd_txt += f"\n\n<b>{link.get_text(strip=True)} :</b>\n"
        async with session.get(href, allow_redirects=False) as nresp:
            nsoup = BeautifulSoup(await nresp.text(), "lxml")
        for no, a in enumerate(nsoup.select('div[class="cotent-box"] > a[href]'), start=1):
            gd_txt += f"{no}. {a['href']}\n"
    return gd_txt


async def cinevood(url: str) -> str:
    session = await get_http_session()
    async with session.get(url) as resp:
        html = await resp.text()
    soup = BeautifulSoup(html, "lxml")
    titles = soup.select("h6")
    links_by_title = {}
    post_title = soup.title.string.strip() if soup.title and soup.title.string else "CineVood"

    host_tags = [
        ("gdtot", "GDToT"),
        ("multiup", "MultiUp"),
        ("filepress", "FilePress"),
        ("gdflix", "GDFlix"),
        ("kolop", "Kolop"),
        ("zipylink", "ZipyLink"),
    ]

    for title in titles:
        title_text = title.get_text(strip=True)
        links = []
        for key, label in host_tags:
            tag = title.find_next("a", href=lambda h, k=key: h and k in h.lower())
            if tag and tag.get("href"):
                links.append(f'<a href="{tag["href"]}"><b>{label}</b></a>')
        if links:
            links_by_title[title_text] = links

    prsd = f"<b>🔖 Title:</b> {post_title}\n"
    for title, links in links_by_title.items():
        prsd += f"\n┏ <b>🏷️ Name:</b> <code>{title}</code>\n"
        prsd += "┗ <b>🔗 Links:</b> " + " | ".join(links) + "\n"
    return prsd


async def kayoanime(url: str) -> str:
    session = await get_http_session()
    async with session.get(url) as resp:
        html = await resp.text()
    soup = BeautifulSoup(html, "lxml")
    gdlinks = soup.select('a[href*="drive.google.com"], a[href*="tinyurl"]')
    title = soup.title.string.strip() if soup.title and soup.title.string else "KayoAnime"
    prsd = f"<b>{title}</b>"
    for n, gd in enumerate(gdlinks, start=1):
        link = gd.get("href", "")
        gd_txt = "GDrive"
        if "tinyurl" in link:
            try:
                async with session.get(link) as r:
                    link = str(r.url)
                domain = (urlparse(link).hostname or "").lower()
                gd_txt = (
                    "Mega"
                    if "mega" in domain
                    else "G Group"
                    if "groups" in domain
                    else "Direct Link"
                )
            except Exception:
                pass
        label = gd.get_text(strip=True) or f"Link {n}"
        prsd += f"\n\n{n}. <i><b>{label}</b></i>\n┗ <b>Links :</b> <a href='{link}'><b>{gd_txt}</b></a>"
    return prsd


async def toonworld4all(url: str) -> str:
    session = await get_http_session()
    if "/redirect/main.php?url=" in url:
        async with session.get(url) as r:
            return f"┎ <b>Source Link:</b> {url}\n┃\n┖ <b>Bypass Link:</b> {r.url}"
    async with session.get(url) as resp:
        xml = await resp.text()
    soup = BeautifulSoup(xml, "lxml")
    if "/episode/" not in url:
        epl = soup.select('a[href*="/episode/"]')
        tls = soup.select('div[class*="mks_accordion_heading"]')
        m = search(r'"name":"(.+?)"', xml)
        stitle = m.group(1) if m else "ToonWorld4All"
        prsd = f"<b><i>{stitle}</i></b>"
        for n, (t, l) in enumerate(zip(tls, epl), start=1):
            t_text = t.strong.get_text(strip=True) if t.strong else t.get_text(strip=True)
            prsd += f'\n\n{n}. <i><b>{t_text}</b></i>\n┖ <b>Link :</b> {l["href"]}'
        return prsd

    links = soup.select('a[href*="/redirect/main.php?url="]')
    titles = soup.select("h5")
    if not titles or not links:
        raise DDLException("No episode links found")
    prsd = f"<b><i>{titles[0].get_text(strip=True)}</i></b>"
    titles.pop(0)
    if not titles:
        return prsd
    slicer = max(1, len(links) // len(titles))
    atasks = []
    for sl in links:
        nsl = sl.get("href", "")
        for _ in range(5):
            if any(x in nsl for x in ("rocklinks", "link1s")):
                break
            async with session.get(nsl, allow_redirects=False) as r:
                loc = r.headers.get("Location") or r.headers.get("location")
                if not loc:
                    break
                nsl = loc
        if "rocklinks" in nsl:
            atasks.append(
                create_task(
                    transcript(
                        nsl,
                        "https://insurance.techymedies.com/",
                        "https://highkeyfinance.com/",
                        5,
                    )
                )
            )
        elif "link1s" in nsl:
            atasks.append(
                create_task(
                    transcript(nsl, "https://link1s.com", "https://anhdep24.com/", 9)
                )
            )

    com_tasks = await gather(*atasks, return_exceptions=True)
    lstd = [com_tasks[i : i + slicer] for i in range(0, len(com_tasks), slicer)]

    for no, tl in enumerate(titles):
        if no >= len(lstd):
            break
        prsd += f"\n\n<b>{tl.get_text(strip=True)}</b>\n┃\n┖ <b>Links :</b> "
        row_items = []
        for l_tag, sl in zip(links, lstd[no]):
            if isinstance(sl, Exception):
                row_items.append(str(sl))
            else:
                row_items.append(f"<a href='{sl}'>{l_tag.get_text(strip=True)}</a>")
        prsd += ", ".join(row_items)
    return prsd


async def tamilmv(url: str) -> str:
    def _fetch():
        return new_scraper().get(url, timeout=Config.BYPASS_TIMEOUT).text

    html = await run_sync(_fetch)
    soup = BeautifulSoup(html, "lxml")
    mag = soup.select('a[href^="magnet:?xt=urn:btih:"]')
    tor = soup.select('a[data-fileext="torrent"]')
    title = soup.title.string.strip() if soup.title and soup.title.string else "1TamilMV"
    parse_data = f"<b><u>{title}</u></b>"
    for no, (t, m) in enumerate(zip(tor, mag), start=1):
        raw_name = t.get_text(strip=True) or f"Torrent {no}"
        filename = sub(r"www\S+|\- |\.torrent", "", raw_name).strip()
        parse_data += (
            f"\n\n{no}. <code>{filename}</code>\n"
            f'┖ <b>Links :</b> <a href="https://t.me/share/url?url={m["href"].split("&")[0]}"><b>Magnet 🧲</b></a> | '
            f'<a href="{t["href"]}"><b>Torrent 🌐</b></a>'
        )
    return parse_data
