from base64 import b64decode
from asyncio import create_task, gather
from re import findall, DOTALL
from urllib.parse import urlparse
from uuid import uuid4

from bs4 import BeautifulSoup
from lxml import etree
from requests import Session

from FZBypass import LOGGER, Config
from FZBypass.core.bot_utils import get_dl
from FZBypass.core.exceptions import DDLException
from FZBypass.core.http_client import get_http_session, new_scraper, run_sync


async def filepress(url: str) -> str:
    try:
        def _resolve_url():
            return new_scraper().get(url, timeout=Config.BYPASS_TIMEOUT).url

        resolved_url = await run_sync(_resolve_url)
        raw = urlparse(resolved_url)
        sess = await get_http_session()
        json_data = {"id": raw.path.rstrip("/").split("/")[-1]}
        async with sess.post(
            f"{raw.scheme}://{raw.hostname}/api/file/telegram/downlaod/",
            headers={"Referer": f"{raw.scheme}://{raw.hostname}"},
            json=json_data,
        ) as resp:
            tg_id = await resp.json(content_type=None)

        if isinstance(tg_id, dict) and tg_id.get("data"):
            t_url = f"https://tghub.xyz/?start={tg_id['data']}"
            async with sess.get(t_url) as t_resp:
                t_text = await t_resp.text()
            bots = findall(r"filepress_[a-zA-Z0-9]+_bot", t_text)
            if not bots:
                raise DDLException("FilePress Telegram bot not found")
            tg_link = f"https://t.me/{bots[0]}/?start={tg_id['data']}"
        else:
            status_txt = tg_id.get("statusText", "Unavailable") if isinstance(tg_id, dict) else "Unavailable"
            tg_link = "Unavailable" if status_txt == "Ok" else status_txt
    except DDLException:
        raise
    except Exception as e:
        raise DDLException(f"FilePress Error: {e.__class__.__name__}")

    tg_link_text = "Unavailable" if tg_link == "Unavailable" else f'<a href="{tg_link}">Click Here</a>'
    return (
        f'┏ <b>FilePress:</b> <a href="{resolved_url}">Click Here</a>\n'
        f"┗ <b>Telegram:</b> {tg_link_text}"
    )


async def gdtot(url: str) -> str:
    def _fetch():
        scraper = new_scraper()
        resolved = scraper.get(url, timeout=Config.BYPASS_TIMEOUT).url
        p_url = urlparse(resolved)
        res = scraper.post(
            f"{p_url.scheme}://{p_url.hostname}/ddl",
            data={"dl": str(resolved.rstrip("/").split("/")[-1])},
            timeout=Config.BYPASS_TIMEOUT,
        )
        d_link = None
        if (drive_link := findall(r"myDl\('(.*?)'\)", res.text)) and "drive.google.com" in drive_link[0]:
            d_link = drive_link[0]
        elif Config.GDTOT_CRYPT:
            scraper.get(resolved, cookies={"crypt": Config.GDTOT_CRYPT}, timeout=Config.BYPASS_TIMEOUT)
            js_script = scraper.post(
                f"{p_url.scheme}://{p_url.hostname}/dld",
                data={"dwnld": resolved.rstrip("/").split("/")[-1]},
                timeout=Config.BYPASS_TIMEOUT,
            )
            g_id = findall(r"gd=(.*?)&", js_script.text)
            if not g_id:
                raise DDLException("GDToT: File not found or user limit exceeded!")
            decoded_id = b64decode(str(g_id[0])).decode("utf-8")
            d_link = f"https://drive.google.com/open?id={decoded_id}"
        else:
            raise DDLException("Drive Link not found — GDTOT_CRYPT not provided!")

        page_content = scraper.get(resolved, timeout=Config.BYPASS_TIMEOUT).content
        return resolved, d_link, page_content

    resolved, d_link, page_content = await run_sync(_fetch)
    soup = BeautifulSoup(page_content, "lxml")
    meta = soup.select('meta[property^="og:description"]')
    if meta and meta[0].get("content"):
        parse_data = meta[0]["content"].replace("Download ", "").rsplit("-", maxsplit=1)
        name = parse_data[0].strip()
        size = parse_data[-1].strip() if len(parse_data) > 1 else "Unknown"
    else:
        name, size = "Unknown", "Unknown"

    parse_txt = (
        f"┏ <b>Name:</b> <code>{name}</code>\n"
        f"┠ <b>Size:</b> <code>{size}</code>\n"
        f'┠ <b>GDToT:</b> <a href="{resolved}">Click Here</a>\n'
    )
    if Config.DIRECT_INDEX:
        idx_link = await get_dl(d_link)
        parse_txt += f"┠ <b>Temp Index:</b> <a href='{idx_link}'>Click Here</a>\n"
    parse_txt += f"┗ <b>GDrive:</b> <a href='{d_link}'>Click Here</a>"
    return parse_txt


