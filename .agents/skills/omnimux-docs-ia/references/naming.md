# Naming norms

## Product surfaces (never conflate)

| Concept | CN | EN | Meaning |
| --- | --- | --- | --- |
| Gateway user account | 账户管理 | Account | OmniMux user, quota, device login, pricing |
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

## Sidebar title contract (POST / GET leaves)

Every callable L3 leaf that shows a METHOD badge **must** use:

```text
<title> = <品牌或产品短名> <能力简称>
```

Examples (Evolink-style):

| Bad (model id only) | Good (CN) | Good (EN) |
| --- | --- | --- |
| `omni_flash` | Omni Flash 视频生成 | Omni Flash video |
| `omni_flash-4s` | Omni Flash 4 秒 | Omni Flash 4s |
| `minimax-h3-t2v` | MiniMax 文生视频 | MiniMax text-to-video |
| `minimax-h3-t2v-async` | MiniMax 文生视频 · 异步 | MiniMax text-to-video async |
| `veo_3_1` | Veo 3.1 视频生成 | Veo 3.1 video |
| `nano_banana_2` | Nano Banana 2 生图 | Nano Banana 2 image |

Rules:

1. **title** and **sidebarTitle** both carry the short capability label (sidebarTitle may truncate brand if needed, never drop capability).  
2. Capability words distinguish **mode** (文生 / 图生 / 首尾帧 / 参考图 / 编辑) and **ops variant** (异步 / 秒数 / HD) when siblings would otherwise look identical.  
3. Body / OpenAPI still pin **model id** exactly as live pricing.  
4. Language **brand contract** pages stay `完整参数` / `Complete reference` (one contract, model enum) — not per-model leaves.  
5. Social-data L3 already uses capability Chinese names — keep; do not replace with model id alone.

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
- **Language:** L3 = brand Complete contract page; model ids in enum table.  
- **Image / video (per-model leaves until contract-axis):** L3 title = brand + capability short name; model id in body.  
- No empty brand folders for paths without catalog models.  
- **Veo 3.1** and **Omni Flash** are separate L2 groups (never “Veo / Omni Flash” combined).

## Page titles

| Page kind | title / sidebarTitle |
| --- | --- |
| Language brand contract | `Claude · 完整参数` / `Claude · Complete reference` |
| Image / video model leaf | **品牌 + 能力简称** (required) |
| Social-data capability | Chinese capability (CN); English capability (EN) |
| Publishing capability | 发起连接 / 列出账户 / … (capability Chinese) |
| Task poll | 查询视频任务 / … |

## Domains

Only: `omnimux.ai`, `api.omnimux.ai`, `docs.omnimux.ai`.  
Never: `*.geminix.cc`, `docs.newapi.pro` as primary.
