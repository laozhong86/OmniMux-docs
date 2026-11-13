#!/usr/bin/env python3
"""Lint the 社媒发布 / Publishing API manual against official-only governance."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLISHING = Path("api-reference/publishing")
FAQS = Path("faqs")
LOCALES = ("zh", "en")

# Retired aggregation vendors must never return to public copy.
VENDOR_PATTERN = re.compile(r"zernio|tikhub", re.I)

# Pages that document a client-side or local call instead of an OpenAPI op.
# Value is the single route the page may declare.
NON_OPENAPI_ROUTES = {
    "presign": "/api/social/v1/media/presign",
    "seats": "/api/social/v1/seats",
}

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)
FIELD = re.compile(r'^(\w+):\s*["\']?(.*?)["\']?\s*$', re.M)
OPENAPI_REF = re.compile(r"^(openapi/\S+\.json)\s+([A-Z]+)\s+(\S+)$")
API_REF = re.compile(r"^([A-Z]+)\s+https://omnimux\.ai(\S+)$")
LINK = re.compile(r"\]\(([^)\s]+)\)")


def frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    return {m.group(1): m.group(2) for m in FIELD.finditer(match.group(1))}


def ops_routes() -> dict[str, set[tuple[str, str]]]:
    routes: dict[str, set[tuple[str, str]]] = {}
    for path in sorted((ROOT / "openapi" / "ops" / "publishing").glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        found: set[tuple[str, str]] = set()
        for route, methods in spec.get("paths", {}).items():
            for method in methods:
                found.add((method.upper(), route))
        routes[path.name] = found
    return routes


def main() -> int:
    errors: list[str] = []
    routes = ops_routes()

    for loc in LOCALES:
        for path in sorted((ROOT / loc / PUBLISHING).rglob("*.mdx")):
            rel = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            meta = frontmatter(text)

            for match in VENDOR_PATTERN.finditer(text):
                line = text[: match.start()].count("\n") + 1
                errors.append(f"{rel}:{line}: retired vendor name {match.group(0)!r} in public copy")

            if "openapi" in meta:
                parsed = OPENAPI_REF.match(meta["openapi"])
                if not parsed:
                    errors.append(f"{rel}: openapi frontmatter must be '<ops.json> METHOD /path'")
                else:
                    ops_file, method, route = parsed.groups()
                    if not (ROOT / ops_file).is_file():
                        errors.append(f"{rel}: missing OpenAPI op {ops_file}")
                    elif (method, route) not in routes.get(Path(ops_file).name, set()):
                        errors.append(f"{rel}: {method} {route} is not declared in {ops_file}")

            if "api" in meta:
                parsed = API_REF.match(meta["api"])
                if not parsed:
                    errors.append(f"{rel}: api frontmatter must be 'METHOD https://omnimux.ai/path'")
                else:
                    _method, route = parsed.groups()
                    expected = NON_OPENAPI_ROUTES.get(path.stem)
                    if expected is None:
                        errors.append(
                            f"{rel}: pages without an OpenAPI op must be allowlisted in NON_OPENAPI_ROUTES"
                        )
                    elif route != expected:
                        errors.append(f"{rel}: declares {route}, expected {expected}")

            for target in LINK.findall(text):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                if target.startswith("/"):
                    candidate = ROOT / target.lstrip("/")
                else:
                    candidate = (path.parent / target).resolve()
                candidates = [candidate, Path(str(candidate) + ".mdx"), candidate / "index.mdx"]
                if not any(c.is_file() for c in candidates):
                    errors.append(f"{rel}: dead link {target}")

    if errors:
        print("check-publishing: FAIL")
        for error in errors:
            print(" ", error)
        return 1
    print("check-publishing: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
