from enum import Enum


class CameraType(str, Enum):
    PINHOLE = "pinhole"
    FISHEYE = "fisheye"
    KANNALA = "kannala"


class InvalidatedReasonInput(str, Enum):
    BAD_CONTENT = "bad-content"
    SLAM_RECORRECTION = "slam-rerun"
    DUPLICATE = "duplicate"
    INCORRECTLY_CREATED = "incorrectly-created"


class InputBatchStatus(str, Enum):
    PENDING = 'pending'
    OPEN = 'open'
    READY = 'ready'
    INPROGESS = 'in-progress'
    COMPLETED = 'completed'


class InputStatus(str, Enum):
    Processing = "processing"
    Created = "created"
    Failed = "failed"
    InvalidatedBadContent = "invalidated:broken-input"
    InvalidatedSlamRerun = "invalidated:slam-rerun"
    InvalidatedDuplicate = "invalidated:duplicate"
    InvalidatedIncorrectlyCreated = "invalidated:incorrectly-created"
