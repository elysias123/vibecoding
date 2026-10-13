# vibecoding

> An Agent Skill for programming work: avoid unrelated work, complete the necessary implementation, and deliver results with verification proportional to risk.

[中文](./README.md)

`vibecoding` is a reusable set of programming-work conventions with optional plugin entry points for Codex and Claude Code. It does not replace your project rules, tests, or permission controls. It helps coding agents choose the smallest complete solution within a clear scope, avoiding pointless retries, overengineering, and unrelated changes.

## When to use it

- Feature development, bug fixes, refactoring, testing, builds, CI, configuration, infrastructure, and schema changes.
- Work where the agent should understand affected code and constraints before making the smallest complete change.
- Workflows that match the scope of validation to the risk of the change instead of mechanically running an entire checklist.
- Situations where repeated failures should trigger root-cause analysis or a change of method instead of endless retries.

It is not intended for pure Q&A, translation, summarization, or tasks unrelated to engineering delivery.

## What it provides

### Core Skill

`skills/vibecoding/SKILL.md` defines the default behavior for programming work:

- preserve task scope, existing architecture, permission boundaries, and user-specified implementation choices;
- reuse existing code, platform capabilities, and installed dependencies before adding a framework or abstraction for a small task;
- leave a focused test or self-check for non-trivial logic;
- use real runtime evidence for real service claims instead of treating a successful build as a completed deployment;
- change to a reasonable method after the same approach repeatedly fails, and clearly explain the original error and trade-off;
- communicate in Chinese by default while preserving code, commands, paths, APIs, and original error text.

### Optional repeated-failure Guard

The plugin Hook attempts to turn “do not endlessly retry the same failed approach” into a shell-call rule: for the **same host, session, working directory, and original command text**, two confirmed failures cause the next identical call to be denied before execution.

- Uses only the Python standard library and SQLite; no `pip` is required.
- Stores only key digests, the latest exit code, and call-deduplication data—not full commands or full output.
- A success clears only that command's own count.
- Supports targeted resets with a stated reason.
- Does not parse shell semantics, rewrite commands, or block MCP, browser, or other specialized tools.

## Quick start

### Install the Skill only

Node.js and `npx` are required. The following command selects the `vibecoding` skill from this repository and retains the interactive confirmation so you can inspect it before installation:

```bash
npx skills add elysias123/vibecoding --skill vibecoding
```

You can also target a specific agent, for example:

```bash
npx skills add elysias123/vibecoding --skill vibecoding --agent codex
```

Installing the Skill alone does not enable the Hook Guard.

### Install the Codex plugin

The repository includes a Codex marketplace manifest and plugin manifest. Once the public repository contains these files, add the remote marketplace directly:

```powershell
codex plugin marketplace add elysias123/vibecoding
codex plugin add vibecoding@vibecoding
```

After installation, review and trust each plugin Hook in Codex `/hooks`, then start a new session. Installing the plugin does not itself enable Hooks.

### Install the Claude Code plugin

Inside a Claude Code session, enter:

```text
/plugin marketplace add elysias123/vibecoding
/plugin install vibecoding@vibecoding
```

Or run in a terminal:

```bash
claude plugin marketplace add elysias123/vibecoding
claude plugin install vibecoding@vibecoding
```

Claude Code finds the plugin through `.claude-plugin/marketplace.json` at the repository root. Review the Hook definitions after installation and reload as directed by the client.

### Install from a local checkout

For development or unpushed changes, replace the remote repository parameter above with the current directory:

```powershell
codex plugin marketplace add D:/path/to/vibecoding-optimization
codex plugin add vibecoding@vibecoding
```

```bash
claude plugin marketplace add ./
claude plugin install vibecoding@vibecoding
```

Do not enable both the plugin Hooks and the [manual project configuration example](./skills/vibecoding/hooks/hooks.example.json), or the same event will be handled twice.

## Usage

A Skill-capable host can automatically select the Skill for programming tasks. You can also invoke it explicitly using the `vibecoding` Skill name shown by the host. `/vibecoding on/off` only controls whether the Skill instructions are enabled; it **does not disable Hooks that are already installed and trusted**.

The Skill is not about enforcing a fixed process. It helps the agent make smaller, more complete changes under real constraints:

1. Read the code, rules, callers, and verification methods touched by the task.
2. Choose the smallest workable layer among existing implementations, the standard library, platform capabilities, or installed dependencies.
3. Update callers, tests, configuration, or documentation affected by the change.
4. Run only the necessary validation that can prove the affected behavior.
5. State verified results and unverified limits that affect use.

## Guard behavior and state

The Guard key is:

```text
host + session ID + normalized working directory + original command text
```

| Completion result | Action |
| --- | --- |
| Confirmed non-zero exit code | Increment the consecutive-failure count for that key |
| Confirmed zero exit code | Clear the failure count for that key |
| Still running, interrupted, unknown result, or Hook error | Do not count it |
| Two confirmed failures already recorded | Deny the next identical call in `PreToolUse` |

By default, the state database is stored at `vibecoding-retry-guard/state.sqlite3` under the system temporary directory. It may be removed by temporary-file cleanup; do not treat it as an audit log or a security boundary.

After fixing the issue or receiving an explicit retry request, use the [targeted reset steps in the Hook guide](./skills/vibecoding/references/hooks.md#定向-reset) to clear a single record. The guide also covers manual integration, removal, database cleanup, and live-host acceptance checks.

## Support status

| Capability | Status |
| --- | --- |
| Use as a standalone Skill | Supported |
| Claude Code plugin discovery and Hook configuration | Supported; failure counting is limited by host event fields |
| Codex plugin discovery and Hook configuration | Supported; the current exit-code protocol prevents complete Guard enforcement |
| Windows script-level tests | Verified |
| macOS / Linux and live-host Hook sessions | Not yet verified |

Hooks are workflow guardrails, not a security sandbox: they cannot undo parallel calls that have already been allowed and do not cover tools that bypass the local Hook path.

## Credits

This project references or benefits from the following projects and documentation:

- [vuejs-ai/skills](https://github.com/vuejs-ai/skills) and [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills): the Skill ecosystem and organization patterns.
- [Anthropic Claude Code](https://github.com/anthropics/claude-code) and Claude Code Plugin / Hook documentation: plugin and event protocols.
- [OpenAI Codex](https://github.com/openai/codex) and Codex Hook documentation: plugin and Hook integration.
- [npxskills](https://github.com/dz3ai/npxskills): cross-agent Skill installation tooling.
- [Ponytail](https://github.com/DietrichGebert/ponytail): the engineering preference for smaller yet complete changes.
- [Stop That Shit](https://github.com/lennney/stop-that-shit): a reference layout for multi-host Skill + Hook plugins.
- [talk-normally](https://github.com/hexiecs/talk-normal): a direct, clear communication style.

All projects above remain the property of their respective authors and maintainers. This project does not imply affiliation with or official endorsement by them.

## License

This project is licensed under the [MIT License](./LICENSE).
