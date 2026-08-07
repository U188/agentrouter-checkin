# AgentRouter 自动签到（GitHub Actions）

针对 https://agentrouter.org 的每日签到（领额度）自动化。

## Secrets 配置

在仓库 **Settings → Secrets and variables → Actions** 添加：

| Secret | 必填 | 说明 |
|---|---|---|
| `AGENTROUTER_SESSION` | ✅ | 登录 https://agentrouter.org 后，F12 → Application → Cookies → 复制 `session` 的值 |
| `AGENTROUTER_USER_ID` | 可选 | 用户 ID（一般不填也行，脚本会动态获取） |
| `TG_BOT_TOKEN` / `TG_CHAT_ID` | 可选 | Telegram 通知 |

## 手动获取 SESSION（一次性）

1. 浏览器登录 https://agentrouter.org
2. 按 F12（或右键 → 检查）
3. 顶部切到 **Application / 应用程序 → Cookies → https://agentrouter.org**
4. 找到名为 `session` 的 Cookie，双击复制它的值
5. 粘贴到上面的 `AGENTROUTER_SESSION` Secret

> 注意：该站有阿里云 WAF 滑块。脚本会用无头浏览器尽力放行（获取 `acw_tc`/`acw_sc__v2` cookie）。
> 若阿里云强制要求人工滑块，脚本会提示需要手动过滑块，此时的结果也会即时推送到 Telegram。