"""
Starts a local instance of the application utilizing a database
mirrored from production.

Because this is used for testing only, the docker module is not included in
requirements.txt, and must be installed separately via
`pip install docker`
"""
import datetime
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Annotated
import uvicorn

import docker
from docker.errors import APIError, NotFound
from docker.models.containers import Container
from pydantic import BaseModel, AfterValidator

from apply_migrations import apply_migrations
from util.helper_functions import get_from_env

def is_absolute_path(path: str) -> str:
    if len(path) == 0:
        raise ValueError("Path is required")
    if path[0] != "/":
        raise ValueError("Container path must be absolute")
    return path

class VolumeInfo(BaseModel):
    host_path: str
    container_path: Annotated[str, AfterValidator(is_absolute_path)]

    def build_volumes(self):
        return {
            get_absolute_path(self.host_path): {
                "bind": self.container_path,
                "mode": "rw"
            }
        }

def wait_for_pg_to_be_ready(container: Container):
    for i in range(30):
        exit_code, output = container.exec_run("pg_isready")
        print(output)
        if exit_code == 0:
            return
        time.sleep(1)
    raise Exception("Timed out waiting for postgres to be ready")

def get_absolute_path(relative_path: str) -> str:
    """
    Get absolute path, using the current file as the point of reference
    """
    current_dir = Path(__file__).parent
    absolute_path = (current_dir / relative_path).resolve()
    return str(absolute_path)


class DockerfileInfo(BaseModel):
    image_tag: str
    dockerfile_directory: Optional[str] = None



class HealthCheckInfo(BaseModel):
    test: list[str]
    interval: int
    timeout: int
    retries: int
    start_period: int

    def build_healthcheck(self) -> dict:
        multiplicative_factor = 1000000000  # Assume 1 second
        return {
            "test": self.test,
            "interval": self.interval * multiplicative_factor,
            "timeout": self.timeout * multiplicative_factor,
            "retries": self.retries,
            "start_period": self.start_period * multiplicative_factor
        }

class DockerInfo(BaseModel):
    dockerfile_info: DockerfileInfo
    volume_info: Optional[VolumeInfo] = None
    name: str
    ports: Optional[dict] = None
    environment: Optional[dict]
    command: Optional[str] = None
    entrypoint: Optional[list[str]] = None
    health_check_info: Optional[HealthCheckInfo] = None

def run_command_checked(command: list[str] or str, shell=False):
    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        shell=shell
    )
    return result

def is_docker_running():
    try:
        client = docker.from_env()
        client.ping()
        return True
    except docker.errors.DockerException as e:
        print(f"Docker is not running: {e}")
        return False

