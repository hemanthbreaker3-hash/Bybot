from os import environ, getenv, path as ospath
from time import time
from logging import getLogger, StreamHandler, INFO, ERROR, basicConfig
from logging.handlers import RotatingFileHandler

try:
    from uvloop import install
    install()
except ImportError:
    pass

from wzgram import Client
from wzgram.enums import ParseMode

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=20 * 1024 * 1024, backupCount=5, encoding="utf-8"),
        StreamHandler(),
    ],
    level=INFO,
)

getLogger("pyrogram").setLevel(ERROR)
getLogger("aiohttp").setLevel(ERROR)
LOGGER = getLogger(__name__)


def _load_shell_env_files():
    """Load .env or env.sh without overriding already-exported shell variables."""
    for fname in (".env", "env.sh"):
        if not ospath.isfile(fname):
            continue
        try:
            with open(fname, encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("export "):
                        line = line[7:].strip()
                    if "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    # Strip inline comments if unquoted
                    if val and val[0] not in ('"', "'") and " #" in val:
                        val = val.split(" #", 1)[0].strip()
                    if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                        val = val[1:-1]
                    if key:
                        environ.setdefault(key, val)
        except Exception as e:
            LOGGER.warning(f"Failed loading {fname}: {e}")


_load_shell_env_files()

try:
    import config
except ImportError:
    config = None


def conf(key: str, default=""):
    """Read config with strict priority: Shell Export > .env/env.sh > config.py > default."""
    env_val = getenv(key)
    if env_val is not None and env_val != "":
        return env_val
    cfg_val = getattr(config, key, None) if config else None
    if cfg_val is not None and cfg_val != "":
        return cfg_val
    return default


def _conf_int(key: str, default: int = 0) -> int:
    val = conf(key, default)
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _conf_bool(key: str, default: bool = False) -> bool:
    val = conf(key, default)
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "on")


BOT_START = time()
BOT_NAME = "AloneKing Star"


class Config:
    BOT_TOKEN = str(conf("BOT_TOKEN", "")).strip()
    API_HASH = str(conf("API_HASH", "")).strip()
    API_ID = _conf_int("API_ID", 0)
    OWNER_ID = _conf_int("OWNER_ID", 0)

    if not BOT_TOKEN or not API_HASH or not API_ID or not OWNER_ID:
        LOGGER.critical(
            "Required credentials missing (BOT_TOKEN, API_ID, API_HASH, OWNER_ID). "
            "Export them in shell or set them in env.sh / config.py. Exiting..."
        )
        raise SystemExit(1)

    CMD_SUFFIX = str(conf("CMD_SUFFIX", "") or "").strip()
    AUTO_BYPASS = _conf_bool("AUTO_BYPASS", False)

    _auth = conf("AUTH_CHATS", "")
    if isinstance(_auth, str):
        AUTH_CHATS = [c.strip() for c in _auth.split() if c.strip()]
    else:
        AUTH_CHATS = [str(c).strip() for c in _auth if str(c).strip()]

    DIRECT_INDEX = str(conf("DIRECT_INDEX", "") or "").strip().rstrip("/")
    LARAVEL_SESSION = str(conf("LARAVEL_SESSION", "") or "").strip()
    XSRF_TOKEN = str(conf("XSRF_TOKEN", "") or "").strip()
    GDTOT_CRYPT = str(conf("GDTOT_CRYPT", "") or "").strip()
    DRIVEFIRE_CRYPT = str(conf("DRIVEFIRE_CRYPT", "") or "").strip()
    HUBDRIVE_CRYPT = str(conf("HUBDRIVE_CRYPT", "") or "").strip()
    KATDRIVE_CRYPT = str(conf("KATDRIVE_CRYPT", "") or "").strip()
    TERA_COOKIE = str(conf("TERA_COOKIE", "") or "").strip()

    PORT = _conf_int("PORT", 8080)
    WORKERS = max(4, _conf_int("WORKERS", 16))
    BYPASS_TIMEOUT = max(5, _conf_int("BYPASS_TIMEOUT", 25))
    MAX_CONCURRENT_BYPASS = max(1, _conf_int("MAX_CONCURRENT_BYPASS", 25))
    MAX_LOOP_HOPS = max(1, _conf_int("MAX_LOOP_HOPS", 10))
    AUTO_UPDATE = _conf_bool("AUTO_UPDATE", False)


Bypass = Client(
    "AloneKingStar",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    workers=Config.WORKERS,
    plugins=dict(root="FZBypass/handlers"),
    parse_mode=ParseMode.HTML,
)
