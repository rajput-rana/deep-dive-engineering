/**
 * LeetCode Problem: Smallest Subtree with all the Deepest Nodes
 * 
 * Problem Link: https://leetcode.com/problems/smallest-subtree-with-all-the-deepest-nodes/
 * 
 * Difficulty: Medium
 * Tags: Hash Table, Tree, Depth-First Search, Breadth-First Search, Binary Tree
 * 
 * Runtime: 0 ms
 * Memory: 43.7 MB
 * 
 * See problem details in: smallest-subtree-with-all-the-deepest-nodes.md
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
    public TreeNode subtreeWithAllDeepest(TreeNode root) {
        return dfs(root).node;
    }

    private Result dfs(TreeNode root) {
        if (root == null) return new Result(null, 0);

        Result left = dfs(root.left);
        Result right = dfs(root.right);

        if (left.depth > right.depth) {
            return new Result(left.node, left.depth + 1);
        } else if (right.depth > left.depth) {
            return new Result(right.node, right.depth + 1);
        } else {
            return new Result(root, left.depth + 1);
        }
    }

    static class Result {
        TreeNode node;
        int depth;

        Result(TreeNode node, int depth) {
            this.node = node;
            this.depth = depth;
        }
    }
}
