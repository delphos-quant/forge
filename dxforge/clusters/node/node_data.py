from dataclasses import dataclass


@dataclass
class NodeData:
    def __init__(self,
                 path: str,
                 tag: str,
                 depends_on: list[str] = None,
                 ports: dict[str | Tuple[int, int]] = None,
                 env: dict[str, str] = None):
        self.path = path
        self.tag = tag
        self.depends_on = depends_on if depends_on else []
        self.ports = ports if ports else {}
        self.env = env
