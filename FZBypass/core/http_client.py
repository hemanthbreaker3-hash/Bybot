from asyncio import Semaphore, to_thread
from functools import partial
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from cloudscraper import create_scraper
from FZBypass import Config

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 14; K) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
)

_session: ClientSession | None = None
_bypass_sem: Semaphore | None = None


def get_bypass_semaphore() -> Semaphore:
    global _bypass_sem
    if _bypass_sem is None:
        _bypass_sem = Semaphore(Config.MAX_CONCURRENT_BYPASS)
    return _bypass_sem


async def get_http_session() -> ClientSession:
    """Return a shared, connection-pooled aiohttp ClientSession."""
    global _session
    if _session is None or _session.closed:
        connector = TCPConnector(
            limit=120,
            limit_per_host=25,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            ssl=False,
        )
        timeout = ClientTimeout(total=Config.BYPASS_TIMEOUT, connect=10)
        _session = ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_UA},
        )
    return _session


async def close_http_session():
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
        _session = None


async def run_sync(func, *args, **kwargs):
    """Run blocking HTTP/scraper calls off the asyncio/uvloop event loop."""
    return await to_thread(partial(func, *args, **kwargs))


def new_scraper(**kwargs):
    return create_scraper(**kwargs)
