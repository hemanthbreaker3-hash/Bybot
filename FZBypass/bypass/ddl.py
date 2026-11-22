from re import findall, compile
from asyncio import sleep as asleep
from urllib.parse import quote, urlparse

from bs4 import BeautifulSoup
from curl_cffi.requests import Session as cSession
from requests import Session

from FZBypass import Config
from FZBypass.core.exceptions import DDLException
from FZBypass.core.http_client import (
    DEFAULT_UA,
    MOBILE_UA,
    get_http_session,
    new_scraper,
    run_sync,
)
from FZBypass.bypass.recaptcha import recaptchaV3


async def get_readable_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h{minutes}m{seconds}s"


async def yandex_disk(url: str) -> str:
    session = await get_http_session()
    try:
        async with session.get(
            f"https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={quote(url, safe='')}"
        ) as resp:
            data = await resp.json(content_type=None)
            if "href" in data:
                return data["href"]
    except Exception as e:
        raise DDLException(f"Yandex Error: {e.__class__.__name__}")
    raise DDLException("File not Found / Download Limit Exceeded")


async def mediafire(url: str) -> str:
    if final_link := findall(
        r"https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+", url
    ):
        return final_link[0]

    def _fetch(target_url: str):
        scraper = new_scraper()
        r1 = scraper.get(target_url, timeout=Config.BYPASS_TIMEOUT)
        if r1.url != target_url:
            r2 = scraper.get(r1.url, timeout=Config.BYPASS_TIMEOUT)
            return r2.text
        return r1.text

    try:
        page = await run_sync(_fetch, url)
    except Exception as e:
        raise DDLException(f"MediaFire Error: {e.__class__.__name__}")

    if final_link := findall(
        r"\'(https?:\/\/download\d+\.mediafire\.com\/\S+\/\S+\/\S+)\'", page
    ):
        return final_link[0]
    if temp_link := findall(
        r'\/\/(www\.mediafire\.com\/file\/\S+\/\S+\/file\?\S+)', page
    ):
        return await mediafire("https://" + temp_link[0].strip('"'))
    raise DDLException("No links found in this page")


async def shrdsk(url: str) -> str:
    def _fetch():
        scraper = new_scraper()
        final_url = scraper.get(url, timeout=Config.BYPASS_TIMEOUT).url
        res = scraper.get(
            f'https://us-central1-affiliate2apk.cloudfunctions.net/get_data?shortid={final_url.rstrip("/").split("/")[-1]}',
            timeout=Config.BYPASS_TIMEOUT,
        )
        return res

    try:
        res = await run_sync(_fetch)
    except Exception as e:
        raise DDLException(f"Shrdsk Error: {e.__class__.__name__}")

    if res.status_code != 200:
        raise DDLException(f"Status Code {res.status_code}")
    data = res.json()
    if "type" in data and data["type"].lower() == "upload" and "video_url" in data:
        return quote(data["video_url"], safe=":/")
    raise DDLException("No Direct Link Found")


async def terabox(url: str) -> str:
    def _fetch():
        sess = Session()
        sess.headers.update({"User-Agent": DEFAULT_UA})

        def retryme(target: str, max_retries: int = 3):
            last_err = None
            for _ in range(max_retries):
                try:
                    return sess.get(target, timeout=Config.BYPASS_TIMEOUT)
                except Exception as err:
                    last_err = err
            raise DDLException(f"Terabox Request Failed: {last_err}")

        first = retryme(url)
        key = first.url.split("?surl=")[-1]
        if Config.TERA_COOKIE:
            sess.cookies.update({"ndus": Config.TERA_COOKIE})

        res = retryme(f"https://www.terabox.com/wap/share/filelist?surl={key}")
        key = res.url.split("?surl=")[-1]
        soup = BeautifulSoup(res.content, "lxml")
        jsToken = None
        for fs in soup.find_all("script"):
            fstring = fs.string
            if fstring and fstring.startswith("try {eval(decodeURIComponent"):
                parts = fstring.split("%22")
                if len(parts) > 1:
                    jsToken = parts[1]
                    break
        if not jsToken:
            raise DDLException("Terabox jsToken not found (check TERA_COOKIE)")

        res = retryme(
            f"https://www.terabox.com/share/list?app_id=250528&jsToken={jsToken}&shorturl={key}&root=1"
        )
        return res.json()

    result = await run_sync(_fetch)
    if result.get("errno") != 0:
        raise DDLException(f"{result.get('errmsg', 'Terabox Error')} — Check TERA_COOKIE")
    items = result.get("list") or []
    if not items:
        raise DDLException("No files found in Terabox link")
    if len(items) > 1:
        raise DDLException("Can't bypass multiple files in one Terabox folder")
    item = items[0]
    if str(item.get("isdir", "0")) != "0":
        raise DDLException("Can't bypass a Terabox folder")
    if dlink := item.get("dlink"):
        return dlink
    raise DDLException("Terabox Link Extraction Failed")


