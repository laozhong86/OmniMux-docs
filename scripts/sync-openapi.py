#!/usr/bin/env python3
"""Sync gateway OpenAPI from the OmniMux product repo into this docs repo.

Usage (from OmniMux-docs root):

  python3 scripts/sync-openapi.py
  python3 scripts/sync-openapi.py --source ../OmniMux/docs/openapi/relay.json

Transforms:
  - set info title/description for public docs
  - set production servers
  - drop operations tagged 未实现/*
  - map Chinese tags to short English labels for the sidebar
  - keep only BearerAuth security scheme
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT.parent / "OmniMux" / "docs" / "openapi" / "relay.json"
DEFAULT_DEST = ROOT / "openapi" / "relay.json"

TAG_MAP = {
    "OpenAI格式(Chat)": "Chat",
    "OpenAI格式(Responses)": "Responses",
    "Claude格式(Messages)": "Claude",
    "Gemini格式": "Gemini",
    "OpenAI格式(Embeddings)": "Embeddings",
    "OpenAI音频(Audio)": "Audio",
    "图片生成/Qwen千问": "Images",
    "视频生成": "Video",
    "视频生成/Sora兼容格式": "Video (Sora)",
    "视频生成/Kling格式": "Video (Kling)",
    "视频生成/即梦格式": "Video (Jimeng)",
    "获取模型列表": "Models",
    "文本补全(Completions)": "Completions",
    "重排序(Rerank)": "Rerank",
    "Moderations": "Moderations",
    "Realtime": "Realtime",
}


def transform(src: dict) -> dict:
    d = copy.deepcopy(src)
    version = (d.get("info") or {}).get("version") or "1.0.0"
    d["info"] = {
        "title": "OmniMux Gateway API",
        "description": (
            "OpenAI-compatible unified AI gateway. "
            "Authenticate with Authorization: Bearer <token>."
        ),
        "version": version,
    }
    d["servers"] = [
        {
            "url": "https://geminix.cc",
            "description": "OmniMux production gateway",
        }
    ]

    new_paths: dict = {}
    dropped = 0
    for path, methods in (d.get("paths") or {}).items():
        keep: dict = {}
        for method, op in methods.items():
            if method.startswith("x-"):
                keep[method] = op
                continue
            tags = op.get("tags") or []
            if any("未实现" in t for t in tags):
                dropped += 1
                continue
            op = copy.deepcopy(op)
            op["tags"] = [TAG_MAP.get(t, t) for t in tags]
            keep[method] = op
        if any(not k.startswith("x-") for k in keep):
            new_paths[path] = keep
    d["paths"] = new_paths

    schemes = (d.get("components") or {}).get("securitySchemes") or {}
    d.setdefault("components", {})["securitySchemes"] = {
        "BearerAuth": schemes.get("BearerAuth")
        or {
            "type": "http",
            "scheme": "bearer",
            "description": "Authorization: Bearer sk-xxxxxx",
        }
    }
    d["security"] = [{"BearerAuth": []}]
    d["_sync_meta"] = {"dropped_unimplemented_ops": dropped}
    return d


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()

    if not args.source.is_file():
        print(f"source not found: {args.source}", file=sys.stderr)
        return 1

    raw = json.loads(args.source.read_text(encoding="utf-8"))
    out = transform(raw)
    meta = out.pop("_sync_meta", {})
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    args.dest.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {args.dest} paths={len(out.get('paths', {}))} "
        f"dropped_ops={meta.get('dropped_unimplemented_ops', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
