from typing import Dict

import yaml
from fastapi import FastAPI

from controller import Controller


class Orchestrator:
    def __init__(self, controllers: dict, port: int = 8000, host: str = "localhost"):
        self.app = FastAPI()

        self.controllers = controllers if controllers else {}
        self._port = port
        self._host = host

    @classmethod
    def from_config(cls, config_file):
        try:
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                return cls(**config)
        except FileNotFoundError:
            print(f"Config file not found: {config_file}")
            return None
        except KeyError:
            print(f"Config file is missing required keys: {config_file}")
            return None

    @property
    def controllers(self):
        return self._controllers

    @controllers.setter
    def controllers(self, value: Dict[str, Controller] | Dict[str, str]):
        self._controllers = {}
        for controller_name, controller in value.items():
            self._controllers[controller_name] = Controller(controller) if isinstance(controller, str) else controller

    def start(self, controller_name, container_name):
        if controller_name in self.controllers:
            self.controllers[controller_name].start_container(container_name)
            return {"message": f"Started container {container_name} in controller {controller_name}"}
        else:
            return {"error": f"Controller {controller_name} not found"}

    def stop(self, controller_name, container_name):
        if controller_name in self.controllers:
            self.controllers[controller_name].stop_container(container_name)
            return {"message": f"Stopped container {container_name} in controller {controller_name}"}
        else:
            return {"error": f"Controller {controller_name} not found"}

    def list_containers(self, controller_name):
        if controller_name in self.controllers:
            containers = self.controllers[controller_name].list_containers()
            return {"containers": containers}
        else:
            return {"error": f"Controller {controller_name} not found"}

    def list_controllers(self):
        return {
            "controllers": {
                controller_name: self.list_containers(controller_name) for controller_name in self.controllers
            }
        }

    def run(self):
        @self.app.post("/start/{controller_name}/{container_name}")
        def start_container(controller_name: str, container_name: str):
            return self.start(controller_name, container_name)

        @self.app.post("/stop/{controller_name}/{container_name}")
        def stop_container(controller_name: str, container_name: str):
            return self.stop(controller_name, container_name)

        @self.app.get("/list/{controller_name}")
        def list_containers(controller_name: str):
            return self.list_containers(controller_name)

        @self.app.get("/list")
        def list_controllers():
            return self.list_controllers()

        @self.app.get("/")
        def alive():
            return {"message": "DXFORGE is running!"}

        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    orchestrator = Orchestrator.from_config("../../config.yaml")
    orchestrator.run()
