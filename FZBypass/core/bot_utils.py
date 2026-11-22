from re import search, match, escape
from urllib.parse import urlparse, parse_qs
from wzgram.filters import create
from wzgram.enums import MessageEntityType

from FZBypass import Config
from FZBypass.core.commands import BotCommands
from FZBypass.core.exceptions import DDLException
from FZBypass.core.http_client import get_http_session

BYPASS_CMDS = "|".join(escape(c) for c in BotCommands.BypassCommand)
EXEC_CMDS = "|".join(escape(c) for c in BotCommands.ExecCommands)


async def auth_topic(_, __, message):
    chat_id_msg = message.chat.id if message.chat else None
    if chat_id_msg is None:
        return False
    for chat in Config.AUTH_CHATS:
        try:
            if ":" in chat:
                chat_id, topic_id = chat.split(":", 1)
                if (
                    int(chat_id) == chat_id_msg
                    and getattr(message, "is_topic_message", False)
                    and message.message_thread_id == int(topic_id)
                ):
                    return True
            elif int(chat) == chat_id_msg:
                return True
        except (ValueError, TypeError):
            continue
    return False


AuthChatsTopics = create(auth_topic)


async def auto_bypass(_, c, message):
    txt = message.text or message.caption or ""
    entities = message.entities or message.caption_entities
    if (
        Config.AUTO_BYPASS
        and entities
        and not match(rf"^\/({EXEC_CMDS})($| )", txt)
        and any(
            enty.type in (MessageEntityType.TEXT_LINK, MessageEntityType.URL)
            for enty in entities
        )
    ):
        return True
    me_username = getattr(getattr(c, "me", None), "username", "")
    bot_mention = f"(@{escape(me_username)})?" if me_username else ""
    if (
        not Config.AUTO_BYPASS
        and message.text
        and match(rf"^\/({BYPASS_CMDS}){bot_mention}($| )", message.text)
        and not match(rf"^\/({EXEC_CMDS})($| )", message.text)
    ):
        return True
    return False


BypassFilter = create(auto_bypass)


def get_sender_info(message):
    """Safely extract (user_id, mention_html) even for channel/anonymous posts."""
    if message.from_user:
        return message.from_user.id, message.from_user.mention
    if message.sender_chat:
        title = message.sender_chat.title or "Channel"
        return message.sender_chat.id, f"<b>{title}</b>"
    return 0, "<b>Anonymous</b>"


def get_gdriveid(link: str) -> str:
    if "folders" in link or "file" in link:
        res = search(
            r"https?:\/\/drive\.google\.com\/(?:drive(?:.*?)\/folders\/|file(?:.*?)\/d\/)([-\w]+)",
            link,
        )
        if res:
            return res.group(1)
    parsed = urlparse(link)
    qs = parse_qs(parsed.query)
    if "id" in qs and qs["id"]:
        return qs["id"][0]
    raise DDLException("Invalid Google Drive URL")


async def get_dl(link: str, direct_mode: bool = False) -> str:
    if direct_mode and not Config.DIRECT_INDEX:
        return "No Direct Index Added!"
    gd_id = get_gdriveid(link)
    try:
        session = await get_http_session()
        async with session.get(f"{Config.DIRECT_INDEX}/generate.aspx?id={gd_id}") as resp:
            data = await resp.json(content_type=None)
            if isinstance(data, dict) and data.get("link"):
                return data["link"]
    except Exception:
        pass
    return f"{Config.DIRECT_INDEX}/direct.aspx?id={gd_id}"


def convert_time(seconds: float) -> str:
    mseconds = max(0.0, seconds * 1000)
    periods = [("d", 86400000), ("h", 3600000), ("m", 60000), ("s", 1000), ("ms", 1)]
    result = ""
    for period_name, period_seconds in periods:
        if mseconds >= period_seconds:
            period_value, mseconds = divmod(mseconds, period_seconds)
            result += f"{int(period_value)}{period_name}"
    return result or "0ms"


SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


def get_readable_size(size) -> str:
    if not size:
        return "0B"
    size = float(size)
    i = 0
    while size >= 1024 and i < len(SIZE_UNITS) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f}{SIZE_UNITS[i]}"


def progress_bar(percent, slots=10) -> str:
    percent = min(max(float(percent or 0), 0), 100)
    filled = int(percent / 100 * slots)
    return f"[{'▰' * filled}{'▱' * (slots - filled)}]"
