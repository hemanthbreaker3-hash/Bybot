<div align="center">

# ★ ***AloneKing Star Bypass Bot*** ★

<i>A **High-Speed Async Multi-Threaded Telegram Bypass &amp; Scraper Bot** powered by pooled `aiohttp`, `uvloop`, and `wzgram`.</i>

</div>

---

## ***Features***
- **Pooled Async Engine** — Shared `aiohttp` connection pool + `asyncio.to_thread` offloading for zero event-loop blocking.
- **LoopBypass V2** — Automatically unwraps nested shorteners with cycle detection &amp; configurable hop limits.
- **AloneKing Star UI** — Clean, interactive Telegram HTML interface with live telemetry refresh and inline mode (`!bp [link]`).
- **Full Shell `export` Support** — Export any credential directly in your shell or `env.sh`; shell exports always take highest priority.
- **One-Script VPS Deploy (`deploy.vps`)** — Automated venv, dependency install, credential export setup, and `systemd` service.

---

## ***1. One-Script VPS Deployment (`deploy.vps`)***

Deploy the entire bot on Ubuntu/Debian VPS in a single command:

```bash
bash deploy.vps
```

Or export your credentials in shell first for zero-prompt deployment:

```bash
export BOT_TOKEN="your_bot_token"
export API_ID="123456"
export API_HASH="your_api_hash"
export OWNER_ID="123456789"
bash deploy.vps --non-interactive
```

---

## ***2. Manual Run with Shell Exports***

Copy `env.example.sh` to `env.sh`, fill in your credentials, and run:

```bash
cp env.example.sh env.sh
nano env.sh
source env.sh
python3 -m FZBypass
```

### ***All Supported Credentials &amp; Variables (Shell `export` / `env.sh` / `config.py`)***
- `BOT_TOKEN` *(Required)* — Bot token from `@BotFather`.
- `API_ID` *(Required)* — Telegram API ID from `my.telegram.org`.
- `API_HASH` *(Required)* — Telegram API Hash from `my.telegram.org`.
- `OWNER_ID` *(Required)* — Numeric Telegram user ID of the bot owner.
- `AUTH_CHATS` — Space-separated chat IDs (`chat_id` or `chat_id:topic_id`).
- `AUTO_BYPASS` — `True` / `False` (default `False`).
- `CMD_SUFFIX` — Optional suffix for commands (e.g. `1` → `/bypass1`).
- `DIRECT_INDEX` — Cloudflare Worker Google Drive Index URL.
- `TERA_COOKIE` — Terabox `ndus` cookie.
- `GDTOT_CRYPT`, `HUBDRIVE_CRYPT`, `KATDRIVE_CRYPT`, `DRIVEFIRE_CRYPT` — Drive site `crypt` cookies.
- `LARAVEL_SESSION`, `XSRF_TOKEN` — `sharer.pw` cookies.
- `PORT` — Health server port (default `8080`).
- `WORKERS` — Telegram client workers (default `16`).
- `BYPASS_TIMEOUT` — HTTP request timeout in seconds (default `25`).
- `MAX_CONCURRENT_BYPASS` — Max concurrent bypass tasks (default `25`).
- `MAX_LOOP_HOPS` — Max nested shortener hops (default `10`).
- `AUTO_UPDATE`, `UPSTREAM_REPO`, `UPSTREAM_BRANCH` — Optional upstream git updater.
