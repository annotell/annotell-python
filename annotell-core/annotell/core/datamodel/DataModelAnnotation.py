import datetime
from apiclients.DataModel.DataModelBase import DataModelBase
from typing import List

class Annotation(DataModelBase):
    def __init__(self, input_id, judgement_id, request_id, confidence=None, work_summary=None, id=None, added=None):
        self.id = id
        self.input_id = input_id
        self.judgement_id = judgement_id
        self.request_id = request_id
        self.confidence = confidence
        self.added = added
        self.work_summary = work_summary


class AnnotationPolicy(DataModelBase):
    def __init__(self, auto_creation, task_flows_name, settings=None, id=None):
        self.id = id
        self.auto_creation = auto_creation
        self.task_flows_name = task_flows_name
        self.settings = settings


class Assignment(DataModelBase):
    def __init__(self, task_id, user_id, continue_chain, priority, settings=None, judgement_id=None, expires=None, completed=None, postpone=False, id=None, created=None):
        self.id = id
        self.created = created
        self.task_id = task_id
        self.user_id = user_id
        self.judgement_id = judgement_id
        self.expires = expires
        self.continue_chain = continue_chain
        self.priority = priority
        self.settings = settings
        self.completed = completed
        self.postpone = postpone


class Data(DataModelBase):
    def __init__(self, data_type_id, content, organization_id, created=None, source=None, external_id=None, id=None):
        self.id = id
        self.data_type_id = data_type_id
        self.content = content
        self.created = created
        self.organization_id = organization_id
        self.source = source
        self.external_id = external_id


class DataList(DataModelBase):
    def __init__(self, organization_id, created=None, id=None):
        self.id = id
        self.organization_id = organization_id
        self.created = created


class DataListMember(DataModelBase):
    def __init__(self, data_list_id, data_id, added_by, added=None, list_index=None, removed=None, removed_by=None, id=None):
        self.id = id
        self.data_list_id = data_list_id
        self.data_id = data_id
        self.added = added
        self.added_by = added_by
        self.list_index = list_index
        self.removed = removed
        self.removed_by = removed_by


class DataType(DataModelBase):
    def __init__(self, name, mime_type, api_route=None, id=None):
        self.id = id
        self.name = name
        self.api_route = api_route
        self.mime_type = mime_type


class Guideline(DataModelBase):
    def __init__(self, published_data_list_id, drafts_data_list_id, id=None):
        self.id = id
        self.published_data_list_id = published_data_list_id
        self.drafts_data_list_id = drafts_data_list_id


class Input(DataModelBase):
    def __init__(self, input_type, data_list_id, id=None):
        self.id = id
        self.input_type = input_type
        self.data_list_id = data_list_id


class InputList(DataModelBase):
    def __init__(self, organization_id, input_type, name, id=None, created=None):
        self.id = id
        self.organization_id = organization_id
        self.input_type = input_type
        self.created = created
        self.name = name


class InputListMember(DataModelBase):
    def __init__(self, input_list_id, input_id, added_by, id=None, list_index=None, removed=None, removed_by=None, added=None):
        self.id = id
        self.input_list_id = input_list_id
        self.input_id = input_id
        self.added = added
        self.added_by = added_by
        self.list_index = list_index
        self.removed = removed
        self.removed_by = removed_by


class InputType(DataModelBase):
    def __init__(self, name):
        self.name = name


class Judgement(DataModelBase):
    def __init__(self, data_id, id=None, created=None):
        self.id = id
        self.created = created
        self.data_id = data_id


class ObjectProperty(DataModelBase):
    def __init__(self, object_property_type, name, pretty_name, description, values, property_settings=None):
        self.object_property_type = object_property_type
        self.name = name
        self.pretty_name = pretty_name
        self.description = description
        self.values = values
        self.property_settings = property_settings


class ObjectType(DataModelBase):
    def __init__(self, object_type_name, pretty_name, description, properties):
        self.object_type_name = object_type_name
        self.pretty_name = pretty_name
        self.description = description
        self.properties = properties


"""
object ObjectTypeName extends Enumeration {
  type ObjectTypeName = Value
  val POINT, LINE, BOUNDING_BOX = Value
}
"""


