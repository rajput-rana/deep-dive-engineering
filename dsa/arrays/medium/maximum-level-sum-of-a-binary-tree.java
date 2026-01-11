/**
 * LeetCode Problem: Maximum Level Sum of a Binary Tree
 * 
 * Problem Link: https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 8 ms
 * Memory: 49.2 MB
 * 
 * See problem details in: maximum-level-sum-of-a-binary-tree.md
 */

/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class Solution {
    public int maxLevelSum(TreeNode root) {
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);

        int level = 1;
        int answerLevel = 1;
        long maxSum = Long.MIN_VALUE;

        while (!queue.isEmpty()) {
            int size = queue.size();
            long sum = 0;

            for (int i = 0; i < size; i++) {
                TreeNode node = queue.poll();
                sum += node.val;

                if (node.left != null)
                    queue.offer(node.left);
                if (node.right != null)
                    queue.offer(node.right);
            }

            if (sum > maxSum) {
                maxSum = sum;
                answerLevel = level;
            }

            level++;
        }

        return answerLevel;
    }
}
