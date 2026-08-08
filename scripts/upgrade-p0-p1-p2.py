#!/usr/bin/env python3
"""Upgrade callable API MDX pages: P1 bullets + P0 contract tables + 402 samples.

Run from OmniMux-docs root:
  python3 scripts/upgrade-p0-p1-p2.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

JSON_402 = """```json 402
{
  "error": {
    "message": "Insufficient quota. Please top up your account.",
    "type": "insufficient_quota",
    "code": "insufficient_quota"
  }
}
```"""

JSON_402_SUCCESS_SHAPE = """```json 402
{
  "success": false,
  "message": "Insufficient quota. Please top up your account."
}
```"""

# Brand heuristic from model id prefix
BRAND_RULES = [
    (r"^claude", "Claude"),
    (r"^gpt-", "GPT"),
    (r"^o[1-9]", "GPT"),
    (r"^gemini", "Gemini"),
    (r"^grok", "Grok"),
    (r"^kimi|^moonshot", "Kimi"),
    (r"^deepseek", "DeepSeek"),
    (r"^minimax", "MiniMax"),
    (r"^glm", "GLM"),
    (r"^nano_banana|^nano-banana", "Nano Banana"),
    (r"^gpt-image|^gpt_image", "GPT Image"),
    (r"^zimage|^z-image", "Z Image"),
    (r"^veo|^omni_flash", "Veo / Omni Flash"),
    (r"^ltx", "LTX"),
    (r"^grok-imagine", "Grok Imagine"),
]


def brand_for(model: str) -> str:
    for pat, name in BRAND_RULES:
        if re.search(pat, model, re.I):
            return name
    return model.split("-")[0].title() if model else "—"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def extract_panel(body: str) -> tuple[str, str]:
    """Return (before_panel, panel_and_after) — panel starts at <Panel>."""
    m = re.search(r"<Panel\b", body)
    if not m:
        return body, ""
    return body[: m.start()].rstrip(), body[m.start() :].rstrip() + "\n"


def extract_table_value(text: str, keys: list[str]) -> str | None:
    for key in keys:
        m = re.search(rf"\|\s*{re.escape(key)}\s*\|\s*`?([^|`]+)`?\s*\|", text, re.I)
        if m:
            return m.group(1).strip()
    return None


def inject_402(panel: str, success_shape: bool = False) -> str:
    if re.search(r"```json\s*402\b", panel):
        return panel
    block = JSON_402_SUCCESS_SHAPE if success_shape else JSON_402
    # Insert after 401 block if present, else after 400, else after 200
    for status in ("401", "400", "200"):
        pat = rf"(```json\s*{status}\b[\s\S]*?```\n)"
        m = re.search(pat, panel)
        if m:
            insert_at = m.end()
            return panel[:insert_at] + "\n" + block + "\n" + panel[insert_at:]
    # Before </ResponseExample>
    m = re.search(r"</ResponseExample>", panel)
    if m:
        return panel[: m.start()] + block + "\n\n" + panel[m.start() :]
    return panel


def ensure_panel_closed(panel: str) -> str:
    if not panel.strip():
        return panel
    if "<Panel>" in panel and "</Panel>" not in panel:
        if "</ResponseExample>" in panel:
            panel = panel.rstrip() + "\n\n</Panel>\n"
        else:
            panel = panel.rstrip() + "\n</Panel>\n"
    return panel


def cn_auth_sk() -> str:
    return """## 鉴权

| 名称 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | string | 是 | `Bearer sk-...`（API Key） |
"""


def en_auth_sk() -> str:
    return """## Authorizations

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `Authorization` | header | string | yes | `Bearer sk-...` (API key) |
"""


def cn_auth_user() -> str:
    return """## 鉴权

| 名称 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| `Authorization` | header | string | 是 | `Bearer <access_token>`（用户 access token） |
| `New-Api-User` | header | string | 是 | 当前用户 id |
"""


def en_auth_user() -> str:
    return """## Authorizations

