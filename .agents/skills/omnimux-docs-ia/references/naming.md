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

- Brand = user-facing family (Claude, GPT, Nano Banana…), not channel slug.  
- L3 = public model id from live pricing.  
- No empty brand folders for paths without catalog models.

## Page titles

| Page kind | title / sidebarTitle |
| --- | --- |
| Series hub | 概述 / Overview |
| Brand file (optional deep link) | Brand name (not in nav under same-named group) |
| Model | model id string |
| Social-data capability | Chinese capability (CN); English capability (EN) |
| Publishing capability | 发起连接 / 列出账户 / … |

## Domains

Only: `omnimux.ai`, `api.omnimux.ai`, `docs.omnimux.ai`.  
Never: `*.geminix.cc`, `docs.newapi.pro` as primary.
