#!/usr/bin/env python3
"""Generate changelog index/pages JSON and en/zh MDX from data/changelog/entries/.

Human page is an Evolink/APIMart-style timeline (date → typed title → body).
Machine feeds stay at data/changelog/index.json and pages/*.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = ROOT / "data" / "changelog" / "entries"
OUT_DIR = ROOT / "data" / "changelog"
PAGES_DIR = OUT_DIR / "pages"
SCHEMA_VERSION = 1
PAGE_SIZE = 20
TYPES = frozenset(
    {"model_launch", "capability", "pricing", "breaking", "platform", "baseline"}
)
MODALITIES = frozenset(
    {"text", "image", "video", "audio", "social-data", "publishing", "platform", "other"}
)
LOCALES = ("en", "zh")

# Evolink-style type chips (public labels). Prefer not to use baseline for new entries.
TYPE_LABEL = {
    "en": {
        "model_launch": "New Model",
        "capability": "Model Update",
        "pricing": "Pricing",
        "breaking": "Breaking",
        "platform": "Platform",
        "baseline": "Catalog note",
    },
    "zh": {
        "model_launch": "新模型",
        "capability": "模型更新",
        "pricing": "价格调整",
        "breaking": "不兼容变更",
        "platform": "平台",
        "baseline": "目录说明",
    },
}


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def loc_text(value: Any, locale: str) -> str:
    if isinstance(value, dict):
        if locale in value and value[locale]:
            return str(value[locale])
        if "en" in value and value["en"]:
            return str(value["en"])
        for v in value.values():
            if v:
                return str(v)
        return ""
    return "" if value is None else str(value)


def load_entries() -> list[dict[str, Any]]:
    if not ENTRIES_DIR.is_dir():
        die(f"missing entries dir: {ENTRIES_DIR}")
    items: list[dict[str, Any]] = []
    for path in sorted(ENTRIES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            die(f"invalid JSON {path}: {e}")
        if not isinstance(data, dict):
            die(f"{path}: root must be object")
        data["_source"] = path.name
        items.append(data)
    # Newer dates first; within a day, higher rank first (default 0); then id desc.
    items.sort(
        key=lambda e: (
            str(e.get("published_at") or ""),
            int(e.get("rank") or 0),
            str(e.get("id") or ""),
        ),
        reverse=True,
    )
    return items


def validate_entry(e: dict[str, Any], path_hint: str) -> list[str]:
    errs: list[str] = []
    eid = e.get("id")
    if not isinstance(eid, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]*", eid):
        errs.append(f"{path_hint}: id must match YYYY-MM-DD-slug")
    if e.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"{path_hint}: schema_version must be {SCHEMA_VERSION}")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", str(e.get("published_at") or "")):
        errs.append(f"{path_hint}: published_at must be YYYY-MM-DD")
    if e.get("type") not in TYPES:
        errs.append(f"{path_hint}: type must be one of {sorted(TYPES)}")
    mods = e.get("modality")
    if not isinstance(mods, list) or not mods:
        errs.append(f"{path_hint}: modality must be non-empty array")
    else:
        for m in mods:
            if m not in MODALITIES:
                errs.append(f"{path_hint}: unknown modality {m!r}")
    for field in ("title", "summary", "body"):
        v = e.get(field)
        if not isinstance(v, dict) or not all(isinstance(v.get(l), str) and v.get(l).strip() for l in LOCALES):
            errs.append(f"{path_hint}: {field}.en and {field}.zh required non-empty strings")
    models = e.get("models", [])
    if not isinstance(models, list) or any(not isinstance(x, str) or not x for x in models):
        errs.append(f"{path_hint}: models must be string array")
    links = e.get("links", [])
    if not isinstance(links, list):
        errs.append(f"{path_hint}: links must be array")
    else:
        for i, link in enumerate(links):
            if not isinstance(link, dict):
                errs.append(f"{path_hint}: links[{i}] must be object")
                continue
            if not isinstance(link.get("label"), dict) or not isinstance(link.get("href"), dict):
                errs.append(f"{path_hint}: links[{i}] needs label{{en,zh}} and href{{en,zh}}")
    tags = e.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(x, str) for x in tags):
        errs.append(f"{path_hint}: tags must be string array")
    if "rank" in e and e["rank"] is not None and not isinstance(e["rank"], int):
        errs.append(f"{path_hint}: rank must be int when set")
    return errs


def meta_of(e: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": e["id"],
        "published_at": e["published_at"],
        "type": e["type"],
        "modality": e.get("modality") or [],
        "title": e["title"],
        "summary": e["summary"],
        "models": e.get("models") or [],
        "tags": e.get("tags") or [],
        "links": e.get("links") or [],
    }


def full_of(e: dict[str, Any]) -> dict[str, Any]:
    out = meta_of(e)
    out["body"] = e["body"]
    out["schema_version"] = SCHEMA_VERSION
    return out


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def chunk(items: list[Any], size: int) -> list[list[Any]]:
    if not items:
        return [[]]
    return [items[i : i + size] for i in range(0, len(items), size)]


def render_mdx(entries: list[dict[str, Any]], locale: str, page: int, total_pages: int) -> str:
    is_en = locale == "en"
    title = "API Updates" if is_en else "API 更新"
    sidebar = title
    desc = (
        "Stay informed about the latest changes and improvements across OmniMux APIs."
        if is_en
        else "获取所有 API 最新变更与改进通知。"
    )
    # User-facing intro only (no repo paths / gen commands). Machine feed in footer.
    intro = (
        "Stay informed about the latest model launches, capability changes, pricing updates, and platform notes on OmniMux.\n\n"
        "The full callable catalog is always on [console pricing](https://omnimux.ai) / "
        "[Pricing API](/en/api-reference/account/pricing). Incidents: [status.omnimux.ai](https://status.omnimux.ai)."
        if is_en
        else "跟踪 OmniMux 的模型上新、能力变更、定价调整与平台说明。\n\n"
        "完整可调用模型以[控制台定价](https://omnimux.ai) / "
        "[定价与账户](/zh/api-reference/account/pricing)为准。故障与可用性见 [status.omnimux.ai](https://status.omnimux.ai)。"
    )

    lines: list[str] = [
        "---",
        f'title: "{title}"',
        f'sidebarTitle: "{sidebar}"',
        f'description: "{desc}"',
        "---",
        "",
        intro,
        "",
    ]

    if total_pages > 1:
        nav_bits = []
        for p in range(1, total_pages + 1):
            href = f"/{locale}/updates" if p == 1 else f"/{locale}/updates/page-{p}"
            label = f"Page {p}" if is_en else f"第 {p} 页"
            if p == page:
                nav_bits.append(f"**{label}**")
            else:
                nav_bits.append(f"[{label}]({href})")
        lines.append(("Pages: " if is_en else "分页：") + " · ".join(nav_bits))
        lines.append("")

    if not entries:
        lines.append("_No updates yet._" if is_en else "_暂无更新。_")
        lines.append("")
    else:
        current_date: str | None = None
        for e in entries:
            eid = e["id"]
            typ = e["type"]
            type_label = TYPE_LABEL[locale].get(typ, typ)
            title_t = loc_text(e["title"], locale)
            summary = loc_text(e["summary"], locale)
            body = loc_text(e["body"], locale).rstrip()
            date = e["published_at"]

            if date != current_date:
                current_date = date
                lines.append(f"### {date}")
                lines.append("")

            lines.append(f'<a id="{eid}"></a>')
            lines.append("")
            lines.append(f"## {title_t}")
            lines.append("")
            lines.append(f"`{type_label}`")
            lines.append("")
            if summary:
                lines.append(f"*{summary}*")
                lines.append("")
            # Do not dump models[] as a wall of chips — IDs belong in the body (APIMart style).
            lines.append(body)
            lines.append("")
            links = e.get("links") or []
            if links:
                lines.append("### " + ("Links" if is_en else "链接"))
                lines.append("")
                for link in links:
                    lab = loc_text(link.get("label"), locale)
                    href = loc_text(link.get("href"), locale)
                    if lab and href:
                        lines.append(f"- [{lab}]({href})")
                lines.append("")
            lines.append("---")
            lines.append("")

        while lines and lines[-1] in ("", "---"):
            lines.pop()
        lines.append("")

    # Footer: machine-readable only (integration / Agent consumers)
    footer = (
        "\n---\n\n"
        f"**Machine-readable:** [`/data/changelog/index.json`](/data/changelog/index.json) · "
        f"[`/data/changelog/pages/{page}.json`](/data/changelog/pages/{page}.json)\n"
        if is_en
        else "\n---\n\n"
        f"**机器可读：** [`/data/changelog/index.json`](/data/changelog/index.json) · "
        f"[`/data/changelog/pages/{page}.json`](/data/changelog/pages/{page}.json)\n"
    )
    lines.append(footer.rstrip())
    lines.append("")
    return "\n".join(lines)


def mdx_path(locale: str, page: int) -> Path:
    if page == 1:
        return ROOT / locale / "updates.mdx"
    return ROOT / locale / "updates" / f"page-{page}.mdx"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-size", type=int, default=PAGE_SIZE)
    parser.add_argument("--check-only", action="store_true", help="validate only, do not write")
    args = parser.parse_args()

    entries = load_entries()
    errors: list[str] = []
    seen: set[str] = set()
    for e in entries:
        hint = e.get("_source") or e.get("id") or "?"
        errors.extend(validate_entry(e, str(hint)))
        eid = e.get("id")
        if isinstance(eid, str):
            if eid in seen:
                errors.append(f"duplicate id: {eid}")
            seen.add(eid)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        die(f"{len(errors)} validation error(s)")

    pages = chunk(entries, max(1, args.page_size))
    total_pages = len(pages)
    index = {
        "schema_version": SCHEMA_VERSION,
        "generated_note": "Generated by scripts/gen-changelog-pages.py — edit entries/, do not hand-edit this file.",
        "page_size": args.page_size,
        "total": len(entries),
        "total_pages": total_pages,
        "items": [meta_of(e) for e in entries],
        "pages": [
            {
                "page": i + 1,
                "path": f"data/changelog/pages/{i + 1}.json",
                "count": len(pages[i]),
            }
            for i in range(total_pages)
        ],
    }

    if args.check_only:
        print(f"ok: {len(entries)} entries, {total_pages} page(s)")
        return

    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    for old in PAGES_DIR.glob("*.json"):
        old.unlink()
    for locale in LOCALES:
        archive_dir = ROOT / locale / "updates"
        if archive_dir.is_dir():
            for old in archive_dir.glob("page-*.mdx"):
                old.unlink()

    write_json(OUT_DIR / "index.json", index)
    for i, page_entries in enumerate(pages, start=1):
        write_json(
            PAGES_DIR / f"{i}.json",
            {
                "schema_version": SCHEMA_VERSION,
                "page": i,
                "page_size": args.page_size,
                "total": len(entries),
                "total_pages": total_pages,
                "items": [full_of(e) for e in page_entries],
            },
        )
        for locale in LOCALES:
            path = mdx_path(locale, i)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                render_mdx(page_entries, locale, i, total_pages),
                encoding="utf-8",
            )

    print(f"wrote index + {total_pages} page(s) JSON and {len(LOCALES)}× MDX for {len(entries)} entries")


if __name__ == "__main__":
    main()