| Name | In | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `Authorization` | header | string | yes | `Bearer <access_token>` |
| `New-Api-User` | header | string | yes | Current user id |
"""


def rebuild_cn_text(meta: dict, old: str) -> str:
    model = extract_table_value(old, ["model"]) or meta.get("title", "")
    brand = extract_table_value(old, ["品牌"]) or brand_for(model)
    return f"""- OpenAI Chat Completions 兼容协议
- 通过请求体 `model` 选择本页模型（`{model}`）
- 默认同步返回；可设 `stream: true` 流式输出

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 语言系列 |
| 品牌 | {brand} |
| model | `{model}` |

## 接口

| 方法 | 路径 |
| --- | --- |
| `POST` | `/v1/chat/completions` |

Base URL：`https://api.omnimux.ai`

{cn_auth_sk()}
## 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 固定为 `{model}` |
| `messages` | array | 是 | OpenAI messages 列表（`role` + `content`） |
| `stream` | boolean | 否 | `true` 时 SSE 流式返回 |
| `temperature` | number | 否 | 采样温度 |
| `max_tokens` | integer | 否 | 最大生成 token 数 |

## 响应

### 200

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 完成 id |
| `object` | string | 通常为 `chat.completion` |
| `model` | string | 实际使用的 model |
| `choices` | array | 生成结果（含 `message`） |
| `usage` | object | prompt / completion / total tokens |

错误形态见右栏示例与 [错误码](/cn/api-reference/errors)。
"""


def rebuild_en_text(meta: dict, old: str) -> str:
    model = extract_table_value(old, ["model"]) or meta.get("title", "")
    brand = extract_table_value(old, ["Brand", "品牌"]) or brand_for(model)
    return f"""- OpenAI Chat Completions compatible
- Select this page's model via body `model` (`{model}`)
- Synchronous by default; set `stream: true` for SSE

## Identity

| Field | Value |
| --- | --- |
| Series | Language series |
| Brand | {brand} |
| model | `{model}` |

## Endpoint

| Method | Path |
| --- | --- |
| `POST` | `/v1/chat/completions` |

Base URL: `https://api.omnimux.ai`

{en_auth_sk()}
## Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | yes | Must be `{model}` |
| `messages` | array | yes | OpenAI messages (`role` + `content`) |
| `stream` | boolean | no | SSE when `true` |
| `temperature` | number | no | Sampling temperature |
| `max_tokens` | integer | no | Max completion tokens |

## Response

### 200

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Completion id |
| `object` | string | Usually `chat.completion` |
| `model` | string | Model used |
| `choices` | array | Results (includes `message`) |
| `usage` | object | Token usage |

Errors: right-rail samples and [Error codes](/en/api-reference/errors).
"""


def rebuild_cn_image(meta: dict, old: str) -> str:
    model = extract_table_value(old, ["model"]) or meta.get("title", "")
    brand = extract_table_value(old, ["品牌"]) or brand_for(model)
    async_note = "异步" in old or "task" in old.lower() or "async" in model.lower()
    bullets = [
        f"- 调用 `POST /v1/images/generations`，`model` 为 `{model}`",
        "- 请求体至少包含 `model` 与 `prompt`",
    ]
    if async_note:
        bullets.append("- 异步任务：用返回的 `task_id` 轮询 [查询图像任务](/cn/api-reference/tasks/image-task)")
    else:
        bullets.append("- 同步或异步以线上响应为准；若返回 task id，请用任务查询接口轮询")
    return f"""{chr(10).join(bullets)}

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 图像系列 |
| 品牌 | {brand} |
| model | `{model}` |

## 接口

| 方法 | 路径 |
| --- | --- |
| `POST` | `/v1/images/generations` |

Base URL：`https://api.omnimux.ai`

{cn_auth_sk()}
## 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 固定为 `{model}` |
| `prompt` | string | 是 | 图像描述 / 编辑说明 |
| `n` | integer | 否 | 生成张数（受网关上限约束） |
| `size` | string | 否 | 尺寸或宽高比（模型相关） |
| `quality` | string | 否 | 质量档位（模型相关） |

