"""Fail early on an unusable local browser and keep browser assertions enabled."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

PREFLIGHT_TIMEOUT = 60
SUITE_TIMEOUT = 900


def run_browser(root: Path, script: str, *, timeout: int = SUITE_TIMEOUT) -> bool:
    """Use the selected browser environment, never optimized Python or fixture mode."""
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)
    env['POKER_BROWSER_REQUIRE_REPO'] = '1'
    try:
        result = subprocess.run([sys.executable, '-u', script], cwd=root,
                                env=env, check=False, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f'{script}: FAIL (browser command exceeded {timeout}s)', flush=True)
        return False
    except OSError as exc:
        print(f'{script}: FAIL ({exc})', flush=True)
        return False
    print(f'{script}: {"PASS" if result.returncode == 0 else "FAIL"}', flush=True)
    return result.returncode == 0


def preflight(root: Path) -> bool:
    print('\n=== Local browser capability preflight ===', flush=True)
    return run_browser(root, '_scripts/release_browser_gate.py', timeout=PREFLIGHT_TIMEOUT)


def browser_smoke() -> None:
    """Check real Chromium and loopback navigation, without external requests."""
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from threading import Thread
    from playwright.sync_api import sync_playwright

    marker = 'local browser release preflight'

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/release-probe':
                self.send_error(404)
                return
            body = ('<!doctype html><title>Release probe</title><p id="probe">'
                    + marker + '</p>').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/release-probe'
    try:
        with sync_playwright() as pw:
            options = {'headless': True, 'timeout': 15000}
            if os.environ.get('CHROMIUM_PATH'):
                options['executable_path'] = os.environ['CHROMIUM_PATH']
            browser = pw.chromium.launch(**options)
            try:
                page = browser.new_page()
                page.route('**/*', lambda route: route.continue_()
                           if route.request.url == url else route.abort())
                response = page.goto(url, timeout=15000)
                if (response is None or response.status != 200
                        or page.locator('#probe').text_content(timeout=5000) != marker):
                    raise RuntimeError('Loopback browser did not render the expected probe')
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    print('Chromium launched and rendered a local HTTP page.', flush=True)


if __name__ == '__main__':
    try:
        browser_smoke()
    except Exception as exc:
        print(f'Browser preflight blocked: {type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        raise SystemExit(1)
