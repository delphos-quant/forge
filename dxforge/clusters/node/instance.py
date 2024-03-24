from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image

from .node_data import NodeData


class Instance:
    def __init__(self,
                 data: NodeData = None,
                 ):
        self.data = data
        self._container: Container | None = None
        self._image: Image | None = None

    @property
    def alive(self):
        if not self._container:
            return False
        return self._container.status == "running"

    @property
    def ip(self):
        if self._container:
            if self.data.network == "host":
                return "localhost"
            elif self.data.network == "bridge":
                return self._container.attrs["NetworkSettings"]["IPAddress"]
            else:
                return self._container.attrs["NetworkSettings"]["Networks"][self.data.network]["IPAddress"]

        return None

    def build(self, docker_client: DockerClient) -> Image:
        return docker_client.images.build(
            path=self.data.path,
            tag=self.data.image_tag
        )

    def start(self, docker_client: DockerClient) -> Container:
        container = docker_client.containers.run(
            image=self.data.image_tag,
            expose=self.data.ports,
            network=self.data.network,
            detach=True,
        )
        self._container = container
        return container

    def stop(self):
        if self._container:
            self._container.stop()
            self._container.remove()
            self._container = None

    def logs(self):
        if self._container:
            return self._container.logs()
        return None

    @property
    def info(self):
        return {
            "ip": self.ip,
            "ports": self.data.ports,
            "network": self.data.network,
        }
