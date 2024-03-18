from __future__ import annotations

import logging
import os

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
    def from_file(cls, controller_path: str, docker_client: DockerClient):
        config = yaml.safe_load(open(controller_path, "r"))
        services = config.get("services", None)

        controller = cls(docker_client) if docker_client else cls()
        for node_name, data in services.items():
            try:
                if node := Node.from_dict(data, cls.get_node_path(data, controller_path)):
                    controller.nodes[node_name] = node
            except ImageNotFound:
                continue

        return controller

    @staticmethod
    def get_node_path(data, controller_path):
        context = data['build'].get('context')
        if context == ".":
            node_path = os.path.dirname(controller_path)
        else:
            node_path = os.path.join(os.path.dirname(controller_path), data['build'].get('context'))
        return node_path

    @property
    def nodes(self) -> dict[str, Node]:
        return self._nodes

    def get_interface(self, node: str | Node, name: str = None):
        if isinstance(node, str):
            node = self.nodes[node]
        return node.get_interface(name)

    def build(self, node: Node):
        for depend_node_name in node.config.depends_on:
            depend_node = self.nodes[depend_node_name]
            self.build(depend_node)
        return node.build(self.docker_client)

    def start(self, node: Node):
        return node.start(self.docker_client)

    @staticmethod
    def stop(node: Node):
        return node.stop()

    def status(self):
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

    @property
    def info(self):
        return {
            "nodes": {node_name: node.info for node_name, node in self.nodes.items()},
        }
