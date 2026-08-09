# Naming norms

## Product surfaces (never conflate)

| Concept | CN | EN | Meaning |
| --- | --- | --- | --- |
| Gateway user account | 账户管理 | **Account management** | OmniMux user, quota, device login, pricing |
| Top-tab FAQs | **常见问题** | **FAQs** | Top nav tab **after** 用户指南 / User guide (not under API 手册) |
| Connected social account | **连接账户** | **Connecting Accounts** | Platform OAuth bind (Zernio guide title) |
| Social **read** APIs | **社交数据** | Social data | TikHub-backed models; vendor = platform brand |
| Social **write** APIs | **社媒发布** | Publishing | `/api/social/v1` connect/posts/media |

### Forbidden / retired labels

| Do not use | Why |
| --- | --- |
| Social Ops / 社媒运营（as L1） | Internal slang; not Zernio or Evolink nav language |
| 已连接账号 Accounts | Bilingual pile-up; “已连接” is state, not section title |
| 社媒账号 + 连接授权 as two L2 | Split of one official concept **Connecting Accounts** |
| TikHub as public **vendor** for social-data | Vendor = TikTok / Instagram / YouTube / X |
| METHOD + path as sidebar title | Implementation detail → body / right panel only |
| Raw model id alone as L3 sidebar title | Hard to tell variants apart; must add capability short label |
| Language leaf sidebar = bare `完整参数` / `Complete API Reference` | Leaf must carry brand: `{Brand} · 完整参数` |
| EN image leaf bare `image` / `generate` | Use **Image Generation** (or `Generation` if brand already ends with Image) |
| EN video leaf bare `video` / `generate` | Use **Video Generation** / **Text-to-Video** / **Image-to-Video** |

## L1 display names (API manual)

| CN | EN |
| --- | --- |
| 语言系列 | Language series |
| 图像系列 | Image series |
| 视频系列 | Video series |
| 社交数据 | Social data |
| 社媒发布 | Publishing |
| 账户管理 | Account management |
| 任务管理 | Task management |

**Top tabs (not API-manual L1):** 用户指南 / User guide · **常见问题 / FAQs**（用户指南右侧）· 集成指南 / Integration guide · API 手册 / API manual.

Account L2 EN: **Authentication** (登录鉴权), **Account info** (账户信息).  
Do **not** rename URL path prefix `api-reference` to `api-manual` (external links).

## Sidebar title contract (callable L3)

```text
title = sidebarTitle = human label (same string preferred)
```

Language Complete **must** include brand on both fields. Other leaves: brand + capability; never model id alone.

### A. Language · brand contract

```text
CN: {Brand} · 完整参数
EN: {Brand} · Complete API Reference
```

Separator: middle dot `·` (not Evolink ASCII ` - `).  
One leaf per brand × Chat Completions; model ids live in OpenAPI enum, not nav.

### B. Image · model leaf

| Kind | CN | EN |
| --- | --- | --- |
| Default | `{Brand} 生图` | `{Brand} Image Generation` |
| Brand already contains `Image` | `{Brand} 生图` | `{Brand} Generation` (e.g. `GPT Image Generation`, `Z Image Generation`) |
| HD | `{Brand} HD 生图` | `{Brand} HD Generation` |
| Async | `… · 异步` | `… · Async` |

### C. Video · model leaf

| Kind | CN | EN |
| --- | --- | --- |
| Generic | `{Brand} 视频生成` | `{Brand} Video Generation` |
| Text-to-video | `{Brand} 文生视频` | `{Brand} Text-to-Video` |
| Image-to-video | `{Brand} 图生视频` | `{Brand} Image-to-Video` |
| First-last frame | `{Brand} 首尾帧` | `{Brand} First-Last Frame` |
| End frame | `{Brand} 尾帧` | `{Brand} End Frame` |
| Duration SKU | `{Brand} {N} 秒` | `{Brand} {N}s` |
| Async | `… · 异步` | `… · Async` |

