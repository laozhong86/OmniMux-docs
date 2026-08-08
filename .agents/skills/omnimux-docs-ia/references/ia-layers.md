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
| 视频系列 | Video series | MiniMax, Veo / Omni Flash, LTX, Grok Imagine（**仅有 model 的品牌**） | model id | `sk-` |
| 社交数据 | Social data | TikTok, Instagram, YouTube, X | 中文能力名（作品详情…） | `sk-` Chat 形态 |
| 社媒发布 | Publishing | 连接账户 / 帖子 / 媒体 | 发起连接、列出账户… | access token + `New-Api-User` |
| 账户管理 | Account | 登录鉴权 / 账户信息 | 设备码登录、余额、定价 | 多为 access token |
| 任务管理 | Tasks | AI 异步任务 | 查询视频/图像任务… | `sk-` |
| 附录 | Appendix | OpenAPI 说明 + relay try-it | OpenAPI ops | `sk-` |

**Not L1 (do not reintroduce without product+docs decision):**

- **概览 meta 组**（API 手册概览 / 文档覆盖说明 / 错误码独立栏目）— 侧栏不展示；错误样例在各 capability 页 Response  
- 音频系列（无 live Audio Generation models）  
- 文件管理（无独立通用文件 API；媒体归社媒发布）  
- Social Ops 命名  
- 空品牌（Kling/Sora/即梦 path 壳无 model）  

**Nav lean rule:** 侧栏只保留可调用能力路径；禁止说明性、覆盖矩阵、重复错误码目录加厚导航。
## Directory map (repo)

```text
cn|en/api-reference/
  text-series/{overview, <brand>/complete.mdx}   # brand contract pages
  image-series/{overview,brands/*,models/*}      # phase 2: prefer contract axis later
  video-series/{overview,brands/*,models/*}
  social-data/{overview,brands/*,tiktok|instagram|youtube|x/*}
  publishing/{overview,connecting-accounts,posts,media,start-connect,...}
  account/{overview,device-login,balance,pricing}
  tasks/{overview,video-task,video-content,image-task}
  appendix/openapi.mdx
docs.json
openapi/relay.json
openapi/ops/chat/<brand>.json    # brand × Chat Completions (model enum)
scripts/gen-chat-capability-pages.py
```


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
