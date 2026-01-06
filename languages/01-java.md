# ☕ Java - Expert Guide

<div align="center">

**Master Java: OOP, JVM, concurrency, and enterprise development**

[![Java](https://img.shields.io/badge/Java-Enterprise-blue?style=for-the-badge)](./)
[![OOP](https://img.shields.io/badge/OOP-Object%20Oriented-green?style=for-the-badge)](./)
[![JVM](https://img.shields.io/badge/JVM-Virtual%20Machine-orange?style=for-the-badge)](./)

*Comprehensive Java guide with Q&A for expert-level understanding*

</div>

---

## 🎯 Java Fundamentals

<div align="center">

### What is Java?

**Java is an object-oriented, platform-independent programming language.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🏗️ Object-Oriented** | Classes, objects, inheritance |
| **🌍 Platform Independent** | Write once, run anywhere (JVM) |
| **🔒 Strongly Typed** | Type safety at compile time |
| **🗑️ Garbage Collected** | Automatic memory management |
| **⚡ Multi-threaded** | Built-in concurrency support |

**Mental Model:** Think of Java like a universal translator - you write code once, and the JVM translates it to run on any platform (Windows, Linux, Mac).

</div>

---

## 🏗️ Object-Oriented Programming

<div align="center">

### Core OOP Concepts

| Concept | Description | Example |
|:---:|:---:|:---:|
| **Encapsulation** | Hide internal details | Private fields, public methods |
| **Inheritance** | Reuse code from parent class | `class Dog extends Animal` |
| **Polymorphism** | Same interface, different behavior | Method overriding |
| **Abstraction** | Hide complexity | Abstract classes, interfaces |

---

### Q&A: OOP Concepts

**Q: What is the difference between abstract class and interface?**

**A:** 
- **Abstract Class:** Can have both abstract and concrete methods, can have instance variables, supports constructors, single inheritance
- **Interface:** Only abstract methods (Java 8+ default methods), only constants, no constructors, multiple inheritance

```java
// Abstract Class
abstract class Animal {
    protected String name;
    abstract void makeSound();
    void sleep() { System.out.println("Sleeping"); }
}

// Interface
interface Flyable {
    void fly();
    default void land() { System.out.println("Landing"); }
}
```

**Q: Explain polymorphism in Java.**

**A:** Polymorphism allows objects of different types to be treated as objects of a common super type.

**Types:**
1. **Compile-time (Method Overloading):** Same method name, different parameters
2. **Runtime (Method Overriding):** Child class overrides parent method

```java
// Compile-time polymorphism
class Calculator {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }
}

// Runtime polymorphism
class Animal {
    void makeSound() { System.out.println("Some sound"); }
}
class Dog extends Animal {
    @Override
    void makeSound() { System.out.println("Bark"); }
}
```

</div>

---

## 🗑️ Memory Management

<div align="center">

### JVM Memory Structure

| Area | Description | Lifecycle |
|:---:|:---:|:---:|
| **Heap** | Object storage | Managed by GC |
| **Stack** | Method calls, local variables | Per thread |
| **Method Area** | Class metadata | Shared |
| **PC Register** | Current instruction | Per thread |
| **Native Method Stack** | Native code | Per thread |

---

### Garbage Collection

**Q: How does garbage collection work in Java?**

**A:** GC automatically reclaims memory from objects no longer referenced.

**GC Process:**
1. **Mark:** Identify unreachable objects
2. **Sweep:** Remove marked objects
3. **Compact:** Defragment memory (optional)

**GC Algorithms:**
- **Serial GC:** Single thread, small apps
- **Parallel GC:** Multiple threads, throughput
- **G1 GC:** Low latency, large heaps
- **ZGC:** Ultra-low latency, large heaps

**Q: What are the different memory generations in heap?**

**A:**
- **Young Generation:** New objects (Eden, Survivor S0, Survivor S1)
- **Old Generation:** Long-lived objects
- **Metaspace:** Class metadata (Java 8+)

</div>

---

## ⚡ Concurrency

<div align="center">

### Threading Basics

**Q: What is the difference between process and thread?**

**A:**
- **Process:** Independent execution unit with own memory space
- **Thread:** Lightweight process sharing memory space

**Q: How do you create a thread in Java?**

**A:** Three ways:

```java
// 1. Extend Thread class
class MyThread extends Thread {
    public void run() {
        System.out.println("Thread running");
    }
}
MyThread t1 = new MyThread();
t1.start();

// 2. Implement Runnable interface
class MyRunnable implements Runnable {
    public void run() {
        System.out.println("Runnable running");
    }
}
Thread t2 = new Thread(new MyRunnable());
t2.start();

// 3. Lambda expression (Java 8+)
Thread t3 = new Thread(() -> System.out.println("Lambda thread"));
t3.start();
```

---

### Synchronization

**Q: What is synchronization and why is it needed?**

**A:** Synchronization prevents race conditions when multiple threads access shared resources.

```java
class Counter {
    private int count = 0;
    
    // Synchronized method
    public synchronized void increment() {
        count++;
    }
    
    // Synchronized block
    public void decrement() {
        synchronized(this) {
            count--;
        }
    }
}
```

**Q: Difference between synchronized and volatile?**

**A:**
- **synchronized:** Provides mutual exclusion, ensures visibility and atomicity
- **volatile:** Only ensures visibility, not atomicity

```java
// Volatile - visibility only
volatile boolean flag = true;

// Synchronized - visibility + atomicity
synchronized void method() { /* ... */ }
```

---

### Concurrent Collections

**Q: What are concurrent collections in Java?**

**A:** Thread-safe collections from `java.util.concurrent` package.

| Collection | Description | Use Case |
|:---:|:---:|:---:|
| **ConcurrentHashMap** | Thread-safe HashMap | High concurrency |
| **CopyOnWriteArrayList** | Thread-safe ArrayList | Read-heavy |
| **BlockingQueue** | Thread-safe queue | Producer-consumer |
| **ConcurrentLinkedQueue** | Lock-free queue | High performance |

</div>

---

## 📦 Collections Framework

<div align="center">

### Collection Hierarchy

```
Collection
├── List (ordered, allows duplicates)
│   ├── ArrayList (array-based, fast random access)
│   ├── LinkedList (doubly-linked, fast insert/delete)
│   └── Vector (synchronized ArrayList)
├── Set (no duplicates)
│   ├── HashSet (hash table)
│   ├── LinkedHashSet (ordered HashSet)
│   └── TreeSet (sorted)
└── Queue (FIFO)
    ├── PriorityQueue
    └── Deque
```

**Q: When to use ArrayList vs LinkedList?**

**A:**
- **ArrayList:** Random access, frequent reads, less memory
- **LinkedList:** Frequent insertions/deletions, sequential access

**Q: How does HashMap work internally?**

**A:** 
- Uses array of buckets (default 16)
- Hash function maps key to bucket index
- Collisions handled by chaining (linked list) or tree (Java 8+)
- Load factor 0.75 triggers rehashing

```java
// HashMap internal structure
// Bucket[0] -> Entry(key1, value1) -> Entry(key2, value2)
// Bucket[1] -> Entry(key3, value3)
```

</div>

---

## 🔑 Key Concepts

<div align="center">

### Exception Handling

**Q: What is the difference between checked and unchecked exceptions?**

**A:**
- **Checked Exceptions:** Must be handled (compile-time), extend Exception
- **Unchecked Exceptions:** Runtime exceptions, extend RuntimeException

```java
// Checked exception - must handle
try {
    FileReader file = new FileReader("file.txt");
} catch (IOException e) {
    e.printStackTrace();
}

// Unchecked exception - optional
int[] arr = new int[5];
arr[10] = 5; // ArrayIndexOutOfBoundsException
```

---

### Generics

**Q: What are generics and why use them?**

**A:** Generics provide type safety and eliminate casting.

```java
// Without generics - unsafe
List list = new ArrayList();
list.add("Hello");
String str = (String) list.get(0); // Casting needed

// With generics - type safe
List<String> list = new ArrayList<>();
list.add("Hello");
String str = list.get(0); // No casting
```

**Q: What is type erasure?**

**A:** Generics are removed at compile time, replaced with Object or bound type.

```java
// At compile time
List<String> list = new ArrayList<>();

// After type erasure (runtime)
List list = new ArrayList(); // Raw type
```

</div>

---

## 🎯 Advanced Topics

<div align="center">

### Streams API (Java 8+)

**Q: What are Java Streams?**

**A:** Streams provide functional-style operations on collections.

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);

// Filter and map
List<Integer> squares = numbers.stream()
    .filter(n -> n % 2 == 0)
    .map(n -> n * n)
    .collect(Collectors.toList());

// Reduce
int sum = numbers.stream()
    .reduce(0, Integer::sum);
```

---

### Lambda Expressions

**Q: What are lambda expressions?**

**A:** Anonymous functions implementing functional interfaces.

```java
// Before Java 8
Runnable r = new Runnable() {
    public void run() {
        System.out.println("Hello");
    }
};

// Java 8+ Lambda
Runnable r = () -> System.out.println("Hello");

// With parameters
Function<Integer, Integer> square = x -> x * x;
```

---

### Optional

**Q: What is Optional and why use it?**

**A:** Optional prevents NullPointerException by wrapping nullable values.

```java
Optional<String> name = Optional.ofNullable(getName());

// Safe access
if (name.isPresent()) {
    System.out.println(name.get());
}

// Functional style
name.ifPresent(System.out::println);
String result = name.orElse("Default");
```

</div>

---

## 💡 Best Practices

<div align="center">

### ✅ Do's

| Practice | Why |
|:---:|:---:|
| **Use StringBuilder for string concatenation** | Performance |
| **Prefer composition over inheritance** | Flexibility |
| **Use final for immutability** | Thread safety |
| **Override equals() and hashCode() together** | Contract |
| **Use try-with-resources** | Automatic resource management |
| **Prefer interfaces over abstract classes** | Flexibility |

---

### ❌ Don'ts

| Anti-Pattern | Problem | Solution |
|:---:|:---:|:---:|
| **Catching Exception** | Too broad | Catch specific exceptions |
| **Using raw types** | Type safety | Use generics |
| **String concatenation in loops** | Performance | Use StringBuilder |
| **Ignoring equals()/hashCode()** | Bugs | Override both |

</div>

---

## 🎓 Interview Questions

<div align="center">

### Hard Interview Questions

**Q: Explain the JVM architecture.**

**A:** 
- **Class Loader:** Loads classes
- **Runtime Data Areas:** Heap, Stack, Method Area
- **Execution Engine:** Interprets bytecode, JIT compiler
- **Native Method Interface:** Interface to native libraries

**Q: What is the difference between == and equals()?**

**A:**
- **==:** Compares references (memory addresses)
- **equals():** Compares object content (should be overridden)

```java
String s1 = new String("Hello");
String s2 = new String("Hello");
s1 == s2;        // false (different references)
s1.equals(s2);   // true (same content)
```

**Q: Explain the volatile keyword.**

**A:** 
- Ensures visibility across threads
- Prevents compiler optimizations
- Not atomic for compound operations
- Use for flags, not for counters

**Q: What is the difference between wait() and sleep()?**

**A:**
- **wait():** Object method, releases lock, must be in synchronized block
- **sleep():** Thread method, doesn't release lock, can be called anywhere

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Java Philosophy** | Write once, run anywhere |
| **OOP** | Encapsulation, inheritance, polymorphism |
| **Memory** | Heap (GC), Stack (thread-local) |
| **Concurrency** | Threads, synchronization, concurrent collections |
| **Collections** | List, Set, Map - choose based on use case |

**💡 Remember:** Java is about OOP, platform independence, and automatic memory management. Master concurrency, collections, and modern Java features (Streams, Lambdas) for expert-level knowledge.

</div>

---

<div align="center">

**Master Java for enterprise development! 🚀**

*From fundamentals to expert-level Java knowledge with comprehensive Q&A.*

</div>

