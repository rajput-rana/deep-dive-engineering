# 🚀 Spring Boot - Expert Guide

<div align="center">

**Master Spring Boot: auto-configuration, microservices, and rapid development**

[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-Auto%20Config-blue?style=for-the-badge)](./)
[![Microservices](https://img.shields.io/badge/Microservices-Architecture-green?style=for-the-badge)](./)
[![REST](https://img.shields.io/badge/REST-APIs-orange?style=for-the-badge)](./)

*Comprehensive Spring Boot guide with exhaustive Q&A for expert-level understanding*

</div>

---

## 🎯 Spring Boot Fundamentals

<div align="center">

### What is Spring Boot?

**Spring Boot is an opinionated framework built on Spring that simplifies application development by providing auto-configuration, embedded servers, and starter dependencies.**

### Key Features

| Feature | Description |
|:---:|:---:|
| **⚙️ Auto-Configuration** | Automatic configuration based on classpath |
| **📦 Starter Dependencies** | Pre-configured dependencies |
| **🔧 Embedded Server** | Tomcat, Jetty, Undertow |
| **📊 Actuator** | Production-ready features |
| **🧪 Testing** | Built-in testing support |
| **📝 No XML** | Java-based configuration |
| **🚀 Standalone** | Run as JAR/WAR |

**Mental Model:** Think of Spring Boot like a smart assistant - it automatically configures everything based on what you have, so you can focus on writing business logic instead of configuration.

</div>

---

## 📚 Interview Questions for Freshers

<div align="center">

### Q1: What is Spring Boot and why is it used?

**A:** Spring Boot is a framework that simplifies Spring application development.

**Why Use Spring Boot:**
1. **Less Configuration:** Auto-configuration reduces boilerplate
2. **Faster Development:** Starters provide ready-to-use dependencies
3. **Embedded Server:** No need for external server setup
4. **Production Ready:** Actuator for monitoring and management
5. **Opinionated Defaults:** Best practices built-in

**Key Benefits:**
- ✅ Rapid application development
- ✅ Minimal configuration
- ✅ Standalone applications
- ✅ Production-ready features

---

### Q2: What is the difference between Spring and Spring Boot?

**A:**

| Aspect | Spring Framework | Spring Boot |
|:---:|:---:|:---:|
| **Configuration** | Manual XML/Java config | Auto-configuration |
| **Dependencies** | Manual dependency management | Starter dependencies |
| **Server** | External server needed | Embedded server |
| **Deployment** | WAR file to server | Standalone JAR |
| **Setup Time** | More time | Less time |
| **Boilerplate** | More boilerplate code | Less boilerplate |

**Spring Boot = Spring Framework + Auto-configuration + Embedded Server**

---

### Q3: What are the key features of Spring Boot?

**A:**

**Core Features:**

1. **Auto-Configuration**
   - Automatically configures beans based on classpath
   - Reduces manual configuration

2. **Starter Dependencies**
   - Pre-configured dependency sets
   - Simplifies dependency management

3. **Embedded Servers**
   - Tomcat, Jetty, Undertow included
   - No external server needed

4. **Production-Ready Features**
   - Actuator for monitoring
   - Health checks, metrics

5. **No XML Configuration**
   - Java-based configuration
   - Annotation-driven

6. **Standalone Applications**
   - Run as JAR files
   - No deployment descriptor needed

---

### Q4: What is the purpose of @SpringBootApplication annotation?

**A:** `@SpringBootApplication` is a convenience annotation that combines three annotations:

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**Equivalent to:**
```java
@Configuration          // Marks as configuration class
@EnableAutoConfiguration // Enables auto-configuration
@ComponentScan         // Scans for components
public class Application {
    // ...
}
```

**What It Does:**
- Enables component scanning
- Enables auto-configuration
- Marks class as configuration source

---

### Q5: How does Spring Boot handle dependency management?

**A:** Spring Boot uses starter dependencies and parent POM.

**1. Starter Dependencies:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

**2. Parent POM:**
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.0</version>
</parent>
```

**Benefits:**
- Version management
- Dependency compatibility
- Default configurations

---

### Q6: What are Spring Boot starters?

**A:** Starters are dependency descriptors that include transitive dependencies.

**Common Starters:**

| Starter | Purpose | Includes |
|:---:|:---:|:---:|
| **spring-boot-starter-web** | Web applications | Spring MVC, Tomcat, Jackson |
| **spring-boot-starter-data-jpa** | JPA support | Hibernate, Spring Data JPA |
| **spring-boot-starter-security** | Security | Spring Security |
| **spring-boot-starter-test** | Testing | JUnit, Mockito, AssertJ |
| **spring-boot-starter-actuator** | Monitoring | Health checks, metrics |
| **spring-boot-starter-validation** | Validation | Bean Validation API |

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
- Jackson (JSON processing)
- Validation
- And more...

---

### Q7: What is Spring Boot Actuator?

**A:** Actuator provides production-ready features for monitoring and managing applications.

**Key Endpoints:**

| Endpoint | Purpose |
|:---:|:---:|
| `/actuator/health` | Application health |
| `/actuator/info` | Application information |
| `/actuator/metrics` | Application metrics |
| `/actuator/env` | Environment properties |
| `/actuator/loggers` | Logger configuration |

**Configuration:**
```properties
management.endpoints.web.exposure.include=health,info,metrics
management.endpoint.health.show-details=always
```

---

### Q8: How to create a Spring Boot application?

**A:** Multiple ways:

**1. Spring Initializr (Web):**
- Visit https://start.spring.io
- Select dependencies
- Generate project

**2. Spring Boot CLI:**
```bash
spring init --dependencies=web,data-jpa myapp
```

**3. IDE (IntelliJ/Eclipse):**
- New Project → Spring Initializr
- Select dependencies
- Generate

**4. Manual Setup:**
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.0</version>
</parent>
```

---

### Q9: What are embedded containers in Spring Boot?

**A:** Embedded containers are servers packaged within the application.

**Supported Containers:**

| Container | Description | Default |
|:---:|:---:|:---:|
| **Tomcat** | Apache Tomcat | ✅ Yes |
| **Jetty** | Eclipse Jetty | No |
| **Undertow** | Undertow | No |

**Why Use:**
- ✅ Standalone applications
- ✅ No external server setup
- ✅ Easy deployment
- ✅ Consistent environment

**Switch Container:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

---

### Q10: How does Spring Boot support externalized configuration?

**A:** Multiple ways to configure:

**1. application.properties:**
```properties
server.port=8080
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
```

**2. application.yml:**
```yaml
server:
  port: 8080
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
```

**3. Environment Variables:**
```bash
export SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/mydb
```

**4. Command Line Arguments:**
```bash
java -jar app.jar --server.port=9000
```

**5. @ConfigurationProperties:**
```java
@ConfigurationProperties(prefix = "app")
public class AppProperties {
    private String name;
    private int timeout;
}
```

---

### Q11: What is the role of application.properties file?

**A:** `application.properties` defines configuration settings.

**Common Configurations:**

```properties
# Server Configuration
server.port=8080
server.servlet.context-path=/api

# Database Configuration
spring.datasource.url=jdbc:mysql://localhost:3306/mydb
spring.datasource.username=root
spring.datasource.password=password
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA Configuration
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

# Logging
logging.level.root=INFO
logging.level.com.example=DEBUG
```

**Profile-Specific:**
- `application-dev.properties`
- `application-prod.properties`
- `application-test.properties`

---

### Q12: How to implement exception handling in Spring Boot?

**A:** Use `@ControllerAdvice` and `@ExceptionHandler`.

**Global Exception Handler:**
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(
            ResourceNotFoundException ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.NOT_FOUND.value(),
            ex.getMessage(),
            System.currentTimeMillis()
        );
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error -> 
            errors.put(error.getField(), error.getDefaultMessage())
        );
        ErrorResponse error = new ErrorResponse(
            HttpStatus.BAD_REQUEST.value(),
            "Validation failed",
            errors
        );
        return ResponseEntity.badRequest().body(error);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex) {
        ErrorResponse error = new ErrorResponse(
            HttpStatus.INTERNAL_SERVER_ERROR.value(),
            ex.getMessage()
        );
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }
}
```

---

### Q13: What is Spring Boot DevTools?

**A:** DevTools provides development-time features.

**Features:**

1. **Automatic Restart:**
   - Restarts application when classpath changes
   - Faster than full restart

2. **Live Reload:**
   - Browser refresh on changes
   - Requires LiveReload browser extension

3. **Property Defaults:**
   - Disables template caching
   - Enables debug logging

4. **Remote Debugging:**
   - Remote application support

**Configuration:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
```

**Note:** Excluded in production builds automatically.

---

### Q14: How does Spring Boot support microservices architecture?

**A:** Spring Boot + Spring Cloud enable microservices.

**Key Components:**

1. **Service Discovery (Eureka):**
```java
@SpringBootApplication
@EnableEurekaClient
public class UserServiceApplication {
    // Registers with Eureka
}
```

2. **API Gateway (Spring Cloud Gateway):**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
```

3. **Configuration Server:**
```java
@SpringBootApplication
@EnableConfigServer
public class ConfigServerApplication {
    // Centralized configuration
}
```

4. **Circuit Breaker (Resilience4j):**
```java
@CircuitBreaker(name = "userService")
public User getUser(Long id) {
    // Circuit breaker pattern
}
```

---

### Q15: What is the significance of spring-boot-starter-parent?

**A:** Parent POM provides:

**Benefits:**

1. **Dependency Management:**
   - Pre-defined versions
   - Compatibility guaranteed

2. **Default Configurations:**
   - Plugin configurations
   - Resource filtering

3. **Property Defaults:**
   - Java version
   - Encoding

**Example:**
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.1.0</version>
</parent>
```

**What It Provides:**
- Default Java version
- UTF-8 encoding
- Dependency versions
- Plugin configurations

</div>

---

## 📚 Intermediate Interview Questions

<div align="center">

### Q1: How does Spring Boot auto-configuration work?

**A:** Auto-configuration uses conditional annotations.

**Process:**

1. **Scan Classpath:** Check for specific classes
2. **Check Conditions:** `@ConditionalOnClass`, `@ConditionalOnProperty`
3. **Create Beans:** If conditions met, create beans
4. **Override:** Can be overridden with custom beans

**Example:**
```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(name = "spring.datasource.url")
@AutoConfigureAfter(DataSourceAutoConfiguration.class)
public class DataSourceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DataSourceProperties properties) {
        return DataSourceBuilder.create()
            .url(properties.getUrl())
            .username(properties.getUsername())
            .password(properties.getPassword())
            .build();
    }
}
```

**Key Annotations:**
- `@ConditionalOnClass` - Class must be on classpath
- `@ConditionalOnMissingBean` - Bean must not exist
- `@ConditionalOnProperty` - Property must be set

---

### Q2: How to exclude auto-configuration?

**A:** Multiple ways:

**1. @SpringBootApplication:**
```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class Application {
    // ...
}
```

**2. application.properties:**
```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

**3. Multiple Exclusions:**
```java
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class,
    HibernateJpaAutoConfiguration.class
})
```

**When to Exclude:**
- Using custom configuration
- Not using specific feature
- Performance optimization

---

### Q3: What is the order of property precedence in Spring Boot?

**A:** (Highest to lowest)

1. **Command Line Arguments:** `--server.port=9000`
2. **SPRING_APPLICATION_JSON:** Environment variable
3. **@TestPropertySource:** Test properties
4. **@SpringBootTest properties:** Test configuration
5. **Config Data (application.properties/yml):** Application config
6. **Default Properties:** Spring Boot defaults

**Example:**
```bash
# Command line (highest priority)
java -jar app.jar --server.port=9000

