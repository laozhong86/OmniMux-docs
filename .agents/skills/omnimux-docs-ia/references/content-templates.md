# Page shape — Evolink-class OpenAPI detail pages

Callable L3 pages **must** match Evolink interface-detail structure:

**left = OpenAPI-rendered contract tree**, **right = sticky request/response examples + Try it**.

Thin Markdown “Body tables with 5 rows” are **not** Complete alignment.

## Target structure

```text
H1 (title)
├─ P1 bullets (blockquote, 2–6)
├─ optional <Note>
├─ thin Identity table (系列 / 品牌|平台 / model|能力)  — OmniMux-only aid
├─ METHOD + path chrome + Try it   ← from OpenAPI / api frontmatter
├─ ## OpenAPI
│   ├─ Authorizations (field-level)
│   ├─ Body | Path | Query (type, required, enum, example, nested)
│   └─ Response per status (200 + errors incl. 402)
└─ right rail: multi-lang request examples + multi-status responses
```

## Frontmatter

```yaml
---
title: "<L3 name or model id>"
sidebarTitle: "<optional>"
description: "<one line>"
api: "POST https://api.omnimux.ai/v1/chat/completions"
---
```

Publishing / user APIs: real method + `https://omnimux.ai/...`.

## MDX skeleton (language Complete)

```mdx
---
title: "<model-id>"
description: "<Brand> · model `<model-id>` · Chat Completions (Complete)"
api: "POST https://api.omnimux.ai/v1/chat/completions"
---

> - OpenAI Chat Completions 兼容协议
> - 通过请求体 `model` 选择本页模型（`<model-id>`）
> - 默认同步；`stream: true` 流式
> - 完整参数见下方 OpenAPI 字段树

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 语言系列 |
| 品牌 | <Brand> |
| model | `<model-id>` |

Base URL：`https://api.omnimux.ai`

## OpenAPI

````yaml openapi/ops/chat/<model-id>.json POST /v1/chat/completions
openapi: 3.1.0
info: …
servers:
  - url: https://api.omnimux.ai
security:
  - BearerAuth: []
paths:
  /v1/chat/completions:
    post:
      …
components:
  securitySchemes:
    BearerAuth: …
  schemas: …
````
```

**Generate with:** `python3 scripts/gen-chat-capability-pages.py --models <id>`  
Do not hand-maintain the OpenAPI block.

## OpenAPI operation requirements

| Requirement | Rule |
| --- | --- |
| Single operation | Exactly one path + one method per page |
| model pin | `model` enum/default/example = page live id |
| Auth | `BearerAuth` http bearer (`sk-`) for AI/social-data |
| Body | Full gateway schema (from `openapi/relay.json` + family overlay later) |
| Examples | ≥1 request example (`simple_text`); prefer `system_prompt` / `streaming` |
| Responses | 200 + **400/401/402/403/404/429/500/502/503** with examples |
| Servers | `https://api.omnimux.ai` (or `https://omnimux.ai` for user API) |

## What replaced thin tables

| Old (P0 Markdown) | New (Evolink-class) |
| --- | --- |
| `## 鉴权` table | OpenAPI `securitySchemes` + Authorizations UI |
| `## 请求体` 5 rows | OpenAPI `requestBody.schema` field tree |
| `## 响应` 200 summary | OpenAPI `responses` schemas + examples |
| `<Panel>` only examples | Prefer OpenAPI-generated right rail; Panel only if Mintlify needs fallback **and** examples stay generator-owned |

## Panel fallback

If a surface cannot embed OpenAPI yet:

1. Record exception in skill / issue.  
2. Temporary: `<Panel>` + Request/Response with **402**.  
3. Schedule OpenAPI op in next phase — not a permanent pattern for language models.

## Social / publishing / tasks (later phases)

Same skeleton: identity (optional) + `## OpenAPI` single op.

- Social: Chat path + business top-level properties in schema.  
- Tasks: Path parameters for `task_id`.  
- Publishing: access token + `New-Api-User` security scheme; base `omnimux.ai`.

## Error catalog

- `cn|en/api-reference/errors.mdx` stays human index.  
- Schemas/examples must stay consistent with op `ErrorResponse` + 402.

## Language pair headings

| CN | EN |
| --- | --- |
| 身份 | Identity |
| OpenAPI | OpenAPI (same) |

## Quality bar (must pass)

- [ ] `## OpenAPI` present and valid OpenAPI 3.x  
- [ ] Mintlify left: Authorizations + expandable Body fields (not only Markdown tables)  
- [ ] model pin correct  
- [ ] 402 in responses  
- [ ] cn + en  
- [ ] Live model only  
- [ ] No path-as-sidebar-title  

## Deferred

- Per-model Quickstart sibling pages  
- Multi-protocol Anthropic pages until live  
- Multi-SDK tabs beyond Mintlify autogenerate  
