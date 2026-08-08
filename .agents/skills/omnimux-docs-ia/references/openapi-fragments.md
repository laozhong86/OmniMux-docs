# OpenAPI ops & generators

## Why

Mintlify renders Evolink-class **Authorizations / Body / Response** only when the page uses:

```yaml
openapi: "openapi/ops/…/file.json METHOD /path"
```

Embedding a full OpenAPI document under `## OpenAPI` as a code fence **fails** (raw YAML wall).

## Layout

```text
openapi/
  relay.json                 # appendix / full snapshot
  ops/
    chat/<brand>.json        # brand × Chat Completions; model.enum = live ids
```

## Chat generator (contract axis)

```bash
python3 scripts/gen-chat-capability-pages.py --all-brands --cleanup-per-model --update-nav
python3 scripts/gen-chat-capability-pages.py --brands claude
```

MDX: `text-series/<brand>/complete.mdx` (bullets + model table).  
UI: frontmatter `openapi:` → ops JSON.

## Field sources

1. `openapi/relay.json` schemas (gateway truth)  
2. Live pricing model ids  
3. Evolink only for **layout** comparison — not BaseURL/credits/unexposed fields  

## Validation

- [ ] ops JSON parses  
- [ ] MDX has `openapi:` frontmatter with **file path + METHOD + path**  
- [ ] MDX does **not** contain fenced `openapi: 3.1.0` dump  
- [ ] Live ego: no raw spec wall; field UI present  

## Task completion gate

Work is incomplete until live sample pages pass the ego acceptance checklist in `content-templates.md`.