# Environment variable
export SPRING_DATASOURCE_URL=jdbc:mysql://localhost:3306/mydb

# application.properties (lower priority)
server.port=8080
```

---

### Q4: What are Spring Boot Profiles?

**A:** Profiles allow different configurations for different environments.

**Creating Profiles:**

**1. application-dev.properties:**
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/devdb
logging.level.root=DEBUG
```

**2. application-prod.properties:**
```properties
spring.datasource.url=jdbc:mysql://prod-server:3306/proddb
logging.level.root=INFO
```

**Activating Profiles:**

**1. application.properties:**
```properties
spring.profiles.active=dev
```

**2. Command Line:**
```bash
java -jar app.jar --spring.profiles.active=prod
```

**3. Environment Variable:**
```bash
export SPRING_PROFILES_ACTIVE=prod
```

**4. Programmatically:**
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(Application.class);
        app.setAdditionalProfiles("prod");
        app.run(args);
    }
}
```

---

### Q5: What is @RestController annotation?

**A:** `@RestController` combines `@Controller` and `@ResponseBody`.

**Difference:**

**@Controller:**
```java
@Controller
public class UserController {
    @RequestMapping("/users")
    public String getUsers(Model model) {
        // Returns view name
        return "users";
    }
}
```

**@RestController:**
```java
@RestController
public class UserController {
    @GetMapping("/users")
    public List<User> getUsers() {
        // Returns JSON directly
        return userService.findAll();
    }
}
```

**Equivalent:**
```java
@Controller
@ResponseBody  // Added
public class UserController {
    // Same as @RestController
}
```

---

### Q6: How does Spring Boot handle database initialization?

**A:** Multiple ways:

**1. SQL Scripts:**
```sql
-- schema.sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255)
);

-- data.sql
INSERT INTO users VALUES (1, 'John');
```

**2. JPA/Hibernate:**
```properties
spring.jpa.hibernate.ddl-auto=create-drop
# Options: none, validate, update, create, create-drop
```

**3. Flyway/Liquibase:**
```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

**Configuration:**
```properties
spring.sql.init.mode=always
spring.sql.init.schema-locations=classpath:schema.sql
spring.sql.init.data-locations=classpath:data.sql
```

---

### Q7: What is CommandLineRunner interface?

**A:** `CommandLineRunner` executes code after application starts.

**Usage:**
```java
@Component
public class DataInitializer implements CommandLineRunner {
    
    @Autowired
    private UserRepository userRepository;
    
    @Override
    public void run(String... args) throws Exception {
        // Execute after application starts
        if (userRepository.count() == 0) {
            userRepository.save(new User("John", "john@example.com"));
        }
    }
}
```

**Multiple Runners:**
```java
@Component
@Order(1)
public class FirstRunner implements CommandLineRunner {
    // Executes first
}

@Component
@Order(2)
public class SecondRunner implements CommandLineRunner {
    // Executes second
}
```

**Alternative:** `ApplicationRunner` (receives `ApplicationArguments`)

---

### Q8: How to monitor a Spring Boot application?

**A:** Multiple approaches:

**1. Spring Boot Actuator:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**2. Custom Health Indicators:**
```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            return Health.up()
                .withDetail("database", "Available")
                .build();
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
}
```

**3. Micrometer Integration:**
```java
@RestController
public class MetricsController {
    
    private final Counter requestCounter;
    
    public MetricsController(MeterRegistry registry) {
        this.requestCounter = Counter.builder("requests.total")
            .description("Total requests")
            .register(registry);
    }
    
    @GetMapping("/api/users")
    public List<User> getUsers() {
        requestCounter.increment();
        return userService.findAll();
    }
}
```

---

### Q9: What is the difference between @SpringBootApplication and @EnableAutoConfiguration?

**A:**

