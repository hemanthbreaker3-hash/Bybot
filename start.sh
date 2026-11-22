#!/usr/bin/env bash
set -e

if [ -f "env.sh" ]; then
  # shellcheck disable=SC1091
  source "env.sh"
fi

if [ -d "/app/.heroku/" ] || [ -d "/app/.scalingo/" ]; then
  exec python3 -m FZBypass
elif [ "${AUTO_UPDATE,,}" = "true" ]; then
  python3 update.py && exec python3 -m FZBypass
else
  exec python3 -m FZBypass
fi
