---
name: omnimux-docs-ia
description: "OmniMux public Mintlify docs (OmniMux-docs) API 手册 IA and content norms. Use when adding/changing docs.omnimux.ai API pages, docs.json navigation, model/brand/series pages, OpenAPI capability detail pages, 社交数据/社媒发布/账户/任务 docs, RequestExample/ResponseExample/Panel, or after shipping user-facing HTTP APIs (public docs gate). Triggers: omnimux docs, Mintlify, API 手册, OpenAPI operation, series brand model, 连接账户, Connecting Accounts. Not for: product Go/relay implementation (use newapi / deploy-vps); admin OpenAPI; inventing models not on live pricing."
---

# omnimux-docs-ia

Public documentation for **OmniMux** lives in the **sibling repo** `OmniMux-docs` (Mintlify → `https://docs.omnimux.ai`).  
This skill is the standing instruction set for **API 手册** architecture and page authoring.

## Load map (layered)

| Layer | File | When to read |
| --- | --- | --- |
| **L0 Always** | This `SKILL.md` | Every invocation |
| **L1 IA** | `references/ia-layers.md` | Any nav / new series / brand / L3 |
| **L2 Naming** | `references/naming.md` | Titles, 社媒 vs 账户, Zernio/TikHub terms |
| **L3 Page shape** | `references/content-templates.md` | Callable detail page = OpenAPI operation |
| **L4 OpenAPI fragments** | `references/openapi-fragments.md` | Generators, ops JSON, field sources |
| **L5 Field matrix** | `references/field-matrix.md` | Family field baselines |
| **L6 Workflows** | `references/workflows.md` | Add model / smoke→docs / align phases |

Do **not** invent parallel IA. Live site + `docs.json` + this skill are the source of truth.

## Repo paths

| Item | Path |
| --- | --- |
| Docs repo (edit here) | sibling `OmniMux-docs` |
| Nav | `docs.json` |
| Locales | `cn/**`, `en/**` |
| Gateway OpenAPI snapshot | `openapi/relay.json` (附录 try-it) |
| Per-capability ops | `openapi/ops/**` (single operation docs) |
| Generators | `scripts/gen-chat-capability-pages.py` (more surfaces later) |

## Hard rules (summary)

1. **IA**: L1 series/management → L2 brand or resource group → L3 model id **or** Chinese capability name.  
2. **No METHOD paths as sidebar titles** (`GET /v1/...` only in body / OpenAPI chrome / right rail).  
3. **No empty brands / planned-only APIs** in nav. Ground AI/social-data L3 in live `GET /api/pricing`.  
4. **社交数据 ≠ 社媒发布**: TikHub **read** (`sk-` Chat) vs Zernio-path **publish** (access token + `New-Api-User`).  
5. **连接账户** (CN) = **Connecting Accounts** (EN).  
6. **No duplicate L2 name under L2**.  
6b. **Lean nav**: do not show meta 概览 (API 手册概览 / 文档覆盖说明 / 错误码 group). Errors live on capability Response tabs. Prefer thin, callable paths only.  
7. **Callable L3 contract = Mintlify `openapi` frontmatter** pointing at `openapi/ops/**` single-operation file (`openapi: "path/to/op.json METHOD /path"`). Mintlify must render **Authorizations / Body field tree / Response** + right-rail Try it (Evolink layout).  
8. **Forbidden**: embedding full OpenAPI YAML/JSON under `## OpenAPI` as a code fence (renders as source dump — “越改越乱”).  
9. **Forbidden as sole contract**: identity + 5-row Markdown Body only.  
10. **Optional thin identity table** above the auto API block.  
11. **Capability bullets** under H1: 2–6.  
12. **402** on billed ops.  
13. **model pin** in ops JSON.  
14. **Field honesty** from `openapi/relay.json` / live.  
15. **Domains only**: `omnimux.ai` / `api.omnimux.ai` / `docs.omnimux.ai`.  
16. **Public docs gate** after smoke.  
17. **Skill first**, then regen.  
18. **cn + en**.  
19. **Task completion gate**: live ego must show Evolink-class layers (no raw openapi wall; Authorizations/Body UI). Until then the layout-align task is **not done**.

## Default procedure (short)

1. Confirm surface + live catalog.  
2. Load L1–L6 references as needed.  
3. Prefer **generator** (`scripts/gen-*.py`) over hand-written MDX bodies.  
4. Register L3 only under L2 in `docs.json`.  
5. Verify: OpenAPI parses; left field tree; Try it / right examples; 402; model pin.  
6. Skill change before bulk regen if norms shift.

## Alignment phases (standing)

| Phase | Scope |
| --- | --- |
| **0** | Skill + chat generator + probe model(s) OpenAPI pages — **done** |
| **1** | All language models Complete — **done** (gen-chat `--all-text`) |
| **2** | Image / video / tasks |
| **3** | Social data / publishing / account |
| **4** | Quickstart optional; retire thin-table generators |

## Out of scope

- Relay/channel product code (`newapi` / `runninghub-omnimux`).  
- Admin OpenAPI.  
- Empty audio/file L1 shells.  
- Anthropic-native pages until gateway publicly documents them.
