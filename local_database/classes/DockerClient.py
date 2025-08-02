import docker
from docker.errors import NotFound, APIError
from docker.models.containers import Container
from docker.models.networks import Network

from local_database.DTOs import DockerfileInfo, DockerInfo


class DockerClient:

    def __init__(self):
        self.client = docker.from_env()

    def run_command(self, command: str, container_id: str) -> None:
        exec_id = self.client.api.exec_create(
            container_id,
            cmd=command,
            tty=False,
            stdin=False
        )
        output_stream = self.client.api.exec_start(exec_id=exec_id, stream=True)
        for line in output_stream:
            print(line.decode().rstrip())

    def start_network(self, network_name) -> Network:
        try:
            self.client.networks.create(network_name, driver="bridge")
        except APIError as e:
            # Assume already exists
            if e.response.status_code != 409:
                raise e
            print("Network already exists")
        return self.client.networks.get(network_name)

    def stop_network(self, network_name) -> None:
        self.client.networks.get(network_name).remove()

    def get_image(
            self,
            dockerfile_info: DockerfileInfo,
            force_rebuild: bool = False
    ) -> None:
        if dockerfile_info.dockerfile_directory:
            # Build image from Dockerfile
            self.client.images.build(
                path=dockerfile_info.dockerfile_directory,
                tag=dockerfile_info.image_tag,
                nocache=force_rebuild,
                rm=True  # Remove intermediate images
            )
            return

        if force_rebuild:
            # Even if not from Dockerfile, re-pull to ensure freshness
            self.client.images.pull(dockerfile_info.image_tag)
            return

        try:
            self.client.images.get(dockerfile_info.image_tag)
        except NotFound:
            self.client.images.pull(dockerfile_info.image_tag)

    def get_existing_container(self, docker_info_name: str) -> Container | None:
        try:
            return self.client.containers.get(docker_info_name)
        except NotFound:
            return None

    def create_container(self, docker_info: DockerInfo, network_name: str, force_rebuild: bool = False):
        self.get_image(
            docker_info.dockerfile_info,
            force_rebuild=force_rebuild
        )

        container = self.client.containers.run(
            image=docker_info.dockerfile_info.image_tag,
            volumes=docker_info.volume_info.build_volumes() if docker_info.volume_info is not None else None,
            command=docker_info.command,
            entrypoint=docker_info.entrypoint,
            detach=True,
            name=docker_info.name,
            ports=docker_info.ports,
            network=network_name,
            environment=docker_info.environment,
            stdout=True,
            stderr=True,
            tty=True,
            healthcheck=docker_info.health_check_info.build_healthcheck() if docker_info.health_check_info is not None else None
        )
        return container


    def run_container(
            self,
            docker_info: DockerInfo,
            network_name: str,
            force_rebuild: bool = False
    ):
        print(f"Running container {docker_info.name}")
        container = self.get_existing_container(docker_info.name)
        if container is None:
            return self.create_container(
                docker_info=docker_info,
                network_name=network_name,
                force_rebuild=force_rebuild
            )
        if force_rebuild:
            print("Rebuilding container...")
            container.remove(force=True)
            return self.create_container(
                docker_info=docker_info,
                network_name=network_name,
                force_rebuild=force_rebuild
            )
        if container.status == 'running':
            print(f"Container '{docker_info.name}' is already running")
            return container
        container.start()
        return container

