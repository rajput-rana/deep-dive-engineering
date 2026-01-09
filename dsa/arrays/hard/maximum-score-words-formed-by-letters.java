/**
 * LeetCode Problem: Maximum Score Words Formed by Letters
 * 
 * Problem Link: https://leetcode.com/problems/maximum-score-words-formed-by-letters/
 * 
 * Difficulty: Hard
 * Tags: Array, Hash Table, String, Dynamic Programming, Backtracking, Bit Manipulation, Counting, Bitmask
 * 
 * Runtime: 1 ms
 * Memory: 43.2 MB
 * 
 * See problem details in: maximum-score-words-formed-by-letters.md
 */

class Solution {
    int maxScore = 0;

    public int maxScoreWords(String[] words, char[] letters, int[] score) {
        int[] freq = new int[26];
        for (char c : letters) {
            freq[c - 'a']++;
        }

        int n = words.length;
        int[][] wordFreq = new int[n][26];
        int[] wordScore = new int[n];

        // Precompute frequency and score of each word
        for (int i = 0; i < n; i++) {
            for (char c : words[i].toCharArray()) {
                int idx = c - 'a';
                wordFreq[i][idx]++;
                wordScore[i] += score[idx];
            }
        }

        backtrack(0, freq, wordFreq, wordScore, 0);
        return maxScore;
    }

    private void backtrack(int idx, int[] freq, int[][] wordFreq, int[] wordScore, int currScore) {
        if (idx == wordFreq.length) {
            maxScore = Math.max(maxScore, currScore);
            return;
        }

        // Option 1: skip current word
        backtrack(idx + 1, freq, wordFreq, wordScore, currScore);

        // Option 2: take current word (if possible)
        if (canTake(freq, wordFreq[idx])) {
            for (int i = 0; i < 26; i++) {
                freq[i] -= wordFreq[idx][i];
            }

            backtrack(idx + 1, freq, wordFreq, wordScore, currScore + wordScore[idx]);

            // restore
            for (int i = 0; i < 26; i++) {
                freq[i] += wordFreq[idx][i];
            }
        }
    }

    private boolean canTake(int[] freq, int[] wf) {
        for (int i = 0; i < 26; i++) {
            if (wf[i] > freq[i])
                return false;
        }
        return true;
    }
}
