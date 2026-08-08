# OmniMux Docs — Agent instructions

## About this project

- Documentation site for **OmniMux**, built on [Mintlify](https://mintlify.com)
- Pages are MDX with YAML frontmatter
- Site config: `docs.json`
- Gateway OpenAPI snapshot: `openapi/relay.json` (synced from the product repo `docs/openapi/relay.json`)
- Do **not** publish admin OpenAPI (`api.json`) on this public site

## Repo boundary

- This repository is **isolated** from the OmniMux product monorepo
- Local clone should live as a **sibling** directory, e.g. `~/Desktop/Project/OmniMux-docs`
- Product code, Docker, and fork-sync stay in the OmniMux product repo
- Bridges from product → docs:
  - OpenAPI file sync for AI relay (`openapi/relay.json`)
  - **Manual MDX for non-OpenAPI user APIs** (e.g. Social Ops under `*/api-reference/social-ops.mdx`)
  - console `docs_link` setting

## Terminology

- **OmniMux** — product name (gateway + console)
- **Gateway / relay API** — user-facing AI endpoints (`/v1/...` on `api.omnimux.ai`)
- **Token / API key (`sk-...`)** — Bearer credential for **gateway** calls only
- **User access token** — console/CLI credential for **user APIs** such as Social Ops (`Authorization` + `New-Api-User`)
- **Social Ops** — multi-platform connect/publish API at `https://omnimux.ai/api/social/v1` (not model-square, not `sk-`)
- **Channel** — upstream provider connection configured by admins
- **Base URL (AI)** — production API Base URL `https://api.omnimux.ai`
- **Domains (sole primary)** — console `https://omnimux.ai`, API `https://api.omnimux.ai`, docs `https://docs.omnimux.ai`. Never document retired hosts (`*.geminix.cc`) or upstream defaults (`docs.newapi.pro`)
- Prefer **token** or **API key** for gateway docs; name **access token** when documenting Social Ops / CLI login

## Site navigation

- Top tabs (both locales): **用户指南 / User guide** · **API 手册 / API manual** · **集成指南 / Integration guide**
- User guide: intro, quickstart, auth, Base URL, models
- API manual: overview · **Social Ops** · OpenAPI (`openapi/relay.json`)
- Integration guide: CLI / desktop / OpenClaw client pages under `*/integration-guide/`

## Style

- User-facing docs: Chinese under `cn/`, English under `en/`
- Active voice, second person ("you" / "你")
- Sentence case for English headings; Chinese headings keep natural phrasing
- Bold UI labels: Click **Settings**
- Code for paths, headers, model ids, and commands
- Use sole primary product domains (`omnimux.ai`, `api.omnimux.ai`, `docs.omnimux.ai`); never dual-list retired domains

## Content boundaries

- Document gateway usage for developers and integrators
- Document **user-facing** Social Ops HTTP APIs (bind, media, posts) when they ship
- Do not document internal admin/back-office APIs on this site
- Do not invent model availability; point to `GET /v1/models` and the console
- When OpenAPI changes in the product repo, refresh `openapi/relay.json` (manual or CI)
- When product adds/changes **non-OpenAPI user APIs** (Social Ops, device login user endpoints used by CLI, etc.), update the matching MDX pages in **both** `cn/` and `en/` and register them in `docs.json` in the **same** docs change set

## Public API documentation gate (mandatory)

Agents working on **OmniMux product** user-facing HTTP APIs MUST treat Mintlify docs as part of the delivery:

1. **After a real smoke test succeeds** (local or production, with evidence: HTTP status + response shape), Agents MUST update this docs repo **before** calling the work complete.
2. Scope of update for a new or changed endpoint:
   - User-facing description (cn + en when both locales exist)
   - Auth mode (gateway `sk-` vs user access token)
   - Request/response fields that callers need
   - `docs.json` navigation entry if a new page is added
3. Product monorepo norms also require this close-out (see OmniMux root `AGENTS.md` → Public docs sync). Shipping code + CLI only, without docs, is **not** done.
4. Prefer linking from `api-reference/overview` when adding a major surface (as with Social Ops).

## Local preview

```bash
npm i -g mint   # or: npx mint dev
mint dev
```

Open `http://localhost:3000`.
