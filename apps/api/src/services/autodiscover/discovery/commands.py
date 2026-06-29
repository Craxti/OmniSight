"""Subprocess helpers for host discovery."""

from __future__ import annotations

import subprocess


def run_cmd(args: list[str]) -> tuple[str | None, str | None]:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.PIPE), None
    except FileNotFoundError:
        return None, f"command not found: {args[0]}"
    except subprocess.CalledProcessError as exc:
        return None, (exc.stderr or exc.stdout or str(exc)).strip()


def run_docker(args: list[str]) -> tuple[str | None, str | None]:
    last_err = ""
    for base in (["docker"], ["sudo", "-n", "docker"]):
        try:
            return subprocess.check_output(base + args, text=True, stderr=subprocess.PIPE), None
        except FileNotFoundError:
            return None, "docker not installed"
        except subprocess.CalledProcessError as exc:
            last_err = (exc.stderr or exc.stdout or str(exc)).strip()
    return None, last_err or "docker command failed (add user to docker group or passwordless sudo)"
