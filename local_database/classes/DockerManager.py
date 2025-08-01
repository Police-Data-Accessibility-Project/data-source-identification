import platform
import subprocess
import sys

import docker
from docker.errors import APIError
from docker.models.containers import Container
from docker.models.networks import Network

from local_database.DTOs import DockerfileInfo, DockerInfo
from local_database.classes.DockerClient import DockerClient
from local_database.classes.DockerContainer import DockerContainer


class DockerManager:
    def __init__(self):
        if not self.is_docker_running():
            self.start_docker_engine()

        self.client = DockerClient()
        self.network_name = "my_network"
        self.network = self.start_network()

    @staticmethod
    def start_docker_engine() -> None:
        system = platform.system()

        match system:
            case "Windows":
                # Use PowerShell to start Docker Desktop on Windows
                subprocess.run([
                    "powershell", "-Command",
                    "Start-Process 'Docker Desktop' -Verb RunAs"
                ])
            case "Darwin":
                # MacOS: Docker Desktop must be started manually or with open
                subprocess.run(["open", "-a", "Docker"])
            case "Linux":
                # Most Linux systems use systemctl to manage Docker
                subprocess.run(["sudo", "systemctl", "start", "docker"])
            case _:
                print(f"Unsupported OS: {system}")
                sys.exit(1)

    @staticmethod
    def is_docker_running() -> bool:
        try:
            client = docker.from_env()
            client.ping()
            return True
        except docker.errors.DockerException as e:
            print(f"Docker is not running: {e}")
            return False

    def run_command(
        self,
        command: str,
        container_id: str
    ) -> None:
        self.client.run_command(command, container_id)

    def start_network(self) -> Network:
        return self.client.start_network(self.network_name)

    def stop_network(self) -> None:
        self.client.stop_network(self.network_name)

    def get_image(
        self,
        dockerfile_info: DockerfileInfo
    ) -> None:
        self.client.get_image(dockerfile_info)

    def run_container(
            self,
            docker_info: DockerInfo,
            force_rebuild: bool = False
    ) -> DockerContainer:
        raw_container = self.client.run_container(
            docker_info,
            network_name=self.network_name,
            force_rebuild=force_rebuild
        )
        return DockerContainer(self.client, raw_container)

    def get_containers(self) -> list[Container]:
        return self.client.client.containers.list()