| Aspect | @SpringBootApplication | @EnableAutoConfiguration |
|:---:|:---:|:---:|
| **Combines** | @Configuration + @EnableAutoConfiguration + @ComponentScan | Only @EnableAutoConfiguration |
| **Component Scanning** | Yes | No |
| **Use Case** | Main application class | Custom configuration classes |

**@SpringBootApplication:**
```java
@SpringBootApplication
public class Application {
    // Equivalent to:
    // @Configuration
    // @EnableAutoConfiguration
    // @ComponentScan
}
```

**@EnableAutoConfiguration:**
```java
@Configuration
@EnableAutoConfiguration
public class CustomConfig {
    // Only enables auto-configuration
    // No component scanning
}
```

---

### Q10: How to customize embedded server in Spring Boot?

**A:** Multiple ways:

**1. application.properties:**
```properties
server.port=9000
server.servlet.context-path=/api
server.tomcat.max-threads=200
```

**2. WebServerFactoryCustomizer:**
```java
@Bean
public WebServerFactoryCustomizer<TomcatServletWebServerFactory> 
    tomcatCustomizer() {
    return factory -> {
        factory.setPort(9000);
        factory.setContextPath("/api");
        factory.addConnectorCustomizers(connector -> {
            connector.setProperty("maxThreads", "200");
        });
    };
}
```

**3. Programmatically:**
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(Application.class);
        app.setDefaultProperties(Collections.singletonMap(
            "server.port", "9000"
        ));
        app.run(args);
    }
}
```

---

### Q11: What is the difference between @Component, @Service, @Repository, and @Controller?

**A:**

| Annotation | Purpose | Use Case |
|:---:|:---:|:---:|
| **@Component** | Generic Spring component | Any Spring-managed bean |
| **@Service** | Business logic layer | Service classes |
| **@Repository** | Data access layer | DAO, repository classes |
| **@Controller** | Web controller (MVC) | Web controllers |
| **@RestController** | REST controller | REST APIs |

**Key Differences:**

**@Repository:**
- Exception translation (DataAccessException)
- Marks for persistence layer

**@Service:**
- Business logic layer
- No special behavior (semantic)

**@Controller:**
- Returns view names (MVC)
- Can return ModelAndView

**@RestController:**
- Returns data directly (JSON/XML)
- @Controller + @ResponseBody

---

### Q12: How does Spring Boot handle transactions?

**A:** Declarative transaction management.

**1. @Transactional Annotation:**
```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
        User from = userRepository.findById(fromId).orElseThrow();
        User to = userRepository.findById(toId).orElseThrow();
        from.debit(amount);
        to.credit(amount);
        userRepository.save(from);
        userRepository.save(to);
        // All or nothing - atomic transaction
    }
}
```

**2. Transaction Propagation:**
```java
@Transactional(propagation = Propagation.REQUIRED)  // Default
public void method1() {
    // Join existing or create new
}

@Transactional(propagation = Propagation.REQUIRES_NEW)
public void method2() {
    // Always create new transaction
}
```

**3. Transaction Isolation:**
```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void method() {
    // Custom isolation level
}
```

---

### Q13: What is Spring Boot Actuator and its endpoints?

**A:** Actuator provides production-ready monitoring.

**Key Endpoints:**

| Endpoint | Purpose | Sensitive |
|:---:|:---:|:---:|
| `/actuator/health` | Health check | No |
| `/actuator/info` | Application info | No |
| `/actuator/metrics` | Application metrics | No |
| `/actuator/env` | Environment properties | Yes |
| `/actuator/configprops` | Configuration properties | Yes |
| `/actuator/beans` | Spring beans | Yes |
| `/actuator/mappings` | Request mappings | Yes |
| `/actuator/loggers` | Logger configuration | Yes |

**Configuration:**
```properties
# Expose endpoints
management.endpoints.web.exposure.include=health,info,metrics

# Exclude sensitive endpoints
management.endpoints.web.exposure.exclude=env,configprops

# Enable all (not recommended for production)
management.endpoints.web.exposure.include=*

# Health check details
management.endpoint.health.show-details=always
```

---

### Q14: How to implement security in Spring Boot?

**A:** Use Spring Security.

**Basic Security:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

**Configuration:**
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .formLogin()
            .httpBasic();
        return http.build();
    }
    
    @Bean
    public UserDetailsService userDetailsService() {
        UserDetails user = User.withDefaultPasswordEncoder()
            .username("user")
            .password("password")
            .roles("USER")
            .build();
        return new InMemoryUserDetailsManager(user);
    }
}
```

**JWT Security:**
```java
@Configuration
@EnableWebSecurity
public class JwtSecurityConfig {
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            )
            .sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .addFilterBefore(jwtAuthenticationFilter(), 
                UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }
}
```

---

### Q15: What is the difference between @RequestParam and @PathVariable?

**A:**

| Aspect | @RequestParam | @PathVariable |
|:---:|:---:|:---:|
| **Usage** | Query parameters | URL path variables |
| **Example** | `/users?id=1` | `/users/1` |
| **Required** | Optional by default | Required by default |

**@RequestParam:**
```java
@GetMapping("/users")
public User getUser(@RequestParam Long id) {
    // URL: /users?id=1
    return userService.findById(id);
}

@GetMapping("/search")
public List<User> search(
        @RequestParam(required = false) String name,
        @RequestParam(defaultValue = "0") int page) {
    // URL: /search?name=John&page=1
    return userService.search(name, page);
}
```

**@PathVariable:**
```java
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    // URL: /users/1
    return userService.findById(id);
}

@GetMapping("/users/{userId}/orders/{orderId}")
public Order getOrder(
        @PathVariable Long userId,
        @PathVariable Long orderId) {
    // URL: /users/1/orders/100
    return orderService.findById(userId, orderId);
}
```

---

### Q16: How to handle file uploads in Spring Boot?

**A:** Use `MultipartFile`.

**Controller:**
```java
@RestController
public class FileUploadController {
    
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(
            @RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("File is empty");
        }
        
        try {
            // Save file
            String filename = file.getOriginalFilename();
            Path path = Paths.get("uploads/" + filename);
            Files.write(path, file.getBytes());
            
            return ResponseEntity.ok("File uploaded: " + filename);
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body("Upload failed: " + e.getMessage());
        }
    }
}
```

**Configuration:**
```properties
spring.servlet.multipart.enabled=true
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB
```

---

### Q17: What is the difference between @Autowired and @Resource?

**A:**

| Aspect | @Autowired | @Resource |
|:---:|:---:|:---:|
| **Source** | Spring framework | JSR-250 (Java standard) |
| **Injection** | By type, then by name | By name, then by type |
| **Required** | Can be optional (@Autowired(required=false)) | Required by default |
| **Use Case** | Spring applications | JSR-250 compatible |

**@Autowired:**
```java
@Autowired
private UserRepository userRepository;  // By type

@Autowired
@Qualifier("userRepositoryJpa")
private UserRepository repository;  // By name with qualifier
```

**@Resource:**
```java
@Resource(name = "userRepository")
private UserRepository repository;  // By name first
```

**Recommendation:** Use `@Autowired` in Spring Boot applications.

---

### Q18: How does Spring Boot handle CORS?

**A:** Cross-Origin Resource Sharing configuration.

**Global CORS Configuration:**
```java
@Configuration
public class CorsConfig {
    
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins("http://localhost:3000")
                    .allowedMethods("GET", "POST", "PUT", "DELETE")
                    .allowedHeaders("*")
                    .allowCredentials(true);
            }
        };
    }
}
```

**Method-Level:**
```java
@CrossOrigin(origins = "http://localhost:3000")
@RestController
public class UserController {
    // CORS enabled for this controller
}
```

**Spring Security:**
```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOrigins(Arrays.asList("http://localhost:3000"));
    configuration.setAllowedMethods(Arrays.asList("GET", "POST"));
    http.cors().configurationSource(corsConfigurationSource());
}
```

