from dataclasses import dataclass


@dataclass
class ExportAnnotation:
    annotation_id: int
    export_content: dict

    @staticmethod
    def from_json(js: dict):
        return ExportAnnotation(int(js["annotationId"]), js["exportContent"])
