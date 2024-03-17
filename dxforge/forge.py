from typing import Dict

import docker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    @property
    def orchestrators(self):
        return self._orchestrators

    @classmethod
    def from_config(cls, config: dict) -> 'Forge':
        docker_client = docker.DockerClient() if docker else None

        controllers = {}

        for name, path in config.get("controllers", {}).items():
            controllers[name] = Controller.from_file(path, docker_client)

        return cls(controllers)

    def get_orchestrator(self) -> Orchestrator:
        return self.orchestrators[0]

    def stop(self):
        for controller in self.controllers.values():
            controller.stop()

    def setup_routes(self):
        @self.app.get("/")
        async def get_status():
            running = {controller_name: [] for controller_name in self.controllers}
            stopped = {controller_name: [] for controller_name in self.controllers}
            status = await self.status()
            for controller_name, controller_status in status.items():
                for node_name, node_status in controller_status.items():
                    if node_status == "running":
                        running[controller_name].append(node_name)
                    else:
                        stopped[controller_name].append(node_name)

            return {"running": running, "stopped": stopped}

        # @self.app.get("/controller/{controller}")
        # async def get_controller_status(controller: str):
        #     status = await self.controllers[controller].status()
        #     return status
        #
        # @self.app.get("/controller/{controller}/{node}")
        # async def get_node_endpoints(controller: str,
        #                              node: str):
        #     async with self.client:
        #         response = await self.controllers[controller].get(node)
        #         return response.json()
        #
        # @self.app.get("/controller/{controller}/{node}/{endpoint}")
        # async def get_node_endpoints(controller: str,
        #                              node: str,
        #                              endpoint: str):
        #     async with self.client:
        #         response = await self.controllers[controller].get(node, endpoint=f"/{endpoint}")
        #         return response.json()
        #
        # @self.app.post("/controller/{controller}/{node}/{endpoint}")
        # async def get_node_endpoints(controller: str,
        #                              node: str,
        #                              endpoint: str,
        #                              request: Request):
        #     data = await request.json()
        #     async with self.client:
        #         response = await self.controllers[controller].post(node, endpoint=f"/{endpoint}", data=data)
        #         return response.json()
