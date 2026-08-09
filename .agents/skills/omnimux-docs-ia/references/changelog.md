# API Updates / changelog

Public developer **change timeline** for OmniMux, rendered with Mintlify’s official **`<Update>`** changelog layout (same pattern as [mintlify.com/docs/changelog](https://www.mintlify.com/docs/changelog)).

| Item | Value |
| --- | --- |
| Human pages | `en/updates.mdx`, `zh/updates.mdx` |
| Layout | Mintlify [`Update`](https://www.mintlify.com/docs/components/update) components; guide: [Changelogs](https://www.mintlify.com/docs/create/changelogs) |
| Data true home | `data/changelog/entries/*.json` |
| Generated feeds | `data/changelog/index.json`, `data/changelog/pages/{n}.json` |
| Generator | `python3 scripts/gen-changelog-pages.py` |
| Checker | `python3 scripts/check-changelog.py` |
| Live | `https://docs.omnimux.ai/en/updates` · `/zh/updates` |
| Content refs (dates/copy style) | [APIMart log-updates](https://apimart.ai/zh/log-updates) · [Evolink changelog](https://evolink.ai/zh/changelog) |

## Product rules

1. **Audience**: developers — not blog, not status, not full catalog.  
2. **Shape**: **one change per entry**, sorted by `published_at` desc (timeline).  
3. **Layout**: generator emits stacked `<Update label tags rss>` blocks (not hand-written `### date` dumps).  
4. **Honesty**: only models on live OmniMux pricing. Never invent IDs. Peer gateway public dates may seed **historical** timeline fill for models we actually carry; **new** entries must use our own ship day.  
5. **Title / rss**: short product line (Evolink-style substance). Body: APIMart-style Model ID + path + highlights.  
6. **i18n**: `title` / `summary` / `body` required for **en** and **zh**.  
7. **`models[]`**: must exist on `GET https://omnimux.ai/api/pricing` when checker has network.  
8. **No catalog dumps**: do not pack an entire modality into one “already available” mega-entry.  
9. **Edit entries only**; never hand-edit generated MDX / `index.json` / `pages/*.json`.  
10. **Public docs gate**: ship user-facing model/API change → append entry same window as docs.

## Mintlify `<Update>` contract (generated)

```mdx
---
title: "API Updates"   # zh: API 更新
description: "..."
rss: true
---

Short intro…

<a id="YYYY-MM-DD-slug"></a>

<Update label="August 7, 2026" tags={["New models", "Video"]} rss={{ title: "Seedance 2.5 — …" }}>

  ## Seedance 2.5

  …

</Update>
```

| Prop | Source |
| --- | --- |
| `label` | `published_at` → en `August 7, 2026` / zh `2026 年 8 月 7 日` |
| `tags` | type chip + modality chip (right-rail filters) |
| `rss.title` | `title[locale]` |
| children | `body[locale]` + links |

## Entry schema (v1)

```json
{
  "schema_version": 1,
  "id": "YYYY-MM-DD-slug",
  "published_at": "YYYY-MM-DD",
  "rank": 0,
  "type": "model_launch|capability|pricing|breaking|platform|baseline",
  "modality": ["text|image|video|audio|social-data|publishing|platform|other"],
  "title": { "en": "…", "zh": "…" },
  "summary": { "en": "…", "zh": "…" },
  "models": ["exact-model-id"],
  "links": [
    {
      "label": { "en": "Docs", "zh": "文档" },
      "href": { "en": "/en/...", "zh": "/zh/..." }
    }
  ],
  "tags": ["optional-internal"],
  "body": { "en": "markdown…", "zh": "markdown…" }
}
```

## Body template (model_launch)

```markdown
## {Display name}

**{Name}** is now available on OmniMux.

### New model

- **Model ID:** `id`
- **API:** Chat Completions or `POST /v1/video/generations`
- **Highlights:** …

(generator appends ### Links from `links[]`)
```

## Append workflow

1. Live pricing / smoke.  
2. Docs pages as required.  
3. Add `data/changelog/entries/YYYY-MM-DD-slug.json`.  
4. `python3 scripts/gen-changelog-pages.py && python3 scripts/check-changelog.py && python3 scripts/check-i18n.py`  
5. Commit entries + generated artifacts together.

## Out of scope

- Status incidents (`status.omnimux.ai`)  
- Competitor pricing numbers / promo copy  
- Models not on live pricing  
- Hand-edited updates MDX  
