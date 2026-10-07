#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
export NOTEBOOKLM_HOME="$PWD/.local/notebooklm"
exec .venv/bin/python scripts/login_neofirm.py
