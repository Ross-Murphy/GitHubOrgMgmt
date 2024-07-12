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
python discovery.py --help
usage: discovery.py [-h] [-r REPO] [-t TEAMSLUG] [-o ORG] [-a {print,write}] [-f FILE]

Crawls a GitHub Organizations repositories and gets their collaborators and team access as yaml

optional arguments:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  Name of repository to inspect. Use "--repo all" for all repos. Warning: All crawls entire ORG tree
  -t TEAMSLUG, --teamslug TEAMSLUG
                        Name slug of GitHub Team to inspect. Use "--team all" for all teams.
  -o ORG, --org ORG     Name of GitHub Organization. Can be read from ENV var GITHUB_ORG_NAME
  -a {print,write}, --action {print,write}
                        print yaml to stdout or write to a file specified
  -f FILE, --file FILE  File name to write yaml output
```


### Interacting with GitHub API via Python
PyGithub Docs : https://pygithub.readthedocs.io/en/stable/reference.html

