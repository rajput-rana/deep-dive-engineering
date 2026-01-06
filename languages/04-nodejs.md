# 🟢 Node.js - Expert Guide

<div align="center">

**Master Node.js: event loop, async programming, and backend development**

[![Node.js](https://img.shields.io/badge/Node.js-Runtime-blue?style=for-the-badge)](./)
[![Event Loop](https://img.shields.io/badge/Event%20Loop-Async-green?style=for-the-badge)](./)
[![Backend](https://img.shields.io/badge/Backend-Server--Side-orange?style=for-the-badge)](./)

*Comprehensive Node.js guide with Q&A for expert-level understanding*

</div>

---

## 🎯 Node.js Fundamentals

<div align="center">

### What is Node.js?

**Node.js is a JavaScript runtime built on Chrome's V8 engine for server-side development.**

### Key Characteristics

| Characteristic | Description |
|:---:|:---:|
| **⚡ Event-Driven** | Non-blocking I/O |
| **🔄 Asynchronous** | Callbacks, promises, async/await |
| **📦 Single-Threaded** | Event loop handles concurrency |
| **🌐 JavaScript** | Same language frontend/backend |
| **📚 NPM** | Package manager |

**Mental Model:** Think of Node.js like a restaurant with one waiter (event loop) who takes orders (events) and delegates to kitchen (thread pool) while serving other tables, making it very efficient.

</div>

---

## 🔄 Event Loop

<div align="center">

### How Event Loop Works

**Q: Explain the Node.js event loop.**

**A:** Event loop is the core mechanism that enables Node.js's non-blocking I/O.

**Phases:**
1. **Timers:** Execute `setTimeout` and `setInterval` callbacks
2. **Pending Callbacks:** Execute I/O callbacks deferred to next loop
3. **Idle, Prepare:** Internal use
4. **Poll:** Fetch new I/O events, execute I/O callbacks
5. **Check:** Execute `setImmediate` callbacks
6. **Close Callbacks:** Execute close callbacks

**Example:**
```javascript
console.log('1');

setTimeout(() => console.log('2'), 0);

Promise.resolve().then(() => console.log('3'));

console.log('4');

// Output: 1, 4, 3, 2
```

**Execution Order:**
1. Synchronous code (1, 4)
2. Microtasks - Promises (3)
3. Macrotasks - Timers (2)

---

### Q&A: Event Loop

**Q: What is the difference between setImmediate and setTimeout?**

**A:**
- **setImmediate:** Executes in Check phase, after I/O callbacks
- **setTimeout(fn, 0):** Executes in Timers phase, minimum 1ms delay

```javascript
setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));

// Output can vary, but immediate usually runs first
```

**Q: What are microtasks and macrotasks?**

**A:**
- **Microtasks:** Promises, queueMicrotask, process.nextTick
- **Macrotasks:** setTimeout, setInterval, setImmediate, I/O

**Priority:** Microtasks execute before macrotasks

</div>

---

## ⚡ Asynchronous Programming

<div align="center">

### Callbacks

**Q: What are callbacks and callback hell?**

**A:** Callbacks are functions passed as arguments to be executed later.

**Callback Hell:**
```javascript
// Nested callbacks - hard to read
fs.readFile('file1.txt', (err, data1) => {
    if (err) throw err;
    fs.readFile('file2.txt', (err, data2) => {
        if (err) throw err;
        fs.writeFile('output.txt', data1 + data2, (err) => {
            if (err) throw err;
            console.log('Done');
        });
    });
});
```

---

### Promises

**Q: How do Promises solve callback hell?**

**A:** Promises provide cleaner async code.

```javascript
// With Promises
fs.promises.readFile('file1.txt')
    .then(data1 => fs.promises.readFile('file2.txt'))
    .then(data2 => fs.promises.writeFile('output.txt', data1 + data2))
    .then(() => console.log('Done'))
    .catch(err => console.error(err));
```

**Q: What is Promise.all vs Promise.allSettled?**

**A:**
- **Promise.all:** Fails fast if any promise rejects
- **Promise.allSettled:** Waits for all promises, returns all results

```javascript
// Promise.all - fails if any fails
Promise.all([promise1, promise2, promise3])
    .then(results => console.log('All succeeded'))
    .catch(err => console.error('One failed'));

// Promise.allSettled - waits for all
Promise.allSettled([promise1, promise2, promise3])
    .then(results => {
        // All results, including failures
        results.forEach(result => {
            if (result.status === 'fulfilled') {
                console.log(result.value);
            } else {
                console.error(result.reason);
            }
        });
    });
```

---

### Async/Await

**Q: What is async/await?**

**A:** Syntactic sugar for Promises, makes async code look synchronous.

```javascript
// With async/await
async function processFiles() {
    try {
        const data1 = await fs.promises.readFile('file1.txt');
        const data2 = await fs.promises.readFile('file2.txt');
        await fs.promises.writeFile('output.txt', data1 + data2);
        console.log('Done');
    } catch (err) {
        console.error(err);
    }
}
```

**Q: How to handle errors in async/await?**

**A:**
```javascript
// Try-catch
async function fetchData() {
    try {
        const data = await api.getData();
        return data;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Or catch on promise
fetchData().catch(error => console.error(error));
```

</div>

---

## 📦 Modules

<div align="center">

### Module System

**Q: What is the difference between CommonJS and ES Modules?**

**A:**

**CommonJS (require/module.exports):**
```javascript
// Export
module.exports = {
    add: (a, b) => a + b,
    subtract: (a, b) => a - b
};

// Import
const { add, subtract } = require('./math');
```

**ES Modules (import/export):**
```javascript
// Export
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;

// Import
import { add, subtract } from './math.js';
```

**Differences:**
- **CommonJS:** Synchronous, runtime resolution
- **ES Modules:** Asynchronous, static analysis, tree-shaking

**Q: What is module caching?**

**A:** Modules are cached after first require. Subsequent requires return cached version.

```javascript
// module.js
console.log('Module loaded');
module.exports = { data: 'test' };

// app.js
require('./module'); // Prints "Module loaded"
require('./module'); // No output (cached)
```

</div>

---

## 🌐 HTTP & Express

<div align="center">

### Building HTTP Servers

**Q: How to create an HTTP server in Node.js?**

**A:**

**Native HTTP:**
```javascript
const http = require('http');

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hello World');
});

server.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

**Express.js:**
```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.get('/users/:id', (req, res) => {
    const userId = req.params.id;
    res.json({ id: userId, name: 'John' });
});

app.post('/users', (req, res) => {
    const user = req.body;
    // Save user
    res.status(201).json(user);
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

---

### Middleware

**Q: What is middleware in Express?**

**A:** Middleware functions execute between request and response.

```javascript
// Custom middleware
const logger = (req, res, next) => {
    console.log(`${req.method} ${req.path}`);
    next(); // Pass to next middleware
};

app.use(logger);

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong' });
});
```

</div>

---

## 🗄️ Database Integration

<div align="center">

### Working with Databases

**Q: How to connect to databases in Node.js?**

**A:**

**MongoDB (Mongoose):**
```javascript
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/mydb');

const UserSchema = new mongoose.Schema({
    name: String,
    email: String
});

const User = mongoose.model('User', UserSchema);

// Create
const user = new User({ name: 'John', email: 'john@example.com' });
await user.save();

// Find
const users = await User.find();
```

**PostgreSQL (pg):**
```javascript
const { Pool } = require('pg');

const pool = new Pool({
    host: 'localhost',
    database: 'mydb',
    user: 'postgres',
    password: 'password'
});

const result = await pool.query('SELECT * FROM users WHERE id = $1', [userId]);
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Hard Interview Questions

**Q: Explain the difference between process.nextTick and setImmediate.**

**A:**
- **process.nextTick:** Executes before event loop phases (highest priority)
- **setImmediate:** Executes in Check phase

```javascript
process.nextTick(() => console.log('nextTick'));
setImmediate(() => console.log('immediate'));
console.log('sync');

// Output: sync, nextTick, immediate
```

**Q: What is the difference between spawn, exec, and fork?**

**A:**
- **spawn:** Streams data, non-blocking
- **exec:** Buffers output, blocking
- **fork:** Special spawn for Node.js processes

**Q: How does Node.js handle concurrency if it's single-threaded?**

**A:** 
- Event loop handles I/O operations asynchronously
- Thread pool (libuv) handles CPU-intensive tasks
- Worker threads for CPU-bound operations

**Q: What is the difference between require and import?**

**A:**
- **require:** CommonJS, synchronous, runtime
- **import:** ES Modules, asynchronous, compile-time

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Event Loop** | Non-blocking I/O mechanism |
| **Async Programming** | Callbacks → Promises → async/await |
| **Modules** | CommonJS vs ES Modules |
| **Single-Threaded** | Event loop + thread pool |
| **NPM** | Package management |

**💡 Remember:** Node.js excels at I/O-bound operations. Master the event loop, async patterns, and module system for expert-level Node.js knowledge.

</div>

---

<div align="center">

**Master Node.js for backend development! 🚀**

*From event loop to async programming - comprehensive Node.js guide with Q&A.*

</div>