---

### Q19: What is the difference between @ControllerAdvice and @RestControllerAdvice?

**A:**

| Aspect | @ControllerAdvice | @RestControllerAdvice |
|:---:|:---:|:---:|
| **Returns** | View names or @ResponseBody | Data directly (JSON/XML) |
| **Use Case** | MVC applications | REST APIs |
| **Equivalent** | @Controller + @ResponseBody | @RestController |

**@ControllerAdvice:**
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public ModelAndView handleException(Exception ex) {
        ModelAndView mav = new ModelAndView("error");
        mav.addObject("error", ex.getMessage());
        return mav;  // Returns view
    }
}
```

**@RestControllerAdvice:**
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleException(Exception ex) {
        ErrorResponse error = new ErrorResponse(ex.getMessage());
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(error);  // Returns JSON
    }
}
```

---

### Q20: How to implement caching in Spring Boot?

**A:** Use Spring Cache abstraction.

**1. Enable Caching:**
```java
@SpringBootApplication
@EnableCaching
public class Application {
    // ...
}
```

**2. Configure Cache:**
```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager("users", "products");
    }
}
```

**3. Use Caching:**
```java
@Service
public class UserService {
    
    @Cacheable("users")
    public User findById(Long id) {
        // Cached - only executes once per id
        return userRepository.findById(id).orElseThrow();
    }
    
    @CacheEvict(value = "users", key = "#id")
    public void delete(Long id) {
        // Evicts cache entry
        userRepository.deleteById(id);
    }
    
    @CachePut(value = "users", key = "#user.id")
    public User update(User user) {
        // Updates cache
        return userRepository.save(user);
    }
}
```

**Redis Cache:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

```java
@Bean
public CacheManager cacheManager(RedisConnectionFactory factory) {
    RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
        .entryTtl(Duration.ofMinutes(10));
    return RedisCacheManager.builder(factory)
        .cacheDefaults(config)
        .build();
}
```

---

### Q21: What is the difference between @ComponentScan and @SpringBootApplication?

**A:**

**@ComponentScan:**
- Scans for components in specified packages
- Part of `@SpringBootApplication`
- Can be customized

**@SpringBootApplication:**
- Includes `@ComponentScan`
- Scans from package of annotated class
- Can customize base packages

**Custom Component Scan:**
```java
@SpringBootApplication
@ComponentScan(basePackages = {"com.example", "com.other"})
public class Application {
    // Scans com.example and com.other packages
}
```

---

### Q22: How to implement async processing in Spring Boot?

**A:** Use `@Async` annotation.

**1. Enable Async:**
```java
@SpringBootApplication
@EnableAsync
public class Application {
    // ...
}
```

**2. Async Method:**
```java
@Service
public class EmailService {
    
    @Async
    public CompletableFuture<String> sendEmail(String to, String subject) {
        // Async execution
        // Returns CompletableFuture
        return CompletableFuture.completedFuture("Email sent");
    }
}
```

**3. Custom Executor:**
```java
@Configuration
@EnableAsync
public class AsyncConfig {
    
    @Bean(name = "taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }
}

@Service
public class EmailService {
    
    @Async("taskExecutor")
    public void sendEmail(String to) {
        // Uses custom executor
    }
}
```

---

### Q23: What is the difference between @Transactional and @Modifying?

**A:**

**@Transactional:**
- Manages transactions
- Can be used on methods/classes
- Works with JPA repositories

**@Modifying:**
- Used with `@Query` for update/delete operations
- Must be used with `@Transactional`
- Required for custom update queries

**Example:**
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.email = :email WHERE u.id = :id")
    int updateEmail(@Param("id") Long id, @Param("email") String email);
    
    @Modifying
    @Transactional
    @Query("DELETE FROM User u WHERE u.active = false")
    int deleteInactiveUsers();
}
```

**Note:** `@Modifying` queries don't return entities, return int (affected rows).

---

### Q24: How to implement pagination in Spring Boot?

**A:** Use Spring Data JPA pagination.

**Repository:**
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    Page<User> findByActiveTrue(Pageable pageable);
    
    @Query("SELECT u FROM User u WHERE u.name LIKE %:name%")
    Page<User> searchByName(@Param("name") String name, Pageable pageable);
}
```

**Service:**
```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    public Page<User> getUsers(int page, int size, String sortBy) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sortBy));
        return userRepository.findAll(pageable);
    }
}
```

**Controller:**
```java
@RestController
public class UserController {
    
    @GetMapping("/users")
    public ResponseEntity<Page<User>> getUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "id") String sortBy) {
        Page<User> users = userService.getUsers(page, size, sortBy);
        return ResponseEntity.ok(users);
    }
}
```

---

### Q25: What is the difference between @Primary and @Qualifier?

**A:**

| Aspect | @Primary | @Qualifier |
|:---:|:---:|:---:|
| **Purpose** | Default bean when multiple candidates | Specific bean selection |
| **Usage** | One primary bean | Multiple qualifiers |
| **Priority** | Lower priority than @Qualifier | Higher priority |

**@Primary:**
```java
@Primary
@Component
public class MySQLDataSource implements DataSource {
    // Default when multiple DataSource beans exist
}

@Component
public class PostgreSQLDataSource implements DataSource {
    // Not primary
}
```

**@Qualifier:**
```java
@Component
@Qualifier("mysql")
public class MySQLDataSource implements DataSource {
    // ...
}

@Service
public class UserService {
    
    @Autowired
    @Qualifier("mysql")
    private DataSource dataSource;  // Specific bean
}
```

**Priority:** `@Qualifier` takes precedence over `@Primary`.

---

### Q26: How to implement validation in Spring Boot?

**A:** Use Bean Validation (JSR-303).

**1. Add Dependency:**
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
```

**2. Entity Validation:**
```java
public class User {
    
    @NotNull
    @NotBlank
    private String name;
    
    @Email
    private String email;
    
    @Min(18)
    @Max(100)
    private int age;
    
    @Pattern(regexp = "^[0-9]{10}$")
    private String phone;
}
```

**3. Controller Validation:**
```java
@RestController
public class UserController {
    
    @PostMapping("/users")
    public ResponseEntity<User> createUser(
            @Valid @RequestBody User user) {
        // @Valid triggers validation
        return ResponseEntity.ok(userService.save(user));
    }
}
```

**4. Custom Validator:**
```java
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = EmailValidator.class)
public @interface ValidEmail {
    String message() default "Invalid email";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

public class EmailValidator implements ConstraintValidator<ValidEmail, String> {
    @Override
    public boolean isValid(String email, ConstraintValidatorContext context) {
        // Custom validation logic
        return email != null && email.contains("@");
    }
}
```

---

### Q27: What is the difference between @GetMapping, @PostMapping, etc.?

**A:** These are composed annotations combining `@RequestMapping` with HTTP method.

| Annotation | HTTP Method | Equivalent @RequestMapping |
|:---:|:---:|:---:|
| **@GetMapping** | GET | @RequestMapping(method = RequestMethod.GET) |
| **@PostMapping** | POST | @RequestMapping(method = RequestMethod.POST) |
| **@PutMapping** | PUT | @RequestMapping(method = RequestMethod.PUT) |
| **@DeleteMapping** | DELETE | @RequestMapping(method = RequestMethod.DELETE) |
| **@PatchMapping** | PATCH | @RequestMapping(method = RequestMethod.PATCH) |

**Example:**
```java
// Old way
@RequestMapping(value = "/users", method = RequestMethod.GET)
public List<User> getUsers() {
    // ...
}

// New way (Spring 4.3+)
@GetMapping("/users")
public List<User> getUsers() {
    // ...
}
```

**Benefits:**
- More concise
- Better readability
- Type-safe

---

### Q28: How to implement rate limiting in Spring Boot?

**A:** Multiple approaches:

**1. Using Bucket4j:**
```xml
<dependency>
    <groupId>com.github.vladimir-bukhtoyarov</groupId>
    <artifactId>bucket4j-core</artifactId>
</dependency>
```

```java
@Service
public class RateLimitService {
    
