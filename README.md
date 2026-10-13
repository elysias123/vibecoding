# vibecoding

> 面向编程任务的 Agent Skill：少做无关工作，完成必要实现，并用与风险相称的验证交付结果。

[English](./README_EN.md)

`vibecoding` 是一份可复用的编程工作规范，也提供面向 Codex 与 Claude Code 的可选插件入口。它不替代你的项目规则、测试或权限控制；它帮助编码代理在明确范围内选择最小完整方案，避免无意义的重试、过度设计和无关改动。

## 适用场景

- 功能开发、缺陷修复、重构、测试、构建、CI、配置、基础设施和模式变更；
- 希望代理先理解受影响代码与约束，再做最小完整修改；
- 希望把验证范围与改动风险匹配，而非机械执行整套检查；
- 希望在重复失败时分析根因或切换方法，而不是无限重试。

不适用于纯问答、翻译、摘要或与工程交付无关的任务。

## 提供什么

### 核心 Skill

`skills/vibecoding/SKILL.md` 定义编程工作的默认行为：

- 保持任务范围、现有架构、权限边界和用户指定实现；
- 优先复用现有代码、平台能力和已安装依赖，不为小需求引入新框架或抽象；
- 为非平凡逻辑保留聚焦测试或自检；
- 用真实运行证据验证真实服务，不把构建通过当作部署完成；
- 同一方案连续失败后切换合理方法，并清楚说明原始错误与取舍；
- 默认使用中文沟通，同时保留代码、命令、路径和错误原文的原始形式。

### 可选重复失败 Guard

插件中的 Hook 尝试把“同一方案连续失败后不要无限重试”落实到 shell 调用：在**同一宿主、会话、工作目录和原始命令文本**内，两个明确失败会使下一次相同调用在执行前被拒绝。

- 使用 Python 标准库和 SQLite，不需要 `pip`；
- 只保存计数键摘要、最近退出码和调用去重记录，不保存完整命令或完整输出；
- 成功只清除该命令自己的计数；
- 支持带理由的定向 reset；
- 不解析 shell 语义，不重写命令，也不拦截 MCP、浏览器或其他专用工具。

## 快速开始

### 只安装 Skill

需要 Node.js 与 `npx`。以下命令从本仓库选择 `vibecoding` skill，安装时保留交互确认以便先审阅内容：

```bash
npx skills add elysias123/vibecoding --skill vibecoding
```

也可以指定目标 Agent，例如：

```bash
npx skills add elysias123/vibecoding --skill vibecoding --agent codex
```

只安装 Skill 不会启用 Hook Guard。

### 安装 Codex 插件

仓库包含 Codex marketplace 清单和插件清单。公开仓库版本包含本次文件后，可直接添加远程 marketplace：

```powershell
codex plugin marketplace add elysias123/vibecoding
codex plugin add vibecoding@vibecoding
```

安装后在 Codex 的 `/hooks` 中逐项审阅并信任本插件 Hook，再开启新会话。插件安装不等于 Hook 已启用。

### 安装 Claude Code 插件

在 Claude Code 会话中输入：

```text
/plugin marketplace add elysias123/vibecoding
/plugin install vibecoding@vibecoding
```

或在终端中运行：

```bash
claude plugin marketplace add elysias123/vibecoding
claude plugin install vibecoding@vibecoding
```

## 使用方式

Skill 在编程任务中可由支持 Skill 的宿主自动选择；也可按宿主界面中显示的 `vibecoding` Skill 名称显式调用。`/vibecoding on/off` 仅控制 Skill 指令是否启用，**不会关闭已经安装和受信任的 Hook**。

Skill 的重点不是强制固定流程，而是让代理在实际约束下作出更小、更完整的改动：

1. 阅读任务触及的代码、规则、调用方和验证方式；
2. 选择现有实现、标准库、平台能力或已安装依赖中最小可行的一层；
3. 补齐会被改动影响的调用方、测试、配置或文档；
4. 只运行能证明受影响行为的必要验证；
5. 说明已验证结果与会影响使用的未验证边界。

## Guard 行为与状态

Guard 的键为：

```text
宿主 + 会话 ID + 规范化工作目录 + 原始命令文本
```

| 完成结果 | 处理 |
| --- | --- |
| 明确非零退出码 | 对该键的连续失败数加一 |
| 明确零退出码 | 清除该键的失败数 |
| 正在运行、中断、未知结果或 Hook 错误 | 不计数 |
| 已有两次明确失败 | 在 `PreToolUse` 拒绝下一次相同调用 |

默认状态库位于系统临时目录下的 `vibecoding-retry-guard/state.sqlite3`。它可能被系统临时文件清理；不应将它当作审计日志或安全边界。

如需在修复问题或得到明确重试要求后清除单条记录，请使用 [Hook 指南中的定向 reset 步骤](./skills/vibecoding/references/hooks.md#定向-reset)。该指南还包含手动接入、移除、数据库清理与真实宿主验收方法。

## 支持状态

| 能力 | 状态 |
| --- | --- |
| 作为独立 Skill 使用 | 支持 |
| Claude Code 插件发现与 Hook 配置 | 支持；失败计数受宿主事件字段限制 |
| Codex 插件发现与 Hook 配置 | 支持；当前退出码协议不足，完整 Guard 受阻 |
| Windows 脚本级测试 | 已验证 |
| macOS / Linux 与真实宿主 Hook 会话 | 待验证 |

Hook 是工作流护栏，不是安全沙箱：它不能撤销已放行的并行调用，也不覆盖不经过本地 Hook 路径的工具。

## 致谢

本项目参考或受益于以下项目与文档：

- [vuejs-ai/skills](https://github.com/vuejs-ai/skills) 与 [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)：Skill 生态与组织方式；
- [Anthropic Claude Code](https://github.com/anthropics/claude-code) 与 Claude Code Plugin / Hook 文档：插件与事件协议；
- [OpenAI Codex](https://github.com/openai/codex) 与 Codex Hook 文档：插件和 Hook 接入；
- [npxskills](https://github.com/dz3ai/npxskills)：跨 Agent Skill 安装工具；
- [Ponytail](https://github.com/DietrichGebert/ponytail)：保持改动最小且完整的工程取向；
- [Stop That Shit](https://github.com/lennney/stop-that-shit)：多宿主 Skill + Hook 插件目录布局的参考；
- [talk-normally](https://github.com/hexiecs/talk-normal)：直接、清晰的沟通取向。

以上项目均归其各自作者与维护者所有；本项目不代表与其存在隶属或官方合作关系。

## 许可证

本项目采用 [MIT License](./LICENSE)。
