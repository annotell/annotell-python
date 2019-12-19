"""
User API client
"""
import requests

from apiclients.AnnotellLogger import AnnotellLogger
from apiclients.BaseApi import BaseApi
from apiclients.DataModel.DataModelBase import data_model_factory
from apiclients.DataModel import DataModelUsers


logger = AnnotellLogger.get_logger(__name__)


class UserApi(BaseApi):
    """ User API client """

    def __init__(self, email, password, base_url="http://annotell.org:8001/v1/"):
        logger.debug("starting " + str(__name__))
        super().__init__(requests.session(), None, base_url)
        self._login(email, password, base_url)

    # --- methods in OrganizationRoute ---

    def create_organization(self, organization):
        org_json = organization.serialize_to_json()
        new_org_params = self._api_post("organization/create", org_json)
        return data_model_factory(DataModelUsers.Organization, new_org_params)

    # --- methods in UserRoute ---

    def create_user(self, user):
        user_json = user.serialize_to_json()
        new_user_params = self._api_post("users/create", user_json)
        return data_model_factory(DataModelUsers.UserWithoutPassword, new_user_params)

    def add_permission(self, permission):
        permission_json = permission.serialize_to_json()
        print(permission_json)
        self._api_post('users/add-permission', permission_json)
        return 200  # api post will throw an exception if not 200

    def list_users(self):
        users_list_json = self._api_get("users/list")
        users_list = list()
        for i_json in users_list_json:
            users_list.append(data_model_factory(DataModelUsers.User, i_json))
        return users_list

    def list_users_in_organization(self, organization):
        users_list_json = self._api_get("users/list?orgId=" + organization.organization_id)
        users_list = list()
        for i_json in users_list_json:
            users_list.append(data_model_factory(DataModelUsers.User, i_json))
        return users_list

    def list_users_in_same_organization(self):
        users_list_json = self._api_get("users/list-organization")
        users_list = list()
        for i_json in users_list_json:
            users_list.append(data_model_factory(DataModelUsers.User, i_json))
        return users_list

    def update_password(self, user, new_password):
        data = user.serialize_to_json()
        data['newPassword'] = new_password
        new_user_params = self._api_post("users/password", data)
        return data_model_factory(DataModelUsers.UserWithoutPassword, new_user_params)

    def update_settings(self, settings):
        data = {
            "settings": settings
        }
        return self._api_post("users/settings/update", data)

    def get_user(self, user_id=None, email=None):
        if user_id is None and email is None:
            raise TypeError('you have to specify either user id xor email')
        if user_id is not None and email is not None:
            raise TypeError('you have to specify either user id xor email')
        elif user_id is not None:
            user_params = self._api_get("users/?userId=" + str(user_id))
        else:
            user_params = self._api_get("users/?email=" + str(email))

        return data_model_factory(DataModelUsers.UserWithoutPassword, user_params)

    def login(self, user):
        self._login(email=user.email, password=user.password, userapi_url=self.base_url)
        return 200

    def logout(self):
        self._api_post('users/logout', {})
        return 200

    def verify(self):
        self._api_get('users/verify')
