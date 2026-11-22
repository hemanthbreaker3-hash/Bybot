from asyncio import create_subprocess_exec
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from os import execl, path as ospath, remove
from sys import executable
from threading import Thread
from time import time

from wzgram import idle
from wzgram.filters import command, user

from FZBypass import BOT_NAME, BOT_START, Bypass, Config, LOGGER
from FZBypass.core.bot_utils import convert_time
from FZBypass.core.commands import BotCommands
from FZBypass.core.http_client import close_http_session, get_http_session


class Health(BaseHTTPRequestHandler):
    def _head(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

    def do_HEAD(self):
        self._head()

    def do_GET(self):
        self._head()
        uptime = convert_time(time() - BOT_START)
        self.wfile.write(f"{BOT_NAME} Bypass Bot is alive | Uptime: {uptime}".encode("utf-8"))

    def log_message(self, *args):
        pass


def serve_health():
    port = Config.PORT
    LOGGER.info(f"Health server listening on port {port}")
    ThreadingHTTPServer(("0.0.0.0", port), Health).serve_forever()


@Bypass.on_message(command(BotCommands.RestartCommand) & user(Config.OWNER_ID))
async def restart(client, message):
    restart_message = await message.reply(
        f"★ <b>{BOT_NAME}</b> — <i>Restarting system...</i>"
    )
    if Config.AUTO_UPDATE:
        proc = await create_subprocess_exec("python3", "update.py")
        await proc.wait()
    with open(".restartmsg", "w", encoding="utf-8") as f:
        f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    await close_http_session()
    execl(executable, executable, "-m", "FZBypass")


async def notify_restart():
    if ospath.isfile(".restartmsg"):
        try:
            with open(".restartmsg", encoding="utf-8") as f:
                chat_id, msg_id = map(int, f)
            await Bypass.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=f"★ <b>{BOT_NAME}</b> — <i>System Restarted Successfully!</i> ⚡",
            )
        except Exception as e:
            LOGGER.error(e)
        finally:
            try:
                remove(".restartmsg")
            except OSError:
                pass


async def main():
    Thread(target=serve_health, daemon=True).start()
    await get_http_session()
    await Bypass.start()
    LOGGER.info(f"{BOT_NAME} Bypass Bot Started! (Workers: {Config.WORKERS})")
    await notify_restart()
    await idle()
    await close_http_session()
    await Bypass.stop()


if __name__ == "__main__":
    Bypass.loop.run_until_complete(main())