## 响应

### 200

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `created` | integer | 创建时间戳（若返回） |
| `data` | array | 图像结果（`url` 或 `b64_json`） |
| `task_id` / `id` | string | 异步时的任务 id（若返回） |

错误形态见右栏示例与 [错误码](/cn/api-reference/errors)。异步查询见 [查询图像任务](/cn/api-reference/tasks/image-task)。
"""


def rebuild_en_image(meta: dict, old: str) -> str:
    model = extract_table_value(old, ["model"]) or meta.get("title", "")
    brand = extract_table_value(old, ["Brand", "品牌"]) or brand_for(model)
    return f"""- Call `POST /v1/images/generations` with `model` `{model}`
- Body requires at least `model` and `prompt`
- If the response is async, poll [Image task](/en/api-reference/tasks/image-task)

## Identity

| Field | Value |
| --- | --- |
| Series | Image series |
| Brand | {brand} |
| model | `{model}` |

## Endpoint

| Method | Path |
| --- | --- |
| `POST` | `/v1/images/generations` |

Base URL: `https://api.omnimux.ai`

{en_auth_sk()}
## Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | yes | Must be `{model}` |
| `prompt` | string | yes | Image description / edit instruction |
| `n` | integer | no | Number of images (gateway-capped) |
| `size` | string | no | Size or aspect ratio (model-specific) |
| `quality` | string | no | Quality tier (model-specific) |

## Response

### 200

| Field | Type | Description |
| --- | --- | --- |
| `created` | integer | Creation timestamp when present |
| `data` | array | Results (`url` or `b64_json`) |
| `task_id` / `id` | string | Async task id when present |

Errors: right rail and [Error codes](/en/api-reference/errors). Async: [Image task](/en/api-reference/tasks/image-task).
"""


def rebuild_cn_video(meta: dict, old: str) -> str:
    model = extract_table_value(old, ["model"]) or meta.get("title", "")
    brand = extract_table_value(old, ["品牌"]) or brand_for(model)
    return f"""- 创建：`POST /v1/video/generations`，`model` 为 `{model}`
- 异步任务：用返回的 `task_id` 查询 [查询视频任务](/cn/api-reference/tasks/video-task)
- 产物 URL 请及时落盘（上游链接可能有时效）

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 视频系列 |
| 品牌 | {brand} |
| model | `{model}` |

## 接口

| 方法 | 路径 |
| --- | --- |
| `POST` | `/v1/video/generations` |
| `GET` | `/v1/video/generations/{{task_id}}` |

Base URL：`https://api.omnimux.ai`

{cn_auth_sk()}
## 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 固定为 `{model}` |
| `prompt` | string | 条件 | 文生视频时必填 |
| `seconds` / `duration` | number | 否 | 时长（秒，受模型与网关上限约束） |
| `size` / `resolution` | string | 否 | 分辨率（模型相关） |
| `image` / `images` | string/array | 否 | 图生视频参考图（模型相关） |

## 响应

### 200（创建）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `task_id` | string | 任务 id，用于轮询 |
| `status` | string | 如 `pending` / `processing` / `completed` |

轮询字段见 [查询视频任务](/cn/api-reference/tasks/video-task)。错误见右栏与 [错误码](/cn/api-reference/errors)。
"""


def rebuild_en_video(meta: dict, old: str) -> str:
    model = extract_table_value(old, ["model"]) or meta.get("title", "")
    brand = extract_table_value(old, ["Brand", "品牌"]) or brand_for(model)
    return f"""- Create: `POST /v1/video/generations` with `model` `{model}`
- Async: poll [Video task](/en/api-reference/tasks/video-task) with returned `task_id`
- Persist result URLs promptly (upstream links may expire)

## Identity

| Field | Value |
| --- | --- |
| Series | Video series |
| Brand | {brand} |
| model | `{model}` |

## Endpoint

| Method | Path |
| --- | --- |
| `POST` | `/v1/video/generations` |
| `GET` | `/v1/video/generations/{{task_id}}` |

