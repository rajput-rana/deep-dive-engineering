/**
 * LeetCode Problem: Count Bowl Subarrays
 * 
 * Problem Link: https://leetcode.com/problems/count-bowl-subarrays/
 * 
 * Difficulty: Medium
 * Tags: Array, Stack, Monotonic Stack
 * 
 * Runtime: 19 ms
 * Memory: 126.2 MB
 * 
 * See problem details in: count-bowl-subarrays.md
 */

class Solution {
    public long bowlSubarrays(int[] nums) {
        int n = nums.length;
        long count = 0;

        // stack stores indices, values are accessed via nums[]
        java.util.Deque<Integer> stack = new java.util.ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            // Pop all smaller elements
            while (!stack.isEmpty() && nums[stack.peek()] < nums[i]) {
                int idx = stack.pop();
                // length >= 3 => distance >= 2
                if (i - idx >= 2) {
                    count++;
                }
            }

            // Check visibility with remaining top
            if (!stack.isEmpty()) {
                int idx = stack.peek();
                if (i - idx >= 2) {
                    count++;
                }
            }

            stack.push(i);
        }

        return count;
    }
}
