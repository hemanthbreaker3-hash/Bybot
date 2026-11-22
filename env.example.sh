# ==============================================================================
# AloneKing Star Bypass Bot — Shell Export Credentials
# ==============================================================================
# Copy this file to env.sh, fill in your values, and run:
#   source env.sh && python3 -m FZBypass
# Or export these variables directly in your shell / systemd / Docker environment.
# Shell exports ALWAYS take precedence over config.py and .env!
# ==============================================================================

# --- Required Credentials ---
export BOT_TOKEN=""
export API_ID=""
export API_HASH=""
export OWNER_ID=""

# --- Access & Command Settings ---
export AUTH_CHATS=""          # Space-separated chat IDs, use chat_id:topic_id for forum topics
export AUTO_BYPASS="False"    # "True" to auto-bypass links without /bypass command
export CMD_SUFFIX=""          # Optional command suffix (e.g. "1" -> /bypass1)

# --- Host & Shortener Cookies / Index (Optional) ---
export DIRECT_INDEX=""        # Cloudflare Worker Google Drive Index URL
export TERA_COOKIE=""         # Terabox "ndus" cookie
export GDTOT_CRYPT=""         # GDToT "crypt" cookie
export HUBDRIVE_CRYPT=""      # HubDrive "crypt" cookie
export KATDRIVE_CRYPT=""      # KatDrive "crypt" cookie
export DRIVEFIRE_CRYPT=""     # DriveFire "crypt" cookie
export LARAVEL_SESSION=""     # sharer.pw "laravel_session" cookie
export XSRF_TOKEN=""          # sharer.pw "XSRF-TOKEN" cookie

# --- Server & Performance Tuning ---
export PORT="8080"
export WORKERS="16"
export BYPASS_TIMEOUT="25"
export MAX_CONCURRENT_BYPASS="25"
export MAX_LOOP_HOPS="10"

# --- Auto-Update (Optional) ---
export AUTO_UPDATE="False"
export UPSTREAM_REPO=""
export UPSTREAM_BRANCH="main"
