from re import match
from urllib.parse import urlparse

from FZBypass import Config
from FZBypass.bypass.dlinks import (
    appflix,
    drivescript,
    filepress,
    gdtot,
    sharer_scraper,
    sharerpw,
)
from FZBypass.bypass.ddl import (
    appurl,
    dropbox,
    gyanilinks,
    justpaste,
    linksxyz,
    linkvertise,
    mediafire,
    ouo,
    rslinks,
    shareus,
    shorter,
    shrdsk,
    surl,
    terabox,
    thinfi,
    transcript,
    try2link,
    yandex_disk,
)
from FZBypass.bypass.scrape import (
    cinevood,
    kayoanime,
    sharespark,
    skymovieshd,
    tamilmv,
    toonworld4all,
)
from FZBypass.core.bot_utils import get_dl
from FZBypass.core.exceptions import DDLException
from FZBypass.core.http_client import get_bypass_semaphore

fmed_list = [
    "fembed.net",
    "fembed.com",
    "femax20.com",
    "fcdn.stream",
    "feurl.com",
    "layarkacaxxi.icu",
    "naniplay.nanime.in",
    "naniplay.nanime.biz",
    "naniplay.com",
    "mm9842.com",
]


def is_share_link(url: str) -> bool:
    return bool(
        match(
            r"https?:\/\/.+\.(gdtot|filepress|pressbee|gdflix)\.\S+|https?:\/\/(gdflix|filepress|pressbee|onlystream|filebee|appdrive)\.\S+",
            url,
        )
    )


def is_excep_link(url: str) -> bool:
    return bool(
        match(
            r"https?:\/\/.+\.(1tamilmv|gdtot|filepress|pressbee|gdflix|sharespark)\.\S+|https?:\/\/(sharer|onlystream|hubdrive|katdrive|drivefire|skymovieshd|toonworld4all|kayoanime|cinevood|gdflix|filepress|pressbee|filebee|appdrive)\.\S+",
            url,
        )
    )


