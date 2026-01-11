import json
import os
import re
import html
from pathlib import Path
from typing import Dict, List

# Mapping from LeetCode tags to DSA folder categories
TAG_TO_CATEGORY = {
    "array": "arrays",
    "hash-table": "arrays",  # Hash tables often go with arrays
    "string": "strings",
    "linked-list": "linked-list",
    "stack": "stacks-queues",
    "queue": "stacks-queues",
    "tree": "trees",
    "binary-tree": "trees",
    "binary-search-tree": "trees",
    "graph": "graphs",
    "depth-first-search": "graphs",  # DFS/BFS are graph algorithms
    "breadth-first-search": "graphs",
    "dynamic-programming": "dynamic-programming",
    "greedy": "greedy",
    "backtracking": "backtracking",
    "bit-manipulation": "bit-manipulation",
    "math": "math",
    "two-pointers": "arrays",  # Two pointers is an array technique
    "sliding-window": "arrays",
    "sorting": "arrays",
    "heap-priority-queue": "stacks-queues",
    "trie": "trees",  # Trie is a tree structure
    "union-find": "graphs",
    "topological-sort": "graphs",
}

def analyze_solution(code: str, title: str, tags: List[str]) -> Dict[str, str]:
    """Analyze solution code and generate explanation"""
    explanation = {
        'intuition': '',
        'approach': '',
        'algorithm': '',
        'complexity': '',
        'edge_cases': '',
        'test_cases': ''
    }
    
    code_lower = code.lower()
    
    # Detect algorithm patterns
    if 'stack' in code_lower:
        explanation['intuition'] = "Use a stack to maintain indices of bars in increasing order of height. When we encounter a bar shorter than the top of the stack, we calculate the area of rectangles formed by popped bars."
        explanation['approach'] = "Maintain a monotonic stack where bars are stored in increasing height order. For each bar, pop all bars taller than current and calculate their rectangle areas."
        explanation['algorithm'] = "1. Initialize stack and maxArea\n2. Iterate through bars (including sentinel at end)\n3. While current bar is shorter than stack top, pop and calculate area\n4. Push current index to stack\n5. Return maxArea"
        explanation['complexity'] = "- **Time Complexity:** O(n) - Each bar is pushed and popped once\n- **Space Complexity:** O(n) - Stack can hold all bars"
        explanation['edge_cases'] = "- Empty array\n- Single bar\n- All bars same height\n- Strictly increasing heights"
    elif 'dfs' in code_lower or 'depth' in code_lower or 'recursive' in code_lower:
        explanation['intuition'] = "Use depth-first search to traverse the tree/graph and solve the problem recursively."
        explanation['approach'] = "Recursively explore all paths, maintaining state as we traverse."
        explanation['algorithm'] = "1. Base case: handle null/terminal nodes\n2. Recursive case: process current node\n3. Recursively solve subproblems\n4. Combine results"
        explanation['complexity'] = "- **Time Complexity:** O(n) where n is number of nodes\n- **Space Complexity:** O(h) where h is height (recursion stack)"
        explanation['edge_cases'] = "- Empty tree\n- Single node\n- Skewed tree (left or right only)"
    elif 'dp' in code_lower or 'dynamic' in code_lower or 'memo' in code_lower:
        explanation['intuition'] = "Break down the problem into smaller subproblems and store results to avoid recomputation."
        explanation['approach'] = "Use dynamic programming with memoization or tabulation to solve overlapping subproblems."
        explanation['algorithm'] = "1. Define state\n2. Identify recurrence relation\n3. Initialize base cases\n4. Fill DP table\n5. Return result"
        explanation['complexity'] = "- **Time Complexity:** O(n*m) where n, m are problem dimensions\n- **Space Complexity:** O(n*m) for DP table"
        explanation['edge_cases'] = "- Empty input\n- Single element\n- All same values"
    elif 'two pointer' in code_lower or 'left' in code_lower and 'right' in code_lower:
        explanation['intuition'] = "Use two pointers to traverse the array from both ends or at different speeds."
        explanation['approach'] = "Maintain two pointers and move them based on problem conditions."
        explanation['algorithm'] = "1. Initialize left and right pointers\n2. While pointers haven't met\n3. Process current elements\n4. Move pointers based on condition\n5. Return result"
        explanation['complexity'] = "- **Time Complexity:** O(n)\n- **Space Complexity:** O(1)"
        explanation['edge_cases'] = "- Empty array\n- Single element\n- All elements same"
    elif 'tree' in code_lower or 'treenode' in code_lower:
        explanation['intuition'] = "Traverse the tree structure to solve the problem."
        explanation['approach'] = "Use tree traversal (DFS/BFS) to visit nodes and process them."
        explanation['algorithm'] = "1. Handle base case (null node)\n2. Process current node\n3. Recursively process children\n4. Combine results"
        explanation['complexity'] = "- **Time Complexity:** O(n) - visit each node once\n- **Space Complexity:** O(h) - recursion stack or queue"
        explanation['edge_cases'] = "- Empty tree\n- Single node\n- Skewed tree"
    else:
        explanation['intuition'] = "Analyze the problem requirements and implement an efficient solution."
        explanation['approach'] = "Process the input according to problem constraints."
        explanation['algorithm'] = "1. Process input\n2. Apply algorithm\n3. Return result"
        explanation['complexity'] = "- **Time Complexity:** O()\n- **Space Complexity:** O()"
        explanation['edge_cases'] = "- Empty input\n- Single element\n- Edge values"
    
    return explanation

