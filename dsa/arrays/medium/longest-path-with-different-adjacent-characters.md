# Longest Path With Different Adjacent Characters

## Problem Statement

<!-- Problem description from LeetCode -->

**LeetCode Link:** https://leetcode.com/problems/longest-path-with-different-adjacent-characters/

## Constraints

<!-- Add constraints from LeetCode problem page -->

## Intuition

Use depth-first search to traverse the tree/graph and solve the problem recursively.

## Approach

Recursively explore all paths, maintaining state as we traverse.

### Algorithm
1. Base case: handle null/terminal nodes
2. Recursive case: process current node
3. Recursively solve subproblems
4. Combine results

### Implementation Notes
- **Runtime:** 92 ms
- **Memory:** 163.9 MB
- **Tags:** N/A
- **Difficulty:** Medium

## Complexity Analysis

- **Time Complexity:** O(n) where n is number of nodes
- **Space Complexity:** O(h) where h is height (recursion stack)

## Edge Cases

- Empty tree
- Single node
- Skewed tree (left or right only)

## Solution Code

See the solution implementation in: [`longest-path-with-different-adjacent-characters.java`](./longest-path-with-different-adjacent-characters.java)

## Test Cases

```java

```
