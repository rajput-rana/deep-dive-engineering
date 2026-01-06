# ⚛️ React.js - Expert Guide

<div align="center">

**Master React: components, hooks, state management, and modern UI development**

[![React](https://img.shields.io/badge/React-UI%20Library-blue?style=for-the-badge)](./)
[![Components](https://img.shields.io/badge/Components-Reusable-green?style=for-the-badge)](./)
[![Hooks](https://img.shields.io/badge/Hooks-Functional-orange?style=for-the-badge)](./)

*Comprehensive React guide with Q&A for expert-level understanding*

</div>

---

## 🎯 React Fundamentals

<div align="center">

### What is React?

**React is a JavaScript library for building user interfaces using component-based architecture.**

### Key Concepts

| Concept | Description |
|:---:|:---:|
| **🧩 Components** | Reusable UI pieces |
| **⚡ Virtual DOM** | Efficient DOM updates |
| **🔄 State** | Component data |
| **📥 Props** | Component inputs |
| **🪝 Hooks** | Functional component features |
| **🎯 JSX** | JavaScript XML syntax |

**Mental Model:** Think of React like LEGO blocks - you build small components (blocks) and combine them to create complex UIs (structures).

</div>

---

## 🧩 Components

<div align="center">

### Component Types

**Q: What is the difference between functional and class components?**

**A:**

**Functional Component (Modern):**
```javascript
function Welcome(props) {
    return <h1>Hello, {props.name}!</h1>;
}

// Arrow function
const Welcome = (props) => {
    return <h1>Hello, {props.name}!</h1>;
};
```

**Class Component (Legacy):**
```javascript
class Welcome extends React.Component {
    render() {
        return <h1>Hello, {this.props.name}!</h1>;
    }
}
```

**💡 Prefer functional components with hooks (modern approach).**

---

### Props

**Q: What are props and how do they work?**

**A:** Props (properties) are inputs passed to components.

```javascript
// Parent component
function App() {
    return <UserCard name="John" age={25} email="john@example.com" />;
}

// Child component
function UserCard({ name, age, email }) {
    return (
        <div>
            <h2>{name}</h2>
            <p>Age: {age}</p>
            <p>Email: {email}</p>
        </div>
    );
}
```

**Key Points:**
- Props are read-only (immutable)
- Pass data from parent to child
- Use destructuring for cleaner code

</div>

---

## 🔄 State Management

<div align="center">

### useState Hook

**Q: How does useState work?**

**A:** useState manages component state in functional components.

```javascript
import { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                Increment
            </button>
            <button onClick={() => setCount(count - 1)}>
                Decrement
            </button>
        </div>
    );
}
```

**Q: What is the difference between setState and useState?**

**A:**
- **Class components:** `this.setState({ count: count + 1 })` (async, batches updates)
- **Functional components:** `setCount(count + 1)` (can be async, batches updates)

**Functional Update:**
```javascript
// Use functional update for state based on previous state
setCount(prevCount => prevCount + 1);
```

---

### useEffect Hook

**Q: What is useEffect and when to use it?**

**A:** useEffect handles side effects (API calls, subscriptions, DOM manipulation).

```javascript
import { useState, useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        // Side effect: fetch user data
        fetch(`/api/users/${userId}`)
            .then(res => res.json())
            .then(data => setUser(data));
    }, [userId]); // Dependency array
    
    if (!user) return <div>Loading...</div>;
    
    return <div>{user.name}</div>;
}
```

**Dependency Array:**
- **Empty []:** Run once on mount
- **[userId]:** Run when userId changes
- **No array:** Run on every render (avoid!)

**Cleanup:**
```javascript
useEffect(() => {
    const subscription = subscribe();
    
    return () => {
        // Cleanup function
        subscription.unsubscribe();
    };
}, []);
```

</div>

---

## 🪝 Advanced Hooks

<div align="center">

### useCallback & useMemo

**Q: What is the difference between useCallback and useMemo?**

**A:**

**useCallback:** Memoizes functions
```javascript
const memoizedCallback = useCallback(() => {
    doSomething(a, b);
}, [a, b]); // Only recreate if a or b changes
```

**useMemo:** Memoizes values
```javascript
const expensiveValue = useMemo(() => {
    return computeExpensiveValue(a, b);
}, [a, b]); // Only recompute if a or b changes
```

**When to use:**
- **useCallback:** Pass functions to child components
- **useMemo:** Expensive calculations

---

### useContext

**Q: How does useContext work?**

**A:** useContext provides access to context values.

```javascript
// Create context
const ThemeContext = createContext('light');

// Provider
function App() {
    const [theme, setTheme] = useState('dark');
    
    return (
        <ThemeContext.Provider value={theme}>
            <Toolbar />
        </ThemeContext.Provider>
    );
}

// Consumer
function Toolbar() {
    const theme = useContext(ThemeContext);
    return <button className={theme}>Button</button>;
}
```

---

### useRef

**Q: What is useRef and when to use it?**

**A:** useRef persists values across renders without causing re-renders.

```javascript
function TextInput() {
    const inputRef = useRef(null);
    
    const focusInput = () => {
        inputRef.current.focus();
    };
    
    return (
        <>
            <input ref={inputRef} type="text" />
            <button onClick={focusInput}>Focus Input</button>
        </>
    );
}
```

**Use Cases:**
- DOM references
- Storing previous values
- Timer IDs

</div>

---

## 🎯 Component Patterns

<div align="center">

### Higher-Order Components (HOC)

**Q: What is a Higher-Order Component?**

**A:** HOC is a function that takes a component and returns a new component.

```javascript
function withLoading(Component) {
    return function LoadingComponent({ isLoading, ...props }) {
        if (isLoading) {
            return <div>Loading...</div>;
        }
        return <Component {...props} />;
    };
}

const UserListWithLoading = withLoading(UserList);
```

---

### Render Props

**Q: What is the render props pattern?**

**A:** Component receives a function as a prop that returns JSX.

```javascript
function Mouse({ render }) {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    
    useEffect(() => {
        const handleMouseMove = (e) => {
            setPosition({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);
    
    return render(position);
}

<Mouse render={({ x, y }) => <p>Mouse at {x}, {y}</p>} />
```

---

### Custom Hooks

**Q: How to create custom hooks?**

**A:** Custom hooks extract component logic into reusable functions.

```javascript
function useFetch(url) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        fetch(url)
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err);
                setLoading(false);
            });
    }, [url]);
    
    return { data, loading, error };
}

// Usage
function UserProfile({ userId }) {
    const { data: user, loading, error } = useFetch(`/api/users/${userId}`);
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    return <div>{user.name}</div>;
}
```

</div>

---

## ⚡ Performance Optimization

<div align="center">

### React.memo

**Q: What is React.memo?**

**A:** React.memo prevents unnecessary re-renders.

```javascript
const UserCard = React.memo(function UserCard({ name, email }) {
    return (
        <div>
            <h3>{name}</h3>
            <p>{email}</p>
        </div>
    );
});

// Only re-renders if props change
```

---

### Code Splitting

**Q: How to implement code splitting?**

**A:** Use React.lazy and Suspense.

```javascript
import { lazy, Suspense } from 'react';

const LazyComponent = lazy(() => import('./HeavyComponent'));

function App() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <LazyComponent />
        </Suspense>
    );
}
```

</div>

---

## 🎓 Interview Questions

<div align="center">

### Hard Interview Questions

**Q: What is the Virtual DOM and how does it work?**

**A:** Virtual DOM is a JavaScript representation of the real DOM. React compares virtual DOM trees and updates only changed parts.

**Process:**
1. State changes
2. New Virtual DOM created
3. Diff algorithm compares old vs new
4. Only changed nodes updated in real DOM

**Q: Explain React's reconciliation algorithm.**

**A:** Reconciliation is how React updates the DOM efficiently:
- **Keys:** Help identify which items changed
- **Diffing:** Compares tree structures
- **Batching:** Groups multiple updates

**Q: What is the difference between controlled and uncontrolled components?**

**A:**
- **Controlled:** React controls form data via state
- **Uncontrolled:** DOM handles form data via refs

```javascript
// Controlled
const [value, setValue] = useState('');
<input value={value} onChange={(e) => setValue(e.target.value)} />

// Uncontrolled
const inputRef = useRef();
<input ref={inputRef} defaultValue="initial" />
```

**Q: How does React handle events?**

**A:** React uses SyntheticEvent wrapper for cross-browser compatibility. Events are delegated to root.

</div>

---

## 💡 Key Takeaways

<div align="center">

| Concept | Key Point |
|:---:|:---:|
| **Components** | Reusable UI pieces |
| **Props** | Data passed to components |
| **State** | Component data (useState) |
| **Hooks** | Functional component features |
| **Virtual DOM** | Efficient updates |

**💡 Remember:** React is about components, state, and props. Master hooks, performance optimization, and patterns for expert-level React knowledge.

</div>

---

<div align="center">

**Master React for modern UI development! 🚀**

*From components to hooks - comprehensive React guide with Q&A for expert-level understanding.*

</div>