def sanitize_filename(title: str) -> str:
    """Convert problem title to a valid filename"""
    # Remove special characters and replace spaces with hyphens
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-')

def get_category(tags: List[Dict]) -> str:
    """Determine the DSA category from LeetCode tags"""
    tag_slugs = [tag.get("slug", "").lower() for tag in tags]
    
    # Priority order: trees and graphs should take precedence
    priority_tags = ["tree", "binary-tree", "binary-search-tree", "trie", "graph", 
                     "depth-first-search", "breadth-first-search", "union-find", 
                     "topological-sort"]
    
    # Check priority tags first
    for tag_slug in tag_slugs:
        if any(priority in tag_slug for priority in priority_tags):
            if "tree" in tag_slug or "trie" in tag_slug:
                return "trees"
            if "graph" in tag_slug or "depth-first-search" in tag_slug or "breadth-first-search" in tag_slug:
                return "graphs"
    
    # Check exact matches in TAG_TO_CATEGORY
    for tag_slug in tag_slugs:
        if tag_slug in TAG_TO_CATEGORY:
            return TAG_TO_CATEGORY[tag_slug]
    
    # Default fallback based on common patterns
    for tag_slug in tag_slugs:
        if "tree" in tag_slug:
            return "trees"
        if "graph" in tag_slug:
            return "graphs"
        if "array" in tag_slug:
            return "arrays"
        if "string" in tag_slug:
            return "strings"
    
    # Default to arrays if nothing matches
    return "arrays"

def get_difficulty_folder(difficulty: str) -> str:
    """Map LeetCode difficulty to folder name"""
    difficulty_lower = difficulty.lower()
    if difficulty_lower == "easy":
        return "easy"
    elif difficulty_lower == "medium":
        return "medium"
    elif difficulty_lower == "hard":
        return "hard"
    return "medium"  # Default

