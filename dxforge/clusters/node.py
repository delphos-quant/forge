import subprocess

import httpx
from docker import DockerClient
from docker.models.containers import Container


def build(compose_file: str, service_name: str, docker):
    if docker:
        subprocess.run(['docker compose', '-f', compose_file, 'build', service_name])
        image = docker.images.get(service_name)

        return image
    else:
        raise NotImplementedError("No script manager implemented")


class Node:
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
