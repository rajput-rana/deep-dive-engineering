import requests
import json
import time
import ssl
import urllib3
from typing import List, Dict

# Disable SSL warnings (for development only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LeetCodeFetcher:
    def __init__(self, session_cookie: str, csrf_token: str):
        self.session_cookie = session_cookie
        self.csrf_token = csrf_token
        self.base_url = "https://leetcode.com"
        self.headers = {
            "Cookie": f"LEETCODE_SESSION={session_cookie}; csrftoken={csrf_token}",
            "X-CSRFToken": csrf_token,
            "Referer": "https://leetcode.com",
            "Content-Type": "application/json"
        }
    
    def get_submissions(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Fetch all accepted submissions with pagination"""
        url = f"{self.base_url}/api/submissions/"
        
        all_submissions = []
        last_key = ""
        page = 0
        max_pages = 100  # Safety limit
        
        while page < max_pages:
            params = {
                "limit": limit,
                "offset": 0,  # LeetCode uses last_key for pagination, not offset
                "lastkey": last_key if last_key else ""
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params, verify=False)
                response.raise_for_status()
                data = response.json()
                
                submissions = data.get("submissions_dump", [])
                if not submissions:
                    print(f"No more submissions found at page {page + 1}")
                    break
                
                # Filter only accepted submissions
                accepted = [s for s in submissions if s.get("status_display") == "Accepted"]
                all_submissions.extend(accepted)
                
                print(f"Page {page + 1}: Fetched {len(accepted)} accepted submissions (Total: {len(all_submissions)})")
                
                # Check if there are more pages
                has_next = data.get("has_next", False)
                last_key = data.get("last_key", "")
                
                # Check pagination - LeetCode API might return empty string for last_key
                # Try to get the last submission's ID as a fallback
                if has_next and not last_key and submissions:
                    # Use the last submission's ID or timestamp as pagination key
                    last_submission = submissions[-1]
                    last_key = str(last_submission.get("id", "")) or str(last_submission.get("timestamp", ""))
                    if last_key:
                        print(f"Using fallback pagination key: {last_key[:30]}...")
                
                # If no more pages, we're done
                if not has_next:
                    print("Reached end of submissions (has_next = False)")
                    break
                
                # If still no last_key after fallback, we can't continue
                if not last_key:
                    print("No pagination key available, stopping pagination")
                    print(f"Note: You may have {len(all_submissions)} total accepted submissions")
                    break
                
                page += 1
                time.sleep(1.5)  # Be nice to the API
                
            except Exception as e:
                print(f"Error fetching submissions at page {page + 1}: {e}")
                print(f"Response: {response.text[:200] if 'response' in locals() else 'No response'}")
                break
        
        return all_submissions
    
    def get_problem_details(self, problem_slug: str) -> Dict:
        """Get full problem details including description, constraints, examples"""
        query = """
        query questionContent($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                likes
                dislikes
                isLiked
                similarQuestions
                contributors {
                    username
                    profileUrl
                    avatarUrl
                }
                topicTags {
                    name
                    slug
                    translatedName
                }
                companyTagStats
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                stats
                hints
                solution {
                    id
                    canSeeDetail
                    paidOnly
                    hasVideoSolution
                    paidOnlyVideo
                }
                status
                sampleTestCase
                metaData
                judgerAvailable
                judgeType
                mysqlSchemas
                enableRunCode
                enableTestMode
                enableDebugger
                envInfo
                libraryUrl
                adminUrl
                challengeType
                acRate
            }
        }
        """
        
        url = f"{self.base_url}/graphql/"
        variables = {
            "titleSlug": problem_slug
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, verify=False)
            response.raise_for_status()
            data = response.json()
            
            question = data.get("data", {}).get("question", {})
            if question:
                return question
        except Exception as e:
            print(f"Error fetching problem details for {problem_slug}: {e}")
        
        return {}
    
    def fetch_all_submissions(self) -> List[Dict]:
        """Fetch all submissions with problem details"""
        print("Fetching your LeetCode submissions...")
        submissions = self.get_submissions()
        
        print(f"\nFound {len(submissions)} accepted submissions")
        print("Fetching problem details (this may take a while)...")
        
        enriched_submissions = []
        for i, submission in enumerate(submissions, 1):
            problem_slug = submission.get("title_slug", "")
            if problem_slug:
                problem_details = self.get_problem_details(problem_slug)
                submission["problem_details"] = problem_details
                print(f"Progress: {i}/{len(submissions)} - {submission.get('title', 'Unknown')}")
                time.sleep(0.5)  # Rate limiting
            
            enriched_submissions.append(submission)
        
        return enriched_submissions


def main():
    import os
    
    # Get credentials from environment variables
    SESSION_COOKIE = os.getenv("LEETCODE_SESSION")
    CSRF_TOKEN = os.getenv("LEETCODE_CSRF_TOKEN")
    
    if not SESSION_COOKIE or not CSRF_TOKEN:
        print("⚠️  Credentials not found in environment variables")
        print("\nTo use this script:")
        print("1. Set environment variables:")
        print("   export LEETCODE_SESSION='your_session_cookie'")
        print("   export LEETCODE_CSRF_TOKEN='your_csrf_token'")
        print("\n2. Or get your cookies:")
        print("   - Login to https://leetcode.com")
        print("   - Open Developer Tools (F12)")
        print("   - Go to Application/Storage tab")
        print("   - Open Cookies -> https://leetcode.com")
        print("   - Copy LEETCODE_SESSION and csrftoken values")
        return
    
    fetcher = LeetCodeFetcher(SESSION_COOKIE, CSRF_TOKEN)
    submissions = fetcher.fetch_all_submissions()
    
    # Save to JSON file
    output_file = "leetcode_submissions.json"
    with open(output_file, "w") as f:
        json.dump(submissions, f, indent=2)
    
    print(f"\n✅ Saved {len(submissions)} submissions to {output_file}")
    print("\nNext steps:")
    print("1. Review the JSON file")
    print("2. Run: python organize_leetcode.py")


if __name__ == "__main__":
    main()

