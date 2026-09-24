# Vue 技能参考

用于 Vue 2 或 3、Nuxt 及 Vue 生态相关工作。匹配第一个适用路由；仅当任务明确跨越多个关注点时才加载额外技能。

## 技能选择器

| 匹配条件 | 技能 | 优先级 | 范围 |
| --- | --- | --- | --- |
| 新的 Vue 3 项目或通用最佳实践 | `vue-best-practices` | CRITICAL | |
| 性能优化 | `vue-best-practices` | CRITICAL | 性能部分 |
| 使用 data() 或 methods 的 Options API 项目 | `vue-options-api-best-practices` | HIGH | |
| Vue Router 4 路由 | `vue-router-best-practices` | MEDIUM | |
| Pinia 状态管理 | `vue-pinia-best-practices` | MEDIUM | |
| 组件或 E2E 测试 | `vue-testing-best-practices` | MEDIUM | |
| Vue JSX | `vue-jsx-best-practices` | LOW | |
| Vue 3 运行时调试 | `vue-debug-guides` | HIGH | |
| 可复用 composable | `create-adaptable-composable` | MEDIUM | |

## 外部技能

| 外部技能 | 链接 | 摘要 |
| --- | --- | --- |
| `vue-best-practices` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-best-practices/SKILL.md> | 默认使用 Vue 3、Composition API 以及带 TypeScript 的 script setup。确认架构，应用基础规则，按需添加可选功能，优化性能，然后进行自检。 |
| `vue-options-api-best-practices` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-options-api-best-practices/SKILL.md> | 用于明确采用 Options API 的项目；涵盖 this 绑定、生命周期时机和 TypeScript。 |
| `vue-router-best-practices` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-router-best-practices/SKILL.md> | 涵盖守卫、响应式参数与查询、路由生命周期和嵌套路由。 |
| `vue-pinia-best-practices` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-pinia-best-practices/SKILL.md> | 涵盖 Setup 与 Options store、响应式陷阱、跨 store 交互和 SSR 隔离。 |
| `vue-testing-best-practices` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-testing-best-practices/SKILL.md> | 使用 Vitest、Vue Test Utils、Playwright E2E，以及异步组件或 Suspense 测试。 |
| `vue-jsx-best-practices` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-jsx-best-practices/SKILL.md> | 涵盖 Vue 与 React JSX 的差异：v-model、插槽、事件修饰符和模板编译。 |
| `vue-debug-guides` | <https://github.com/vuejs-ai/skills/blob/main/skills/vue-debug-guides/SKILL.md> | 诊断响应式、计算值、监听器、组件、props、模板、表单、事件、生命周期、插槽、provide/inject、SSR 和性能问题。 |
| `create-adaptable-composable` | <https://github.com/vuejs-ai/skills/blob/main/skills/create-adaptable-composable/SKILL.md> | 只读输入使用 MaybeRefOrGetter，可写输入使用 MaybeRef；监听器源使用 toRef，普通值使用 toValue。要求 Vue 3+ 或 Nuxt 3+，函数值输入不要使用 MaybeRefOrGetter。 |

## 内置回退规则

- 默认使用 Composition API 和带 TypeScript 的 script setup。
- 将响应式源状态精简地保存在 ref 或 reactive 中，并通过 computed 派生状态。
- 保持 props 向下、事件向上的数据流。
- 出现三个或更多独立 UI 区域、重复模板，或编排与展示混杂时拆分组件。
- 使用 useXxx composable 复用逻辑和副作用。
- 按 script、template、style 的顺序组织 SFC 区块。
