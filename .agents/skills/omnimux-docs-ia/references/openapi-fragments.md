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
    chat/<model-id>.json     # single POST /v1/chat/completions, model pinned
```

## Chat generator

```bash
python3 scripts/gen-chat-capability-pages.py --models <id>
python3 scripts/gen-chat-capability-pages.py --all-text
```

MDX body is short (bullets + identity). Contract UI is 100% from the ops JSON via frontmatter.

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
