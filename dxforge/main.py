import os
from dotenv import load_dotenv

import uvicorn
import yaml
from fastapi import FastAPI

from dxforge import Forge


load_dotenv()
config_file = os.getenv("CONFIG_FILE", "config.yaml")
config = yaml.safe_load(open(config_file, "r"))


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


app = App()


def main():
    host = os.getenv("HOST", None)
    port = int(os.getenv("PORT", 8000))

    forge = Forge()

    try:
        pass
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        pass
    finally:
        pass


if __name__ == "__main__":
    main()
else:
    __all__ = ["app"]
