from dataclasses import dataclass
from typing import List

@dataclass
class FilesToUpload:
    """
    Used when retrieving upload urls from input api
    """

    files_to_upload: List[str]
    
    def to_dict(self):
        return dict(filesToUpload=self.files_to_upload)
