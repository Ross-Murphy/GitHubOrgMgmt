import github.Organization
import github.Team
import yaml
import github
from github.GithubException import UnknownObjectException

class IndentDumper(yaml.Dumper):
    '''
    This fixes pyyaml yaml.dump indentation
    By default, PyYAML indent list items on the same level as their parent.
    This will cause lots of linters to fail.
    See here : https://reorx.com/blog/python-yaml-tips/
    Note that Dumper cannot be passed to yaml.safe_dump which has its owner dumper class defined.
    yaml.safe_dump() is recommended when you need to ensure security and avoid the risk of arbitrary code execution 
    when dealing with data from untrusted sources. 
    Use yaml.dump() when you need to serialize complex or custom Python objects and are confident that the data being serialized is safe.
    '''
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


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
        self.type: str = 'repo'
        self.html_url: str = None
        self.direct_collabs: dict = {}
        self.outside_collabs: dict = {}
        self.teams: dict = {}
        self.contributors: set = set()

    def add_contributor(self, login: str)-> None:
        ''' 
        Add github login to list of contributors.
        This value is useful only as a discovery item. Meaning it is populated by checking commits made on a branch.
        Setting this here would be meaningless.
        '''
        self.contributors.add(login)

    def add_direct_collabs(self, login: str, role: str)-> None:
        ''' Add github login to list of direct collaborators'''
        if role in self.direct_collabs.keys():
            current_direct_collabs = set(self.direct_collabs[role]) # convert list to set to avoid duplicates
            current_direct_collabs.add(login)           
            self.direct_collabs[role] = list(current_direct_collabs) # Convert set back to list for yaml export
        else:
            self.direct_collabs[role] = list() # Make empty list since the role set is empty so we don't need to worry about dupes
            self.direct_collabs[role].append(login)

    def add_outside_collabs(self, login: str, role: str)-> None:
        ''' Add github login to list of outside collaborators'''
        if role in self.outside_collabs.keys():
            current_outside_collabs = set(self.outside_collabs[role]) # convert list to set to avoid duplicates
            current_outside_collabs.add(login)           
            self.outside_collabs[role] = list(current_outside_collabs) # Convert set back to list for yaml export
        else:
            self.outside_collabs[role] = list() # Make empty list since the role set is empty so we don't need to worry about dupes
            self.outside_collabs[role].append(login)

    def add_team(self, team_slug: str, role: str)-> None:
        '''
        Add a team name expressed as a github slug and adds it to the list.
        '''
        #self.teams.add(team_slug)
        if role in self.teams.keys():
            current_teams = set(self.teams[role]) # convert list to set to avoid duplicates
            current_teams.add(team_slug)
            self.teams[role] = list(current_teams) # Convert set back to list for yaml export
        else:
            self.teams[role] = list() # Make empty list since the role set is empty so we don't need to worry about dupes
            self.teams[role].append(team_slug) 

    def remove_team(self, team_slug: str)-> None:
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
                "type": str(self.type),
                "direct_collabs": self.direct_collabs,
                "outside_collabs": self.outside_collabs,
                "teams": self.teams,
                "contributors": list(self.contributors)
            }
        }

    def get_repo_as_yaml(self) -> str:
        '''
        Returns repo object as a yaml formated string.      
        '''
        return yaml.dump(self.get_repo_structure(), sort_keys=False, Dumper=IndentDumper)


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
        self.type:str = 'team'
        self.id: int = 0
        self.html_url:str =  None
        self.description:str = None
        self.parent_id:int = 0
        self.parent_name:str = None
        self.members:dict = {}


    def add_member(self, login: str, role: str = 'member')-> None:
#        self.members.add(login)
        if role in self.members.keys():
            current_members = set(self.members[role]) # convert list to set to avoid duplicates
            current_members.add(login)
            self.members[role] = list(current_members) # Convert set back to list for yaml export
        else:
            self.members[role] = list()   
            self.members[role].append(login)

    def remove_member(self, login)-> None:
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
                "type": str(self.type),
                "html_url": str(self.html_url),
                "id": int(self.id),
                "parent_id": int(self.parent_id),
                "parent_name": str(self.parent_name),                               
                "members": self.members
            }
        }
    def get_team_as_yaml(self) -> str:
        '''
        Returns team object as a yaml formated string.      
        '''
        return yaml.dump(self.get_team_structure(), sort_keys=False, Dumper=IndentDumper)


