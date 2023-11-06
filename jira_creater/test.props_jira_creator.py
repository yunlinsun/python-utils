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
auth = HTTPBasicAuth(username, api_token)
headers = {
   "Accept": "application/json",
   "Content-Type": "application/json"
}

# Git Setting
repo = git.Repo('/home/steven/project/liferay-portal')
cutoff_date = datetime(2023, 7, 31).replace(tzinfo=timezone.utc)

# Traverse all modifiled files
test_files = []
for file in repo.tree().traverse():
  if file.path.endswith('test.properties') and '/' in file.path:
    test_files.append(file)

# Create issue  
for file in test_files:
  commits = repo.iter_commits(paths=file.path, since=cutoff_date)
  try:
    commit = next(commits)
    date = commit.committed_datetime.strftime("%Y-%m-%d")
    
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
    response = requests.post(url, headers=headers, auth=auth, json=data)
    # print(response.text)
    
    # Get the issue link
    response_json = response.json()  
    print(response.text, "Ticket link:", base_url + response_json["key"])
    
  except StopIteration:
    # print(f"No commits found for {file.path}")
    pass