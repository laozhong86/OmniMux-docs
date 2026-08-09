#!/usr/bin/env python3
"""Generate language-series pages by **contract**, not by model id.

Norm (confirmed): one Complete page per (brand × protocol) when request/response
shape is shared; `model` is an enum of live ids. Separate pages only when
method/path/schema differ.

Usage (OmniMux-docs root):
  python3 scripts/gen-chat-capability-pages.py --all-brands
  python3 scripts/gen-chat-capability-pages.py --brands claude gpt
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELAY = ROOT / "openapi" / "relay.json"
OPS_DIR = ROOT / "openapi" / "ops" / "chat"
MODELS_DIR = ROOT / "cn" / "api-reference" / "text-series" / "models"

# brand key → (display CN, display EN, model-id prefix regex)
BRANDS: dict[str, tuple[str, str, str]] = {
    "claude": ("Claude", "Claude", r"^claude"),
    "gemini": ("Gemini", "Gemini", r"^gemini"),
    "gpt": ("GPT", "GPT", r"^gpt-"),
    "grok": ("Grok", "Grok", r"^grok"),
    "kimi": ("Kimi", "Kimi", r"^kimi"),
    "deepseek": ("DeepSeek", "DeepSeek", r"^deepseek"),
    "minimax": ("MiniMax", "MiniMax", r"^minimax"),
    "glm": ("GLM", "GLM", r"^glm"),
}

ERROR_EXAMPLES = {
    "400": {
        "error": {
            "message": "Invalid request: missing required field or invalid parameter",
            "type": "invalid_request_error",
            "code": "bad_request",
        }
    },
    "401": {
        "error": {
            "message": "Invalid token or authentication failed",
            "type": "authentication_error",
            "code": "unauthorized",
        }
    },
    "402": {
        "error": {
            "message": "Insufficient quota. Please top up your account.",
            "type": "insufficient_quota",
            "code": "insufficient_quota",
        }
    },
    "403": {
        "error": {
            "message": "Model not allowed for this token, or access denied",
            "type": "permission_error",
            "code": "forbidden",
        }
    },
    "404": {
        "error": {
            "message": "Not found",
            "type": "invalid_request_error",
            "code": "not_found",
        }
    },
    "429": {
        "error": {
            "message": "Rate limit exceeded. Please retry later.",
            "type": "rate_limit_error",
            "code": "rate_limit_exceeded",
        }
    },
    "500": {
        "error": {
            "message": "Internal server error",
            "type": "server_error",
            "code": "internal_error",
        }
    },
    "502": {
        "error": {
            "message": "Upstream provider error or bad gateway",
            "type": "server_error",
            "code": "bad_gateway",
        }
    },
    "503": {
        "error": {
            "message": "Service temporarily unavailable",
            "type": "server_error",
            "code": "service_unavailable",
        }
    },
}

ERROR_DESCRIPTIONS = {
    "400": "Invalid request parameters",
    "401": "Unauthenticated — invalid or expired token",
    "402": "Insufficient quota — top up required",
    "403": "Access denied — model or token scope",
    "404": "Resource not found",
    "429": "Rate limit exceeded",
    "500": "Internal server error",
    "502": "Upstream / bad gateway",
    "503": "Service temporarily unavailable",
}


CATALOG = OPS_DIR / "_brand_models.json"


def load_catalog() -> dict[str, list[str]]:
    if CATALOG.exists():
        return json.loads(CATALOG.read_text(encoding="utf-8"))
    return {}


def save_catalog(catalog: dict[str, list[str]]) -> None:
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def discover_models(brand_key: str) -> list[str]:
    _, _, pat = BRANDS[brand_key]
    rx = re.compile(pat, re.I)
    models: list[str] = []
    if MODELS_DIR.exists():
        for p in sorted(MODELS_DIR.glob("*.mdx")):
            mid = p.stem
            if rx.search(mid):
                models.append(mid)
    if not models:
        cat = load_catalog()
        if brand_key in cat:
            return list(cat[brand_key])
    if not models and OPS_DIR.exists():
        brand_op = OPS_DIR / f"{brand_key}.json"
        if brand_op.exists():
            op = json.loads(brand_op.read_text(encoding="utf-8"))
            enum = (
                op.get("components", {})
                .get("schemas", {})
                .get("ChatCompletionRequest", {})
                .get("properties", {})
                .get("model", {})
                .get("enum")
            )
            if enum:
                return list(enum)
    return models

def collect_refs(node: Any, found: set[str]) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            found.add(ref.split("/")[-1])
        for v in node.values():
            collect_refs(v, found)
    elif isinstance(node, list):
        for v in node:
            collect_refs(v, found)


def resolve_schema_closure(schemas: dict[str, Any], roots: list[str]) -> dict[str, Any]:
    needed: set[str] = set(roots)
    changed = True
    while changed:
        changed = False
        for name in list(needed):
            if name not in schemas:
                continue
            before = len(needed)
            collect_refs(schemas[name], needed)
            if len(needed) > before:
                changed = True
    return {n: copy.deepcopy(schemas[n]) for n in sorted(needed) if n in schemas}


def pin_models(schema: dict[str, Any], models: list[str]) -> dict[str, Any]:
    s = copy.deepcopy(schema)
    props = s.setdefault("properties", {})
    example = models[0] if models else ""
    props["model"] = {
        "type": "string",
        "description": (
            "Model id for this brand on OmniMux. Same request/response shape for all "
            "ids below; only the `model` value changes."
        ),
        "enum": models,
        "default": example,
        "example": example,
    }
    return s


def build_op(relay: dict[str, Any], brand_key: str, models: list[str]) -> dict[str, Any]:
    schemas = relay["components"]["schemas"]
    req = pin_models(schemas["ChatCompletionRequest"], models)
    brand_cn, brand_en, _ = BRANDS[brand_key]
    title = f"{brand_en} · Chat Completions"
    closed = resolve_schema_closure(
        {**schemas, "ChatCompletionRequest": req},
        ["ChatCompletionRequest", "ChatCompletionResponse", "ErrorResponse"],
    )
    closed["ChatCompletionRequest"] = req
    example_model = models[0]

    success_example = {
        "id": "chatcmpl-example",
        "object": "chat.completion",
        "created": 1741428397,
        "model": example_model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "…"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 18,
            "completion_tokens": 120,
            "total_tokens": 138,
        },
    }

    responses: dict[str, Any] = {
        "200": {
            "description": "Chat completion successful",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ChatCompletionResponse"},
                    "example": success_example,
                }
            },
        }
    }
    for code, desc in ERROR_DESCRIPTIONS.items():
        responses[code] = {
            "description": desc,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"},
                    "example": ERROR_EXAMPLES[code],
                }
            },
        }

    model_list = ", ".join(f"`{m}`" for m in models)
    return {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "description": (
                f"OpenAI-compatible Chat Completions for {brand_en} models on OmniMux. "
                f"Supported model ids: {model_list}."
            ),
            "version": "1.0.0",
        },
        "servers": [
            {
                "url": "https://api.omnimux.ai",
                "description": "OmniMux production gateway",
            }
        ],
        "security": [{"BearerAuth": []}],
        "tags": [
            {
                "name": "Chat Completion",
                "description": "OpenAI-compatible chat completions",
            }
        ],
        "paths": {
            "/v1/chat/completions": {
                "post": {
                    "tags": ["Chat Completion"],
                    "summary": f"{brand_en} Chat Completions",
                    "description": (
                        f"- Protocol: OpenAI Chat Completions\n"
                        f"- Path: `POST /v1/chat/completions`\n"
                        f"- Brand: {brand_en}\n"
                        f"- Choose model via body `model` (enum below)\n"
                        f"- Same request/response schema for all ids in this brand\n"
                        f"- Synchronous by default; `stream: true` for SSE"
                    ),
                    "operationId": f"createChatCompletion_{brand_key}",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatCompletionRequest"
                                },
                                "examples": {
                                    "simple_text": {
                                        "summary": "Single-turn text",
                                        "value": {
                                            "model": example_model,
                                            "messages": [
                                                {
                                                    "role": "user",
                                                    "content": "介绍一下人工智能的发展历史",
                                                }
                                            ],
                                        },
                                    },
                                    "system_prompt": {
                                        "summary": "System + user",
                                        "value": {
                                            "model": example_model,
                                            "messages": [
                                                {
                                                    "role": "system",
                                                    "content": "You are a concise assistant.",
                                                },
                                                {
                                                    "role": "user",
                                                    "content": "Explain streaming in one sentence.",
                                                },
                                            ],
                                        },
                                    },
                                    "streaming": {
                                        "summary": "Streaming",
                                        "value": {
                                            "model": example_model,
                                            "stream": True,
                                            "messages": [
                                                {
                                                    "role": "user",
                                                    "content": "Say hello",
                                                }
                                            ],
                                        },
                                    },
                                },
                            }
                        },
                    },
                    "responses": responses,
                }
            }
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": (
                        "API key auth. Header: `Authorization: Bearer sk-...` "
                        "(create keys in the OmniMux console)."
                    ),
                }
            },
            "schemas": closed,
        },
    }


def model_table_cn(models: list[str]) -> str:
    rows = "\n".join(f"| `{m}` |" for m in models)
    return f"""| model id |
