# Minimum Number of Steps to Make Two Strings Anagram

## Problem Statement

You are given two strings of the same length `s` and `t`. In one step you can choose **any character** of `t` and replace it with **another character**.

Return *the **minimum number of steps** to make `t` an anagram of `s`*.

An **Anagram** of a string is a string that contains the same characters with a different (or the same) ordering.

**Example 1:**

```
Input: s = "bab", t = "aba"
Output: 1
Explanation: Replace the first 'a' in t with 'b', t = "bba" which is anagram of s.
```

**Example 2:**

```
Input: s = "leetcode", t = "practice"
Output: 5
Explanation: Replace 'p', 'r', 'a', 'i' and 'c' from t with proper characters to make t anagram of s.
```

**Example 3:**

```
Input: s = "anagram", t = "mangaar"
Output: 0
Explanation: "anagram" and "mangaar" are anagrams.
```

**LeetCode Link:** https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram/

## Constraints

- `1 <= s.length <= 5 * 10^4`
- `s.length == t.length`
- `s` and `t` consist of lowercase English letters only

## Intuition

To make `t` an anagram of `s`, both strings must have the same character frequencies. We need to find how many characters in `t` need to be changed.

The key insight: **We only need to change characters that are "extra" in `t`**. Characters that `t` has more of than `s` need to be reduced.

## Approach

**Frequency Counting:**

1. Count frequency of each character in both strings
2. For each character, if `s` has more occurrences than `t`, we need to add that many
3. But since we can only replace (not add), we count characters that `t` has **more** of than `s`
4. These "extra" characters in `t` need to be replaced

Actually, simpler approach:
- Count how many characters `s` has that `t` doesn't have enough of
- This equals the number of replacements needed

### Algorithm

1. Count frequency of each character in `s` and `t`
2. For each character:
   - If `freqS[i] > freqT[i]`: We need `freqS[i] - freqT[i]` more of this character
   - Sum all such differences
3. Return the sum (minimum steps needed)

### Implementation Notes

- **Runtime:** 9 ms
- **Memory:** 47.8 MB
- **Tags:** Hash Table, String, Counting
- **Difficulty:** Medium

**Key Points:**
- We count characters that `s` needs but `t` doesn't have enough of
- Each such character requires one replacement step
- Characters that `t` has extra of will be replaced automatically

## Complexity Analysis

- **Time Complexity:** O(n) where n is length of strings
- **Space Complexity:** O(1) - Fixed size frequency arrays (26 characters)

## Edge Cases

- **Already anagrams**: Return 0
- **Completely different**: Return length of string
- **Same string**: Return 0
- **One character different**: Return 1

## Solution Code

See the solution implementation in: [`minimum-number-of-steps-to-make-two-strings-anagram.java`](./minimum-number-of-steps-to-make-two-strings-anagram.java)

## Test Cases

```java
// Test Case 1: Example from problem
s = "bab", t = "aba"
Expected: 1

// Test Case 2: Already anagram
s = "anagram", t = "mangaar"
Expected: 0

// Test Case 3: Completely different
s = "abc", t = "xyz"
Expected: 3

// Test Case 4: Same string
s = "abc", t = "abc"
Expected: 0
```
