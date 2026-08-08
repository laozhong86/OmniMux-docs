# Page shape & right-rail examples

## Language

- `cn/` and `en/` for every new user-facing API page.  
- Active voice; English sentence case; Chinese natural headings.  
- Code: paths, headers, model ids, commands.

## Capability / model page skeleton (CN)

Frontmatter (API pages that have a primary HTTP method):

```yaml
---
title: "<L3 name>"
sidebarTitle: "<optional shorter>"
description: "<one line>"
api: "POST https://api.omnimux.ai/v1/chat/completions"
---
```

Use real method/URL for publishing (`https://omnimux.ai/api/social/v1/...`) or tasks.

Body (left column — prose only):

1. Identity table (系列 / 品牌或平台 / model 或能力)  
2. 接口 table (方法 + 路径) — **human names in nav, paths here**  
3. Auth + base URL notes  
4. Optional field notes  

**Right column** (required for callable surfaces):

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

</ResponseExample>

</Panel>
```

### Why `<Panel>`

Without `<Panel>`, Mintlify often leaves **「在此页面」TOC** on the right and dumps RequestExample **inline below**.  
`<Panel>` **replaces TOC** and pins examples on the right (desktop). Mobile: examples scroll inline.

### Do not

- Put only `## 请求示例` / `## 响应示例` + `<Tabs>` in the main column as the primary UX.  
- Use path strings as `title` / `sidebarTitle`.

## Error catalog page

- `cn|en/api-reference/errors.mdx` under Overview.  
- Keep in sync with common gateway statuses (200/400/401/403/404/429/500/502/503).

## OpenAPI pages

- Generated from `openapi/relay.json` under 附录.  
- Playground via `docs.json` `api.openapi` + optional group openapi.  
- Prefer not mixing full OpenAPI op lists into series L1 groups.

## Coverage tiers

| Tier | Meaning | Nav |
| --- | --- | --- |
| A | Committed public | Full pages |
| B | Limited (CLI-primary) | Short page or overview row |
| C | Admin / console-only | State in coverage only |

## Quality bar (Evolink-class)

- Full curl with `--request`, `--url`, `--header`, `--data`  
- Multi-status response samples  
- Business fields for social-data models  
- No competitor-only brands without live catalog rows  
