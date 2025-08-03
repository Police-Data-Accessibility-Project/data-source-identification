import time

from docker.models.containers import Container

from local_database.classes.DockerClient import DockerClient


class DockerContainer:

    def __init__(self, dc: DockerClient, container: Container):
        self.dc = dc
        self.container = container

    def run_command(self, command: str) -> None:
        self.dc.run_command(command, self.container.id)

    def stop(self) -> None:
        self.container.stop()

    def log_to_file(self) -> None:
        logs = self.container.logs(stdout=True, stderr=True)
        container_name = self.container.name
        with open(f"{container_name}.log", "wb") as f:
            f.write(logs)

    def wait_for_pg_to_be_ready(self) -> None:
        for i in range(30):
            exit_code, output = self.container.exec_run("pg_isready")
            print(output)
            if exit_code == 0:
                return
            time.sleep(1)
        raise Exception("Timed out waiting for postgres to be ready")

