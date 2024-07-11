import os
import yaml

from github import Github
from github import Auth
from github import GithubIntegration
from common import RepoObject, discover_repository

ORG_NAME = 'sait-ca'
ACCESS_TOKEN = os.getenv("GITHUB_PRIVATE_TOKEN") # Read GitHub Personal Access Token (PAT) as an ENV Var
'''
use a bash script like this to set the PAT or do it some other way.
#!/bin/bash
read -s -p "GitHub Access Token:" GITHUB_PRIVATE_TOKEN 
export GITHUB_PRIVATE_TOKEN
'''

if not ACCESS_TOKEN: 
    print("Exiting: GITHUB_PRIVATE_TOKEN not defined")
    exit()

if not ORG_NAME: 
    print("Exiting: ORG_NAME not defined")
    exit()

# using an access token
auth = Auth.Token(ACCESS_TOKEN)


# First create a Github instance:
# Public Web Github
g = Github(auth=auth)


# # Then play with your Github objects:
# for repo in g.get_user().get_repos():
#     print(repo.name)

for repo in g.get_organization(ORG_NAME).get_repos(type='all', sort='pushed'):
    #if str(repo.name) == 'EnterpriseMonitoring':
    if str(repo.name) == 'Standing_Session':    
        this_repo = discover_repository(repo)
        print(this_repo.get_repo_as_yaml())

# To close connections after use
g.close()