async def drivescript(url: str, crypt: str, dtype: str) -> str:
    def _fetch():
        rs = Session()
        resp = rs.get(url, timeout=Config.BYPASS_TIMEOUT)
        titles = findall(r">(.*?)<\/h4>", resp.text)
        sizes = findall(r">(.*?)<\/td>", resp.text)
        title = titles[0] if titles else "Unknown"
        size = sizes[1] if len(sizes) > 1 else "Unknown"
        p_url = urlparse(url)

        dlink = ""
        js_query = {}
        if dtype != "DriveFire":
            try:
                js_query = rs.post(
                    f"{p_url.scheme}://{p_url.hostname}/ajax.php?ajax=direct-download",
                    data={"id": str(url.rstrip("/").split("/")[-1])},
                    headers={"x-requested-with": "XMLHttpRequest"},
                    timeout=Config.BYPASS_TIMEOUT,
                ).json()
                if str(js_query.get("code")) == "200":
                    dlink = f"{p_url.scheme}://{p_url.hostname}{js_query['file']}"
            except Exception as e:
                LOGGER.error(e)

        if not dlink and crypt:
            rs.get(url, cookies={"crypt": crypt}, timeout=Config.BYPASS_TIMEOUT)
            js_query = rs.post(
                f"{p_url.scheme}://{p_url.hostname}/ajax.php?ajax=download",
                data={"id": str(url.rstrip("/").split("/")[-1])},
                headers={"x-requested-with": "XMLHttpRequest"},
                timeout=Config.BYPASS_TIMEOUT,
            ).json()
            if str(js_query.get("code")) == "200":
                dlink = f"{p_url.scheme}://{p_url.hostname}{js_query['file']}"

        if not dlink:
            if not crypt:
                raise DDLException(f"{dtype} Crypt not provided and Direct Link failed")
            raise DDLException(str(js_query.get("file", f"{dtype} Extraction Failed")))

        res = rs.get(dlink, timeout=Config.BYPASS_TIMEOUT)
        return title, size, res.text

    title, size, res_text = await run_sync(_fetch)
    soup = BeautifulSoup(res_text, "lxml")
    gd_data = soup.select('a[class="btn btn-primary btn-user"]')
    if not gd_data:
        raise DDLException(f"{dtype}: Download buttons not found")

    parse_txt = (
        f"┏ <b>Name:</b> <code>{title}</code>\n"
        f"┠ <b>Size:</b> <code>{size}</code>\n"
        f'┠ <b>{dtype}:</b> <a href="{url}">Click Here</a>'
    )
    if dtype == "HubDrive" and len(gd_data) > 1:
        parse_txt += f'\n┠ <b>Instant:</b> <a href="{gd_data[1]["href"]}">Click Here</a>'
    d_link = gd_data[0]["href"]
    if d_link and Config.DIRECT_INDEX:
        idx_link = await get_dl(d_link)
        parse_txt += f"\n┠ <b>Temp Index:</b> <a href='{idx_link}'>Click Here</a>"
    parse_txt += f"\n┗ <b>GDrive:</b> <a href='{d_link}'>Click Here</a>"
    return parse_txt


async def appflix(url: str) -> str:
    async def appflix_single(single_url: str) -> str:
        def _get_page():
            scraper = new_scraper()
            final_u = scraper.get(single_url, timeout=Config.BYPASS_TIMEOUT).url
            html = scraper.get(final_u, allow_redirects=False, timeout=Config.BYPASS_TIMEOUT).text
            return final_u, html

        resolved_url, html = await run_sync(_get_page)
        soup = BeautifulSoup(html, "lxml")
        ss = soup.select("li[class^='list-group-item']")
        dbot = soup.select("a[href*='drivebot.lol']")
        dbotv2 = dbot[0]["href"] if "gdflix" in resolved_url and dbot else None

        try:
            d_link = await sharer_scraper(resolved_url)
        except Exception as e:
            if not dbotv2:
                raise DDLException(str(e))
            d_link = str(e)

        name_txt = ss[0].get_text(strip=True).split(":", 1)[-1].strip() if len(ss) > 0 else "Unknown"
        size_txt = ss[2].get_text(strip=True).split(":", 1)[-1].strip() if len(ss) > 2 else "Unknown"

        parse_txt = (
            f"┏ <b>Name:</b> <code>{name_txt}</code>\n"
            f"┠ <b>Size:</b> <code>{size_txt}</code>\n"
            f"┠ <b>Source:</b> <code>{resolved_url}</code>"
        )
        if dbotv2:
            parse_txt += f"\n┠ <b>DriveBot V2:</b> <a href='{dbotv2}'>Click Here</a>"
        if d_link and Config.DIRECT_INDEX and "drive.google.com" in d_link:
            idx_link = await get_dl(d_link)
            parse_txt += f"\n┠ <b>Temp Index:</b> <a href='{idx_link}'>Click Here</a>"
        parse_txt += f"\n┗ <b>GDrive:</b> <a href='{d_link}'>Click Here</a>"
        return parse_txt

    if "/pack/" in url:
        def _get_pack():
            scraper = new_scraper()
            final_u = scraper.get(url, timeout=Config.BYPASS_TIMEOUT).url
            content = scraper.get(final_u, timeout=Config.BYPASS_TIMEOUT).content
            return final_u, content

        resolved, content = await run_sync(_get_pack)
        soup = BeautifulSoup(content, "lxml")
        p_url = urlparse(resolved)
        atasks = [
            create_task(appflix_single(f"{p_url.scheme}://{p_url.hostname}" + ss["href"]))
            for ss in soup.select("a[href^='/file/']")
        ]
        completed_tasks = await gather(*atasks, return_exceptions=True)
        body = ""
        for bp_link in completed_tasks:
            if isinstance(bp_link, Exception):
                body += f"\n\n<b>Error:</b> {bp_link}"
            else:
                body += f"\n\n{bp_link}"
        title = soup.title.string if soup.title and soup.title.string else "Pack"
        return f"┏ <b>Name:</b> <code>{title}</code>\n┗ <b>Source:</b> <code>{resolved}</code>{body}"

    return await appflix_single(url)


