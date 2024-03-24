import subprocess
from typing import Tuple, Dict
from uuid import uuid4

import httpx
from docker import DockerClient

from .instance import Instance
from .node_data import NodeData


def build(compose_file: str, service_name: str, docker):
    if docker:
        subprocess.run(['docker compose', '-f', compose_file, 'build', service_name])
        image = docker.images.get(service_name)

        return image
    else:
        raise NotImplementedError("No script manager implemented")


class Node:
    def __init__(self, config: NodeData, instance_config=None):
        self._config = config
        self.instance_config = instance_config
        self.instances: Dict[str, Instance] = {}

    @classmethod
    def from_dict(cls, path, config: dict, instance_config=None) -> 'Node':
        if ports := config.get("expose"):
            ports = [int(port) for port in ports]
        else:
            ports = []
        config = NodeData(
            path=path,
            image_tag=config.get("image"),
            depends_on=config.get("depends_on"),
            ports=ports,
            env=config.get("env"),
            network=config.get("network"),
        )

        return cls(config, instance_config)

    @property
    def client(self):
        return httpx.AsyncClient()

    @property
    def config(self):
        return self._config

    @property
    def info(self):
        return {
            "instances": {uuid: instance.alive for uuid, instance in self.instances.items()},
            "instance_config": self.instance_config
        }

    def create_instance(self, uuid: str = None):
        if uuid is None:
            uuid = uuid4()
        self.instances[uuid] = Instance(self._config)

        return uuid

    def _run(self, func, *args, **kwargs):
        success = set()
        errors = {}
        for uuid, instance in self.instances.items():
            try:
                func(instance, *args, **kwargs)
                success.add(str(uuid))
            except Exception as e:
                errors[str(uuid)] = str(e)
        return {
            "success": success,
            "errors": errors
        }

    def build(self, docker_client: DockerClient):
        return self._run(Instance.build, docker_client)

    def start(self, docker_client: DockerClient):
        return self._run(Instance.start, docker_client)

    def stop(self):
        return self._run(Instance.stop)

    def get_interface(self, name=None) -> Tuple[int, str]:
        if name is None:
            raise NotImplementedError("No instance union implemented")
        return self._config.ports[name], self.instances[name].info["host"]

    def log(self, uuid):
        return self.instances[uuid].logs()
