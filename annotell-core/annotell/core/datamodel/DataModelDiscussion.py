from apiclients.DataModel.DataModelBase import DataModelBase


class Discussion(DataModelBase):
    def __init__(self, assignment_id, judgement_id=None, created=None, id=None):
        self.id = id
        self.assignment_id = assignment_id
        self.judgement_id = judgement_id
        self.created = created


class DiscussionContributor(DataModelBase):
    def __init__(self, discussion_id, user_id, id=None):
        self.id = id
        self.discussion_id = discussion_id
        self.user_id = user_id


class DiscussionTopic(DataModelBase):
    def __init__(self, data_id, discussion_id, created=None, completed=None, id=None):
        self.id = id
        self.data_id = data_id
        self.discussion_id = discussion_id
        self.created = created
        self.completed = completed


class ResolvedDiscussionTopic(DataModelBase):
    def __init__(self, discussion_topic, contributions, data, number_of_messages, number_of_unseen_messages):
        self.discussion_topic = discussion_topic
        self.contributions = contributions
        self.data = data
        self.number_of_messages = number_of_messages
        self.number_of_unseen_messages = number_of_unseen_messages


class Contribution(DataModelBase):
    def __init__(self, discussion_topic_id, user_id, data_id, contribution_type, id=None, created=None, archived=None):
        self.id = id
        self.discussion_topic_id = discussion_topic_id
        self.user_id = user_id
        self.data_id = data_id
        self.contribution_type = contribution_type
        self.created = created
        self.archived = archived


class ResolvedContribution(DataModelBase):
    def __init__(self, contribution, data):
        self.contribution = contribution
        self.data = data
        

class DiscussionWithTopic(DataModelBase):
    def __init__(self, discussion, topic):
        self.discussion = discussion
        self.topic = topic


class DiscussionTopicWithContribution(DataModelBase):
    def __init__(self, discussion_topic, contribution):
        self.discussion_topic = discussion_topic
        self.contribution = contribution