    private final Map<String, Bucket> cache = new ConcurrentHashMap<>();
    
    public Bucket resolveBucket(String key) {
        return cache.computeIfAbsent(key, k -> {
            return Bucket4j.builder()
                .addLimit(Bandwidth.classic(10, Refill.intervally(10, Duration.ofMinutes(1))))
                .build();
        });
    }
}

@RestController
public class ApiController {
    
    @Autowired
    private RateLimitService rateLimitService;
    
    @GetMapping("/api/data")
    public ResponseEntity<?> getData(HttpServletRequest request) {
        String key = request.getRemoteAddr();
        Bucket bucket = rateLimitService.resolveBucket(key);
        
        if (bucket.tryConsume(1)) {
            return ResponseEntity.ok("Data");
        }
        return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
            .body("Rate limit exceeded");
    }
}
```

**2. Using Spring Cloud Gateway:**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: http://localhost:8080
          filters:
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
```

---

### Q29: What is the difference between @Value and @ConfigurationProperties?

**A:**

| Aspect | @Value | @ConfigurationProperties |
|:---:|:---:|:---:|
| **Scope** | Single property | Multiple related properties |
| **Type Safety** | No | Yes (type-safe) |
| **Validation** | No | Yes (@Valid) |
| **Relaxed Binding** | No | Yes (kebab-case, etc.) |

**@Value:**
```java
@Component
public class AppConfig {
    
    @Value("${app.name}")
    private String appName;
    
    @Value("${app.timeout:30}")  // Default value
    private int timeout;
    
    @Value("#{systemProperties['java.home']}")  // SpEL
    private String javaHome;
}
```

**@ConfigurationProperties:**
```java
@ConfigurationProperties(prefix = "app")
@Validated
public class AppProperties {
    
    @NotBlank
    private String name;
    
    @Min(1)
    @Max(100)
    private int timeout;
    
    private List<String> features;
    
    // Getters and setters
}

// Usage
@SpringBootApplication
@EnableConfigurationProperties(AppProperties.class)
public class Application {
    // ...
}
```

**application.properties:**
```properties
app.name=MyApp
app.timeout=30
app.features[0]=feature1
app.features[1]=feature2
```

**Recommendation:** Use `@ConfigurationProperties` for multiple related properties.

---

### Q30: How to implement scheduled tasks in Spring Boot?

**A:** Use `@Scheduled` annotation.

**1. Enable Scheduling:**
```java
@SpringBootApplication
@EnableScheduling
public class Application {
    // ...
}
```

**2. Scheduled Methods:**
```java
@Component
public class ScheduledTasks {
    
    @Scheduled(fixedRate = 5000)  // Every 5 seconds
    public void taskWithFixedRate() {
        System.out.println("Fixed rate task");
    }
    
    @Scheduled(fixedDelay = 5000)  // 5 seconds after previous completes
    public void taskWithFixedDelay() {
        System.out.println("Fixed delay task");
    }
    
    @Scheduled(cron = "0 0 12 * * ?")  // Every day at noon
    public void taskWithCron() {
        System.out.println("Cron task");
    }
    
    @Scheduled(initialDelay = 10000, fixedRate = 5000)  // Start after 10s
    public void taskWithInitialDelay() {
        System.out.println("Task with initial delay");
    }
}
```

**3. Custom Task Scheduler:**
```java
@Configuration
@EnableScheduling
public class SchedulingConfig {
    
    @Bean
    public TaskScheduler taskScheduler() {
        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(10);
        scheduler.setThreadNamePrefix("scheduled-");
        scheduler.initialize();
        return scheduler;
    }
}
```

</div>

---

## 📚 Advanced/Expert Interview Questions

<div align="center">

### Q1: How does Spring Boot auto-configuration work internally?

**A:** Auto-configuration uses conditional annotations and classpath scanning.

**Process:**

1. **Spring Boot Starter:** Includes `spring-boot-autoconfigure` jar
2. **META-INF/spring.factories:** Lists auto-configuration classes
3. **@ConditionalOnClass:** Checks if class exists on classpath
4. **@ConditionalOnProperty:** Checks property values
5. **Bean Creation:** Creates beans if conditions met

**spring.factories:**
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,\
org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration
```

**Auto-Configuration Class:**
```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(prefix = "spring.datasource", name = "url")
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public DataSource dataSource(DataSourceProperties properties) {
        return DataSourceBuilder.create()
            .url(properties.getUrl())
            .username(properties.getUsername())
            .password(properties.getPassword())
            .build();
    }
}
```

---

### Q2: What is the difference between @SpringBootTest and @WebMvcTest?

**A:**

| Aspect | @SpringBootTest | @WebMvcTest |
|:---:|:---:|:---:|
| **Context** | Full application context | Only web layer |
| **Beans** | All beans loaded | Only web-related beans |
| **Speed** | Slower | Faster |
| **Use Case** | Integration tests | Controller unit tests |

**@SpringBootTest:**
```java
@SpringBootTest
@AutoConfigureMockMvc
class UserServiceIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private UserRepository userRepository;  // Available
    
    @Test
    void testGetUser() throws Exception {
        // Full context loaded
    }
}
```

**@WebMvcTest:**
```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;  // Must mock
    
    @Test
    void testGetUser() throws Exception {
        // Only web layer loaded
    }
}
```

---

### Q3: How does Spring Boot handle multiple datasources?

**A:** Configure multiple DataSource beans.

**Configuration:**
```java
@Configuration
public class DataSourceConfig {
    
    @Primary
    @Bean(name = "primaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean(name = "secondaryDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.secondary")
    public DataSource secondaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    public LocalContainerEntityManagerFactoryBean primaryEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("primaryDataSource") DataSource dataSource) {
        return builder
            .dataSource(dataSource)
            .packages("com.example.primary")
            .persistenceUnit("primary")
            .build();
    }
    
    @Bean
    public LocalContainerEntityManagerFactoryBean secondaryEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("secondaryDataSource") DataSource dataSource) {
        return builder
            .dataSource(dataSource)
            .packages("com.example.secondary")
            .persistenceUnit("secondary")
            .build();
    }
}
```

**application.properties:**
```properties
spring.datasource.primary.url=jdbc:mysql://localhost:3306/primarydb
spring.datasource.primary.username=root
spring.datasource.primary.password=password

spring.datasource.secondary.url=jdbc:mysql://localhost:3306/secondarydb
spring.datasource.secondary.username=root
spring.datasource.secondary.password=password
```

---

### Q4: What is the difference between @MockBean and @Mock?

**A:**

| Aspect | @MockBean | @Mock |
|:---:|:---:|:---:|
| **Framework** | Spring Boot | Mockito |
| **Context** | Adds to Spring context | Standalone mock |
| **Use Case** | Integration tests | Unit tests |
| **Replacement** | Replaces bean in context | No context |

**@MockBean:**
```java
@SpringBootTest
class UserServiceTest {
    
    @MockBean
    private UserRepository userRepository;  // Replaces bean in context
    
    @Autowired
    private UserService userService;  // Uses mocked repository
    
    @Test
    void test() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        // ...
    }
}
```

**@Mock:**
```java
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;  // Standalone mock
    
    @InjectMocks
    private UserService userService;  // Injects mock
    
    @Test
    void test() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        // ...
    }
}
```

---

### Q5: How to implement custom starter in Spring Boot?

**A:** Create a custom starter module.

**1. Create Starter Module:**
```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-autoconfigure</artifactId>
</dependency>
```

**2. Create Auto-Configuration:**
```java
@Configuration
@ConditionalOnClass(CustomService.class)
@EnableConfigurationProperties(CustomProperties.class)
public class CustomAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public CustomService customService(CustomProperties properties) {
        return new CustomService(properties);
    }
}
```

**3. Create Properties:**
```java
@ConfigurationProperties(prefix = "custom")
public class CustomProperties {
    private String name;
    private int timeout;
    // Getters and setters
}
```

**4. Register in spring.factories:**
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.custom.CustomAutoConfiguration
```

