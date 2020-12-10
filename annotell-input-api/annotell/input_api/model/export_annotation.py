
from annotell.input_api.model.abstract.abstract_models import Response

class ExportAnnotation(Response):
    def __init__(self, annotation_id: int, export_content: dict):
        self.annotation_id = annotation_id
        self.export_content = export_content

    @staticmethod
    def from_json(js: dict):
        return ExportAnnotation(int(js["annotationId"]), js["exportContent"])

    def __repr__(self):
        return f"<ExportAnnotation(" + \
            f"annotation_id={self.annotation_id}, " + \
            f"export_content={{...}})>"