class OrgObject:
    '''
    Class for representing a GitHub Org membership as Yaml
    '''
    def __init__(self, login) -> None:
        self.login = login
        self.name: str = None
        self.description: str = None
        self.members_list = set()
        self.outside_collaborators = set()
        self.invitations = set()
        self.type: str = 'org'

    def add_member(self, login)-> None:
        self.members_list.add(login)

    def remove_member(self, login)-> None:
        self.members_list.discard(login)

    def add_collab(self, login)-> None:
        self.outside_collaborators.add(login)

    def remove_collab(self, login)-> None:
        self.outside_collaborators.discard(login)

    def add_invited_user(self, login)-> None: # This is pulled from GH and not something we intend to set here.
        self.invitations.add(login)

    def get_org_member_structure(self) -> dict:
        '''
        Returns the structure of the Organization membership as a dict of lists and str
            self.name: {
                "name": str(self.name),
                "description": str(self.description),
                "members": list(self.members_list),
                "collaborators": list(self.outside_collaborators),
                "pending_invites": list(self.invitations)
            }
        '''
        return {
            self.login: {
                "name": str(self.name),
                "description": str(self.description),
                "type": str(self.type),
                "members": list(self.members_list),
                "collaborators": list(self.outside_collaborators),
                "pending_invites": list(self.invitations)
            }
        }

    def get_org_members_as_yaml(self) -> str:
        '''
        Returns Org Membership object as a yaml formated string.      
        '''
        return yaml.dump(self.get_org_member_structure(), sort_keys=False, Dumper=IndentDumper)


def discover_org(org:github.Organization.Organization)-> OrgObject:
    this_org = OrgObject(org.login)
    this_org.name = org.name
    this_org.description = org.description
    member_list = org.get_members()
    outside_collaborators = org.get_outside_collaborators()
    invitations = org.invitations()

    if member_list:
        for member in member_list:
            this_org.add_member(member.login)
    if outside_collaborators:
        for collab in outside_collaborators:
            this_org.add_collab(collab.login)

    if invitations:
        for invited in invitations:
            this_org.add_invited_user(invited.login)

    return this_org


def convert_org_member_to_collab( org:github.Organization, login:str)->None:
    members = org.get_members()
    for member in members:
        if member.login == login:
            org.convert_to_outside_collaborator(member)


def discover_team(team:github.Team.Team)-> TeamObject:
    this_team = TeamObject(slug=team.slug)
    this_team.name = team.name
    this_team.description = team.description
    this_team.id = team.id
    this_team.html_url = team.html_url
    if team.parent:
        this_team.parent_id = team.parent.id
        this_team.parent_name = team.parent.name
    for member in team.get_members(role='maintainer'):
        this_team.add_member(member.login, role='maintainer')

    for member in team.get_members(role='member'):
        this_team.add_member(member.login, role='member')

    return this_team


def discover_repository(repo:github.Repository.Repository, discover_contributors:bool = False, branch:str=None) ->RepoObject:
    this_repo = RepoObject(name=repo.name)
    this_repo.html_url = repo.html_url
    # Add list of direct collaborators and their role
    for collab in repo.get_collaborators(affiliation='direct'):
        role = repo.get_collaborator_permission(collab)
        this_repo.add_direct_collabs(login=collab.login, role=role)    
    # Add list of outside collaborators and their role
    for collab in repo.get_collaborators(affiliation='outside'):
        role = repo.get_collaborator_permission(collab)
        this_repo.add_outside_collabs(login=collab.login, role=role)

    for team in repo.get_teams():
        perm = team.get_repo_permission(repo)
        # Example of custom type <class 'github.Permissions.Permissions'>
        # The following is considered 'Write' permission in the GitHub UI
        # Permissions(triage=True, push=True, pull=True, maintain=False, admin=False)
        if perm.admin == True:
            this_repo.add_team(team.slug, 'admin')
        elif perm.maintain == True:
            this_repo.add_team(team.slug, 'maintain')
        elif perm.push == True:
            this_repo.add_team(team.slug, 'write') # Permissions(triage=True, push=True, pull=True, maintain=False, admin=False)
        elif perm.triage == True:
            this_repo.add_team(team.slug, 'triage')
        elif perm.pull == True:
            this_repo.add_team(team.slug, 'read')

    if discover_contributors: # Complete discovery was requested
        authors = set()
        if not branch:
            #branches = [repo.get_branch(repo.default_branch)]
            contribs = repo.get_contributors() # Save a few hundred API calls by using builtin get_contributors method if default branch requested
            for author in contribs:
                this_repo.add_contributor(str(author.login)) 
        else:    
            if branch == 'all': # Get all branches and commits. API rate limit can be hit here. Improvement required
                branches = repo.get_branches()           
            elif branch:
                branches = [repo.get_branch(branch)]    
            
            for branch in branches:
                commits = repo.get_commits(sha=branch.name)
                for commit in commits:
                    authors.add(commit.author.login)
            for user in authors:
                #print(f"{user.name},{user.login}")
                this_repo.add_contributor(str(user))            
    return this_repo


