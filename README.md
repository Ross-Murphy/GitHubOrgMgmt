# GitHubOrgMgmt
Code used for managing a GitHub Organization

---
## Requirements 
To authenticate with GitHub you will need a Personal Access Token (aka PAT).
Read More: [GitHub Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)

Python Modules required.
---

PyGithub - https://pypi.org/project/PyGithub/

PyYaml - https://pypi.org/project/PyYAML/

argparse - https://docs.python.org/3/library/argparse.html

**How to install.** 
```shell
pip install pygithub, pyyaml, argparse
```
***A Python virtual environment is recommended.***

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
  -c, --complete        Complete. Used with --repo. Crawl commits to discover who has commited to repo on any branch
  -m, --members         output list of Organization Members. Only org members can belong to a team
```

### Sample usage and output
```
# Setup your org and GitHub PAT
GitHub Organization Name:our-org
GitHub Access Token:****************************

# run discovery
python discovery.py -r AwesomeRepo
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

Discover team
`python discovery.py -t team-awesome`

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
Discover Organization Membership
the -m flag can be added to output the Org membership broken down by Members, Collaborators and pending invites

`python discovery.py -m`



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

#### Interacting with GitHub API via Python
PyGithub Docs : https://pygithub.readthedocs.io/en/stable/reference.html

