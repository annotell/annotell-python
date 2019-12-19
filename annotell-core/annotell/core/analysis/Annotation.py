

class Annotation:
    def __init__(self, assignments_id=None, users_id=None, assignments_completed=None, continue_chain=None,
                 tasks_id=None, inputs_id=None, actions_name=None, builds_on_assignments_id=None,
                 organizations_id=None, data_content=None, filename=None):
        self.assignments_id = assignments_id
        self.users_id = users_id
        self.assignments_completed = assignments_completed
        self.continue_chain = continue_chain
        self.tasks_id = tasks_id
        self.inputs_id = inputs_id
        self.actions_name = actions_name
        self.builds_on_assignments_id = builds_on_assignments_id
        self.organizations_id = organizations_id
        self.data_content = data_content
        self.filename = filename

    def __repr__(self):
        # being able to write print(annotation) with all meta data
        tmp = 'A LidarAnnotation object with properties: \n'
        tmp += '\tassignments_id = %s\n' % self.assignments_id
        tmp += '\tusers_id = %s\n' % self.users_id
        tmp += '\tassignments_completed = %s\n' % self.assignments_completed
        tmp += '\tcontinue_chain = %s\n' % self.continue_chain
        tmp += '\ttasks_id = %s\n' % self.tasks_id
        tmp += '\tinputs_id = %s\n' % self.inputs_id
        tmp += '\tactions_name = %s\n' % self.actions_name
        tmp += '\tbuilds_on_assignments_id = %s\n' % self.builds_on_assignments_id
        tmp += '\torganizations_id = %s\n' % self.organizations_id
        nbr_boxes = len(self.data_content) if isinstance(self.data_content, list) else 0
        tmp += '\tdata_content: contains %s boxes' % nbr_boxes
        return tmp

