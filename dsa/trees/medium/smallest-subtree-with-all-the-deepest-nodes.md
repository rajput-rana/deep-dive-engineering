# Smallest Subtree with all the Deepest Nodes

## Problem Statement

Given the `root` of a binary tree, the depth of each node is the shortest distance to the root.

Return *the smallest subtree such that it contains **all** the deepest nodes in the original tree*.

A node is called **deepest** if it has the largest depth possible among any node in the entire tree.

The **subtree** of a node is a tree consisting of that node, plus the set of all descendants of that node.

**Example 1:**

```
Input: root = [3,5,1,6,2,0,8,null,null,7,4]
Output: [2,7,4]
Explanation: We return the node with value 2, colored in yellow in the diagram.
The nodes colored in blue are the deepest nodes of the tree.
Notice that nodes 5, 3 and 2 contain the deepest nodes in the tree but node 2 is the smallest subtree among them.
```

**Example 2:**

```
Input: root = [1]
Output: [1]
Explanation: The root is the deepest node in the tree.
```

**Example 3:**

```
Input: root = [0,1,3,null,2]
Output: [2]
Explanation: The deepest node in the tree is 2, the valid subtrees are the subtrees of nodes 2, 1 and 0 but the subtree of node 2 is the smallest.
```

**LeetCode Link:** https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/

## Constraints

- The number of nodes in the tree will be in the range `[1, 500]`
- `0 <= Node.val <= 500`
- The values of the nodes in the tree are **unique**

## Intuition

The problem requires finding the **lowest common ancestor (LCA)** of all deepest nodes. If all deepest nodes are in the same subtree, we need to go deeper. If they're in different subtrees, the current node is the answer.

We use **DFS** to:
1. Find the depth of deepest nodes
2. For each node, return the deepest node in its subtree and the depth
3. If both left and right subtrees have deepest nodes at the same depth, current node is the LCA
4. Otherwise, return the subtree that contains the deeper nodes

## Approach

We perform a **post-order DFS traversal**:

1. **Base case**: If node is null, return (null, depth 0)
2. **Recursive case**: 
   - Get deepest node and depth from left subtree
   - Get deepest node and depth from right subtree
   - **If left depth > right depth**: Deepest nodes are in left subtree, return left result
   - **If right depth > left depth**: Deepest nodes are in right subtree, return right result
   - **If depths are equal**: Current node is LCA of all deepest nodes, return current node
3. Return the node and its depth (max of left/right depth + 1)

### Algorithm

1. Define a Result class to hold (node, depth)
2. Perform DFS starting from root
3. For each node:
   - If null, return (null, 0)
   - Recursively get left and right results
   - Compare depths:
     - Left deeper → return left result with depth+1
     - Right deeper → return right result with depth+1
     - Equal depths → return (current node, depth+1)
4. Return the node from root's result

### Implementation Notes

- **Runtime:** 0 ms
- **Memory:** 43.7 MB
- **Tags:** Hash Table, Tree, Depth-First Search, Breadth-First Search, Binary Tree
- **Difficulty:** Medium

**Key Points:**
- Post-order traversal ensures we know depths of both subtrees before processing current node
- When depths are equal, current node is the LCA
- Result class encapsulates both the answer node and depth information

## Complexity Analysis

- **Time Complexity:** O(n) - Visit each node exactly once
- **Space Complexity:** O(h) - Recursion stack depth equals tree height (O(n) worst case for skewed tree)

## Edge Cases

- **Single node**: Root is the answer
- **Perfectly balanced tree**: All deepest nodes at same level
- **Skewed tree**: Deepest nodes form a path
- **All nodes at same depth**: Root is the answer

## Solution Code

See the solution implementation in: [`smallest-subtree-with-all-the-deepest-nodes.java`](./smallest-subtree-with-all-the-deepest-nodes.java)

## Test Cases

```java
// Test Case 1: Example from problem
root = [3,5,1,6,2,0,8,null,null,7,4]
Expected: [2,7,4]

// Test Case 2: Single node
root = [1]
Expected: [1]

// Test Case 3: All deepest nodes in one subtree
root = [0,1,3,null,2]
Expected: [2]

// Test Case 4: Perfectly balanced
root = [1,2,3,4,5,6,7]
Expected: [1,2,3,4,5,6,7] (root is LCA)
```
