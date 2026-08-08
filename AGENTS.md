# OmniMux Docs — Agent instructions

## About

- Public docs for **OmniMux** (Mintlify) → `https://docs.omnimux.ai`
- Config: `docs.json` · Locales: `cn/`, `en/` · Gateway OpenAPI: `openapi/relay.json` only (never admin `api.json`)

## Repo boundary

- Isolated sibling of the product monorepo (e.g. `~/Desktop/Project/OmniMux-docs`)
- Bridges: OpenAPI sync; manual MDX for non-relay user APIs; console `docs_link`

## API 手册 — load skill (mandatory for nav/content)

For **any** API manual / `docs.json` / series-brand-model / 社交数据 / 社媒发布 / account-task docs / right-rail examples / public docs gate after API smoke:

→ Load skill **`omnimux-docs-ia`**  
  Path: `.agents/skills/omnimux-docs-ia/SKILL.md`  
  Then load `references/ia-layers.md`, `naming.md`, `content-templates.md`, `workflows.md` as needed.

Do **not** invent IA. Do **not** follow stale chat memory over that skill.

## Hard gates

1. User-facing API smoke → docs update (cn+en + nav) before work is “done”.  
2. Domains only: `omnimux.ai`, `api.omnimux.ai`, `docs.omnimux.ai`.  
3. No METHOD-path sidebar titles; no empty brands; no planned-only nav.  
4. 连接账户 = Connecting Accounts; 社交数据 ≠ 社媒发布; never L1 name “Social Ops”.  
5. Right-rail examples: `<Panel>` + `<RequestExample>` + `<ResponseExample>`.

## Terminology (minimal)

| Term | Meaning |
| --- | --- |
| `sk-` | Gateway Bearer only |
| access token + `New-Api-User` | User APIs (publishing, device login follow-up) |
| 社交数据 | TikHub-backed read models on `/v1/chat/completions` |
| 社媒发布 | `/api/social/v1` connect / posts / media |

## Style

- cn/ + en/ · active voice · product domains only · no dual retired hosts

## Local preview

```bash
npx mint dev
# http://localhost:3000
```

## Ops notes

- Human ops checklist: `OPS.md`
- OpenAPI sync helper: `scripts/sync-openapi.py` (when present)