async def try2link(url: str) -> str:
    DOMAIN = "https://try2link.com"
    code = url.rstrip("/").split("/")[-1]
    session = await get_http_session()
    referers = ["https://hightrip.net/", "https://to-travel.net/", "https://world2our.com/"]
    html = ""
    for referer in referers:
        try:
            async with session.get(f"{DOMAIN}/{code}", headers={"Referer": referer}) as res:
                if res.status == 200:
                    html = await res.text()
                    break
        except Exception:
            continue
    if not html:
        raise DDLException("Try2Link page unreachable")
    soup = BeautifulSoup(html, "lxml")
    form = soup.find(id="go-link")
    if not form:
        raise DDLException("Try2Link form not found")
    data = {inp.get("name"): inp.get("value") for inp in form.find_all("input") if inp.get("name")}
    await asleep(6)
    async with session.post(
        f"{DOMAIN}/links/go",
        data=data,
        headers={"X-Requested-With": "XMLHttpRequest"},
    ) as resp:
        if "application/json" in resp.headers.get("Content-Type", ""):
            json_data = await resp.json(content_type=None)
            if isinstance(json_data, dict) and json_data.get("url"):
                return json_data["url"]
    raise DDLException("Try2Link Extraction Failed")


async def gyanilinks(url: str) -> str:
    code = url.rstrip("/").split("/")[-1]
    DOMAIN = "https://go.bloggingaro.com"
    session = await get_http_session()
    async with session.get(
        f"{DOMAIN}/{code}",
        headers={"Referer": "https://tech.hipsonyc.com/", "User-Agent": MOBILE_UA},
    ) as res:
        cookies = res.cookies
        await res.text()
    async with session.get(
        f"{DOMAIN}/{code}",
        headers={"Referer": "https://hipsonyc.com/", "User-Agent": MOBILE_UA},
        cookies=cookies,
    ) as resp:
        html = await resp.text()
    soup = BeautifulSoup(html, "lxml")
    data = {inp.get("name"): inp.get("value") for inp in soup.find_all("input") if inp.get("name")}
    await asleep(5)
    async with session.post(
        f"{DOMAIN}/links/go",
        data=data,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": MOBILE_UA,
            "Referer": f"{DOMAIN}/{code}",
        },
        cookies=cookies,
    ) as links:
        if "application/json" in links.headers.get("Content-Type", ""):
            json_data = await links.json(content_type=None)
            if isinstance(json_data, dict) and json_data.get("url"):
                return json_data["url"]
    raise DDLException("GyaniLinks Extraction Failed")


async def ouo(url: str) -> str:
    tempurl = url.replace("ouo.io", "ouo.press")
    p = urlparse(tempurl)
    uid = tempurl.rstrip("/").split("/")[-1]
    headers = {
        "authority": "ouo.press",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "max-age=0",
        "referer": "http://www.google.com/ig/adde?moduleurl=",
        "upgrade-insecure-requests": "1",
    }

    def _get_initial():
        client = cSession(headers=headers)
        return client, client.get(tempurl, impersonate="chrome110", timeout=Config.BYPASS_TIMEOUT)

    client, res = await run_sync(_get_initial)
    next_url = f"{p.scheme}://{p.hostname}/go/{uid}"

    for _ in range(2):
        if res.headers.get("Location"):
            break
        bs4 = BeautifulSoup(res.content, "lxml")
        if not bs4.form:
            raise DDLException("Ouo form not found")
        inputs = bs4.form.find_all("input", {"name": compile(r"token$")})
        data = {inp.get("name"): inp.get("value") for inp in inputs if inp.get("name")}
        data["x-token"] = await recaptchaV3()

        def _post_step(target_url, payload):
            return client.post(
                target_url,
                data=payload,
                headers={"content-type": "application/x-www-form-urlencoded"},
                allow_redirects=False,
                impersonate="chrome110",
                timeout=Config.BYPASS_TIMEOUT,
            )

        res = await run_sync(_post_step, next_url, data)
        next_url = f"{p.scheme}://{p.hostname}/xreallcygo/{uid}"

    loc = res.headers.get("Location")
    if not loc:
        raise DDLException("Ouo Link Extraction Failed")
    return loc


async def mdisk(url: str) -> str:
    """Deprecated (Preserved)"""
    header = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://mdisk.me/",
        "User-Agent": DEFAULT_UA,
    }
    api_url = f'https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={url.rstrip("/").split("/")[-1]}'
    session = await get_http_session()
    async with session.get(api_url, headers=header) as resp:
        res = await resp.json(content_type=None)
    return res["download"] + "\n\n" + res["source"]


