# Workflows

## W0. Public docs gate (product + docs)

When product ships/changes **user-facing HTTP**:

1. Smoke succeeds.  
2. Update **OmniMux-docs** (cn + en + `docs.json` if new).  
3. Callable L3 uses **OpenAPI operation** page shape (not thin tables only).

## W1. Add AI language model (same Chat contract)

1. Confirm live on `GET /api/pricing`.  
2. Add model id to brand enum by ensuring discovery list (filename under models archive **or** update brand catalog in generator) then:
   ```bash
   python3 scripts/gen-chat-capability-pages.py --brands <brand>
   ```
3. Do **not** add a new nav leaf per model.  
4. Smoke brand complete URL; ego: Authorizations/Body + model enum includes new id.

## W1b. Regen all language brand contracts

```bash
python3 scripts/gen-chat-capability-pages.py --all-brands --cleanup-per-model --update-nav
```

## W1c. New protocol under same brand

If path/schema differs (e.g. `/v1/messages`), add a **second** contract page under the brand — not a per-model page.

## W2. Add social-data capability

1. Live model + platform vendor.  
2. CN capability title / EN title.  
3. OpenAPI op (chat-wrapper + business fields) — Phase 3 generator; until then temporary Panel is technical debt.  
4. Register under platform group.

## W3. Publishing endpoint

User API on `omnimux.ai`; access token + `New-Api-User`. OpenAPI op Phase 3.

## W4. Task poll

Path-param OpenAPI for `task_id`. Link from image/video create pages.

## W5. Remove / hide

Empty brands, planned APIs, Social Ops names, L2-duplicate children.

## W6. Verify

```bash
python3 -c "import json; json.load(open('docs.json'))"
python3 -c "import json; json.load(open('openapi/ops/chat/gpt-5.4.json'))"
# after deploy
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://docs.omnimux.ai/cn/api-reference/text-series/models/gpt-5.4
```

Ego checklist:

- [ ] Authorizations section  
- [ ] Body fields expandable (model, messages, stream, …)  
- [ ] Response statuses include 402  
- [ ] Right sticky request example  
- [ ] Not “only 5-row Markdown Body”

## W7. OpenAPI relay sync

```bash
python3 scripts/sync-openapi.py
# then regenerate affected ops
python3 scripts/gen-chat-capability-pages.py --models …
```

## W8. Micro-optimization loop

1. Compare Evolink / live.  
2. Human confirm.  
3. **Skill first**.  
4. Regen content.  

## W9. Family overlay / field matrix change

1. Update `references/field-matrix.md` + generator.  
2. Regen all models in family.  
3. Do not hand-patch one MDX OpenAPI block.

## Branching

- Docs: feature branch → PR → Mintlify deploy.  
- Phase branches: `docs/evolink-detail-align-phaseN`.
