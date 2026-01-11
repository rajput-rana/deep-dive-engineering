# Max Dot Product Of Two Subsequences

## Problem Statement

Given two arrays `nums1` and `nums2`.

Return the maximum dot product between **non-empty** subsequences of `nums1` and `nums2` with the same length.

A subsequence of an array is a new array which is formed from the original array by deleting some (can be none) of the characters without disturbing the relative positions of the remaining characters.

**Example 1:**
```
Input: nums1 = [2,1,-2,5], nums2 = [3,0,-6]
Output: 18
Explanation: Take subsequence [2,-2] from nums1 and subsequence [3,-6] from nums2.
Their dot product is (2*3 + (-2)*(-6)) = 6 + 12 = 18.
```

**Example 2:**
```
Input: nums1 = [3,-2], nums2 = [2,-6,7]
Output: 21
Explanation: Take subsequence [3] from nums1 and subsequence [7] from nums2.
Their dot product is (3*7) = 21.
```

**LeetCode Link:** https://leetcode.com/problems/max-dot-product-of-two-subsequences/

## Constraints

- `1 <= nums1.length, nums2.length <= 500`
- `-1000 <= nums1[i], nums2[i] <= 1000`

## Intuition

This is a **dynamic programming** problem similar to Longest Common Subsequence. We need to find subsequences of equal length with maximum dot product.

## Approach

Use DP where `dp[i][j]` represents the maximum dot product using first `i` elements of nums1 and first `j` elements of nums2. For each position, we can:
1. Take the product of current elements and add to previous best
2. Skip current element from nums1
3. Skip current element from nums2
4. Take only current product (start new subsequence)

### Algorithm
1. Initialize DP table with very small values (Integer.MIN_VALUE/2)
2. For each position (i, j):
   - Calculate product = nums1[i-1] * nums2[j-1]
   - dp[i][j] = max(product, product + dp[i-1][j-1], dp[i-1][j], dp[i][j-1])
3. Return dp[n][m]

### Implementation Notes
- **Runtime:** 7 ms
- **Memory:** 46.4 MB
- **Tags:** N/A
- **Difficulty:** Medium
- **Algorithm Type:** Dynamic Programming

## Complexity Analysis

- **Time Complexity:** O(n × m) where n, m are lengths of arrays
- **Space Complexity:** O(n × m) for DP table

## Edge Cases

- All negative numbers
- All positive numbers
- Mixed positive and negative
- Single element arrays

## Solution Code

See the solution implementation in: [`max-dot-product-of-two-subsequences.java`](./max-dot-product-of-two-subsequences.java)

## Test Cases

```java
// See examples in problem statement above
// Additional test cases can be added here
```
