/**
 * LeetCode Problem: Non-decreasing Subsequences
 * 
 * Problem Link: https://leetcode.com/problems/non-decreasing-subsequences/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 6 ms
 * Memory: 53.3 MB
 * 
 * See problem details in: non-decreasing-subsequences.md
 */

class Solution {
     public List<List<Integer>> findSubsequences(int[] nums) {
        List<List<Integer>> res = new ArrayList<>();
        backtrack(nums, 0, new ArrayList<>(), res);
        return res;
    }

    private void backtrack(int[] nums, int start, List<Integer> path, List<List<Integer>> res) {
        if (path.size() >= 2) {
            res.add(new ArrayList<>(path));
        }

        // Used to avoid duplicates at the same recursion depth
        Set<Integer> used = new HashSet<>();

        for (int i = start; i < nums.length; i++) {
            // Non-decreasing condition
            if (!path.isEmpty() && nums[i] < path.get(path.size() - 1)) {
                continue;
            }

            // Avoid duplicate choices at this depth
            if (used.contains(nums[i])) {
                continue;
            }

            used.add(nums[i]);
            path.add(nums[i]);
            backtrack(nums, i + 1, path, res);
            path.remove(path.size() - 1);
        }
    }

}
