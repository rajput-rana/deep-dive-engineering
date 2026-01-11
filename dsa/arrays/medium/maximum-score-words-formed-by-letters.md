# Maximum Score Words Formed by Letters

## Problem Statement

Given a list of `words`, a list of single `letters` (might be repeating), and a score of every character.

Return the maximum score of **any** valid set of words formed by using the given letters (each letter can only be used **once**). It is not necessary to use all characters in `letters` and each word can only be used **once**.

**Example 1:**

```
Input: words = ["dog","cat","dad","good"], letters = ["a","a","c","d","d","d","g","o","o"], score = [1,0,9,5,0,0,3,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0]
Output: 23
Explanation:
Score  a=1, c=9, d=5, g=3, o=2
Given letters, we can form the words "dad" (5+1+5) and "good" (3+2+2+5) with a score of 23.
Words "dad" and "dog" only get a score of 21.
```

**Example 2:**

```
Input: words = ["xxxz","ax","bx","cx"], letters = ["z","a","b","c","x","x","x"], score = [4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,0,10]
Output: 27
Explanation:
Score  a=4, b=4, c=4, x=5, z=10
Given letters, we can form the words "ax" (4+5), "bx" (4+5) and "cx" (4+5) with a score of 27.
Word "xxxz" only get a score of 25.
```

**LeetCode Link:** https://leetcode.com/problems/maximum-score-words-formed-by-letters/

## Constraints

- `1 <= words.length <= 14`
- `1 <= words[i].length <= 15`
- `1 <= letters.length <= 100`
- `letters[i].length == 1`
- `score.length == 26`
- `0 <= score[i] <= 10`
- `words[i]`, `letters[i]` contains only lower case English letters

## Intuition

This is a **backtracking/knapsack** problem. We need to choose a subset of words that:
1. Can be formed using available letters (each letter used at most once)
2. Maximizes the total score

We use **backtracking** to try all combinations:
- For each word, decide whether to include it or skip it
- If including, check if we have enough letters
- Track maximum score found

## Approach

**Backtracking Algorithm:**

1. **Precompute**: Calculate frequency array of available letters and score of each word
2. **Backtrack**: For each word:
   - **Option 1**: Skip the word
   - **Option 2**: Include the word (if letters available)
     - Subtract word's letter frequencies
     - Add word's score
     - Recurse
     - Restore frequencies (backtrack)
3. Track maximum score

### Algorithm

1. Count frequency of available letters
2. Precompute frequency and score for each word
3. Backtrack function:
   - Base case: Processed all words, update maxScore
   - Skip current word: Recurse with next word
   - Take current word (if possible):
     - Check if can form word with available letters
     - Subtract letter frequencies
     - Add word score
     - Recurse
     - Restore frequencies
4. Return maxScore

### Implementation Notes

- **Runtime:** 1 ms
- **Memory:** 43.2 MB
- **Tags:** Array, String, Backtracking, Bit Manipulation
- **Difficulty:** Hard

**Key Points:**
- Precompute word frequencies and scores for efficiency
- Use frequency array to track available letters
- Backtrack by restoring frequencies after recursion
- Prune branches where word can't be formed

## Complexity Analysis

- **Time Complexity:** O(2^n × m) where n is number of words, m is average word length
- **Space Complexity:** O(n × m) for storing word frequencies and recursion stack

## Edge Cases

- **Single word**: Return its score if formable
- **No words formable**: Return 0
- **All words formable**: Try all combinations
- **Limited letters**: Some words can't be formed together

## Solution Code

See the solution implementation in: [`maximum-score-words-formed-by-letters.java`](./maximum-score-words-formed-by-letters.java)

## Test Cases

```java
// Test Case 1: Example from problem
words = ["dog","cat","dad","good"]
letters = ["a","a","c","d","d","d","g","o","o"]
Expected: 23

// Test Case 2: Single word
words = ["abc"], letters = ["a","b","c"]
Expected: Score of "abc"

// Test Case 3: No words formable
words = ["xyz"], letters = ["a","b","c"]
Expected: 0
```
