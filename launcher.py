from __future__ import annotations

import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path


APP_PORT = 8501


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent


def app_path() -> Path:
    return resource_root() / "app.py"


def open_browser_later(url: str, delay_seconds: float = 1.8) -> None:
    timer = threading.Timer(delay_seconds, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()


def main() -> int:
    url = f"http://localhost:{APP_PORT}"
    if is_port_open("127.0.0.1", APP_PORT):
        webbrowser.open(url)
        return 0

    os.environ["SONIC_RUNTIME_ROOT"] = str(runtime_root())
    os.environ["SONIC_RESOURCE_ROOT"] = str(resource_root())

    script = app_path()
    if not script.exists():
        print(f"Could not find app.py at {script}", file=sys.stderr)
        return 1

    open_browser_later(url)

    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        str(script),
        "--server.port",
        str(APP_PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())
