#!/usr/bin/env python3
"""Generate Evolink-class chat capability pages from openapi/relay.json.

Phase 0+: single-operation OpenAPI embedded in MDX (Mintlify renders
Authorizations / Body field tree / Response + Try it + right-rail examples).

Usage (from OmniMux-docs root):
  python3 scripts/gen-chat-capability-pages.py --models gpt-5.4
  python3 scripts/gen-chat-capability-pages.py --all-text   # later: all text models
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

BRAND_RULES = [
    (r"^claude", "Claude"),
    (r"^gpt-", "GPT"),
    (r"^o[1-9]", "GPT"),
    (r"^gemini", "Gemini"),
    (r"^grok", "Grok"),
    (r"^kimi|^moonshot", "Kimi"),
    (r"^deepseek", "DeepSeek"),
    (r"^minimax", "MiniMax"),
    (r"^glm", "GLM"),
]

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


def brand_for(model: str) -> str:
    for pat, name in BRAND_RULES:
        if re.search(pat, model, re.I):
            return name
    return model.split("-")[0].title()


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
    out = {}
    for name in sorted(needed):
        if name in schemas:
            out[name] = copy.deepcopy(schemas[name])
    return out


def pin_model(schema: dict[str, Any], model: str) -> dict[str, Any]:
    s = copy.deepcopy(schema)
    props = s.setdefault("properties", {})
    props["model"] = {
        "type": "string",
        "description": f"Model id. This page pins `{model}`.",
        "enum": [model],
        "default": model,
        "example": model,
    }
    return s


def build_op(relay: dict[str, Any], model: str) -> dict[str, Any]:
    schemas = relay["components"]["schemas"]
    req = pin_model(schemas["ChatCompletionRequest"], model)
    brand = brand_for(model)
    title = f"{model} · Chat Completions"
    closed = resolve_schema_closure(
        {**schemas, "ChatCompletionRequest": req},
        ["ChatCompletionRequest", "ChatCompletionResponse", "ErrorResponse"],
    )
    closed["ChatCompletionRequest"] = req

    success_example = {
        "id": "chatcmpl-example",
        "object": "chat.completion",
        "created": 1741428397,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "…",
                },
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

    return {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "description": (
                f"OpenAI-compatible Chat Completions for `{model}` ({brand}) on OmniMux gateway."
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
                    "summary": f"{model} Chat Completions",
                    "description": (
                        f"- OpenAI Chat Completions protocol\n"
                        f"- Select model via body `model` = `{model}`\n"
                        f"- Synchronous by default; set `stream: true` for SSE\n"
                        f"- Multimodal / tools fields per gateway schema when supported"
                    ),
                    "operationId": f"createChatCompletion_{re.sub(r'[^a-zA-Z0-9_]', '_', model)}",
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
                                            "model": model,
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
                                            "model": model,
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
                                            "model": model,
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


def render_mdx_cn(model: str, brand: str, op_rel: str) -> str:
    """Mintlify renders Authorizations/Body/Response when openapi is in frontmatter.

    Do NOT embed raw OpenAPI YAML under ## OpenAPI — that dumps as a code block.
    Format: openapi: \"path/to/spec.json METHOD /path\"
    See: https://www.mintlify.com/docs/api-playground/openapi-setup
    """
    return f"""---
title: "{model}"
description: "{brand} · model `{model}` · Chat Completions (Complete)"
openapi: "{op_rel} POST /v1/chat/completions"
---

> - OpenAI Chat Completions 兼容协议
> - 通过请求体 `model` 选择本页模型（`{model}`）
> - 默认同步返回；可设 `stream: true` 流式输出
> - 下方为 Mintlify 渲染的 Authorizations / Body / Response（对齐 Evolink 布局）

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 语言系列 |
| 品牌 | {brand} |
| model | `{model}` |

Base URL：`https://api.omnimux.ai`
"""


def render_mdx_en(model: str, brand: str, op_rel: str) -> str:
    return f"""---
title: "{model}"
description: "{brand} · model `{model}` · Chat Completions (Complete)"
openapi: "{op_rel} POST /v1/chat/completions"
---

> - OpenAI Chat Completions compatible
> - Select this page's model via body `model` (`{model}`)
> - Synchronous by default; set `stream: true` for SSE
> - Below: Mintlify-rendered Authorizations / Body / Response (Evolink-class layout)

## Identity

| Field | Value |
| --- | --- |
| Series | Language series |
| Brand | {brand} |
| model | `{model}` |

Base URL: `https://api.omnimux.ai`
"""


def list_text_models() -> list[str]:
    d = ROOT / "cn" / "api-reference" / "text-series" / "models"
    return sorted(p.stem for p in d.glob("*.mdx"))


def write_model(model: str) -> None:
    relay = json.loads(RELAY.read_text(encoding="utf-8"))
    op = build_op(relay, model)
    brand = brand_for(model)
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    safe = model.replace("/", "_")
    op_path = OPS_DIR / f"{safe}.json"
    op_path.write_text(json.dumps(op, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    op_rel = f"openapi/ops/chat/{safe}.json"

    cn = ROOT / "cn" / "api-reference" / "text-series" / "models" / f"{safe}.mdx"
    en = ROOT / "en" / "api-reference" / "text-series" / "models" / f"{safe}.mdx"
    cn.write_text(render_mdx_cn(model, brand, op_rel), encoding="utf-8")
    en.write_text(render_mdx_en(model, brand, op_rel), encoding="utf-8")
    print(f"wrote {op_path.relative_to(ROOT)}")
    print(f"wrote {cn.relative_to(ROOT)}")
    print(f"wrote {en.relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", help="model ids")
    ap.add_argument("--all-text", action="store_true")
    args = ap.parse_args()
    if args.all_text:
        models = list_text_models()
    elif args.models:
        models = args.models
    else:
        raise SystemExit("pass --models … or --all-text")
    if not RELAY.exists():
        raise SystemExit(f"missing {RELAY}")
    for m in models:
        write_model(m)


if __name__ == "__main__":
    main()
