/**
 * LeetCode Problem: Minimum Deletions to Make Character Frequencies Unique
 * 
 * Problem Link: https://leetcode.com/problems/minimum-deletions-to-make-character-frequencies-unique/
 * 
 * Difficulty: Medium
 * Tags: N/A
 * 
 * Runtime: 7 ms
 * Memory: 47.7 MB
 * 
 * See problem details in: minimum-deletions-to-make-character-frequencies-unique.md
 */

class Solution {
    public int minDeletions(String s) {
        int[] freq = new int[26];
        
        // Count frequencies
        for (char c : s.toCharArray()) {
            freq[c - 'a']++;
        }

        Set<Integer> used = new HashSet<>();
        int deletions = 0;

        for (int f : freq) {
            // Reduce frequency until it becomes unique or zero
            while (f > 0 && used.contains(f)) {
                f--;
                deletions++;
            }
            if (f > 0) {
                used.add(f);
            }
        }

        return deletions;
    }
}
