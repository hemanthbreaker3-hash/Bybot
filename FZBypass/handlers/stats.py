from asyncio import to_thread
from platform import python_version
from time import time

from psutil import (
    Process,
    cpu_count,
    cpu_percent,
    disk_usage,
    swap_memory,
    virtual_memory,
)
from wzgram.filters import command, regex, user
from wzgram.types import InlineKeyboardButton, InlineKeyboardMarkup

from FZBypass import BOT_NAME, BOT_START, Bypass, Config
from FZBypass.core.bot_utils import (
    AuthChatsTopics,
    convert_time,
    get_readable_size,
    progress_bar,
)
from FZBypass.core.commands import BotCommands


def usable_cpus(proc):
    try:
        return len(proc.cpu_affinity())
    except Exception:
        return cpu_count(logical=True) or "N/A"


def bot_stats() -> str:
    proc = Process()
    memory = virtual_memory()
    swap = swap_memory()
    total, used, free, disk = disk_usage(".")
    bot_ram = proc.memory_info().rss
    cpu = cpu_percent(interval=0.1)
    cores = cpu_count(logical=True) or 0
    p_cores = cpu_count(logical=False) or 0
    return (
        f"★ <b>{BOT_NAME.upper()} — SYSTEM TELEMETRY</b> ★\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"┏ <b>⏱ Uptime:</b> <code>{convert_time(time() - BOT_START)}</code>\n"
        f"┠ <b>🐍 Python:</b> <code>{python_version()}</code>  •  <b>Workers:</b> <code>{Config.WORKERS}</code>\n"
        f"┗ <b>🧠 Bot RAM:</b> <code>{get_readable_size(bot_ram)}</code>\n\n"
        f"┏ <b>💾 SYSTEM RAM</b>\n"
        f"┠ {progress_bar(memory.percent)} <b>{memory.percent}%</b>\n"
        f"┗ <b>U:</b> {get_readable_size(memory.used)} | <b>F:</b> {get_readable_size(memory.available)} | <b>T:</b> {get_readable_size(memory.total)}\n\n"
        f"┏ <b>🔄 SWAP MEMORY</b>\n"
        f"┠ {progress_bar(swap.percent)} <b>{swap.percent}%</b>\n"
        f"┗ <b>U:</b> {get_readable_size(swap.used)} | <b>F:</b> {get_readable_size(swap.free)} | <b>T:</b> {get_readable_size(swap.total)}\n\n"
        f"┏ <b>⚙️ CPU</b>\n"
        f"┠ {progress_bar(cpu)} <b>{cpu}%</b>\n"
        f"┗ <b>Cores:</b> {cores} (P: {p_cores} / V: {max(0, cores - p_cores)}) • <b>Usable:</b> {usable_cpus(proc)}\n\n"
        f"┏ <b>💿 DISK</b>\n"
        f"┠ {progress_bar(disk)} <b>{disk}%</b>\n"
        f"┗ <b>U:</b> {get_readable_size(used)} | <b>F:</b> {get_readable_size(free)} | <b>T:</b> {get_readable_size(total)}"
    )


def _stats_markup(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data=f"stats {uid} refresh"),
                InlineKeyboardButton("✖ Close", callback_data=f"stats {uid} close"),
            ]
        ]
    )


@Bypass.on_message(
    command(BotCommands.StatsCommand) & (user(Config.OWNER_ID) | AuthChatsTopics)
)
async def send_stats(client, message):
    uid = message.from_user.id if message.from_user else 0
    await message.reply(
        await to_thread(bot_stats),
        reply_markup=_stats_markup(uid),
    )


@Bypass.on_callback_query(regex(r"^stats "))
async def stats_cb(client, query):
    _, owner, action = query.data.split()
    uid = query.from_user.id
    if int(owner) != 0 and uid != int(owner):
        return await query.answer("Not Yours!", show_alert=True)
    if action == "refresh":
        await query.answer("Refreshing...")
        text = await to_thread(bot_stats)
        try:
            await query.message.edit_text(text, reply_markup=_stats_markup(uid))
        except Exception:
            pass
    elif action == "close":
        await query.answer()
        await query.message.delete()
