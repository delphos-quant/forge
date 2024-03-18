from typing import List

import docker
import httpx

from .clusters import Orchestrator, Controller
from .utils import SingletonMeta


class Forge(metaclass=SingletonMeta):
    def __init__(self,
                 orchestrators: List[Orchestrator]):
        self._orchestrators = orchestrators

    @classmethod
    def from_config(cls, config: dict) -> 'Forge':
        docker_client = docker.DockerClient() if docker else None

        controllers = {}

        for name, path in config.get("controllers", {}).items():
            controllers[name] = Controller.from_file(path, docker_client)
        orchestrator = Orchestrator(controllers, docker_client)

        return cls([orchestrator])

    @property
    def client(self):
        return httpx.AsyncClient()

    @property
    def orchestrator(self):
        return self._orchestrators[0]

    async def stop(self):
        await self._orchestrators[0].stop()
