from typing import List, Mapping, Dict, Any, Type, Optional
import json
from datetime import datetime
import math

"""
    API MODEL RESPONSES
"""


def ts_to_dt(unixtimemillis: int) -> datetime:
    unixtimeseconds = unixtimemillis // 1000
    return datetime.utcfromtimestamp(unixtimeseconds)


class Response:
    @staticmethod
    def from_json(js: dict):
        raise NotImplementedError


class RequestCall:
    def to_dict(self) -> dict:
        raise NotImplementedError


class FilesPointCloudWithImages(RequestCall):
    def __init__(self, images: List[str], pointclouds: List[str]):
        self.images = images
        self.pointclouds = pointclouds

    def to_dict(self):
        return dict(
            images=self.images,
            pointclouds=self.pointclouds
        )


class CalibrationSpec(RequestCall):
    def __init__(self, external_id: str, calibration: Dict[str, Any]):
        self.external_id = external_id
        self.calibration = calibration

    def to_dict(self):
        return {
            'externalId': self.external_id,
            'calibration': self.calibration
        }


class SourceSpecification(RequestCall):
    def __init__(self, images_to_source: Dict[str, str],
                 source_to_pretty_name: Optional[Dict[str, str]] = None,
                 source_order: Optional[List[str]] = None):

        self.images_to_source = images_to_source
        self.source_to_pretty_name = source_to_pretty_name
        self.source_order = source_order

    def to_dict(self):
        as_dict = {}
        if self.source_to_pretty_name:
            as_dict['sourceToPrettyName'] = self.source_to_pretty_name
        if self.source_order:
            as_dict['sourceOrder'] = self.source_order

        as_dict['imagesToSource'] = self.images_to_source
        return as_dict


class Metadata(RequestCall):
    def __init__(self, external_id: str, source_specification: SourceSpecification,
                 calibration_spec: Optional[CalibrationSpec] = None,
                 calibration_id: Optional[int] = None):

        if not calibration_spec and not calibration_id:
            raise Exception("calibration_spec or calibration_id must be set")

        self.external_id = external_id
        self.source_specification = source_specification
        self.calibration_spec = calibration_spec
        self.calibration_id = calibration_id

    def to_dict(self):
        as_dict = {}
        if self.calibration_spec:
            as_dict['calibrationSpec'] = self.calibration_spec.to_dict()
        elif self.calibration_id:
            as_dict['calibrationId'] = self.calibration_id

        as_dict['externalId'] = self.external_id
        as_dict['sourceSpecification'] = self.source_specification.to_dict()
        return as_dict


class CalibrationNoContent(Response):
    def __init__(self, id: int, external_id: str, created: datetime):
        self.id = id
        self.external_id = external_id
        self.created = created

    @staticmethod
    def from_json(js: dict):
        return CalibrationNoContent(
            int(js["id"]), js["externalId"], ts_to_dt(js["created"]["timestamp"])
        )

    def __repr__(self):
        return f"<CalibrationWithContent(" + \
            f"id={self.id}, " + \
            f"external_id={self.external_id}, " + \
            f"created={self.created})>"


class CalibrationWithContent(Response):
    def __init__(self, id: int, external_id: str, created: datetime,
                 calibration: Mapping[str, dict]):
        self.id = id
        self.external_id = external_id
        self.created = created
        self.calibration = calibration

    @staticmethod
    def from_json(js: dict):
        return CalibrationWithContent(int(js["id"]), js["externalId"],
                                      ts_to_dt(js["created"]["timestamp"]), js["calibration"])

    def __repr__(self):
        return f"<CalibrationWithContent(" + \
            f"id={self.id}, " + \
            f"external_id={self.external_id}, " + \
            f"created={self.created}, " + \
            f"calibration={{...}})>"


class InputList(Response):
    def __init__(self, id: int, project_id: int, name: str, created: datetime):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.created = created

    @staticmethod
    def from_json(js: dict):
        return InputList(int(js["id"]), int(js["projectId"]), js["name"],
                         ts_to_dt(js["created"]["timestamp"]))

    def __repr__(self):
        return f"<InputList(" + \
            f"id={self.id}, " + \
            f"project_id={self.project_id}, " + \
            f"name={self.name}, " + \
            f"created={self.created})>"


class Project(Response):
    def __init__(self, id: int, created: datetime, title: str, description: str,
                 deadline: Optional[str], status: str):
        self.id = id
        self.created = created
        self.title = title
        self.description = description
        self.deadline = deadline
        self.status = status

    @staticmethod
    def from_json(js: dict):
        return Project(int(js["id"]), ts_to_dt(js["created"]["timestamp"]), js["title"],
                       js["description"], js.get("deadline"), js["status"])

    def __repr__(self):
        return f"<Project(" + \
            f"id={self.id}, " + \
            f"created={self.created}, " + \
            f"title={self.title}, " + \
            f"description={self.description}, " + \
            f"deadline={self.deadline}, " + \
            f"status={self.status})>"


class Request(Response):
    def __init__(self, id: int, created: datetime, project_id: int, title: str, description: str,
                 input_list_id: int):
        self.id = id
        self.created = created
        self.project_id = project_id
        self.title = title
        self.description = description
        self.input_list_id = input_list_id

    @staticmethod
    def from_json(js: dict):
        return Request(int(js["id"]), ts_to_dt(js["created"]["timestamp"]), int(js["projectId"]),
                       js["title"], js["description"], int(js["inputListId"]))

    def __repr__(self):
        return f"<Request(" + \
            f"id={self.id}, " + \
            f"created={self.created}, " + \
            f"project_id={self.project_id}, " + \
            f"title={self.title}, " + \
            f"description={self.description}, " + \
            f"input_list_id={self.input_list_id})>"


class CreateInputResponse(Response):
    def __init__(self, internal_id: str, external_id: str, converting_files: List[str]):
        self.internal_id = internal_id
        self.external_id = external_id
        self.converting_files = converting_files

    @staticmethod
    def from_json(js: dict):
        return CreateInputResponse(js["internalId"], js["externalId"], js["convertingFiles"])

    def __repr__(self):
        return f"<CreateInputResponse(" + \
            f"internal_id={self.internal_id}, external_id={self.external_id}, " + \
            f"converting_files={self.converting_files})>"


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


class InputJob(Response):
    def __init__(self, id: int, internal_id: str, external_id: str, filename: str,
                 success: bool, added: datetime, error_message: Optional[str]):
        self.id = id
        self.internal_id = internal_id
        self.external_id = external_id
        self.filename = filename
        self.success = success
        self.added = added
        self.error_message = error_message

    @staticmethod
    def from_json(js: dict):
        return InputJob(int(js["id"]), js["jobId"], js["externalId"], js["filename"],
                        bool(js["success"]), ts_to_dt(js["added"]["timestamp"]), js.get("errorMessage"))

    def __repr__(self):
        return f"<InputJob(" + \
            f"id={self.id}, " + \
            f"internal_id={self.internal_id}, " + \
            f"external_id={self.external_id}, " + \
            f"filename={self.filename}, " + \
            f"success={self.success}, " + \
            f"added={self.added}, " + \
            f"error_message={self.error_message})>"
