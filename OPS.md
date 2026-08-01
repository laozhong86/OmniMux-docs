# OmniMux Docs — 运维清单

面向人类与 Agent 的落地操作清单。文档站与产品仓隔离。

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

### 2. 自定义域名 `docs.geminix.cc`

1. Dashboard → Custom domain → 添加 `docs.geminix.cc`
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
docs_link = https://docs.geminix.cc
```

域名未就绪时，可先填 Mintlify 临时域名。

可选：产品仓默认值仍是 `https://docs.newapi.pro`；改代码默认值另开产品 PR，与文档仓无关。

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
4. `docs.geminix.cc` HTTPS 正常（域名步骤完成后）
5. 控制台顶栏 Docs 指向新站
