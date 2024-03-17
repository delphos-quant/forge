from typing import Dict

import docker
import httpx

from .clusters import Orchestrator, Controller


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class Forge(Singleton):
    def __init__(self,
                 controllers: Dict[str, Controller] = None):
        self._orchestrators = [Orchestrator(controllers)]

    @classmethod
    def from_config(cls, config: dict) -> 'Forge':
        docker_client = docker.DockerClient() if docker else None

        controllers = {}

        for name, path in config.get("controllers", {}).items():
            controllers[name] = Controller.from_file(path, docker_client)

        return cls(controllers)

    @property
    def client(self):
        return httpx.AsyncClient()

    @property
    def orchestrator(self):
        return self._orchestrators[0]

    def stop(self):
        for controller in self.orchestrator.controllers.values():
            controller.stop()
