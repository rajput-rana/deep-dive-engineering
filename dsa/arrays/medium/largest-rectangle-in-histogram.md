# Largest Rectangle In Histogram

## Problem Statement

Given an array of integers `heights` representing the histogram's bar height where the width of each bar is `1`, return *the area of the largest rectangle in the histogram*.

**Example 1:**
```
Input: heights = [2,1,5,6,2,3]
Output: 10
Explanation: The above is a histogram where width of each bar is 1.
The largest rectangle is shown in the red area, which has an area = 10 units.
```

**Example 2:**
```
Input: heights = [2,4]
Output: 4
```

**LeetCode Link:** https://leetcode.com/problems/largest-rectangle-in-histogram/

## Constraints

- `1 <= heights.length <= 10^5`
- `0 <= heights[i] <= 10^4`

## Intuition

Use a **monotonic stack** to maintain indices of bars in increasing height order. When we encounter a bar shorter than the top of the stack, we calculate the area of rectangles formed by popped bars.

## Approach

Maintain a monotonic increasing stack (bars stored in increasing height order). For each bar:
1. Pop bars taller than current and calculate their rectangle areas
2. The rectangle extends from previous bar in stack (left boundary) to current position (right boundary)
3. Push current bar index
4. Use a sentinel (height 0) at the end to process all remaining bars

### Algorithm
1. Initialize stack and maxArea = 0
2. Iterate through all bars (including sentinel at index n with height 0)
3. While stack not empty and current bar height < height at stack top:
   - Pop top index
   - Calculate height = heights[popped_index]
   - Calculate width = current_index - (stack_top_index or -1) - 1
   - Update maxArea = max(maxArea, height × width)
4. Push current index to stack
5. Return maxArea

### Implementation Notes
- **Runtime:** 67 ms
- **Memory:** 78.3 MB
- **Tags:** N/A
- **Difficulty:** Medium
- **Algorithm Type:** Monotonic Stack

## Complexity Analysis

- **Time Complexity:** O(n) - Each bar is pushed exactly once and popped at most once
- **Space Complexity:** O(n) - Stack can hold all bar indices in worst case

## Edge Cases

- Empty array (returns 0)
- Single bar (returns that bar's height)
- All bars same height (rectangle spans entire histogram)
- Strictly increasing heights (stack never pops until sentinel)
- Strictly decreasing heights (each bar pops all previous bars)

## Solution Code

See the solution implementation in: [`largest-rectangle-in-histogram.java`](./largest-rectangle-in-histogram.java)

## Test Cases

```java
// See examples in problem statement above
// Additional test cases can be added here
```