**5. Use Starter:**
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>custom-spring-boot-starter</artifactId>
</dependency>
```

---

### Q6: What is the difference between @Transactional and @Transactional(readOnly=true)?

**A:**

| Aspect | @Transactional | @Transactional(readOnly=true) |
|:---:|:---:|:---:|
| **Read Operations** | Can read | Can read |
| **Write Operations** | Can write | Cannot write |
| **Performance** | Normal | Optimized (hints to JPA) |
| **Use Case** | Read-write operations | Read-only operations |

**Read-Only Transaction:**
```java
@Transactional(readOnly = true)
public List<User> findAll() {
    // Optimized for read-only
    // JPA can skip dirty checking
    return userRepository.findAll();
}

@Transactional  // Read-write
public User save(User user) {
    // Can write
    return userRepository.save(user);
}
```

**Benefits of readOnly:**
- Performance optimization
- JPA hints (no dirty checking)
- Database optimization

---

### Q7: How does Spring Boot handle database migrations?

**A:** Using Flyway or Liquibase.

**Flyway:**

**1. Add Dependency:**
```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

**2. Create Migrations:**
```sql
-- V1__Create_users_table.sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255)
);

-- V2__Add_email_column.sql
ALTER TABLE users ADD COLUMN email VARCHAR(255);
```

**3. Configuration:**
```properties
spring.flyway.enabled=true
spring.flyway.locations=classpath:db/migration
spring.flyway.baseline-on-migrate=true
```

**Liquibase:**

**1. Add Dependency:**
```xml
<dependency>
    <groupId>org.liquibase</groupId>
    <artifactId>liquibase-core</artifactId>
</dependency>
```

**2. Create changelog:**
```xml
<!-- db/changelog/db.changelog-master.xml -->
<databaseChangeLog>
    <changeSet id="1" author="developer">
        <createTable tableName="users">
            <column name="id" type="BIGINT">
                <constraints primaryKey="true"/>
            </column>
            <column name="name" type="VARCHAR(255)"/>
        </createTable>
    </changeSet>
</databaseChangeLog>
```

---

### Q8: What is the difference between @ComponentScan and @Import?

**A:**

| Aspect | @ComponentScan | @Import |
|:---:|:---:|:---:|
| **Purpose** | Scan for components | Import configuration classes |
| **Scope** | Package scanning | Specific classes |
| **Use Case** | Auto-discovery | Explicit import |

**@ComponentScan:**
```java
@ComponentScan(basePackages = "com.example")
public class Config {
    // Scans com.example package for @Component, @Service, etc.
}
```

**@Import:**
```java
@Configuration
@Import({DatabaseConfig.class, SecurityConfig.class})
public class AppConfig {
    // Explicitly imports configuration classes
}
```

**Use Cases:**
- **@ComponentScan:** Auto-discovery of components
- **@Import:** Import specific configurations, third-party configs

---

### Q9: How to implement custom health indicators?

**A:** Implement `HealthIndicator` interface.

**Custom Health Indicator:**
```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(1)) {
                return Health.up()
                    .withDetail("database", "Available")
                    .withDetail("validationQuery", "SELECT 1")
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withDetail("database", "Unavailable")
                .withDetail("error", e.getMessage())
                .build();
        }
        return Health.down().build();
    }
}
```

**Composite Health:**
```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    
    @Autowired
    private List<HealthIndicator> healthIndicators;
    
    @Override
    public Health health() {
        Map<String, Object> details = new HashMap<>();
        boolean allHealthy = true;
        
        for (HealthIndicator indicator : healthIndicators) {
            Health health = indicator.health();
            details.put(indicator.getClass().getSimpleName(), health.getStatus());
            if (health.getStatus() != Status.UP) {
                allHealthy = false;
            }
        }
        
        return allHealthy ? Health.up().withDetails(details).build()
                          : Health.down().withDetails(details).build();
    }
}
```

---

### Q10: What is the difference between @ConditionalOnClass and @ConditionalOnBean?

**A:**

| Aspect | @ConditionalOnClass | @ConditionalOnBean |
|:---:|:---:|:---:|
| **Checks** | Class on classpath | Bean in Spring context |
| **Timing** | Compile/classpath time | Runtime (after context loads) |
| **Use Case** | Check for library | Check for bean existence |

**@ConditionalOnClass:**
```java
@Configuration
@ConditionalOnClass(DataSource.class)  // Checks if DataSource class exists
public class DataSourceConfig {
    // Only if DataSource class is on classpath
}
```

**@ConditionalOnBean:**
```java
@Configuration
@ConditionalOnBean(DataSource.class)  // Checks if DataSource bean exists
public class JdbcTemplateConfig {
    // Only if DataSource bean is in context
}
```

**Order Matters:**
- `@ConditionalOnClass` checked first (classpath)
- `@ConditionalOnBean` checked later (after beans created)

---

### Q11: How to implement custom error pages in Spring Boot?

**A:** Multiple approaches:

**1. Static Error Pages:**
```
src/main/resources/static/error/
├── 404.html
├── 500.html
└── error.html
```

**2. Template Error Pages:**
```
src/main/resources/templates/error/
├── 404.html
└── 500.html
```

**3. Custom ErrorController:**
```java
@Controller
public class CustomErrorController implements ErrorController {
    
    @RequestMapping("/error")
    public String handleError(HttpServletRequest request) {
        Object status = request.getAttribute(RequestDispatcher.ERROR_STATUS_CODE);
        
        if (status != null) {
            Integer statusCode = Integer.valueOf(status.toString());
            
            if (statusCode == 404) {
                return "error/404";
            } else if (statusCode == 500) {
                return "error/500";
            }
        }
        return "error/error";
    }
}
```

**4. @ControllerAdvice:**
```java
@ControllerAdvice
public class GlobalErrorHandler {
    
    @ExceptionHandler(Exception.class)
    public ModelAndView handleException(Exception ex) {
        ModelAndView mav = new ModelAndView("error");
        mav.addObject("error", ex.getMessage());
        return mav;
    }
}
```

---

### Q12: What is the difference between @SpringBootApplication and @EnableAutoConfiguration?

**A:** (Already covered, but expanding)

**@SpringBootApplication:**
```java
@SpringBootApplication
public class Application {
    // Equivalent to:
    // @Configuration
    // @EnableAutoConfiguration
    // @ComponentScan(basePackages = "com.example")
}
```

**@EnableAutoConfiguration:**
```java
@Configuration
@EnableAutoConfiguration
public class Config {
    // Only enables auto-configuration
    // No component scanning
    // Must be used with @Configuration
}
```

**When to Use:**
- **@SpringBootApplication:** Main application class
- **@EnableAutoConfiguration:** Custom configuration classes that need auto-config

---

### Q13: How does Spring Boot handle JSON serialization?

**A:** Uses Jackson by default.

**1. Default Configuration:**
```java
@RestController
public class UserController {
    
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        // Automatically serialized to JSON
        return userService.findById(id);
    }
}
```

**2. Custom ObjectMapper:**
```java
@Configuration
public class JacksonConfig {
    
    @Bean
    @Primary
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);
        mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
        mapper.registerModule(new JavaTimeModule());
        return mapper;
    }
}
```

