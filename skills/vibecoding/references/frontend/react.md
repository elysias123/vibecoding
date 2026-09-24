# React 与 React Native 技能参考

用于 React、Next.js 或 React Native 工作。匹配第一个适用路由；仅当任务明确跨越多个关注点时才加载额外技能。

## 技能选择器

| 匹配条件 | 技能 | 优先级 | 范围 |
| --- | --- | --- | --- |
| 新的 React 或 Next.js 项目 | `react-best-practices` | CRITICAL | |
| React 性能优化 | `react-best-practices` | CRITICAL | 仅 CRITICAL 和 HIGH 规则 |
| 组件 API 设计或重构 | `composition-patterns` | HIGH | |
| 页面或路由过渡动画 | `react-view-transitions` | MEDIUM | |
| React Native 或 Expo 应用 | `react-native-skills` | CRITICAL | |

## 外部技能

| 外部技能 | 来源/链接 | 摘要 |
| --- | --- | --- |
| `react-best-practices` | Vercel engineering；<https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md> | 优先级：消除异步瀑布并优化包体积（CRITICAL）；服务器性能（HIGH）；客户端获取、重复渲染、渲染、JavaScript 性能和高级模式。 |
| `composition-patterns` | <https://github.com/vercel-labs/agent-skills/blob/main/skills/composition-patterns/SKILL.md> | 构建可扩展的组件 API：避免布尔属性泛滥，使用复合组件和清晰的变体，通过 provider 解耦状态，并恰当应用 React 19 API。 |
| `react-view-transitions` | <https://github.com/vercel-labs/agent-skills/blob/main/skills/react-view-transitions/SKILL.md> | 使用 View Transition API 实现进入、退出、更新、方向导航和共享元素动画。通过受支持的 React 调度 API 触发过渡。 |
| `react-native-skills` | <https://github.com/vercel-labs/agent-skills/blob/main/skills/react-native-skills/SKILL.md> | 优先考虑列表性能、GPU 友好动画、原生导航、UI 模式、状态、渲染、monorepo 和配置。 |

## 内置回退规则

- 使用单一职责组件，并在职责出现分歧时以约 200 行为界拆分。
- 对昂贵工作或回调稳定性使用 useMemo 和 useCallback；不要过度记忆化。
- 使用 SWR 或 TanStack Query 获取数据，而不是直接组合 useEffect 与 fetch。
- 仅在需要时，将状态从组件本地逐步扩展到 Context、Zustand 或 Jotai，再到 Redux。
- 在 Next.js 中优先使用 Server Components，仅为交互添加 use client。
- 使用 Promise.all 并行执行独立异步工作，避免瀑布。
