/**
 * LeetCode Problem: Largest Rectangle in Histogram
 * 
 * Problem Link: https://leetcode.com/problems/largest-rectangle-in-histogram/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 67 ms
 * Memory: 78.3 MB
 * 
 * See problem details in: largest-rectangle-in-histogram.md
 */

class Solution {
    public int largestRectangleArea(int[] heights) {
        Stack<Integer> stack = new Stack<>();
        int maxArea = 0;
        int n = heights.length;

        for (int i = 0; i <= n; i++) {
            int currHeight = (i == n) ? 0 : heights[i];

            while (!stack.isEmpty() && currHeight < heights[stack.peek()]) {
                int height = heights[stack.pop()];
                int right = i;
                int left = stack.isEmpty() ? -1 : stack.peek();
                int width = right - left - 1;

                maxArea = Math.max(maxArea, height * width);
            }

            stack.push(i);
        }

        return maxArea;
    }
}
