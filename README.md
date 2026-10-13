# vibecoding

[中文](./README.md) | [English](./README_EN.md)

这是一个面向编程任务的技能，可以提升 vibecoding 过程中的体验，并提升代码的可靠性、可读性与可维护性。

仓库同时提供 Codex 与 Claude Code 插件：设计目标是同一宿主、会话、目录中的同一原始 shell 命令累计两次明确失败后拒绝下一次相同调用；但当前 Codex 官方响应协议只给出 stdout 字符串，无法可靠完成计数，因此 Codex 目前属于协议降级，不能宣称覆盖全部路径。

## 安装与启用

仅安装技能：

```bash
npx skills elysias123/vibecoding
```

技能在编程任务中自动激活，也可使用 `/vibecoding on/off` 控制。仅安装技能不会启用失败 guard；该开关也不会关闭已经安装并信任的 hooks。

插件版本为 `0.1.0`，需要 Python 3.10+（标准库，无需 pip）、支持对应 hooks 协议的宿主，以及可写的系统临时目录。hook 进程必须能通过 `python` 找到解释器；macOS/Linux 若只提供 `python3`，或需要指定虚拟环境，请先修改 hook command 中的解释器。插件由宿主提供根目录环境变量，不依赖当前 shell 的变量展开。

Codex 本地 marketplace 安装：

```powershell
codex plugin marketplace add D:/project/vibecoding-optimization
codex plugin add vibecoding@vibecoding
```

Claude Code 在本仓库根目录执行：

```powershell
claude plugin marketplace add ./
claude plugin install vibecoding@vibecoding
```

安装后分别在各宿主中审阅并信任本插件 hooks，按宿主提示重新加载或开启新会话；插件安装本身不等于 hooks 已启用。Codex 必须允许项目配置且 hooks 功能未被本地或管理员配置禁用；Claude Code 的 hooks 也须未被设置禁用。不要同时注册插件 hooks 与项目手动示例。

完整的[操作前提、项目手动启用、定向重置、移除和真实宿主验收步骤](./skills/vibecoding/references/hooks.md)见 hooks 文档。

## 协议与覆盖限制

- Codex 监听 `PreToolUse` / `PostToolUse` 的 `^Bash$`；Claude Code 监听这两个事件及 `PostToolUseFailure` 的 `^(Bash|PowerShell)$`。处理同步完成，超时 5 秒。
- **Codex 协议降级（未覆盖）**：固定提交 [`be5296d`](https://github.com/openai/codex/blob/be5296d4672f59205c1b8a76f46e74eae4f10d51/codex-rs/core/src/tools/context.rs) 的 `post_tool_use_response` 直接产生 `JsonValue::String(truncated_output_with_policy)`，只有命令 stdout 正文，没有可信退出码头部。Codex 的任意字符串，包括 JSON 字符串或宿主头模拟，均跳过并给出 warning；只有事件对象中明确整数 `exit_code` / `exitCode` 才能计数。因此当前 Codex hooks 不能完整计数或硬阻止所有路径，需宿主提供可信结构化退出码；不使用 wrapper、transcript 日志或 host patch。
- Claude 的成功事件通常没有退出码；本 guard 只接受已完成响应中明确的整数 `exit_code` / `exitCode`。缺少可靠退出码时警告并跳过，**不清旧计数**。两次明确失败后的第三次相同调用仍会被拒绝，修复后需定向 reset 或更完整的宿主协议。
- Claude 失败只读取 `PostToolUseFailure.error` 第一行的精确 `Exit code N`；中断跳过。未知协议不通过 `error` 关键词猜测结果，而是简短警告并跳过。
- 只匹配原始命令文本和宿主提供的目录，不分析 shell 内部 `cd`；不拦截已并行放行的调用，不覆盖专门工具或 MCP，不承诺安全沙箱。
- Codex 后台原始完成事件支持待真实验收；Claude 后台 `TaskOutput` 不计数。临时数据库可能被操作系统清理。

兼容目标是 Windows、macOS、Linux；当前脚本级验收范围仅为 Windows；Codex 因官方响应字段不兼容处于协议阻塞，Claude 成功事件也通常缺少退出码。其他操作系统与两个真实宿主尚未验证，不能把配置入口描述成完整防护。项目内实现已通过 Windows 聚焦测试；尚未安装或信任 hooks，测试不代表真实宿主已启用。

## 致谢

- [vuejs-ai/skills](https://github.com/vuejs-ai/skills)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [hexiecs/talk-normally](https://github.com/hexiecs/talk-normal)
