#!/usr/bin/env python3
"""Lint docs leaf titles against omnimux-docs-ia naming norms."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fm(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        km = re.match(r'^(\w+):\s*["\']?(.*?)["\']?\s*$', line)
        if km:
            out[km.group(1)] = km.group(2).strip()
    return out


def main() -> int:
    # Language complete: sidebar must include brand + complete phrase
    for loc, needle in [("cn", "完整参数"), ("en", "Complete reference")]:
        for p in sorted((ROOT / loc / "api-reference/text-series").glob("*/complete.mdx")):
            meta = fm(p)
            title = meta.get("title", "")
            side = meta.get("sidebarTitle") or title
            brand = p.parent.name
            # brand folder is slug; title should contain · and needle
            if needle not in side or "·" not in side:
                errors.append(f"{p}: sidebarTitle must be '{{Brand}} · {needle}', got {side!r}")
            if side != title:
                errors.append(f"{p}: title/sidebarTitle mismatch: {title!r} vs {side!r}")
            # bare complete forbidden
            if side.strip() in {needle, f'"{needle}"'}:
                errors.append(f"{p}: bare sidebarTitle {side!r}")

    # Image/video model leaves: non-empty capability, not model-id-only
    for series in ("image-series", "video-series"):
        for loc in ("cn", "en"):
            models = ROOT / loc / "api-reference" / series / "models"
            if not models.is_dir():
                continue
            for p in sorted(models.glob("*.mdx")):
                meta = fm(p)
                title = meta.get("title", "")
                side = meta.get("sidebarTitle") or title
                leaf = p.stem
                if not side:
                    errors.append(f"{p}: empty title/sidebarTitle")
                    continue
                if side == leaf or side.replace("-", "_") == leaf.replace("-", "_"):
                    errors.append(f"{p}: sidebarTitle is raw model id {side!r}")
                if loc == "en":
                    low = side.lower()
                    # forbid bare trailing capability words alone as whole title
                    if low in {"generate", "image", "video", "async"}:
                        errors.append(f"{p}: EN bare capability word {side!r}")
                    if re.search(r"\bgenerate\b", low) and "generation" not in low:
                        errors.append(f"{p}: EN uses bare 'generate' — prefer Generation / Text-to-Video: {side!r}")

    # Orphans that must not exist
    for rel in (
        "cn/api-reference/coverage.mdx",
        "cn/api-reference/errors.mdx",
        "en/api-reference/coverage.mdx",
        "en/api-reference/errors.mdx",
    ):
        if (ROOT / rel).exists():
            errors.append(f"orphan must be deleted: {rel}")

    if errors:
        print("check-naming: FAIL")
        for e in errors:
            print(" ", e)
        return 1
    print("check-naming: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