Base URL: `https://api.omnimux.ai`

{en_auth_sk()}
## Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | yes | Must be `{model}` |
| `prompt` | string | conditional | Required for text-to-video |
| `seconds` / `duration` | number | no | Duration in seconds (bounded) |
| `size` / `resolution` | string | no | Resolution (model-specific) |
| `image` / `images` | string/array | no | Image-to-video references |

## Response

### 200 (create)

| Field | Type | Description |
| --- | --- | --- |
| `task_id` | string | Task id for polling |
| `status` | string | e.g. `pending` / `processing` / `completed` |

See [Video task](/en/api-reference/tasks/video-task). Errors: right rail and [Error codes](/en/api-reference/errors).
"""


def rebuild_cn_social(meta: dict, old: str, platform: str) -> str:
    model = extract_table_value(old, ["model"]) or ""
    biz = extract_table_value(old, ["主要业务字段", "Business field"]) or ""
    title = meta.get("title", "能力")
    plat = {
        "x": "X",
        "tiktok": "TikTok",
        "instagram": "Instagram",
        "youtube": "YouTube",
    }.get(platform, platform.title())
    # business field type heuristic
    biz_type = "string"
    biz_desc = {
        "aweme_id": "TikTok 作品 id",
        "unique_id": "TikTok 用户 unique_id",
        "uniqueId": "TikTok 用户 uniqueId",
        "keyword": "搜索关键词",
        "username": "平台用户名",
        "url": "作品/帖子 URL",
        "query": "搜索词",
        "tweet_id": "推文 id",
        "screen_name": "X 用户 screen_name",
        "channel_id": "YouTube channel id",
        "video_id": "YouTube video id",
        "search_query": "搜索词",
    }.get(biz, "业务主键")
    return f"""- 社交数据 **读取** 能力：OpenAI Chat Completions 形态，鉴权 `sk-`
- `model` 为 `{model}`；`messages` 可传 dummy（如 `"."`）
- 业务参数放在请求体 **top-level**（如 `{biz or "…"}`），不要塞进 system prompt
- 与 **社媒发布** 无关（发布见连接账户 / 帖子）

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 社交数据 |
| 平台 | {plat} |
| 能力 | {title} |
| model | `{model}` |

## 接口

| 方法 | 路径 |
| --- | --- |
| `POST` | `/v1/chat/completions` |

Base URL：`https://api.omnimux.ai`

{cn_auth_sk()}
## 请求体

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 固定为 `{model}` |
| `messages` | array | 是 | 可传 dummy user message |
| `{biz or "…"}` | {biz_type} | 是 | {biz_desc} |

## 响应

### 200

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 完成 id |
| `object` | string | `chat.completion` |
| `model` | string | `{model}` |
| `choices[].message.content` | string | 上游平台 JSON 字符串（结构因接口而异） |

错误形态见右栏示例与 [错误码](/cn/api-reference/errors)。
"""


def rebuild_en_social(meta: dict, old: str, platform: str) -> str:
    model = extract_table_value(old, ["model"]) or ""
    biz = extract_table_value(old, ["主要业务字段", "Business field"]) or ""
    title = meta.get("title", "Capability")
    plat = platform.title() if platform != "x" else "X"
    return f"""- Social **data read** via OpenAI Chat Completions shape; auth `sk-`
- `model` is `{model}`; `messages` may be a dummy (e.g. `"."`)
- Business params are **top-level** body fields (e.g. `{biz or "…"}`)
- Not publishing (see Connecting Accounts / Posts)

## Identity

| Field | Value |
| --- | --- |
| Series | Social data |
| Platform | {plat} |
| Capability | {title} |
| model | `{model}` |

## Endpoint

| Method | Path |
| --- | --- |
| `POST` | `/v1/chat/completions` |

Base URL: `https://api.omnimux.ai`

{en_auth_sk()}
## Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | yes | Must be `{model}` |
| `messages` | array | yes | Dummy user message allowed |
| `{biz or "…"}` | string | yes | Primary business key for this capability |

