# Maximum Level Sum Of A Binary Tree

## Problem Statement

Given the `root` of a binary tree, the **level** of its root is `1`, the level of its children is `2`, and so on.

Return the **smallest** level `x` such that the sum of all the values of nodes at level `x` is **maximal**.

**Example 1:**
```
Input: root = [1,7,0,7,-8,null,null]
Output: 2
Explanation: 
Level 1 sum = 1.
Level 2 sum = 7 + 0 = 7.
Level 3 sum = 7 + -8 = -1.
So we return the level with the maximum sum which is level 2.
```

**Example 2:**
```
Input: root = [989,null,10250,98693,-89388,null,null,null,-32127]
Output: 2
```

**LeetCode Link:** https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/

## Constraints

- The number of nodes in the tree is in the range `[1, 10^4]`
- `-10^5 <= Node.val <= 10^5`

## Intuition

Use **BFS (level-order traversal)** to process each level, calculate sum, and track the level with maximum sum.

## Approach

Perform BFS level by level:
1. Use a queue for level-order traversal
2. For each level, sum all node values
3. Track the level with maximum sum
4. Return the smallest level number if there's a tie

### Algorithm
1. Initialize queue with root, level = 1, maxSum = Long.MIN_VALUE, answerLevel = 1
2. While queue not empty:
   - Get current level size
   - Sum all nodes in current level
   - If sum > maxSum, update maxSum and answerLevel
   - Add children to queue
   - Increment level
3. Return answerLevel

### Implementation Notes
- **Runtime:** 8 ms
- **Memory:** 49.2 MB
- **Tags:** N/A
- **Difficulty:** Medium
- **Algorithm Type:** BFS (Level-order Traversal)

## Complexity Analysis

- **Time Complexity:** O(n) - Visit each node once
- **Space Complexity:** O(w) where w is maximum width of tree (queue size)

## Edge Cases

- Single node tree
- Skewed tree (all nodes in one path)
- All nodes have same value
- Negative values

## Solution Code

See the solution implementation in: [`maximum-level-sum-of-a-binary-tree.java`](./maximum-level-sum-of-a-binary-tree.java)

## Test Cases

```java
// See examples in problem statement above
// Additional test cases can be added here
```
