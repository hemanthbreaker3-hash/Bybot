from wzgram.filters import command, regex
from wzgram.types import InlineKeyboardButton, InlineKeyboardMarkup

from FZBypass import BOT_NAME, Bypass, Config
from FZBypass.core.commands import BotCommands


def _start_text() -> str:
    return (
        f"★ <b>{BOT_NAME.upper()} BYPASS</b> ★\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <i>High-Speed Async Link Unwrapper &amp; Scraper</i>\n\n"
        f"┏ <b>Core Capabilities:</b>\n"
        f"┠ 🚀 <b>Pooled Async Engine</b> — <i>Ultra-fast concurrent bypass</i>\n"
        f"┠ 🔁 <b>LoopBypass V2</b> — <i>Auto-unwraps nested shorteners</i>\n"
        f"┠ ☁️ <b>Cloud &amp; GDrive</b> — <i>Terabox, GDToT, HubDrive, GDFlix &amp; more</i>\n"
        f"┗ ⚡ <b>Inline Mode</b> — <i>Use</i> <code>!bp [link]</code> <i>in any chat</i>\n\n"
        f"📖 <b>Commands:</b> /{BotCommands.HelpCommand}  •  "
        f"📊 <b>Stats:</b> /{BotCommands.StatsCommand}"
    )


def _start_markup(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 Commands", callback_data=f"ak_nav {uid} help"),
                InlineKeyboardButton("📊 Stats", callback_data=f"ak_nav {uid} stats"),
            ],
            [
                InlineKeyboardButton("⚡ Try Inline Bypass", switch_inline_query_current_chat="!bp "),
            ],
        ]
    )


@Bypass.on_message(command(BotCommands.StartCommand))
async def start_msg(client, message):
    uid = message.from_user.id if message.from_user else 0
    await message.reply(
        _start_text(),
        reply_markup=_start_markup(uid),
        disable_web_page_preview=True,
    )


@Bypass.on_callback_query(regex(r"^ak_nav "))
async def nav_cb(client, query):
    _, owner, target = query.data.split()
    uid = query.from_user.id
    if int(owner) != 0 and uid != int(owner):
        return await query.answer("Not Yours!", show_alert=True)

    if target == "home":
        await query.answer()
        return await query.message.edit_text(
            _start_text(),
            reply_markup=_start_markup(uid),
            disable_web_page_preview=True,
        )
    if target == "help":
        from FZBypass.handlers.help import build_help_text

        await query.answer()
        me = getattr(getattr(client, "me", None), "username", "bot")
        return await query.message.edit_text(
            build_help_text(me, uid == Config.OWNER_ID),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⬅️ Back", callback_data=f"ak_nav {uid} home"),
                        InlineKeyboardButton("✖ Close", callback_data=f"ak_nav {uid} close"),
                    ]
                ]
            ),
            disable_web_page_preview=True,
        )
    if target == "stats":
        from asyncio import to_thread
        from FZBypass.handlers.stats import bot_stats

        await query.answer("Refreshing telemetry...")
        text = await to_thread(bot_stats)
        return await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔄 Refresh", callback_data=f"ak_nav {uid} stats"),
                        InlineKeyboardButton("⬅️ Back", callback_data=f"ak_nav {uid} home"),
                    ]
                ]
            ),
            disable_web_page_preview=True,
        )
    if target == "close":
        await query.answer()
        return await query.message.delete()
