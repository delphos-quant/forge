import os

from dotenv import load_dotenv

import yaml
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from dxforge import Forge
from dxforge.routers import controller


class App(FastAPI):
    def __init__(self, origins=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if origins is None:
            origins = [
                "http://localhost:80",
                "http://localhost:443",
                "http://localhost:3000",
                "http://localhost:8000",
                "http://localhost:8080",
            ]

        self.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.include_router(controller.router, prefix="/controllers", tags=["controller"])


def main() -> FastAPI:
    load_dotenv()
    config_file = os.getenv("CONFIG_FILE", "config.yaml")
    config = yaml.safe_load(open(config_file, "r"))

    description = """
    The dxforge suite is aimed at small teams and large teams that plan on scaling, 
    reducing costs and maintenance of quantitative trading strategies.

    The framework focuses on managing different strategies, their instances, feeds and portfolios 
    via distributed and scalable nodes, without the need of managing them individually.
    """

    Forge.from_config(config)
    return App(
        title="dxforge",
        description=description,
        summary="An API-based orchestration platform by DivergeX.",
        version="v0.1.0",
        # terms_of_service="http://example.com/terms/",
        # contact={
        #     "name": "Deadpoolio the Amazing",
        #     "url": "http://x-force.example.com/contact/",
        #     "email": "dp@x-force.example.com",
        # },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    )


if __name__ == "__main__":
    app = main()

    host = os.getenv("HOST", None)
    port = int(os.getenv("PORT", 8000))

    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        pass
    finally:
        pass
else:
    app = main()
    __all__ = ["app"]