async def _bypass_single(link: str) -> str:
    domain = (urlparse(link).hostname or "").lower()

    # File Hoster Links
    if match(r"https?:\/\/(yadi|disk\.yandex)\.\S+", link):
        return await yandex_disk(link)
    if match(r"https?:\/\/.+\.mediafire\.\S+", link):
        return await mediafire(link)
    if match(r"https?:\/\/shrdsk\.\S+", link):
        return await shrdsk(link)
    if any(
        x in domain
        for x in (
            "1024tera",
            "terabox",
            "nephobox",
            "4funbox",
            "mirrobox",
            "momerybox",
            "teraboxapp",
        )
    ):
        return await terabox(link)
    if "drive.google.com" in domain:
        return await get_dl(link, True)

    # DDL / Shortener Links
    if match(r"https?:\/\/try2link\.\S+", link):
        return await try2link(link)
    if match(r"https?:\/\/(gyanilinks|gtlinks)\.\S+", link):
        return await gyanilinks(link)
    if match(r"https?:\/\/adrinolinks\.\S+", link):
        return await transcript(link, "https://adrinolinks.in", "https://bhojpuritop.in/", 8)
    if match(r"https?:\/\/adsfly\.\S+", link):
        return await transcript(link, "https://go.adsfly.in/", "https://letest25.co/", 3)
    if match(r"https?:\/\/(.+\.)?anlinks\.\S+", link):
        return await transcript(link, "https://anlinks.in/", "https://dsblogs.fun/", 8)
    if match(r"https?:\/\/ronylink\.\S+", link):
        return await transcript(link, "https://go.ronylink.com/", "https://livejankari.com/", 3)
    if match(r"https?:\/\/.+\.evolinks\.\S+", link):
        return await transcript(link, "https://ads.evolinks.in/", link, 3)
    if match(r"https?:\/\/.+\.tnshort\.\S+", link):
        return await transcript(link, "https://news.sagenews.in/", "https://movies.djnonstopmusic.in/", 5)
    if match(r"https?:\/\/(xpshort|push\.bdnewsx|techymozo)\.\S+", link):
        return await transcript(link, "https://xpshort.com/", "https://www.comptegratuite.com/", 4.9)
    if match(r"https?:\/\/go\.lolshort\.\S+", link):
        return await transcript(link, "https://get.lolshort.tech/", "https://tech.animezia.com/", 8)
    if match(r"https?:\/\/onepagelink\.\S+", link):
        return await transcript(link, "https://go.onepagelink.in/", "https://gorating.in/", 3.1)
    if match(r"https?:\/\/earn\.moneykamalo\.\S+", link):
        return await transcript(link, "https://go.moneykamalo.com/", "https://bloging.techkeshri.com/", 4)
    if match(r"https?:\/\/droplink\.\S+", link):
        return await transcript(link, "https://droplink.co/", "https://yoshare.net/", 3.1)
    if match(r"https?:\/\/tinyfy\.\S+", link):
        return await transcript(link, "https://tinyfy.in", "https://www.yotrickslog.tech/", 0)
    if match(r"https?:\/\/krownlinks\.\S+", link):
        return await transcript(link, "https://go.hostadviser.net/", "https://blog.hostadviser.net/", 8)
    if match(r"https?:\/\/(du-link|dulink)\.\S+", link):
        return await transcript(link, "https://du-link.in", "https://profitshort.com/", 0)
    if match(r"https?:\/\/indianshortner\.\S+", link):
        return await transcript(link, "https://indianshortner.com/", "https://moddingzone.in/", 5)
    if match(r"https?:\/\/m\.easysky\.\S+", link):
        return await transcript(link, "https://techy.veganab.co/", "https://camdigest.com/", 5)
    if match(r"https?:\/\/(.+\.)?linkbnao\.\S+", link):
        return await transcript(link, "https://vip.linkbnao.com", "https://ffworld.xyz/", 2)
    if match(r"https?:\/\/.+\.tnlink\.\S+", link):
        return await transcript(link, "https://news.sagenews.in/", "https://knowstuff.in/", 5)
    if match(r"https?:\/\/link4earn\.\S+", link):
        return await transcript(link, "https://link4earn.com", "https://studyis.xyz/", 6)
    if match(r"https?:\/\/shortingly\.\S+", link):
        return await transcript(link, "https://go.blogytube.com/", "https://blogytube.com/", 5)
    if match(r"https?:\/\/short2url\.\S+", link):
        return await transcript(link, "https://techyuth.xyz/blog", "https://blog.coin2pay.xyz/", 10)
    if match(r"https?:\/\/urlsopen\.\S+", link):
        return await transcript(link, "https://s.humanssurvival.com/", "https://1topjob.xyz/", 5)
    if match(r"https?:\/\/mdisk\.\S+", link):
        return await transcript(link, "https://mdisk.pro", "https://www.meclipstudy.in/", 5)
    if match(r"https?:\/\/(pkin|go\.paisakamalo)\.\S+", link):
        return await transcript(link, "https://go.paisakamalo.in", "https://healthtips.techkeshri.com/", 5)
    if match(r"https?:\/\/linkpays\.\S+", link):
        return await transcript(link, "https://tech.smallinfo.in/Gadget/", "https://finance.filmypoints.in/", 6)
    if match(r"https?:\/\/sklinks\.\S+", link):
        return await transcript(link, "https://sklinks.in", "https://dailynew.online/", 5)
    if match(r"https?:\/\/link1s\.\S+", link):
        return await transcript(link, "https://link1s.com", "https://anhdep24.com/", 9)
    if match(r"https?:\/\/tulinks\.\S+", link):
        return await transcript(link, "https://tulinks.one", "https://www.blogger.com/", 8)
    if match(r"https?:\/\/.+\.tulinks\.\S+", link):
        return await transcript(link, "https://go.tulinks.online", "https://tutelugu.co/", 8)
    if match(r"https?:\/\/(.+\.)?vipurl\.\S+", link):
        return await transcript(link, "https://count.vipurl.in/", "https://kiss6kartu.in/", 5)
    if match(r"https?:\/\/indyshare\.\S+", link):
        return await transcript(link, "https://indyshare.net", "https://insurancewolrd.in/", 3.1)
    if match(r"https?:\/\/linkyearn\.\S+", link):
        return await transcript(link, "https://linkyearn.com", "https://gktech.uk/", 5)
    if match(r"https?:\/\/earn4link\.\S+", link):
        return await transcript(link, "https://m.open2get.in/", "https://ezeviral.com/", 8)
    if match(r"https?:\/\/linksly\.\S+", link):
        return await transcript(link, "https://go.linksly.co/", "https://en.themezon.net/", 5)
    if match(r"https?:\/\/(.+\.)?mdiskshortner\.\S+", link):
        return await transcript(link, "https://mdiskshortner.link", "https://yosite.net/", 0)
    if match(r"https?:\/\/(?:\w+\.)?rocklinks\.\S+", link):
        return await transcript(link, "https://land.povathemes.com/", "https://blog.disheye.com/", 4.9)
    if match(r"https?:\/\/mplaylink\.\S+", link):
        return await transcript(link, "https://tera-box.cloud/", "https://mvplaylink.in.net/", 5)
    if match(r"https?:\/\/shrinke\.\S+", link):
        return await transcript(link, "https://en.shrinke.me/", "https://themezon.net/", 15)
    if match(r"https?:\/\/urlspay\.\S+", link):
        return await transcript(link, "https://finance.smallinfo.in/", "https://tech.filmypoints.in/", 5)
    if match(r"https?:\/\/.+\.tnvalue\.\S+", link):
        return await transcript(link, "https://page.finclub.in/", "https://finclub.in/", 8)
    if match(r"https?:\/\/sxslink\.\S+", link):
        return await transcript(link, "https://getlink.sxslink.com/", "https://cinemapettai.in/", 5)
    if match(r"https?:\/\/moneycase\.\S+", link):
        return await transcript(link, "https://last.moneycase.link/", "https://www.infokeeda.xyz/", 3.1)
    if match(r"https?:\/\/urllinkshort\.\S+", link):
        return await transcript(link, "https://web.urllinkshort.in", "https://suntechu.in/", 5)
    if match(r"https?:\/\/.+\.dtglinks\.\S+", link):
        return await transcript(link, "https://happyfiles.dtglinks.in/", "https://tech.filohappy.in/", 5)
    if match(r"https?:\/\/v2links\.\S+", link):
        return await transcript(link, "https://vzu.us/", "https://newsbawa.com/", 5)
    if match(r"https?:\/\/v2\.kpslink\.\S+", link):
        return await transcript(link, "https://v2.kpslink.in/", "https://infotamizhan.xyz/", 5)
    if match(r"https?:\/\/(.+\.)?kpslink\.\S+", link):
        return await transcript(link, "https://kpslink.in/", "https://infotamizhan.xyz/", 3.1)
    if match(r"https?:\/\/tamizhmasters\.\S+", link):
        return await transcript(link, "https://tamizhmasters.com/", "https://pokgames.com/", 5)
    if match(r"https?:\/\/tglink\.\S+", link):
        return await transcript(link, "https://tglink.in/", "https://www.proappapk.com/", 5)
    if match(r"https?:\/\/pandaznetwork\.\S+", link):
        return await transcript(link, "https://pandaznetwork.com/", "https://panda.freemodsapp.xyz/", 5)
    if match(r"https?:\/\/url4earn\.\S+", link):
        return await transcript(link, "https://go.url4earn.in/", "https://techminde.com/", 8)
    if match(r"https?:\/\/ez4short\.\S+", link):
        return await transcript(link, "https://ez4short.com/", "https://ez4mods.com/", 5)
    if match(r"https?:\/\/dalink\.\S+", link):
        return await transcript(link, "https://get.tamilhit.tech/MR-X/tamil/", "https://www.tamilhit.tech/", 8)
    if match(r"https?:\/\/.+\.omnifly\.\S+", link):
        return await transcript(link, "https://f.omnifly.in.net/", "https://ignitesmm.com/", 5)
    if match(r"https?:\/\/sheralinks\.\S+", link):
        return await transcript(link, "https://sheralinks.com/", "https://blogyindia.com/", 0.8)
    if match(r"https?:\/\/bindaaslinks\.\S+", link):
        return await transcript(link, "https://appsinsta.com/blog", "https://pracagov.com/", 3)
    if match(r"https?:\/\/viplinks\.\S+", link):
        return await transcript(link, "https://m.vip-link.net/", "https://m.leadcricket.com/", 5)
    if match(r"https?:\/\/.+\.short2url\.\S+", link):
        return await transcript(link, "https://techyuth.xyz/blog/", "https://blog.mphealth.online/", 10)
    if match(r"https?:\/\/shrinkforearn\.\S+", link):
        return await transcript(link, "https://shrinkforearn.in/", "https://wp.uploadfiles.in/", 8)
    if match(r"https?:\/\/bringlifes\.\S+", link):
        return await transcript(link, "https://bringlifes.com/", "https://loanoffering.in/", 5)
    if match(r"https?:\/\/.+\.linkfly\.\S+", link):
        return await transcript(link, "https://insurance.yosite.net/", "https://yosite.net/", 10)
    if match(r"https?:\/\/.+\.earn2me\.\S+", link):
        return await transcript(link, "https://blog.filepresident.com/", "https://easyworldbusiness.com/", 5)
    if match(r"https?:\/\/.+\.vplinks\.\S+", link):
        return await transcript(link, "https://vplink.in", "https://insurance.findgptprompts.com/", 5)
    if match(r"https?:\/\/.+\.narzolinks\.\S+", link):
        return await transcript(link, "https://go.narzolinks.click/", "https://hydtech.in/", 5)
    if match(r"https?:\/\/earn2short\.\S+", link):
        return await transcript(link, "https://go.earn2short.in/", "https://tech.insuranceinfos.in/", 0.8)
    if match(r"https?:\/\/instantearn\.\S+", link):
        return await transcript(link, "https://get.instantearn.in/", "https://love.petrainer.in/", 5)
    if match(r"https?:\/\/linkjust\.\S+", link):
        return await transcript(link, "https://linkjust.com/", "https://forexrw7.com/", 3.1)
    if match(r"https?:\/\/pdiskshortener\.\S+", link):
        return await transcript(link, "https://pdiskshortener.com/", "", 10)
    if match(r"https?:\/\/publicearn\.\S+", link):
        return await transcript(link, "https://publicearn.com/", "https://careersides.com/", 4.9)
    if match(r"https?:\/\/modijiurl\.\S+", link):
        return await transcript(link, "https://modijiurl.com/", "https://loanoffering.in/", 8)
    if match(r"https?:\/\/linkshortx\.\S+", link):
        return await transcript(link, "https://linkshortx.in/", "https://nanotech.org.in/", 4.9)
    if match(r"https?:\/\/.+\.shorito\.\S+", link):
        return await transcript(link, "https://go.shorito.com/", "https://healthgo.gorating.in/", 8)
    if match(r"https?:\/\/pdisk\.\S+", link):
        return await transcript(link, "https://last.moneycase.link/", "https://www.webzeni.com/", 4.9)
    if match(r"https?:\/\/ziplinker\.\S+", link):
        return await transcript(link, "https://ziplinker.net", "https://fintech.techweeky.com/", 1)
    if match(r"https?:\/\/ouo\.\S+", link):
        return await ouo(link)
    if match(r"https?:\/\/(shareus|shrs)\.\S+", link):
        return await shareus(link)
    if match(r"https?:\/\/(.+\.)?dropbox\.\S+", link):
        return await dropbox(link)
    if match(r"https?:\/\/linkvertise\.\S+", link):
        return await linkvertise(link)
    if match(r"https?:\/\/rslinks\.\S+", link):
        return await rslinks(link)
    if match(r"https?:\/\/(bit|tinyurl|(.+\.)?short|shorturl|t)\.\S+", link):
        return await shorter(link)
    if match(r"https?:\/\/appurl\.\S+", link):
        return await appurl(link)
    if match(r"https?:\/\/surl\.\S+", link):
        return await surl(link)
    if match(r"https?:\/\/thinfi\.\S+", link):
        return await thinfi(link)
    if match(r"https?:\/\/justpaste\.\S+", link):
        return await justpaste(link)
    if match(r"https?:\/\/linksxyz\.\S+", link):
        return await linksxyz(link)

    # Scraper Sites
    if match(r"https?:\/\/cinevood\.\S+", link):
        return await cinevood(link)
    if match(r"https?:\/\/kayoanime\.\S+", link):
        return await kayoanime(link)
    if match(r"https?:\/\/toonworld4all\.\S+", link):
        return await toonworld4all(link)
    if match(r"https?:\/\/skymovieshd\.\S+", link):
        return await skymovieshd(link)
    if match(r"https?:\/\/.+\.sharespark\.\S+", link):
        return await sharespark(link)
    if match(r"https?:\/\/.+\.1tamilmv\.\S+", link):
        return await tamilmv(link)

    # GDrive / Sharer Sites
    if match(r"https?:\/\/hubdrive\.\S+", link):
        return await drivescript(link, Config.HUBDRIVE_CRYPT, "HubDrive")
    if match(r"https?:\/\/katdrive\.\S+", link):
        return await drivescript(link, Config.KATDRIVE_CRYPT, "KatDrive")
    if match(r"https?:\/\/drivefire\.\S+", link):
        return await drivescript(link, Config.DRIVEFIRE_CRYPT, "DriveFire")
    if match(r"https?:\/\/sharer\.\S+", link):
        return await sharerpw(link)
    if is_share_link(link):
        if "gdtot" in domain:
            return await gdtot(link)
        if "filepress" in domain or "pressbee" in domain:
            return await filepress(link)
        if "appdrive" in domain or "gdflix" in domain:
            return await appflix(link)
        return await sharer_scraper(link)

    # Exceptions
    if match(r"https?:\/\/.+\.technicalatg\.\S+", link):
        raise DDLException("Bypass Not Allowed!")
    raise DDLException(f"No Bypass Function Found for: {link}")


