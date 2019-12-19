"""
Engine API client
"""
import warnings
import requests
from utilities.AnnotellLogger import AnnotellLogger
from api.BaseApi import BaseApi
from api.DataModel.DataModelBase import data_model_factory
from api.DataModel import DataModelUsers, DataModelAnnotation, DataModelDiscussion
from typing import List

logger = AnnotellLogger.get_logger(__name__)


class EngineApi(BaseApi):
    """ Engine API client """

    def __init__(self, token, session=requests.session(), base_url="http://annotell.org:8002/v1/"):
        logger.debug("starting " + str(__name__))
        super().__init__(session, token, base_url)

    def get_requests(self, organization=None):
        if organization:
            requests_assignments_json = self._api_get(f'request/list?organization=true')
        else:
            requests_assignments_json = self._api_get(f'request/list')
        return requests_assignments_json

    def get_next_assignment(self, requestId: int, taskAction: str):
        next_assignment = self._api_get(
            f'assignment/next?requestId={requestId}&taskAction={taskAction}')
        return data_model_factory(DataModelAnnotation.Assignment, next_assignment)

    def create_annotation_policy(self,
                                 annotation_policy: DataModelAnnotation.AnnotationPolicy) -> DataModelAnnotation.AnnotationPolicy:
        annotation_policy_json = annotation_policy.serialize_to_json()
        annotation_policy_json_new_param = self._api_post(
            'policy/create',
            data=annotation_policy_json
        )
        return data_model_factory(DataModelAnnotation.AnnotationPolicy, annotation_policy_json_new_param)

    def create_request_team(self, request_team: DataModelUsers.RequestTeam):
        request_team_json = request_team.serialize_to_json()
        request_team_json_new_param = self._api_post(
            'team/add-to-request',
            data=request_team_json
        )
        return data_model_factory(DataModelUsers.RequestTeam, request_team_json_new_param)

    # --- methods from TeamRoute ---
    def create_team(self, team):
        team_json = team.serialize_to_json()
        team_json_new_param = self._api_post('team/create', data=team_json)
        try:
            return data_model_factory(DataModelUsers.Team, team_json_new_param)
        except KeyError:
            warnings.warn('create team user route does not return proper dict')
            team_json_new_param = {'team': team_json_new_param}
            return data_model_factory(DataModelUsers.Team, team_json_new_param)

    def create_team_member(self, team_member):
        team_member_json = team_member.serialize_to_json()
        team_member_json_new_param = self._api_post(
            'team/create-team-member', data=team_member_json)
        return data_model_factory(DataModelUsers.TeamMember, team_member_json_new_param)

    # --- methods from ProjectRoute ---
    def create_project(self, project):
        project_json = project.serialize_to_json()
        project_json_new_param = self._api_post('project/create', data=project_json)

        return data_model_factory(DataModelAnnotation.Project, project_json_new_param)

    def create_data_type(self, data_type):
        data_type_json = data_type.serialize_to_json()
        data_type_json_new_param = self._api_post(
            "data/create-data-type", data_type_json, with_token=True)
        return data_model_factory(DataModelAnnotation.DataType, data_type_json_new_param)

    def create_data(self, data):
        data_json = data.serialize_to_json()
        data_json_new_param = self._api_post("data/create", data_json)
        return data_model_factory(DataModelAnnotation.Data, data_json_new_param)

    def create_data_list(self, data_list):
        data_list_json = data_list.serialize_to_json()
        data_list_json_new_param = self._api_post("data/create-list", data_list_json)
        return data_model_factory(DataModelAnnotation.DataList, data_list_json_new_param)

    def create_data_list_member(self, data_list_member):
        data_list_member_json = data_list_member.serialize_to_json()
        data_list_member_json_new_param = self._api_post(
            "data/create-list-member", data_list_member_json)
        return data_model_factory(DataModelAnnotation.DataListMember, data_list_member_json_new_param)

    def get_input_types(self):
        # TODO: This does not yet have scala endpoints
        input_types_json = self._api_get('input/get-input-types')
        input_types = [
            data_model_factory(
                DataModelAnnotation.InputType,
                input_type_json
            ) for input_type_json in input_types_json
        ]
        return input_types

    def create_input(self, input):
        input_json = input.serialize_to_json()
        input_json_new_param = self._api_post("input/create", input_json)
        return data_model_factory(DataModelAnnotation.Input, input_json_new_param)

    def create_input_list(self, input_list):
        input_list_json = input_list.serialize_to_json()
        input_list_json_new_param = self._api_post("input/create-list", input_list_json)
        return data_model_factory(DataModelAnnotation.InputList, input_list_json_new_param)

    def create_input_list_member(self, input_list_member):
        input_list_member_json = input_list_member.serialize_to_json()
        input_list_member_json_new_param = self._api_post(
            "input/create-list-member", input_list_member_json)
        return data_model_factory(DataModelAnnotation.InputListMember, input_list_member_json_new_param)

    def create_task_definition(self, task_definition):
        task_def_json = task_definition.serialize_to_json()
        task_def_json_new_param = self._api_post("data/create-task-definition", task_def_json)
        return data_model_factory(DataModelAnnotation.TaskDefinition, task_def_json_new_param)

    def create_guideline(self, guideline):
        guideline_json = guideline.serialize_to_json()
        guideline_json_new_param = self._api_post("data/create-guideline", guideline_json)
        return data_model_factory(DataModelAnnotation.Guideline, guideline_json_new_param)

    def create_request(self, request):
        request_json = request.serialize_to_json()
        request_json_new_param = self._api_post("request/create", request_json)
        return data_model_factory(DataModelAnnotation.Request, request_json_new_param)

    def create_judgement(self, assignment_id, data_id):
        body = {
            "assignmentId": assignment_id,
            "dataId": data_id
        }
        judgement_json_new_param = self._api_post("judgement/create", body)
        return data_model_factory(DataModelAnnotation.Judgement, judgement_json_new_param)

    def complete_assignment(self, assignment_id, data):
        data_json = data.serialize_to_json()
        body = {
            "assignmentId": assignment_id,
            "data": data_json
        }
        completed_assignment_json_new_param = self._api_post("assignment/complete", body)
        return data_model_factory(DataModelAnnotation.Judgement, completed_assignment_json_new_param)

    def create_annotation(self, annotation):
        annotation_json = annotation.serialize_to_json()
        annotation_json_new_param = self._api_post("annotation/create", annotation_json)
        return data_model_factory(DataModelAnnotation.Annotation, annotation_json_new_param)

    def create_task(self, task):
        task_json = task.serialize_to_json()
        task_json_new_param = self._api_post("task/create", task_json)
        return data_model_factory(DataModelAnnotation.Task, task_json_new_param)

    def create_assignment(self, assignment):
        assignment_json = assignment.serialize_to_json()
        assignment_json_new_param = self._api_post("assignment/create", assignment_json)
        return data_model_factory(DataModelAnnotation.Assignment, assignment_json_new_param)

    def create_review(self, review_task):
        review_task_json = review_task.serialize_to_json()
        review_task_json_new_param = self._api_post("task/create-review", review_task_json)
        return data_model_factory(DataModelAnnotation.Task, review_task_json_new_param)

    def create_correct(self, correct_task):
        correct_task_json = correct_task.serialize_to_json()
        correct_task_json_new_param = self._api_post("task/create-correct", correct_task_json)
        return data_model_factory(DataModelAnnotation.Task, correct_task_json_new_param)

    def create_discussion(self, assignment_id, topic_data, judgement_data=None):
        judgement_data_json = judgement_data.serialize_to_json() if judgement_data else None
        topic_data_json = topic_data.serialize_to_json()
        body = {
            "assignmentId": assignment_id,
            "judgementData": judgement_data_json,
            "topicData": topic_data_json
        }
        discussion_json_new_param = self._api_post("discussion/create", body)
        return data_model_factory(DataModelDiscussion.DiscussionWithTopic, discussion_json_new_param)

    def create_discussion_topic(self, discussion_id, data):
        data_json = data.serialize_to_json()
        body = {
            "discussionId": discussion_id,
            "data": data_json
        }
        discussion_topic_json_new_param = self._api_post("discussion/create-topic", body)
        return data_model_factory(DataModelDiscussion.ResolvedDiscussionTopic, discussion_topic_json_new_param)

    def complete_discussion_topic(self, discussion_topic_id, contribution_data):
        data_json = contribution_data.serialize_to_json()
        body = {
            "discussionTopicId": discussion_topic_id,
            "contributionData": data_json
        }
        complete_discussion_topic_json_new_param = self._api_post("discussion/complete-topic", body)
        return data_model_factory(DataModelDiscussion.DiscussionTopicWithContribution,
                                  complete_discussion_topic_json_new_param)

    def create_contribution(self, discussion_topic_id, data, contribution_type):
        data_json = data.serialize_to_json()
        body = {
            "discussionTopicId": discussion_topic_id,
            "data": data_json,
            "contributionType": contribution_type
        }
        contribution_json_new_param = self._api_post("discussion/create-contribution", body)
        return data_model_factory(DataModelDiscussion.ResolvedContribution, contribution_json_new_param)

    # --- so far this is only used for testing AE ---
    def get_tasks_without_active_assignments(self, request_id, task_action=None):

        header = f"requestId={request_id}"
        if task_action:
            header += f"&taskAction={task_action}"

        response = self._api_get(f"task/without-active-assignments?{header}")
        return [
            data_model_factory(DataModelAnnotation.Task, {'task': task_json}) for task_json in response['tasks']
        ]

    def populate_input_list(self, populateInputList: DataModelAnnotation.PopulateInputList):
        body = populateInputList.serialize_to_json()
        discussion_topic_json_new_param = self._api_post("input/populate-input-list", body)
        return discussion_topic_json_new_param

    def create_corrections(self, correct_tasks: List[DataModelAnnotation.CorrectTask]):
        body = [t.serialize_to_json() for t in correct_tasks]

        response = self._api_post("task/create-corrects", body)
        return response

    def create_tasks(self, tasks: List[DataModelAnnotation.Task]):
        body = [t.serialize_to_json() for t in tasks]
        response = self._api_post("task/create-several", body)
        return response
