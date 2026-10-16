#!/usr/bin/env python3
"""Generate the bilingual GPT Image contract without widening standard service."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD_MODEL = "gpt-image-2.5"
OTHER_MODELS = ["gpt-image-2.5-hd", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst"]
PATH = "/v1/images/generations"
SIZES = [
    ("1:1", "1024x1024"), ("2:3", "1024x1536"),
    ("3:2", "1536x1024"), ("3:4", "1024x1360"),
    ("4:3", "1360x1024"), ("9:16", "1088x1920"),
    ("16:9", "1920x1088"),
]


def localized(zh, chinese, english):
    return chinese if zh else english


def standard_schema(zh):
    reference_description = localized(zh,
        "公开 HTTPS 参考图：JPEG、PNG 或 WebP，单张最多 5 MiB（5242880 字节），解码后最多 40000000 像素，任一边最多 23170 像素。URL 不得包含凭据或片段，最终地址也必须符合公网访问检查。所有参考别名合计最多一张，重复值也计数；不接受 base64 或文件上传。",
        "A public HTTPS reference image in JPEG, PNG, or WebP format, up to 5 MiB (5242880 bytes), 40000000 decoded pixels, and 23170 pixels on either edge. The URL must not contain credentials or a fragment; the final destination must also pass public-network checks. At most one reference is allowed across all aliases, including duplicate values. Base64 and file uploads are not accepted.")
    reference_url = {"type": "string", "format": "uri", "pattern": "^https://", "description": reference_description}
    reference = {"oneOf": [reference_url] + [
        {"type": "object", "required": [key], "additionalProperties": False, "properties": {key: reference_url}}
        for key in ("url", "image_url")
    ]}
    reference_field = {"oneOf": [reference, {"type": "array", "maxItems": 1, "items": reference}], "description": reference_description}
    size_values = [ratio for ratio, _ in SIZES] + [pixels for _, pixels in SIZES]
    size_description = localized(zh,
        "仅支持所列七种画幅和精确像素。省略或空字符串使用 1024x1024；3:4 与 4:3 是近似画幅，旧 1024x1365 和 1365x1024 不再接受。size 和 aspect_ratio 同时提供时必须对应相同像素。",
        "Only the seven listed aspect ratios and exact pixel sizes are supported. Omission or an empty string uses 1024x1024. The 3:4 and 4:3 labels are approximate; the old 1024x1365 and 1365x1024 sizes are no longer accepted. When both size and aspect_ratio are present, they must resolve to the same pixels.")
    seed = {"type": "integer", "minimum": 0, "description": localized(zh, "非负整数，须在服务接受的整数范围内。", "A nonnegative integer within the service's accepted integer range.")}
    properties = {
        "model": {"type": "string", "enum": [STANDARD_MODEL], "default": STANDARD_MODEL},
        "prompt": {"type": "string", "minLength": 1, "maxLength": 8192,
            "description": localized(zh,
                "完整提示词须同时不超过 8192 个 Unicode 码点、16384 个 UTF-8 字节和本服务按 o200k_base 计数的 5000 个词元，空白也计入上限，且不得全为空白。这是标准服务的运营限制，不是官方独立 Flare / Sunburst 型号的 32000 字符上限；本地词元计数不代表供应商最终计费量，也不保证单次采购成本上限。超限在预留费用和发送供应商请求前明确拒绝，不截断、压缩或替换。",
                "The complete prompt must satisfy all three limits: 8192 Unicode code points, 16384 UTF-8 bytes, and 5000 tokens counted by this service with o200k_base. Whitespace counts toward the limits, and a whitespace-only prompt is invalid. These are the standard service's operating limits, not the 32000-character vendor limit for the separate Flare / Sunburst models. The local token count does not represent final supplier billing usage or guarantee a per-request procurement cost ceiling. Over-limit prompts are rejected before reserving funds or sending a supplier request, without truncating, compressing, or replacing them.")},
        "n": {"type": "integer", "enum": [1], "default": 1},
        "size": {"type": "string", "enum": size_values + [""], "default": "1024x1024", "description": size_description},
        "aspect_ratio": {"type": "string", "enum": size_values + [""], "description": size_description},
        "quality": {"type": "string", "enum": ["medium"], "default": "medium"},
        "output_format": {"type": "string", "enum": ["png"], "default": "png",
            "description": localized(zh, "仅 PNG 输出。JPEG / WebP 仅为可接受的参考图格式。", "PNG output only. JPEG / WebP are supported reference-input formats only.")},
        "group": {"type": "string", "description": localized(zh, "可选的既有授权路由覆盖字段；标准用法无需选择供应商。不会作为供应商参数发送。", "An optional existing authorized routing override; ordinary standard use does not require supplier selection. It is not forwarded as a supplier parameter.")},
        "seed": seed,
        "metadata": {"type": "object", "additionalProperties": False, "properties": {"seed": seed}},
    }
    properties.update({key: reference_field for key in ("image", "images", "image_urls", "input_reference")})
    return {"title": localized(zh, "标准服务", "Standard service"), "type": "object", "required": ["model", "prompt"], "additionalProperties": False, "properties": properties}


def other_schema(zh):
    return {"title": localized(zh, "其他既有独立型号", "Other existing separate models"), "type": "object", "required": ["model", "prompt"], "properties": {
        "model": {"type": "string", "enum": OTHER_MODELS},
        "prompt": {"type": "string", "description": localized(zh, "独立 Flare / Sunburst 的官方提示词上限仍为 32000 字符；本次标准服务限制不修改这些型号的合同。hd 上限本页不作未经核验的承诺。", "The vendor prompt limit for separate Flare / Sunburst models remains 32000 characters; this standard-service change does not alter their contracts. This page does not assert an unverified hd limit.")},
        "n": {"type": "integer", "description": localized(zh, "图像数量，受所选型号和路线限制。", "Image count, subject to the selected model and route limits.")},
        "size": {"type": "string", "description": localized(zh, "尺寸受所选型号和路线限制。", "Accepted sizes depend on the selected model and route.")},
        "quality": {"type": "string", "description": localized(zh, "质量选项受所选型号和路线限制。", "Quality options depend on the selected model and route.")},
        "images": {"type": "array", "items": {"type": "string"}, "description": localized(zh, "保留既有独立型号的参考字段合同；不由标准服务的单参考上限推导其限制。", "Retains the existing separate-model reference-field contract; its limits are not derived from the standard service's one-reference limit.")},
    }}


for lang in ("en", "zh"):
    zh = lang == "zh"
    title = localized(zh, "GPT Image · 图像生成", "GPT Image · Image generation")
    description = localized(zh, "GPT Image 标准生图与既有独立型号的调用规范。", "Request contracts for GPT Image standard generation and existing separate models.")
    example = {"model": STANDARD_MODEL, "prompt": localized(zh, "成年男性角色设定板：白底，左侧面部近景，右侧完整全身，人物外观保持一致。", "An adult male character sheet on white: a facial close-up on the left and a full-body view on the right, with a consistent appearance."), "n": 1, "size": "16:9", "quality": "medium", "output_format": "png"}
    response = {"type": "object", "description": localized(zh, "按实际响应读取图像结果或异步任务；任务受理不等于图片已完成。", "Read image results or an asynchronous task according to the returned shape. Task acceptance does not mean an image is complete."), "properties": {
        "created": {"type": "integer"}, "data": {"type": "array", "items": {"type": "object", "properties": {"url": {"type": "string"}, "b64_json": {"type": "string"}}}},
        "id": {"type": "string", "description": localized(zh, "返回时为原异步任务编号，继续查询该任务。", "The original asynchronous task ID, when returned. Continue polling that task.")},
        "object": {"type": "string"}, "model": {"type": "string"}, "status": {"type": "string"}}}
    op = {"summary": title, "operationId": "generateGPTImage", "description": description, "security": [{"BearerAuth": []}], "requestBody": {"required": True, "content": {"application/json": {"schema": {"oneOf": [standard_schema(zh), other_schema(zh)]}, "example": example}}}, "responses": {"200": {"description": localized(zh, "图像结果或已受理的原异步任务。", "Image results or the accepted original asynchronous task."), "content": {"application/json": {"schema": response}}}}}
    errors = {
        "400": ("输入无效或超出标准服务已审核范围。", "Invalid input or parameters outside the standard service's reviewed scope."),
        "401": ("需要身份验证。", "Authentication required."), "402": ("额度不足。", "Insufficient quota."),
        "403": ("无权访问。", "Forbidden."), "429": ("请求过于频繁。", "Rate limit exceeded."), "500": ("服务错误。", "Server error."),
    }
    for status, texts in errors.items():
        op["responses"][status] = {"description": localized(zh, *texts)}
    spec = {"openapi": "3.0.3", "info": {"title": title, "version": "1.1.0"}, "servers": [{"url": "https://api.omnimux.ai"}], "paths": {PATH: {"post": op}}, "components": {"securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer"}}}}
    dest = ROOT / "openapi/ops/image" / lang / "gpt-image.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")

    notice = localized(zh,
        "自 2026-09-10 起，`gpt-image-2` 和 `gpt-image-2-hd` 已分别更名为 `gpt-image-2.5` 和 `gpt-image-2.5-hd`。旧型号不再接受；这些不是兼容别名。下述标准服务限制仅适用于裸 `gpt-image-2.5` 的标准路线，不修改其他独立型号。",
        "Since September 10, 2026, `gpt-image-2` and `gpt-image-2-hd` have been renamed to `gpt-image-2.5` and `gpt-image-2.5-hd`. Old IDs are not accepted; these are not compatibility aliases. The standard-service limits below apply only to the standard route of bare `gpt-image-2.5`, not to other separate models.")
    heading = localized(zh, "## 标准规格", "## Standard specifications")
    introduction = localized(zh,
        "标准路线支持文生图和单参考图编辑，每次生成一张 `medium` 质量的 PNG 图片。`n`、`quality`、`output_format` 省略时分别为 `1`、`medium`、`png`。仅接受 JSON，不支持文件上传或表单提交。",
        "The standard route supports text-to-image generation and editing with one reference image. Each request produces one medium-quality PNG image. Omitted `n`, `quality`, and `output_format` default to `1`, `medium`, and `png`. Only JSON is accepted; file uploads and form submissions are not supported.")
    table = localized(zh, "| 画幅 | 精确输出像素 |\n| --- | --- |", "| Aspect ratio | Exact output pixels |\n| --- | --- |") + "\n" + "\n".join(f"| {ratio} | {pixels} |" for ratio, pixels in SIZES)
    dimensions = localized(zh,
        "`size` 可使用上述画幅标签或精确像素值；省略或空字符串默认为 `1024x1024`。3:4 和 4:3 使用近似画幅：长边由旧 1365 调整为 1360 像素，相差 5 像素。旧 `1024x1365` / `1365x1024` 明确拒绝。`size` 与 `aspect_ratio` 同时填写时必须对应相同像素。角色工作台显式使用 `1920x1088` 横版角色板或多视角板；多视角是在同一张图内呈现多个视图，不是多张输出。",
        "Use one of the listed aspect-ratio labels or exact pixel sizes for `size`; omission or an empty string defaults to `1024x1024`. The 3:4 and 4:3 labels are approximate: their longer edge changes from 1365 to 1360 pixels, a difference of 5 pixels. The old `1024x1365` / `1365x1024` sizes are explicitly rejected. If both `size` and `aspect_ratio` are supplied, they must resolve to the same pixels. The character workbench explicitly uses a `1920x1088` landscape character sheet or multi-view board. A multi-view board contains several views in one image, not multiple output images.")
    references = localized(zh,
        "## 单参考图\n\n文生图可不传参考；编辑时提供一张公开 HTTPS 图片。接受 JPEG、PNG、WebP，单张最多 5 MiB（5242880 字节），解码后最多 40000000 像素，任一边最多 23170 像素。URL 和最终目的地址须通过公网访问检查。\n\n`image`、`images`、`image_urls`、`input_reference` 是参考别名，每项可为 URL 字符串或仅含 `url` / `image_url` 单键的对象，也可包在数组中；所有字段合计最多一张，重复填写同一 URL 也计为多张。此标准路线不接受 base64。JPEG / WebP 是参考输入格式，输出仍仅为 PNG。",
        "## One reference image\n\nA reference is optional for text-to-image generation and required for editing. Supply one public HTTPS image in JPEG, PNG, or WebP format, up to 5 MiB (5242880 bytes), 40000000 decoded pixels, and 23170 pixels on either edge. Both the URL and its final destination must pass public-network checks.\n\n`image`, `images`, `image_urls`, and `input_reference` are reference aliases. An item may be a URL string or an object containing only `url` or `image_url`, optionally wrapped in an array. At most one reference is allowed across all fields, including duplicate URLs. This standard route does not accept base64. JPEG / WebP are reference-input formats; output remains PNG only.")
    prompt = localized(zh,
        "## 提示词与拒绝范围\n\n完整提示词须同时满足三项上限：**8192 个 Unicode 码点、16384 个 UTF-8 字节，以及本服务使用 `o200k_base` 计算的 5000 个词元**。首尾空白也计数，不得全为空白。这是本标准服务的运营限制；独立 Flare / Sunburst 的官方 32000 字符事实保持不变。本服务的词元计数用于请求准入，不代表供应商最终计费量，也不保证单次采购成本上限。\n\n工作台的角色描述仍沿用原输入长度限制，但最终拼接后的完整提示词还要满足上述三项限制。部分包含大量四字节字符或词元较多的原 4000 字符长描述会因此被拒绝；不能把“4000 字符可输入”理解为所有组合都能提交成功。服务不会截断、压缩或替换提示词。\n\n多图输出、多参考、更高质量、JPEG / WebP 输出、未列出尺寸、遮罩、透明背景及其他未经审核的扩展参数会明确拒绝，不自动降级。已识别标准路线的公开请求返回 HTTP 400，且不创建供应商任务、不预留生成费用。工作台可能先排队后检查；超限任务会明确无费失败，不能据此承诺所有工作台输入都即时返回 HTTP 400。无法识别型号或分组的畸形请求沿用原分发错误。",
        "## Prompt limits and rejected requests\n\nThe complete prompt must satisfy all three limits: **8192 Unicode code points, 16384 UTF-8 bytes, and 5000 tokens counted by this service with `o200k_base`**. Leading and trailing whitespace counts, and whitespace-only prompts are invalid. These are this standard service's operating limits; the vendor's 32000-character limit for separate Flare / Sunburst models is unchanged. The service token count determines request eligibility; it does not represent final supplier billing usage or guarantee a per-request procurement cost ceiling.\n\nThe workbench retains its existing character-description input limit, but the final assembled prompt must also satisfy all three limits above. Some existing 4000-character descriptions containing many four-byte characters or a high token count are therefore rejected. Being able to enter 4000 characters does not guarantee that every combination can be submitted. The service does not truncate, compress, or replace the prompt.\n\nMultiple output images, multiple references, higher quality, JPEG / WebP output, unlisted sizes, masks, transparent backgrounds, and other unreviewed extensions are explicitly rejected without a silent downgrade. Identified standard-route public requests return HTTP 400 without creating a supplier task or reserving generation funds. The workbench may queue a task before validating it; an over-limit task fails explicitly without a charge. This does not promise an immediate HTTP 400 for every workbench input. Malformed requests whose model or group cannot be identified retain the existing routing error.")
    pricing = localized(zh,
        "## 报价与线路\n\n角色工作台自动选择已审核且支持本次输入的线路，无需用户选择供应商。同一账户档位、相同标准请求采用统一每张报价，实际金额以提交前报价为准；换用合格候选线路不会追加费用。本页不把供应商采购价或历史基础价当作客户实付价。\n\n系统仅在能够证明首选没有创建供应商任务，且内置重试规则和总预算允许时尝试下一条合格线路。备用必须经过审核；本页不承诺当前始终有两条健康线路。",
        "## Quotes and routing\n\nThe character workbench automatically selects reviewed routes compatible with the current input; users do not need to choose a supplier. The same account tier and standard request receive a consistent per-image quote. The amount shown before submission is authoritative; switching to an eligible route does not add a charge. Supplier procurement costs and historical base prices are not presented here as the final customer price.\n\nThe system may try the next eligible route only when it can prove that no supplier task was created on the first route and the native retry rules and total attempt budget allow it. A backup must be reviewed. This page does not promise that two healthy routes are always available.")
    completion = localized(zh,
        "## 任务受理与完成\n\n返回异步任务编号表示已接单，不代表图片已经完成。继续查询原任务直到取得可打开的图片或明确最终状态。超时、断连、缺回执等结果不明情况，以及已经接单的任务，会继续核对原单，不会自动重复生成。已失败的旧任务不会因本次更新自动重发。\n\n其他既有独立型号（`gpt-image-2.5-hd`、`gpt-image-2.5-flare`、`gpt-image-2.5-sunburst`）保留各自合同；本页的单图、单参考和运营提示词上限不能外推为它们的新限制，也不能由底层更宽能力推导标准服务已开放全部规格。",
        "## Task acceptance and completion\n\nAn asynchronous task ID confirms acceptance, not image completion. Continue polling the original task until a usable image or an explicit final state is available. Timeouts, disconnections, missing acknowledgements, and accepted tasks are reconciled against the original task rather than automatically submitted again. This update does not automatically resubmit old failed tasks.\n\nOther existing separate models (`gpt-image-2.5-hd`, `gpt-image-2.5-flare`, and `gpt-image-2.5-sunburst`) retain their own contracts. The one-image, one-reference, and operating prompt limits on this page must not be applied to them as new restrictions. Likewise, broader underlying model capabilities do not mean every specification is available through the standard service.")
    body = "\n\n".join((f"<Warning>\n{notice}\n</Warning>", heading, introduction, table, dimensions, references, prompt, pricing, completion))
    task_example = json.dumps({"id": "task_example", "object": "image.generation.task", "model": STANDARD_MODEL, "status": "pending", "created": 0}, ensure_ascii=False)
    page = ROOT / lang / "api-reference/image-series/gpt-image/generate.mdx"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(f'''---
title: "{title}"
sidebarTitle: "{title}"
description: "{description}"
openapi: "openapi/ops/image/{lang}/gpt-image.json POST {PATH}"
---

{body}

<Panel>
<RequestExample>

```bash curl
curl --request POST \\
  --url https://api.omnimux.ai/v1/images/generations \\
  --header 'Authorization: Bearer <token>' \\
  --header 'Content-Type: application/json' \\
  --data '{json.dumps(example, ensure_ascii=False)}'
```

</RequestExample>
<ResponseExample>

```json 200 — illustrative async task
{task_example}
```

```json 400
{{"error":{{"message":"Unsupported standard image request","type":"invalid_request"}}}}
```

```json 402
{{"error":{{"message":"Insufficient quota","type":"insufficient_quota"}}}}
```

</ResponseExample>
</Panel>
''')
