#!/usr/bin/env python3
"""Generate changelog index/pages JSON and en/zh MDX from data/changelog/entries/.

Human MDX matches Mintlify official Product updates layout:
https://www.mintlify.com/docs/changelog
  — frontmatter + stacked <Update label tags rss> blocks.
Machine feeds stay at data/changelog/index.json and pages/*.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENTRIES_DIR = ROOT / "data" / "changelog" / "entries"
OUT_DIR = ROOT / "data" / "changelog"
PAGES_DIR = OUT_DIR / "pages"
SCHEMA_VERSION = 1
PAGE_SIZE = 50  # changelog timelines are usually one long page
TYPES = frozenset(
    {"model_launch", "capability", "pricing", "breaking", "platform", "baseline"}
)
MODALITIES = frozenset(
    {"text", "image", "video", "audio", "social-data", "publishing", "platform", "other"}
)
LOCALES = ("en", "zh")

# Type + modality → filter chips (Mintlify Update tags = right-rail filters)
TYPE_TAG = {
    "en": {
        "model_launch": "New models",
        "capability": "Improvements",
        "pricing": "Pricing",
        "breaking": "Breaking",
        "platform": "Platform",
        "baseline": "Catalog",
    },
    "zh": {
        "model_launch": "新模型",
        "capability": "能力更新",
        "pricing": "价格调整",
        "breaking": "不兼容变更",
        "platform": "平台",
        "baseline": "目录",
    },
}
MODALITY_TAG = {
    "en": {
        "text": "Text",
        "image": "Image",
        "video": "Video",
        "audio": "Audio",
        "social-data": "Social data",
        "publishing": "Publishing",
        "platform": "Platform",
        "other": "Other",
    },
    "zh": {
        "text": "文本",
        "image": "图像",
        "video": "视频",
        "audio": "音频",
        "social-data": "社交数据",
        "publishing": "社媒发布",
        "platform": "平台",
        "other": "其他",
    },
}

_MONTH_EN = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


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


def format_label(published_at: str, locale: str) -> str:
    """Mintlify official uses 'August 7, 2026'; zh uses '2026 年 8 月 7 日'."""
    y, m, d = (int(x) for x in published_at.split("-"))
    if locale == "zh":
        return f"{y} 年 {m} 月 {d} 日"
    return f"{_MONTH_EN[m - 1]} {d}, {y}"


def build_tags(e: dict[str, Any], locale: str) -> list[str]:
    tags: list[str] = []
    typ = e.get("type")
    if typ in TYPE_TAG[locale]:
        tags.append(TYPE_TAG[locale][typ])
    for mod in e.get("modality") or []:
        if mod == "platform" and typ == "platform":
            continue
        label = MODALITY_TAG[locale].get(mod)
        if label and label not in tags:
            tags.append(label)
    # entry-level free tags (optional English keys) — skip if already covered
    for t in e.get("tags") or []:
        if not isinstance(t, str) or not t.strip():
            continue
        # keep raw only if not a raw modality slug already mapped
        if t in MODALITY_TAG["en"] or t in TYPE_TAG["en"].values():
            continue
        if t not in tags and t not in ("available", "feed", "chat", "async"):
            # don't dump internal slugs as chips
            if re.fullmatch(r"[a-z0-9-]+", t) and t in (
                "text",
                "image",
                "video",
                "audio",
                "social-data",
                "platform",
            ):
                continue
    return tags


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
    if not isinstance(eid, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]*", eid
    ):
        errs.append(f"{path_hint}: id must match YYYY-MM-DD-slug")
    if e.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"{path_hint}: schema_version must be {SCHEMA_VERSION}")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", str(e.get("published_at") or "")):
        errs.append(f"{path_hint}: published_at must be YYYY-MM-DD")
    else:
        try:
            date.fromisoformat(str(e["published_at"]))
        except ValueError:
            errs.append(f"{path_hint}: published_at is not a valid date")
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
        if not isinstance(v, dict) or not all(
            isinstance(v.get(l), str) and v.get(l).strip() for l in LOCALES
        ):
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


def jsx_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def indent_block(text: str, spaces: int = 2) -> str:
    pad = " " * spaces
    lines = text.rstrip().splitlines()
    return "\n".join(pad + line if line.strip() else "" for line in lines)


def render_update(e: dict[str, Any], locale: str) -> str:
    """One Mintlify <Update> block (official changelog style)."""
    label = format_label(str(e["published_at"]), locale)
    tags = build_tags(e, locale)
    rss_title = loc_text(e["title"], locale)
    body = loc_text(e["body"], locale).rstrip()
    links = e.get("links") or []

    # Append docs links as markdown list (inside Update body)
    if links:
        link_heading = "### Links" if locale == "en" else "### 链接"
        link_lines = [link_heading, ""]
        for link in links:
            lab = loc_text(link.get("label"), locale)
            href = loc_text(link.get("href"), locale)
            if lab and href:
                link_lines.append(f"- [{lab}]({href})")
        body = body + "\n\n" + "\n".join(link_lines)

    tags_jsx = "[" + ", ".join(jsx_string(t) for t in tags) + "]"
    # Mintlify: <Update label="..." tags={[...]} rss={{ title: "..." }}>
    open_tag = (
        f"<Update label={jsx_string(label)} tags={{{tags_jsx}}} "
        f"rss={{{{ title: {jsx_string(rss_title)} }}}}>"
    )
    # Anchor id for deep links / checker (official Update also anchors on label)
    anchor = f'<a id="{e["id"]}"></a>'
    inner = indent_block(body, 2)
    return f"{anchor}\n\n{open_tag}\n\n{inner}\n\n</Update>"


def render_mdx(entries: list[dict[str, Any]], locale: str, page: int, total_pages: int) -> str:
    is_en = locale == "en"
    title = "API Updates" if is_en else "API 更新"
    desc = (
        "Stay informed about the latest model launches, capability changes, pricing, and platform notes on OmniMux."
        if is_en
        else "获取所有 API 最新变更与改进通知。"
    )
    # Match Mintlify official: short blurb under H1 via description; minimal intro prose
    intro = (
        "Stay up to date with OmniMux gateway model launches and platform changes. "
        "The full callable catalog is on [console pricing](https://omnimux.ai) / "
        "[Pricing](/en/api-reference/account/pricing)."
        if is_en
        else "跟踪 OmniMux 网关的模型上新与平台变更。"
        "完整可调用模型以[控制台定价](https://omnimux.ai) / "
        "[定价与账户](/zh/api-reference/account/pricing)为准。"
    )

    lines: list[str] = [
        "---",
        f'title: "{title}"',
        f'sidebarTitle: "{title}"',
        f'description: "{desc}"',
        "rss: true",
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
        for e in entries:
            lines.append(render_update(e, locale))
            lines.append("")

    footer = (
        "---\n\n"
        f"**Machine-readable:** [`/data/changelog/index.json`](/data/changelog/index.json) · "
        f"[`/data/changelog/pages/{page}.json`](/data/changelog/pages/{page}.json)\n"
        if is_en
        else "---\n\n"
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

    print(
        f"wrote index + {total_pages} page(s) JSON and {len(LOCALES)}× MDX "
        f"for {len(entries)} entries (Mintlify <Update> layout)"
    )


if __name__ == "__main__":
    main()
