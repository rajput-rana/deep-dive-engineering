/**
 * LeetCode Problem: Maximum Product of Splitted Binary Tree
 * 
 * Problem Link: https://leetcode.com/problems/maximum-product-of-splitted-binary-tree/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 5 ms
 * Memory: 59.4 MB
 * 
 * See problem details in: maximum-product-of-splitted-binary-tree.md
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
    private long totalSum = 0;
    private long maxProduct = 0;
    private static final int MOD = 1_000_000_007;

    public int maxProduct(TreeNode root) {
        // 1st pass: compute total sum
        computeTotalSum(root);

        // 2nd pass: compute subtree sums & maximize product
        computeSubtreeSum(root);

        return (int) (maxProduct % MOD);
    }

    private void computeTotalSum(TreeNode node) {
        if (node == null)
            return;
        totalSum += node.val;
        computeTotalSum(node.left);
        computeTotalSum(node.right);
    }

    private long computeSubtreeSum(TreeNode node) {
        if (node == null)
            return 0;

        long left = computeSubtreeSum(node.left);
        long right = computeSubtreeSum(node.right);

        long subSum = node.val + left + right;

        // consider cutting above this node
        long product = subSum * (totalSum - subSum);
        maxProduct = Math.max(maxProduct, product);

        return subSum;
    }
}
