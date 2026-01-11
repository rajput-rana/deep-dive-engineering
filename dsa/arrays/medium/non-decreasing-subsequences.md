# Non Decreasing Subsequences

## Problem Statement

Given an integer array `nums`, return *all the different possible non-decreasing subsequences of the given array with at least two elements*. You may return the answer in **any order**.

**Example 1:**
```
Input: nums = [4,6,7,7]
Output: [[4,6],[4,6,7],[4,6,7,7],[4,7],[4,7,7],[6,7],[6,7,7],[7,7]]
```

**Example 2:**
```
Input: nums = [4,4,3,2,1]
Output: [[4,4]]
```

**LeetCode Link:** https://leetcode.com/problems/non-decreasing-subsequences/

## Constraints

- `1 <= nums.length <= 15`
- `-100 <= nums[i] <= 100`

## Intuition

Use **backtracking** to generate all non-decreasing subsequences. Avoid duplicates by skipping same values at the same recursion depth.

## Approach

Backtracking with duplicate prevention:
1. Start with empty path
2. For each position, decide whether to include current element
3. Ensure non-decreasing order
4. Use a Set at each recursion level to avoid duplicate choices
5. Add path to result if length >= 2

### Algorithm
1. Initialize result list
2. Backtrack function:
   - If path size >= 2, add to result
   - Use Set to track used values at current depth
   - For each remaining element:
     - Skip if violates non-decreasing order
     - Skip if already used at this depth
     - Add to path, recurse, remove from path
3. Return result

### Implementation Notes
- **Runtime:** 6 ms
- **Memory:** 53.3 MB
- **Tags:** N/A
- **Difficulty:** Medium
- **Algorithm Type:** Backtracking

## Complexity Analysis

- **Time Complexity:** O(2^n × n) - Exponential due to all subsequences
- **Space Complexity:** O(n) - Recursion stack and path storage

## Edge Cases

- All elements same
- Strictly decreasing array
- Strictly increasing array
- Duplicate elements

## Solution Code

See the solution implementation in: [`non-decreasing-subsequences.java`](./non-decreasing-subsequences.java)

## Test Cases

```java
// See examples in problem statement above
// Additional test cases can be added here
```
