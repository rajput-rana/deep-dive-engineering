# Regular Expression Matching

## Problem Statement

Given an input string `s` and a pattern `p`, implement regular expression matching with support for `'.'` and `'*'` where:

- `'.'` Matches any single character.
- `'*'` Matches zero or more of the preceding element.

The matching should cover the **entire** input string (not partial).

**Example 1:**
```
Input: s = "aa", p = "a"
Output: false
Explanation: "a" does not match the entire string "aa".
```

**Example 2:**
```
Input: s = "aa", p = "a*"
Output: true
Explanation: '*' means zero or more of the preceding element, 'a'. Therefore, by repeating 'a' once, it becomes "aa".
```

**Example 3:**
```
Input: s = "ab", p = ".*"
Output: true
Explanation: ".*" means "zero or more (*) of any character (.)".
```

**LeetCode Link:** https://leetcode.com/problems/regular-expression-matching/

## Constraints

- 1 <= s.length <= 20
- 1 <= p.length <= 20
- s contains only lowercase English letters
- p contains only lowercase English letters, '.' and '*'
- It is guaranteed for each appearance of '*', there will be a previous valid character to match

## Intuition

Use **dynamic programming** where `dp[i][j]` represents whether first `i` characters of `s` match first `j` characters of `p`. Handle `*` by considering zero or more occurrences of preceding character.

## Approach

DP with two cases:
1. If pattern char matches string char or is '.': dp[i][j] = dp[i-1][j-1]
2. If pattern char is '*':
   - Zero occurrences: dp[i][j] = dp[i][j-2]
   - One or more: if preceding char matches, dp[i][j] = dp[i-1][j]

### Algorithm
1. Initialize dp[0][0] = true
2. Handle patterns like a*, a*b* matching empty string
3. For each (i, j):
   - If p[j-1] == '.' or p[j-1] == s[i-1]: dp[i][j] = dp[i-1][j-1]
   - Else if p[j-1] == '*':
     - Zero: dp[i][j] = dp[i][j-2]
     - One+: if p[j-2] matches s[i-1], dp[i][j] |= dp[i-1][j]
4. Return dp[m][n]

### Implementation Notes
- **Runtime:** 1 ms
- **Memory:** 43.7 MB
- **Tags:** N/A
- **Difficulty:** Medium
- **Algorithm Type:** Dynamic Programming

## Complexity Analysis

- **Time Complexity:** O(m × n) where m, n are lengths of string and pattern
- **Space Complexity:** O(m × n) for DP table

## Edge Cases

- Empty string with pattern like 'a*'
- Pattern with multiple '*' characters
- Pattern starting with '*'
- String and pattern both empty

## Solution Code

See the solution implementation in: [`regular-expression-matching.java`](./regular-expression-matching.java)

## Test Cases

```java
// See examples in problem statement above
// Additional test cases can be added here
```
