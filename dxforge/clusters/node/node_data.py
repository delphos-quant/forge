from dataclasses import dataclass
from typing import List, Dict


@dataclass
class NodeData:
    def __init__(self,
                 path: str,
                 image_tag: str,
                 depends_on: List[str] = None,
                 ports: List[int] = None,
                 env: Dict[str, str] = None,
                 network='host'):
        self.path = path
        self.image_tag = image_tag
        self.depends_on = depends_on if depends_on else []
        self.ports = ports if ports else []
        self.env = env
        self.network = network