| --- |
{rows}
"""


def model_table_en(models: list[str]) -> str:
    rows = "\n".join(f"| `{m}` |" for m in models)
    return f"""| model id |
| --- |
{rows}
"""


def render_mdx_cn(brand_key: str, models: list[str], op_rel: str) -> str:
    brand_cn, brand_en, _ = BRANDS[brand_key]
    return f"""---
title: "{brand_cn} · 完整参数"
sidebarTitle: "{brand_cn} · 完整参数"
description: "{brand_cn} · Chat Completions 完整参数（同合同，model 枚举）"
openapi: "{op_rel} POST /v1/chat/completions"
---

> - 协议：OpenAI Chat Completions（`POST /v1/chat/completions`）
> - 本页为 **{brand_cn} 共用合同**；换模型只改 body 的 `model`
> - 默认同步；`stream: true` 流式

## 可用 model

{model_table_cn(models)}

Base URL：`https://api.omnimux.ai`
"""


def render_mdx_en(brand_key: str, models: list[str], op_rel: str) -> str:
    brand_cn, brand_en, _ = BRANDS[brand_key]
    return f"""---
title: "{brand_en} · Complete API Reference"
sidebarTitle: "{brand_en} · Complete API Reference"
description: "{brand_en} · Chat Completions complete API reference (shared contract, model enum)"
openapi: "{op_rel} POST /v1/chat/completions"
---