async def sharerpw(url: str, force: bool = False) -> str:
    if not Config.XSRF_TOKEN and not Config.LARAVEL_SESSION:
        raise DDLException("XSRF_TOKEN or LARAVEL_SESSION not provided!")

    def _fetch():
        scraper = new_scraper(allow_brotli=False)
        resp = scraper.get(
            url,
            cookies={
                "XSRF-TOKEN": Config.XSRF_TOKEN,
                "laravel_session": Config.LARAVEL_SESSION,
            },
            timeout=Config.BYPASS_TIMEOUT,
        )
        parse_txt = findall(r">(.*?)<\/td>", resp.text)
        ddl_btn = etree.HTML(resp.content).xpath("//button[@id='btndirect']")
        tokens = findall(r"_token\s=\s'(.*?)'", resp.text, DOTALL)
        if not tokens:
            raise DDLException("Sharer.pw _token not found (check cookies)")
        data = {"_token": tokens[0]}
        if not force:
            data["nl"] = 1
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }
        res = scraper.post(url + "/dl", headers=headers, data=data, timeout=Config.BYPASS_TIMEOUT).json()
        return parse_txt, ddl_btn, res

    parse_txt, ddl_btn, res = await run_sync(_fetch)
    name = parse_txt[2] if len(parse_txt) > 2 else "Unknown"
    size = parse_txt[8] if len(parse_txt) > 8 else "Unknown"
    added = parse_txt[11] if len(parse_txt) > 11 else "Unknown"

    parse_data = (
        f"┏ <b>Name:</b> <code>{name}</code>\n"
        f"┠ <b>Size:</b> <code>{size}</code>\n"
        f"┠ <b>Added On:</b> <code>{added}</code>\n"
    )
    if res.get("status") == 0:
        if Config.DIRECT_INDEX:
            idx_link = await get_dl(res["url"])
            parse_data += f"\n┠ <b>Temp Index:</b> <a href='{idx_link}'>Click Here</a>"
        return parse_data + f"\n┗ <b>GDrive:</b> <a href='{res['url']}'>Click Here</a>"
    if res.get("status") == 2:
        msg = res.get("message", "Unknown error").replace("<br/>", "\n")
        return parse_data + f"\n┗ <b>Error:</b> {msg}"
    if len(ddl_btn) and not force:
        return await sharerpw(url, force=True)
    raise DDLException("Sharer.pw Extraction Failed")


async def sharer_scraper(url: str) -> str:
    def _fetch():
        scraper = new_scraper()
        resolved = scraper.get(url, timeout=Config.BYPASS_TIMEOUT).url
        raw = urlparse(resolved)
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        res = scraper.get(resolved, headers={"User-Agent": ua}, timeout=Config.BYPASS_TIMEOUT)
        key = findall(r'"key",\s+"(.*?)"', res.text)
        if not key:
            raise DDLException("Download Link Key not found!")
        if not etree.HTML(res.content).xpath("//button[@id='drc']"):
            raise DDLException("Link doesn't have direct download button")
        boundary = uuid4()
        headers = {
            "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
            "x-token": raw.hostname,
            "User-Agent": ua,
        }
        data = (
            f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n'
            f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key[0]}\r\n'
            f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n'
            f"------WebKitFormBoundary{boundary}--\r\n"
        )
        post_res = scraper.post(
            resolved, cookies=res.cookies, headers=headers, data=data, timeout=Config.BYPASS_TIMEOUT
        ).json()
        if "url" not in post_res:
            raise DDLException("Drive Link not found, Try in your browser")
        if "drive.google.com" in post_res["url"]:
            return post_res["url"]
        final_res = scraper.get(post_res["url"], timeout=Config.BYPASS_TIMEOUT)
        drive_link = etree.HTML(final_res.content).xpath("//a[contains(@class,'btn')]/@href")
        if drive_link and "drive.google.com" in drive_link[0]:
            return drive_link[0]
        raise DDLException("Drive Link not found, Try in your browser")

    return await run_sync(_fetch)
