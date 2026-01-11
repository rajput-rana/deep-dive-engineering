# Largest Rectangle in Histogram

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

The key insight is that for each bar, the largest rectangle it can form extends to the left until it hits a shorter bar, and to the right until it hits a shorter bar. We can use a **monotonic stack** to efficiently find these boundaries.

When we encounter a bar shorter than the one at the top of the stack, we know that the bar at the top can't extend further to the right. We pop it and calculate the rectangle area it can form.

## Approach

We maintain a **monotonic increasing stack** (bars stored in increasing height order). For each bar:

1. **Pop bars taller than current**: When we find a bar shorter than the stack top, we know bars in the stack can't extend further right. We pop them and calculate their rectangle areas.
2. **Calculate area**: For each popped bar, the rectangle extends from the previous bar in stack (left boundary) to current position (right boundary).
3. **Push current bar**: After popping all taller bars, push current bar index.
4. **Handle remaining bars**: After processing all bars, process remaining bars in stack using a sentinel height of 0.

### Algorithm

1. Initialize an empty stack and `maxArea = 0`
2. Iterate through all bars (including a sentinel at index `n` with height 0)
3. While stack is not empty and current bar height < height at stack top:
   - Pop the top index from stack
   - Calculate height = heights[popped_index]
   - Calculate width = current_index - (stack_top_index or -1) - 1
   - Update maxArea = max(maxArea, height × width)
4. Push current index to stack
5. Return maxArea

### Implementation Notes

- **Runtime:** 67 ms
- **Memory:** 78.3 MB
- **Tags:** Array, Stack, Monotonic Stack
- **Difficulty:** Hard

**Key Points:**
- Using a sentinel (height 0 at index n) ensures all bars are processed
- Stack stores indices, not heights, to calculate width correctly
- Left boundary is the previous index in stack (or -1 if stack empty)
- Right boundary is current index

## Complexity Analysis

- **Time Complexity:** O(n) - Each bar is pushed exactly once and popped at most once
- **Space Complexity:** O(n) - Stack can hold all bar indices in worst case (strictly increasing heights)

## Edge Cases

- **Empty array**: Should return 0 (handled by initialization)
- **Single bar**: Returns that bar's height
- **All bars same height**: Rectangle spans entire histogram
- **Strictly increasing heights**: Stack never pops until sentinel
- **Strictly decreasing heights**: Each bar pops all previous bars

## Solution Code

See the solution implementation in: [`largest-rectangle-in-histogram.java`](./largest-rectangle-in-histogram.java)

## Test Cases

```java
// Test Case 1: Example from problem
heights = [2,1,5,6,2,3]
Expected: 10

// Test Case 2: Two bars
heights = [2,4]
Expected: 4

// Test Case 3: Single bar
heights = [5]
Expected: 5

// Test Case 4: All same height
heights = [3,3,3,3]
Expected: 12

// Test Case 5: Strictly increasing
heights = [1,2,3,4,5]
Expected: 9 (height 3 × width 3)

// Test Case 6: Strictly decreasing
heights = [5,4,3,2,1]
Expected: 9 (height 3 × width 3)
```
