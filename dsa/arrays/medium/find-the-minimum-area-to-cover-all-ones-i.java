/**
 * LeetCode Problem: Find the Minimum Area to Cover All Ones I
 * 
 * Problem Link: https://leetcode.com/problems/find-the-minimum-area-to-cover-all-ones-i/
 * 
 * Difficulty: Medium
 * Tags: Array, Matrix
 * 
 * Runtime: 5 ms
 * Memory: 239.8 MB
 * 
 * See problem details in: find-the-minimum-area-to-cover-all-ones-i.md
 */

class Solution {
    public int minimumArea(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;

        int minRow = rows, maxRow = -1;
        int minCol = cols, maxCol = -1;

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (grid[i][j] == 1) {
                    minRow = Math.min(minRow, i);
                    maxRow = Math.max(maxRow, i);
                    minCol = Math.min(minCol, j);
                    maxCol = Math.max(maxCol, j);
                }
            }
        }

        int height = maxRow - minRow + 1;
        int width = maxCol - minCol + 1;

        return height * width;
    }
}
