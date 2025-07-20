#!/usr/bin/env python3
"""
Generate backup PR lists for Jekyll site.
Fetches PR data from GitHub API and generates YAML file for Jekyll consumption.
"""

import os
import sys
import yaml
import requests
import time
from datetime import datetime
from typing import List, Dict, Any


def get_github_token() -> str:
    """Get GitHub token from environment."""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    return token


def make_github_request(url: str, token: str) -> Dict[Any, Any]:
    """Make authenticated request to GitHub API with rate limiting."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'pureween-blog-backup-generator'
    }
    
    response = requests.get(url, headers=headers)
    
    # Basic rate limiting - wait if we're getting close to limits
    remaining = int(response.headers.get('X-RateLimit-Remaining', '0'))
    if remaining < 10:
        reset_time = int(response.headers.get('X-RateLimit-Reset', '0'))
        current_time = int(time.time())
        if reset_time > current_time:
            sleep_time = min(reset_time - current_time + 1, 60)  # Max 60 seconds
            print(f"Rate limit low ({remaining} remaining), sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
    
    response.raise_for_status()
    return response.json()


def get_high_value_prs(token: str, repo_owner: str, repo_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get high value PRs (critical label or >10 comments).
    """
    # Search for PRs with critical label
    critical_url = f"https://api.github.com/search/issues?q=repo:{repo_owner}/{repo_name}+is:pr+is:open+label:critical&sort=updated&order=desc&per_page={limit}"
    
    # Search for PRs with many comments  
    commented_url = f"https://api.github.com/search/issues?q=repo:{repo_owner}/{repo_name}+is:pr+is:open+comments:>10&sort=comments&order=desc&per_page={limit}"
    
    try:
        critical_prs = make_github_request(critical_url, token).get('items', [])
        commented_prs = make_github_request(commented_url, token).get('items', [])
        
        # Combine and deduplicate by PR number
        seen_numbers = set()
        high_value_prs = []
        
        for pr in critical_prs + commented_prs:
            if pr['number'] not in seen_numbers:
                seen_numbers.add(pr['number'])
                high_value_prs.append({
                    'number': pr['number'],
                    'title': pr['title'],
                    'url': pr['html_url'],
                    'user': pr['user']['login'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'comments': pr['comments'],
                    'labels': [label['name'] for label in pr.get('labels', [])]
                })
                
                if len(high_value_prs) >= limit:
                    break
        
        return high_value_prs[:limit]
    
    except requests.exceptions.RequestException as e:
        print(f"Warning: GitHub API request failed for high value PRs: {e}")
        return []
    except Exception as e:
        print(f"Warning: Failed to fetch high value PRs: {e}")
        return []


def get_least_changes_prs(token: str, repo_owner: str, repo_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get PRs with least file changes.
    """
    # Get open PRs
    prs_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=open&sort=updated&direction=desc&per_page=100"
    
    try:
        prs = make_github_request(prs_url, token)
        
        pr_details = []
        for i, pr in enumerate(prs):
            try:
                # Small delay between requests to be respectful
                if i > 0:
                    time.sleep(0.1)
                    
                # Get detailed PR info including file changes
                pr_detail_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr['number']}"
                pr_detail = make_github_request(pr_detail_url, token)
                
                pr_details.append({
                    'number': pr_detail['number'],
                    'title': pr_detail['title'],
                    'url': pr_detail['html_url'],
                    'user': pr_detail['user']['login'],
                    'created_at': pr_detail['created_at'],
                    'updated_at': pr_detail['updated_at'],
                    'comments': pr_detail.get('comments', 0),
                    'changed_files': pr_detail.get('changed_files', 0),
                    'labels': [label['name'] for label in pr_detail.get('labels', [])]
                })
            except requests.exceptions.RequestException as e:
                print(f"Warning: Failed to fetch details for PR #{pr['number']}: {e}")
                continue
        
        # Sort by fewest changed files
        pr_details.sort(key=lambda x: x['changed_files'])
        return pr_details[:limit]
    
    except requests.exceptions.RequestException as e:
        print(f"Warning: GitHub API request failed for least changes PRs: {e}")
        return []
    except Exception as e:
        print(f"Warning: Failed to fetch least changes PRs: {e}")
        return []


def generate_backup_prs_yaml(repo_owner: str, repo_name: str, output_path: str):
    """Generate the backup PRs YAML file."""
    token = get_github_token()
    
    print(f"Fetching PR data for {repo_owner}/{repo_name}...")
    
    high_value_prs = get_high_value_prs(token, repo_owner, repo_name)
    least_changes_prs = get_least_changes_prs(token, repo_owner, repo_name)
    
    backup_data = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'repository': f"{repo_owner}/{repo_name}",
        'high_value_prs': high_value_prs,
        'least_changes_prs': least_changes_prs
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write YAML file
    with open(output_path, 'w') as f:
        yaml.dump(backup_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"Generated backup PR data with {len(high_value_prs)} high value PRs and {len(least_changes_prs)} least changes PRs")
    print(f"Output written to: {output_path}")


def main():
    """Main entry point."""
    # Default to Microsoft/dotnet-maui repository as an example
    # Can be overridden via environment variables
    repo_owner = os.environ.get('REPO_OWNER', 'microsoft')
    repo_name = os.environ.get('REPO_NAME', 'maui')
    output_path = os.environ.get('OUTPUT_PATH', '_data/backup_prs.yaml')
    
    try:
        generate_backup_prs_yaml(repo_owner, repo_name, output_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()