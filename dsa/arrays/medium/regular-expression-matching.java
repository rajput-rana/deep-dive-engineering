/**
 * LeetCode Problem: Regular Expression Matching
 * 
 * Problem Link: https://leetcode.com/problems/regular-expression-matching/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 1 ms
 * Memory: 43.7 MB
 * 
 * See problem details in: regular-expression-matching.md
 */

class Solution {
    public boolean isMatch(String s, String p) {
        int m = s.length();
        int n = p.length();

        boolean[][] dp = new boolean[m + 1][n + 1];
        dp[0][0] = true;

        // Patterns like a*, a*b*, a*b*c* can match empty string
        for (int j = 2; j <= n; j++) {
            if (p.charAt(j - 1) == '*') {
                dp[0][j] = dp[0][j - 2];
            }
        }

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                char sc = s.charAt(i - 1);
                char pc = p.charAt(j - 1);

                if (pc == '.' || pc == sc) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else if (pc == '*') {
                    // zero occurrences
                    dp[i][j] = dp[i][j - 2];

                    char prev = p.charAt(j - 2);
                    // one or more occurrences
                    if (prev == '.' || prev == sc) {
                        dp[i][j] |= dp[i - 1][j];
                    }
                }
            }
        }

        return dp[m][n];
    }
}
