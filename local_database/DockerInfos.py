from local_database.DTOs import DockerInfo, DockerfileInfo, HealthCheckInfo, VolumeInfo
from local_database.constants import LOCAL_DATA_SOURCES_DB_NAME
from util.helper_functions import get_from_env, project_path


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


def get_data_sources_data_dumper_info() -> DockerInfo:
    return DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="datadumper",
            dockerfile_directory=str(project_path(
                "local_database",
                "DataDumper"
            ))
        ),
        volume_info=VolumeInfo(
            host_path=str(project_path(
                "local_database",
                "DataDumper",
                "dump"
            )),
            container_path="/dump"
        ),
        name="datadumper",
        environment={
            "DUMP_HOST": get_from_env("PROD_DATA_SOURCES_HOST"),
            "DUMP_USER": get_from_env("PROD_DATA_SOURCES_USER"),
            "DUMP_PASSWORD": get_from_env("PROD_DATA_SOURCES_PASSWORD"),
            "DUMP_NAME": get_from_env("PROD_DATA_SOURCES_DB"),
            "DUMP_PORT": get_from_env("PROD_DATA_SOURCES_PORT"),
            "RESTORE_HOST": get_from_env("POSTGRES_HOST"),
            "RESTORE_USER": get_from_env("POSTGRES_USER"),
            "RESTORE_PORT": get_from_env("POSTGRES_PORT"),
            "RESTORE_DB_NAME": LOCAL_DATA_SOURCES_DB_NAME,
            "RESTORE_PASSWORD": get_from_env("POSTGRES_PASSWORD"),
            "DUMP_FILE": "/dump/data_sources_db_dump.sql",
            "DUMP_SCHEMA_ONLY": "true"
        },
        command="bash"
    )


def get_source_collector_data_dumper_info() -> DockerInfo:
    return DockerInfo(
        dockerfile_info=DockerfileInfo(
            image_tag="datadumper",
            dockerfile_directory=str(project_path(
                "local_database",
                "DataDumper"
            ))
        ),
        volume_info=VolumeInfo(
            host_path=str(project_path(
                "local_database",
                "DataDumper",
                "dump"
            )),
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
