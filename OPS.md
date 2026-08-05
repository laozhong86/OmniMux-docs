# OmniMux Docs — 运维清单

面向人类与 Agent 的落地操作清单。文档站与产品仓隔离。

## 域名（唯一主域，无旧域兼容）

| 角色 | 主机 |
| --- | --- |
| 控制台 / 站点 | `https://omnimux.ai` |
| API 网关 | `https://api.omnimux.ai` |
| 文档 | `https://docs.omnimux.ai` |

用户文档、OpenAPI `servers`、控制台 `docs_link` / `server_address` 只写上表。不双写、不引导已退役主机。

## 已完成（Phase 1 内容）

- [x] 独立仓 `OmniMux-docs` + 本地兄弟目录
- [x] Mintlify 品牌壳（`docs.json`、logo、主题色 Signal Acid）
- [x] 中/英：首页、快速开始、鉴权、模型
- [x] 网关 OpenAPI：`openapi/relay.json`（已过滤「未实现」、补 `servers`）

## 你需要完成的 Dashboard / DNS

### 1. 绑定 GitHub App

1. 打开 [Mintlify Dashboard](https://dashboard.mintlify.com)
2. 安装 GitHub App，**只授权** `laozhong86/OmniMux-docs`
3. 生产分支：`main`
4. 推送后确认 Deployment 成功
5. 记下临时域名：`https://<subdomain>.mintlify.app`（以面板为准）

### 2. 自定义域名 `docs.omnimux.ai`

1. Dashboard → Custom domain → 添加 `docs.omnimux.ai`
2. Cloudflare（或其它 DNS）添加：
   - 类型：`CNAME`
   - 名称：`docs`
   - 目标：`cname.mintlify.builders`（以面板显示为准）
   - **代理状态：仅 DNS（灰云）** — 橙云会导致 1014
3. 按面板添加验证 TXT（如有）
4. 面板 Retry validation，直到 HTTPS 正常

**禁止：** 把根域 `@` CNAME 到 Mintlify（会冲掉主站）。

### 3. 产品入口 `docs_link`

控制台 → 系统设置 → 通用：

```text
docs_link = https://docs.omnimux.ai
```

## 日常维护

| 动作 | 在哪里做 |
| --- | --- |
| 改 MDX / 导航 | 本仓 `cn/` `en/` `docs.json` |
| 更新 OpenAPI | 产品仓改 `docs/openapi/relay.json` → 同步到本仓 `openapi/` |
| 预览 | `mint dev` |
| 发布 | `git push origin main` |

## 验收

1. `mint dev` 本地中/英首页与 Quickstart 可打开
2. push 后 Mintlify 部署成功
3. API 参考 Tab 能展开 endpoints
4. `docs.omnimux.ai` HTTPS 正常（域名步骤完成后）
5. 控制台顶栏 Docs 指向新站

## API 域名 `api.omnimux.ai`

Railway 已添加自定义域 `api.omnimux.ai`。在 Cloudflare（omnimux.ai 区）添加：

| Type | Name | Target | Proxy |
| --- | --- | --- | --- |
| CNAME | `api` | `s36b9wzi.up.railway.app` | 可橙云或灰云（按你现有 `omnimux.ai` 习惯） |
| TXT | `_railway-verify.api` | `railway-verify=7d8c0937664f021129067ded9b243bd2e9cf1756df25d5ad20a10097220f014b` | 仅 DNS |

验收：`curl -sS https://api.omnimux.ai/api/status` 返回 JSON；`curl -sS https://api.omnimux.ai/v1/models -H "Authorization: Bearer $KEY"` 可鉴权。

## Production P0 harden (2026-08-01)

Applied on live OmniMux:

| Control | Value |
| --- | --- |
| RegisterEnabled | false |
| PasswordRegisterEnabled | false |
| PasswordLoginEnabled | true |
| passkey.enabled | false |
| passkey.rp_id | omnimux.ai |
| passkey.origins | https://omnimux.ai,https://omnimux.ai/dashboard |
| docs_link | https://docs.omnimux.ai |
| server_address | https://omnimux.ai |
| API domain | https://api.omnimux.ai |

Secrets (local Keychain only, not in git):

- Admin password: service `omnimux/production/admin_password`, account `omnimux-production-admin`
- Session secret: service `omnimux/production/session_secret`, account `omnimux-production`

```bash
security find-generic-password -s 'omnimux/production/admin_password' -a 'omnimux-production-admin' -w
```

Backup:

```bash
# from OmniMux repo
python3 scripts/ops/mysql-backup.py
# output: ~/Desktop/Project/OmniMux-backups/new_api_*.sql.gz
```

Residual risks (not closed in P0):

- Railway MySQL/Redis still expose TCP proxy URLs (plugin default); prefer private network for routine ops
- MySQL/Redis passwords not rotated in this pass (shared plugin risk; schedule with downtime)
- Sibling `tokens` service deploy still failing (independent of OmniMux)
- No Turnstile keys yet (registration closed instead)
- Continuous monitoring: run `scripts/ops/prod-healthcheck.sh` via cron/launchd

