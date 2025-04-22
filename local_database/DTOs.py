from typing import Annotated, Optional

from pydantic import BaseModel, AfterValidator

from local_database.local_db_util import is_absolute_path, get_absolute_path


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
