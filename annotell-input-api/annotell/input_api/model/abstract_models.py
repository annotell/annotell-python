from typing import Dict


class RequestCall:
    def to_dict(self) -> Dict:
        raise NotImplementedError


class SensorCalibration(RequestCall):

    def to_dict(self) -> Dict:
        raise NotImplementedError


class Response:
    @staticmethod
    def from_json(js: dict):
        raise NotImplementedError
