"""Convert relative TypeScript imports under src/ to @/ alias."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

IMPORT_RE = re.compile(
    r"""(?P<prefix>from\s+|import\s+)['"](?P<spec>\.[^'"]+)['"]""",
)


def _resolve_spec(from_file: Path, spec: str) -> str | None:
    target = (from_file.parent / spec).resolve()
    try:
        rel = target.relative_to(SRC.resolve())
    except ValueError:
        return None
    return "@/" + rel.as_posix()


def migrate_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    changed = False

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        spec = match.group("spec")
        alias = _resolve_spec(path, spec)
        if alias is None:
            return match.group(0)
        changed = True
        return f"{match.group('prefix')}'{alias}'"

    new_text = IMPORT_RE.sub(repl, text)
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return changed


def main() -> None:
    count = 0
    for file in SRC.rglob("*"):
        if file.suffix not in {".ts", ".tsx"}:
            continue
        if "generated" in file.parts:
            continue
        if migrate_file(file):
            count += 1
            print(file.relative_to(ROOT))
    print(f"Migrated {count} files")


if __name__ == "__main__":
    main()
