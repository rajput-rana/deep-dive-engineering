/**
 * LeetCode Problem: Minimum Number of Steps to Make Two Strings Anagram
 * 
 * Problem Link: https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 9 ms
 * Memory: 47.8 MB
 * 
 * See problem details in: minimum-number-of-steps-to-make-two-strings-anagram.md
 */

class Solution {
    public int minSteps(String s, String t) {
         int[] freqS = new int[26];
        int[] freqT = new int[26];

        for (int i = 0; i < s.length(); i++) {
            freqS[s.charAt(i) - 'a']++;
            freqT[t.charAt(i) - 'a']++;
        }

        int steps = 0;
        for (int i = 0; i < 26; i++) {
            if (freqS[i] > freqT[i]) {
                steps += freqS[i] - freqT[i];
            }
        }
        return steps;
    }
}
