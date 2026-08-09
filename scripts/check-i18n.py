#!/usr/bin/env python3
"""Lint cn/en docs parity for OmniMux-docs (Mintlify languages)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CJK = re.compile(r"[\u4e00-\u9fff]")
CROSS_LINK = re.compile(
    r"\]\((?:https://docs\.omnimux\.ai)?/(cn|en)/[^)\s]+\)"
)
# FAQ may keep product term 积分 in EN
CJK_WHITELIST_PREFIXES = (
    "en/faqs/",
)


def mdx_rels(locale: str) -> set[str]:
    base = ROOT / locale
    out: set[str] = set()
    for p in base.rglob("*.mdx"):
        out.add(str(p.relative_to(base)).replace("\\", "/")[:-4])
    return out


def nav_rels() -> tuple[set[str], set[str]]:
    d = json.loads((ROOT / "docs.json").read_text(encoding="utf-8"))
    cn: set[str] = set()
    en: set[str] = set()

    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for x in obj:
                walk(x)
        elif isinstance(obj, str):
            if obj.startswith("cn/"):
                cn.add(obj[3:])
            elif obj.startswith("en/"):
                en.add(obj[3:])

    walk(d.get("navigation", {}))
    return cn, en


def body_no_code(text: str) -> str:
    text = re.sub(r"^---.*?---\n", "", text, count=1, flags=re.S)
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return text


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    disk_cn, disk_en = mdx_rels("cn"), mdx_rels("en")
    if disk_cn != disk_en:
        errors.append(f"disk path mismatch only_cn={sorted(disk_cn-disk_en)} only_en={sorted(disk_en-disk_cn)}")

    nav_cn, nav_en = nav_rels()
    if nav_cn != nav_en:
        errors.append(f"nav path mismatch only_cn={sorted(nav_cn-nav_en)} only_en={sorted(nav_en-nav_cn)}")

    for loc, rels in (("cn", nav_cn), ("en", nav_en)):
        for rel in sorted(rels):
            path = ROOT / loc / f"{rel}.mdx"
            if not path.is_file():
                errors.append(f"nav missing file: {loc}/{rel}.mdx")

    # cross-locale links
    for loc, other in (("cn", "en"), ("en", "cn")):
        for p in (ROOT / loc).rglob("*.mdx"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in CROSS_LINK.finditer(text):
                if m.group(1) == other:
                    errors.append(f"cross-locale link in {p.relative_to(ROOT)}: {m.group(0)}")

    # EN CJK warning
    for p in (ROOT / "en").rglob("*.mdx"):
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        if any(rel.startswith(w) for w in CJK_WHITELIST_PREFIXES):
            continue
        n = len(CJK.findall(body_no_code(p.read_text(encoding="utf-8", errors="ignore"))))
        if n > 15:
            warnings.append(f"EN heavy CJK ({n}): {rel}")

    # line-count drift warning
    for rel in sorted(disk_cn & disk_en):
        cn_lines = len((ROOT / "cn" / f"{rel}.mdx").read_text(encoding="utf-8", errors="ignore").splitlines())
        en_lines = len((ROOT / "en" / f"{rel}.mdx").read_text(encoding="utf-8", errors="ignore").splitlines())
        if abs(cn_lines - en_lines) > 40:
            warnings.append(f"line drift |cn-en|={abs(cn_lines-en_lines)} cn={cn_lines} en={en_lines} {rel}")

    if warnings:
        print("check-i18n: WARN")
        for w in warnings:
            print(" ", w)
    if errors:
        print("check-i18n: FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print("check-i18n: OK" + (f" ({len(warnings)} warnings)" if warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
