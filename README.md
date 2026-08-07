# AgentRouter 自动签到（GitHub Actions）

针对 https://agentrouter.org 的每日签到自动化，完全仿照 U188/AnyRouter-Auto-Checkin 写法。

## Secrets 配置

fork 本项目 或 直接 push 到你自己的仓库后，在 **Settings → Secrets and variables → Actions** 添加：

| Secret 名称 | 是否必填 | 说明 |
|---|---|---|
| `SESSION` | ✅ 必填 | 登录 https://agentrouter.org 后，F12 → Application → Cookies → 复制 `session` 的值 |
| `USER_ID` | 可选 | 用户 ID。不填时脚本会通过 `/api/user/self` 自动获取 |
| `TG_BOT_TOKEN` | ❌ 可选 | Telegram Bot Token（通知用） |
| `TG_CHAT_ID` | ❌ 可选 | Telegram Chat ID |

## 手动获取 SESSION（一次性）

1. 浏览器登录 https://agentrouter.org
2. 按 F12（或右键 → 检查）
3. 顶部切到 **Application / 应用程序 → Cookies → https://agentrouter.org**
4. 找到名为 `session` 的 Cookie，复制它的值，填入仓库 `SESSION` Secret

## 工作流

- 定时：每天 `01:00 UTC`（北京时间 09:00）自动触发一次
- 手动：**Actions → AgentRouter Daily Check-in → Run workflow**
- 完成后会清理旧的 run 记录，保留最近 1 条