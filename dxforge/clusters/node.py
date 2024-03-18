import subprocess
from dataclasses import dataclass
from typing import Tuple, Dict
from uuid import uuid4

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
                 env: dict[str, str] = None):
        self.path = path
        self.tag = tag
        self.depends_on = depends_on if depends_on else []
        self.ports = ports if ports else {}
        self.env = env


class Instance:
    def __init__(self,
                 config: NodeConfig = None,
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


class Node:
    def __init__(self, config: NodeConfig):
        self._config = config
        self.instances: Dict[str, Instance] = {}

    @classmethod
    def from_dict(cls, config: dict):
        config = NodeConfig(
            path=config.get("path"),
            tag=config.get("tag"),
            depends_on=config.get("depends_on"),
            ports=config.get("ports"),
            env=config.get("env")
        )

        return cls(config)

    @property
    def client(self):
        return httpx.AsyncClient()

    @property
    def config(self):
        return self._config

    @property
    def alive(self):
        return any([instance.alive for instance in self.instances.values()])

    @property
    def info(self):
        return {
            "alive": self.alive,
            "instances": {uuid: instance.alive for uuid, instance in self.instances.items()},
            "interface": {
                "ports": self._config.ports
            }
        }

    def create_instance(self, uuid: str = None):
        if uuid is None:
            uuid = uuid4()
        self.instances[uuid] = Instance(self._config)

        return uuid

    def build(self, docker_client: DockerClient):
        for instance in self.instances.values():
            instance.build(docker_client)

    def start(self, docker_client: DockerClient):
        status = {}
        for uuid, instance in self.instances.items():
            try:
                instance.start(docker_client)
                status[uuid] = "started"
            except Exception as e:
                status[uuid] = e
        return {
            "instances": status,
        }

    def stop(self):
        for instance in self.instances.values():
            instance.stop()

    def get_interface(self, name=None) -> Tuple[int, str]:
        if name is None:
            raise NotImplementedError("No instance union implemented")
        return self._config.ports[name], self.instances[name].info["host"]
