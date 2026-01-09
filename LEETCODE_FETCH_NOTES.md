# LeetCode Submission Fetcher Notes

## Current Status

The script currently fetches **19 accepted submissions**, but you mentioned having **50+ solved problems**.

## Pagination Issue

The LeetCode API's `/api/submissions/` endpoint appears to have limitations:
- Returns `has_next: true` but `last_key: null` after the first page
- May only return recent submissions (last 20-30)
- Pagination might require a different approach

## Solutions to Fetch All Submissions

### Option 1: Use LeetCode's GraphQL API
The GraphQL endpoint might provide better pagination:
```python
query = """
query recentAcSubmissions($username: String!, $limit: Int!) {
    recentAcSubmissions(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
        statusDisplay
        lang
        runtime
        memory
    }
}
"""
```

### Option 2: Manual Export
1. Go to https://leetcode.com/api/submissions/
2. Use browser DevTools to inspect the API calls
3. Export all submissions manually

### Option 3: Use LeetCode Export Tools
- https://github.com/NeverMendel/leetcode-export
- https://github.com/joshcai/leetcode-sync

## Usage

1. Set environment variables:
```bash
export LEETCODE_SESSION='your_session_cookie'
export LEETCODE_CSRF_TOKEN='your_csrf_token'
```

2. Fetch submissions:
```bash
python fetch_leetcode.py
```

3. Organize into DSA folder:
```bash
python organize_leetcode.py
```

## Files Created

Each problem gets two files:
- `problem-name.md` - Problem statement, approach, complexity
- `problem-name.java` - Solution code with metadata

Both files reference each other for easy navigation.

