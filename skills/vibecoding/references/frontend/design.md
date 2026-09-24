# 前端设计参考

用于与框架无关或跨框架的 UI 实现。不要用于纯视觉构思、品牌探索或非编程设计讨论。

## 外部技能

- `frontend-design`：<https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md>
  - 采用生产级界面设计：根据目标推导基调与约束，选择有辨识度的字体，定义基于 CSS 变量的色彩系统，优先采用 CSS 动效，并有意识地组织空间构图。

## 内置回退规则

- 建立清晰的层级，每个视图只设一个主要操作，并弱化次要元素。
- 通过 CSS 自定义属性使用一种主色、一种强调色和中性色。
- 最多使用两种字体系列，并保持正文 4.5:1、大号文本 3:1 的对比度。
- 使用一致的间距刻度，例如以 4px 为基准或采用 Tailwind 默认值。
- 使用细微的 150 至 300ms 交互过渡，并遵循 `prefers-reduced-motion`。
- 避免使用没有用户体验目的的装饰元素。
