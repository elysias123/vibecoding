# 前端任务路由器

仅在主技能激活后使用此路由器。加载匹配的最小前端参考集合。

## 加载策略

- 匹配任务后，仅加载列出的子文件；切勿预加载无关参考。
- 对应技能优先从当前项目和本地已安装技能目录中查找并加载；本地未找到时，再读取外部来源。
- 获取外部技能仅限临时读取其内容，不安装技能、不写入本地技能目录，也不改变环境。
- 没有实现工作时，不要将此路由器用于通用设计讨论或前端问答。
- 外部技能不可用时，使用匹配文件中的回退规则，并在结果中说明。

前端设计参考 `references/frontend/fundamentals.md`，React 与 React Native 技能参考 `references/frontend/react.md`，Vue 技能参考 `references/frontend/vue.md`。

## 其他参考资料路由

| 匹配条件 | 加载内容 | 说明 |
| --- | --- | --- |
| React 或 Next.js 项目 | `references/frontend/react.md` | |
| Vue 项目 | `references/frontend/vue.md` | |
| React Native 或 Expo 应用 | `references/frontend/react.md` 中的“React Native”部分 | |
| 多个前端关注点 | 按列出顺序加载所有匹配文件 | 跳过重复内容。 |
