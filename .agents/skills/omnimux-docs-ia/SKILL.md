---
name: omnimux-docs-ia
description: "OmniMux public Mintlify docs (OmniMux-docs) API 手册 IA and content norms. Use when adding/changing docs.omnimux.ai API pages, docs.json navigation, model/brand/series pages, 社交数据/社媒发布/账户/任务 docs, RequestExample/ResponseExample/Panel right rail, or after shipping user-facing HTTP APIs (public docs gate). Triggers: omnimux docs, Mintlify, API 手册, docs.json, 连接账户, Connecting Accounts, series brand model, 新建栏目. Not for: product Go/relay implementation (use newapi / deploy-vps); admin OpenAPI; inventing models not on live pricing."
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
| **L3 Page shape** | `references/content-templates.md` | MDX body, right-panel examples, errors |
| **L4 Workflows** | `references/workflows.md` | Add model / brand / social API / smoke→docs gate |

Do **not** invent parallel IA. Live site + `docs.json` + this skill are the source of truth.

## Repo paths

| Item | Path |
| --- | --- |
| Docs repo (edit here) | sibling `OmniMux-docs` (e.g. `~/Desktop/Project/OmniMux-docs`) |
| Nav | `docs.json` |
| Locales | `cn/**`, `en/**` (both for user-facing API) |
| OpenAPI (AI gateway only) | `openapi/relay.json` — **no** admin `api.json` |
| Agent always-on | `AGENTS.md` (thin; points here) |

Product monorepo may soft-link this skill under `.agents/skills/omnimux-docs-ia`. Edits to docs still land in **OmniMux-docs**.

## Hard rules (summary)

1. **IA**: L1 series/management → L2 brand or resource group → L3 model id **or** Chinese capability name.  
2. **No METHOD paths as sidebar titles** (`GET /v1/...` only in body / right panel).  
3. **No empty brands / planned-only APIs** in nav. Ground AI/social-data L3 in live `GET /api/pricing` (or `GET /v1/models`).  
4. **社交数据 ≠ 社媒发布**: TikHub **read** (`sk-` Chat) vs Zernio-path **publish** (access token + `New-Api-User`).  
5. **连接账户** (CN) = **Connecting Accounts** (EN, Zernio official). Not “Social Ops”, not “已连接账号 Accounts”.  
6. **No duplicate L2 name under L2**: group label is the brand/platform; children are only L3 (no second “YouTube” hub row).  
7. **Right rail examples**: wrap in `<Panel>` + `<RequestExample>` + `<ResponseExample>`; prefer `api:` frontmatter on capability pages.  
8. **Left contract layers (P0)**: callable L3 pages MUST document **鉴权 / Authorizations**, **请求体 Body 和/或 Path**, and **响应 Response (200 fields)** — not identity + path only.  
9. **Capability bullets (P1)**: 2–4 bullets under H1 (protocol/mode, sync-async, auth surface, cross-links).  
10. **402 quota (P2)**: billed gateway ResponseExample and `errors.mdx` MUST include **402** `insufficient_quota`.  
11. **Public docs gate**: after successful smoke of a user-facing HTTP API, update OmniMux-docs (cn+en + `docs.json`) before calling work done.  
12. **Domains only**: `omnimux.ai` / `api.omnimux.ai` / `docs.omnimux.ai`.  
13. **Detail optimization loop**: any accepted docs micro-fix updates **this skill first**, then MDX content (never content-only drift).

## Default procedure (short)

1. Confirm surface: AI model · social-data · publishing · account · task.  
2. Load **L1–L4 references** as needed.  
3. Diff live catalog if adding models (`GET /api/pricing`).  
4. Add/update MDX under the correct tree; register **only** L3 pages under L2 groups in `docs.json` (no brand hub child).  
5. Include **P0 contract tables + P1 bullets + Panel examples with 402**.  
6. `mint dev` or post-merge smoke key URLs (200); desktop curl in right rail.  
7. Do not leave product PR “done” without docs when the gate applies.  
8. If norms change: edit skill references **before** bulk MDX.

## Out of scope

- Implementing relay/channel code (product repo + `newapi` / `runninghub-omnimux`).  
- Admin/back-office OpenAPI.  
- Copying Evolink/Zernio brand lists that are not live on OmniMux.