## Response

### 200

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Completion id |
| `object` | string | `chat.completion` |
| `model` | string | `{model}` |
| `choices[].message.content` | string | Upstream platform JSON as string |

Errors: right rail and [Error codes](/en/api-reference/errors).
"""


def rebuild_cn_task(meta: dict, old: str, kind: str) -> str:
    api = meta.get("api", "")
    if "image" in kind or "image" in api:
        path = "/v1/images/generations/{task_id}"
        title_hint = "图像"
        create_link = "图像创建页"
    elif "content" in kind:
        path = extract_table_value(old, ["URL", "路径"]) or "/v1/video/generations/{task_id}/content"
        title_hint = "视频内容"
        create_link = "视频创建页"
    else:
        path = "/v1/video/generations/{task_id}"
        title_hint = "视频"
        create_link = "视频创建页"
    return f"""- 查询 AI 异步{title_hint}任务状态与结果
- `task_id` 来自对应创建接口响应，不是社媒帖子 id
- 完成后请及时保存产物 URL

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 任务管理 |
| 能力 | {meta.get("title", "查询任务")} |

## 接口

| 方法 | 路径 |
| --- | --- |
| `GET` | `{path}` |

Base URL：`https://api.omnimux.ai`

{cn_auth_sk()}
## 路径参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `task_id` | string | 是 | 创建任务响应中的 id；替换 path 中的 `{{task_id}}` |

## 响应

### 200

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `task_id` / `id` | string | 任务 id |
| `status` | string | 如 `pending` / `processing` / `completed` / `failed` |
| `result` / `data` | object | 完成后的产物信息（结构因模型而异） |

错误见右栏与 [错误码](/cn/api-reference/errors)。创建见{create_link}（对应系列 model 页）。
"""


def rebuild_en_task(meta: dict, old: str, kind: str) -> str:
    api = meta.get("api", "")
    if "image" in kind or "image" in api:
        path = "/v1/images/generations/{task_id}"
    elif "content" in kind:
        path = "/v1/video/generations/{task_id}/content"
    else:
        path = "/v1/video/generations/{task_id}"
    return f"""- Poll AI async task status and results
- `task_id` comes from the create response (not a social post id)
- Persist result URLs when completed

## Identity

| Field | Value |
| --- | --- |
| Series | Tasks |
| Capability | {meta.get("title", "Query task")} |

## Endpoint

| Method | Path |
| --- | --- |
| `GET` | `{path}` |

Base URL: `https://api.omnimux.ai`

{en_auth_sk()}
## Path parameters

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `task_id` | string | yes | Id from create response; substitute into the path |

## Response

### 200

| Field | Type | Description |
| --- | --- | --- |
| `task_id` / `id` | string | Task id |
| `status` | string | e.g. `pending` / `processing` / `completed` / `failed` |
| `result` / `data` | object | Result payload when completed |

Errors: right rail and [Error codes](/en/api-reference/errors).
"""


def rebuild_cn_pub(meta: dict, old: str) -> str:
    method = extract_table_value(old, ["方法"]) or "POST"
    path = extract_table_value(old, ["路径", "URL"]) or meta.get("api", "").split(" ", 1)[-1]
    title = meta.get("title", "")
    # path-only if full URL
    path_short = path.replace("https://omnimux.ai", "") if path.startswith("http") else path
    return f"""- 社媒 **发布** 用户 API（非 `sk-` 社交数据读）
- Base：`https://omnimux.ai`；鉴权 access token + `New-Api-User`
- 连接账户命名对齐 Zernio **Connecting Accounts**

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 社媒发布 |
| 能力 | {title} |

## 接口

| 方法 | 路径 |
| --- | --- |
| `{method}` | `{path_short}` |

Base URL：`https://omnimux.ai`

{cn_auth_user()}
## 请求体 / 参数

以右栏 cURL 为准。常见字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| （见示例） | — | — | 不同资源（连接 / 帖子 / 媒体）字段不同 |

## 响应

