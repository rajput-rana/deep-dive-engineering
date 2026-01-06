# 🚀 Spring Boot - Expert Guide

<div align="center">

**Master Spring Boot: auto-configuration, microservices, and rapid development**

[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-Auto%20Config-blue?style=for-the-badge)](./)
[![Microservices](https://img.shields.io/badge/Microservices-Architecture-green?style=for-the-badge)](./)
[![REST](https://img.shields.io/badge/REST-APIs-orange?style=for-the-badge)](./)

*Comprehensive Spring Boot guide with Q&A for expert-level understanding*

</div>

---

## 🎯 Spring Boot Fundamentals

<div align="center">

### What is Spring Boot?

**Spring Boot is an opinionated framework built on Spring that simplifies application development.**

### Key Features

| Feature | Description |
|:---:|:---:|
| **⚙️ Auto-Configuration** | Automatic configuration based on classpath |
| **📦 Starter Dependencies** | Pre-configured dependencies |
| **🔧 Embedded Server** | Tomcat, Jetty, Undertow |
| **📊 Actuator** | Production-ready features |
| **🧪 Testing** | Built-in testing support |
| **📝 No XML** | Java-based configuration |

**Mental Model:** Think of Spring Boot like a smart assistant - it automatically configures everything based on what you have, so you can focus on writing business logic instead of configuration.

</div>

---

## ⚙️ Auto-Configuration

<div align="center">

### How Auto-Configuration Works

**Q: How does Spring Boot auto-configuration work?**

**A:** Spring Boot automatically configures beans based on:
1. **Classpath:** What dependencies are present
2. **Properties:** Application properties
3. **Conditions:** `@ConditionalOnClass`, `@ConditionalOnProperty`

**Example:**
```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(name = "spring.datasource.url")
public class DataSourceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource() {
        // Auto-configure DataSource if HikariCP is on classpath
        return DataSourceBuilder.create().build();
    }
}
```

**Q: How to exclude auto-configuration?**

**A:**
```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class Application {
    // ...
}
```

Or in `application.properties`:
```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

</div>

---

## 📦 Starter Dependencies

<div align="center">

### Common Starters

**Q: What are Spring Boot starters?**

**A:** Starters are dependency descriptors that include transitive dependencies.

| Starter | Description | Includes |
|:---:|:---:|:---:|
| **spring-boot-starter-web** | Web applications | Spring MVC, Tomcat, Jackson |
| **spring-boot-starter-data-jpa** | JPA support | Hibernate, Spring Data JPA |
| **spring-boot-starter-security** | Security | Spring Security |
| **spring-boot-starter-test** | Testing | JUnit, Mockito, AssertJ |
| **spring-boot-starter-actuator** | Monitoring | Health checks, metrics |

**Example:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

This single dependency includes:
- Spring Web MVC
- Embedded Tomcat
- Jackson (JSON)
- Validation
- And more...

</div>

---

## 🔧 Application Properties

<div align="center">

### Configuration Management

**Q: How to configure Spring Boot applications?**

**A:** Multiple ways:

1. **application.properties**
```properties
server.port=8080
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=password
```

2. **application.yml**
```yaml
server:
  port: 8080
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: password
```

3. **Environment Variables**
```bash
export SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/mydb
```

4. **@ConfigurationProperties**
```java
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    private int timeout;
    // Getters and setters
}
```

**Q: What is the order of property precedence?**

**A:** (Highest to lowest)
1. Command line arguments
2. Properties from `SPRING_APPLICATION_JSON`
3. `@TestPropertySource`
4. `@SpringBootTest` properties
5. Config data (application.properties)
6. Default properties

</div>

---

## 🌐 REST APIs

<div align="center">

### Building REST APIs

**Q: How to create REST APIs in Spring Boot?**

**A:**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        return ResponseEntity.ok(userService.findAll());
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {
        User created = userService.save(user);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(created);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody User user) {
        return ResponseEntity.ok(userService.update(id, user));
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

### Exception Handling

**Q: How to handle exceptions globally?**

**A:**

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex) {
        // Handle validation errors
        return ResponseEntity.badRequest().body(error);
    }
}
```

</div>

---

## 📊 Spring Boot Actuator

<div align="center">

### Monitoring & Health Checks

**Q: What is Spring Boot Actuator?**

**A:** Actuator provides production-ready features for monitoring and managing applications.

**Endpoints:**
- `/actuator/health` - Health check
- `/actuator/info` - Application info
- `/actuator/metrics` - Application metrics
- `/actuator/env` - Environment properties

**Configuration:**
```properties
management.endpoints.web.exposure.include=health,info,metrics
management.endpoint.health.show-details=always
```

**Custom Health Indicator:**
```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    @Override
    public Health health() {
        // Check custom condition
        if (isHealthy()) {
            return Health.up().build();
        }
        return Health.down()
            .withDetail("error", "Custom service unavailable")
            .build();
    }
}
```

</div>

---

## 🧪 Testing

<div align="center">

### Testing Strategies

**Q: How to test Spring Boot applications?**

**A:**

1. **Unit Tests** (No Spring context)
```java
class UserServiceTest {
    @Mock
    private UserRepository repository;
    
    @InjectMocks
    private UserService userService;
    
    @Test
    void testCreateUser() {
        // Test logic
    }
}
```

2. **Integration Tests** (With Spring context)
```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testGetUser() throws Exception {
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("John"));
    }
}
```

3. **Slice Tests** (Partial context)
```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    // Only web layer loaded
}
```

</div>

---

## 🏗️ Microservices

<div align="center">

### Building Microservices

**Q: How to build microservices with Spring Boot?**

**A:** Key components:

1. **Service Discovery** (Eureka, Consul)
2. **API Gateway** (Spring Cloud Gateway)
3. **Configuration Server** (Spring Cloud Config)
4. **Circuit Breaker** (Resilience4j)
5. **Distributed Tracing** (Sleuth, Zipkin)

**Example Microservice:**
```java
@SpringBootApplication
@EnableEurekaClient
@EnableCircuitBreaker
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Hard Interview Questions

**Q: What is the difference between Spring and Spring Boot?**

**A:**
- **Spring:** Framework, requires configuration
- **Spring Boot:** Opinionated framework, auto-configuration, embedded server

**Q: How does Spring Boot starter work internally?**

**A:** Starters use Maven's transitive dependencies. They don't contain code, just dependency declarations.

**Q: What is the difference between @SpringBootApplication and @EnableAutoConfiguration?**

**A:**
- **@SpringBootApplication:** Combines @Configuration, @EnableAutoConfiguration, @ComponentScan
- **@EnableAutoConfiguration:** Only enables auto-configuration

**Q: How to customize embedded server in Spring Boot?**

**A:**
```java
@Bean
public WebServerFactoryCustomizer<TomcatServletWebServerFactory> 
    tomcatCustomizer() {
    return factory -> {
        factory.setPort(9000);
        factory.setContextPath("/api");
    };
}
```

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Auto-Configuration** | Automatic setup based on classpath |
| **Starters** | Pre-configured dependencies |
| **Actuator** | Production monitoring |
| **REST APIs** | @RestController, exception handling |
| **Testing** | Unit, integration, slice tests |

**💡 Remember:** Spring Boot simplifies Spring development with auto-configuration and starters. Master these concepts for rapid application development.

</div>

---

<div align="center">

**Master Spring Boot for rapid development! 🚀**

*From auto-configuration to microservices - comprehensive Spring Boot guide with Q&A.*

</div>