**3. Custom Serializer:**
```java
public class UserSerializer extends JsonSerializer<User> {
    @Override
    public void serialize(User user, JsonGenerator gen, SerializerProvider serializers) 
            throws IOException {
        gen.writeStartObject();
        gen.writeStringField("name", user.getName());
        gen.writeNumberField("age", user.getAge());
        gen.writeEndObject();
    }
}

@JsonSerialize(using = UserSerializer.class)
public class User {
    // Custom serialization
}
```

---

### Q14: How to implement API versioning in Spring Boot?

**A:** Multiple approaches:

**1. URL Versioning:**
```java
@RestController
@RequestMapping("/api/v1/users")
public class UserControllerV1 {
    // Version 1
}

@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 {
    // Version 2
}
```

**2. Header Versioning:**
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping(headers = "API-Version=1")
    public ResponseEntity<User> getUserV1(@PathVariable Long id) {
        // Version 1 logic
    }
    
    @GetMapping(headers = "API-Version=2")
    public ResponseEntity<UserV2> getUserV2(@PathVariable Long id) {
        // Version 2 logic
    }
}
```

**3. Content Negotiation:**
```java
@GetMapping(value = "/users/{id}", produces = {
    "application/vnd.api.v1+json",
    "application/vnd.api.v2+json"
})
public ResponseEntity<?> getUser(
        @PathVariable Long id,
        @RequestHeader("Accept") String accept) {
    if (accept.contains("v1")) {
        return ResponseEntity.ok(userV1);
    }
    return ResponseEntity.ok(userV2);
}
```

---

### Q15: What is the difference between @RequestHeader and HttpHeaders?

**A:**

**@RequestHeader:**
- Extracts specific header value
- Simpler for single headers

**HttpHeaders:**
- Provides all headers
- More flexible

**@RequestHeader:**
```java
@GetMapping("/api/data")
public ResponseEntity<?> getData(
        @RequestHeader("Authorization") String auth,
        @RequestHeader(value = "X-Custom-Header", required = false) String custom) {
    // Specific headers
}
```

**HttpHeaders:**
```java
@GetMapping("/api/data")
public ResponseEntity<?> getData(HttpHeaders headers) {
    String auth = headers.getFirst("Authorization");
    List<String> customHeaders = headers.get("X-Custom-Header");
    // All headers available
}
```

---

### Q16: How to implement request/response logging in Spring Boot?

**A:** Use interceptors or filters.

**1. Interceptor:**
```java
@Component
public class LoggingInterceptor implements HandlerInterceptor {
    
    private static final Logger logger = LoggerFactory.getLogger(LoggingInterceptor.class);
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, 
                           Object handler) {
        logger.info("Request: {} {}", request.getMethod(), request.getRequestURI());
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                               Object handler, Exception ex) {
        logger.info("Response: {} - Status: {}", request.getRequestURI(), 
                   response.getStatus());
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Autowired
    private LoggingInterceptor loggingInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loggingInterceptor);
    }
}
```

**2. Filter:**
```java
@Component
public class LoggingFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, 
                        FilterChain chain) throws IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        logger.info("Request: {} {}", httpRequest.getMethod(), httpRequest.getRequestURI());
        
        chain.doFilter(request, response);
        
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        logger.info("Response Status: {}", httpResponse.getStatus());
    }
}
```

**3. Using Actuator:**
```properties
management.endpoints.web.logging.enabled=true
logging.level.org.springframework.web=DEBUG
```

---

### Q17: What is the difference between @RequestBody and @RequestParam?

**A:**

| Aspect | @RequestBody | @RequestParam |
|:---:|:---:|:---:|
| **Content Type** | JSON/XML (body) | Form data (query/body) |
| **Location** | Request body | Query parameters or form data |
| **Use Case** | Complex objects | Simple parameters |
| **Binding** | JSON to object | String to parameter |

**@RequestBody:**
```java
@PostMapping("/users")
public ResponseEntity<User> createUser(@RequestBody User user) {
    // JSON body: {"name": "John", "email": "john@example.com"}
    return ResponseEntity.ok(userService.save(user));
}
```

**@RequestParam:**
```java
@GetMapping("/users")
public List<User> searchUsers(
        @RequestParam String name,
        @RequestParam(required = false, defaultValue = "0") int page) {
    // URL: /users?name=John&page=1
    return userService.search(name, page);
}
```

---

### Q18: How to implement custom validation annotations?

**A:** Create custom validator.

**1. Create Annotation:**
```java
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PhoneNumberValidator.class)
public @interface ValidPhoneNumber {
    String message() default "Invalid phone number";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

**2. Create Validator:**
```java
public class PhoneNumberValidator implements ConstraintValidator<ValidPhoneNumber, String> {
    
    private static final Pattern PHONE_PATTERN = 
        Pattern.compile("^[0-9]{10}$");
    
    @Override
    public void initialize(ValidPhoneNumber constraintAnnotation) {
        // Initialization if needed
    }
    
    @Override
    public boolean isValid(String phone, ConstraintValidatorContext context) {
        if (phone == null) {
            return true;  // Let @NotNull handle null
        }
        return PHONE_PATTERN.matcher(phone).matches();
    }
}
```

**3. Use Annotation:**
```java
public class User {
    
    @ValidPhoneNumber
    private String phone;
}
```

---

### Q19: What is the difference between @Transactional and @Transactional(propagation=REQUIRES_NEW)?

**A:**

**@Transactional (REQUIRED - default):**
- Joins existing transaction if exists
- Creates new if no transaction

**@Transactional(propagation = REQUIRES_NEW):**
- Always creates new transaction
- Suspends existing transaction

**Example:**
```java
@Service
public class OrderService {
    
    @Transactional
    public void processOrder(Order order) {
        orderRepository.save(order);
        paymentService.processPayment(order);  // Same transaction
    }
}

@Service
public class PaymentService {
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processPayment(Order order) {
        // New transaction - commits independently
        // Even if processOrder() fails, payment is saved
        paymentRepository.save(payment);
    }
}
```

**Use Case:** Logging, auditing - should commit even if main transaction fails.

---

### Q20: How to implement custom actuator endpoints?

**A:** Create custom endpoint.

**1. Create Endpoint:**
```java
@Component
@Endpoint(id = "custom")
public class CustomEndpoint {
    
    @ReadOperation
    public Map<String, Object> customInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("status", "UP");
        info.put("timestamp", System.currentTimeMillis());
        return info;
    }
    
    @WriteOperation
    public void customAction(@Selector String action) {
        // Custom action
        System.out.println("Action: " + action);
    }
}
```

**2. Expose Endpoint:**
```properties
management.endpoints.web.exposure.include=custom
management.endpoint.custom.enabled=true
```

**3. Access:**
```
GET /actuator/custom
POST /actuator/custom/{action}
```

---

### Q21: What is the difference between @SpringBootApplication and @SpringBootConfiguration?

**A:**

**@SpringBootApplication:**
- Combines @Configuration, @EnableAutoConfiguration, @ComponentScan
- Used for main application class

**@SpringBootConfiguration:**
- Alternative to @Configuration
- Indicates Spring Boot configuration
- Can be used in tests

**Example:**
```java
@SpringBootApplication
public class Application {
    // Main application
}

@SpringBootConfiguration
public class TestConfig {
    // Test configuration
}
```

---

### Q22: How to implement custom property sources in Spring Boot?

**A:** Use `@PropertySource` or programmatic approach.

**1. @PropertySource:**
```java
@Configuration
@PropertySource("classpath:custom.properties")
public class CustomConfig {
    // Loads custom.properties
}
```

**2. Programmatic:**
```java
@SpringBootApplication
public class Application {
    
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(Application.class);
        
        // Add property source
        app.setDefaultProperties(Collections.singletonMap(
            "custom.property", "value"
        ));
        
        app.run(args);
    }
}
```

**3. EnvironmentPostProcessor:**
```java
public class CustomEnvironmentPostProcessor implements EnvironmentPostProcessor {
    
    @Override
    public void postProcessEnvironment(ConfigurableEnvironment environment,
                                     SpringApplication application) {
        Properties props = new Properties();
        // Load custom properties
        environment.getPropertySources()
            .addFirst(new PropertiesPropertySource("custom", props));
    }
}
```

---

### Q23: What is the difference between @MockBean and @SpyBean?

**A:**

| Aspect | @MockBean | @SpyBean |
|:---:|:---:|:---:|
| **Behavior** | Mock (no real implementation) | Spy (real implementation, can verify) |
| **Default** | Returns default/null | Calls real method |
| **Use Case** | Complete mock | Partial mock, verify calls |

**@MockBean:**
```java
@SpringBootTest
class UserServiceTest {
    
    @MockBean
    private UserRepository userRepository;  // Complete mock
    
    @Test
    void test() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        // Must stub all methods used
    }
}
```

**@SpyBean:**
```java
@SpringBootTest
class UserServiceTest {
    
    @SpyBean
    private UserRepository userRepository;  // Real implementation
    
    @Test
    void test() {
        // Real methods called unless stubbed
        verify(userRepository, times(1)).findById(1L);
    }
}
```

---

### Q24: How to implement custom banner in Spring Boot?

**A:** Create `banner.txt` file.

**1. Create banner.txt:**
```
src/main/resources/banner.txt
```

**2. Custom Banner:**
```
  ____  _             _        ____        _   
 / ___|| |_ _ __ ___ | |__    | __ )  ___ | |_ 
 \___ \| __| '__/ _ \| '_ \   |  _ \ / _ \| __|
  ___) | |_| | | (_) | |_) |  | |_) | (_) | |_ 
 |____/ \__|_|  \___/|_.__/   |____/ \___/ \__|
```

**3. Disable Banner:**
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(Application.class);
        app.setBannerMode(Banner.Mode.OFF);
        app.run(args);
    }
}
```

**4. Programmatic Banner:**
```java
app.setBanner(new Banner() {
    @Override
    public void printBanner(Environment environment, Class<?> sourceClass, PrintStream out) {
        out.println("Custom Banner");
    }
});
```

---

### Q25: What is the difference between @Transactional and @Modifying?

**A:** (Already covered, but expanding)

**@Transactional:**
- Manages transaction boundaries
- Works with all repository methods
- Can be used on service methods

**@Modifying:**
- Required for custom update/delete queries
- Must be used with @Transactional
- Returns int (affected rows)

**Example:**
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // Standard method - @Transactional not needed (handled by JPA)
    User save(User user);
    
    // Custom update - needs @Modifying + @Transactional
    @Modifying
    @Transactional
    @Query("UPDATE User u SET u.email = :email WHERE u.id = :id")
    int updateEmail(@Param("id") Long id, @Param("email") String email);
}
```

