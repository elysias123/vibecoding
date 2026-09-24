# Java 后端参考

用于采用 Spring Boot、Quarkus 或 Micronaut 的 Java 后端工作。

## 外部技能

没有可用的精选外部技能。使用内置回退规则。

## 内置回退规则

- **框架**：生态成熟度使用 Spring Boot；云原生快速启动使用 Quarkus；编译期 DI 与低内存使用 Micronaut。
- **结构**：按领域组织 `controller/`、`service/`、`repository/`、`dto/` 和 `entity/`；大型项目使用多模块 Maven 或 Gradle。
- **依赖注入**：优先使用构造函数注入；避免使用 `@Autowired` 进行字段注入。
- **数据库**：使用 Spring Data JPA 搭配 Hibernate 或 jOOQ；使用 Flyway 或 Liquibase 进行迁移。
- **验证**：对控制器 DTO 应用 Bean Validation，例如 `@Valid` 和 `@NotNull`。
- **错误**：使用 `@ControllerAdvice` 和 `@ExceptionHandler` 返回结构化的全局错误响应。
- **身份验证**：使用 Spring Security、BCryptPasswordEncoder，以及适用时的 OAuth2/JWT 资源服务器支持。
- **异步**：简单后台工作使用 `@Async`；响应式或高并发工作使用 WebFlux 或 Java 21 虚拟线程。
- **测试**：单元测试使用 JUnit 5 和 Mockito；集成测试使用 `@SpringBootTest` 和 MockMvc；数据库集成使用 Testcontainers。
- **构建**：使用 Maven 或 Gradle 搭配 Spring Boot 插件，并采用多阶段 Docker 构建。
- **日志**：使用 SLF4J 和 Logback，结合 MDC 记录请求与用户上下文。