def wait_for_health(container, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        container.reload()  # Refresh container state
        state = container.attrs.get("State")
        print(state)
        health = container.attrs.get("State", {}).get("Health", {})
        status = health.get("Status")
        print(f"Health status: {status}")
        if status == "healthy":
            print("Postgres is healthy.")
            return
        elif status == "unhealthy":
            raise Exception("Postgres container became unhealthy.")
        time.sleep(1)
    raise TimeoutError("Timed out waiting for Postgres to become healthy.")

def start_docker_engine():
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

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.network_name = "my_network"
        self.network = self.start_network()

    def run_command(self, command: str, container_id: str):
        exec_id = self.client.api.exec_create(
            container_id,
            cmd=command,
            tty=True,
            stdin=False
        )
        output_stream = self.client.api.exec_start(exec_id=exec_id, stream=True)
        for line in output_stream:
            print(line.decode().rstrip())

    def start_network(self):
        try:
            self.client.networks.create(self.network_name, driver="bridge")
        except APIError as e:
            # Assume already exists
            print(e)
        return self.client.networks.get("my_network")

    def stop_network(self):
        self.client.networks.get("my_network").remove()

    def get_image(self, dockerfile_info: DockerfileInfo):
        if dockerfile_info.dockerfile_directory:
            # Build image from Dockerfile
            self.client.images.build(
                path=get_absolute_path(dockerfile_info.dockerfile_directory),
                tag=dockerfile_info.image_tag
            )
        else:
            # Pull or use existing image
            self.client.images.pull(dockerfile_info.image_tag)


    def run_container(
            self,
            docker_info: DockerInfo,
    ) -> Container:
        print(f"Running container {docker_info.name}")
        try:
            container = self.client.containers.get(docker_info.name)
            if container.status == 'running':
                print(f"Container '{docker_info.name}' is already running")
                return container
            print("Restarting container...")
            container.start()
            return container
        except NotFound:
            # Container does not exist; proceed to build/pull image and run
            pass

        self.get_image(docker_info.dockerfile_info)

        container = self.client.containers.run(
            image=docker_info.dockerfile_info.image_tag,
            volumes=docker_info.volume_info.build_volumes() if docker_info.volume_info is not None else None,
            command=docker_info.command,
            entrypoint=docker_info.entrypoint,
            detach=True,
            name=docker_info.name,
            ports=docker_info.ports,
            network=self.network_name,
            environment=docker_info.environment,
            stdout=True,
            stderr=True,
            tty=True,
            healthcheck=docker_info.health_check_info.build_healthcheck() if docker_info.health_check_info is not None else None
        )
        return container


class TimestampChecker:
    def __init__(self):
        self.last_run_time: Optional[datetime.datetime] = self.load_last_run_time()

    def load_last_run_time(self) -> Optional[datetime.datetime]:
        # Check if file `last_run.txt` exists
        # If it does, load the last run time
        if os.path.exists("local_state/last_run.txt"):
            with open("local_state/last_run.txt", "r") as f:
                return datetime.datetime.strptime(
                    f.read(),
                    "%Y-%m-%d %H:%M:%S"
                )
        return None

    def last_run_within_24_hours(self):
        if self.last_run_time is None:
            return False
        return datetime.datetime.now() - self.last_run_time < datetime.timedelta(days=1)

    def set_last_run_time(self):
        # If directory `local_state` doesn't exist, create it
        if not os.path.exists("local_state"):
            os.makedirs("local_state")

        with open("local_state/last_run.txt", "w") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def get_database_docker_info() -> DockerInfo:
    return DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="postgres:15",
        ),
        name="data_source_identification_db",
        ports={
            "5432/tcp": 5432
        },
        environment={
            "POSTGRES_PASSWORD": "HanviliciousHamiltonHilltops",
            "POSTGRES_USER": "test_source_collector_user",
            "POSTGRES_DB": "source_collector_test_db"
        },
        health_check_info=HealthCheckInfo(
            test=["pg_isready", "-U", "test_source_collector_user", "-h", "127.0.0.1", "-p", "5432"],
            interval=1,
            timeout=3,
            retries=30,
            start_period=2
        )
    )

def get_data_dumper_docker_info() -> DockerInfo:
    return DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="datadumper",
            dockerfile_directory="local_database/DataDumper"
        ),
        volume_info=VolumeInfo(
            host_path="./local_database/DataDumper/dump",
            container_path="/dump"
        ),
        name="datadumper",
        environment={
            "DUMP_HOST": get_from_env("DUMP_HOST"),
            "DUMP_USER": get_from_env("DUMP_USER"),
            "DUMP_PASSWORD": get_from_env("DUMP_PASSWORD"),
            "DUMP_NAME": get_from_env("DUMP_DB_NAME"),
            "DUMP_PORT": get_from_env("DUMP_PORT"),
            "RESTORE_HOST": "data_source_identification_db",
            "RESTORE_USER": "test_source_collector_user",
            "RESTORE_PORT": "5432",
            "RESTORE_DB_NAME": "source_collector_test_db",
            "RESTORE_PASSWORD": "HanviliciousHamiltonHilltops",
        },
        command="bash"
    )

def main():
    docker_manager = DockerManager()
    # Ensure docker is running, and start if not
    if not is_docker_running():
        start_docker_engine()

    # Ensure Dockerfile for database is running, and if not, start it
    database_docker_info = get_database_docker_info()
    container = docker_manager.run_container(database_docker_info)
    wait_for_pg_to_be_ready(container)


    # Start dockerfile for Datadumper
    data_dumper_docker_info = get_data_dumper_docker_info()

    # If not last run within 24 hours, run dump operation in Datadumper
    # Check cache if exists and
    checker = TimestampChecker()
    container = docker_manager.run_container(data_dumper_docker_info)
    if checker.last_run_within_24_hours():
        print("Last run within 24 hours, skipping dump...")
    else:
        docker_manager.run_command(
            '/usr/local/bin/dump.sh',
            container.id
        )
    docker_manager.run_command(
        "/usr/local/bin/restore.sh",
        container.id
    )
    print("Stopping datadumper container")
    container.stop()
    checker.set_last_run_time()

    # Upgrade using alembic
    apply_migrations()

    # Run `fastapi dev main.py`
    try:
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000
        )
    finally:
        # Add feature to stop all running containers
        print("Stopping containers...")
        for container in docker_manager.client.containers.list():
            container.stop()

        print("Containers stopped.")






if __name__ == "__main__":
    main()