def github_team_exists(org:github.Organization, team_slug:str)-> bool:
    try:
        team = org.get_team_by_slug(team_slug)
        return True
    except UnknownObjectException as ex:
        return False


def get_github_team_by_name(org:github.Organization, team_name:str)-> github.Team.Team:
    teams_list = org.get_teams()
    for team in teams_list:
        if team.name == team_name:
            return team
    return None    


def create_github_team(org:github.Organization, team_name:str, description:str = None, parent_team_id:int = 0, privacy:str = 'closed' )-> github.Team.Team:
    team = get_github_team_by_name(org=org, team_name=team_name)
    if team:
        #print (f'[WARNING] Team Exists but creation requested. Action Taken is None. Team Slug: {team.slug}')
        return team   
    else:
        if parent_team_id > 0:
            team = org.create_team(name= team_name, description=description, parent_team_id=parent_team_id, privacy=privacy)
        else: 
            team = org.create_team(name= team_name, description=description, privacy=privacy)         
    if team:
        print (f'[CHANGED] Created Team {team_name} - GitHub Team Slug: {team.slug}')
        return team
    else:
        return None
    

def update_team_membership(gh:github.Github, team:github.Team.Team, login:str, action:str, role:str = 'member')-> bool:
    '''
    Add or remove a login from a GitHub team or change roles ie. member or maintainer.
    ---
    gh =  a GitHub class instance authenticated and connected to GitHub
    team = team object of type github.Team.Team
    login:str = <GitHubLogin>  The github login to operate with.
    action:str = [add | del]  Add or remove member from team
    role:str = [member(default) | maintainer]  Github roles

    Example:
    ```
    team = gh.get_organization(ORG_NAME).get_team_by_slug(team-awesome)
    update_team_membership(gh, team, DevDude99, 'add', 'maintainer')
    ```

    '''
    try: 
        gh_user_obj = gh.get_user(login)
    except github.GithubException as err:
        print(err) 
        print(f"Error: GitHub login not found: {login}")           
        return False
    
    if not gh_user_obj: # Something else happend that returned 'None' for user but did not throw an exception
        print(f"Warning: GitHub login not found: {login}")           
        return False
    
    if action == 'add':
        try: 
            if team.has_in_members(gh_user_obj) and ( team.get_team_membership(gh_user_obj) ).role == role:
                #print(f"Debug: {gh_user_obj.login} has role {role} in team {team.name}")
                return True
            else:
                # add member
                team.add_membership(gh_user_obj, role)
                return True
        except github.GithubException as err:
            print(err) 
            print(f"GitHub Error: Returned when checking team role or adding login: {login} to role: {role} in team: {team.name}")           
            return False
        
    elif action == 'del':
        try:
            team.remove_membership(gh_user_obj)
        except github.GithubException as err:
            print(err)
            print(f"GitHub Error: Returned when removing login: {login} from team: {team.name}")                       
            return False
        return True


def set_team_membership_from_yaml(gh:github.Github, gh_team:github.Team.Team, input_team_membership:dict)->None:
    '''
    Modify a GitHub Team membership based on a structure loaded from a YAML input file.
    The GitHub team object is an input to this function so it is assumed to exist in GitHub.

    gh =  a GitHub class instance authenticated and connected to GitHub
    team = team object of type github.Team.Team
    gh_team = team object of type github.Team.Team 
    input_team_membership = Team membership structure loaded from an input file
    
    Example of a GitHug team object
    gh_team = gh.get_organization(ORG_NAME).get_team_by_slug(team-awesome)
    
    # Sample team structure in yaml

        ```yaml 
        team-awesome:
            name: Team Awesome
            description: A very awesome team
            type: team
            html_url: https://github.com/orgs/my-org/teams/team-awesome
            id: 654321
            parent_id: 123456
            parent_name: ITDept
                members:
                    maintainer:
                        - TeamLead
                        - TeamGitGuru
                    member:
                        - TeamMember1
                        - TeamMember2
        ```
    '''
        # Poll GH to see if team exists and what changes need to be made.
    #gh_team = gh.get_organization(ORG_NAME).get_team_by_slug(slug=team_slug)

    team_slug = gh_team.slug
    team_struct = discover_team(gh_team) # Get current team into TeamObject structure
    current_team_membership = team_struct.get_team_structure()[team_slug]['members'] # Get the membership structure
    for role in current_team_membership.keys(): # Check
        for login in current_team_membership[role]:
            if role not in input_team_membership or login not in input_team_membership[role]: # If Role empty or member does not have that role 
                #print( f"must remove {login}")
                if update_team_membership(gh, gh_team, login, 'del'):
                    print (f'[CHANGED] Login: {login} removed from Team: {gh_team.slug}')
                else:
                    print (f'[WARNING] Something prevented removing Login: {login} from Team: {gh_team.slug}')
    for role in input_team_membership.keys():
        for login in input_team_membership[role]:
            if role not in current_team_membership or login not in current_team_membership[role]: # If Role empty or member does not have that role
                #print(f'must add {login}')
                if update_team_membership(gh, gh_team, login, 'add', role=role):
                    print (f'[CHANGED] Login: {login} added to Team: {gh_team.slug} with Role: {role}')
                else:
                    print (f'[WARNING] Something prevented adding Login: {login} to Team: {gh_team.slug} with Role: {role}')                        


