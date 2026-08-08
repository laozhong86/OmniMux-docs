# Field matrix (chat Complete baseline)

Source of truth for **documented** fields: OmniMux `openapi/relay.json`  
`ChatCompletionRequest` / related schemas. Do not invent competitor-only params.

## ChatCompletionRequest (gateway baseline)

| Field | Required | Notes |
| --- | --- | --- |
| `model` | yes | **Pinned** per page |
| `messages` | yes | string or multimodal content parts |
| `temperature` | no | 0–2 |
| `top_p` | no | |
| `n` | no | |
| `stream` | no | |
| `stream_options` | no | e.g. `include_usage` |
| `stop` | no | string or array |
| `max_tokens` | no | |
| `max_completion_tokens` | no | |
| `presence_penalty` | no | |
| `frequency_penalty` | no | |
| `logit_bias` | no | |
| `user` | no | |
| `tools` | no | when model supports |
| `tool_choice` | no | |
| `response_format` | no | |
| `seed` | no | |
| `reasoning_effort` | no | low/medium/high when supported |
| `modalities` | no | |
| `audio` | no | |

## Message

| Field | Notes |
| --- | --- |
| `role` | system/user/assistant/tool/developer |
| `content` | string **or** array of parts |
| `name` | optional |
| `tool_calls` / `tool_call_id` | tools flow |
| `reasoning_content` | reasoning models |

## MessageContent parts

`text` · `image_url` · `input_audio` · `file` · `video_url`

## Response (200)

`id` · `object` · `created` · `model` · `choices` · `usage` · `system_fingerprint`

## Error statuses (billed chat)

`400` `401` `402` `403` `404` `429` `500` `502` `503`

## Family notes (documentation emphasis only)

| Family | Emphasize in bullets / examples |
| --- | --- |
| GPT | multimodal content, tools |
| Claude | long context; tools when exposed via Chat |
| Gemini | multimodal |
| Kimi | reasoning_effort / reasoning_content when used |
| GLM | tools / thinking-related fields if present in request |
| MiniMax | tools / stream |
| DeepSeek | reasoning_effort when used |
| Grok | tools / reasoning when used |

**Honesty rule:** If a field is in relay schema, document it. If Evolink shows a field we do not expose, **omit** (default) unless product later adds it.

## Non-chat surfaces

Documented in later phases (image/video/social/publishing). Do not force chat matrix onto them.
