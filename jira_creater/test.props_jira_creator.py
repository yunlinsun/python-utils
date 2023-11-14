import git
from datetime import datetime, timezone
import os
import requests
from requests.auth import HTTPBasicAuth

# Jira Setting
username = 'yunlin.sun@liferay.com'
api_token = os.getenv('JIRA_TOKEN') 
base_url = 'https://liferay.atlassian.net/browse/'
url = 'https://liferay.atlassian.net/rest/api/3/issue/'
search_url = 'https://liferay.atlassian.net/rest/api/3/search/'
auth = HTTPBasicAuth(username, api_token)
headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}

# Git Setting
repo = git.Repo('/home/me/dev/projects/liferay-portal')
cutoff_date = datetime(2023, 7, 31).replace(tzinfo=timezone.utc)

# Traverse all modifiled files
test_files = []
for file in repo.tree().traverse():
  if file.path.endswith('test.properties') and '/' in file.path:
    test_files.append(file)

# Define get_existing_issue_key function
def get_existing_issue_key(file_path):
    # Use Jira REST API to query open issues related to the file path
    query_url = f"{search_url}?jql=project=LRQA%20AND%20summary~%22Backport%20review%20of%20{file_path}%22%20AND%20status!=Closed"
    
    try:
        response = requests.get(query_url, headers=headers, auth=auth)
        response.raise_for_status()  # 抛出HTTP错误
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve Jira issues. Error: {str(e)}")
        return None

    issues = response.json().get("issues", [])
    if issues:
        return issues[0]["key"]
    return None


# Define get_issue_status function
def get_issue_status(issue_key):
    # Use Jira REST API to query the status of a specific issue
    query_url = f"{url}{issue_key}?fields=status"
    response = requests.get(query_url, headers=headers, auth=auth)
    issue_status = response.json().get("fields", {}).get("status", {}).get("name")
    return issue_status

# Create issue  
for file in test_files:
  commits = repo.iter_commits(paths=file.path, since=cutoff_date)
  try:
    commit = next(commits)
    date = commit.committed_datetime.strftime("%Y-%m-%d")
    
    # Check if a corresponding Jira task already exists
    existing_issue_key = get_existing_issue_key(file.path)
    if existing_issue_key:
        print(f"Jira task for {file.path} already exists: {base_url + existing_issue_key}")

        # Check if the status is not Closed
        issue_status = get_issue_status(existing_issue_key)
        if issue_status and issue_status != "Closed":
            print(f"Jira task is not closed. Status: {issue_status}")
        else:
            print("Jira task is closed.")

        continue

    # Set json
    data = {
    "fields": {
        "project": {
            "key": "LRQA"
        },
        "issuetype": {
            "name": "Task"  
        },
        "summary": f"Backport review of {file.path}",
        "components": [
            {
                "name": "CNQA"
            }
        ],
        "description": {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Modified on: " + str(date),
                        }
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": " ",
                        },
                        {
                            "type": "text",
                            "text": "Need backport review: ",
                        },                      
                        {
                            "type": "text",
                            "text": "click here to see the file.",
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {
                                        "href": "https://github.com/liferay/liferay-portal/commits/master/" + file.path
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "labels": ["ESQA_Backport"] 
    }
    }   
    
    # Create issue
    # response = requests.post(url, headers=headers, auth=auth, json=data)
    # print(response.text)
    print("Simulating Jira issue creation:")
    print("Summary:", data["fields"]["summary"])
    print("")
    
    # Get the issue link
    # response_json = response.json()  
    # print(response.text, "Ticket link:", base_url + response_json["key"])
    issue_key = "SIMULATED-123"  # Replace with a simulated issue key
    print(f"Simulated Ticket link: {base_url + issue_key}")
    
  except StopIteration:
    # print(f"No commits found for {file.path}")
    pass