### 200

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `success` | boolean | 是否成功 |
| `data` | object | 业务数据 |

错误见右栏与 [错误码](/cn/api-reference/errors)。
"""


def rebuild_en_pub(meta: dict, old: str) -> str:
    method = extract_table_value(old, ["Method", "方法"]) or "POST"
    path = extract_table_value(old, ["Path", "URL", "路径"]) or meta.get("api", "").split(" ", 1)[-1]
    path_short = path.replace("https://omnimux.ai", "") if path.startswith("http") else path
    title = meta.get("title", "")
    return f"""- Social **publishing** user API (not `sk-` social-data read)
- Base: `https://omnimux.ai`; auth access token + `New-Api-User`
- Connecting Accounts naming matches Zernio

## Identity

| Field | Value |
| --- | --- |
| Series | Publishing |
| Capability | {title} |

## Endpoint

| Method | Path |
| --- | --- |
| `{method}` | `{path_short}` |

Base URL: `https://omnimux.ai`

{en_auth_user()}
## Body / parameters

Follow the right-rail cURL. Fields differ by resource (connect / posts / media).

## Response

### 200

| Field | Type | Description |
| --- | --- | --- |
| `success` | boolean | Success flag |
| `data` | object | Payload |

Errors: right rail and [Error codes](/en/api-reference/errors).
"""


def rebuild_cn_account(meta: dict, old: str) -> str:
    method = extract_table_value(old, ["方法"]) or "GET"
    path = extract_table_value(old, ["路径", "URL"]) or meta.get("api", "").split(" ", 1)[-1]
    path_short = path.replace("https://omnimux.ai", "") if path and path.startswith("http") else path
    return f"""- 账户管理用户 API
- 鉴权多为 access token + `New-Api-User`（设备码流程见对应页）

## 身份

| 字段 | 值 |
| --- | --- |
| 系列 | 账户管理 |
| 能力 | {meta.get("title", "")} |

## 接口

| 方法 | 路径 |
| --- | --- |
| `{method}` | `{path_short}` |

Base URL：`https://omnimux.ai`

{cn_auth_user()}
## 请求体 / 参数

以右栏 cURL 与线上为准。

## 响应

### 200

成功时返回账户相关字段（如 `quota` / `used_quota`）。错误见右栏与 [错误码](/cn/api-reference/errors)。
"""


def rebuild_en_account(meta: dict, old: str) -> str:
    method = extract_table_value(old, ["Method", "方法"]) or "GET"
    path = extract_table_value(old, ["Path", "URL", "路径"]) or meta.get("api", "").split(" ", 1)[-1]
    path_short = path.replace("https://omnimux.ai", "") if path and path.startswith("http") else path
    return f"""- Account management user API
- Usually access token + `New-Api-User` (see device-login for bootstrap)

## Identity

| Field | Value |
| --- | --- |
| Series | Account |
| Capability | {meta.get("title", "")} |

## Endpoint

| Method | Path |
| --- | --- |
| `{method}` | `{path_short}` |

Base URL: `https://omnimux.ai`

{en_auth_user()}
## Body / parameters

Follow the right-rail cURL.

## Response

### 200

