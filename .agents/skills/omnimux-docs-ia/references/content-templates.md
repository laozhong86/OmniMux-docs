# Page shape & right-rail examples

Evolink-class capability pages: **left = contract layers**, **right = sticky examples**.  
Desktop right rail requires `<Panel>` wrapping Request/Response examples.

## Language

- `cn/` and `en/` for every new user-facing API page.  
- Active voice; English sentence case; Chinese natural headings.  
- Code: paths, headers, model ids, commands.

## Page layers (required for callable L3)

```text
H1 (title frontmatter)
├─ P1  能力说明 bullets（2–4 条）
├─ 身份 / 定位表（系列 · 品牌/平台 · model 或能力）
├─ 接口（方法 + 路径；path 只写在正文，不写侧栏标题）
├─ P0  鉴权（Authorizations）字段表
├─ P0  请求体 Body 和/或 路径参数 Path（字段级）
├─ P0  响应 Response（200 主字段；错误见右栏 + 错误码页）
└─ <Panel> RequestExample + ResponseExample（含 402）
```

Overview / brand hub / coverage pages may omit P0 field tables when they are not callable.

## Frontmatter

```yaml
---
title: "<L3 name>"
sidebarTitle: "<optional shorter>"
description: "<one line; used in search / SEO>"
api: "POST https://api.omnimux.ai/v1/chat/completions"
---
```

- Use real method + full URL for publishing (`https://omnimux.ai/api/social/v1/...`) and tasks.  
- `api:` enables Mintlify method/path chrome + Try-it when OpenAPI matches; still required even when using Panel.

## P1 · Capability bullets (under H1)

Immediately after frontmatter (before identity table), **2–4 bullets**:

| Surface | Typical bullets |
| --- | --- |
| Language | OpenAI Chat Completions 兼容；`model` 选本页模型；默认同步；可选 `stream` |
| Image | `POST /v1/images/generations`；关键参数；异步则链任务查询 |
| Video | 创建任务 + 轮询；链 [查询视频任务](…) |
| Social data | Chat 形态 + dummy `messages`；业务字段 top-level；`sk-` |
| Publishing | access token + `New-Api-User`；资源路径 |
| Tasks | Path 参数 `task_id`；来自创建接口响应 |

Do not dump full marketing copy. Prefer modes / sync-async / auth surface / cross-links.

## P0 · Contract tables (left column)

### 鉴权（Authorizations）/ Authorizations

| 名称 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | string | 是 | `Bearer sk-...` 或用户 access token |
| `New-Api-User` | header | string | 条件 | 用户 API（发布/设备后续）必填，值为 user id |

AI + 社交数据：仅 `sk-`。社媒发布 / 部分账户：access token + `New-Api-User`。

### 请求体（Body）/ Path Parameters

Every **required** and **commonly used optional** field as a row:

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 本页 model id（固定示例值） |
| `messages` | array | 是 | OpenAI messages（社交数据可传 dummy） |
| *business* | … | 是 | 社交数据业务字段（如 `aweme_id`） |

- Type + required + short description + constraint/example when useful.  
- Social-data: elevate `主要业务字段` into Body rows (not only identity table).  
- Task GET: use **路径参数** section for `task_id` (source, format, example).

### 响应（Response）

Document **200** primary fields in a table (id / choices / data / task_id / status / …).  
Point errors to right-rail multi-status samples + [错误码](/cn/api-reference/errors) page.  
Do not re-list every error status as full tables on every model page.

## Right column (`<Panel>`)

Required for every callable surface:

```mdx
<Panel>

<RequestExample>

```bash cURL
curl --request POST \
  --url https://api.omnimux.ai/v1/chat/completions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{ ... }'
```

</RequestExample>

<ResponseExample>

```json 200
{ ... success body ... }
```

```json 400
{ "error": { "message": "...", "type": "invalid_request_error", "code": "bad_request" } }
```

```json 401
{ "error": { "message": "...", "type": "authentication_error", "code": "unauthorized" } }
```

```json 402
{ "error": { "message": "Insufficient quota. Please top up your account.", "type": "insufficient_quota", "code": "insufficient_quota" } }
```

```json 403
{ "error": { "message": "...", "type": "permission_error", "code": "forbidden" } }
```

```json 429
{ "error": { "message": "...", "type": "rate_limit_error", "code": "rate_limit_exceeded" } }
```

```json 500
{ "error": { "message": "...", "type": "server_error", "code": "internal_error" } }
```

```json 502
{ "error": { "message": "...", "type": "server_error", "code": "bad_gateway" } }
```

```json 503
{ "error": { "message": "...", "type": "server_error", "code": "service_unavailable" } }
```

</ResponseExample>

</Panel>
```

