from typing import Dict, Union, Mapping
from datetime import datetime
from annotell.input_api.model.abstract.abstract_models import RequestCall, Response
from annotell.input_api.model.calibration_explicit import *
from annotell.input_api.util import ts_to_dt



class Calibration(RequestCall):
    def __init__(self, calibration_dict: Dict[str, Union[CameraCalibrationExplicit, LidarCalibrationExplicit]]):  # noqa:E501
        self.calibration_dict = calibration_dict

    def to_dict(self):
        return dict(
            [(k, v.to_dict()) for (k, v) in self.calibration_dict.items()]
        )

class CalibrationSpec(RequestCall):
    def __init__(self, external_id: str,
                 calibration: Calibration):
        self.external_id = external_id
        self.calibration = calibration

    def to_dict(self):
        return {
            'externalId': self.external_id,
            'calibration': self.calibration.to_dict()
        }


class CalibrationNoContent(Response):
    def __init__(self, id: int, external_id: str, created: datetime):
        self.id = id
        self.external_id = external_id
        self.created = created

    @staticmethod
    def from_json(js: dict):
        return CalibrationNoContent(
            int(js["id"]), js["externalId"], ts_to_dt(js["created"])
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
                                      ts_to_dt(js["created"]), js["calibration"])

    def __repr__(self):
        return f"<CalibrationWithContent(" + \
            f"id={self.id}, " + \
            f"external_id={self.external_id}, " + \
            f"created={self.created}, " + \
            f"calibration={{...}})>"
