from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image

from .node_data import NodeData


class Instance:
    def __init__(self,
                 config: NodeData = None,
                 ):
        self.config = config
        self._container: Container | None = None
        self._image: Image | None = None

    @property
    def alive(self):
        if not self._container:
            return False
        return self._container.status == "running"

    def build(self, docker_client: DockerClient) -> Image:
        return docker_client.images.build(
            path=self.config.path,
            tag=self.config.tag
        )

    def start(self, docker_client, tag: str = None) -> Container:
        container = docker_client.containers.run(
            tag if tag else self.config.tag,
            ports={port: port for port in self.config.ports.values()},
            detach=True,
        )
        self._container = container
        return container

    def stop(self):
        if self._container:
            self._container.stop()
            self._container.remove()
            self._container = None

    @property
    def info(self):
        return {
            "host": self._container.attrs["NetworkSettings"]["IPAddress"] if self._container else None,
            "ports": self.config.ports
        }
