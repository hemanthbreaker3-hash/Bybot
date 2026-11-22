from wzgram.filters import command
from wzgram.types import InlineKeyboardButton, InlineKeyboardMarkup

from FZBypass import BOT_NAME, Bypass, Config
from FZBypass.core.commands import BotCommands

BYPASS_CMDS = ", ".join(f"/{c}" for c in BotCommands.BypassCommand)


def build_help_text(me_username: str, is_owner: bool = False) -> str:
    text = (
        f"★ <b>{BOT_NAME.upper()} — COMMAND CENTER</b> ★\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"┏ <b>⚡ BYPASS ENGINE</b>\n"
        f"┠ <b>{BYPASS_CMDS}</b> <code>[link]</code>\n"
        f"┠ <i>Or reply to any message containing links</i>\n"
        f"┗ <i>Inline:</i> <code>@{me_username} !bp [link]</code>\n\n"
        f"┏ <b>📌 GENERAL</b>\n"
        f"┠ <b>/{BotCommands.StartCommand}</b> — <i>Welcome &amp; quick menu</i>\n"
        f"┠ <b>/{BotCommands.HelpCommand}</b> — <i>This command guide</i>\n"
        f"┗ <b>/{BotCommands.StatsCommand}</b> — <i>Live system &amp; bot telemetry</i>"
    )
    if is_owner:
        text += (
            f"\n\n┏ <b>🛡 OWNER CONTROLS</b>\n"
            f"┠ <b>/{BotCommands.LogCommand}</b> — <i>Download or inspect logs</i>\n"
            f"┠ <b>/{BotCommands.RestartCommand}</b> — <i>Restart bot process</i>\n"
            f"┠ <b>/{BotCommands.BashCommand}</b> <code>[code]</code> — <i>Execute Python</i>\n"
            f"┗ <b>/{BotCommands.ShellCommand}</b> <code>[cmd]</code> — <i>Execute Shell</i>"
        )
    if Config.AUTO_BYPASS:
        text += "\n\n⚡ <i>AUTO_BYPASS is enabled — any link sent is bypassed automatically.</i>"
    return text


@Bypass.on_message(command(BotCommands.HelpCommand))
async def help_msg(client, message):
    uid = message.from_user.id if message.from_user else 0
    me = getattr(getattr(client, "me", None), "username", "bot")
    await message.reply(
        build_help_text(me, uid == Config.OWNER_ID),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✖ Close", callback_data=f"ak_nav {uid} close")]]
        ),
        disable_web_page_preview=True,
    )
