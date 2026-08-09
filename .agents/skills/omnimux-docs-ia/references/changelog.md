# API Updates / changelog

Public developer change feed for OmniMux.

| Item | Value |
| --- | --- |
| Human pages | `en/updates.mdx`, `zh/updates.mdx` (+ `updates/page-N.mdx` when paginated) |
| Data true home | `data/changelog/entries/*.json` |
| Generated feeds | `data/changelog/index.json` (meta), `data/changelog/pages/{n}.json` (bodies) |
| Generator | `python3 scripts/gen-changelog-pages.py` |
| Checker | `python3 scripts/check-changelog.py` |
| Live site | `https://docs.omnimux.ai/en/updates` · `/zh/updates` |

## Product rules

1. **Audience**: developers integrating the gateway — not blog, not status page.  
2. **Honesty**: only claim live OmniMux catalog / shipped public APIs. Never copy competitor launch dates as ours.  
3. **Baseline**: type `baseline` is for catalog snapshots (e.g. feed day-zero). Real subsequent changes use other types.  
4. **Data / page split**: edit **entries only**; never hand-edit generated `index.json`, `pages/*.json`, or updates MDX.  
5. **i18n**: every entry requires non-empty `title` / `summary` / `body` for **en** and **zh**.  
6. **Models**: `models[]` ids MUST exist on live `GET https://omnimux.ai/api/pricing` (checker enforces when network available).  
7. **Public docs gate**: when shipping user-facing model or API change, append changelog in the **same delivery window** as docs MDX/OpenAPI updates.

## Entry schema (v1)

```json
{
  "schema_version": 1,
  "id": "YYYY-MM-DD-slug",
  "published_at": "YYYY-MM-DD",
  "rank": 0,
  "type": "model_launch|capability|pricing|breaking|platform|baseline",
  "modality": ["text|image|video|audio|social-data|publishing|platform|other"],
  "title": { "en": "...", "zh": "..." },
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
- Prefer **one change theme per entry**; do not dump the entire catalog except `baseline`.

## Body template (model_launch)

```markdown
Short launch sentence with **model display name**.

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
5. If new pagination page appears, ensure `docs.json` still points at `en/updates` / `zh/updates` (page-1); archive pages are linked from MDX.  
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
- Hand-written updates MDX that bypasses the generator  