---

### Q26: How to implement custom message converters in Spring Boot?

**A:** Configure HttpMessageConverter.

**1. Custom Converter:**
```java
public class CustomMessageConverter extends AbstractHttpMessageConverter<User> {
    
    public CustomMessageConverter() {
        super(MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML);
    }
    
    @Override
    protected boolean supports(Class<?> clazz) {
        return User.class.isAssignableFrom(clazz);
    }
    
    @Override
    protected User readInternal(Class<? extends User> clazz, 
                               HttpInputMessage inputMessage) throws IOException {
        // Custom deserialization
        return objectMapper.readValue(inputMessage.getBody(), clazz);
    }
    
    @Override
    protected void writeInternal(User user, HttpOutputMessage outputMessage) 
            throws IOException {
        // Custom serialization
        objectMapper.writeValue(outputMessage.getBody(), user);
    }
}
```

**2. Register Converter:**
```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Override
    public void configureMessageConverters(List<HttpMessageConverter<?>> converters) {
        converters.add(new CustomMessageConverter());
    }
}
```

---

### Q27: What is the difference between @SpringBootApplication and @EnableAutoConfiguration?

**A:** (Already covered)

---

### Q28: How to implement custom Spring Boot starter?

**A:** (Already covered in Q5 of Advanced section)

---

### Q29: What is the difference between @ConditionalOnProperty and @ConditionalOnExpression?

**A:**

**@ConditionalOnProperty:**
- Checks single or multiple properties
- Simple conditions

**@ConditionalOnExpression:**
- SpEL expressions
- Complex conditions

**@ConditionalOnProperty:**
```java
@Configuration
@ConditionalOnProperty(
    name = "app.feature.enabled",
    havingValue = "true",
    matchIfMissing = false
)
public class FeatureConfig {
    // Only if app.feature.enabled=true
}
```

**@ConditionalOnExpression:**
```java
@Configuration
@ConditionalOnExpression(
    "${app.feature.enabled:false} and ${app.debug:false}"
)
public class FeatureConfig {
    // Complex condition using SpEL
}
```

---

### Q30: How to implement custom Spring Boot auto-configuration?

**A:** Create auto-configuration class.

**1. Create Auto-Configuration:**
```java
@Configuration
@ConditionalOnClass(CustomService.class)
@ConditionalOnProperty(prefix = "custom", name = "enabled", havingValue = "true")
@EnableConfigurationProperties(CustomProperties.class)
public class CustomAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public CustomService customService(CustomProperties properties) {
        return new CustomService(properties);
    }
}
```

**2. Create Properties:**
```java
@ConfigurationProperties(prefix = "custom")
public class CustomProperties {
    private boolean enabled = true;
    private String name;
    // Getters and setters
}
```

**3. Register:**
```properties
# META-INF/spring.factories
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.CustomAutoConfiguration
```

</div>

---

## 🎯 Spring Boot Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use @ConfigurationProperties** | Type-safe configuration |
| **Enable Actuator in production** | Monitoring and health checks |
| **Use profiles** | Environment-specific config |
| **Implement proper exception handling** | Better error responses |
| **Use @Transactional appropriately** | Data consistency |
| **Enable caching** | Performance optimization |
| **Use DTOs** | Don't expose entities directly |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Expose all actuator endpoints** | Security risk | Expose only needed |
| **No exception handling** | Poor error responses | Use @ControllerAdvice |
| **Too many @Autowired** | Tight coupling | Use constructor injection |
| **No validation** | Invalid data | Use @Valid |

</div>

---

## 🎓 Complete Interview Question Bank

<div align="center">

### Quick Reference: Common Questions

| Category | Questions |
|:---:|:---:|
| **Fundamentals** | What is Spring Boot, difference from Spring, starters |
| **Auto-Configuration** | How it works, conditional annotations, exclusion |
| **REST APIs** | @RestController, exception handling, validation |
| **Testing** | @SpringBootTest, @WebMvcTest, @MockBean |
| **Actuator** | Endpoints, health indicators, custom endpoints |
| **Microservices** | Service discovery, API gateway, circuit breaker |
| **Advanced** | Custom starters, multiple datasources, async |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Spring Boot Purpose** | Rapid application development |
| **Auto-Configuration** | Automatic setup based on classpath |
| **Starters** | Pre-configured dependencies |
| **Actuator** | Production monitoring |
| **Profiles** | Environment-specific configuration |
| **Testing** | Unit, integration, slice tests |

**💡 Remember:** Spring Boot simplifies Spring development. Master auto-configuration, starters, Actuator, and testing for expert-level Spring Boot knowledge.

</div>

---

## 📚 Additional Resources

<div align="center">

### Recommended Reading

- **Spring Boot Reference Documentation**
- **Spring Boot in Action** by Craig Walls
- **Pro Spring Boot 2** by Felipe Gutierrez

### Practice

- Build REST APIs
- Implement microservices
- Create custom starters

</div>

---

<div align="center">

**Master Spring Boot for rapid development! 🚀**

*Comprehensive Spring Boot guide with exhaustive Q&A covering fundamentals to expert-level concepts.*

</div>
