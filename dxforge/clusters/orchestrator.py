from typing import Dict

import httpx
import docker

from .controller import Controller
from .node import Node


class Orchestrator:
    def __init__(self, controllers: Dict[str, Controller]):
        self.docker = docker.DockerClient() if docker else None
        self.controllers = {} if not controllers else controllers

    @property
    def client(self):
        return httpx.AsyncClient()

    async def test_node(self, controller: Controller | str, node: Node | str):
        try:
            if isinstance(controller, str):
                controller = self.controllers[controller]
            response = await controller.get(node)
            return response.status_code == 200
        except (httpx.HTTPError, httpx.InvalidURL):
            return False

    async def status(self):
        status = {}
        for controller_name, controller in self.controllers.items():
            status[controller_name] = await controller.status()
        return status
