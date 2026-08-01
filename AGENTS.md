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
- **Base URL** — production default `https://api.omnimux.ai`
- Prefer **token** or **API key** for user docs; avoid internal admin jargon on public pages

## Style

- User-facing docs: Chinese under `cn/`, English under `en/`
- Active voice, second person ("you" / "你")
- Sentence case for English headings; Chinese headings keep natural phrasing
- Bold UI labels: Click **Settings**
- Code for paths, headers, model ids, and commands
- Use real product domains (`omnimux.ai`, `api.omnimux.ai`); do not default to `docs.newapi.pro` or upstream branding in user-facing copy

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