def create_problem_files(submission: Dict, base_path: Path) -> None:
    """Create both markdown and code files for a problem submission"""
    title = submission.get("title", "Unknown")
    title_slug = submission.get("title_slug", "")
    code = submission.get("code", "")
    difficulty = submission.get("problem_details", {}).get("difficulty", "Medium")
    tags = submission.get("problem_details", {}).get("topicTags", [])
    runtime = submission.get("runtime", "N/A")
    memory = submission.get("memory", "N/A")
    
    # Determine category and difficulty folder
    category = get_category(tags)
    difficulty_folder = get_difficulty_folder(difficulty)
    
    # Create directory structure
    problem_dir = base_path / category / difficulty_folder
    problem_dir.mkdir(parents=True, exist_ok=True)
    
    # Create base filename (without extension)
    base_filename = sanitize_filename(title)
    md_filepath = problem_dir / f"{base_filename}.md"
    code_filepath = problem_dir / f"{base_filename}.java"
    
    # Determine language and file extension
    language = submission.get("lang_name", "Java").lower()
    if "python" in language:
        code_filepath = problem_dir / f"{base_filename}.py"
        code_lang = "python"
    elif "java" in language:
        code_filepath = problem_dir / f"{base_filename}.java"
        code_lang = "java"
    elif "cpp" in language or "c++" in language:
        code_filepath = problem_dir / f"{base_filename}.cpp"
        code_lang = "cpp"
    else:
        code_filepath = problem_dir / f"{base_filename}.java"
        code_lang = "java"
    
    # Force update - remove existing files to regenerate with full details
    if md_filepath.exists():
        md_filepath.unlink()
    if code_filepath.exists():
        pass  # Keep code file, just update markdown
    
    # Extract tag names
    tag_names = [tag.get("name", "") for tag in tags]
    tag_list = ", ".join(tag_names) if tag_names else "N/A"
    
    # Extract problem content from GraphQL response
    problem_details = submission.get("problem_details", {})
    content_html = problem_details.get("content", "")
    
    # Parse HTML content to extract problem statement and constraints
    problem_statement = ""
    constraints = ""
    
    if content_html:
        # Remove HTML tags and decode entities
        # Extract text between <p> tags for problem statement
        problem_text = re.sub(r'<[^>]+>', '\n', content_html)
        problem_text = html.unescape(problem_text)
        problem_text = re.sub(r'\n+', '\n', problem_text).strip()
        
        # Split into problem statement and constraints
        parts = problem_text.split("Constraints:")
        if len(parts) > 1:
            problem_statement = parts[0].strip()
            constraints_section = parts[1].split("Example")[0].strip() if "Example" in parts[1] else parts[1].strip()
            # Extract constraint lines
            constraint_lines = [line.strip() for line in constraints_section.split('\n') if line.strip() and line.strip().startswith('-')]
            constraints = '\n'.join(constraint_lines) if constraint_lines else constraints_section
        else:
            problem_statement = problem_text
    
    # Analyze solution code to generate explanation
    solution_explanation = analyze_solution(code, title, tag_names)
    
    # Create markdown content with full problem details
    md_content = f"""# {title}

## Problem Statement

{problem_statement if problem_statement else "<!-- Problem description from LeetCode -->"}

**LeetCode Link:** https://leetcode.com/problems/{title_slug}/

## Constraints

{constraints if constraints else "<!-- Add constraints from LeetCode problem page -->"}

## Intuition

{solution_explanation.get('intuition', '<!-- Explain the core insight or approach at a high level -->')}

## Approach

{solution_explanation.get('approach', '<!-- Detailed step-by-step solution approach -->')}

### Algorithm
{solution_explanation.get('algorithm', '1. \n2. \n3. ')}

### Implementation Notes
- **Runtime:** {runtime}
- **Memory:** {memory}
- **Tags:** {tag_list}
- **Difficulty:** {difficulty}

## Complexity Analysis

{solution_explanation.get('complexity', '- **Time Complexity:** O()\n- **Space Complexity:** O()')}

## Edge Cases

{solution_explanation.get('edge_cases', '- \n- ')}

## Solution Code

See the solution implementation in: [`{base_filename}.{code_filepath.suffix[1:]}`](./{base_filename}.{code_filepath.suffix[1:]})

## Test Cases

```{code_lang}
{solution_explanation.get('test_cases', '// Example test cases')}
```
"""
    
    # Create code file content
    code_content = f"""/**
 * LeetCode Problem: {title}
 * 
 * Problem Link: https://leetcode.com/problems/{title_slug}/
 * 
 * Difficulty: {difficulty}
 * Tags: {tag_list}
 * 
 * Runtime: {runtime}
 * Memory: {memory}
 * 
 * See problem details in: {base_filename}.md
 */

{code}
"""
    
    # Write markdown file
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # Write code file
    with open(code_filepath, "w", encoding="utf-8") as f:
        f.write(code_content)
    
    print(f"✅ Created: {category}/{difficulty_folder}/{base_filename}.md + .{code_filepath.suffix[1:]}")

def main():
    # Read submissions JSON
    json_file = Path("leetcode_submissions.json")
    if not json_file.exists():
        print(f"❌ Error: {json_file} not found!")
        return
    
    with open(json_file, "r", encoding="utf-8") as f:
        submissions = json.load(f)
    
    print(f"📚 Processing {len(submissions)} submissions...\n")
    
    # Base path for DSA folder
    base_path = Path("dsa")
    
    # Track unique problems (by title_slug) to avoid duplicates
    seen_problems = set()
    unique_submissions = []
    
    for submission in submissions:
        title_slug = submission.get("title_slug", "")
        if title_slug and title_slug not in seen_problems:
            seen_problems.add(title_slug)
            unique_submissions.append(submission)
    
    print(f"📝 Found {len(unique_submissions)} unique problems\n")
    
    # Create files for each unique problem
    for submission in unique_submissions:
        create_problem_files(submission, base_path)
    
    print(f"\n✨ Successfully organized {len(unique_submissions)} problems!")

if __name__ == "__main__":
    main()

