import yaml

class RepoObject:
    '''
    Class for representing a GitHub repo as yaml or as a python dict
        Obj Strcuture: 
             self.name: {
                "description": str(self.description),
                "html_url": str(self.html_url),
                "direct_collabs": list(self.direct_collabs),
                "outside_collabs": list(self.outside_collabs),
                "teams": list(self.teams),
                "contributors": list(self.contributors)
            }

    # Yaml Structure of a sample repo
    ```
    SomeAwesomeRepo:
        description: 'A repo with some code in it that helps us be Awesome'
        html_url: 'https://github.com/org-name/SomeAwesomeRepo'
        direct_collabs: # collaborator affiliation = direct 
        - CoolCoder99
        - DevDude76
        outside_collabs: # collaborator affiliation = outside
        - CoolCoder99
        teams: # Teams with explicit access defined. These should be GitHub team 'slugs' and not the team name. Slugs are easier to work with.
        - team-awesome
        - team-okay-i-guess
        contributors: # 'Visible' GitHub Login those of who have authored commits on any branch this in this repo
        - CoolCoder99
        - DevDude76 
        - AwesomeTeamGuy6 # A commit was found made by a team or org member
        - SomeRetiredBozo # User who's made commits but may no longer be a collab or in a team.
        - ExpiredContractor # User who's made commits but may no longer be a collab or in a team.
    ```    
    '''  

    def __init__(self, name) -> None:
        self.name: str = name
        self.description: str = None
        self.html_url: str = None
        self.direct_collabs: set = set()
        self.outside_collabs: set = set()
        self.teams: set = set()
        self.contributors: set = set()

    def add_contributor(self, login: str):
        ''' 
        Add github login to list of contributors.
        This value is useful only as a discovery item. Meaning it is populated by checking commits made on a branch.
        Setting this here would be meaningless.
        '''
        self.contributors.add(login)

    def add_direct_collabs(self, login: str):
        ''' Add github login to list of direct collaborators'''
        self.direct_collabs.add(login)

    def add_outside_collabs(self, login: str):
        ''' Add github login to list of outside collaborators'''
        self.outside_collabs.add(login)

    def add_team(self, team_slug: str):
        '''
        Add a team name expressed as a github slug and adds it to the list.
        '''
        self.teams.add(team_slug)

    def remove_team(self, team_slug: str):
        '''
        Remove a team name identified as a github slug from the team on this object.
        '''
        self.teams.discard(team_slug) 

    def get_repo_structure(self) -> dict:
        '''
        Returns a repository object which is a dict of lists and strings.
        Interally the class uses set() for the lists to prevent duplicates
        However when exported they are converted to simple list() "arrays" for yaml etc.
        '''
        return {
            self.name: {
                "description": str(self.description),
                "html_url": str(self.html_url),
                "direct_collabs": list(self.direct_collabs),
                "outside_collabs": list(self.outside_collabs),
                "teams": list(self.teams),
                "contributors": list(self.contributors)
            }
        }

    def get_repo_as_yaml(self) -> str:
        '''
        Returns repo object as a yaml formated string.      
        '''
        return yaml.safe_dump(self.get_repo_structure(), sort_keys=False)

class TeamObject:
    '''
    Class for representing a GitHub Team membership as yaml.     
        TeamObj Structure {
            team.slug: {
                "name": str(self.name),
                "description": str(self.description),
                "html_url": str(self.html_url),
                "id": int(self.id),
                "parent_id": str(self.parent.id),
                "parent_name": str(self.parent.name),                               
                "members": list(self.members)
            }
        }    
    '''
    
    def __init__(self, slug) -> None:
        self.slug:str = slug
        self.name:str = None
        self.id: int = 0
        self.html_url:str =  None
        self.description:str = None
        self.parent_id:int = 0
        self.parent_name:str = None
        self.members:set = set()


    def add_member(self, login):
        self.members.add(login)

    def remove_member(self, login):
        self.members.difference(login)

    def get_team_structure(self) -> dict:
        '''
        Returns a team object which is a dict of lists, strings and int for id.
        Interally the class uses set() for the lists to prevent duplicates
        However when exported they are converted to simple list() "arrays" for yaml etc.
        '''
        return {
            self.slug: {
                "name": str(self.name),
                "description": str(self.description),
                "html_url": str(self.html_url),
                "id": int(self.id),
                "parent_id": int(self.parent_id),
                "parent_name": str(self.parent_name),                               
                "members": list(self.members)
            }
        }
    def get_team_as_yaml(self) -> str:
        '''
        Returns team object as a yaml formated string.      
        '''
        return yaml.safe_dump(self.get_team_structure(), sort_keys=False)


def discover_team(team)-> TeamObject:
    this_team = TeamObject(slug=team.slug)
    this_team.name = team.name
    this_team.description = team.description
    this_team.id = team.id
    this_team.html_url = team.html_url
    if team.parent:
        this_team.parent_id = team.parent.id
        this_team.parent_name = team.parent.name
    for member in team.get_members():
        this_team.add_member(member.login)

    return this_team

def discover_repository(repo) ->RepoObject:
    this_repo = RepoObject(name=repo.name)
    this_repo.html_url = repo.html_url

    for collab in repo.get_collaborators(affiliation='direct'):
        this_repo.add_direct_collabs(collab.login)    

    for collab in repo.get_collaborators(affiliation='outside'):
        this_repo.add_outside_collabs(collab.login)

    for team in repo.get_teams():
        this_repo.add_team(team.slug)

    branches = repo.get_branches()
    authors = set()
    for branch in branches:
        commits = repo.get_commits(sha=branch.name)
        for commit in commits:
            authors.add(commit.author.login)
    for user in authors:
        #print(f"{user.name},{user.login}")
        this_repo.add_contributor(str(user))            
    return this_repo
