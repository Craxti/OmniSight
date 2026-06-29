#!/usr/bin/env python3
"""Split monolithic locale files into per-feature modules."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web" / "src" / "i18n" / "locales"


def split_locale(locale: str) -> None:
    src = ROOT / f"{locale}.ts"
    text = src.read_text(encoding="utf-8")
    text = re.sub(r"^import .+\n", "", text, flags=re.MULTILINE)
    body = re.sub(rf"export const {locale} = \{{\n?", "", text.strip())
    if body.endswith("}"):
        body = body[:-1]

    out_dir = ROOT / locale
    out_dir.mkdir(exist_ok=True)
    keys: list[str] = []
    i = 0
    while i < len(body):
        m = re.match(r"\n?(\s*)([a-zA-Z_][\w]*): \{", body[i:])
        if not m:
            break
        key = m.group(2)
        start = i + m.end() - 1
        depth = 0
        j = start
        while j < len(body):
            ch = body[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        chunk = body[start:j].strip()
        (out_dir / f"{key}.ts").write_text(f"export const {key} = {chunk}\n", encoding="utf-8")
        keys.append(key)
        i = j
        while i < len(body) and body[i] in ",\n ":
            i += 1

    imports = "\n".join(f"import {{ {k} }} from './{k}'" for k in keys)
    exports = ",\n  ".join(keys)
    if locale == "en":
        index = f"{imports}\n\nexport const {locale} = {{\n  {exports},\n}} as const\nexport type LocaleMessages = typeof {locale}\n"
    else:
        index = f"import type {{ LocaleMessages }} from '../en/index'\n\n{imports}\n\nexport const {locale} = {{\n  {exports},\n}} satisfies LocaleMessages\n"
    (out_dir / "index.ts").write_text(index, encoding="utf-8")
    print(f"{locale}: {len(keys)} sections -> {out_dir}")


if __name__ == "__main__":
    for loc in ("en", "ru"):
        split_locale(loc)
