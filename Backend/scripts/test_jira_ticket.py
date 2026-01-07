"""
Test script to create a Jira ticket using Jira REST API.
Tests the Jira integration by creating a sample vulnerability ticket.

Usage:
    python scripts/test_jira_ticket.py
    
Or with arguments:
    python scripts/test_jira_ticket.py --url https://example.atlassian.net --email user@example.com --token YOUR_TOKEN --project PROJ
"""
import argparse
import sys
from datetime import datetime

import requests


def create_jira_ticket(
    jira_url: str,
    email: str,
    api_token: str,
    project_key: str,
    summary: str = None,
    description: str = None,
    issue_type: str = "Bug"
) -> dict:
    """
    Create a Jira ticket using REST API v3.
    
    Args:
        jira_url: Base Jira URL (e.g., https://example.atlassian.net)
        email: Jira user email
        api_token: Jira API token
        project_key: Project key (e.g., PROJ, DEV)
        summary: Issue summary/title
        description: Issue description
        issue_type: Type of issue (Bug, Task, Story, etc.)
    
    Returns:
        Created issue data with key and URL
    """
    # Remove trailing slash from URL
    jira_url = jira_url.rstrip('/')
    
    # Default summary and description if not provided
    if not summary:
        summary = f"[TEST] Vulnerability Test Ticket - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    if not description:
        description = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a test vulnerability ticket created by VMS Bridge.",
                            "marks": [{"type": "strong"}]
                        }
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Vulnerability Details:"
                        }
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Severity: High",
                                            "marks": [{"type": "strong"}]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "CVE: CVE-2024-12345"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Package: test-package@1.0.0"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    
    # API endpoint
    url = f"{jira_url}/rest/api/3/issue"
    
    # Request headers
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Request payload
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": issue_type
            }
        }
    }
    
    # Make request with basic auth
    auth = (email, api_token)
    
    print(f"Creating Jira ticket in project '{project_key}'...")
    print(f"URL: {url}")
    print(f"Email: {email}")
    print(f"Summary: {summary}")
    print()
    
    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth)
        response.raise_for_status()
        
        result = response.json()
        issue_key = result.get("key")
        issue_url = f"{jira_url}/browse/{issue_key}"
        
        print("✅ Ticket created successfully!")
        print(f"   Issue Key: {issue_key}")
        print(f"   URL: {issue_url}")
        print()
        
        return {
            "key": issue_key,
            "url": issue_url,
            "id": result.get("id"),
            "self": result.get("self")
        }
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Create a test Jira ticket to verify integration"
    )
    parser.add_argument(
        "--url",
        help="Jira base URL (e.g., https://example.atlassian.net)",
        required=False
    )
    parser.add_argument(
        "--email",
        help="Jira user email",
        required=False
    )
    parser.add_argument(
        "--token",
        help="Jira API token",
        required=False
    )
    parser.add_argument(
        "--project",
        help="Project key (e.g., PROJ, DEV)",
        required=False
    )
    parser.add_argument(
        "--summary",
        help="Custom issue summary",
        required=False
    )
    parser.add_argument(
        "--type",
        help="Issue type (Bug, Task, Story, etc.)",
        default="Bug",
        required=False
    )
    
    args = parser.parse_args()
    
    # Interactive mode if no arguments provided
    if not args.url:
        print("=== Jira Ticket Creation Test ===\n")
        jira_url = input("Jira URL (e.g., https://example.atlassian.net): ").strip()
        email = input("Jira Email: ").strip()
        api_token = input("Jira API Token: ").strip()
        project_key = input("Project Key (e.g., PROJ): ").strip().upper()
        
        if not all([jira_url, email, api_token, project_key]):
            print("\n❌ Error: All fields are required!")
            sys.exit(1)
    else:
        jira_url = args.url
        email = args.email
        api_token = args.token
        project_key = args.project.upper() if args.project else None
        
        if not all([jira_url, email, api_token, project_key]):
            print("❌ Error: --url, --email, --token, and --project are all required!")
            sys.exit(1)
    
    print()
    result = create_jira_ticket(
        jira_url=jira_url,
        email=email,
        api_token=api_token,
        project_key=project_key,
        summary=args.summary,
        issue_type=args.type
    )
    
    print("Test completed successfully! ✨")
    return result


if __name__ == "__main__":
    main()
