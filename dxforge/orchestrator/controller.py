from __future__ import annotations

import logging
import subprocess

from docker import DockerClient
from docker.errors import ImageNotFound
import yaml

from .node import Node


class Controller:
    def __init__(self, docker: DockerClient = None):
        self._services: dict[str, Node] = {}
        self.docker = docker
        self.logger = logging.Logger(__name__)

    @classmethod
    def from_file(cls, file_path: str, docker: DockerClient):
        config = yaml.safe_load(open(file_path, "r"))
        services = config.get("services", None)

        server = cls(docker) if docker else cls()
        for service_name, data in services.items():
            try:
                subprocess.run(['docker', 'compose', '-f', file_path, 'build', service_name])
                image = docker.images.get(service_name)

                service = Node.from_file(image, docker)
                if service:
                    server._services[service_name] = service
            except ImageNotFound:
                continue

        return server

    async def get(self, service: str | Node, endpoint: str = "/"):
        if isinstance(service, str):
            service = self._services[service]
        return await service.get(endpoint)

    async def post(self, service: str | Node, endpoint: str = "/", data=None):
        if isinstance(service, str):
            service = self._services[service]
        return await service.post(endpoint, data)

    def start(self, service_name: str | None = None):
        if service_name:
            self._services[service_name].start()
            return
        for service in self._services.values():
            service.start()

    def stop(self, service=None):
        if service:
            self._services[service].stop()
            return
        for service in self._services.values():
            service.stop()

    async def status(self):
        status = {}
        for service_name, service in self._services.items():
            try:
                response = await self.get(service)
                status[service_name] = "running" if response.status_code == 200 else "stopped"
            except RuntimeError:
                self.logger.warning(f"Service {service_name} not started")
                status[service_name] = "stopped"

        return status
