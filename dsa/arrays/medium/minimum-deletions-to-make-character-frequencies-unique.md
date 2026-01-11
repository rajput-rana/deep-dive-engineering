# Minimum Deletions To Make Character Frequencies Unique

## Problem Statement

A string `s` is called **good** if there are no two different characters in `s` that have the same **frequency**.

Given a string `s`, return *the **minimum** number of characters you need to delete to make `s` **good***.

**Example 1:**
```
Input: s = "aab"
Output: 0
Explanation: s is already good.
```

**Example 2:**
```
Input: s = "aaabbbcc"
Output: 2
Explanation: You can delete two 'b's resulting in the good string "aaabcc".
Another way is to delete one 'b' and one 'c' resulting in the good string "aaabbc".
```

**Example 3:**
```
Input: s = "ceabaacb"
Output: 2
Explanation: You can delete both 'c's resulting in the good string "eabaab".
```

**LeetCode Link:** https://leetcode.com/problems/minimum-deletions-to-make-character-frequencies-unique/

## Constraints

- `1 <= s.length <= 10^5`
- `s` contains only lowercase English letters.

## Intuition

Count character frequencies, then ensure all frequencies are unique by reducing duplicates. Use a greedy approach: for each frequency, reduce it until it becomes unique or zero.

## Approach

1. Count frequency of each character
2. For each frequency, check if it's already used
3. If duplicate, reduce frequency until unique or zero
4. Track number of deletions needed

### Algorithm
1. Count frequencies of all characters
2. Use a Set to track used frequencies
3. For each frequency:
   - While frequency > 0 and already in used set:
     - Decrement frequency and increment deletions
   - If frequency > 0, add to used set
4. Return total deletions

### Implementation Notes
- **Runtime:** 7 ms
- **Memory:** 47.7 MB
- **Tags:** N/A
- **Difficulty:** Medium
- **Algorithm Type:** Algorithm

## Complexity Analysis

- **Time Complexity:** O(n + k²) where n is string length, k is number of unique characters (at most 26)
- **Space Complexity:** O(k) for frequency array and used set

## Edge Cases

- All characters same (no deletions needed)
- All characters unique (no deletions needed)
- Many characters with same frequency

## Solution Code

See the solution implementation in: [`minimum-deletions-to-make-character-frequencies-unique.java`](./minimum-deletions-to-make-character-frequencies-unique.java)

## Test Cases

```java
// See examples in problem statement above
// Additional test cases can be added here
```
