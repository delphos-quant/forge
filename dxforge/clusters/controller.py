from __future__ import annotations

import logging
import subprocess

from docker import DockerClient
from docker.errors import ImageNotFound
import yaml

from .node import Node


class Controller:
    def __init__(self, docker: DockerClient = None):
        self._nodes: dict[str, Node] = {}
        self.docker = docker
        self.logger = logging.Logger(__name__)

    @classmethod
    def from_file(cls, file_path: str, docker: DockerClient):
        config = yaml.safe_load(open(file_path, "r"))
        services = config.get("services", None)

        controller = cls(docker) if docker else cls()
        for service_name, data in services.items():
            try:
                subprocess.run(['docker', 'compose', '-f', file_path, 'build', service_name])
                image = docker.images.get(service_name)

                service = Node.from_file(image, docker)
                if service:
                    controller.nodes[service_name] = service
            except ImageNotFound:
                continue

        return controller

    @property
    def nodes(self):
        return self._nodes

    async def get(self, service: str | Node, endpoint: str = "/"):
        if isinstance(service, str):
            service = self.nodes[service]
        return await service.get(endpoint)

    async def post(self, service: str | Node, endpoint: str = "/", data=None):
        if isinstance(service, str):
            service = self.nodes[service]
        return await service.post(endpoint, data)

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
        for service_name, service in self.nodes.items():
            try:
                response = await self.get(service)
                if response.status_code == 200:
                    status["nodes"]["running"].append(service_name)
                else:
                    status["nodes"]["stopped"].append(service_name)
            except RuntimeError:
                self.logger.warning(f"Service {service_name} not started")
                status["nodes"]["stopped"].append(service_name)

        return status
