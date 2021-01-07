from dataclasses import dataclass

from annotell.input_api.model.v1.scene_input import SceneInput


@dataclass
class LidarsSequence(SceneInput):
    def path(self):
        return "lidar-sequence"
