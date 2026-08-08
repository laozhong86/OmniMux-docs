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

## Site navigation (API manual IA)

- Top tabs (both locales): **用户指南 / User guide** · **API 手册 / API manual** · **集成指南 / Integration guide**
- User guide: intro, quickstart, auth, Base URL, models
- **API manual IA** — Evolink-style **series → brand → protocol endpoints** (gateway reality: brands share paths, differ by `model`):
  1. **Overview** + coverage (A/B/C)
  2. **Cross-cutting** — device login, async tasks
  3. **Language / Image / Video / Audio series** — series overview MDX → **brand** MDX under `*/{text,image,video}-series/brands/` → brand MDX list first; OpenAPI try-it only inside a nested `协议接口` / `Protocol endpoints` group with `expanded: false` (never flat-list POST next to brands)
  4. **Social Ops** — first-class MDX (not in relay OpenAPI)
  5. **Appendix** — OpenAPI snapshot notes only (must **not** re-attach full openapi dump as a sibling group)
- Brand lists MUST be grounded in live OmniMux catalog (`GET /api/pricing` / `GET /v1/models`), not competitor-only brand names.
- Integration guide: CLI / desktop / OpenClaw under `*/integration-guide/`
- Agents MUST add a brand page when onboarding a new product family users discover by name; nest new relay paths under the matching series group (`POST /v1/...` form).

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
- When adding a major modality or product family, add or extend the matching **series overview** under `*/api-reference/{image,video,audio}-series/` (or Social Ops) — do not leave discovery only under OpenAPI try-it

## Public API documentation gate (mandatory)

Agents working on **OmniMux product** user-facing HTTP APIs MUST treat Mintlify docs as part of the delivery:

1. **After a real smoke test succeeds** (local or production, with evidence: HTTP status + response shape), Agents MUST update this docs repo **before** calling the work complete.
2. Scope of update for a new or changed endpoint:
   - User-facing description (cn + en when both locales exist)
   - Auth mode (gateway `sk-` vs user access token)
   - Request/response fields that callers need
   - Series / Social / cross-cutting MDX when the surface is capability-shaped
   - `docs.json` navigation entry if a new page is added
   - OpenAPI sync when the path is part of the relay public surface
3. Product monorepo norms also require this close-out (see OmniMux root `AGENTS.md` → Public docs sync). Shipping code + CLI only, without docs, is **not** done.
4. Prefer linking from `api-reference/overview` and the matching series page when adding a major surface (as with Social Ops).

## Local preview

```bash
npm i -g mint   # or: npx mint dev
mint dev
```

Open `http://localhost:3000`.

## API manual IA (confirmed)

- L1: 语言系列 / 图像系列 / 视频系列 / 社交数据 / 社媒发布 / 账户管理 / 任务管理
- L2: brand (AI/social-data platforms) or resource group (连接账户 / 帖子 / 媒体)
- L3: model id (AI) or Chinese capability name (社交数据 / 社媒发布 / 任务)
- EN L2 for connect: **Connecting Accounts** (Zernio official); CN: **连接账户**
- Do **not** list empty brands, planned APIs, or use METHOD path as sidebar titles
- Social data ≠ Publishing (TikHub read vs Zernio write)
