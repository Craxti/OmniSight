"""Host metadata collection."""

from __future__ import annotations

import subprocess
from pathlib import Path


def host_info() -> dict[str, str]:
    hostname = subprocess.check_output(["hostname"], text=True).strip() or "unknown"
    if hostname in ("localhost", "localhost.localdomain"):
        try:
            hostname = Path("/etc/hostname").read_text(encoding="utf-8").strip() or hostname
        except OSError:
            pass
    ip = ""
    try:
        ip = subprocess.check_output(["hostname", "-I"], text=True).strip().split()[0]
    except (subprocess.CalledProcessError, IndexError):
        pass
    os_name = "Linux"
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                os_name = line.split("=", 1)[1].strip().strip('"')
                break
    except OSError:
        pass
    return {"hostname": hostname, "ip": ip, "os": os_name}
