# OmniMux Docs

Public documentation for [OmniMux](https://omnimux.ai) — unified AI gateway.

Built with [Mintlify](https://mintlify.com). Content lives in this repository only (not in the product monorepo).

## Local development

```bash
git clone https://github.com/laozhong86/OmniMux-docs.git
cd OmniMux-docs
npm i -g mint   # optional; or use npx
mint dev
```

Preview: [http://localhost:3000](http://localhost:3000)

## Structure

| Path | Purpose |
| --- | --- |
| `docs.json` | Site config, nav, i18n, OpenAPI |
| `cn/` | Chinese pages (default locale) |
| `en/` | English pages |
| `openapi/relay.json` | Gateway OpenAPI snapshot for API reference |
| `logo/` | Brand logos |

## Publishing

1. Install the [Mintlify GitHub App](https://dashboard.mintlify.com/settings/organization/github-app) for **this repo only**
2. Push to `main` → Mintlify deploys automatically
3. Custom domain (recommended): `docs.omnimux.ai` → CNAME `cname.mintlify.builders` (**DNS only / grey cloud** on Cloudflare)

## Product wiring

In the OmniMux console (System settings → General):

```text
general_setting.docs_link = https://docs.omnimux.ai
```

(Use the temporary `*.mintlify.app` URL until the custom domain is live.)

## OpenAPI sync

Source of truth: product repo `docs/openapi/relay.json`.

```bash
# from product checkout
python3 - <<'PY'
# or: cp docs/openapi/relay.json ../OmniMux-docs/openapi/relay.json
# then re-run the clean script if you maintain one
PY
cp docs/openapi/relay.json ../OmniMux-docs/openapi/relay.json
```

Prefer a small cleaner (strip unimplemented ops, set `servers`) before publish — see git history for the Phase 1 transform.

## Ops layout

```text
~/Desktop/Project/
├── OmniMux/         # product
└── OmniMux-docs/    # this repo — docs day-to-day work
```

Do not nest Mintlify sources inside the product tree.
