import argparse

from orchestrator import Orchestrator


def main():
    parser = argparse.ArgumentParser(description="Start the strategies strategy server.")
    parser.add_argument("config", help="Path to the strategy config file")
    args = parser.parse_args()

    orchestrator = Orchestrator(args.config)
    orchestrator.start(args.config.host, args.config.port)
    orchestrator.stop()


if __name__ == "__main__":
    main()
