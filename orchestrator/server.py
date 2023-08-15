import argparse

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import yaml


class ServerOrchestrator:
    def __init__(self, config_file, origins: list[str] = None):
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
            return {"available": self.managers}

        @self.app.post("/managers/")
        async def refresh_managers():
            self.refresh_managers()
            return {"message": "Managers refreshed successfully"}

        @self.app.get("/managers/{manager_name}/")
        async def proxy_get_routes(manager_name: str):
            status = self.verify_manager(manager_name)
            if "error" in status:
                raise HTTPException(status_code=404, detail=f"Manager '{manager_name}' not available")

            async with self.get_client() as client:
                response = await client.get(f"{self.managers[manager_name]['route']}/")

                return response.json()["endpoints"]

        @self.app.get("/managers/{manager_name}/{endpoint}")
        async def proxy_get_method(manager_name: str,
                                   endpoint: str):
            status = self.verify_manager(manager_name)
            if "error" in status:
                raise HTTPException(status_code=404, detail=f"Manager '{manager_name}' not available")

            async with self.get_client() as client:
                response = await client.get(f"{self.managers[manager_name]['route']}/{endpoint}")

                return response.json()

        @self.app.post("/managers/{manager_name}/{endpoint}")
        async def proxy_post_method(manager_name: str, endpoint: str, request: Request):
            status = self.verify_manager(manager_name)
            if "error" in status:
                raise HTTPException(status_code=404, detail=f"Manager '{manager_name}' not available")

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
    parser.add_argument("--cors", default=None, type=list, help="Specify cors origins")
    args = parser.parse_args()

    orchestrator = ServerOrchestrator(args.config_file, args.cors)
    orchestrator.run(args.host, args.port)


if __name__ == "__main__":
    main()
