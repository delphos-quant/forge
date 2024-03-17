import os
from typing import Dict
from dotenv import load_dotenv

import docker
import uvicorn
import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src import Orchestrator, Controller


class Forge(Orchestrator):
    def __init__(self,
                 controllers: Dict[str, Controller] = None,
                 origins=None,
                 *args,
                 **kwargs):
        super().__init__(controllers)
        self.app = FastAPI(*args, **kwargs)

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
        self.setup_routes()

    @classmethod
    def from_config(cls, config: dict) -> 'Forge':
        docker_client = docker.DockerClient() if docker else None

        controllers = {}

        for name, path in config.get("controllers", {}).items():
            controllers[name] = Controller.from_file(path, docker_client)

        return cls(controllers)

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

        @self.app.get("/{resource}")
        async def get_resource(resource: str):
            if resource == 'favicon.ico':
                icon = open('src/assets/favicon.ico', 'rb')
                return icon.read()
            else:
                return {"error": "Resource not found"}

        @self.app.get("/controller/{controller}")
        async def get_controller_status(controller: str):
            status = await self.controllers[controller].status()
            return status

        @self.app.get("/controller/{controller}/{node}")
        async def get_node_endpoints(controller: str,
                                     node: str):
            async with self.client:
                response = await self.controllers[controller].get(node)
                return response.json()

        @self.app.get("/controller/{controller}/{node}/{endpoint}")
        async def get_node_endpoints(controller: str,
                                     node: str,
                                     endpoint: str):
            async with self.client:
                response = await self.controllers[controller].get(node, endpoint=f"/{endpoint}")
                return response.json()

        @self.app.post("/controller/{controller}/{node}/{endpoint}")
        async def get_node_endpoints(controller: str,
                                     node: str,
                                     endpoint: str,
                                     request: Request):
            data = await request.json()
            async with self.client:
                response = await self.controllers[controller].post(node, endpoint=f"/{endpoint}", data=data)
                return response.json()


def main():
    load_dotenv()

    host = os.getenv("HOST", None)
    port = int(os.getenv("PORT", 8000))

    config_file = os.getenv("CONFIG_FILE", "config.yaml")
    config = yaml.safe_load(open(config_file, "r"))

    forge = Forge.from_config(config)

    try:
        uvicorn.run(forge.app, host=host, port=port)
    except KeyboardInterrupt:
        pass
    finally:
        forge.stop()


if __name__ == "__main__":
    main()
else:
    forge = Forge.from_config(yaml.safe_load(open("config.yaml", "r")))
    app = forge.app
    __all__ = ["app"]
