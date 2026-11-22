# Copy this file to config.py in the repo root and fill it up.
# NOTE: Exported shell environment variables (export KEY="value") and .env
# ALWAYS take priority over empty or default values here.

# Required
BOT_TOKEN = ""
API_HASH = ""
API_ID = ""
AUTH_CHATS = ""  # Separate multiple ids by space and : for topic_ids
OWNER_ID = 0  # Telegram user id of the bot owner

# Optional
AUTO_BYPASS = False
CMD_SUFFIX = ""  # Suffix added to every command, e.g. "1" gives /bypass1
LARAVEL_SESSION = ""
XSRF_TOKEN = ""
GDTOT_CRYPT = ""
HUBDRIVE_CRYPT = ""
DRIVEFIRE_CRYPT = ""
KATDRIVE_CRYPT = ""
DIRECT_INDEX = ""
PORT = 8080  # Health server port, Render / Koyeb override it via $PORT
TERA_COOKIE = ""

# Performance Tuning
WORKERS = 16
BYPASS_TIMEOUT = 25
MAX_CONCURRENT_BYPASS = 25
MAX_LOOP_HOPS = 10

# Update
AUTO_UPDATE = False
UPSTREAM_REPO = ""
UPSTREAM_BRANCH = "main"
