"""
Starts a local instance of the application utilizing a database
mirrored from production.
"""
import uvicorn

from apply_migrations import apply_migrations
from local_database.DockerInfos import get_database_docker_info, get_source_collector_data_dumper_info
from local_database.classes.DockerManager import DockerManager
from local_database.classes.TimestampChecker import TimestampChecker
from local_database.constants import RESTORE_SH_DOCKER_PATH, DUMP_SH_DOCKER_PATH


def main():
    docker_manager = DockerManager()

    # Ensure Dockerfile for database is running, and if not, start it
    database_docker_info = get_database_docker_info()
    db_container = docker_manager.run_container(database_docker_info)
    db_container.wait_for_pg_to_be_ready()


    # Start dockerfile for Datadumper
    data_dumper_docker_info = get_source_collector_data_dumper_info()

    # If not last run within 24 hours, run dump operation in Datadumper
    # Check cache if exists and
    checker = TimestampChecker()
    data_dump_container = docker_manager.run_container(data_dumper_docker_info)
    if checker.last_run_within_24_hours():
        print("Last run within 24 hours, skipping dump...")
    else:
        data_dump_container.run_command(
            DUMP_SH_DOCKER_PATH,
        )
    data_dump_container.run_command(
        RESTORE_SH_DOCKER_PATH,
    )
    print("Stopping datadumper container")
    data_dump_container.stop()
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
        for container in docker_manager.get_containers():
            container.stop()

        print("Containers stopped.")






if __name__ == "__main__":
    main()