from __future__ import annotations

import logging

from docker import DockerClient
from docker.errors import ImageNotFound
import yaml

from .node import Node


class Controller:
    def __init__(self, docker_client: DockerClient = None):
        self._nodes: dict[str, Node] = {}
        self.docker_client = docker_client
        self.logger = logging.Logger(__name__)

    @classmethod
    def from_file(cls, file_path: str, docker_client: DockerClient):
        config = yaml.safe_load(open(file_path, "r"))
        services = config.get("services", None)

        controller = cls(docker_client) if docker_client else cls()
        for service_name, data in services.items():
            try:
                service = Node.from_dict(data, docker_client)
                if service:
                    controller.nodes[service_name] = service
            except ImageNotFound:
                continue

        return controller

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    def get_interface(self, node: str | Node, name: str = None):
        if isinstance(node, str):
            node = self.nodes[node]
        return node.get_interface(name)

    def build(self, node_name: str | None = None):
        if node_name:
            node = self.nodes[node_name]
            for node in node.config.depends_on:
                self.nodes[node].build()
            self.nodes[node_name].build()
            return
        for node in self.nodes.values():
            node.build()

    def start(self, service_name: str | None = None):
        if service_name:
            self.nodes[service_name].start()
            return
        for service in self.nodes.values():
            service.start()

    def stop(self, service=None):
        if service:
            self.nodes[service].stop()
            return
        for service in self.nodes.values():
            service.stop()

    async def status(self):
        status = {
            "nodes": {
                "stopped": [],
                "running": []
            }
        }
        for node_name, node in self.nodes.items():
            try:
                if node.alive:
                    status["nodes"]["running"].append(node_name)
                else:
                    status["nodes"]["stopped"].append(node_name)
            except RuntimeError:
                self.logger.warning(f"Node {node_name} not started")
                status["nodes"]["stopped"].append(node_name)

        return status
