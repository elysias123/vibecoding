# Node.js 后端参考

用于采用 Express、Fastify、Hono 或 NestJS 的 Node.js 后端工作。

## 外部技能

没有可用的精选外部技能。使用内置回退规则。

## 内置回退规则

- **框架**：需要广泛生态时使用 Express；重视性能时使用 Fastify；轻量边缘工作使用 Hono；企业级结构使用 NestJS。
- **结构**：优先使用 `/modules/users/` 这样的功能模块，而不是全局 controller/service 分层。
- **错误**：使用集中式错误处理中间件，并防止未处理的 Promise 拒绝。
- **数据库**：使用 Prisma 获得类型安全的迁移，或使用 Drizzle 获得贴近 SQL 的访问方式；避免在业务逻辑中使用原始查询。
- **身份验证**：无状态 API 使用 JWT，SSR 使用会话；使用 bcrypt 或 argon2 对密码哈希；绝不在代码中存储机密。
- **验证**：尽早使用 Zod 验证请求体、路径参数和查询参数。
- **日志**：使用 pino 或 winston 等工具输出结构化 JSON 日志，并包含请求 ID。
- **测试**：单元测试使用 Vitest 或 Jest，HTTP 集成测试使用 Supertest。
- **TypeScript**：启用严格模式，并定义请求和响应的数据结构。
