# Longest Path With Different Adjacent Characters

## Problem Statement

You are given a **tree** (i.e. a connected, undirected graph that has no cycles) rooted at node `0` consisting of `n` nodes numbered from `0` to `n - 1`. The tree is represented by a **0-indexed** array `parent` of size `n`, where `parent[i]` is the parent of node `i`. Since node `0` is the root, `parent[0] == -1`.

You are also given a string `s` of length `n`, where `s[i]` is the character assigned to node `i`.

Return *the length of the **longest path** in the tree such that no pair of **adjacent** nodes on the path have the same character assigned to them*.

**Example 1:**

```
Input: parent = [-1,0,0,1,1,2], s = "abacbe"
Output: 3
Explanation: The longest path where each two adjacent nodes have different characters is the path: 0 -> 1 -> 3.
The length of this path is 3, so 3 is returned.
It can be proven that there is no longer path that satisfies the condition.
```

**Example 2:**

```
Input: parent = [-1,0,0,0], s = "aabc"
Output: 3
Explanation: The longest path where each two adjacent nodes have different characters is the path: 2 -> 0 -> 3.
The length of this path is 3, so 3 is returned.
```

**LeetCode Link:** https://leetcode.com/problems/longest-path-with-different-adjacent-characters/

## Constraints

- `n == parent.length == s.length`
- `1 <= n <= 10^5`
- `0 <= parent[i] <= n - 1` for all `i >= 1`
- `parent[0] == -1`
- `parent` represents a valid tree
- `s` consists of only lowercase English letters

## Intuition

This is a **tree diameter** problem with a constraint: adjacent nodes must have different characters. We need to find the longest path in the tree where no two adjacent nodes share the same character.

The path can go:
- **Downward** from a node through its children
- **Through a node** connecting two subtrees

We use **DFS** to:
1. For each node, find the longest downward paths from its children (with different characters)
2. Combine the two longest paths through the node
3. Track the global maximum

## Approach

**DFS Algorithm:**

1. **Build tree**: Convert parent array to adjacency list
2. **DFS from root**: For each node:
   - Get longest paths from all children (with different characters)
   - Keep track of longest and second longest paths
   - Update global answer: `longest + secondLongest + 1`
   - Return longest downward path including current node

### Algorithm

1. Build tree structure from parent array
2. Initialize `answer = 1` (at least one node)
3. DFS function:
   - For each child:
     - Skip if child has same character as current node
     - Get longest path from child subtree
     - Update longest and secondLongest
   - Update global answer = max(answer, longest + secondLongest + 1)
   - Return longest + 1 (longest downward path)
4. Return answer

### Implementation Notes

- **Runtime:** 92 ms
- **Memory:** 163.9 MB
- **Tags:** Array, String, Tree, Depth-First Search, Graph, Topological Sort
- **Difficulty:** Hard

**Key Points:**
- Path can go through a node (combining two subtrees)
- Only consider children with different characters
- Track longest and second longest paths
- Global answer tracks best path found so far

## Complexity Analysis

- **Time Complexity:** O(n) - Visit each node once
- **Space Complexity:** O(n) - Tree structure and recursion stack

## Edge Cases

- **Single node**: Answer is 1
- **All nodes same character**: Answer is 1 (can't have adjacent nodes)
- **Linear tree**: Path follows the chain
- **Star tree**: Path goes through center node

## Solution Code

See the solution implementation in: [`longest-path-with-different-adjacent-characters.java`](./longest-path-with-different-adjacent-characters.java)

## Test Cases

```java
// Test Case 1: Example from problem
parent = [-1,0,0,1,1,2], s = "abacbe"
Expected: 3

// Test Case 2: All different characters
parent = [-1,0,1,2], s = "abcd"
Expected: 4

// Test Case 3: All same characters
parent = [-1,0,0,0], s = "aaaa"
Expected: 1
```
