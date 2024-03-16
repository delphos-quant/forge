import docker
import yaml

from node import Node


class Controller:
    def __init__(self, compose_file='docker-compose.yaml'):
        self.compose_file = compose_file
        self.services = []
        self.client = docker.from_env()

    def read_compose_file(self):
        with open(self.compose_file, 'r') as file:
            compose_data = yaml.safe_load(file)
        return compose_data

    def parse_services(self):
        compose_data = self.read_compose_file()
        if 'services' in compose_data:
            for service_name, service_config in compose_data['services'].items():
                image_tag = service_config.get('image', 'latest')
                container_name = service_config.get('container_name', service_name)
                ports = service_config.get('ports')
                self.services.append(Node(image_tag, container_name, ports))

    def start_services(self):
        for service in self.services:
            service.start_container()

    def stop_services(self):
        for service in self.services:
            service.stop_container()

    def remove_services(self):
        for service in self.services:
            service.remove_container()

    def list_containers(self):
        containers = self.client.containers.list()
        if containers:
            print("Containers that are up:")
            for container in containers:
                print(f"- {container.name}")
        else:
            print("No containers are up.")

    def stop_container(self, container_name):
        container = self.client.containers.get(container_name)
        if container:
            container.stop()
            print(f"Container stopped: {container_name}")
        else:
            print(f"Container not found: {container_name}")

    def start_container(self, container_name):
        container = self.client.containers.get(container_name)
        if container:
            container.start()
            print(f"Container started: {container_name}")
        else:
            print(f"Container not found: {container_name}")
