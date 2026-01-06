# ☕ Java - Expert Guide

<div align="center">

**Master Java: OOP, JVM, concurrency, and enterprise development**

[![Java](https://img.shields.io/badge/Java-Enterprise-blue?style=for-the-badge)](./)
[![OOP](https://img.shields.io/badge/OOP-Object%20Oriented-green?style=for-the-badge)](./)
[![JVM](https://img.shields.io/badge/JVM-Virtual%20Machine-orange?style=for-the-badge)](./)

*Comprehensive Java guide with exhaustive Q&A for expert-level understanding*

</div>

---

## 🎯 Java Fundamentals

<div align="center">

### What is Java?

**Java is an object-oriented, platform-independent programming language developed by Sun Microsystems (now Oracle).**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **🏗️ Object-Oriented** | Classes, objects, inheritance, polymorphism |
| **🌍 Platform Independent** | Write once, run anywhere (JVM) |
| **🔒 Strongly Typed** | Type safety at compile time |
| **🗑️ Garbage Collected** | Automatic memory management |
| **⚡ Multi-threaded** | Built-in concurrency support |
| **🔒 Secure** | No pointers, bytecode verification |

**Mental Model:** Think of Java like a universal translator - you write code once, and the JVM translates it to run on any platform (Windows, Linux, Mac).

</div>

---

## 📚 Interview Questions for Freshers

<div align="center">

### Q1: Why is Java a platform independent language?

**A:** Java achieves platform independence through the Java Virtual Machine (JVM).

**Process:**
1. Java source code (`.java`) compiled to bytecode (`.class`)
2. Bytecode is platform-independent
3. JVM interprets/compiles bytecode to machine code for specific platform

```
Java Source → Compiler → Bytecode → JVM → Machine Code
(.java)              (.class)          (Platform-specific)
```

**Key Point:** Same bytecode runs on any platform with JVM installed.

---

### Q2: Why is Java not a pure object-oriented language?

**A:** Java supports primitive data types (int, char, boolean, etc.) which are not objects.

**Pure OOP Requirements:**
- ✅ Everything should be an object
- ✅ No primitive types

**Java Has:**
- ❌ Primitive types: `int`, `char`, `boolean`, `byte`, `short`, `long`, `float`, `double`
- ✅ Wrapper classes: `Integer`, `Character`, `Boolean`, etc.

**Note:** Java 5+ autoboxing/unboxing helps, but primitives still exist.

---

### Q3: Difference between Heap and Stack Memory in Java

**A:**

| Aspect | Heap Memory | Stack Memory |
|:---:|:---:|:---:|
| **Storage** | Objects and instance variables | Method calls, local variables |
| **Access** | Slower | Faster |
| **Size** | Larger, dynamic | Smaller, fixed per thread |
| **Lifecycle** | Managed by GC | Automatic (method ends) |
| **Thread Safety** | Shared across threads | Thread-local |

**Example:**
```java
public class MemoryExample {
    int instanceVar = 10;  // Stored in heap
    
    public void method() {
        int localVar = 20;  // Stored in stack
        Object obj = new Object();  // Object in heap, reference in stack
    }
}
```

**How Java Utilizes:**
- **Stack:** Method execution, local variables, method parameters
- **Heap:** Object storage, instance variables, arrays

---

### Q4: Can Java be said to be the complete object-oriented programming language?

**A:** No, because:
1. **Primitive Types:** Not objects (int, char, boolean)
2. **Static Methods:** Can be called without objects
3. **Wrapper Classes:** Exist but primitives preferred for performance

**However:** Java is one of the most object-oriented languages, with strong OOP support.

---

### Q5: How is Java different from C++?

**A:**

| Aspect | Java | C++ |
|:---:|:---:|:---:|
| **Platform** | Platform-independent | Platform-dependent |
| **Memory Management** | Automatic (GC) | Manual (new/delete) |
| **Pointers** | No explicit pointers | Supports pointers |
| **Multiple Inheritance** | Via interfaces only | Via classes |
| **Operator Overloading** | No | Yes |
| **Preprocessor** | No | Yes (#include) |
| **Goto Statement** | No | Yes |
| **Compilation** | Bytecode | Machine code |

---

### Q6: Pointers are used in C/C++. Why does Java not make use of pointers?

**A:** Java doesn't use explicit pointers for:

**Reasons:**
1. **Security:** Prevents memory corruption, buffer overflows
2. **Simplicity:** Easier to learn and use
3. **Garbage Collection:** Automatic memory management
4. **Platform Independence:** No direct memory access

**Java Uses:**
- **References:** Similar to pointers but safer
- **No pointer arithmetic:** Cannot manipulate memory addresses

```java
// Java - References (safe)
String str = new String("Hello");
// str is a reference, not a pointer

// C++ - Pointers (unsafe)
char* ptr = "Hello";
ptr++;  // Pointer arithmetic - not possible in Java
```

---

### Q7: What do you understand by an instance variable and a local variable?

**A:**

**Instance Variable:**
- Declared in class, outside methods
- Belongs to object instance
- Stored in heap
- Default values assigned
- Accessible throughout class

**Local Variable:**
- Declared inside method/block
- Belongs to method/block
- Stored in stack
- No default values (must initialize)
- Accessible only within scope

```java
class Example {
    int instanceVar;  // Instance variable (default: 0)
    
    public void method() {
        int localVar = 10;  // Local variable (must initialize)
        // instanceVar accessible here
    }
    // localVar not accessible here
}
```

---

### Q8: What are the default values assigned to variables and instances in Java?

**A:**

| Type | Default Value |
|:---:|:---:|
| **byte, short, int, long** | 0 |
| **float, double** | 0.0 |
| **char** | '\u0000' (null character) |
| **boolean** | false |
| **Object references** | null |

**Note:** Local variables don't have default values - must initialize.

```java
class DefaultValues {
    int a;           // 0
    double b;        // 0.0
    boolean c;       // false
    String d;        // null
    
    public void method() {
        int local;   // Compile error - must initialize
    }
}
```

---

### Q9: What do you mean by data encapsulation?

**A:** Encapsulation is bundling data (variables) and methods together, hiding internal details.

**Benefits:**
- ✅ Data protection
- ✅ Controlled access
- ✅ Maintainability
- ✅ Flexibility to change implementation

```java
class BankAccount {
    private double balance;  // Encapsulated data
    
    public void deposit(double amount) {  // Controlled access
        if (amount > 0) {
            balance += amount;
        }
    }
    
    public double getBalance() {  // Read-only access
        return balance;
    }
}
```

---

### Q10: Tell us something about JIT compiler

**A:** JIT (Just-In-Time) compiler converts bytecode to native machine code at runtime.

**How It Works:**
1. Bytecode interpreted initially
2. JIT identifies frequently executed code (hot spots)
3. Compiles hot spots to native code
4. Native code cached for reuse

**Benefits:**
- ✅ Faster execution than pure interpretation
- ✅ Adaptive optimization
- ✅ Platform-specific optimizations

**JIT vs AOT (Ahead-of-Time):**
- **JIT:** Compiles at runtime, can optimize based on usage
- **AOT:** Compiles before execution, faster startup

---

### Q11: Can you tell the difference between equals() method and equality operator (==) in Java?

**A:**

| Aspect | == | equals() |
|:---:|:---:|:---:|
| **Type** | Operator | Method |
| **Compares** | References (memory addresses) | Object content |
| **Primitives** | Compares values | Not applicable |
| **Objects** | Compares references | Compares content (if overridden) |

```java
String s1 = new String("Hello");
String s2 = new String("Hello");
String s3 = s1;

s1 == s2;        // false (different references)
s1.equals(s2);  // true (same content)
s1 == s3;        // true (same reference)

// For primitives
int a = 5;
int b = 5;
a == b;  // true (compares values)
```

**Important:** Always override `equals()` and `hashCode()` together.

---

### Q12: How is an infinite loop declared in Java?

**A:** Several ways:

```java
// 1. for loop
for (;;) {
    // Infinite loop
}

// 2. while loop
while (true) {
    // Infinite loop
}

// 3. do-while loop
do {
    // Infinite loop
} while (true);
```

**Use Cases:**
- Server applications
- Event loops
- Game loops

**Break from infinite loop:**
```java
while (true) {
    if (condition) {
        break;  // Exit loop
    }
}
```

---

### Q13: Briefly explain the concept of constructor overloading

**A:** Constructor overloading allows multiple constructors with different parameters.

```java
class Student {
    private String name;
    private int age;
    
    // Constructor 1: No parameters
    public Student() {
        this.name = "Unknown";
        this.age = 0;
    }
    
    // Constructor 2: Name only
    public Student(String name) {
        this.name = name;
        this.age = 0;
    }
    
    // Constructor 3: Name and age
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

// Usage
Student s1 = new Student();
Student s2 = new Student("John");
Student s3 = new Student("John", 20);
```

**Rules:**
- Same name (class name)
- Different parameters (number/type)
- Can call other constructors using `this()`

---

### Q14: Define Copy constructor in Java

**A:** Copy constructor creates an object by copying another object of the same class.

**Java doesn't have built-in copy constructors** - you implement them:

```java
class Person {
    private String name;
    private int age;
    
    // Regular constructor
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // Copy constructor
    public Person(Person other) {
        this.name = other.name;
        this.age = other.age;
    }
}

// Usage
Person p1 = new Person("John", 25);
Person p2 = new Person(p1);  // Copy
```

**Alternative:** Use `clone()` method (implements `Cloneable`).

---

### Q15: Can the main method be Overloaded?

**A:** Yes, but only the standard `main(String[] args)` is called by JVM.

```java
public class MainOverload {
    // Standard main - called by JVM
    public static void main(String[] args) {
        System.out.println("Standard main");
        main(10);  // Call overloaded main
    }
    
    // Overloaded main - can be called manually
    public static void main(int x) {
        System.out.println("Overloaded main: " + x);
    }
}
```

**Note:** JVM only recognizes `public static void main(String[] args)`.

---

### Q16: Comment on method overloading and overriding by citing relevant examples

**A:**

**Method Overloading (Compile-time Polymorphism):**
- Same method name, different parameters
- Resolved at compile time
- Can differ in: number, type, order of parameters

```java
class Calculator {
    int add(int a, int b) {
        return a + b;
    }
    
    double add(double a, double b) {
        return a + b;
    }
    
    int add(int a, int b, int c) {
        return a + b + c;
    }
}
```

**Method Overriding (Runtime Polymorphism):**
- Same method signature in parent and child
- Resolved at runtime
- Uses `@Override` annotation

```java
class Animal {
    void makeSound() {
        System.out.println("Some sound");
    }
}

class Dog extends Animal {
    @Override
    void makeSound() {
        System.out.println("Bark");
    }
}
```

**Key Differences:**

| Aspect | Overloading | Overriding |
|:---:|:---:|:---:|
| **Resolution** | Compile-time | Runtime |
| **Parameters** | Must differ | Must be same |
| **Return Type** | Can differ | Must be compatible |
| **Access Modifier** | Can differ | Cannot be more restrictive |
| **Scope** | Same class | Different classes (inheritance) |

---

### Q17: A single try block and multiple catch blocks can co-exist in a Java Program. Explain

**A:** Yes, you can have multiple catch blocks for different exception types.

```java
try {
    int result = 10 / 0;  // ArithmeticException
    String str = null;
    str.length();  // NullPointerException
} catch (ArithmeticException e) {
    System.out.println("Division by zero");
} catch (NullPointerException e) {
    System.out.println("Null pointer");
} catch (Exception e) {
    System.out.println("General exception");
}
```

**Rules:**
- More specific exceptions first
- General exceptions last
- Only one catch block executes
- Java 7+ supports multi-catch: `catch (Exception1 | Exception2 e)`

---

### Q18: Explain the use of final keyword in variable, method and class

**A:**

**1. Final Variable:**
- Cannot be reassigned
- Must be initialized
- Constants: `public static final int MAX = 100;`

```java
final int x = 10;
x = 20;  // Compile error

final String name;
name = "John";  // OK - initialized once
name = "Jane";  // Compile error
```

**2. Final Method:**
- Cannot be overridden in subclass
- Used for security/design

```java
class Parent {
    final void method() {
        // Cannot be overridden
    }
}

class Child extends Parent {
    void method() {  // Compile error
        // Cannot override
    }
}
```

**3. Final Class:**
- Cannot be extended
- Examples: String, Integer, Math

```java
final class MyClass {
    // Cannot be extended
}

class SubClass extends MyClass {  // Compile error
    // Not allowed
}
```

---

### Q19: Do final, finally and finalize keywords have the same function?

**A:** No, they serve different purposes:

| Keyword | Purpose | Usage |
|:---:|:---:|:---:|
| **final** | Prevents modification/inheritance | Variable, method, class |
| **finally** | Always executes cleanup code | Exception handling |
| **finalize()** | Called before object garbage collection | Object cleanup (deprecated) |

```java
// final - prevents modification
final int x = 10;

// finally - always executes
try {
    // code
} finally {
    // Always executes
}

// finalize() - deprecated, avoid using
protected void finalize() throws Throwable {
    // Cleanup (deprecated in Java 9)
}
```

**Note:** `finalize()` is deprecated (Java 9+) - use try-with-resources instead.

---

### Q20: Is it possible that the 'finally' block will not be executed? If yes then list the case

**A:** Yes, in rare cases:

**Cases where finally doesn't execute:**
1. **JVM exits:** `System.exit(0)` before finally
2. **Infinite loop:** Blocking operation in try
3. **Killing process:** OS kills JVM process
4. **Daemon thread:** JVM exits before daemon thread completes

```java
try {
    System.exit(0);  // JVM exits - finally won't execute
} finally {
    System.out.println("This won't print");
}
```

**Normal cases:** Finally always executes, even with return statements.

---

### Q21: When can you use super keyword?

**A:** `super` keyword refers to parent class:

**Uses:**
1. **Call parent constructor:** `super()`
2. **Access parent method:** `super.methodName()`
3. **Access parent variable:** `super.variableName`

```java
class Parent {
    String name = "Parent";
    
    Parent(String name) {
        this.name = name;
    }
    
    void display() {
        System.out.println("Parent display");
    }
}

class Child extends Parent {
    String name = "Child";
    
    Child(String name) {
        super(name);  // Call parent constructor
    }
    
    void display() {
        super.display();  // Call parent method
        System.out.println(super.name);  // Access parent variable
        System.out.println(this.name);   // Access child variable
    }
}
```

---

### Q22: Can the static methods be overloaded?

**A:** Yes, static methods can be overloaded.

```java
class MathUtils {
    static int add(int a, int b) {
        return a + b;
    }
    
    static double add(double a, double b) {
        return a + b;
    }
    
    static int add(int a, int b, int c) {
        return a + b + c;
    }
}
```

**Note:** Static methods cannot be overridden (only hidden).

---

### Q23: Why is the main method static in Java?

**A:** 
1. **Entry Point:** JVM needs to call main without creating object
2. **No Object Required:** Static methods can be called without instance
3. **JVM Limitation:** JVM can only call static methods directly

```java
public class Main {
    // Static - can be called without object
    public static void main(String[] args) {
        // JVM calls: Main.main(args)
    }
    
    // Non-static - would require object creation
    public void main(String[] args) {
        // JVM cannot call this directly
    }
}
```

**If main were non-static:** JVM would need to create object first, causing chicken-egg problem.

---

### Q24: Can the static methods be overridden?

**A:** No, static methods cannot be overridden - they can be **hidden**.

```java
class Parent {
    static void method() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    static void method() {  // Hiding, not overriding
        System.out.println("Child");
    }
}

// Usage
Parent.method();  // Parent
Child.method();   // Child

Parent obj = new Child();
obj.method();     // Parent (not Child) - method hiding
```

**Key Point:** Method resolution based on reference type, not object type.

---

### Q25: Difference between static methods, static variables, and static classes in Java

**A:**

**Static Methods:**
- Belong to class, not instance
- Can access only static members
- Called using class name

**Static Variables:**
- Shared across all instances
- Single copy in memory
- Initialized when class loads

**Static Classes:**
- Only nested classes can be static
- Don't need outer class instance
- Cannot access non-static members of outer class

```java
class Outer {
    static int staticVar = 10;  // Static variable
    
    static void staticMethod() {  // Static method
        System.out.println(staticVar);
    }
    
    static class Nested {  // Static nested class
        void method() {
            System.out.println(staticVar);  // Can access static members
        }
    }
}
```

---

### Q26: What is the main objective of garbage collection?

**A:** Garbage collection automatically reclaims memory from unreachable objects.

**Objectives:**
1. **Memory Management:** Free unused memory
2. **Prevent Memory Leaks:** Remove unreferenced objects
3. **Automatic:** No manual memory management needed
4. **Efficiency:** Optimize memory usage

**How It Works:**
- Identifies unreachable objects
- Marks them for deletion
- Reclaims memory
- Compacts heap (optional)

---

### Q27: What is a ClassLoader?

**A:** ClassLoader loads Java classes into JVM.

**Types:**
1. **Bootstrap ClassLoader:** Loads core Java classes (rt.jar)
2. **Extension ClassLoader:** Loads extension classes
3. **Application ClassLoader:** Loads application classes

**Delegation Model:**
- Child classloader delegates to parent
- Parent-first loading strategy

```java
// Get classloader
ClassLoader loader = MyClass.class.getClassLoader();
System.out.println(loader);
```

---

### Q28: What part of memory - Stack or Heap - is cleaned in garbage collection process?

**A:** **Heap memory** is cleaned by garbage collection.

**Why:**
- **Heap:** Stores objects (can become unreachable)
- **Stack:** Automatic cleanup when method ends (no GC needed)

**GC Process:**
1. Scans heap for unreachable objects
2. Marks them for deletion
3. Reclaims memory
4. Stack cleaned automatically (method returns)

---

### Q29: What are shallow copy and deep copy in Java?

**A:**

**Shallow Copy:**
- Copies object reference, not object itself
- Both references point to same object
- Changes reflect in both

**Deep Copy:**
- Creates new object with copied values
- Independent objects
- Changes don't affect each other

```java
class Address {
    String city;
    Address(String city) { this.city = city; }
}

// Shallow copy
Address addr1 = new Address("NYC");
Address addr2 = addr1;  // Shallow - same reference

// Deep copy
Address addr3 = new Address(addr1.city);  // Deep - new object
```

**Implementation:**
- **Shallow:** `clone()` method (default)
- **Deep:** Custom implementation or serialization

</div>

---

## 📚 Intermediate Interview Questions

<div align="center">

### Q1: Apart from the security aspect, what are the reasons behind making strings immutable in Java?

**A:** 

**Reasons:**
1. **String Pool:** Enables string interning, saves memory
2. **Thread Safety:** Immutable = naturally thread-safe
3. **HashCode Caching:** HashCode calculated once, cached
4. **Security:** Prevents modification of sensitive data
5. **Performance:** Can be safely shared

```java
String s1 = "Hello";
String s2 = "Hello";  // Reuses from string pool
// s1 == s2 (same reference)
```

---

### Q2: What is a singleton class in Java? And How to implement a singleton class?

**A:** Singleton ensures only one instance of a class exists.

**Implementation:**

```java
// Eager initialization
class Singleton {
    private static final Singleton instance = new Singleton();
    
    private Singleton() {}  // Private constructor
    
    public static Singleton getInstance() {
        return instance;
    }
}

// Lazy initialization (thread-safe)
class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// Enum singleton (best practice)
enum Singleton {
    INSTANCE;
    
    public void doSomething() {
        // Implementation
    }
}
```

---

### Q3: How would you differentiate between a String, StringBuffer, and a StringBuilder?

**A:**

| Aspect | String | StringBuffer | StringBuilder |
|:---:|:---:|:---:|:---:|
| **Mutability** | Immutable | Mutable | Mutable |
| **Thread Safety** | Yes (immutable) | Yes (synchronized) | No |
| **Performance** | Slower (creates new objects) | Slower (synchronized) | Faster |
| **Use Case** | When value won't change | Multi-threaded environment | Single-threaded environment |

```java
// String - immutable
String str = "Hello";
str = str + " World";  // Creates new object

// StringBuffer - thread-safe, mutable
StringBuffer sb = new StringBuffer("Hello");
sb.append(" World");  // Modifies same object

// StringBuilder - not thread-safe, mutable
StringBuilder sbd = new StringBuilder("Hello");
sbd.append(" World");  // Modifies same object
```

**When to Use:**
- **String:** When value won't change
- **StringBuffer:** Multi-threaded string manipulation
- **StringBuilder:** Single-threaded string manipulation (preferred)

---

### Q4: Using relevant properties highlight the differences between interfaces and abstract classes

**A:**

| Property | Interface | Abstract Class |
|:---:|:---:|:---:|
| **Methods** | All abstract (Java 8+ default methods) | Abstract + concrete |
| **Variables** | Only constants (public static final) | Any variables |
| **Inheritance** | Multiple (implements) | Single (extends) |
| **Constructors** | No | Yes |
| **Access Modifiers** | Public (default) | Any |
| **Main Method** | Yes (Java 8+) | Yes |
| **Static Methods** | Yes (Java 8+) | Yes |

```java
// Interface
interface Flyable {
    void fly();  // Abstract method
    default void land() {  // Default method (Java 8+)
        System.out.println("Landing");
    }
    static void info() {  // Static method (Java 8+)
        System.out.println("Flyable interface");
    }
}

// Abstract Class
abstract class Animal {
    protected String name;  // Instance variable
    
    Animal(String name) {  // Constructor
        this.name = name;
    }
    
    abstract void makeSound();  // Abstract method
    
    void sleep() {  // Concrete method
        System.out.println("Sleeping");
    }
}
```

---

### Q5: What is a Comparator in Java?

**A:** Comparator is used to define custom sorting order for objects.

```java
import java.util.*;

class Student {
    String name;
    int age;
    
    Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
}

// Comparator for age
class AgeComparator implements Comparator<Student> {
    public int compare(Student s1, Student s2) {
        return s1.age - s2.age;
    }
}

// Usage
List<Student> students = new ArrayList<>();
students.add(new Student("John", 20));
students.add(new Student("Jane", 18));

Collections.sort(students, new AgeComparator());

// Lambda expression (Java 8+)
Collections.sort(students, (s1, s2) -> s1.age - s2.age);
```

**Comparator vs Comparable:**

| Aspect | Comparator | Comparable |
|:---:|:---:|:---:|
| **Package** | java.util | java.lang |
| **Method** | compare(obj1, obj2) | compareTo(obj) |
| **Usage** | External sorting logic | Natural ordering |
| **Flexibility** | Multiple comparators | Single ordering |

---

### Q6: What makes a HashSet different from a TreeSet?

**A:**

| Aspect | HashSet | TreeSet |
|:---:|:---:|:---:|
| **Ordering** | No order | Sorted order |
| **Null Values** | Allows one null | No null (if natural ordering) |
| **Performance** | O(1) average | O(log n) |
| **Implementation** | Hash table | Red-black tree |
| **Requires** | hashCode(), equals() | Comparable or Comparator |

```java
// HashSet - no order
Set<String> hashSet = new HashSet<>();
hashSet.add("Apple");
hashSet.add("Banana");
hashSet.add("Apple");  // Duplicate ignored
// Order: unpredictable

// TreeSet - sorted order
Set<String> treeSet = new TreeSet<>();
treeSet.add("Apple");
treeSet.add("Banana");
// Order: Apple, Banana (sorted)
```

---

### Q7: What are the differences between HashMap and HashTable in Java?

**A:**

| Aspect | HashMap | Hashtable |
|:---:|:---:|:---:|
| **Synchronization** | Not synchronized | Synchronized |
| **Thread Safety** | No | Yes |
| **Null Keys/Values** | Allows one null key, multiple null values | No null |
| **Performance** | Faster | Slower (synchronization overhead) |
| **Legacy** | Modern (Java 1.2+) | Legacy (Java 1.0) |
| **Iterator** | Fail-fast | Fail-safe |

```java
// HashMap - not synchronized
Map<String, Integer> map = new HashMap<>();
map.put(null, 1);  // Allowed
map.put("key", null);  // Allowed

// Hashtable - synchronized
Hashtable<String, Integer> table = new Hashtable<>();
table.put(null, 1);  // NullPointerException
```

**Recommendation:** Use `ConcurrentHashMap` for thread-safe operations.

---

### Q8: What is the importance of reflection in Java?

**A:** Reflection allows inspection and modification of classes, methods, fields at runtime.

**Uses:**
1. **Framework Development:** Spring, Hibernate use reflection
2. **IDE Features:** Code completion, debugging
3. **Testing:** JUnit uses reflection
4. **Dynamic Loading:** Load classes dynamically

```java
import java.lang.reflect.*;

class MyClass {
    private String name;
    
    public void setName(String name) {
        this.name = name;
    }
}

// Reflection example
Class<?> clazz = MyClass.class;
Method[] methods = clazz.getDeclaredMethods();
Field[] fields = clazz.getDeclaredFields();

// Invoke method dynamically
Method method = clazz.getMethod("setName", String.class);
Object obj = clazz.newInstance();
method.invoke(obj, "John");
```

**Drawbacks:**
- Performance overhead
- Security restrictions
- Breaks encapsulation

---

### Q9: What are the different ways of threads usage?

**A:** Multiple ways to use threads:

**1. Extend Thread Class:**
```java
class MyThread extends Thread {
    public void run() {
        System.out.println("Thread running");
    }
}
MyThread t = new MyThread();
t.start();
```

**2. Implement Runnable:**
```java
class MyRunnable implements Runnable {
    public void run() {
        System.out.println("Runnable running");
    }
}
Thread t = new Thread(new MyRunnable());
t.start();
```

**3. Implement Callable (returns value):**
```java
class MyCallable implements Callable<String> {
    public String call() {
        return "Result";
    }
}
ExecutorService executor = Executors.newFixedThreadPool(1);
Future<String> future = executor.submit(new MyCallable());
String result = future.get();
```

**4. Lambda Expression:**
```java
Thread t = new Thread(() -> System.out.println("Lambda thread"));
t.start();
```

---

### Q10: What are the different types of Thread Priorities in Java?

**A:** Thread priorities range from 1 to 10:

| Priority | Constant | Value |
|:---:|:---:|:---:|
| **Minimum** | MIN_PRIORITY | 1 |
| **Normal** | NORM_PRIORITY | 5 (default) |
| **Maximum** | MAX_PRIORITY | 10 |

```java
Thread t1 = new Thread(() -> System.out.println("Low priority"));
t1.setPriority(Thread.MIN_PRIORITY);  // 1

Thread t2 = new Thread(() -> System.out.println("Normal priority"));
t2.setPriority(Thread.NORM_PRIORITY);  // 5 (default)

Thread t3 = new Thread(() -> System.out.println("High priority"));
t3.setPriority(Thread.MAX_PRIORITY);  // 10
```

**Note:** Priority is a hint to scheduler, not guaranteed.

---

### Q11: What is the difference between the program and the process?

**A:**

| Aspect | Program | Process |
|:---:|:---:|:---:|
| **Definition** | Static code/file | Running instance of program |
| **Memory** | Stored on disk | Loaded in memory |
| **Lifecycle** | Persistent | Created, runs, terminates |
| **Resources** | No resources | Has memory, CPU, file handles |

**Example:**
- **Program:** `MyApp.java` (source code)
- **Process:** Running instance of MyApp (has PID, memory space)

---

### Q12: What is the difference between the 'throw' and 'throws' keyword in Java?

**A:**

| Aspect | throw | throws |
|:---:|:---:|:---:|
| **Usage** | Throw exception explicitly | Declare exceptions method may throw |
| **Location** | Inside method body | Method signature |
| **Exception Type** | Single exception instance | One or more exception types |
| **Purpose** | Create and throw exception | Indicate possible exceptions |

```java
// throw - throw exception
void method() {
    if (condition) {
        throw new IllegalArgumentException("Invalid argument");
    }
}

// throws - declare exceptions
void method() throws IOException, SQLException {
    // Method may throw these exceptions
    // Caller must handle
}
```

---

### Q13: What are the differences between constructor and method of a class in Java?

**A:**

| Aspect | Constructor | Method |
|:---:|:---:|:---:|
| **Name** | Same as class name | Any valid name |
| **Return Type** | No return type | Has return type (void if none) |
| **Invocation** | Automatically on object creation | Explicitly called |
| **Inheritance** | Not inherited | Inherited |
| **Purpose** | Initialize object | Perform operation |

```java
class Example {
    // Constructor
    Example() {  // No return type, same name as class
        // Initialize object
    }
    
    // Method
    void doSomething() {  // Has return type, any name
        // Perform operation
    }
}
```

---

### Q14: Java works as "pass by value" or "pass by reference" phenomenon?

**A:** Java is **pass by value** always.

**For Primitives:**
- Value is copied
- Changes don't affect original

```java
void modify(int x) {
    x = 20;  // Doesn't affect original
}

int a = 10;
modify(a);
System.out.println(a);  // Still 10
```

**For Objects:**
- Reference value is copied
- Both references point to same object
- Object can be modified through reference

```java
void modify(MyObject obj) {
    obj.value = 20;  // Modifies object
    obj = new MyObject();  // Doesn't affect original reference
}

MyObject obj = new MyObject();
obj.value = 10;
modify(obj);
System.out.println(obj.value);  // 20 (object modified)
```

**Key Point:** Reference is passed by value, not object itself.

---

### Q15: What is the 'IS-A' relationship in OOPs Java?

**A:** IS-A relationship represents inheritance.

**Example:**
- Dog IS-A Animal
- Car IS-A Vehicle
- Manager IS-A Employee

```java
class Animal {
    void eat() {
        System.out.println("Eating");
    }
}

class Dog extends Animal {  // Dog IS-A Animal
    void bark() {
        System.out.println("Barking");
    }
}

// Usage
Dog dog = new Dog();
dog.eat();   // Inherited from Animal
dog.bark();  // Own method
```

**IS-A vs HAS-A:**
- **IS-A:** Inheritance (extends)
- **HAS-A:** Composition (object as member)

---

### Q16: Which among String or String Buffer should be preferred when there are lot of updates required to be done in the data?

**A:** **StringBuilder** (or StringBuffer for thread-safe) should be preferred.

**Reason:**
- **String:** Creates new object for each operation (inefficient)
- **StringBuilder/StringBuffer:** Modifies same object (efficient)

```java
// Inefficient - String
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i;  // Creates 1000 new objects
}

// Efficient - StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);  // Modifies same object
}
String result = sb.toString();
```

**Choose:**
- **StringBuilder:** Single-threaded (faster)
- **StringBuffer:** Multi-threaded (thread-safe)

---

### Q17: How to not allow serialization of attributes of a class in Java?

**A:** Use `transient` keyword.

```java
import java.io.*;

class User implements Serializable {
    String name;
    transient String password;  // Won't be serialized
    int age;
    
    User(String name, String password, int age) {
        this.name = name;
        this.password = password;
        this.age = age;
    }
}

// Serialization
User user = new User("John", "secret123", 25);
ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("user.ser"));
oos.writeObject(user);
// password field not serialized
```

**Use Cases:**
- Sensitive data (passwords)
- Derived/calculated fields
- Non-serializable objects

---

### Q18: What happens if the static modifier is not included in the main method signature in Java?

**A:** Program compiles but **cannot be executed** by JVM.

**Why:**
- JVM looks for `public static void main(String[] args)`
- Without `static`, JVM cannot call main without creating object
- Results in runtime error: `Error: Main method is not static`

```java
// Won't run
public void main(String[] args) {  // Missing static
    System.out.println("Hello");
}
// Error: Main method is not static in class Main

// Will run
public static void main(String[] args) {  // Has static
    System.out.println("Hello");
}
```

---

### Q19: Can we make the main() thread a daemon thread?

**A:** No, main thread cannot be made daemon thread.

**Why:**
- Main thread is created by JVM
- It's the initial thread
- JVM exits when main thread terminates

```java
public static void main(String[] args) {
    Thread.currentThread().setDaemon(true);  // IllegalThreadStateException
    // Cannot set main thread as daemon
}
```

**Note:** You can create daemon threads from main thread.

---

### Q20: What do you understand by Object Cloning and how do you achieve it in Java?

**A:** Object cloning creates a copy of an object.

**Ways to Clone:**

**1. Using clone() method:**
```java
class Student implements Cloneable {
    String name;
    int age;
    
    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();  // Shallow copy
    }
}

Student s1 = new Student("John", 20);
Student s2 = (Student) s1.clone();
```

**2. Using Copy Constructor:**
```java
class Student {
    String name;
    int age;
    
    Student(Student other) {  // Copy constructor
        this.name = other.name;
        this.age = other.age;
    }
}

Student s2 = new Student(s1);
```

**3. Using Serialization:**
```java
// Deep copy using serialization
ByteArrayOutputStream baos = new ByteArrayOutputStream();
ObjectOutputStream oos = new ObjectOutputStream(baos);
oos.writeObject(original);
ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
ObjectInputStream ois = new ObjectInputStream(bais);
Object cloned = ois.readObject();
```

---

### Q21: How does an exception propagate in the code?

**A:** Exception propagates up the call stack until caught.

**Propagation Flow:**
```
method3() throws Exception
    ↓
method2() calls method3() - doesn't handle
    ↓
method1() calls method2() - doesn't handle
    ↓
main() calls method1() - must handle or declare throws
```

```java
void method3() {
    throw new RuntimeException("Error");
}

void method2() {
    method3();  // Exception propagates up
}

void method1() {
    method2();  // Exception propagates up
}

public static void main(String[] args) {
    try {
        method1();  // Must handle here
    } catch (RuntimeException e) {
        System.out.println("Caught: " + e.getMessage());
    }
}
```

---

### Q22: How do exceptions affect the program if it doesn't handle them?

**A:** Unhandled exceptions cause program termination.

**Unchecked Exceptions:**
- Program crashes if not handled
- Stack trace printed
- JVM terminates

**Checked Exceptions:**
- Must be handled or declared in throws
- Compile error if not handled

```java
// Unchecked exception - crashes if not handled
public static void main(String[] args) {
    int[] arr = new int[5];
    arr[10] = 5;  // ArrayIndexOutOfBoundsException
    // Program terminates
}

// Checked exception - compile error if not handled
public static void main(String[] args) {
    FileReader file = new FileReader("file.txt");
    // Compile error: Unhandled exception type FileNotFoundException
}
```

---

### Q23: Is it mandatory for a catch block to be followed after a try block?

**A:** No, but you need either catch or finally.

**Valid Combinations:**
```java
// 1. try-catch
try {
    // code
} catch (Exception e) {
    // handle
}

// 2. try-finally
try {
    // code
} finally {
    // cleanup
}

// 3. try-catch-finally
try {
    // code
} catch (Exception e) {
    // handle
} finally {
    // cleanup
}

// 4. try-with-resources (Java 7+)
try (Resource r = new Resource()) {
    // code
}  // Resource automatically closed
```

**Invalid:**
```java
try {
    // code
}  // Compile error - need catch or finally
```

---

### Q24: Will the finally block get executed when the return statement is written at the end of try block and catch block?

**A:** Yes, finally block **always executes** before return.

```java
int method() {
    try {
        return 1;  // Finally executes first
    } catch (Exception e) {
        return 2;  // Finally executes first
    } finally {
        System.out.println("Finally");  // Always executes
        return 3;  // This return takes precedence
    }
}
// Returns 3 (finally return overrides)
```

**Exception:** `System.exit(0)` prevents finally execution.

---

### Q25: Can you call a constructor of a class inside another constructor?

**A:** Yes, using `this()` keyword.

```java
class Student {
    String name;
    int age;
    
    Student() {
        this("Unknown", 0);  // Call parameterized constructor
    }
    
    Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```

**Rules:**
- Must be first statement in constructor
- Can only call one constructor
- Cannot call instance methods before `this()`

---

### Q26: Contiguous memory locations are usually used for storing actual values in an array but not in ArrayList. Explain

**A:**

**Array:**
- Contiguous memory blocks
- Direct memory access
- Fixed size

**ArrayList:**
- Uses array internally
- But can grow dynamically
- When capacity exceeded, creates new larger array and copies elements

```java
// Array - contiguous memory
int[] arr = new int[5];
// Memory: [0][1][2][3][4] (contiguous)

// ArrayList - uses array internally
ArrayList<Integer> list = new ArrayList<>();
// Initially: array of size 10
// When full: creates new array of size 15, copies elements
// Old array becomes eligible for GC
```

**Key Point:** ArrayList uses arrays internally, but manages growth dynamically.

---

### Q27: Why does the java array index start with 0?

**A:** Historical and technical reasons:

**Reasons:**
1. **C Language Influence:** Java inherited from C
2. **Memory Addressing:** `arr[i]` = `base_address + i * element_size`
3. **Mathematical Convenience:** Easier calculations
4. **Convention:** Industry standard

**Mathematical Reason:**
```
If array starts at 0:
Address of arr[i] = base + i * size

If array starts at 1:
Address of arr[i] = base + (i-1) * size (more complex)
```

---

### Q28: Why is the remove method faster in the linked list than in an array?

**A:**

**LinkedList:**
- O(1) for removal (if have reference to node)
- Just update pointers
- No shifting needed

**Array/ArrayList:**
- O(n) for removal
- Must shift all elements after removed element
- More memory operations

```java
// LinkedList - O(1)
LinkedList<Integer> list = new LinkedList<>();
list.add(1);
list.add(2);
list.add(3);
list.remove(1);  // Just update pointers

// ArrayList - O(n)
ArrayList<Integer> list = new ArrayList<>();
list.add(1);
list.add(2);
list.add(3);
list.remove(1);  // Must shift elements 2,3 left
```

**Note:** If removing by index, LinkedList is O(n) to find node, then O(1) to remove.

---

### Q29: How many overloaded add() and addAll() methods are available in the List interface?

**A:**

**add() methods:**
1. `boolean add(E e)` - Add element to end
2. `void add(int index, E element)` - Add at specific index

**addAll() methods:**
1. `boolean addAll(Collection<? extends E> c)` - Add all from collection
2. `boolean addAll(int index, Collection<? extends E> c)` - Add all at specific index

```java
List<String> list = new ArrayList<>();

// add() methods
list.add("A");              // Add to end
list.add(0, "B");           // Add at index 0

// addAll() methods
List<String> other = Arrays.asList("C", "D");
list.addAll(other);          // Add all to end
list.addAll(1, other);       // Add all at index 1
```

---

### Q30: How does the size of ArrayList grow dynamically? And also state how it is implemented internally

**A:**

**Growth Mechanism:**
1. Initial capacity: 10 (default)
2. When full, creates new array: `newCapacity = oldCapacity + (oldCapacity >> 1)` (1.5x)
3. Copies elements to new array
4. Old array eligible for GC

**Internal Implementation:**
```java
// Simplified ArrayList internals
class ArrayList<E> {
    private Object[] elementData;  // Internal array
    private int size;             // Current size
    
    public boolean add(E e) {
        ensureCapacity(size + 1);  // Check if need to grow
        elementData[size++] = e;
        return true;
    }
    
    private void ensureCapacity(int minCapacity) {
        if (minCapacity > elementData.length) {
            int newCapacity = elementData.length + (elementData.length >> 1);
            elementData = Arrays.copyOf(elementData, newCapacity);
        }
    }
}
```

**Growth Formula:** `newCapacity = oldCapacity * 1.5` (approximately)

</div>

---

## 📚 Experienced Interview Questions

<div align="center">

### Q1: Although inheritance is a popular OOPs concept, it is less advantageous than composition. Explain

**A:** Composition is often preferred over inheritance.

**Problems with Inheritance:**
1. **Tight Coupling:** Child tightly coupled to parent
2. **Fragile Base Class:** Changes in parent affect children
3. **Multiple Inheritance:** Not supported (diamond problem)
4. **Rigid Hierarchy:** Hard to change inheritance structure

**Benefits of Composition:**
1. **Loose Coupling:** Can change implementation easily
2. **Flexibility:** Can compose multiple behaviors
3. **Testability:** Easier to test and mock
4. **Reusability:** Can reuse without inheritance

```java
// Inheritance - tight coupling
class Car extends Vehicle {
    // Car is tightly coupled to Vehicle
}

// Composition - loose coupling
class Car {
    private Engine engine;      // Has-A relationship
    private Wheels wheels;      // Can change implementation
    // More flexible
}
```

**Rule:** Favor composition over inheritance.

---

### Q2: What is the difference between '>>' and '>>>' operators in Java?

**A:**

| Operator | Name | Description |
|:---:|:---:|:---:|
| **>>** | Signed right shift | Preserves sign bit |
| **>>>** | Unsigned right shift | Fills with 0 |

```java
int a = -8;  // 11111111111111111111111111111000

// Signed right shift (>>)
int b = a >> 1;  // 11111111111111111111111111111100 (-4)
// Sign bit preserved

// Unsigned right shift (>>>)
int c = a >>> 1;  // 01111111111111111111111111111100 (2147483644)
// Fills with 0, no sign preservation
```

**Use Cases:**
- **>>:** Arithmetic operations, preserving sign
- **>>>:** Bit manipulation, treating as unsigned

---

### Q3: What are Composition and Aggregation? State the difference

**A:**

**Composition (Strong HAS-A):**
- Part cannot exist without whole
- Lifecycle dependent
- Example: House and Room

**Aggregation (Weak HAS-A):**
- Part can exist independently
- Lifecycle independent
- Example: University and Student

```java
// Composition - Room cannot exist without House
class House {
    private Room room;  // Composition
    
    House() {
        this.room = new Room();  // Created with House
    }
}

// Aggregation - Student can exist without University
class University {
    private List<Student> students;  // Aggregation
    
    void addStudent(Student student) {
        students.add(student);  // Student exists independently
    }
}
```

**Key Difference:** Lifecycle dependency.

---

### Q4: How is the creation of a String using new() different from that of a literal?

**A:**

**String Literal:**
- Stored in string pool
- Reused if same value exists
- Same reference for same values

**String with new():**
- Creates new object in heap
- Not in string pool (unless interned)
- Different reference even for same value

```java
String s1 = "Hello";           // String pool
String s2 = "Hello";           // String pool (reused)
String s3 = new String("Hello");  // Heap (new object)
String s4 = new String("Hello");  // Heap (another new object)

s1 == s2;  // true (same reference)
s1 == s3;  // false (different references)
s3 == s4;  // false (different objects)
s1.equals(s3);  // true (same content)
```

**Memory:**
- **Literal:** String pool (permgen/metaspace)
- **new():** Heap memory

---

### Q5: How is the 'new' operator different from the 'newInstance()' operator in Java?

**A:**

| Aspect | new | newInstance() |
|:---:|:---:|:---:|
| **Type** | Operator | Method |
| **Compile-time** | Known at compile time | Runtime (reflection) |
| **Performance** | Faster | Slower |
| **Exception** | No exception | Can throw exceptions |

```java
// new - compile-time
MyClass obj = new MyClass();

// newInstance() - runtime (reflection)
Class<?> clazz = Class.forName("MyClass");
MyClass obj = (MyClass) clazz.newInstance();
// Can throw InstantiationException, IllegalAccessException
```

**Use Cases:**
- **new:** Normal object creation
- **newInstance():** Dynamic class loading, frameworks

---

### Q6: Is exceeding the memory limit possible in a program despite having a garbage collector?

**A:** Yes, several scenarios:

**Causes:**
1. **Memory Leaks:** Objects referenced but not used
2. **Large Objects:** Objects larger than available memory
3. **GC Overhead:** Too much time spent in GC
4. **Heap Size:** JVM heap size limits

```java
// Memory leak example
List<Object> list = new ArrayList<>();
while (true) {
    list.add(new Object());  // Objects never eligible for GC
    // OutOfMemoryError eventually
}
```

**Solutions:**
- Increase heap size: `-Xmx2g`
- Fix memory leaks
- Optimize object creation
- Use object pooling

---

### Q7: What are the differences between fail-fast and fail-safe iterators?

**A:**

| Aspect | Fail-Fast | Fail-Safe |
|:---:|:---:|:---:|
| **Concurrent Modification** | Throws ConcurrentModificationException | Doesn't throw |
| **Collection** | Original collection | Copy of collection |
| **Performance** | Faster | Slower (creates copy) |
| **Examples** | ArrayList, HashMap | CopyOnWriteArrayList, ConcurrentHashMap |

```java
// Fail-fast iterator
List<String> list = new ArrayList<>();
list.add("A");
Iterator<String> it = list.iterator();
list.add("B");  // Modifies collection
it.next();      // ConcurrentModificationException

// Fail-safe iterator
List<String> list = new CopyOnWriteArrayList<>();
list.add("A");
Iterator<String> it = list.iterator();
list.add("B");  // Modifies collection
it.next();      // No exception (works on copy)
```

---

### Q8: What is the difference between the Enumeration and Iterator interface?

**A:**

| Aspect | Enumeration | Iterator |
|:---:|:---:|:---:|
| **Legacy** | Old (Java 1.0) | Modern (Java 1.2) |
| **Remove** | Cannot remove elements | Can remove elements |
| **Method Names** | hasMoreElements(), nextElement() | hasNext(), next() |
| **Use Case** | Legacy code | Modern code |

```java
// Enumeration (legacy)
Vector<String> vector = new Vector<>();
Enumeration<String> e = vector.elements();
while (e.hasMoreElements()) {
    String element = e.nextElement();
    // Cannot remove
}

// Iterator (modern)
List<String> list = new ArrayList<>();
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    String element = it.next();
    it.remove();  // Can remove
}
```

**Recommendation:** Use Iterator for new code.

---

### Q9: What is the difference between the '>>' and '>>>' operators in Java?

**A:** (Already covered above)

---

### Q10: What is the difference between a process and a thread?

**A:** (Already covered in concurrency section)

---

### Q11: What is the difference between the 'throw' and 'throws' keyword in Java?

**A:** (Already covered above)

---

### Q12: What is the difference between HashMap and ConcurrentHashMap?

**A:**

| Aspect | HashMap | ConcurrentHashMap |
|:---:|:---:|:---:|
| **Thread Safety** | No | Yes |
| **Null Keys/Values** | Allows one null key | No null |
| **Locking** | No locking | Segment-level locking (Java 7) / Node-level (Java 8+) |
| **Performance** | Faster (single-threaded) | Slower but better than Hashtable |
| **Iterator** | Fail-fast | Weakly consistent |

```java
// HashMap - not thread-safe
Map<String, Integer> map = new HashMap<>();
// Not safe for concurrent access

// ConcurrentHashMap - thread-safe
Map<String, Integer> concurrentMap = new ConcurrentHashMap<>();
// Safe for concurrent access
// Better performance than Hashtable
```

**Java 8+ Improvements:**
- Node-level locking instead of segment-level
- Better concurrency
- Improved performance

---

### Q13: What is the difference between Serializable and Externalizable interface?

**A:**

| Aspect | Serializable | Externalizable |
|:---:|:---:|:---:|
| **Control** | Automatic serialization | Manual control |
| **Methods** | No methods to implement | readExternal(), writeExternal() |
| **Performance** | Slower | Faster (more control) |
| **Use Case** | Simple serialization | Custom serialization logic |

```java
// Serializable - automatic
class Student implements Serializable {
    String name;
    int age;
    // Serialization handled automatically
}

// Externalizable - manual control
class Student implements Externalizable {
    String name;
    int age;
    
    @Override
    public void writeExternal(ObjectOutput out) throws IOException {
        out.writeUTF(name);
        out.writeInt(age);
    }
    
    @Override
    public void readExternal(ObjectInput in) throws IOException {
        name = in.readUTF();
        age = in.readInt();
    }
}
```

---

### Q14: What is the difference between Collection and Collections in Java?

**A:**

| Aspect | Collection | Collections |
|:---:|:---:|:---:|
| **Type** | Interface | Utility class |
| **Purpose** | Root interface for collections | Provides utility methods |
| **Methods** | add(), remove(), size() | sort(), reverse(), max(), min() |

```java
// Collection - interface
Collection<String> collection = new ArrayList<>();
collection.add("A");

// Collections - utility class
List<String> list = new ArrayList<>();
Collections.sort(list);        // Static utility method
Collections.reverse(list);
String max = Collections.max(list);
```

---

### Q15: What is the difference between Comparable and Comparator?

**A:** (Already covered above)

---

### Q16: What is the difference between fail-fast and fail-safe iterators?

**A:** (Already covered above)

---

### Q17: What is the difference between Iterator and ListIterator?

**A:**

| Aspect | Iterator | ListIterator |
|:---:|:---:|:---:|
| **Direction** | Forward only | Bidirectional |
| **Collection** | Any Collection | List only |
| **Methods** | hasNext(), next(), remove() | hasNext(), next(), hasPrevious(), previous(), add(), set() |

```java
List<String> list = new ArrayList<>();
list.add("A");
list.add("B");
list.add("C");

// Iterator - forward only
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    System.out.println(it.next());
}

// ListIterator - bidirectional
ListIterator<String> lit = list.listIterator();
while (lit.hasNext()) {
    System.out.println(lit.next());
}
while (lit.hasPrevious()) {
    System.out.println(lit.previous());
}
lit.add("D");  // Can add
lit.set("E");  // Can set
```

---

### Q18: What is the difference between HashMap and LinkedHashMap?

**A:**

| Aspect | HashMap | LinkedHashMap |
|:---:|:---:|:---:|
| **Ordering** | No order | Insertion order (or access order) |
| **Performance** | Faster | Slightly slower |
| **Implementation** | Hash table | Hash table + doubly-linked list |
| **Use Case** | Fast access, no order needed | Need insertion/access order |

```java
// HashMap - no order
Map<String, Integer> map = new HashMap<>();
map.put("C", 3);
map.put("A", 1);
map.put("B", 2);
// Order: unpredictable

// LinkedHashMap - insertion order
Map<String, Integer> linkedMap = new LinkedHashMap<>();
linkedMap.put("C", 3);
linkedMap.put("A", 1);
linkedMap.put("B", 2);
// Order: C, A, B (insertion order)
```

---

### Q19: What is the difference between Set and List in Java?

**A:**

| Aspect | Set | List |
|:---:|:---:|:---:|
| **Duplicates** | No duplicates | Allows duplicates |
| **Ordering** | No order (HashSet) or sorted (TreeSet) | Maintains insertion order |
| **Access** | No index-based access | Index-based access |
| **Implementation** | HashSet, TreeSet, LinkedHashSet | ArrayList, LinkedList, Vector |

```java
// Set - no duplicates
Set<String> set = new HashSet<>();
set.add("A");
set.add("A");  // Ignored
// Size: 1

// List - allows duplicates
List<String> list = new ArrayList<>();
list.add("A");
list.add("A");  // Added
// Size: 2
list.get(0);    // Index-based access
```

---

### Q20: What is the difference between ArrayList and Vector?

**A:**

| Aspect | ArrayList | Vector |
|:---:|:---:|:---:|
| **Synchronization** | Not synchronized | Synchronized |
| **Thread Safety** | No | Yes |
| **Performance** | Faster | Slower |
| **Growth** | 1.5x | 2x |
| **Legacy** | Modern (Java 1.2) | Legacy (Java 1.0) |

```java
// ArrayList - not synchronized
List<String> list = new ArrayList<>();
// Faster, not thread-safe

// Vector - synchronized
Vector<String> vector = new Vector<>();
// Slower, thread-safe

// Recommendation: Use Collections.synchronizedList() or CopyOnWriteArrayList
```

---

### Q21: What is the difference between checked and unchecked exceptions?

**A:** (Already covered above)

---

### Q22: What is the difference between error and exception?

**A:**

| Aspect | Error | Exception |
|:---:|:---:|:---:|
| **Type** | Unchecked | Checked or Unchecked |
| **Recovery** | Usually cannot recover | Can be handled |
| **Examples** | OutOfMemoryError, StackOverflowError | IOException, NullPointerException |
| **Handling** | Should not catch | Should catch |

```java
// Error - usually fatal
try {
    // Code causing OutOfMemoryError
} catch (Error e) {
    // Usually cannot recover
}

// Exception - can be handled
try {
    // Code causing IOException
} catch (Exception e) {
    // Can handle and recover
}
```

---

### Q23: What is the difference between wait() and notify() methods?

**A:**

| Aspect | wait() | notify() |
|:---:|:---:|:---:|
| **Purpose** | Releases lock and waits | Wakes up waiting thread |
| **Lock** | Must own object's monitor | Must own object's monitor |
| **Usage** | Called on object | Called on object |
| **Thread State** | WAITING | Wakes up WAITING thread |

```java
class SharedResource {
    private boolean flag = false;
    
    public synchronized void waitForFlag() throws InterruptedException {
        while (!flag) {
            wait();  // Releases lock, waits
        }
    }
    
    public synchronized void setFlag() {
        flag = true;
        notify();  // Wakes up one waiting thread
        // notifyAll() - wakes up all waiting threads
    }
}
```

**Important:** Must be called within synchronized block.

---

### Q24: What is the difference between sleep() and wait() methods?

**A:** (Already covered above)

---

### Q25: What is the difference between notify() and notifyAll()?

**A:**

| Aspect | notify() | notifyAll() |
|:---:|:---:|:---:|
| **Wakes Up** | One waiting thread | All waiting threads |
| **Selection** | JVM chooses | All threads compete |
| **Use Case** | When only one thread can proceed | When multiple threads can proceed |

```java
synchronized (obj) {
    obj.notify();      // Wakes up one thread
    obj.notifyAll();   // Wakes up all threads
}
```

**Recommendation:** Use `notifyAll()` unless you're sure only one thread should proceed.

---

### Q26: What is the difference between yield() and sleep() methods?

**A:**

| Aspect | yield() | sleep() |
|:---:|:---:|:---:|
| **Purpose** | Hints scheduler to give CPU to other threads | Sleeps for specified time |
| **Guarantee** | No guarantee | Guaranteed sleep time |
| **State** | RUNNABLE | TIMED_WAITING |
| **Interruption** | Cannot be interrupted | Can be interrupted |

```java
// yield() - hint to scheduler
Thread.yield();  // May or may not pause

// sleep() - guaranteed pause
Thread.sleep(1000);  // Sleeps for 1 second
```

---

### Q27: What is the difference between start() and run() methods?

**A:**

| Aspect | start() | run() |
|:---:|:---:|:---:|
| **Creates Thread** | Yes, new thread | No, runs in current thread |
| **Call** | Once per thread | Can call multiple times |
| **Execution** | Asynchronous | Synchronous |

```java
Thread t = new Thread(() -> System.out.println("Running"));

t.start();  // Creates new thread, asynchronous
// Output: "Running" (in new thread)

t.run();    // Runs in current thread, synchronous
// Output: "Running" (in current thread)
```

**Important:** Always use `start()` to create new thread.

---

### Q28: What is the difference between synchronized method and synchronized block?

**A:**

| Aspect | Synchronized Method | Synchronized Block |
|:---:|:---:|:---:|
| **Scope** | Entire method | Specific block |
| **Lock** | Object lock (instance) or class lock (static) | Can specify lock object |
| **Performance** | Slower (locks entire method) | Faster (locks only block) |
| **Flexibility** | Less flexible | More flexible |

```java
class Example {
    // Synchronized method
    public synchronized void method1() {
        // Entire method synchronized
    }
    
    // Synchronized block
    public void method2() {
        // Non-critical code
        synchronized(this) {
            // Only this block synchronized
        }
        // Non-critical code
    }
    
    // Synchronized block with different lock
    private final Object lock = new Object();
    public void method3() {
        synchronized(lock) {
            // Synchronized on specific object
        }
    }
}
```

**Best Practice:** Use synchronized blocks for better performance.

---

### Q29: What is the difference between ConcurrentHashMap and Hashtable?

**A:** (Similar to HashMap vs Hashtable, but ConcurrentHashMap is better)

| Aspect | ConcurrentHashMap | Hashtable |
|:---:|:---:|:---:|
| **Locking** | Segment-level (Java 7) / Node-level (Java 8+) | Entire map |
| **Performance** | Better (allows concurrent reads) | Slower (locks entire map) |
| **Null Values** | No null | No null |
| **Iterator** | Weakly consistent | Fail-safe |

**Recommendation:** Use ConcurrentHashMap for thread-safe operations.

---

### Q30: What is the difference between Runnable and Callable interface?

**A:**

| Aspect | Runnable | Callable |
|:---:|:---:|:---:|
| **Return Value** | void | Returns value |
| **Exception** | Cannot throw checked exceptions | Can throw checked exceptions |
| **Method** | run() | call() |
| **Usage** | Thread, ExecutorService | ExecutorService only |

```java
// Runnable - no return value
Runnable r = () -> {
    System.out.println("Running");
    // Cannot return value
};

// Callable - returns value
Callable<String> c = () -> {
    System.out.println("Running");
    return "Result";  // Returns value
};

// Usage with ExecutorService
ExecutorService executor = Executors.newFixedThreadPool(1);
Future<String> future = executor.submit(c);
String result = future.get();  // Get result
```

</div>

---

## 🎯 Advanced Java Concepts

<div align="center">

### JVM Architecture Deep Dive

**Q: Explain JVM architecture in detail.**

**A:** 

**Components:**

1. **Class Loader Subsystem:**
   - Loading: Loads .class files
   - Linking: Verification, preparation, resolution
   - Initialization: Static initializers

2. **Runtime Data Areas:**
   - **Method Area:** Class metadata, static variables
   - **Heap:** Object storage (Young + Old generation)
   - **Stack:** Per-thread stack (local variables, method calls)
   - **PC Register:** Current instruction pointer
   - **Native Method Stack:** Native code execution

3. **Execution Engine:**
   - **Interpreter:** Interprets bytecode
   - **JIT Compiler:** Compiles hot code to native
   - **Garbage Collector:** Manages heap memory

4. **Native Method Interface (JNI):**
   - Interface to native libraries

---

### Memory Model

**Q: Explain Java Memory Model (JMM).**

**A:** JMM defines how threads interact through memory.

**Key Concepts:**
- **Happens-Before:** Ordering guarantees
- **Visibility:** Changes visible to other threads
- **Atomicity:** Operations are atomic

**Volatile:**
- Ensures visibility
- Prevents reordering
- Not atomic for compound operations

**Synchronized:**
- Ensures visibility and atomicity
- Establishes happens-before relationship

</div>

---

## 💡 Best Practices & Patterns

<div align="center">

### Design Patterns

**Singleton Pattern:**
```java
// Thread-safe singleton
class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

**Factory Pattern:**
```java
interface Animal {
    void makeSound();
}

class Dog implements Animal {
    public void makeSound() { System.out.println("Bark"); }
}

class AnimalFactory {
    public static Animal createAnimal(String type) {
        if ("dog".equals(type)) return new Dog();
        // ...
        return null;
    }
}
```

</div>

---

## 🎓 Complete Interview Question Bank

<div align="center">

### Quick Reference: Common Questions

| Category | Questions |
|:---:|:---:|
| **OOP** | Abstract class vs Interface, Polymorphism, Encapsulation |
| **Memory** | Heap vs Stack, GC, Memory leaks |
| **Concurrency** | Threads, Synchronization, Deadlock, Volatile |
| **Collections** | HashMap internals, ArrayList vs LinkedList, Fail-fast |
| **Exceptions** | Checked vs Unchecked, try-catch-finally |
| **Strings** | Immutability, String pool, StringBuilder vs StringBuffer |
| **JVM** | Architecture, ClassLoader, Bytecode |

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Java Philosophy** | Write once, run anywhere |
| **OOP** | Encapsulation, inheritance, polymorphism, abstraction |
| **Memory** | Heap (GC), Stack (automatic), String pool |
| **Concurrency** | Threads, synchronization, concurrent collections |
| **Collections** | List, Set, Map - choose based on use case |
| **Strings** | Immutable, use StringBuilder for concatenation |
| **Exceptions** | Checked (compile-time), Unchecked (runtime) |

**💡 Remember:** Master these concepts for expert-level Java knowledge. Practice coding, understand JVM internals, and know when to use which collection or concurrency mechanism.

</div>

---

## 📚 Additional Resources

<div align="center">

### Recommended Reading

- **Effective Java** by Joshua Bloch
- **Java: The Complete Reference** by Herbert Schildt
- **Java Concurrency in Practice** by Brian Goetz

### Practice Platforms

- [InterviewBit Java Questions](https://www.interviewbit.com/java-interview-questions/)
- LeetCode
- HackerRank

</div>

---

<div align="center">

**Master Java for enterprise development! 🚀**

*Comprehensive Java guide with exhaustive Q&A covering fundamentals to expert-level concepts.*

</div>
