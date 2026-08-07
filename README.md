# AgentRouter 自动签到（GitHub Actions）

针对 https://agentrouter.org 的每日签到自动化，完全仿照 U188/AnyRouter-Auto-Checkin 写法。

## Secrets 配置

fork 本项目 或 直接 push 到你自己的仓库后，在 **Settings → Secrets and variables → Actions** 添加：

| Secret 名称 | 是否必填 | 说明 |
|---|---|---|
| `SESSION` | 单账号必填 | 登录后 cookie 的 `session` 值。**多账号时用逗号分隔**，如 `sess1,sess2` |
| `SESSIONS` | 多账号(推荐) | JSON 数组，支持给每个账号起名，优先级最高 |
| `SESSION_IDS` | 可选 | 与 `SESSION` 逗号分隔对应的 `user_id` 列表（不填也能自动获取） |
| `USER_ID` | 可选 | 单账号用户 ID（不填自动获取） |
| `TG_BOT_TOKEN` / `TG_CHAT_ID` | ❌ 可选 | Telegram 通知 |

## 多账号配置（两种方式任选其一）

### 方式一：SESSIONS（JSON 数组，推荐，可命名）
在 `SESSIONS` Secret 填如下 **JSON 数组**（注意：必须用 `[ ]` 方括号，每个账号一对 `{ }`，用逗号分隔）：

```json
[
  {"name": "账号A", "session": "sessAAA...", "user_id": "1001"},
  {"name": "账号B", "session": "sessBBB...", "user_id": "1002"}
]
```

- `name` 可选（通知里显示）；`user_id` 可选（不填自动获取）。
- 也可以偷懒：`SESSIONS` 直接填逗号分隔的 session 字符串，如：
  ```
  sessAAA...,sessBBB...
  ```

### 方式二：SESSION + SESSION_IDS（逗号分隔）
`SESSION` 里用逗号放多个 session：
```
sessAAA...,sessBBB...,sessCCC...
```
`SESSION_IDS`（可选，与上面一一对应）：
```
1001,1002,1003
```

> 💡 配置后建议先去 **Actions → 你的工作流 → Run workflow** 手动跑一次验证。

## 手动获取 SESSION（一次性）

1. 浏览器登录 https://agentrouter.org
2. 按 F12（或右键 → 检查）
3. 顶部切到 **Application / 应用程序 → Cookies → https://agentrouter.org**
4. 找到名为 `session` 的 Cookie，复制它的值，填入仓库 `SESSION` Secret

## 工作流

- 定时：每天 `01:00 UTC`（北京时间 09:00）自动触发一次
- 手动：**Actions → AgentRouter Daily Check-in → Run workflow**
- 完成后会清理旧的 run 记录，保留最近 1 条