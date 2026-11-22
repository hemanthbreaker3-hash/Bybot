from contextlib import redirect_stdout, suppress
from html import escape
from io import BytesIO, StringIO
from os import chdir, getcwd
from re import match
from textwrap import indent
from traceback import format_exc
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE

from wzgram.filters import command, user
from FZBypass import BOT_NAME, Bypass, Config, LOGGER
from FZBypass.core.commands import BotCommands


@Bypass.on_message(command(BotCommands.BashCommand) & user(Config.OWNER_ID))
async def bash(_, message):
    msg = str(await get_result(message) or "")
    if len(msg) > 2000:
        with BytesIO(msg.encode("utf-8")) as out_file:
            out_file.name = "output.txt"
            await message.reply_document(out_file)
    else:
        LOGGER.info(f"OUTPUT: '{msg}'")
        if not msg or msg == "\n":
            msg = "<i>MessageEmpty</i>"
        elif not match(r"<(blockquote|spoiler|b|i|code|s|u|/a)>", msg):
            msg = f"<blockquote>{escape(msg)}</blockquote>"
        await message.reply(msg)


async def get_result(message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        return ""
    content = parts[1]
    body = (
        "\n".join(content.split("\n")[1:-1])
        if content.startswith("```") and content.endswith("```")
        else content.strip("` \n")
    )
    env = {"__builtins__": globals()["__builtins__"], "bot": Bypass, "message": message}
    chdir(getcwd())

    stdout = StringIO()
    to_compile = f'async def func():\n{indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return f"{e.__class__.__name__}: {e}"

    func = env["func"]
    try:
        with redirect_stdout(stdout):
            func_return = await func()
    except Exception:
        return f"{stdout.getvalue()}{format_exc()}"

    value = stdout.getvalue()
    if func_return is None:
        if value:
            return value
        with suppress(Exception):
            return repr(eval(body, env))
        return ""
    return f"{value}{func_return}"


@Bypass.on_message(command(BotCommands.ShellCommand) & user(Config.OWNER_ID))
async def shell(_, message):
    cmd = (message.text or "").split(maxsplit=1)
    if len(cmd) == 1 or not cmd[1].strip():
        return await message.reply("<i>No command to execute was given.</i>")
    cmd = cmd[1]
    proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout_txt = stdout.decode(errors="replace").strip()
    stderr_txt = stderr.decode(errors="replace").strip()
    reply = ""
    if stdout_txt:
        reply += f"<b>📤 Stdout</b>\n<blockquote>{escape(stdout_txt)}</blockquote>\n"
        LOGGER.info(f"Shell - {cmd} - {stdout_txt}")
    if stderr_txt:
        reply += f"<b>⚠️ Stderr</b>\n<blockquote>{escape(stderr_txt)}</blockquote>"
        LOGGER.error(f"Shell - {cmd} - {stderr_txt}")
    if len(reply) > 3000:
        raw = f"STDOUT:\n{stdout_txt}\n\nSTDERR:\n{stderr_txt}".encode("utf-8")
        with BytesIO(raw) as out_file:
            out_file.name = "shell_output.txt"
            await message.reply_document(out_file)
    elif reply:
        await message.reply(f"★ <b>{BOT_NAME.upper()} SHELL</b> ★\n\n{reply}")
    else:
        await message.reply("<i>No Output</i>")
