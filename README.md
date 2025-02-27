# GitHubOrgMgmt
Code used for managing a GitHub Organization

---
## Requirements 
To authenticate with GitHub you will need a Personal Access Token (aka PAT).
Read More: [GitHub Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)

Tokens should have the following least priv access rights:
Suggested rights:
`admin:org_hook, public_repo, read:audit_log, read:enterprise, read:gpg_key, read:user, repo:invite, repo:status, repo_deployment, user:email, write:org, write:repo_hook`

Python Modules required.
---

PyGithub - https://pypi.org/project/PyGithub/
PyGithub Docs : https://pygithub.readthedocs.io/en/stable/reference.html

PyYaml - https://pypi.org/project/PyYAML/

argparse - https://docs.python.org/3/library/argparse.html

**How to install.** 
```shell
# clone the repo
git clone https://github.com/Ross-Murphy/GitHubOrgMgmt.git

# create virtual env
python3 -m venv .venv

# activate venv
source .venv/bin/activate

# Update pip
python3 -m pip install --upgrade pip

# Install requirements
python3 -m pip install -r requirements.txt

#  or manually per package
pip install pygithub, pyyaml, argparse

```
***A Python virtual environment is recommended.***

### Discover Organization membership and repository access

```
# python discovery.py --help

usage: discovery.py [-h] [-r REPO] [-t TEAMSLUG] [-o ORG] [-f [FILE]] [-c] [-m]

Crawls a GitHub Organizations repositories and gets their collaborators and team access as yaml

optional arguments:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  Name of repository to inspect. Use "--repo all" for all repos. Warning: All crawls entire ORG tree
  -t TEAMSLUG, --teamslug TEAMSLUG
                        Name slug of GitHub Team to inspect. Use "--team all" for all teams.
  -o ORG, --org ORG     Name of GitHub Organization. Can be read from ENV var GITHUB_ORG_NAME
  -f [FILE], --file [FILE]
                        File name to write yaml output
  -c, --complete        Complete. Used with --repo. Crawl repo branches to discover who's commited. Warning: May trigger Rate Limit
  -m, --members         output list of Organization Members. Only org members can belong to a team
```

### Sample usage and output
#### Setup
```
# Setup your org and GitHub PAT
source set_token.sh
GitHub Organization Name:our-org
GitHub Access Token:****************************

# run discovery of a repo
python3 discovery.py -r AwesomeRepo
```
Output
```yaml
AwesomeRepo: # Name of Repository
  description: This is our awesome GitHub Repo
  html_url: https://github.com/our-org/AwesomeRepo
  type: repo
  direct_collabs: # All explicitly defined collaborators (affilation=direct) sorted by role.  
    write: # Built-in Roles are admin, maintain, write, triage and read.
      - DevDude76
      - CodeGal99
    read:
      - RadProjectMgr
  outside_collabs: # direct collaborators who are outside the organization membership
    write:
      - DevDude76
    read:
      - RadProjectMgr
  teams: # Teams with explicit access. Built-in Roles are admin, maintain, write, triage and read.
    write:
      - team-awesome # team 'slug' is used here rather than the team name
      - team-okay-i-guess
    read:
      - code-users

  contributors: # This is a historic record of who has commited code to any branch. Not Used for setting values in GH
    - CodeGal99
    - DevDude76  
    - AwesomeTeamGuy6 # A commit was found made by a team or org member
    - SomeRetiredBozo # A commit was found made by User who may no longer be a collab or in a team.
    - ExpiredContractor # A commit was found made by User who may no longer be a collab or in a team.

 ```

Discover teams
---
`python3 discovery.py -t team-awesome`

Output
```yaml
team-awesome: # team slug name
  name: Team Awesome # Team name
  description: An Awesome Infrastruture team
  type: team
  html_url: https://github.com/orgs/our-org/teams/team-awesome # URL to the team page
  id: 654321 # GitHub Team ID
  parent_id: 123456 # Id of parent team if exists else = '0'
  parent_name: ParentTeamName # Parent Team Name
  members: # List of team members
    maintainer:
      - TeamLead
    member:  
      - AwesomeTeamGuy6
      - AwesomeTeamMember
      - AwesomeTeamDev
      - SomeoneElseAwesome
```

the -m flag can be added to output the Org membership broken down by Members, Collaborators and pending invites

`python discovery.py -m`

### Modify Org Memberships and repo permissions

`python modify.py --help`
```
usage: modify.py [-h] [-o ORG] [-f FILE] [-t TEAMSLUG] [-m]

Modify a GitHub Organization membership and repository permisisons using yaml input files

optional arguments:
  -h, --help            show this help message and exit
  -o ORG, --org ORG     Name of GitHub Organization. Can be read from ENV var GITHUB_ORG_NAME
  -f FILE, --file FILE  Input yaml file for operation
  -t TEAMSLUG, --teamslug TEAMSLUG
                        Name slug of GitHub Team to modify. Use "--team all" for all teams.
  -m, --members         Set Org memership based on yaml input file
```

### More Reading

#### PyGithub
https://github.com/PyGithub/PyGithub
https://pygithub.readthedocs.io/en/stable/reference.html

#### Github API Docs
https://docs.github.com/en/rest?