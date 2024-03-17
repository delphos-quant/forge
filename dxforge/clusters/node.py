import subprocess
from dataclasses import dataclass
from typing import Tuple

import httpx
from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image


def build(compose_file: str, service_name: str, docker):
    if docker:
        subprocess.run(['docker compose', '-f', compose_file, 'build', service_name])
        image = docker.images.get(service_name)

        return image
    else:
        raise NotImplementedError("No script manager implemented")


@dataclass
class NodeConfig:
    def __init__(self,
                 path: str,
                 tag: str,
                 depends_on: list[str] = None,
                 ports: dict[str, tuple | int] = None,
                 host: str = "localhost",
                 env: dict[str, str] = None):
        self.path = path
        self.tag = tag
        self.depends_on = depends_on if depends_on else []
        self.ports = ports if ports else {}
        self.host = host
        self.env = env


class Instance:
    def __init__(self,
                 config: NodeConfig = None,
                 ):
        self.config = config
        self._container: Container | None = None
        self._image: Image | None = None

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
    def alive(self):
        if not self._container:
            return False
        return self._container.status == "running"


class Node:
    def __init__(self, config: NodeConfig, docker_client: DockerClient = None):
        self._config = config
        self.docker_client = docker_client
        self.instances = {}

    @classmethod
    def from_dict(cls, config: dict, docker_client: DockerClient):
        config = NodeConfig(
            path=config.get("path"),
            tag=config.get("tag"),
            depends_on=config.get("depends_on"),
            ports=config.get("ports"),
            host=config.get("host"),
            env=config.get("env")
        )

        return cls(config, docker_client)

    @property
    def client(self):
        return httpx.AsyncClient()

    @property
    def config(self):
        return self._config

    @property
    def alive(self):
        return any([instance.alive for instance in self.instances.values()])

    def add_instance(self, uuid: str):
        self.instances[uuid] = Instance(self._config)

    def build(self):
        if self.docker_client:
            for instance in self.instances.values():
                instance.build(self.docker_client)
        else:
            raise NotImplementedError("No script manager implemented")

    def start(self):
        if self.docker_client:
            for instance in self.instances.values():
                instance.start(self.docker_client)
        else:
            raise NotImplementedError("No script manager implemented")

    def stop(self):
        if self.docker_client:
            for instance in self.instances.values():
                instance.stop()
        else:
            raise NotImplementedError("No script manager implemented")

    def get_interface(self, name=None) -> Tuple[str, int]:
        if name is None:
            raise NotImplementedError("No instance union implemented")
        return self._config.host, self._config.ports[name]
