from typing import Dict

import httpx
import docker

from .controller import Controller
from .node import Node


class Orchestrator:
    def __init__(self, controllers: Dict[str, Controller]):
        self.docker = docker.DockerClient() if docker else None
        self.controllers = {} if not controllers else controllers

    def node_status(self, controller: Controller | str = None, node: Node | str = None):
        try:
            if isinstance(controller, str):
                controller = self.controllers[controller]
            return controller.nodes[node].alive if isinstance(node, str) else node.alive
        except (httpx.HTTPError, httpx.InvalidURL):
            return False

    def status(self):
        status = {
            controller_name: {
                "stopped": [],
                "running": []
            }
            for controller_name in self.controllers
        }
        for controller in self.controllers:
            for node in self.controllers[controller].nodes:
                if self.controllers[controller].nodes[node].alive:
                    status[controller]["running"].append(node)
                else:
                    status[controller]["stopped"].append(node)
        return status