### Status set (gateway default)

| Status | When to include |
| --- | --- |
| 200 | always |
| 400 | always |
| 401 | always |
| **402** | **always on billed gateway surfaces** (quota) — P2 |
| 403 | always for model/token scope |
| 404 | path/resource resources (tasks, posts, …) |
| 429 | always |
| 500 | always |
| 502 / 503 | gateway surfaces (upstream / unavailable) |

Publishing may use `{ "success": false, "message": "..." }` shape; still include **402** when quota applies, or note account-level limits.

### Why `<Panel>`

Without `<Panel>`, Mintlify often leaves **「在此页面」TOC** on the right and dumps RequestExample **inline below**.  
`<Panel>` **replaces TOC** and pins examples on the right (desktop). Mobile: examples scroll inline.

### Do not

- Put only `## 请求示例` / `## 响应示例` + `<Tabs>` in the main column as the primary UX.  
- Use path strings as `title` / `sidebarTitle`.  
- Leave only identity + path table with **no** Authorizations/Body field rows on callable L3 pages.

## CN skeleton (language model)

```mdx
---
title: "<model-id>"
description: "<Brand> · model `<model-id>`"
api: "POST https://api.omnimux.ai/v1/chat/completions"
---

- OpenAI Chat Completions 兼容协议
- 通过请求体 `model` 选择本页模型
- 默认同步返回；可设 `stream: true` 流式输出

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 语言系列 |
| 品牌 | <Brand> |
| model | `<model-id>` |

## 接口

| 方法 | 路径 |
| --- | --- |
| `POST` | `/v1/chat/completions` |

Base URL：`https://api.omnimux.ai`

## 鉴权

| 名称 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | string | 是 | `Bearer sk-...` |

## 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 固定为 `<model-id>` |
| `messages` | array | 是 | OpenAI messages 列表 |
| `stream` | boolean | 否 | 流式 SSE |
| `temperature` | number | 否 | 采样温度 |
| `max_tokens` | integer | 否 | 最大生成 token |

## 响应

### 200

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 完成 id |
| `object` | string | `chat.completion` |
| `model` | string | 实际 model |
| `choices` | array | 生成结果 |
| `usage` | object | token 用量 |

错误形态见右栏示例与 [错误码](/cn/api-reference/errors)。

<Panel>
… RequestExample + ResponseExample（含 402）…
</Panel>
```

## CN skeleton (social-data)

- L3 title = 中文能力名；identity 含 platform + model.  
- Body **must** document business field(s) with type/required.  
- RequestExample: dummy `messages` + top-level business fields.  
- 200 content is often JSON-in-string from upstream — say so in Response table.

## EN skeleton

Mirror CN structure with English headings:

| CN | EN |
| --- | --- |
| 身份 | Identity |
| 接口 | Endpoint |
| 鉴权 | Authorizations |
| 请求体 | Body |
| 路径参数 | Path parameters |
| 响应 | Response |

## Error catalog page

- `cn|en/api-reference/errors.mdx` under Overview.  
- Keep in sync: **200 / 400 / 401 / 402 / 403 / 404 / 429 / 500 / 502 / 503**.  
- 402 = insufficient quota (insufficient_quota).

## OpenAPI pages

- Generated from `openapi/relay.json` under 附录.  
- Playground via `docs.json` `api.openapi` + optional group openapi.  
- Prefer not mixing full OpenAPI op lists into series L1 groups.  
- **Future (not required for P0)**: per-capability OpenAPI fragments for page-level Try it (Evolink-style). Hand-written P0 tables ship first.

## Coverage tiers

| Tier | Meaning | Nav |
| --- | --- | --- |
| A | Committed public | Full pages (P0+P1+P2) |
| B | Limited (CLI-primary) | Short page or overview row |
| C | Admin / console-only | State in coverage only |

## Quality bar (Evolink-class)

- [ ] P1 bullets under H1  
- [ ] P0 Authorizations + Body/Path field tables  
- [ ] P0 Response 200 field summary  
- [ ] Full curl with `--request`, `--url`, `--header`, `--data`  
- [ ] Multi-status ResponseExample including **402**  
- [ ] Business fields for social-data models  
- [ ] No competitor-only brands without live catalog rows  
- [ ] Right rail via `<Panel>` (desktop curl left ≈ >50% viewport)

## Deferred (not in default package)

- P4 sidebar METHOD badges without path titles  
- P5 language Quickstart vs Complete Reference dual pages  
- P6 per-page OpenAPI operation + Try it  
- Full multi-language SDK tabs (Python/JS…) beyond cURL  
