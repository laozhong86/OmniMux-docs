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
| Gateway OpenAPI snapshot | `openapi/relay.json` (generator source only; **not** sidebar dump) |
| Per-capability ops | `openapi/ops/**` (single operation docs) |
| Generators | `scripts/gen-chat-capability-pages.py` (more surfaces later) |

## Hard rules (summary)

1. **IA**: L1 series → L2 brand/resource → L3 **call contract** (not default per-model).  
2. **Paging axis**: page = auth + method + path + schema. **`model` is enum inside the page.** Same brand + same Chat Completions shape → **one** Complete page. Split only for different protocol/path/shape.  
3. **Language series**: `text-series/<brand>/complete` + `openapi/ops/chat/<brand>.json` (model enum). No per-model Complete leaves in nav.  
4. **No METHOD paths as sidebar titles**. Callable L3 titles = **品牌 + 能力简称** (e.g. `Omni Flash 文生视频` / `Omni Flash 4 秒`), never raw model id alone — see `references/naming.md`.  
4b. **`title` and `sidebarTitle` same human label** (preferred). Language Complete **must** keep brand on both: `Claude · 完整参数` / `Claude · Complete reference` — never bare `完整参数` in the sidebar.  
5. **No empty brands / planned-only APIs**. Ground models in live pricing for enums.  
6. **社交数据 ≠ 社媒发布**.  
7. **连接账户** = **Connecting Accounts**.  
8. **No duplicate L2 name under L2**.  
9. **Lean nav**: no OpenAPI **附录** dump groups (Models/Chat/Images/Video…);  no meta 概览 group; **no series/account/task `overview` pages** in sidebar or repo (delete, do not leave orphan leaves); no per-model spam when contract is shared.  
10. **Callable page = Mintlify `openapi` frontmatter** → ops JSON (`openapi: "…json METHOD /path"`). Renders Authorizations/Body/Response (Evolink layout).  
11. **Forbidden**: raw OpenAPI YAML fence dump under `## OpenAPI`.  
12. **402** on billed ops.  
13. **Field honesty** from `openapi/relay.json` / live.  
14. **Domains only**: `omnimux.ai` / `api.omnimux.ai` / `docs.omnimux.ai`.  
15. **Public docs gate** after smoke.  
16. **Skill first**, then regen.  
17. **cn + en**.

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
