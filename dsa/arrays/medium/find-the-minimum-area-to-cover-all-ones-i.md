# Find the Minimum Area to Cover All Ones I

## Problem Statement

You are given a 2D binary `grid`. You need to find the minimum area of a rectangle such that it can cover all the `1`s in the grid.

A rectangle covers a `1` if the `1` is located inside the rectangle or on its boundary.

Return *the minimum area of such a rectangle*.

**Example 1:**

```
Input: grid = [[0,1,0],[1,0,1]]
Output: 6
Explanation: The minimum area rectangle that covers all ones has dimensions 2×3, so area = 6.
```

**Example 2:**

```
Input: grid = [[0,0],[1,0]]
Output: 1
Explanation: The minimum area rectangle that covers all ones has dimensions 1×1, so area = 1.
```

**LeetCode Link:** https://leetcode.com/problems/find-the-minimum-area-to-cover-all-ones-i/

## Constraints

- `1 <= grid.length, grid[0].length <= 100`
- `grid[i][j]` is either `0` or `1`
- There is at least one `1` in the grid

## Intuition

We need to find the **bounding box** of all `1`s in the grid. The minimum rectangle that covers all ones is the rectangle from the topmost row to bottommost row and leftmost column to rightmost column that contain `1`s.

## Approach

**Simple Bounding Box:**

1. Find the minimum and maximum row indices that contain `1`
2. Find the minimum and maximum column indices that contain `1`
3. Calculate area = (maxRow - minRow + 1) × (maxCol - minCol + 1)

### Algorithm

1. Initialize minRow = rows, maxRow = -1, minCol = cols, maxCol = -1
2. Iterate through grid:
   - If grid[i][j] == 1:
     - Update minRow = min(minRow, i)
     - Update maxRow = max(maxRow, i)
     - Update minCol = min(minCol, j)
     - Update maxCol = max(maxCol, j)
3. Calculate height = maxRow - minRow + 1
4. Calculate width = maxCol - minCol + 1
5. Return height × width

### Implementation Notes

- **Runtime:** 5 ms
- **Memory:** 239.8 MB
- **Tags:** Array, Matrix
- **Difficulty:** Medium

**Key Points:**
- Simple bounding box calculation
- Single pass through grid
- +1 because we need to include both boundaries

## Complexity Analysis

- **Time Complexity:** O(rows × cols) - Visit each cell once
- **Space Complexity:** O(1) - Only using a few variables

## Edge Cases

- **Single `1`**: Area is 1
- **All `1`s**: Area is entire grid
- **`1`s in one row**: Height is 1
- **`1`s in one column**: Width is 1

## Solution Code

See the solution implementation in: [`find-the-minimum-area-to-cover-all-ones-i.java`](./find-the-minimum-area-to-cover-all-ones-i.java)

## Test Cases

```java
// Test Case 1: Example from problem
grid = [[0,1,0],[1,0,1]]
Expected: 6

// Test Case 2: Single cell
grid = [[1]]
Expected: 1

// Test Case 3: All ones
grid = [[1,1],[1,1]]
Expected: 4
```
