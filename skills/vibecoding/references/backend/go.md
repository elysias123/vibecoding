# Go 后端参考

用于采用 net/http、Gin、Echo 或 Fiber 的 Go 后端工作。

## 外部技能

没有可用的精选外部技能。使用内置回退规则。

## 内置回退规则

- **框架**：零依赖场景使用 `net/http`；需要中间件生态时使用 Gin 或 Echo；需要类 Express API 时使用 Fiber。
- **结构**：使用 `cmd/` 存放入口，`internal/` 存放私有包，`pkg/` 存放公共库。
- **错误**：将 `error` 作为最后一个返回值，使用 `fmt.Errorf("context: %w", err)` 包装错误，库代码绝不 `panic`。
- **数据库**：PostgreSQL 使用 `database/sql` 与 pgx；追求便利时使用 GORM；需要类型安全 SQL 时使用 sqlc。
- **身份验证**：使用 `golang-jwt/jwt` 和身份验证中间件；将机密保存在环境变量中。
- **并发**：使用 goroutine 和 channel；传递 `context.Context` 处理取消与超时。
- **验证**：使用 `go-playground/validator` 标签或自定义验证中间件。
- **测试**：使用 `testing`；可选用 testify 进行断言，并用 `httptest` 测试处理器。
- **构建**：使用带 `ldflags` 的 `go build` 注入版本，并采用多阶段 Docker 构建。