Keep current capability axis (mode vs duration SKU); naming only unifies labels. Do not merge Veo 3.1 and Omni Flash L2 groups.

### D. Account / tasks / social / publishing

| Kind | CN | EN |
| --- | --- | --- |
| Device login | 设备码登录 | Device Code Login |
| Balance | 查询余额 | Get Balance |
| Pricing | 查询定价 | Get Pricing |
| Video task poll | 查询视频任务 | Query Video Task |
| Social capability | 作品详情 / 用户资料 / … | Post Detail / User Profile / User Posts / Video Search / … (Title Case) |
| Publishing | 发起连接 / 列出账户 / … | Start Connection / List Accounts / Disconnect Account / Create Post / Get Post / Media Presign / Upload Media |

## Examples (Evolink-style leaf labels)

| Bad | Good (CN) | Good (EN) |
| --- | --- | --- |
| `完整参数` (no brand) | Claude · 完整参数 | Claude · Complete API Reference |
| `omni_flash` | Omni Flash 视频生成 | Omni Flash Video Generation |
| `omni_flash-4s` | Omni Flash 4 秒 | Omni Flash 4s |
| `minimax-h3-t2v` | MiniMax 文生视频 | MiniMax Text-to-Video |
| `nano_banana_2` only | Nano Banana 2 生图 | Nano Banana 2 Image Generation |
| `GPT Image generate` | GPT Image 生图 | GPT Image Generation |

## Zernio alignment (publishing)

Official guide: [Connecting Accounts](https://docs.zernio.com/guides/connecting-accounts.mdx)

| CN L2 | EN L2 | Paths (body) |
| --- | --- | --- |
| 连接账户 | Connecting Accounts | `POST …/connect`, `GET …/accounts`, `DELETE …/accounts/{id}` |
| 帖子 | Posts | `POST/GET …/posts` |
| 媒体 | Media | `POST …/media/presign`, client `PUT` |

Post **status** lives under **帖子**, never under **任务管理**.

## TikHub alignment (social data)

- Upstream: TikHub; public docs discovery: platform → capability.  
- L3 CN examples: 作品详情 / 用户资料 / 用户作品列表 / 视频搜索 / 综合搜索 / …  
- Body always shows `model` id (e.g. `instagram-post`).  
- Call shape: `POST /v1/chat/completions` + dummy `messages` + business fields top-level.

## AI series brands

- Brand = user-facing family (Claude, GPT, Nano Banana, Omni Flash, Veo 3.1…), not channel slug.  
- **Language:** L3 = brand Complete contract; model ids in enum table.  
- **Image / video (per-model leaves until contract-axis):** L3 title = brand + capability short name; model id in body.  
- No empty brand folders for paths without catalog models.  
- **Veo 3.1** and **Omni Flash** are separate L2 groups (never “Veo / Omni Flash” combined).

## Page titles (summary)

| Page kind | title / sidebarTitle |
| --- | --- |
| Language brand contract | `{Brand} · 完整参数` / `{Brand} · Complete API Reference` (**both fields**) |
| Image / video model leaf | **品牌 + 能力简称** (required; EN per tables B/C) |
| Social-data capability | Chinese capability (CN); Title Case capability (EN) |
| Publishing capability | 发起连接 / Start Connection / … |
| Task poll | 查询视频任务 / Query Video Task |

## Domains

Only: `omnimux.ai`, `api.omnimux.ai`, `docs.omnimux.ai`.  
Never: `*.geminix.cc`, `docs.newapi.pro` as primary.

## Tasks (hard)

| Keep in nav | Path | Notes |
| --- | --- | --- |
| 查询视频任务 | `GET /v1/video/generations/{task_id}` | Primary poll for video series creates |
| **Do not** list as generic task helpers | `GET /v1/videos/{task_id}/content` | OpenAI Videos **file download**, not status poll |
| **Do not** invent | `GET /v1/images/generations/{task_id}` | Not in public relay OpenAPI |

## Lint

```bash
python3 scripts/check-naming.py
```

Must pass before merge when titles or nav groups change.
