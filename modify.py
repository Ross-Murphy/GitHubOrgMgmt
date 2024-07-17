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
                    description='Modify a GitHub Organization membership and repository permisisons using yaml input files',
                    epilog='')

parser.add_argument('-o','--org', help='Name of GitHub Organization. Can be read from ENV var GITHUB_ORG_NAME')
parser.add_argument('-f','--file', help='Input yaml file for operation')
parser.add_argument('-t','--teamslug', help='Name slug of GitHub Team to modify. Use "--team all" for all teams.')
parser.add_argument('-m','--members', action="store_true", help='Set Org memership based on yaml input file')
args = parser.parse_args()

### Setup Vars from Args

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

input_file = args.file
team_slug = args.teamslug

### End Var setup

# Set GitHub access token
auth = Auth.Token(ACCESS_TOKEN)

# Create GitHub Instance with Auth Token
gh = Github(auth=auth)


def get_yaml_from_file(file_name)->dict:
    with open(file_name, 'r') as file:
        input_data = yaml.safe_load(file)
    return input_data

if input_file:
    try:
        input_data = get_yaml_from_file(input_file)
    except Exception as err:
        print(err)
        exit()
   

#Process Teams 
if team_slug and team_slug == 'all': # arg --team all
    pass

elif team_slug: # arg --team teamslug  
    
    try: # Try Load proposed team from yaml
        input_team_membership = input_data[team_slug]['members']
    except KeyError:
        print(f"Fatal Error: Team Slug '{team_slug}' not found in dict loaded from yaml input file '{input_file}'"  )
        exit()
    gh_team = gh.get_organization(ORG_NAME).get_team_by_slug(slug=team_slug)
    set_team_membership_from_yaml(gh, gh_team, input_team_membership)

# Close github connections after use
gh.close()