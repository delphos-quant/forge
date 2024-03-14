import argparse

from orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(description="Start the strategies strategy server.")
    parser.add_argument("config", help="Path to the strategy config file")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: localhost)")
    parser.add_argument("--port", default=8000, type=int, help="Port to listen on (default: 8080)")
    args = parser.parse_args()

    orchestrator = Orchestrator(args.config)
    orchestrator.start(args.host, args.port)
    orchestrator.stop()


if __name__ == "__main__":
    main()