_DIRECT_RETURN_PATTERNS = (
    r"https?:\/\/(yadi|disk\.yandex)\.\S+",
    r"https?:\/\/.+\.mediafire\.\S+",
    r"https?:\/\/shrdsk\.\S+",
    r"https?:\/\/cinevood\.\S+",
    r"https?:\/\/kayoanime\.\S+",
    r"https?:\/\/toonworld4all\.\S+",
    r"https?:\/\/skymovieshd\.\S+",
    r"https?:\/\/.+\.sharespark\.\S+",
    r"https?:\/\/.+\.1tamilmv\.\S+",
    r"https?:\/\/hubdrive\.\S+",
    r"https?:\/\/katdrive\.\S+",
    r"https?:\/\/drivefire\.\S+",
    r"https?:\/\/sharer\.\S+",
)


def _is_terminal(link: str) -> bool:
    domain = (urlparse(link).hostname or "").lower()
    if "drive.google.com" in domain or is_share_link(link):
        return True
    if any(x in domain for x in ("1024tera", "terabox", "nephobox", "4funbox", "mirrobox", "momerybox", "teraboxapp")):
        return True
    return any(match(p, link) for p in _DIRECT_RETURN_PATTERNS)


async def direct_link_checker(link: str, onlylink: bool = False):
    async with get_bypass_semaphore():
        blink = await _bypass_single(link)
        if onlylink or _is_terminal(link):
            return blink

        links = []
        seen = {link}
        for _ in range(Config.MAX_LOOP_HOPS):
            links.append(blink)
            if not isinstance(blink, str) or blink in seen:
                break
            seen.add(blink)
            try:
                next_link = await _bypass_single(blink)
                if is_excep_link(links[-1]):
                    links.append("\n\n" + str(next_link))
                    break
                blink = next_link
            except Exception:
                break
        return links
