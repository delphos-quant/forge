from __future__ import annotations

import docker
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import yaml

from .servers import Server, Service


class Orchestrator:
    def __init__(self, config_path, origins: list[str] = None):
        self.app = FastAPI()

        if origins is None:
            origins = [
                "http://localhost:80",
                "http://localhost:443",
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8080",
            ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.port = None
        self.host = None
        self.docker = docker.DockerClient() if docker else None
        self.servers: dict[str, Server] = {}

        self.config(config_path)
        self.setup_routes()

    @property
    def client(self):
        return httpx.AsyncClient()

    def config(self, config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        self.port = config.get("port", 8000)
        self.host = config.get("host", "")
        config_servers = config.get("servers", None)

        for server_name in config_servers:
            server = Server.from_file(config_servers[server_name]["path"], self.docker)
            server.start()
            self.servers[server_name] = server

    async def test_service(self, server: Server | str, service: Service | str):
        try:
            if isinstance(server, str):
                server = self.servers[server]
            response = await server.get(service)
            return response.status_code == 200
        except (httpx.HTTPError, httpx.InvalidURL):
            return False

    async def status(self):
        status = {}
        for server_name, server in self.servers.items():
            status[server_name] = await server.status()
        return status

    def setup_routes(self):
        @self.app.get("/")
        async def get_status():
            running = {server_name: [] for server_name in self.servers}
            stopped = {server_name: [] for server_name in self.servers}
            status = await self.status()
            for server_name, server_status in status.items():
                for service, service_status in server_status.items():
                    service_name = str(service.image)
                    if service_status == "running":
                        running[server_name].append(service_name)
                    else:
                        stopped[server_name].append(service_name)

            return {"running": running, "stopped": stopped}

        @self.app.get("/{server}/")
        async def get_server_status(server: str):
            return self.servers[server].status()

        @self.app.get("/{server}/{service}")
        async def get_service_endpoints(server: str,
                                        service: str):
            async with self.client:
                response = await self.servers[server].get(service)
                return response.json()

        @self.app.get("/{server}/{service}/{endpoint}")
        async def get_service_endpoints(server: str,
                                        service: str,
                                        endpoint: str):
            async with self.client:
                response = await self.servers[server].get(service, endpoint=f"/{endpoint}")
                return response.json()

        @self.app.post("/{server}/{service}/{endpoint}")
        async def get_service_endpoints(server: str,
                                        service: str,
                                        endpoint: str,
                                        request: Request):
            data = await request.json()
            async with self.client:
                response = await self.servers[server].post(service, endpoint=f"/{endpoint}", data=data)
                return response.json()

    def stop(self):
        for server in self.servers.values():
            server.stop()

    def start(self, host=None, port=None):
        import uvicorn
        uvicorn.run(self.app,
                    host=host if host else self.host,
                    port=port if port else self.port)
