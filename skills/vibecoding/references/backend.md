# 后端任务路由器

仅在主技能激活后使用此路由器。加载匹配的最小后端参考集合。

## 加载策略

- 匹配任务后，仅加载列出的子文件；绝不预加载无关参考。
- 外部技能不可用时，使用匹配文件中的回退规则，并在结果中说明。
- 对于 API 设计、数据库设计、身份验证或授权，将 `fundamentals.md` 与技术栈专用参考一起加载。

## 路由

| 匹配条件 | 加载文件 | 说明 |
| --- | --- | --- |
| Node.js、Express、Fastify、NestJS 或 Hono | `references/backend/nodejs.md` | |
| Python、FastAPI、Flask 或 Django | `references/backend/python.md` | |
| Go、Gin、Echo 或 Fiber | `references/backend/go.md` | |
| Java、Spring Boot、Quarkus 或 Micronaut | `references/backend/java.md` | |
| Rust、Actix-web、Axum 或 Rocket | `references/backend/rust.md` | |
| REST 或 GraphQL API 设计 | `references/backend/fundamentals.md` | |
| 数据库设计或 ORM | `references/backend/fundamentals.md` 与对应技术栈文件 | |
| 身份验证或授权 | `references/backend/fundamentals.md` 与对应技术栈文件 | |
| 不受支持的后端技术栈 | `references/backend/fundamentals.md` | 应用通用原则。 |

## 技术栈方向

- **简单快速**：使用最简单的框架选项，并跳过高级模式。
- **可维护**：使用结构化框架、ORM 和验证层。
- **高性能**：使用面向性能的框架、优化的数据库访问和缓存。