async def transcript(url: str, DOMAIN: str, ref: str, sltime) -> str:
    code = url.rstrip("/").split("/")[-1]
    domain = DOMAIN.rstrip("/")
    session = await get_http_session()
    async with session.get(
        f"{domain}/{code}",
        headers={"Referer": ref, "User-Agent": MOBILE_UA},
    ) as res:
        html = await res.text()
        cookies = res.cookies

    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    if title_tag and title_tag.text.strip() == "Just a moment...":
        raise DDLException("Unable to bypass due to Cloudflare protection")

    data = {
        inp.get("name"): inp.get("value")
        for inp in soup.find_all("input")
        if inp.get("name") and inp.get("value")
    }
    if sltime and sltime > 0:
        await asleep(sltime)

    async with session.post(
        f"{domain}/links/go",
        data=data,
        headers={
            "Referer": f"{domain}/{code}",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": MOBILE_UA,
        },
        cookies=cookies,
    ) as resp:
        if "application/json" in resp.headers.get("Content-Type", ""):
            jdata = await resp.json(content_type=None)
            if isinstance(jdata, dict) and jdata.get("url"):
                return jdata["url"]
    raise DDLException("Link Extraction Failed")


async def justpaste(url: str) -> str:
    session = await get_http_session()
    async with session.get(url) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, "lxml")
    inps = soup.select('div[id="articleContent"] > p')
    lines = [elem.get_text(strip=True) for elem in inps if elem.get_text(strip=True)]
    if not lines:
        raise DDLException("No content found in JustPaste")
    return ", ".join(lines)


async def linksxyz(url: str) -> str:
    session = await get_http_session()
    async with session.get(url) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, "lxml")
    inps = soup.select('div[id="redirect-info"] > a')
    if not inps or not inps[0].get("href"):
        raise DDLException("LinksXYZ Extraction Failed")
    return inps[0]["href"]


async def shareus(url: str) -> str:
    DOMAIN = "https://api.shrslink.xyz"
    code = url.rstrip("/").split("/")[-1]
    headers = {"User-Agent": MOBILE_UA, "Origin": "https://shareus.io"}
    session = await get_http_session()
    async with session.get(f"{DOMAIN}/v?shortid={code}&initial=true&referrer=", headers=headers) as r1:
        sid = (await r1.json(content_type=None)).get("sid")
    if not sid:
        raise DDLException("ShareUS ID Error")
    async with session.get(f"{DOMAIN}/get_link?sid={sid}", headers=headers) as r2:
        data = await r2.json(content_type=None)
        dest = data.get("link_info", {}).get("destination")
        if dest:
            return dest
    raise DDLException("ShareUS Link Extraction Failed")


async def dropbox(url: str) -> str:
    return (
        url.replace("www.", "")
        .replace("dropbox.com", "dl.dropboxusercontent.com")
        .replace("?dl=0", "")
    )


async def linkvertise(url: str) -> str:
    session = await get_http_session()
    async with session.get("https://bypass.pm/bypass2", params={"url": url}) as r:
        resp = await r.json(content_type=None)
    if resp.get("success"):
        return resp["destination"]
    raise DDLException(resp.get("msg", "Linkvertise Bypass Failed"))


async def rslinks(url: str) -> str:
    session = await get_http_session()
    async with session.get(url, allow_redirects=False) as resp:
        loc = resp.headers.get("Location") or resp.headers.get("location")
    if not loc:
        raise DDLException("RSLinks Location Header Missing")
    code = loc.split("ms9")[-1]
    return f"http://techyproio.blogspot.com/p/short.html?{code}=="


async def shorter(url: str) -> str:
    def _fetch():
        scraper = new_scraper()
        return scraper.get(url, allow_redirects=False, timeout=Config.BYPASS_TIMEOUT)

    try:
        resp = await run_sync(_fetch)
        loc = resp.headers.get("Location") or resp.headers.get("location")
        if loc:
            return loc
    except Exception:
        pass
    raise DDLException("Shortener Redirect Extraction Failed")


async def appurl(url: str) -> str:
    def _fetch():
        return new_scraper().get(url, allow_redirects=False, timeout=Config.BYPASS_TIMEOUT)

    resp = await run_sync(_fetch)
    soup = BeautifulSoup(resp.text, "lxml")
    meta = soup.select('meta[property="og:url"]')
    if not meta or not meta[0].get("content"):
        raise DDLException("AppURL Extraction Failed")
    return meta[0]["content"]


async def surl(url: str) -> str:
    def _fetch():
        return new_scraper().get(f"{url}+", timeout=Config.BYPASS_TIMEOUT)

    resp = await run_sync(_fetch)
    soup = BeautifulSoup(resp.text, "lxml")
    long_url = soup.select('p[class="long-url"]')
    if not long_url or not long_url[0].get_text(strip=True):
        raise DDLException("SURL Extraction Failed")
    parts = long_url[0].get_text(strip=True).split()
    if len(parts) < 2:
        raise DDLException("SURL Extraction Failed")
    return parts[1]


async def thinfi(url: str) -> str:
    try:
        session = await get_http_session()
        async with session.get(url) as resp:
            html = await resp.text()
        soup = BeautifulSoup(html, "lxml")
        href = soup.p.a.get("href") if soup.p and soup.p.a else None
        if href:
            return href
    except Exception:
        pass
    raise DDLException("ThinFi Extraction Failed")
