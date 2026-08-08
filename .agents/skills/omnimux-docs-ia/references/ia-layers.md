# API 手册 · 分层 IA

## Mental model

```text
L1  系列 / 管理面          （发现主轴）
 └── L2  品牌 或 资源组     （产品族 / 资源域）
      └── L3  model id 或 能力名   （可调用单元）
```

- **AI 网关**（图/文/视频/社交数据读）：路径多为共用 `/v1/*`，差异在 `model` → L2=品牌，L3=`model` id（社交数据 L3 用**中文能力名**，正文写 model id）。  
- **社媒发布**：路径是资源 REST → L2=资源组（连接账户/帖子/媒体），L3=中文能力名。  
- **账户 / 任务**：管理面，不是模型广场。

## L1 catalog (current)

| L1 (CN) | L1 (EN) | L2 | L3 | Auth |
| --- | --- | --- | --- | --- |
| 语言系列 | Language series | Claude, Gemini, GPT, Grok, Kimi, DeepSeek, MiniMax, GLM | model id | `sk-` |
| 图像系列 | Image series | Nano Banana, GPT Image, Z Image | model id | `sk-` |
| 视频系列 | Video series | MiniMax, Veo / Omni Flash, LTX, Grok Imagine（**仅有 model 的品牌**） | model id | `sk-` |
| 社交数据 | Social data | TikTok, Instagram, YouTube, X | 中文能力名（作品详情…） | `sk-` Chat 形态 |
| 社媒发布 | Publishing | 连接账户 / 帖子 / 媒体 | 发起连接、列出账户… | access token + `New-Api-User` |
| 账户管理 | Account | 登录鉴权 / 账户信息 | 设备码登录、余额、定价 | 多为 access token |
| 任务管理 | Tasks | AI 异步任务 | 查询视频/图像任务… | `sk-` |
| 概览 | Overview | — | 覆盖说明、错误码 | — |
| 附录 | Appendix | OpenAPI 说明 + relay try-it | OpenAPI ops | `sk-` |

**Not L1 (do not reintroduce without product+docs decision):**

- 音频系列（无 live Audio Generation models）  
- 文件管理（无独立通用文件 API；媒体归社媒发布）  
- Social Ops 命名  
- 空品牌（Kling/Sora/即梦 path 壳无 model）

## Directory map (repo)

```text
cn|en/api-reference/
  overview.mdx, coverage.mdx, errors.mdx
  text-series/{overview,brands/*,models/*}
  image-series/{overview,brands/*,models/*}
  video-series/{overview,brands/*,models/*}
  social-data/{overview,brands/*,tiktok|instagram|youtube|x/*}
  publishing/{overview,connecting-accounts,posts,media,start-connect,...}
  account/{overview,device-login,balance,pricing}
  tasks/{overview,video-task,video-content,image-task}
  appendix/openapi.mdx
docs.json          # navigation only lists L3 under L2 groups (no brand hub child)
openapi/relay.json # AI gateway OpenAPI snapshot
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

- Full try-it dump: **附录** only (`openapi/relay.json`).  
- Do not re-attach full OpenAPI as a top-level sibling that re-lists Models/Chat/Images next to series.  
- Prefer series → brand → model MDX for discovery; OpenAPI for schema/try-it.

## Credentials map

| Surface | Base | Credential |
| --- | --- | --- |
| AI + 社交数据 | `https://api.omnimux.ai` | `Authorization: Bearer sk-...` |
| 社媒发布 / 设备码后续用户 API | `https://omnimux.ai` | access token + `New-Api-User: <user_id>` |