class Project(DataModelBase):
    def __init__(self, organization_id, title, description, id=None, created=None, deadline=None, status=None):
        self.id = id
        self.created = created
        self.organization_id = organization_id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status


"""
object PropertyType extends Enumeration {
  type PropertyType = Value
  val CATEGORY: annotation.PropertyType.Value = Value
}
"""


class PropertyValue(DataModelBase):
    def __init__(self, property_value_type, name, pretty_name, properties, group=None):
        self.property_value_type = property_value_type
        self.name = name
        self.pretty_name = pretty_name
        self.properties = properties
        self.group = group



"""
object PropertyValueType extends Enumeration {
  type PropertyValueType = Value
  val STRING, BOOLEAN = Value
}
"""


class Request(DataModelBase):
    def __init__(self, project_id, title, description, input_list_id, task_definition_id, guideline_id,
                 active, annotation_policy_id=None, input_creator=None, id=None, created=None):
        self.id = id
        self.created = created
        self.project_id = project_id
        self.title = title
        self.description = description
        self.input_list_id = input_list_id
        self.task_definition_id = task_definition_id
        self.guideline_id = guideline_id
        self.annotation_policy_id = annotation_policy_id
        self.active = active
        self.input_creator = input_creator


class Task(DataModelBase):
    def __init__(self, request_id, input_id, action, priority, builds_on_assignment_id=None, settings=None, id=None, created=None):
        self.id = id
        self.request_id = request_id
        self.created = created
        self.input_id = input_id
        self.action = action
        self.builds_on_assignment_id = builds_on_assignment_id
        self.priority = priority
        self.settings = settings


class ReviewTask(Task):
    def __init__(self, builds_on_assignment_id, priority, request_id=None, settings=None):
        super().__init__(
            request_id=request_id,
            input_id=None,
            action='review',
            priority=priority,
            builds_on_assignment_id=builds_on_assignment_id,
            settings=settings,
            id=None,
            created=None
        )


class CorrectTask(Task):
    def __init__(self, builds_on_assignment_id, priority, request_id=None, settings=None):
        super().__init__(
            request_id=request_id,
            input_id=None,
            action='correct',
            priority=priority,
            builds_on_assignment_id=builds_on_assignment_id,
            settings=settings,
            id=None,
            created=None
        )
"""
object TaskAction extends Enumeration {
  type TaskAction = Value
  val ANNOTATE, REVIEW, CORRECT, NEGOTIATE = Value
}

object TaskAllocationChain extends Enumeration {
  type TaskAllocationChain = Value
  val AnnotateCorrect, AnnotateCorrectReview = Value
}
"""


class TaskDefinition(DataModelBase):
    def __init__(self, published_data_list_id, drafts_data_list_id, id=None):
        self.id = id
        self.published_data_list_id = published_data_list_id
        self.drafts_data_list_id = drafts_data_list_id


class TaskFlow(DataModelBase):
    def __init__(self, name, id=None):
        self.id = id
        self.name = name


class WorkSummary(DataModelBase):
    def __init__(self, data_id, id=None):
        self.id = id
        self.data_id = data_id


class InputListInfo(DataModelBase):
    def __init__(self, added_by: int, data_owner: int, input_type: str, input_list_id: int):
        self.added_by = added_by
        self.data_owner = data_owner
        self.input_type = input_type
        self.input_list_id = input_list_id

class InputListCreationSpec(DataModelBase):
    def __init__(self, index_input_list: bool, index_data_list: bool):
        self.index_input_list = index_input_list
        self.index_data_list = index_data_list

class InputData(DataModelBase):
    def __init__(self, datas: List[Data]):
        self.datas = datas

class PopulateInputList(DataModelBase):
    def __init__(self, info: InputListInfo, spec: InputListCreationSpec, input_datas: List[InputData]):
        self.info = info
        self.spec = spec
        self.input_datas = input_datas

class ActiveWorkingTimeWithInfo(DataModelBase):
    def __init__(self, active_working_time: int, number_of_assignments: int, number_of_assignments_missing: int):
        self.active_working_time = active_working_time
        self.number_of_assignments = number_of_assignments
        self.number_of_assignments_missing = number_of_assignments_missing