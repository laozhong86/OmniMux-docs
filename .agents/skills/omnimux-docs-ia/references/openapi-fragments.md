# OpenAPI ops & generators

## Why

Evolink detail pages are **one OpenAPI operation per capability**.  
OmniMux matches that with `openapi/ops/**` + MDX `## OpenAPI` embed.

## Layout

```text
openapi/
  relay.json                 # full gateway snapshot (附录 try-it)
  ops/
    chat/<model-id>.json     # single POST /v1/chat/completions pinned to model
    image/                   # phase 2
    video/                   # phase 2
    social/                  # phase 3
    tasks/                   # phase 2
    publishing/              # phase 3
```

## Chat generator (Phase 0/1)

```bash
# from OmniMux-docs root
python3 scripts/gen-chat-capability-pages.py --models gpt-5.4
python3 scripts/gen-chat-capability-pages.py --all-text   # phase 1 bulk
```

**Sources (priority):**

1. `openapi/relay.json` components (`ChatCompletionRequest`, `Message`, …) — **gateway truth**  
2. Live pricing model list — which ids get pages  
3. Evolink same-id pages — structure/example naming only; **do not copy** BaseURL/credits/unexposed fields  

**Pinning:** overwrites `model` property to enum/default/example = page id.

**Errors:** inject 400–503 examples including **402**.

## MDX fence format

```mdx
## OpenAPI

````yaml openapi/ops/chat/<model-id>.json POST /v1/chat/completions
openapi: 3.1.0
…
````
```

- First line after fence: meta path + METHOD + path (Evolink-compatible).  
- Body: full OpenAPI document (YAML preferred; JSON if PyYAML unavailable).  
- Prefer regenerating from `ops/*.json` rather than editing MDX OpenAPI by hand.

## Hand-edit policy

| Allowed | Forbidden |
| --- | --- |
| Generator + family overlay config | Hand-editing only one locale’s OpenAPI block |
| Fixing relay.json upstream then regen | Inventing fields not in gateway schema |
| Identity bullets in MDX above OpenAPI | Dual contract (Markdown Body table **and** OpenAPI) long-term |

## Family overlays (Phase 1+)

Future: `openapi/fragments/chat/families/*.yaml` merge extra descriptions/enums.  
Until overlays exist, **relay schema = Complete baseline** (already richer than old 5-row tables).

## Validation checklist

- [ ] `json.load` / YAML parse succeeds  
- [ ] Exactly one path key and one method  
- [ ] `components.securitySchemes` present  
- [ ] `model` enum contains page id  
- [ ] responses include `402` for billed surfaces  
- [ ] cn and en MDX both regenerated  

## Sync relay

```bash
python3 scripts/sync-openapi.py
```

Then regenerate affected ops pages.