Account fields such as `quota` / `used_quota` when applicable. Errors: right rail and [Error codes](/en/api-reference/errors).
"""


def classify(path: Path) -> str | None:
    s = str(path).replace("\\", "/")
    if "/brands/" in s or s.endswith("/overview.mdx") or s.endswith("coverage.mdx"):
        return None
    if "/appendix/" in s:
        return None
    if "/text-series/models/" in s:
        return "text"
    if "/image-series/models/" in s:
        return "image"
    if "/video-series/models/" in s:
        return "video"
    if "/social-data/" in s and "/brands/" not in s:
        return "social"
    if "/tasks/" in s and not s.endswith("overview.mdx"):
        return "task"
    if "/publishing/" in s and not s.endswith("overview.mdx") and not s.endswith(
        ("connecting-accounts.mdx", "posts.mdx", "media.mdx")
    ):
        # hub pages connecting-accounts/posts/media may be non-callable shells
        return "pub"
    if "/account/" in s and not s.endswith("overview.mdx"):
        return "account"
    return None


def social_platform(path: Path) -> str:
    parts = path.parts
    try:
        i = parts.index("social-data")
        return parts[i + 1]
    except (ValueError, IndexError):
        return "platform"


def default_panel_for_type(kind: str, meta: dict, model: str, biz: str, locale: str) -> str:
    """Minimal Panel if page had none."""
    if kind in ("text", "social"):
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "." if kind == "social" else "Hello"}],
        }
        if biz:
            data[biz] = "EXAMPLE"
        import json

        data_s = json.dumps(data, ensure_ascii=False, indent=2)
        curl = f"""```bash cURL
curl --request POST \\
  --url https://api.omnimux.ai/v1/chat/completions \\
  --header 'Authorization: Bearer <token>' \\
  --header 'Content-Type: application/json' \\
  --data '{data_s}'
```"""
    elif kind == "image":
        curl = f"""```bash cURL
curl --request POST \\
  --url https://api.omnimux.ai/v1/images/generations \\
  --header 'Authorization: Bearer <token>' \\
  --header 'Content-Type: application/json' \\
  --data '{{
  "model": "{model}",
  "prompt": "a product photo on white background",
  "n": 1
}}'
```"""
    elif kind == "video":
        curl = f"""```bash cURL
curl --request POST \\
  --url https://api.omnimux.ai/v1/video/generations \\
  --header 'Authorization: Bearer <token>' \\
  --header 'Content-Type: application/json' \\
  --data '{{
  "model": "{model}",
  "prompt": "cinematic product shot"
}}'
```"""
    else:
        curl = """```bash cURL
curl --request GET \\
  --url https://api.omnimux.ai/v1/video/generations/$TASK_ID \\
  --header 'Authorization: Bearer <token>'
```"""
    resp = f"""```json 200
{{ "ok": true }}
```

```json 400
{{ "error": {{ "message": "Invalid request", "type": "invalid_request_error", "code": "bad_request" }} }}
```

```json 401
{{ "error": {{ "message": "Invalid token", "type": "authentication_error", "code": "unauthorized" }} }}
```

{JSON_402}

```json 403
{{ "error": {{ "message": "Forbidden", "type": "permission_error", "code": "forbidden" }} }}
```

```json 429
{{ "error": {{ "message": "Rate limit exceeded", "type": "rate_limit_error", "code": "rate_limit_exceeded" }} }}
```

```json 500
{{ "error": {{ "message": "Internal server error", "type": "server_error", "code": "internal_error" }} }}
```
"""
    return f"""<Panel>

<RequestExample>

{curl}

</RequestExample>

<ResponseExample>

{resp}

</ResponseExample>

</Panel>
"""


def process_file(path: Path) -> bool:
    kind = classify(path)
    if not kind:
        return False
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    # Skip pure hubs without Panel and without api
    if "api" not in meta and "<Panel" not in body and kind in ("pub",):
        # still upgrade callable ones only
        if "<Panel" not in body:
            return False

    left_old, panel = extract_panel(body)
    locale = "cn" if "/cn/" in str(path) else "en"
    success_shape = kind in ("pub", "account")

    if kind == "text":
        left = rebuild_cn_text(meta, left_old) if locale == "cn" else rebuild_en_text(meta, left_old)
    elif kind == "image":
        left = rebuild_cn_image(meta, left_old) if locale == "cn" else rebuild_en_image(meta, left_old)
    elif kind == "video":
        left = rebuild_cn_video(meta, left_old) if locale == "cn" else rebuild_en_video(meta, left_old)
    elif kind == "social":
        plat = social_platform(path)
        left = (
            rebuild_cn_social(meta, left_old, plat)
            if locale == "cn"
            else rebuild_en_social(meta, left_old, plat)
        )
    elif kind == "task":
        left = rebuild_cn_task(meta, left_old, path.stem) if locale == "cn" else rebuild_en_task(meta, left_old, path.stem)
    elif kind == "pub":
        if "<Panel" not in body and "api" not in meta:
            return False
        left = rebuild_cn_pub(meta, left_old) if locale == "cn" else rebuild_en_pub(meta, left_old)
    elif kind == "account":
        left = rebuild_cn_account(meta, left_old) if locale == "cn" else rebuild_en_account(meta, left_old)
    else:
        return False

    if not panel:
        model = extract_table_value(left_old, ["model"]) or meta.get("title", "")
        biz = extract_table_value(left_old, ["主要业务字段", "Business field"]) or ""
        panel = default_panel_for_type(kind, meta, model, biz, locale)
    else:
        panel = ensure_panel_closed(panel)
        panel = inject_402(panel, success_shape=success_shape)

    # Ensure ResponseExample exists for EN pages that only had Request
    if "<RequestExample>" in panel and "<ResponseExample>" not in panel:
        model = extract_table_value(left_old, ["model"]) or meta.get("title", "")
        extra = f"""
