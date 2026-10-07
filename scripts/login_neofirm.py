"""Complete human Google sign-in before the CLI's URL-only login capture."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlencode, urlparse

from notebooklm.config import get_base_url
from notebooklm.paths import get_browser_profile_dir, get_home_dir, get_profile_dir
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def google_session_ready(context, page, base_url):
    # Host alone is not authentication: the anonymous marketing page uses it too.
    return (urlparse(page.url).hostname == urlparse(base_url).hostname
            and any(cookie["name"] == "SID" and cookie.get("value")
                    for cookie in context.cookies([base_url, "https://accounts.google.com/"])))


def wait_for_google_session(context, page, base_url, timeout=300):
    deadline = time.monotonic() + timeout
    while not google_session_ready(context, page, base_url):
        if time.monotonic() >= deadline:
            raise RuntimeError("Google 로그인 시간 초과. 창에서 로그인 후 다시 실행하세요.")
        page.wait_for_timeout(1000)


def verify_auth(cli):
    result = subprocess.run([cli, "auth", "check", "--test", "--passive", "--json"],
                            cwd=ROOT, capture_output=True, text=True, timeout=120)
    data = json.loads(result.stdout)
    checks = data.get("checks", {})
    if result.returncode or data.get("status") != "ok" or checks.get("token_fetch") is not True:
        # Never print raw diagnostics: they may contain identity or cookie data.
        raise RuntimeError("NotebookLM 서버 인증 실패. 로그인 창에서 NotebookLM 이용 가능 여부를 확인하세요.")
    print('AUTH OK: status=ok, token_fetch=true', flush=True)


def main():
    if os.environ.get("NOTEBOOKLM_AUTH_JSON"):
        raise RuntimeError("NOTEBOOKLM_AUTH_JSON이 설정되어 있습니다. 파일 기반 로그인 전에 해제하세요.")
    get_home_dir(create=True)
    get_profile_dir(create=True)
    profile = get_browser_profile_dir()
    profile.mkdir(parents=True, exist_ok=True, mode=0o700)
    profile.chmod(0o700)
    base_url = get_base_url()
    print("Chrome 창에서 Google 로그인 후 NotebookLM 노트북 목록을 여세요. 최대 5분 기다립니다.", flush=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(profile), channel="chrome", headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"])
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
            if not google_session_ready(context, page, base_url):
                page.goto("https://accounts.google.com/ServiceLogin?"
                          + urlencode({"continue": base_url + "/"}), wait_until="commit")
            wait_for_google_session(context, page, base_url)
        finally:
            context.close()
    # Delegate cookie filtering, rotation and secure storage to the installed CLI.
    cli = str(ROOT / ".venv/bin/notebooklm")
    print("Google 세션 확인. NotebookLM CLI로 저장하고 서버 인증을 검사합니다.", flush=True)
    result = subprocess.run([cli, "login", "--browser", "chrome"], cwd=ROOT,
                            capture_output=True, text=True, timeout=420)
    if result.returncode:
        raise RuntimeError("NotebookLM CLI 로그인 저장 실패. Chrome 창을 모두 닫고 다시 실행하세요.")
    verify_auth(cli)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        message = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        print(f"LOGIN FAILED: {message}", file=sys.stderr)
        sys.exit(1)
