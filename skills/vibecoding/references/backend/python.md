# Python 后端参考

用于采用 FastAPI、Flask 或 Django 的 Python 后端工作。

## 外部技能

没有可用的精选外部技能。使用内置回退规则。

## 内置回退规则

- **框架**：异步与自动文档使用 FastAPI；追求简单时使用 Flask；需要完整能力时使用 Django。
- **结构**：按领域组织包，每个领域包含 `routers/`、`services/`、`models/` 和 `schemas/`。
- **类型**：使用类型提示和 Pydantic 请求/响应模型。
- **数据库**：使用 SQLAlchemy 2.0 或 Tortoise ORM，并使用 Alembic 迁移。
- **身份验证**：通过 FastAPI 安全工具使用 OAuth2 和 JWT；适用时使用 Django 内置身份验证；密码哈希使用 passlib。
- **异步**：FastAPI I/O 端点优先使用 `async def`；避免在异步上下文中执行阻塞调用。
- **错误**：使用自定义异常处理器和结构化错误响应。
- **测试**：FastAPI 使用 pytest 与 `httpx.AsyncClient`；Django 使用测试客户端。
- **依赖**：在 `pyproject.toml` 中使用 uv 或 poetry，并锁定生产依赖版本。
