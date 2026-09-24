# 前端基础参考

用于 CSS、无障碍、性能、TypeScript 和工具链相关工作。

- 使用 CSS 自定义属性定义主题和设计令牌。
- 使用 Tailwind 时，避免使用 `bg-${color}-500` 这样的动态类名拼接；使用完整类名以便提取。
- 全局设置 `box-sizing: border-box`，采用移动优先的 `min-width` 媒体查询，并将选择器嵌套限制在三层以内。
- 优先使用 `nav`、`main`、`article`、`button` 等语义化 HTML，而不是只用 `div` 组成结构。
- 让每个交互元素都支持键盘操作，并提供适当的焦点管理。
- 为图片提供有意义的 `alt` 文本；装饰性图片使用空 `alt`。
- 满足 WCAG AA 对比度要求：正文 4.5:1，大号文本 3:1。
- 提供 `prefers-reduced-motion` 回退方案。
- 将 LCP 控制在 2.5 秒以内、INP 控制在 200 毫秒以内、CLS 控制在 0.1 以内。
- 使用带明确尺寸的 WebP 或 AVIF 图片。
- 内联关键 CSS，并延迟加载非关键资源。
- 第三方脚本使用 `async` 或 `defer`，并在 hydration 后加载分析脚本。
- 默认按路由进行代码拆分。
- 为组件 props 和事件定义明确类型；使用收窄后的 `unknown`，避免使用 `any`。
- 使用 Zod 或等效工具在运行时验证 API 响应。
- 导出公共类型，并将内部类型保持为私有。
- 通用 React、Vue 或 Svelte 工具链使用 Vite；Next.js 使用其内置工具。
- 使用 ESM 导入，并避免 barrel 文件副作用，以保留 tree shaking 能力。
