from apiclients.DataModel.DataModelBase import DataModelBase


class ApiToken(DataModelBase):
    def __init__(self, user_id, created, token):
        self.user_id = user_id
        self.created = created
        self.token = token


class Organization(DataModelBase):
    def __init__(self, name, domain, id=None):
        self.id = id
        self.name = name
        self.domain = domain


class Permission(DataModelBase):
    def __init__(self, email, role):
        self.email = email
        self.role = role


class RequestTeam(DataModelBase):
    def __init__(self, request_id, team_id, added=None):
        self.request_id = request_id
        self.team_id = team_id
        self.added = added


class Responsibility(DataModelBase):
    def __init__(self, name, id=None):
        self.id = id
        self.name = name


class Role(DataModelBase):
    def __init__(self, name, id=None):
        self.id = id
        self.name = name


class Team(DataModelBase):
    def __init__(self, name, created=None, id=None):
        self.id = id
        self.name = name
        self.created = created


class TeamMember(DataModelBase):
    def __init__(self, team_id, user_id, responsibility, active, added=None):
        self.team_id = team_id
        self.user_id = user_id
        self.responsibility = responsibility
        self.active = active
        self.added = added


class UserWithoutPassword(DataModelBase):
    def __init__(self, first_name, last_name, email, organization_id, id=None, account_status=None, settings=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.organization_id = organization_id
        self.account_status = account_status
        self.settings = settings


class User(UserWithoutPassword):
    def __init__(self, first_name, last_name, email, password, organization_id, id=None, account_status=None, settings=None):
        UserWithoutPassword.__init__(self, first_name, last_name, email, organization_id, id, account_status, settings)
        self.password = password


class UserSession(DataModelBase):
    def __init__(self, user_id, session_id, expires):
        self.user_id = user_id
        self.session_id = session_id
        self.expires = expires

