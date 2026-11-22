from asyncio import create_task, gather, sleep as asleep
from html import escape
from time import time

from wzgram.enums import MessageEntityType
from wzgram.errors import FloodWait, QueryIdInvalid
from wzgram.filters import user
from wzgram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from FZBypass import BOT_NAME, Bypass, Config
from FZBypass.bypass.checker import direct_link_checker, is_excep_link
from FZBypass.core.bot_utils import (
    AuthChatsTopics,
    BypassFilter,
    convert_time,
    get_sender_info,
)

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


async def _safe_edit(msg, text: str):
    try:
        await msg.edit(text, disable_web_page_preview=True)
    except FloodWait as fw:
        await asleep(fw.value + 0.5)
        await msg.edit(text, disable_web_page_preview=True)


@Bypass.on_message(BypassFilter & (user(Config.OWNER_ID) | AuthChatsTopics))
async def bypass_check(client, message):
    uid, mention = get_sender_info(message)
    if (reply_to := message.reply_to_message) and (
        reply_to.text is not None or reply_to.caption is not None
    ):
        txt = reply_to.text or reply_to.caption or ""
        entities = reply_to.entities or reply_to.caption_entities or []
    elif Config.AUTO_BYPASS or len((message.text or "").split()) > 1:
        txt = message.text or message.caption or ""
        entities = message.entities or message.caption_entities or []
    else:
        return await message.reply(f"★ <b>{BOT_NAME}</b> — <i>No Link Provided!</i>")

    tlinks, atasks = [], []
    for enty in entities:
        link = ""
        if enty.type == MessageEntityType.URL:
            link = txt[enty.offset : (enty.offset + enty.length)]
        elif enty.type == MessageEntityType.TEXT_LINK:
            link = enty.url or ""
        if link:
            tlinks.append(link)
            atasks.append(create_task(direct_link_checker(link)))

    if not atasks:
        return await message.reply(f"★ <b>{BOT_NAME}</b> — <i>No Valid Links Found!</i>")

    wait_msg = await message.reply(
        f"⚡ <b>{BOT_NAME}</b> — <i>Bypassing {len(atasks)} link(s)...</i>"
    )
    start = time()
    completed_tasks = await gather(*atasks, return_exceptions=True)
    end = time()

    parse_data = []
    for result, link in zip(completed_tasks, tlinks):
        if isinstance(result, Exception):
            bp_link = f"\n┗ <b>❌ Error:</b> <code>{escape(str(result))}</code>"
        elif is_excep_link(link):
            bp_link = str(result)
        elif isinstance(result, list):
            bp_link, ui = "", "┗"
            for ind, lplink in reversed(list(enumerate(result, start=1))):
                bp_link = f"\n{ui} <b>⚡ {ind}x Bypass:</b> {lplink}" + bp_link
                ui = "┠"
        else:
            bp_link = f"\n┗ <b>⚡ Bypass:</b> {result}"

        if is_excep_link(link):
            parse_data.append(f"{bp_link}\n\n{SEP}\n\n")
        else:
            parse_data.append(
                f"┏ <b>🔗 Source:</b> {link}{bp_link}\n\n{SEP}\n\n"
            )

    if parse_data:
        parse_data[-1] += (
            f"┏ <b>📦 Total Links:</b> <code>{len(atasks)}</code>\n"
            f"┠ <b>⏱ Completed In:</b> <code>{convert_time(end - start)}</code>\n"
            f"┗ <b>👤 Requested By:</b> {mention} (<code>#ID{uid}</code>)"
        )

    tg_txt = f"★ <b>{BOT_NAME.upper()} BYPASS</b> ★\n{SEP}\n\n"
    for tg_data in parse_data:
        if len(tg_txt) + len(tg_data) > 4000 and tg_txt:
            await _safe_edit(wait_msg, tg_txt)
            wait_msg = await message.reply(
                f"⚡ <b>{BOT_NAME}</b> — <i>Fetching remaining results...</i>",
                reply_to_message_id=wait_msg.id,
            )
            tg_txt = ""
            await asleep(0.5)
        tg_txt += tg_data

    if tg_txt:
        await _safe_edit(wait_msg, tg_txt)
    else:
        await wait_msg.delete()


@Bypass.on_inline_query()
async def inline_query(client, query):
    answers = []
    raw_query = (query.query or "").strip()
    if raw_query.lower().startswith("!bp "):
        link = raw_query[4:].strip()
        start = time()
        try:
            bp_link = await direct_link_checker(link, True)
            end = time()

            if not is_excep_link(link):
                bp_link = f"┏ <b>🔗 Source:</b> {link}\n┗ <b>⚡ Bypass:</b> {bp_link}"
            answers.append(
                InlineQueryResultArticle(
                    title="⚡ AloneKing Star — Bypass Success!",
                    input_message_content=InputTextMessageContent(
                        f"★ <b>{BOT_NAME.upper()} BYPASS</b> ★\n{SEP}\n\n"
                        f"{bp_link}\n\n{SEP}\n"
                        f"⏱ <b>Took Only <code>{convert_time(end - start)}</code></b>",
                        disable_web_page_preview=True,
                    ),
                    description=f"Bypass: {link}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "⚡ Bypass Again",
                                    switch_inline_query_current_chat="!bp ",
                                )
                            ]
                        ]
                    ),
                )
            )
        except Exception as e:
            end = time()
            answers.append(
                InlineQueryResultArticle(
                    title="❌ AloneKing Star — Bypass Error!",
                    input_message_content=InputTextMessageContent(
                        f"★ <b>{BOT_NAME.upper()} BYPASS</b> ★\n{SEP}\n\n"
                        f"┏ <b>🔗 Source:</b> {link}\n"
                        f"┗ <b>❌ Error:</b> <code>{escape(str(e))}</code>\n\n{SEP}\n"
                        f"⏱ <b>Took <code>{convert_time(end - start)}</code></b>",
                        disable_web_page_preview=True,
                    ),
                    description=f"Error bypassing: {link}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔁 Try Again",
                                    switch_inline_query_current_chat="!bp ",
                                )
                            ]
                        ]
                    ),
                )
            )
    else:
        answers.append(
            InlineQueryResultArticle(
                title=f"★ {BOT_NAME} — Inline Bypass Guide",
                input_message_content=InputTextMessageContent(
                    f"★ <b>{BOT_NAME.upper()} BYPASS</b> ★\n{SEP}\n\n"
                    f"⚡ <i>High-Speed Async Link Unwrapper &amp; Scraper</i>\n\n"
                    f"🎛 <b>Inline Usage:</b> <code>!bp [Single Link]</code>",
                    disable_web_page_preview=True,
                ),
                description="Type !bp [link] to bypass inline",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "⚡ Try Bypass", switch_inline_query_current_chat="!bp "
                            ),
                        ]
                    ]
                ),
            )
        )
    try:
        await query.answer(results=answers, cache_time=0)
    except QueryIdInvalid:
        pass
