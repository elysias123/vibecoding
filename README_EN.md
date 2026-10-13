# vibecoding

[中文](./README.md) | [English](./README_EN.md)

This is a skill designed for programming tasks. It improves the vibecoding experience and enhances code reliability, readability, and maintainability.

Optional Codex and Claude Code plugins (`0.1.0`) are included. With reliable completion events, two explicit failures for the same host, session, directory and exact shell command deny the next identical call. A confirmed exit code 0 or a targeted reset clears only that command.

**Codex is currently protocol-degraded, not fully covered.** The official [fixed commit](https://github.com/openai/codex/blob/be5296d4672f59205c1b8a76f46e74eae4f10d51/codex-rs/core/src/tools/context.rs) returns command stdout as a string, without a trusted exit code. All Codex strings, including JSON strings and simulated headers, warn and skip. Full counting and hard blocking require a trusted structured exit-code response from the host.

## Installation

Requires Python 3.10+, a matching host hooks protocol and a writable temporary directory. No pip dependencies. Change `python` in hook commands to `python3` or an interpreter path if needed.

Skill only, without hooks:

```bash
npx skills elysias123/vibecoding
```

Codex local marketplace:

```powershell
codex plugin marketplace add D:/project/vibecoding-optimization
codex plugin add vibecoding@vibecoding
```

Claude Code, from this repository root:

```powershell
claude plugin marketplace add ./
claude plugin install vibecoding@vibecoding
```

Review and trust hooks separately in each host; ensure local/admin settings permit them and reload as instructed. Do not also register the manual example. `/vibecoding on/off` controls the skill, not installed hooks.

## Recovery and limits

Claude failure counting uses only the exact `Exit code N` first line of `PostToolUseFailure.error`; interrupts skip. Claude success events usually lack an exit code: without an explicit integer `exit_code`/`exitCode` in a completed response, warn and **do not clear old counts**. After a fix, use targeted reset or a fuller host protocol. Unknown formats warn and skip; no output-keyword guessing.

[Hooks guide (Chinese)](./skills/vibecoding/references/hooks.md): prerequisites, manual setup, exact JSON/raw stdin reset, removal and acceptance steps. Hooks are synchronous, timeout 5 seconds; Codex matches `^Bash$`, Claude `^(Bash|PowerShell)$`. No automatic reset.

Only exact commands and host-provided directories are matched; shell-internal `cd` is not analyzed. Already admitted parallel calls, dedicated tools, MCP and other hosts are outside coverage. Codex background completion remains unverified; Claude `TaskOutput` is not counted. Temporary state may be cleared by the OS. This is not a security sandbox; no host patch, wrapper or transcript parser is provided.

Windows script-level acceptance is separate from live-host coverage. macOS/Linux and both live hosts remain unverified; full Codex enforcement is host-protocol-blocked. The focused tests pass on Windows; hooks have not been installed or trusted. Passing tests does not prove live enforcement.

## Thanks

- [vuejs-ai/skills](https://github.com/vuejs-ai/skills)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [hexiecs/talk-normally](https://github.com/hexiecs/talk-normal)
