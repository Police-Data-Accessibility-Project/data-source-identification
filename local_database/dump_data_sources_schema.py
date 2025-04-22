from local_database.DockerInfos import get_data_sources_data_dumper_info
from local_database.classes.DockerManager import DockerManager
from local_database.constants import DUMP_SH_DOCKER_PATH


def main():
    docker_manager = DockerManager()
    data_sources_docker_info = get_data_sources_data_dumper_info()
    container = docker_manager.run_container(
        data_sources_docker_info,
        force_rebuild=True
    )
    try:
        container.run_command(DUMP_SH_DOCKER_PATH)
    finally:
        container.stop()



if __name__ == "__main__":
    main()