<ResponseExample>

```json 200
{{
  "id": "chatcmpl-example",
  "object": "chat.completion",
  "model": "{model}",
  "choices": [
    {{
      "index": 0,
      "message": {{ "role": "assistant", "content": "…" }},
      "finish_reason": "stop"
    }}
  ]
}}
```

```json 400
{{ "error": {{ "message": "Invalid request", "type": "invalid_request_error", "code": "bad_request" }} }}
```

```json 401
{{ "error": {{ "message": "Invalid token", "type": "authentication_error", "code": "unauthorized" }} }}
```

{JSON_402}

```json 403
{{ "error": {{ "message": "Forbidden", "type": "permission_error", "code": "forbidden" }} }}
```

```json 429
{{ "error": {{ "message": "Rate limit exceeded", "type": "rate_limit_error", "code": "rate_limit_exceeded" }} }}
```

```json 500
{{ "error": {{ "message": "Internal server error", "type": "server_error", "code": "internal_error" }} }}
```

</ResponseExample>
"""
        panel = panel.replace("</Panel>", extra + "\n</Panel>")

    # rebuild frontmatter with api if missing for known types
    fm_lines = ["---"]
    for k in ("title", "sidebarTitle", "description", "api"):
        if k in meta:
            fm_lines.append(f'{k}: "{meta[k]}"')
    if "api" not in meta and kind == "text":
        fm_lines.append('api: "POST https://api.omnimux.ai/v1/chat/completions"')
    fm_lines.append("---")
    fm = "\n".join(fm_lines) + "\n\n"

    new_text = fm + left.rstrip() + "\n\n" + panel.lstrip()
    if not new_text.endswith("\n"):
        new_text += "\n"
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def upgrade_errors() -> None:
    """Ensure 402 appears in the status table and ResponseExample. Idempotent."""
    for loc in ("cn", "en"):
        path = ROOT / loc / "api-reference" / "errors.mdx"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        if "| `402`" not in text:
            row = (
                "| `402` | 额度不足（需充值） |\n"
                if loc == "cn"
                else "| `402` | Insufficient quota |\n"
            )
            text = re.sub(
                r"(\|\s*`401`\s*\|\s*[^\n|]+\s*\|\n)",
                r"\1" + row,
                text,
                count=1,
            )
        if "```json 402" not in text:
            block = "\n" + JSON_402 + "\n"
            text = re.sub(
                r"(```json\s*401\b[\s\S]*?```\n)",
                r"\1" + block,
                text,
                count=1,
            )
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"updated errors: {path.relative_to(ROOT)}")


def main() -> None:
    changed = 0
    for loc in ("cn", "en"):
        base = ROOT / loc / "api-reference"
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.mdx")):
            try:
                if process_file(path):
                    changed += 1
                    print(f"ok {path.relative_to(ROOT)}")
            except Exception as e:
                print(f"FAIL {path}: {e}")
    upgrade_errors()
    print(f"done, changed={changed}")


if __name__ == "__main__":
    main()
