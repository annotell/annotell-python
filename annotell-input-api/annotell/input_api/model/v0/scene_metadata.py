
from typing import List, Optional
from annotell.input_api.model.abstract.abstract_models import RequestCall
from annotell.input_api.model.v0.source_specification import SourceSpecification


class SceneMetaData(RequestCall):
    def __init__(self, external_id: str, source_specification: Optional[SourceSpecification] = None):
        self.external_id = external_id
        self.source_specification = source_specification

    def to_dict(self):
        as_dict = dict(externalId=self.external_id)
        if self.source_specification is not None:
            as_dict["sourceSpecification"] = self.source_specification.to_dict()
        return as_dict

class CalibratedSceneMetaData(SceneMetaData):
    def __init__(self, external_id: str,
                 calibration_id: int,
                 source_specification: Optional[SourceSpecification] = None):

        super().__init__(external_id, source_specification)
        self.calibration_id = calibration_id

    def to_dict(self):
        as_dict = super().to_dict()
        if self.calibration_id is not None:
            as_dict['calibrationId'] = self.calibration_id

        return as_dict