import argparse

from fastapi import FastAPI, Request
import httpx
import yaml


class ServerOrchestrator:
    def __init__(self, config_file):
        self.app = FastAPI()
        self.managers = self.load_manager_info(config_file)
        self.refresh_managers()
        self.setup_routes()

    @classmethod
    def get_client(cls):
        return httpx.AsyncClient()

    @classmethod
    def load_manager_info(cls, config_file):
        with open(config_file, 'r') as file:
            manager_info = yaml.safe_load(file)
        return manager_info

    def test_manager(self, manager_name):
        if self.managers[manager_name].get("disabled", False):
            return False
        try:
            url = f"{self.managers[manager_name]['route']}"
            response = httpx.get(url)
            return response.status_code == 200
        except (httpx.HTTPError, httpx.InvalidURL):
            return False

    def refresh_managers(self):
        for manager_name in self.managers:
            self.managers[manager_name]["status"] = "available" if self.test_manager(manager_name) else "unavailable"

    def verify_manager(self, manager_name):
        if manager_name not in self.managers:
            return {"error": "Invalid manager specified"}
        if self.managers[manager_name]["status"] != "available":
            return {"error": "Manager is unavailable"}
        return {"status": "ok"}

    def setup_routes(self):
        @self.app.get("/managers/")
        async def list_managers():
            return {"managers_example": self.managers}

        @self.app.post("/managers/")
        async def refresh_managers():
            self.refresh_managers()
            return "ok"

        @self.app.get("/managers/{manager_name}/")
        async def proxy_get_routes(manager_name: str):
            status = self.verify_manager(manager_name)
            if "error" in status:
                return status

            async with self.get_client() as client:
                response = await client.get(f"{self.managers[manager_name]['route']}/")

                return response.json()["endpoints"]

        @self.app.get("/managers/{manager_name}/{endpoint}")
        async def proxy_get_method(manager_name: str,
                                   endpoint: str):
            status = self.verify_manager(manager_name)
            if "error" in status:
                return status

            async with self.get_client() as client:
                response = await client.get(f"{self.managers[manager_name]['route']}/{endpoint}")

                return response.json()

        @self.app.post("/managers/{manager_name}/{endpoint}")
        async def proxy_post_method(manager_name: str, endpoint: str, request: Request):
            status = self.verify_manager(manager_name)
            if "error" in status:
                return status

            data = await request.json()
            async with self.get_client() as client:
                response = await client.post(f"{self.managers[manager_name]['route']}/{endpoint}", json=data)

                return response.json()

    def run(self, host="0.0.0.0", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="Start the managers_example manager server.")
    parser.add_argument("config_file", help="Path to the manager config file")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", default=8000, type=int, help="Port to listen on (default: 8000)")
    args = parser.parse_args()

    orchestrator = ServerOrchestrator(args.config_file)
    orchestrator.run(args.host, args.port)


if __name__ == "__main__":
    main()
