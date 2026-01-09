/**
 * LeetCode Problem: Longest Path With Different Adjacent Characters
 * 
 * Problem Link: https://leetcode.com/problems/longest-path-with-different-adjacent-characters/
 * 
 * Difficulty: Hard
 * Tags: Array, String, Tree, Depth-First Search, Graph, Topological Sort
 * 
 * Runtime: 92 ms
 * Memory: 163.9 MB
 * 
 * See problem details in: longest-path-with-different-adjacent-characters.md
 */

class Solution {
    private int answer = 1;

    public int longestPath(int[] parent, String s) {
        int n = parent.length;
        List<List<Integer>> tree = new ArrayList<>();

        for (int i = 0; i < n; i++) {
            tree.add(new ArrayList<>());
        }

        // build tree
        for (int i = 1; i < n; i++) {
            tree.get(parent[i]).add(i);
        }

        dfs(0, tree, s);
        return answer;
    }

    private int dfs(int node, List<List<Integer>> tree, String s) {
        int longest = 0;
        int secondLongest = 0;

        for (int child : tree.get(node)) {
            int childLen = dfs(child, tree, s);

            if (s.charAt(child) == s.charAt(node))
                continue;

            if (childLen > longest) {
                secondLongest = longest;
                longest = childLen;
            } else if (childLen > secondLongest) {
                secondLongest = childLen;
            }
        }

        // update global answer
        answer = Math.max(answer, longest + secondLongest + 1);

        // return longest downward path including this node
        return longest + 1;
    }
}
