import os
import sys
import yaml
import argparse

from github import Github
from github import Auth
from common import *

ACCESS_TOKEN = os.getenv("GITHUB_PRIVATE_TOKEN") # Read GitHub Personal Access Token (PAT) as an ENV Var
'''
use a bash script like this to set the PAT or do it some other way.
#!/bin/bash
read -s -p "GitHub Access Token:" GITHUB_PRIVATE_TOKEN 
export GITHUB_PRIVATE_TOKEN
'''

parser = argparse.ArgumentParser(
                    prog=os.path.basename(sys.argv[0]),
                    description='Crawls a GitHub Organizations repositories and gets their collaborators and team access as yaml',
                    epilog='')

parser.add_argument('-r','--repo', help='Name of repository to inspect. Use "--repo all" for all repos. Warning: All crawls entire ORG tree')
parser.add_argument('-t','--teamslug', help='Name slug of GitHub Team to inspect. Use "--team all" for all teams.')
parser.add_argument('-o','--org', help='Name of GitHub Organization. Can be read from ENV var GITHUB_ORG_NAME')
parser.add_argument('-f','--file', nargs='?', const='stdout.yml', help='File name to write yaml output')
parser.add_argument('-c','--complete', action="store_true",help='Complete. Used with --repo. Crawl commits to discover who has commited to repo on any branch')
parser.add_argument('-m','--members', action="store_true",help='output list of Organization Members. Only org members can belong to a team')
args = parser.parse_args()

### Setup Vars from Args
repo_name = args.repo
team_slug = args.teamslug
discover_contributors = args.complete
discover_members = args.members
print_yaml_doc = False # Default option is print to stdout only.  --file will allow write to file.

if args.file: # We have set file output to true with --file
    print_yaml_doc = True
    output_file = args.file

if args.org: # --org ORG_NAME was set on cli
    ORG_NAME =  args.org
else: 
    ORG_NAME = os.getenv("GITHUB_ORG_NAME") # Read GitHub Org Name ENV Var GITHUB_ORG_NAME

if not ACCESS_TOKEN: # Exit if no token set
    print("Exiting: GITHUB_PRIVATE_TOKEN empty or not defined. Set as ENV var GITHUB_PRIVATE_TOKEN")
    exit()

if not ORG_NAME: # Assert ORG_NAME is set
    print("Exiting: GitHub Orgnaization Name not set. Set as ENV var GITHUB_ORG_NAME or use arg --org <GH-ORG-NAME>")
    exit()
### End Var setup

# Set GitHub access token
auth = Auth.Token(ACCESS_TOKEN)

# Create GitHub Instance with Auth Token
g = Github(auth=auth)

# Start Output gathering.
if print_yaml_doc: # If we are dumping to a file prepend with the yaml doc string ---
    file_output = "---\n"
    print(file_output, end='')

if repo_name and repo_name == 'all': # arg --repo all
    for repo in g.get_organization(ORG_NAME).get_repos(type='all', sort='pushed'):
        this_repo = discover_repository(repo, discover_contributors)
        repo_as_yaml = this_repo.get_repo_as_yaml()
        if print_yaml_doc:
            file_output += repo_as_yaml           
        print(this_repo.get_repo_as_yaml(), end='') # end = '' because Yaml linters get fussy about newlines. 
        # They want a file to end with exactly 1 and the yaml.dump already has one
elif repo_name: # arg --repo RepoName
    repo = g.get_organization(ORG_NAME).get_repo(name=repo_name)
    if repo:
        this_repo = discover_repository(repo, discover_contributors)
        repo_as_yaml = this_repo.get_repo_as_yaml()
        if print_yaml_doc:
            file_output += repo_as_yaml                
        print(repo_as_yaml, end='')

if team_slug and team_slug == 'all': # arg --team all
    for team in g.get_organization(ORG_NAME).get_teams():
        this_team = discover_team(team)
        team_as_yaml = this_team.get_team_as_yaml()
        if print_yaml_doc:
            file_output += team_as_yaml
        print(team_as_yaml, end='')

elif team_slug: # arg --team teamslug
    team = g.get_organization(ORG_NAME).get_team_by_slug(slug=team_slug)
    if team:
        this_team = discover_team(team)
        team_as_yaml = this_team.get_team_as_yaml()
        if print_yaml_doc:
            file_output += team_as_yaml
        print(team_as_yaml, end='')

if discover_members: # arg -m was called. Get Og Membership Structure.
    org = g.get_organization(ORG_NAME)
    if org:
        this_org = discover_org(org)
        org_yaml = this_org.get_org_members_as_yaml()
        if print_yaml_doc:
            file_output += org_yaml
        print(org_yaml, end='')
        

if print_yaml_doc:
    f = open(output_file, "a") # default file is stdout.yml. Override with --file
    f.write(file_output)
    f.close()


# To close connections after use
g.close()