import os
import yaml
import argparse

from github import Github
from github import Auth
from github import GithubIntegration
from common import RepoObject, discover_repository, discover_team

ACCESS_TOKEN = os.getenv("GITHUB_PRIVATE_TOKEN") # Read GitHub Personal Access Token (PAT) as an ENV Var
'''
use a bash script like this to set the PAT or do it some other way.
#!/bin/bash
read -s -p "GitHub Access Token:" GITHUB_PRIVATE_TOKEN 
export GITHUB_PRIVATE_TOKEN
'''

parser = argparse.ArgumentParser(
                    prog='GitHub Org discovery',
                    description='Crawls a GitHub Organizations repositories and gets their collaborators and team access as yaml',
                    epilog='')

parser.add_argument('-r','--repo', help='Name of repository to inspect. Use "--repo all" for all repos. Warning: All crawls entire ORG tree')
parser.add_argument('-t','--teamslug', help='Name slug of GitHub Team to inspect. Use "--team all" for all teams.')
parser.add_argument('-o','--org', help='Name of GitHub Organization. Can be read from ENV var GITHUB_ORG_NAME')
parser.add_argument('-a','--action', choices=['print', 'write'], default='print', help='print yaml to stdout or write to a file specified')
parser.add_argument('-f','--file', default='stdout.yml', help='File name to write yaml output')
args = parser.parse_args()

repo_name = args.repo
team_slug = args.teamslug

if args.org:
    ORG_NAME =  args.org
else: 
    ORG_NAME = os.getenv("GITHUB_ORG_NAME") # Read GitHub Org Name ENV Var GITHUB_ORG_NAME

if not ACCESS_TOKEN: 
    print("Exiting: GITHUB_PRIVATE_TOKEN empty or not defined. Set as ENV var GITHUB_PRIVATE_TOKEN")
    exit()

if not ORG_NAME: 
    print("Exiting: GitHub Orgnaization Name not set. Set as ENV var GITHUB_ORG_NAME or use arg --org <GH-ORG-NAME>")
    exit()

# using an access token
auth = Auth.Token(ACCESS_TOKEN)


# First create a Github instance:
# Public Web Github
g = Github(auth=auth)


# # Then play with your Github objects:
# for repo in g.get_user().get_repos():
#     print(repo.name)

if repo_name and repo_name == 'all':
    for repo in g.get_organization(ORG_NAME).get_repos(type='all', sort='pushed'):
        #if str(repo.name) == 'EnterpriseMonitoring':
        if str(repo.name) == 'Standing_Session':    # THIS IS FOR TESTING TO PREVENT WALKING ALL REPOS . Remove me.
            this_repo = discover_repository(repo)
            print(this_repo.get_repo_as_yaml())
elif repo_name:
    repo = g.get_organization(ORG_NAME).get_repo(name=repo_name)
    if repo:
        this_repo = discover_repository(repo)
        print(this_repo.get_repo_as_yaml())

if team_slug and team_slug == 'all':
    for team in g.get_organization(ORG_NAME).get_teams():
        this_team = discover_team(team)
        print(this_team.get_team_as_yaml())

elif team_slug:
    team = g.get_organization(ORG_NAME).get_team_by_slug(slug=team_slug)
    if team:
        this_team = discover_team(team)
        print(this_team.get_team_as_yaml())



# To close connections after use
g.close()