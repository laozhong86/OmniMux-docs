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
- Only bridge from product → docs: OpenAPI file sync + console `docs_link` setting

## Terminology

- **OmniMux** — product name (gateway + console)
- **Gateway / relay API** — user-facing AI endpoints (`/v1/...`)
- **Token / API key** — `sk-...` Bearer credential for gateway calls
- **Channel** — upstream provider connection configured by admins
- **Base URL** — production API Base URL `https://api.omnimux.ai`
- **Domains (sole primary)** — console `https://omnimux.ai`, API `https://api.omnimux.ai`, docs `https://docs.omnimux.ai`. Never document retired hosts (`*.geminix.cc`) or upstream defaults (`docs.newapi.pro`)
- Prefer **token** or **API key** for user docs; avoid internal admin jargon on public pages

## Site navigation

- Top tabs (both locales): **用户指南 / User guide** · **API 手册 / API manual** · **集成指南 / Integration guide**
- User guide: intro, quickstart, auth, Base URL, models
- API manual: overview + OpenAPI (`openapi/relay.json`)
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
- Do not document internal admin/back-office APIs on this site
- Do not invent model availability; point to `GET /v1/models` and the console
- When OpenAPI changes in the product repo, refresh `openapi/relay.json` (manual or CI)

## Local preview

```bash
npm i -g mint   # or: npx mint dev
mint dev
```

Open `http://localhost:3000`.
