# 重复失败 guard：安装、恢复与验收

设计目标是在同一宿主、会话、目录中，同一准确原始 shell 命令累计两次明确失败后，在 `PreToolUse` 拒绝第三次调用。阈值固定为 2，不自动 reset；只有可靠退出码 0 或定向 reset 才清该命令计数。

**当前 Codex 协议降级，不能完整计数或硬阻止所有路径。** 官方固定提交 [`be5296d4672f59205c1b8a76f46e74eae4f10d51`](https://github.com/openai/codex/blob/be5296d4672f59205c1b8a76f46e74eae4f10d51/codex-rs/core/src/tools/context.rs) 的 `post_tool_use_response` 直接产生 `JsonValue::String(truncated_output_with_policy)`，只有命令 stdout 正文，没有可信退出码头部。任何 Codex 字符串，包括 JSON 字符串或模拟宿主头，都警告并跳过，避免 stdout 伪造。必须由宿主提供可信结构化退出码，才能启用完整计数。当前配置是接入入口，不是已生效的完整硬约束。

**Claude 成功事件通常缺少退出码，不清旧计数。** 失败事件的稳定 `Exit code N` 第一行可用于计数，两次明确失败后的第三次相同调用仍会拒绝；修复后需定向 reset 或更完整宿主协议。

## 操作前提与启用

- Python 3.10+，只使用标准库，无需 pip。hook 子进程必须能找到 `python`；macOS/Linux 若只有 `python3` 或使用特定解释器，修改 command 的解释器。路径含空格时正确加引号。
- 宿主支持对应 hooks 协议，项目配置可加载，且本地/管理员设置未禁用 hooks。安装后分别审阅并信任当前定义，按宿主提示重新加载或开新会话；安装不等于 hooks 已启用。
- 子进程能读取脚本、写入数据库。宿主 export `PLUGIN_ROOT` 或 `CLAUDE_PLUGIN_ROOT`，入口在 Python 内拼接路径，不依赖 shell 变量展开。
- Windows、macOS、Linux 为兼容目标；当前只有 Windows 脚本级验证，macOS/Linux 和真实 Codex/Claude Code 待验证。本轮不执行安装或信任，无法证明真实宿主拦截。

默认数据库是 `tempfile.gettempdir()/vibecoding-retry-guard/state.sqlite3`。host namespace 隔离宿主，再按会话、目录、准确原始命令匹配。Windows 目录规范化大小写，POSIX 保留大小写，命令正文不改写。SQLite 事务更新，完成事件按 `tool_use_id` 去重；成功或 reset 不清完成去重历史。诊断不回显敏感命令。

Codex 本地 marketplace：

```powershell
codex plugin marketplace add D:/project/vibecoding-optimization
codex plugin add vibecoding@vibecoding
```

Claude Code：从仓库根目录执行：

```powershell
claude plugin marketplace add ./
claude plugin install vibecoding@vibecoding
```

两个 marketplace 和 plugin 名均为 `vibecoding`，插件版本 `0.1.0`，source 指根目录 `./`。Claude marketplace 必填的 owner 使用项目名 `vibecoding`，不声明个人作者。

Codex manifest 显式声明 `skills: ./skills/` 与 `hooks: ./hooks/codex-hooks.json`；Claude manifest 声明同一 skills 路径，默认发现 `hooks/hooks.json`，不再重复注册 hooks。所有 handler 同步，`timeout: 5`，不配置 async。

插件 bootstrap 命令仅通过 Python 启动，两个宿主只替换 `--host`：

```text
python -c "import os,runpy;runpy.run_path(os.path.join(os.environ.get('PLUGIN_ROOT') or os.environ['CLAUDE_PLUGIN_ROOT'],'skills','vibecoding','scripts','retry_guard.py'),run_name='__main__')" --host codex
```

仅通过 `npx skills elysias123/vibecoding` 安装技能不启用 guard；`/vibecoding on/off` 不影响已装 hooks。

## 事件协议与边界

| 宿主 | 事件 | matcher |
| --- | --- | --- |
| Codex | `PreToolUse` / `PostToolUse` | `^Bash$` |
| Claude Code | `PreToolUse` / `PostToolUse` / `PostToolUseFailure` | `^(Bash|PowerShell)$` |

Codex 只接受 object 中明确整数 `exit_code` / `exitCode`，且不在运行的响应；全部字符串不可信。Claude `PostToolUse` 也只接受明确整数退出码、已完成的响应：0 清本命令计数，非零计失败，不从“成功事件”推断 0。Claude 官方 Bash 成功示例只有 `stdout`、`stderr`、`interrupted`、`isImage`；tools reference 明确 `rg`/`grep` 退出 1、`robocopy` 退出 0..7 也可被视为成功，故缺退出码只能警告并跳过，不清旧计数。

Claude 失败仅解析 `PostToolUseFailure.error` 第一行精确 `Exit code N`；`is_interrupt` 跳过，后续错误正文不是协议。未知协议、身份不完整或脚本内部数据库错误 fail-open：简短 `systemMessage` 后跳过；不按 error 关键词猜测。解释器无法启动或宿主取消超时 hook 时，脚本无法发消息，行为由宿主决定。

只使用原始参数的目录或事件 cwd，不解析 shell 命令。内部 `cd` 无法可靠识别时，计数使用宿主提供的 cwd；命令空白、换行不同即不同键。已并行放行的调用不取消，专门工具不经过这些 handler，无 MCP/其他宿主支持，不承诺安全沙箱。

Codex 后台原始完成支持仍待真实验收，且当前 stdout-only 响应同样降级；运行中响应不计数。Claude 后台 `TaskOutput` 不计数。临时 DB 可能被操作系统清理，从而丢失计数与去重历史。本项目不扩展 host patch、wrapper、transcript 或日志读取器。

## 项目手动 Codex 配置

不安装插件时，将 [hooks.example.json](../hooks/hooks.example.json) 的两项 handler 合并到目标项目 `.codex/hooks.json`，保留其他 hooks。按实际脚本路径和 Python executable 修改两项 command，示例使用：

```text
python D:/project/vibecoding-optimization/skills/vibecoding/scripts/retry_guard.py --host codex
```

这是手动项目配置，不是全局自动启用。仍需信任项目配置和 hooks，并受相同协议降级限制。插件和手动方案选一种，不重复注册；不要覆盖已有 hooks 文件。

## 定向 reset

只有修复失败原因或用户明确要求重试后才 reset，不为绕过拒绝而自动清零。它只删除目标失败计数，保留完成去重历史。取得真实 `session_id` 和执行目录，替换下面 `ID`、`D:/work` 与实际脚本路径；Claude 改用 `--host claude`。

命令正文从 stdin 输入，不在 argv 重复暴露密钥。推荐 PowerShell JSON 字符串，保留准确换行：

```powershell
$scriptPath = 'D:/project/vibecoding-optimization/skills/vibecoding/scripts/retry_guard.py'
$sessionId = 'ID'
$eventCwd = 'D:/work'
# $command 为原调用准确文本，包括原有空白与换行。
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$command | ConvertTo-Json -Compress | python $scriptPath reset --host codex --session-id $sessionId --cwd $eventCwd --reason '已修复失败原因'
```

stdin 可以是 JSON 字符串（解析后保留其精确换行）或原始文本（保留全部 stdin 字符）。JSON 文档外的管道换行不影响字符串；原始文本管道的额外换行会改变键。不要 trim 或重写命令。命令含密钥时避免将值粘贴到 shell 历史。

macOS/Linux 原始文本输入：

```sh
printf '%s' "$command" | python3 /absolute/path/skills/vibecoding/scripts/retry_guard.py reset --host codex --session-id ID --cwd /absolute/work --reason '已修复失败原因'
```

查看默认库路径：

```powershell
python $scriptPath path
```

独立测试库可加 `--database`；hook、reset 和 path 必须指同一库：

```powershell
$command | ConvertTo-Json -Compress | python $scriptPath reset --host codex --session-id $sessionId --cwd $eventCwd --reason '已修复失败原因' --database D:/tmp/vibecoding-acceptance.sqlite3
python $scriptPath path --database D:/tmp/vibecoding-acceptance.sqlite3
```

## 移除与数据库清理

- 通过对应宿主插件管理界面移除 `vibecoding`，按提示重新加载。不要移除其他插件；`/vibecoding off` 不会停 hooks。
- 手动合并配置时，只移除 command 指向本 guard 的两项 Codex handler 或三项 Claude handler；同一事件的其他 handler、用户和其他插件 hooks 全部保留。容器仍有其他内容时不要删整个容器/文件。
- 卸载不自动删状态。需要整库删除时，先停止所有读写该库的宿主会话与 hook 进程，用 `python SCRIPT path` 确定绝对路径，再仅删除该精确数据库文件及其确实存在的 SQLite 伴随文件。不要递归删临时目录，不用通配符。整库删除会清除所有宿主/会话计数和去重历史，通常优先定向 reset。

## 待执行的真实验收

聚焦测试直接调用共享实现，并解析清单和启动两个 Hook 入口。可从仓库根目录复现：

```powershell
$env:PYTHONUTF8 = '1'
python -B -m unittest discover -s D:/project/vibecoding-optimization/skills/vibecoding/scripts -p test_retry_guard.py -v
```

这些测试使用独立临时数据库和模拟事件，不会安装或信任 hooks，也不能证明真实宿主已拒绝执行。

将 `UNIQUE` 换成独有标识，在真实宿主新会话、固定 cwd 中通过被覆盖的 shell 工具调用下列无害命令；它只追加临时标记并退出 7：

```text
python -c "import pathlib,tempfile; p=pathlib.Path(tempfile.gettempdir())/'vibecoding-guard-acceptance-UNIQUE.txt'; p.open('a',encoding='utf-8').write('ran\n'); raise SystemExit(7)"
```

1. Claude 两次明确失败应产生两行标记，第三次同一准确调用应拒绝，文件仍为两行。普通终端不触发宿主 hooks，不能用于证明拦截。当前 Codex stdout-only 路径应警告跳过，不能期待完整计数；只有拿到可信结构化退出码的宿主版本，才做其两失败第三拒绝验收。
2. 用真实 host/session/cwd 和准确原命令定向 reset，再调用一次应放行，增加一行标记；这是明确请求的无害重试。
3. 独立测试库集中验证成功仅清本命令、去重、reset 保留完成历史及 host/session/cwd/命令隔离；POSIX 大小写与 macOS/Linux 实际行为另行验证。
4. Codex 字符串（含 JSON 或假头）警告跳过；Claude 无退出码成功不清零，中断及未知失败格式跳过。不得把输出里的模拟退出码当宿主证据。
5. Codex 后台原始命令与最终事件关联需实际观察，当前继续标待验证；Claude 后台 TaskOutput 不计数，已放行并行调用及专门工具不作为拦截成功。

交付状态应区分：实现与配置完成；完整 Codex 约束被宿主协议阻塞；真实宿主、后台及其他 OS 未验证。

## 官方参考

- [Codex hooks](https://developers.openai.com/codex/hooks)：事件、环境变量、信任与项目配置。
- [Codex 固定 SHA 核心实现](https://github.com/openai/codex/blob/be5296d4672f59205c1b8a76f46e74eae4f10d51/codex-rs/core/src/tools/context.rs)：stdout-only 响应反证。
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)：成功/失败事件与稳定退出码头。
- [Claude tools reference](https://code.claude.com/docs/en/tools-reference)：非零退出码仍被视为成功的情况。
- [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference) 与 [marketplace](https://code.claude.com/docs/en/plugin-marketplaces)：默认 hooks 发现、本地安装。
