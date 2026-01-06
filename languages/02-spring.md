# 🌱 Spring Framework - Expert Guide

<div align="center">

**Master Spring: IoC, DI, AOP, and enterprise patterns**

[![Spring](https://img.shields.io/badge/Spring-Framework-blue?style=for-the-badge)](./)
[![IoC](https://img.shields.io/badge/IoC-Inversion%20of%20Control-green?style=for-the-badge)](./)
[![AOP](https://img.shields.io/badge/AOP-Aspect%20Oriented-orange?style=for-the-badge)](./)

*Comprehensive Spring Framework guide with Q&A for expert-level understanding*

</div>

---

## 🎯 Spring Framework Fundamentals

<div align="center">

### What is Spring Framework?

**Spring is a comprehensive framework for building enterprise Java applications.**

### Key Features

| Feature | Description |
|:---:|:---:|
| **🔄 Inversion of Control (IoC)** | Dependency injection |
| **🔀 Aspect-Oriented Programming (AOP)** | Cross-cutting concerns |
| **🌐 MVC Framework** | Web application development |
| **💾 Data Access** | JDBC, ORM integration |
| **🔒 Security** | Authentication and authorization |
| **📊 Transaction Management** | Declarative transactions |

**Mental Model:** Think of Spring like a smart factory manager - instead of you creating and managing objects, Spring creates them for you and wires them together (dependency injection).

</div>

---

## 🔄 Inversion of Control (IoC) & Dependency Injection

<div align="center">

### Core Concepts

**Q: What is Inversion of Control (IoC)?**

**A:** IoC is a design principle where object creation and dependency management is handled by a container (Spring), not by the objects themselves.

**Traditional Approach:**
```java
// Tight coupling - bad
class UserService {
    private UserRepository repository = new UserRepositoryImpl();
}
```

**Spring Approach:**
```java
// Loose coupling - good
class UserService {
    private UserRepository repository;
    
    // Constructor injection
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

---

### Dependency Injection Types

**Q: What are the different types of dependency injection?**

**A:** Three types:

1. **Constructor Injection** (Recommended)
```java
@Service
public class UserService {
    private final UserRepository repository;
    
    public UserService(UserRepository repository) {
        this.repository = repository;
    }
}
```

2. **Setter Injection**
```java
@Service
public class UserService {
    private UserRepository repository;
    
    @Autowired
    public void setRepository(UserRepository repository) {
        this.repository = repository;
    }
}
```

3. **Field Injection** (Not recommended)
```java
@Service
public class UserService {
    @Autowired
    private UserRepository repository;
}
```

**💡 Prefer constructor injection for required dependencies.**

</div>

---

## 🫘 Spring Beans

<div align="center">

### Bean Lifecycle

**Q: What is a Spring Bean?**

**A:** A Spring Bean is an object that is instantiated, assembled, and managed by the Spring IoC container.

**Q: Explain the Spring Bean lifecycle.**

**A:**
1. **Instantiation:** Container creates bean instance
2. **Population:** Dependencies injected
3. **Initialization:** `@PostConstruct` or `InitializingBean`
4. **Ready:** Bean available for use
5. **Destruction:** `@PreDestroy` or `DisposableBean`

```java
@Component
public class MyBean implements InitializingBean, DisposableBean {
    
    @PostConstruct
    public void init() {
        System.out.println("PostConstruct called");
    }
    
    @Override
    public void afterPropertiesSet() {
        System.out.println("AfterPropertiesSet called");
    }
    
    @PreDestroy
    public void cleanup() {
        System.out.println("PreDestroy called");
    }
    
    @Override
    public void destroy() {
        System.out.println("Destroy called");
    }
}
```

---

### Bean Scopes

**Q: What are the different bean scopes in Spring?**

**A:**

| Scope | Description | Use Case |
|:---:|:---:|:---:|
| **singleton** | One instance per container (default) | Stateless services |
| **prototype** | New instance each time | Stateful beans |
| **request** | One per HTTP request | Web applications |
| **session** | One per HTTP session | User-specific data |
| **application** | One per ServletContext | Web applications |

```java
@Component
@Scope("prototype")
public class PrototypeBean {
    // New instance each time
}

@Component
@Scope("singleton") // Default
public class SingletonBean {
    // One instance shared
}
```

</div>

---

## 🔀 Aspect-Oriented Programming (AOP)

<div align="center">

### AOP Concepts

**Q: What is AOP and why is it useful?**

**A:** AOP separates cross-cutting concerns (logging, security, transactions) from business logic.

**Without AOP:**
```java
class UserService {
    public void createUser(User user) {
        logger.info("Creating user"); // Cross-cutting concern
        // Business logic
        transactionManager.begin(); // Cross-cutting concern
        repository.save(user);
        transactionManager.commit();
    }
}
```

**With AOP:**
```java
@Transactional
@Loggable
class UserService {
    public void createUser(User user) {
        // Only business logic
        repository.save(user);
    }
}
```

---

### AOP Terminology

| Term | Description |
|:---:|:---:|
| **Aspect** | Module encapsulating cross-cutting concern |
| **Join Point** | Point in execution (method call) |
| **Pointcut** | Expression matching join points |
| **Advice** | Action taken at join point |
| **Weaving** | Applying aspects to target objects |

---

### Types of Advice

**Q: What are the different types of advice?**

**A:**

1. **Before:** Executes before method
2. **After:** Executes after method (success or failure)
3. **AfterReturning:** Executes after successful return
4. **AfterThrowing:** Executes after exception
5. **Around:** Wraps method execution

```java
@Aspect
@Component
public class LoggingAspect {
    
    @Before("execution(* com.example.service.*.*(..))")
    public void logBefore(JoinPoint joinPoint) {
        System.out.println("Before: " + joinPoint.getSignature());
    }
    
    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        System.out.println("Before");
        Object result = joinPoint.proceed();
        System.out.println("After");
        return result;
    }
}
```

</div>

---

## 🌐 Spring MVC

<div align="center">

### MVC Architecture

**Q: Explain Spring MVC architecture.**

**A:** Model-View-Controller pattern for web applications.

**Flow:**
```
Request → DispatcherServlet → HandlerMapping → Controller
                                              ↓
Response ← View ← ViewResolver ← ModelAndView
```

**Components:**
- **DispatcherServlet:** Front controller
- **HandlerMapping:** Maps requests to controllers
- **Controller:** Handles request, returns model
- **ViewResolver:** Resolves view names to views
- **View:** Renders response

---

### Controller Annotations

**Q: What are the different controller annotations?**

**A:**

| Annotation | Description | Use Case |
|:---:|:---:|:---:|
| **@Controller** | MVC controller | Web controllers |
| **@RestController** | REST controller (includes @ResponseBody) | REST APIs |
| **@Service** | Service layer | Business logic |
| **@Repository** | Data access layer | DAO, repositories |

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(userService.save(user));
    }
}
```

</div>

---

## 💾 Transaction Management

<div align="center">

### Declarative Transactions

**Q: How does Spring transaction management work?**

**A:** Spring provides declarative transaction management using AOP.

```java
@Service
@Transactional
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Transactional(rollbackFor = Exception.class)
    public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
        User from = userRepository.findById(fromId);
        User to = userRepository.findById(toId);
        from.debit(amount);
        to.credit(amount);
        userRepository.save(from);
        userRepository.save(to);
        // If exception occurs, all changes rolled back
    }
}
```

**Q: What is @Transactional propagation?**

**A:** Defines how transactions behave when called from another transactional method.

| Propagation | Description |
|:---:|:---:|
| **REQUIRED** | Join existing or create new (default) |
| **REQUIRES_NEW** | Always create new transaction |
| **SUPPORTS** | Join if exists, otherwise no transaction |
| **NOT_SUPPORTED** | Suspend current transaction |
| **MANDATORY** | Must have transaction, else exception |
| **NEVER** | Must not have transaction, else exception |
| **NESTED** | Nested transaction |

</div>

---

## 🔒 Spring Security

<div align="center">

### Security Basics

**Q: How does Spring Security work?**

**A:** Spring Security provides authentication and authorization.

**Key Components:**
- **Authentication:** Who are you?
- **Authorization:** What can you do?
- **Filters:** Security filter chain

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
            .formLogin();
        return http.build();
    }
}
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Hard Interview Questions

**Q: What is the difference between @Component, @Service, @Repository, and @Controller?**

**A:**
- **@Component:** Generic Spring component
- **@Service:** Business logic layer
- **@Repository:** Data access layer (exception translation)
- **@Controller:** Web controller (MVC)
- **@RestController:** REST controller (@Controller + @ResponseBody)

**Q: Explain Spring Bean Factory vs ApplicationContext.**

**A:**
- **BeanFactory:** Basic IoC container, lazy loading
- **ApplicationContext:** Advanced container, eager loading, AOP, events

**Q: What is the difference between @Autowired and @Qualifier?**

**A:**
- **@Autowired:** Injects dependency by type
- **@Qualifier:** Specifies which bean to inject when multiple candidates

```java
@Autowired
@Qualifier("userRepositoryJpa")
private UserRepository repository;
```

**Q: How does Spring handle circular dependencies?**

**A:** 
- Constructor injection: Cannot resolve (throws exception)
- Setter/Field injection: Uses proxy objects to break cycle

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **IoC** | Container manages object lifecycle |
| **DI** | Dependencies injected, not created |
| **AOP** | Separates cross-cutting concerns |
| **Beans** | Managed objects in Spring container |
| **MVC** | Model-View-Controller for web apps |

**💡 Remember:** Spring is about IoC, DI, and AOP. Master bean lifecycle, dependency injection types, and AOP for expert-level Spring knowledge.

</div>

---

<div align="center">

**Master Spring Framework for enterprise Java! 🚀**

*From IoC to AOP - comprehensive Spring guide with Q&A for expert-level understanding.*

</div>

