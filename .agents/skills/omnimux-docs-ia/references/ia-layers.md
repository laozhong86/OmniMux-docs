# API 手册 · 分层 IA

## Mental model

```text
L1  系列 / 管理面          （发现主轴）
 └── L2  品牌 或 资源组     （产品族 / 资源域）
      └── L3  调用合同页     （协议 + 路径 + schema；非默认 per-model）
```

### Paging axis (confirmed)

**Page = stable call contract** (auth + method + path + request/response schema).  
**`model` is an enum inside the contract**, not the default nav leaf.

| Split page when | Do **not** split page when |
| --- | --- |
| Different path/protocol (Chat vs Messages vs Responses) | Same Chat Completions shape, only model id differs |
| Different modality endpoint (image/video) | Pricing / speed / marketing differences only |
| Materially different required fields or response shape | Live catalog has many SKUs under one brand |

**Language series:** one Complete page per brand × Chat Completions (`…/text-series/<brand>/complete`), with model table + OpenAPI `model` enum.  
**Social data:** still L3 = capability name (business fields differ).  
**社媒发布:** L3 = capability (resource REST).

- **AI 网关语言：** L2=品牌，L3=「完整参数」合同页。  
- **社媒发布**：路径是资源 REST → L2=资源组，L3=中文能力名。  
- **账户 / 任务**：管理面。

## L1 catalog (current)

| L1 (CN) | L1 (EN) | L2 | L3 | Auth |
| --- | --- | --- | --- | --- |
| 语言系列 | Language series | Claude, Gemini, GPT, Grok, Kimi, DeepSeek, MiniMax, GLM | **完整参数**（合同页，非 per-model） | `sk-` |
| 图像系列 | Image series | Nano Banana, GPT Image, Z Image | model id | `sk-` |
| 视频系列 | Video series | MiniMax, **Veo 3.1**, **Omni Flash**（分栏，勿合并）, LTX, Grok Imagine | model id（合同轴后续可收敛） | `sk-` |
| 社交数据 | Social data | TikTok, Instagram, YouTube, X | 中文能力名（作品详情…） | `sk-` Chat 形态 |
| 社媒发布 | Publishing | 连接账户 / 帖子 / 媒体 | 发起连接、列出账户… | access token + `New-Api-User` |
| 账户管理 | Account | 登录鉴权 / 账户信息 | 设备码登录、余额、定价 | 多为 access token |
| 任务管理 | Tasks | AI 异步任务 | 查询视频/图像任务… | `sk-` |
| 附录 | Appendix | OpenAPI 说明 + relay try-it | OpenAPI ops | `sk-` |

**Not L1 (do not reintroduce without product+docs decision):**

- **任何 `overview` / 概述 栏目页**（系列概述、API 手册概览、覆盖说明、集成指南概览等）— **删除文件且不进 `docs.json`**  
- **概览 meta 组**（错误码独立栏目等）— 错误样例在 capability Response  
- 音频系列（无 live Audio Generation models）  
- 文件管理（无独立通用文件 API；媒体归社媒发布）  
- Social Ops 命名  
- 空品牌（Kling/Sora/即梦 path 壳无 model）  

**Nav lean rule:** 侧栏只保留可调用合同/能力路径；禁止概述、覆盖矩阵、重复说明页加厚导航。

**Nav icons (Mintlify `icon` on groups):** L1 系列与其下 L2 品牌/资源组共用**系列统一图标**（对齐 Evolink：图像品牌皆 `image`，视频品牌皆 `video`）。

| 系列 | icon |
| --- | --- |
| 语言系列 | `message-square` |
| 图像系列 | `image` |
| 视频系列 | `video` |
| 社交数据 | `share-2` |
| 社媒发布 | `send` |
| 账户管理 | `user` |
| 任务管理 | `list-checks` |
| 附录 | `book-open` |
## Directory map (repo)

```text
cn|en/api-reference/
  text-series/<brand>/complete.mdx    # brand contract pages (no overview)
  image-series/{brands/*,models/*}
  video-series/{brands/*,models/*}
  social-data/{brands/*,tiktok|instagram|youtube|x/*}
  publishing/{connecting-accounts,posts,media,start-connect,...}
  account/{device-login,balance,pricing}
  tasks/{video-task,video-content,image-task}
  appendix/openapi.mdx
docs.json
openapi/relay.json
openapi/ops/chat/<brand>.json
scripts/gen-chat-capability-pages.py
```

Do **not** create `**/overview.mdx` for series or guides.

Brand MDX under `brands/` may exist for deep links / series overview tables, but **`docs.json` must not nest a child page titled the same as the L2 group**.

## `docs.json` nesting pattern

```json
{
  "group": "YouTube",
  "pages": [
    "cn/api-reference/social-data/youtube/video-detail",
    "cn/api-reference/social-data/youtube/channel-info"
  ]
}
```

**Wrong:**

```json
{
  "group": "YouTube",
  "pages": [
    "cn/api-reference/social-data/brands/youtube",
    "cn/api-reference/social-data/youtube/video-detail"
  ]
}
```

**Wrong:** L3 title = `` `GET /v1/video/generations/{task_id}` ``

## OpenAPI placement

| Kind | Role |
| --- | --- |
| **L3 capability page** | **Single operation** OpenAPI embedded in MDX (`openapi/ops/**` + `## OpenAPI`) — Evolink-class detail |
| **附录** | Full gateway dump `openapi/relay.json` for bulk try-it |
| **Not** | Top-level OpenAPI groups re-listing Chat/Images next to series as primary discovery |

- Prefer series → brand → model MDX for discovery.  
- L3 page type = **OpenAPI capability page** (see `content-templates.md`), not protocol-only dump.

## Credentials map

| Surface | Base | Credential |
| --- | --- | --- |
| AI + 社交数据 | `https://api.omnimux.ai` | `Authorization: Bearer sk-...` |
| 社媒发布 / 设备码后续用户 API | `https://omnimux.ai` | access token + `New-Api-User: <user_id>` |
