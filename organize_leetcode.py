import json
import os
import re
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
    
    # Skip if files already exist
    if md_filepath.exists() and code_filepath.exists():
        print(f"⚠️  Skipping {title} - files already exist")
        return
    
    # Extract tag names
    tag_names = [tag.get("name", "") for tag in tags]
    tag_list = ", ".join(tag_names) if tag_names else "N/A"
    
    # Create markdown content with problem details
    md_content = f"""# {title}

## Problem Statement

<!-- Problem description from LeetCode -->

**LeetCode Link:** https://leetcode.com/problems/{title_slug}/

Visit the [LeetCode problem page](https://leetcode.com/problems/{title_slug}/) for the complete problem statement, examples, and constraints.

## Constraints

<!-- Add constraints from LeetCode problem page -->

## Intuition

<!-- Explain the core insight or approach at a high level -->

## Approach

<!-- Detailed step-by-step solution approach -->

### Algorithm
1. 
2. 
3. 

### Implementation Notes
- **Runtime:** {runtime}
- **Memory:** {memory}
- **Tags:** {tag_list}
- **Difficulty:** {difficulty}

## Complexity Analysis

- **Time Complexity:** O()
- **Space Complexity:** O()

## Edge Cases

- 
- 

## Solution Code

See the solution implementation in: [`{base_filename}.{code_filepath.suffix[1:]}`](./{base_filename}.{code_filepath.suffix[1:]})

## Test Cases

```{code_lang}
// Example test cases
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

