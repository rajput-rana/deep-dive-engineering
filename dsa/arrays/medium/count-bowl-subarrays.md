# Count Bowl Subarrays

## Problem Statement

Given an array `nums`, a **bowl subarray** is a contiguous subarray where:
- The subarray has length at least 3
- There exists an element in the subarray that is greater than all other elements in the subarray, and this maximum element is not at either end of the subarray

Return the total number of bowl subarrays.

**Example 1:**

```
Input: nums = [1,2,3,2,1]
Output: 2
Explanation: 
- [1,2,3,2] is a bowl subarray (3 is the maximum, not at ends)
- [2,3,2,1] is a bowl subarray (3 is the maximum, not at ends)
```

**Example 2:**

```
Input: nums = [1,2,3,4,5]
Output: 0
Explanation: No bowl subarray exists (maximum is always at the end)
```

**LeetCode Link:** https://leetcode.com/problems/count-bowl-subarrays/

## Constraints

- `3 <= nums.length <= 10^5`
- `1 <= nums[i] <= 10^9`

## Intuition

A bowl subarray has a "peak" element (maximum) that is not at either end. We need to count all subarrays where:
1. Length >= 3
2. Maximum element is in the middle (not first or last)

We use a **monotonic stack** approach:
- Maintain a stack of indices in decreasing order of values
- When we find a larger element, elements in stack can form bowl subarrays
- Check if the distance between current and stack top is >= 2 (length >= 3)

## Approach

**Monotonic Stack Algorithm:**

1. Use a stack to maintain indices in decreasing value order
2. For each element:
   - Pop all smaller elements from stack
   - For each popped element, if distance >= 2, it forms a bowl subarray
   - Check if current element forms bowl with stack top
   - Push current index

### Algorithm

1. Initialize stack and count = 0
2. For each index i:
   - While stack not empty and nums[stack.top] < nums[i]:
     - Pop index j
     - If i - j >= 2, increment count (bowl subarray found)
   - If stack not empty and i - stack.top >= 2:
     - Increment count (current forms bowl with stack top)
   - Push i to stack
3. Return count

### Implementation Notes

- **Runtime:** 19 ms
- **Memory:** 126.2 MB
- **Tags:** Array, Stack, Monotonic Stack
- **Difficulty:** Medium

**Key Points:**
- Stack maintains decreasing order
- Check distance >= 2 to ensure length >= 3
- Count both when popping and when checking stack top

## Complexity Analysis

- **Time Complexity:** O(n) - Each element pushed and popped at most once
- **Space Complexity:** O(n) - Stack can hold all indices

## Edge Cases

- **Strictly increasing**: No bowl subarrays (max always at end)
- **Strictly decreasing**: No bowl subarrays (max always at start)
- **Single peak**: Multiple bowl subarrays around peak
- **Multiple peaks**: Count bowls around each peak

## Solution Code

See the solution implementation in: [`count-bowl-subarrays.java`](./count-bowl-subarrays.java)

## Test Cases

```java
// Test Case 1: Example from problem
nums = [1,2,3,2,1]
Expected: 2

// Test Case 2: No bowl subarrays
nums = [1,2,3,4,5]
Expected: 0

// Test Case 3: Single peak
nums = [1,5,1]
Expected: 1
```
