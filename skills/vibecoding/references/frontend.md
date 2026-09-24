# 前端任务路由器

仅在主技能激活后使用此路由器。加载匹配的最小前端参考集合。

## 加载策略

- 匹配任务后，仅加载列出的子文件；切勿预加载无关参考。
- 没有实现工作时，不要将此路由器用于通用设计讨论或前端问答。
- 外部技能不可用时，使用匹配文件中的回退规则，并在结果中说明。

## 路由

| 匹配条件 | 加载内容 | 说明 |
| --- | --- | --- |
| React 或 Next.js 项目 | `references/frontend/react.md` | |
| Vue 项目 | `references/frontend/vue.md` | |
| React Native 或 Expo 应用 | `references/frontend/react.md` 中的“React Native”部分 | |
| 与框架无关的 UI 或视觉实现 | `references/frontend/design.md` | |
| CSS、无障碍、性能、TypeScript 或工具链 | `references/frontend/fundamentals.md` | |
| Svelte、Angular、Solid 或其他不受支持的框架 | `references/frontend/fundamentals.md` | 应用通用原则。 |
| 多个前端关注点 | 按列出顺序加载所有匹配文件 | 跳过重复内容。 |

## 技术栈方向

- **简单快速**：仅加载匹配参考中的核心技能，并跳过可选技能。
- **可维护**：加载核心技能以及相关的架构或模式技能。
- **高性能**：加载核心技能及其 CRITICAL 或 HIGH 性能规则。
