# API Updates / changelog

Public developer **change timeline** for OmniMux (not a second model catalog).

| Item | Value |
| --- | --- |
| Human pages | `en/updates.mdx`, `zh/updates.mdx` (+ `updates/page-N.mdx` when paginated) |
| Data true home | `data/changelog/entries/*.json` |
| Generated feeds | `data/changelog/index.json` (meta), `data/changelog/pages/{n}.json` (bodies) |
| Generator | `python3 scripts/gen-changelog-pages.py` |
| Checker | `python3 scripts/check-changelog.py` |
| Live site | `https://docs.omnimux.ai/en/updates` · `/zh/updates` |
| Product refs (format only) | [APIMart log-updates](https://apimart.ai/zh/log-updates) · [Evolink changelog](https://evolink.ai/zh/changelog) |

## Product rules

1. **Audience**: developers integrating the gateway — not blog, not status page, not full catalog.  
2. **Shape**: **timeline by `published_at` (newest first)** — one change theme per entry.  
3. **Honesty**: only claim live OmniMux catalog / shipped public APIs. **Never** copy competitor launch dates as ours.  
4. **Title formula (Evolink-style)**:
   - zh: `新模型 | {名} — {卖点}` · `模型更新 | …` · `价格调整 | …` · `不兼容变更 | …` · `平台 | …`
   - en: `New Model | {Name} — {hook}` · `Model Update | …` · `Pricing | …` · `Breaking | …` · `Platform | …`
5. **Body formula (APIMart-style)**: short lead → **New model / What changed** (Model ID bullets or small table) → optional capabilities / migration notes → docs CTAs. Put IDs in the body — do **not** rely on generator model-id walls.  
6. **Data / page split**: edit **entries only**; never hand-edit generated `index.json`, `pages/*.json`, or updates MDX.  
7. **i18n**: every entry requires non-empty `title` / `summary` / `body` for **en** and **zh**.  
8. **Models**: `models[]` ids MUST exist on live `GET https://omnimux.ai/api/pricing` (checker enforces when network available). Prefer representative IDs for theme waves; full inventory stays on pricing.  
9. **`baseline` type**: legacy / discouraged. Do **not** add modality-wide catalog dumps. Use `model_launch` with honest “already available” wording for feed day-zero seeds, or `platform` for feed open.  
10. **Public docs gate**: when shipping user-facing model or API change, append changelog in the **same delivery window** as docs MDX/OpenAPI updates.  
11. **Human MDX**: generator intro is user-facing only (no repo paths / gen commands). Machine feeds stay in the page footer.

## Entry schema (v1)

```json
{
  "schema_version": 1,
  "id": "YYYY-MM-DD-slug",
  "published_at": "YYYY-MM-DD",
  "rank": 0,
  "type": "model_launch|capability|pricing|breaking|platform|baseline",
  "modality": ["text|image|video|audio|social-data|publishing|platform|other"],
  "title": { "en": "New Model | Name — hook", "zh": "新模型 | 名称 — 卖点" },
  "summary": { "en": "...", "zh": "..." },
  "models": ["exact-model-id"],
  "links": [
    {
      "label": { "en": "Docs", "zh": "文档" },
      "href": { "en": "/en/...", "zh": "/zh/..." }
    }
  ],
  "tags": ["optional", "tags"],
  "body": { "en": "markdown...", "zh": "markdown..." }
}
```

- `id`: lowercase slug; filename SHOULD be `{id}.json`.  
- `published_at`: calendar day of public change (ops evidence or docs merge day).  
- `rank` (optional int): higher wins when `published_at` ties (default `0`).  
- Prefer **one change theme per entry**.

## Body template (model_launch)

```markdown
**{Display name}** is now available on OmniMux.  // or: already available when this feed opened

## New model

- **Model ID:** `id-here`
- **Path / contract:** e.g. Chat Completions or `POST /v1/video/generations`
- **Highlights:** 1–3 bullets

## Key capabilities

- …

## Documentation

- Link to docs complete / model page
```

## Append workflow (Agent)

1. Confirm live: pricing and/or smoke for the surface.  
2. Update API docs as required by public docs gate.  
3. Create `data/changelog/entries/YYYY-MM-DD-slug.json`.  
4. Run:
   ```bash
   python3 scripts/gen-changelog-pages.py
   python3 scripts/check-changelog.py
   python3 scripts/check-i18n.py
   ```
5. If a new pagination page appears, ensure `docs.json` still points at `en/updates` / `zh/updates` (page-1); archive pages are linked from MDX.  
6. Commit entries + generated artifacts together.  
7. Optional: Discord `#changelog` short summary (ops skill) — not a substitute for this feed.

## Caching / consumers

| File | Use |
| --- | --- |
| `index.json` | Lightweight list (id, date, type, titles, summaries, models) — prefer for menus / “latest” widgets |
| `pages/n.json` | Full markdown bodies for one page — lazy-load when rendering detail |
| MDX pages | SEO + default human reading on Mintlify CDN |

Do not introduce a production DB `/api/changelog` unless product explicitly approves core work. Static files are the v1 contract.

## Out of scope

- Status / incident posts (`status.omnimux.ai`)  
- Internal ops notes, channel keys, admin-only surfaces  
- Inventing models not on live pricing  
- Competitor launch calendars as our dates  
- Hand-written updates MDX that bypasses the generator  
- Full catalog dumps on the human page (use pricing / model square)  
