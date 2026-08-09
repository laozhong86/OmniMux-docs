#!/usr/bin/env python3
"""Validate changelog entries and that generated artifacts are in sync."""

from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "gen_changelog_pages", ROOT / "scripts" / "gen-changelog-pages.py"
)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)

load_entries = _mod.load_entries
validate_entry = _mod.validate_entry
meta_of = _mod.meta_of
full_of = _mod.full_of
mdx_path = _mod.mdx_path
PAGE_SIZE = _mod.PAGE_SIZE
LOCALES = _mod.LOCALES
chunk = _mod.chunk


def fetch_pricing_models() -> set[str] | None:
    url = "https://omnimux.ai/api/pricing"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "omnimux-docs-check-changelog/1"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        print(f"warn: could not fetch live pricing ({e}); skipping model membership checks")
        return None
    items = data.get("data") if isinstance(data, dict) else None
    if not isinstance(items, list):
        print("warn: unexpected pricing shape; skipping model membership checks")
        return None
    names = {m.get("model_name") for m in items if isinstance(m, dict) and m.get("model_name")}
    return {n for n in names if isinstance(n, str)}


def main() -> int:
    errors: list[str] = []
    entries = load_entries()
    seen: set[str] = set()
    for e in entries:
        hint = e.get("_source") or e.get("id") or "?"
        errors.extend(validate_entry(e, str(hint)))
        eid = e.get("id")
        if isinstance(eid, str):
            if eid in seen:
                errors.append(f"duplicate id: {eid}")
            seen.add(eid)

    live = fetch_pricing_models()
    if live is not None:
        for e in entries:
            for mid in e.get("models") or []:
                if mid not in live:
                    errors.append(
                        f"{e.get('id')}: model {mid!r} not on live pricing (remove or onboard first)"
                    )

    index_path = ROOT / "data" / "changelog" / "index.json"
    if not index_path.is_file():
        errors.append("missing data/changelog/index.json — run gen-changelog-pages.py")
    else:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        expected_items = [meta_of(e) for e in entries]
        if index.get("items") != expected_items:
            errors.append("index.json items out of sync with entries/ — run gen-changelog-pages.py")
        if index.get("total") != len(entries):
            errors.append("index.json total mismatch")

    pages = chunk(entries, PAGE_SIZE)
    total_pages = len(pages)
    for i, page_entries in enumerate(pages, start=1):
        ppath = ROOT / "data" / "changelog" / "pages" / f"{i}.json"
        if not ppath.is_file():
            errors.append(f"missing {ppath.relative_to(ROOT)}")
            continue
        payload = json.loads(ppath.read_text(encoding="utf-8"))
        if payload.get("items") != [full_of(e) for e in page_entries]:
            errors.append(f"{ppath.name} out of sync — run gen-changelog-pages.py")
        for locale in LOCALES:
            mpath = mdx_path(locale, i)
            if not mpath.is_file():
                errors.append(f"missing {mpath.relative_to(ROOT)}")
            else:
                text = mpath.read_text(encoding="utf-8")
                for e in page_entries:
                    if e["id"] not in text:
                        errors.append(f"{mpath.name}: missing anchor/id {e['id']}")

    pages_dir = ROOT / "data" / "changelog" / "pages"
    if pages_dir.is_dir():
        for f in pages_dir.glob("*.json"):
            try:
                n = int(f.stem)
            except ValueError:
                errors.append(f"unexpected page file {f.name}")
                continue
            if n < 1 or n > total_pages:
                errors.append(f"stale page file {f.name}")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(f"FAIL: {len(errors)} issue(s)", file=sys.stderr)
        return 1
    print(f"ok: {len(entries)} entries, {total_pages} page(s), artifacts in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