> - Protocol: OpenAI Chat Completions (`POST /v1/chat/completions`)
> - **Shared contract** for all {brand_en} ids below; only body `model` changes
> - Synchronous by default; `stream: true` for SSE

## Available models

{model_table_en(models)}

Base URL: `https://api.omnimux.ai`
"""


def write_brand(brand_key: str, models: list[str] | None = None) -> None:
    if brand_key not in BRANDS:
        raise SystemExit(f"unknown brand {brand_key}")
    models = models or discover_models(brand_key)
    if not models:
        raise SystemExit(f"no models for brand {brand_key}")

    catalog = load_catalog()
    catalog[brand_key] = models
    save_catalog(catalog)

    relay = json.loads(RELAY.read_text(encoding="utf-8"))
    op = build_op(relay, brand_key, models)
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    op_path = OPS_DIR / f"{brand_key}.json"
    op_path.write_text(json.dumps(op, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    op_rel = f"openapi/ops/chat/{brand_key}.json"

    for loc, render in (("cn", render_mdx_cn), ("en", render_mdx_en)):
        d = ROOT / loc / "api-reference" / "text-series" / brand_key
        d.mkdir(parents=True, exist_ok=True)
        page = d / "complete.mdx"
        page.write_text(render(brand_key, models, op_rel), encoding="utf-8")
        print(f"wrote {page.relative_to(ROOT)}")
    print(f"wrote {op_path.relative_to(ROOT)} models={models}")

def remove_per_model_pages() -> None:
    """Delete per-model MDX and ops; keep brand complete ops + catalog."""
    for loc in ("cn", "en"):
        mdir = ROOT / loc / "api-reference" / "text-series" / "models"
        if not mdir.exists():
            continue
        for p in mdir.glob("*.mdx"):
            p.unlink()
            print(f"removed {p.relative_to(ROOT)}")
    if OPS_DIR.exists():
        for p in OPS_DIR.glob("*.json"):
            # keep brand ops and internal catalog
            if p.stem in BRANDS or p.name.startswith("_"):
                continue
            p.unlink()
            print(f"removed {p.relative_to(ROOT)}")

def update_docs_json() -> None:
    path = ROOT / "docs.json"
    d = json.loads(path.read_text(encoding="utf-8"))

    def brand_pages(loc: str) -> list[dict[str, Any]]:
        order = ["claude", "gemini", "gpt", "grok", "kimi", "deepseek", "minimax", "glm"]
        out = []
        labels = {
            "cn": {k: v[0] for k, v in BRANDS.items()},
            "en": {k: v[1] for k, v in BRANDS.items()},
        }
        for k in order:
            out.append(
                {
                    "group": labels[loc][k],
                    "pages": [f"{loc}/api-reference/text-series/{k}/complete"],
                }
            )
        return out

    for lang in d["navigation"]["languages"]:
        loc = "cn" if lang.get("language") == "cn" else "en"
        for tab in lang.get("tabs", []):
            if tab.get("tab") not in ("API 手册", "API manual"):
                continue
            for g in tab.get("groups", []):
                if g.get("group") not in ("语言系列", "Language series"):
                    continue
                # no series overview pages — lean nav (contract leaves only)
                g["pages"] = brand_pages(loc)
                print(f"updated {loc} language series nav", len(g["pages"]))
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brands", nargs="*", help="brand keys")
    ap.add_argument("--all-brands", action="store_true")
    ap.add_argument("--cleanup-per-model", action="store_true", help="delete old per-model pages/ops")
    ap.add_argument("--update-nav", action="store_true", help="rewrite language series in docs.json")
    args = ap.parse_args()

    if not RELAY.exists():
        raise SystemExit(f"missing {RELAY}")

    if args.all_brands:
        brands = list(BRANDS.keys())
    elif args.brands:
        brands = args.brands
    else:
        brands = []

    for b in brands:
        write_brand(b)

    if args.cleanup_per_model:
        remove_per_model_pages()
    if args.update_nav:
        update_docs_json()


if __name__ == "__main__":
    main()
