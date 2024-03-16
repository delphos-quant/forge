import docker
from docker.errors import APIError


class Node:
    def __init__(self, image_tag='latest', container_name=None, ports=None):
        self.image_tag = image_tag
        self.container_name = container_name
        self.ports = ports
        self.client = docker.from_env()

    def start_container(self):
        try:
            container = self.client.containers.run(
                image=self.image_tag,
                name=self.container_name,
                ports=self.ports,
                detach=True
            )
            print(f"Container started: {self.container_name}")
            return container
        except APIError as e:
            print(f"Failed to start container: {e}")
            return None

    def stop_container(self):
        container = self.client.containers.get(self.container_name)
        if container:
            container.stop()
            print(f"Container stopped: {self.container_name}")
        else:
            print(f"Container not found: {self.container_name}")

    def remove_container(self):
        container = self.client.containers.get(self.container_name)
        if container:
            container.remove()
            print(f"Container removed: {self.container_name}")
        else:
            print(f"Container not found: {self.container_name}")
