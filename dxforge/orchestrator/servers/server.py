from __future__ import annotations

import logging
import subprocess

from docker import DockerClient
from docker.errors import ImageNotFound
from docker.models.containers import Container
import httpx
import yaml


def build(compose_file: str, service_name: str, docker):
    if docker:
        subprocess.run(['docker compose', '-f', compose_file, 'build', service_name])
        image = docker.images.get(service_name)

        return image
    else:
        raise NotImplementedError("No script manager implemented")


class Service:
    def __init__(self, image, ports: dict[str, tuple | list | str], host=None, docker: DockerClient = None):
        self.image = image
        self.container: Container | None = None

        for name, port in ports.items():
            if isinstance(port, str):
                ports[name] = port

        self.ports: dict[str, tuple | list | str] = ports
        self.host = host if host else "localhost"
        self.docker = docker

    @classmethod
    def from_file(cls, image, docker: DockerClient):
        image_config = image.attrs['Config']

        env_vars = image_config.get('Env', [])
        env = {}
        for var in env_vars:
            key, value = var.split('=', 1)
            env[key] = value

        http_port = env.get('HTTP_PORT', None)
        websocket_port = env.get('WEBSOCKET_PORT', None)

        if not http_port and not websocket_port:
            return

        ports = {}

        if http_port:
            ports['HTTP_PORT'] = str(http_port)
        if websocket_port:
            ports['WEBSOCKET_PORT'] = str(websocket_port)

        host = env.get('HOST', None)

        service = cls(image, ports, host, docker=docker)
        return service

    @property
    def client(self):
        return httpx.AsyncClient()

    def start(self):
        if self.docker:
            self.container = self.docker.containers.run(
                self.image,
                ports={port: port for port in self.ports.values()},
                detach=True,
            )
        else:
            raise NotImplementedError("No script manager implemented")

    def stop(self):
        if self.docker and self.container:
            self.container.stop()
            self.container.remove()
        else:
            raise NotImplementedError("No script manager implemented")

    async def get(self, endpoint: str):
        if not self.docker:
            raise NotImplementedError("No script manager implemented")
        elif not self.container:
            raise RuntimeError("Container not started")

        protocol = "http"
        async with self.client:
            return await self.client.get(
                f"{protocol}://{self.host}:{self.ports['HTTP_PORT']}{endpoint}"
            )

    async def post(self, endpoint: str, data):
        if not self.docker:
            raise NotImplementedError("No script manager implemented")
        elif not self.container:
            raise RuntimeError("Container not started")

        protocol = "http"
        async with self.client:
            return await self.client.post(
                f"{protocol}://{self.host}:{self.ports['HTTP_PORT']}{endpoint}",
                json=data
            )


class Server:
    def __init__(self, docker: DockerClient = None):
        self._services: dict[str, Service] = {}
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

                service = Service.from_file(image, docker)
                if service:
                    server._services[service_name] = service
            except ImageNotFound:
                continue

        return server

    async def get(self, service: str | Service, endpoint: str = "/"):
        if isinstance(service, str):
            service = self._services[service]
        return await service.get(endpoint)

    async def post(self, service: str | Service, endpoint: str = "/", data=None):
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
            except (RuntimeError, httpx.ConnectError):
                self.logger.warning(f"Service {service_name} not started")
                status[service_name] = "stopped"

        return status
