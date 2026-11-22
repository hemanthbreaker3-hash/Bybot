from os import path as opath, getenv
from logging import (
    StreamHandler,
    INFO,
    basicConfig,
    error as log_error,
    info as log_info,
)
from logging.handlers import RotatingFileHandler
from subprocess import run as srun

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=20 * 1024 * 1024, backupCount=5, encoding="utf-8"),
        StreamHandler(),
    ],
)

try:
    import config
except ImportError:
    config = None

UPSTREAM_REPO = getenv("UPSTREAM_REPO") or getattr(config, "UPSTREAM_REPO", None) or ""
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH") or getattr(config, "UPSTREAM_BRANCH", None) or "main"

if UPSTREAM_REPO:
    if opath.exists(".git"):
        srun(["rm", "-rf", ".git"], check=False)

    cmd = (
        "git init -q "
        '&& git config user.email "alonekingstar@users.noreply.github.com" '
        '&& git config user.name "AloneKingStar" '
        "&& git add . "
        '&& git commit -sm "update" -q '
        f'&& git remote add origin "{UPSTREAM_REPO}" '
        "&& git fetch origin -q "
        f'&& git reset --hard "origin/{UPSTREAM_BRANCH}" -q'
    )
    update = srun(cmd, shell=True)

    if update.returncode == 0:
        log_info("Successfully updated with latest commit from UPSTREAM_REPO")
    else:
        log_error("Something went wrong while updating, check UPSTREAM_REPO if valid or not!")
else:
    log_info("UPSTREAM_REPO is not set; skipping upstream update.")
