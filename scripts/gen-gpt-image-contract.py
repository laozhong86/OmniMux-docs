#!/usr/bin/env python3
"""Generate the bilingual GPT Image generation contract from the public model IDs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ["gpt-image-2.5", "gpt-image-2.5-hd"]
PATH = "/v1/images/generations"
example = {"model": MODELS[0], "prompt": "A product photo on a white background", "n": 1}
for lang in ("en", "zh"):
    zh = lang == "zh"
    title = "GPT Image · 图像生成" if zh else "GPT Image · Image generation"
    description = "使用 GPT Image 2.5 按次模型生成图像。" if zh else "Generate images with the GPT Image 2.5 per-call models."
    response = {"type": "object", "description": "响应可为图像结果或异步任务；按实际响应处理。" if zh else "The response can contain image results or an asynchronous task; handle the returned shape.", "properties": {
        "created": {"type": "integer"}, "data": {"type": "array", "items": {"type": "object", "properties": {"url": {"type": "string"}, "b64_json": {"type": "string"}}}},
        "id": {"type": "string", "description": "异步任务 ID（若返回）。" if zh else "Asynchronous task ID, when returned."},
        "object": {"type": "string"}, "model": {"type": "string"}, "status": {"type": "string"}}}
    op = {"summary": title, "operationId": "generateGPTImage", "description": description, "security": [{"BearerAuth": []}], "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "required": ["model", "prompt"], "properties": {
        "model": {"type": "string", "enum": MODELS, "default": MODELS[0]}, "prompt": {"type": "string"},
        "n": {"type": "integer", "description": "图像数量，受所选模型和渠道限制。" if zh else "Image count, subject to the selected model and route limits."},
        "size": {"type": "string", "description": "可接受的尺寸取决于所选模型与渠道；不保证所有尺寸可用。" if zh else "Accepted sizes depend on the selected model and route; not every size is guaranteed."},
        "quality": {"type": "string", "description": "质量选项取决于所选模型与渠道。" if zh else "Quality options depend on the selected model and route."}}}, "example": example}}},
        "responses": {"200": {"description": "图像结果或已提交的异步任务。" if zh else "Image results or an accepted asynchronous task.", "content": {"application/json": {"schema": response}}}}}
    for status, text in {"400": "Invalid request", "401": "Authentication required", "402": "Insufficient quota", "403": "Forbidden", "429": "Rate limit exceeded", "500": "Server error"}.items():
        op["responses"][status] = {"description": text}
    spec = {"openapi": "3.0.3", "info": {"title": title, "version": "1.0.0"}, "servers": [{"url": "https://api.omnimux.ai"}], "paths": {PATH: {"post": op}}, "components": {"securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer"}}}}
    dest = ROOT / "openapi/ops/image" / lang / "gpt-image.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    notice = ("自 2026-09-10 起，`gpt-image-2` 和 `gpt-image-2-hd` 已分别更名为 `gpt-image-2.5` 和 `gpt-image-2.5-hd`。旧 model ID 不再接受；请更新请求中的 `model`。这不是兼容别名。" if zh else "Since September 10, 2026, `gpt-image-2` and `gpt-image-2-hd` have been renamed to `gpt-image-2.5` and `gpt-image-2.5-hd`. The old model IDs are no longer accepted. Update the `model` in your requests; these are not compatibility aliases.")
    text = ("这两个按次模型的基础价分别为 USD 0.0441/次和 USD 0.005479/次；分组倍率可能影响最终费用。本次更名未改变价格。\n\n返回 `data` 时读取图像结果；返回 `image.generation.task` 时表示异步任务已提交，不代表图像已生成。响应形态取决于实际路由，请勿将任务提交响应当作最终结果。\n\nFlare 和 Sunburst 是独立的 Token 计费模型，不属于此按次契约，目前尚未开放。" if zh else "The base prices for these per-call models are USD 0.0441/call and USD 0.005479/call, respectively; group multipliers may affect the final charge. This rename does not change prices.\n\nRead image results when `data` is returned. An `image.generation.task` response means an asynchronous task was submitted, not that an image is ready. The response shape depends on the route; do not treat task acceptance as the final result.\n\nFlare and Sunburst are separate token-billed models. They are not part of this per-call contract and are not yet available.")
    page = ROOT / lang / "api-reference/image-series/gpt-image/generate.mdx"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(f'---\ntitle: "{title}"\nsidebarTitle: "{title}"\ndescription: "{description}"\nopenapi: "openapi/ops/image/{lang}/gpt-image.json POST {PATH}"\n---\n\n<Warning>\n{notice}\n</Warning>\n\n{text}\n\n<Panel>\n<RequestExample>\n\n```bash curl\ncurl --request POST \\\n  --url https://api.omnimux.ai/v1/images/generations \\\n  --header \'Authorization: Bearer <token>\' \\\n  --header \'Content-Type: application/json\' \\\n  --data \'{json.dumps(example)}\'\n```\n\n</RequestExample>\n<ResponseExample>\n\n```json 200 — illustrative async task\n{{"id":"task_example","object":"image.generation.task","model":"gpt-image-2.5-hd","status":"pending","created":0}}\n```\n\n```json 402\n{{"error":{{"message":"Insufficient quota","type":"insufficient_quota"}}}}\n```\n\n</ResponseExample>\n</Panel>\n')
