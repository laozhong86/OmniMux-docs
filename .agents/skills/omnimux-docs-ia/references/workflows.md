# Workflows

## W0. Public docs gate (product + docs)

When product ships/changes **user-facing HTTP**:

1. Smoke succeeds (status + response shape evidence).  
2. Same delivery updates **OmniMux-docs** (cn + en + `docs.json` if new pages).  
3. Do not call product work “done” on code/CLI alone.

Product monorepo `AGENTS.md` should point at this skill for the how.

## W1. Add AI model (language / image / video)

1. Confirm model on live `GET /api/pricing` (or models list).  
2. Map brand → existing L2 or create brand (vendor-facing name).  
3. Create `cn|en/api-reference/{text|image|video}-series/models/<model-id>.mdx` with:
   - P1 bullets · identity · endpoint · P0 Authorizations/Body/Response tables  
   - `<Panel>` RequestExample + ResponseExample including **402**  
4. Optionally refresh `brands/<brand>.mdx` model table (deep link OK).  
5. `docs.json`: under brand **group**, append only the model path (no brand hub child).  
6. Deploy / smoke URL 200; verify right rail.

## W2. Add social-data capability

1. Confirm model + vendor platform on pricing; tags include social-data.  
2. CN L3 = capability name; EN L3 = English capability.  
3. Page under `social-data/<platform>/<slug>.mdx`; identity + **Body field rows** for business keys.  
4. RequestExample includes dummy messages + required field.  
5. Register under platform group in `docs.json`.  
6. Vendor meta on product side stays **platform brand**, not TikHub.

## W3. Add publishing endpoint

1. Path under `/api/social/v1`.  
2. Place under 连接账户 / 帖子 / 媒体 by resource.  
3. CN capability title; EN capability title; `api:` full URL on `omnimux.ai`.  
4. Auth: access token + `New-Api-User`.  
5. Panel request/response; post status **not** under 任务管理.

## W4. Add task poll helper

1. Only AI async (image/video task_id).  
2. L3 Chinese/EN capability name (查询视频任务…), paths in body.  
3. Link from image/video model pages.

## W5. Remove / hide

- Empty brand groups  
- Planned APIs without live routes  
- Stale Social Ops nav entries  
- Duplicate L2-named children  

## W6. Verify

```bash
# from OmniMux-docs
python3 -c "import json; json.load(open('docs.json'))"
# optional
npx mint dev   # or mint dev
# after deploy
curl -sS -o /dev/null -w '%{http_code}\n' https://docs.omnimux.ai/cn/api-reference/overview
```

Desktop check: example curl `getBoundingClientRect().left` should be **> 50% viewport width** (right rail), not content column only.

Callable L3 checklist: page text includes Authorizations/鉴权 + Body/请求体 (or Path) + 402 sample.

## W8. Micro-optimization (detail loop)

1. Ego or live compare vs Evolink / self when improving page shape.  
2. List gaps → **human confirm**.  
3. Update **skill** (`content-templates` / hard rules) first.  
4. Then regenerate or edit MDX.  
5. Never ship content that contradicts skill.

## W7. OpenAPI sync

```bash
python3 scripts/sync-openapi.py   # from OmniMux-docs if present
```

Source: product `docs/openapi/relay.json` → drop 未实现 tags → set servers to api.omnimux.ai.

## Branching

- Docs-only: branch on OmniMux-docs; PR to `main`; Mintlify auto-deploy.  
- Do not edit product monorepo for pure docs IA unless linking skills/AGENTS pointers.
