# 前端设计参考

用于与框架无关或跨框架的 UI 实现。不要用于纯视觉构思、品牌探索或非编程设计讨论。

## 准则

- 基于现有项目改动时，优先复用该页面相同组件样式。

## 设计方向与策略

- 采用生产级界面设计：根据目标推导基调与约束，选择有辨识度的字体，定义基于 CSS 变量的色彩系统，优先采用 CSS 动效，并有意识地组织空间构图。
- **从零开始，创造独特视觉方向**：优先使用 `apple-design`，强制进行设计计划与反模板审查，建立独特的美学方向和设计 token 系统。
- **已有明确设计方向，但动效和交互细节粗糙**：使用 `animate` 和 `apple-design`，为系统注入专业级别的动效和交互细节。
- **需要审计现有动画代码**：使用 `improve-animations` 产出改进计划。
- **不确定动效术语或想发现动效机会**：使用 `animation-vocabulary` 和 `find-animation-opportunities`。
- **移动端体验优化**：使用 `mobile-native` 解决手感问题。
- **组合使用**：初期用 `apple-design` 确立美学方向，实现阶段引入 `animate`、`mobile-native` 等打磨细节。

## 外部技能

- `apple-design`：<https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md>
  - 从 Apple WWDC 设计演讲中提炼设计和动效原则，翻译成 Web 开发可用的规则，让 AI 对齐 Apple 级别的设计标准。
- `animation-vocabulary`：<https://github.com/emilkowalski/skills/blob/main/skills/animation-vocabulary/SKILL.md>
  - 反向查询的术语词典，当你只能模糊描述动效时，帮你找到准确专业术语，以便下达精确指令。
- `improve-animations`：<https://github.com/emilkowalski/skills/blob/main/skills/improve-animations/SKILL.md>
  - 扫描代码库中的动画代码，产出按优先级排序的改进计划，供其他 Agent 执行修复。
- `find-animation-opportunities`：<https://github.com/emilkowalski/skills/blob/main/skills/find-animation-opportunities/SKILL.md>
  - 发现“该动却没动”的地方，同时指出不应添加动画的高频操作点，只读，提出动效建议和参数。
- `animate`：<https://github.com/emilkowalski/skills/blob/main/skills/animate/SKILL.md>
  - 从零开始构建动画，严格按照决策顺序：该不该动 → 目的 → 工具 → 属性 → 曲线 → 时长，写出能通过严格质量评审的动画代码。
- `mobile-native`：<https://github.com/emilkowalski/skills/blob/main/skills/mobile-native/SKILL.md>
  - 解决 Web 应用在手机上“手感像网页而不像 App”的问题，处理移动端特有细节：粘滞 hover、点击高亮闪烁、100vh 视口 bug、输入框自动缩放、点击延迟、安全区域适配等。
  - **使用时机**：项目实现和精修阶段，需要打磨交互细节、提升“手感”时。尤其适合需要达到 Apple、Linear 级别动效品质的场景。

## 内置回退规则

- 建立清晰的层级，每个视图只设一个主要操作，并弱化次要元素。
- 通过 CSS 自定义属性使用一种主色、一种强调色和中性色。
- 最多使用两种字体系列，并保持正文 4.5:1、大号文本 3:1 的对比度。
- 使用一致的间距刻度，例如以 4px 为基准或采用 Tailwind 默认值。
- 使用细微的 150 至 300ms 交互过渡，并遵循 `prefers-reduced-motion`。
- 避免使用没有用户体验目的的装饰元素。