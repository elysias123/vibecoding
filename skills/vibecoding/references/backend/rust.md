# Rust 后端参考

用于采用 Actix-web、Axum 或 Rocket 的 Rust 后端工作。

## 外部技能

没有可用的精选外部技能。使用内置回退规则。

## 内置回退规则

- **框架**：Tokio 生态使用 Axum；成熟高吞吐服务使用 Actix-web；宏驱动且重视易用性时使用 Rocket。
- **结构**：使用 `src/main.rs`、`routes/`、`handlers/`、`models/` 和 `db/`；多个 crate 使用 Cargo workspace。
- **错误**：实现可转换为响应的 AppError；库错误使用 thiserror，应用错误使用 anyhow；生产路径绝不 `unwrap`。
- **数据库**：异步编译期检查查询使用 SQLx；同步强类型场景使用 Diesel；使用相应的迁移工具。
- **身份验证**：使用 jsonwebtoken 搭配中间件或提取器，并使用 argon2 进行密码哈希。
- **异步**：使用 Tokio；后台任务使用 `tokio::spawn`，并发使用 `tokio::select!`，CPU 密集型工作使用 `spawn_blocking`。
- **验证**：在处理器入口使用 validator 派生宏验证请求结构体。
- **序列化**：使用 serde 和 serde_json；为 API 类型派生 Serialize 和 Deserialize。
- **测试**：使用 `#[tokio::test]`；Axum 使用 `tower::ServiceExt`；Actix 使用 `actix_web::test`；数据库集成使用 testcontainers-rs。
- **构建**：使用带 LTO 的 `cargo build --release`，并采用多阶段 Docker 构建。
- **安全**：优先使用安全 Rust；每个 `unsafe` 块都必须添加说明其不变量的 SAFETY 注释。