def set_org_membership_from_yaml(gh:github.Github, org:github.Organization, input_org:dict)->None:
    '''
    Modify a Github Organizaiton membership based on dict input.
    '''
    # Poll github and compare current membership with desired membership loaded from yaml file.
    ## Current Org Obj is what is currently configured in GitHub
    current_org_obj = discover_org(org).get_org_member_structure()[org.login]
    current_org_members:list = current_org_obj['members']
    current_org_collabs:list = current_org_obj['collaborators']
    current_org_pending_invites:list = current_org_obj['pending_invites']

    ## Imported Org Obj is what is imported from Yaml
    imported_org_obj = input_org[org.login]
    imported_org_members:list = imported_org_obj['members']
    imported_org_collaborators:list = imported_org_obj['collaborators']

    ## Ensure imported member is in either current members list or pending_invites.
    for org_member in imported_org_members:
        # If imported org member is not current a member but is already invited skip them and advise user.
        if org_member not in current_org_members and org_member in current_org_pending_invites:
            print(f'[UNCHANGED] Login: {org_member} has pending invite to GitHub Org: {org.login}') 
            continue
        # If imported org member is not yet an org member and has no pending invite, 
        if org_member not in current_org_members and org_member not in current_org_pending_invites:
            # invite the member to the org
            try:
                user_obj = gh.get_user(login=org_member) # Get the NamedUser obj
                org.add_to_members(member=user_obj, role='member')
                print(f'[CHANGED] Login: {org_member} was invited to GitHub Org: {org.login}')
            except UnknownObjectException as ex:
                print(f'[UNCHANGED] GitHub reports the provided login: {org_member} was not found in GitHub')
                continue    
            

    ## Check imported collaborators list against current org membership
    for collab in imported_org_collaborators:
        # if collab is in current collab list and not in org members, they're good, skip them
        if collab in current_org_collabs and collab not in current_org_members:
            continue
        # if imported collaborator is currently an org member, convert to outside collaborator
        if collab in current_org_members and collab not in imported_org_members:
            try:
                user_obj = gh.get_user(login=collab) # Get the NamedUser obj
                org.convert_to_outside_collaborator(user_obj)
                print(f'[CHANGED] Login: {collab} was converted to outside collaborator for GitHub Org: {org.login}')
            except UnknownObjectException as ex:
                print(f'[UNCHANGED] GitHub reports the provided login: {org_member} was not found')
                continue
        # If the collab is not in the current collaborators warn the user.
        # if collab not in current_org_collabs and collab not in imported_org_members :
        #     print(f'[WARNING] Login: {collab} is listed in import data but not found in Org collaborators. Is your import data up-to-date and correct?')

    ## Check current org membership and remove from org those missing in the import.
    for org_member in current_org_members:
        # If a current org member is not in the list of imported org members, remove them from the org
        if org_member not in imported_org_members and org_member not in imported_org_collaborators :
            try:
                user_obj = gh.get_user(login=org_member) # Get the NamedUser obj
                #TESTING# org.remove_from_membership(user_obj)
                print(f'[CHANGED] Login: {org_member} was removed from GitHub Org: {org.login}')    
            except UnknownObjectException as ex: # Handle case where user account been deleted or is no longer an Org Member
                # Debugging code here: This may serve as feeding a loging function later.
                # template = "A GitHub exception of type {0} occurred. Arguments:\n{1!r}"
                # message = template.format(type(ex).__name__, ex.args)
                # print (message)
                print(f'[UNCHANGED] GitHub reports the provided login: {org_member} was not found in GitHub or in Org')
                continue    
    # Check current collaborators and remove those missing from import
    for collab in current_org_collabs:
        # remove outside collaborators no longer listed in import as org members or collabs.
        # Removing a user from this list will remove them from all the organization's repositories.
        if collab not in imported_org_collaborators and collab not in imported_org_members:
            try:
                user_obj = gh.get_user(login=collab) # Get the NamedUser obj
                org.remove_outside_collaborator(user_obj)
                print(f'[CHANGED] Login: {collab} was removed as Outside Collaborator from GitHub Org: {org.login}') 
            except UnknownObjectException as ex:  
                print(f'[UNCHANGED] GitHub reports the provided login: {org_member} was not found in GitHub')
                continue