# Page shape — Evolink-class layout (Mintlify OpenAPI frontmatter)

**Task done only when** live pages match Evolink structure/layout:

- Left: **Authorizations → Body (field tree) → Response** (Mintlify-rendered, not Markdown dump)
- Right: sticky request examples + multi-status responses + Try it
- **No** raw `openapi: 3.1.0` / full YAML source visible as the main content

## Correct Mintlify wiring

```yaml
---
title: "<model-id>"
description: "…"
openapi: "openapi/ops/chat/<model-id>.json POST /v1/chat/completions"
---
```

- Spec file path **must** be included when many ops share the same METHOD+path.  
- Official docs: [OpenAPI setup — Create MDX pages](https://www.mintlify.com/docs/api-playground/openapi-setup)  
- Optional prose above auto block: bullets + thin identity table only.

## Forbidden (causes “越改越乱”)

```mdx
## OpenAPI
````yaml …
openapi: 3.1.0
paths: …
````
```

That renders as a **code dump**, not Authorizations/Body UI.

Also avoid dual `api:` + giant hand-written Panel as the only contract once OpenAPI frontmatter works.

## Target structure (acceptance)

```text
H1 title
├─ bullets (2–6)
├─ optional Note
├─ thin Identity (OmniMux)
├─ METHOD + path chrome + Try it     ← from openapi frontmatter
├─ Authorizations (field-level)      ← Mintlify
├─ Body | Path | Query field tree    ← Mintlify
├─ Response statuses + field tree    ← Mintlify
└─ right rail: examples + errors
```

## Ego acceptance checklist (must all pass)

On a sample page (e.g. `claude-fable-5`):

- [ ] `hasRawOpenapi === false` (no visible `openapi: 3.1.0` wall)
- [ ] Headings include Authorizations (or 鉴权 equivalent via OpenAPI UI)
- [ ] Body field anchors exist (`body-model`, `body-messages`, …) **or** equivalent expandable param rows
- [ ] sticky curl / Try it present
- [ ] 402 appears in error examples when billed
- [ ] Compared to Evolink Complete: same **layers**, not same competitor copy

## Generator

```bash
python3 scripts/gen-chat-capability-pages.py --models claude-fable-5
python3 scripts/gen-chat-capability-pages.py --all-text
```

Writes `openapi/ops/chat/*.json` + short MDX with `openapi:` frontmatter only.

## Social / image / video (later)

Same frontmatter pattern pointing at surface-specific ops files.
