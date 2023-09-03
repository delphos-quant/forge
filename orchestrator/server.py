import argparse

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import yaml
import docker


class ServerOrchestrator:
    def __init__(self, config_path, origins: list[str] = None):
        self.app = FastAPI()
        self.docker = docker.from_env()

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

        self.strategies = {}
        self.port = None
        self.host = None

        self.config(config_path)
        self.setup_routes()

    def config(self, config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        self.port = config.get("port", 8000)
        self.host = config.get("host", "")

        strategies_compose = config.get("strategies", None)
        # read the docker-compose.yaml to get the ports of the strategies
        if strategies_compose:
            with open(strategies_compose, 'r') as file:
                strategies_config = yaml.safe_load(file)
            for strategy, data in strategies_config["services"].items():
                self.strategies[strategy] = {
                    "image": data["image"],
                    "status": "unavailable"
                }
                env = {key: value for key, value in (env_var.split('=') for env_var in
                                                     self.docker.images.get(data["image"]).attrs['Config']['Env'])}

                if data.get("container_name", False):
                    self.strategies[strategy]["container_name"] = data["container_name"]

                if env.get("WEBSOCKET_PORT", False):
                    self.strategies[strategy]["websocket"] = f"http://localhost:{env['WEBSOCKET_PORT']}"

                if env.get("SERVER_PORT", False):
                    self.strategies[strategy]["server"] = f"http://localhost:{env['SERVER_PORT']}"
                    self.strategies[strategy]["status"] = "available" if self.test_strategy(strategy) else "unavailable"

    @classmethod
    def get_client(cls):
        return httpx.AsyncClient()

    def start_strategy(self, strategy):
        self.docker.containers.run(
            self.strategies[strategy]["image"],
            ports={self.strategies[strategy]["port"]: self.strategies[strategy]["port"]},
            detach=True
        )

    def test_strategy(self, strategy):
        try:
            url = f"{self.strategies[strategy]['server']}"
            response = httpx.get(url)
            return response.status_code == 200
        except (httpx.HTTPError, httpx.InvalidURL):
            return False

    def verify_strategy(self, strategy):
        if strategy not in self.strategies:
            return {"error": "Invalid strategy specified"}
        if self.strategies[strategy].get("status", None) != "available":
            return {"error": "strategy is unavailable"}
        return {"status": "ok"}

    def refresh_strategies(self):
        for strategy in self.strategies:
            self.strategies[strategy]["status"] = "available" if self.test_strategy(strategy) else "unavailable"

    def setup_routes(self):
        @self.app.get("/strategy/")
        async def list_strategys():
            available = []
            unavailable = []
            for strategy in self.strategies:
                if self.strategies[strategy]["status"] == "available":
                    available.append(strategy)
                else:
                    unavailable.append(strategy)

            return {"available": available, "unavailable": unavailable}

        @self.app.post("/strategy/")
        async def refresh_strategies():
            self.refresh_strategies()
            return {"message": "strategies refreshed successfully"}

        @self.app.get("/strategy/{strategy}/")
        async def proxy_get_routes(strategy: str):
            if strategy not in self.strategies or self.strategies[strategy].get("status", None) != "available":
                raise HTTPException(status_code=404, detail=f"strategy '{strategy}' not available")

            async with self.get_client() as client:
                response = await client.get(f"{self.strategies[strategy]['server']}/")

                return response.json()["endpoints"]

        @self.app.get("/strategy/{strategy_name}/{endpoint}")
        async def proxy_get_method(strategy_name: str,
                                   endpoint: str):
            status = self.verify_strategy(strategy_name)
            if "error" in status:
                raise HTTPException(status_code=404, detail=f"strategy '{strategy_name}' not available")

            async with self.get_client() as client:
                response = await client.get(f"{self.strategies[strategy_name]['server']}/{endpoint}")

                return response.json()

        @self.app.post("/strategy/{strategy_name}/{endpoint}")
        async def proxy_post_method(strategy_name: str, endpoint: str, request: Request):
            status = self.verify_strategy(strategy_name)
            if "error" in status:
                raise HTTPException(status_code=404, detail=f"strategy '{strategy_name}' not available")

            data = await request.json()
            async with self.get_client() as client:
                response = await client.post(f"{self.strategies[strategy_name]['server']}/{endpoint}", json=data)

                return response.json()

    def run(self, host=None, port=None):
        import uvicorn
        uvicorn.run(self.app,
                    host=host if host else self.host,
                    port=port if port else self.port)


def main():
    parser = argparse.ArgumentParser(description="Start the strategies strategy server.")
    parser.add_argument("config", help="Path to the strategy config file")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", default=8000, type=int, help="Port to listen on (default: 8000)")
    parser.add_argument("--cors", default=None, type=list, help="Specify cors origins")
    args = parser.parse_args()

    orchestrator = ServerOrchestrator(args.config, args.cors)
    orchestrator.run(args.host, args.port)


if __name__ == "__main__":
    main()
