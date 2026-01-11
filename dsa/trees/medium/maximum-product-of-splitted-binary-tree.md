# Maximum Product of Splitted Binary Tree

## Problem Statement

Given the `root` of a binary tree, split the binary tree into two subtrees by removing one edge such that the product of the sums of the subtrees is maximized.

Return *the maximum product of the sums of the two subtrees*. Since the answer may be too large, return it **modulo** `10^9 + 7`.

**Note:** You need to maximize the answer before taking the mod and not after taking it.

**Example 1:**

```
Input: root = [1,2,3,4,5,6]
Output: 110
Explanation: Remove the red edge and get 2 binary trees with sum 11 and 10. Their product is 110 (11*10)
```

**Example 2:**

```
Input: root = [1,null,2,3,4,null,null,5,6]
Output: 90
Explanation: Remove the red edge and get 2 binary trees with sum 15 and 6. Their product is 90 (15*6)
```

**LeetCode Link:** https://leetcode.com/problems/maximum-product-of-splitted-binary-tree/

## Constraints

- The number of nodes in the tree is in the range `[2, 5 * 10^4]`
- `1 <= Node.val <= 10^4`

## Intuition

To maximize the product of two subtree sums, we need to find the optimal edge to remove. The product `sum1 × sum2` is maximized when the two sums are as close as possible (given that `sum1 + sum2 = total`).

We use **two-pass DFS**:
1. First pass: Calculate total sum of all nodes
2. Second pass: For each node, calculate subtree sum and check if removing the edge above it gives a better product

## Approach

**Two-Pass Algorithm:**

1. **First Pass (computeTotalSum)**: Traverse tree to calculate total sum of all nodes
2. **Second Pass (computeSubtreeSum)**: 
   - For each node, calculate sum of its subtree
   - If we remove edge above this node, we get two parts:
     - Subtree sum: `subSum`
     - Remaining sum: `totalSum - subSum`
   - Product = `subSum × (totalSum - subSum)`
   - Track maximum product

### Algorithm

1. Initialize `totalSum = 0`, `maxProduct = 0`
2. First DFS: Calculate total sum of all nodes
3. Second DFS: For each node:
   - Calculate subtree sum (node + left subtree + right subtree)
   - Calculate product = subtreeSum × (totalSum - subtreeSum)
   - Update maxProduct
   - Return subtree sum to parent
4. Return maxProduct % MOD

### Implementation Notes

- **Runtime:** 5 ms
- **Memory:** 59.4 MB
- **Tags:** Tree, Depth-First Search, Binary Tree
- **Difficulty:** Medium

**Key Points:**
- Two-pass approach: first to get total, second to evaluate each split
- Use `long` to avoid integer overflow
- Modulo operation only at the end

## Complexity Analysis

- **Time Complexity:** O(n) - Two DFS traversals, each visits each node once
- **Space Complexity:** O(h) - Recursion stack depth equals tree height

## Edge Cases

- **Two nodes**: Remove the single edge
- **Skewed tree**: All nodes in one path
- **Perfectly balanced**: Multiple split options
- **Large values**: Need long to prevent overflow

## Solution Code

See the solution implementation in: [`maximum-product-of-splitted-binary-tree.java`](./maximum-product-of-splitted-binary-tree.java)

## Test Cases

```java
// Test Case 1: Example from problem
root = [1,2,3,4,5,6]
Expected: 110

// Test Case 2: Skewed tree
root = [1,null,2,null,3,null,4]
Expected: Product of split at optimal point

// Test Case 3: Balanced tree
root = [1,2,3,4,5,6,7]
Expected: Maximum product
```
