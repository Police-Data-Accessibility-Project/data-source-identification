The DataDumper directory contains scripts for backing up and restoring the Source Collector Database.

## Files and Directories
- A `Dockerfile` which contains the instructions for building the docker image with Postgres functionality enabled
- A `dump.sh` script which handles the dump process
- A `restore.sh` script which handles the restore process
- A `docker-compose.yml` file which handles the setup of the docker container and can be modified to run either `dump.sh` or `restore.sh`
- A `.env` file which contains environment variables for the docker container
- A `dump` directory which stores the dump.

## Environment Variables

| Name            | Description                                                                                                                                                                                                                                                       | Example                        |
|-----------------|-------------------------------------------------------------------------------------|--------------------------------|
| `DUMP_HOST`     | The host of the database to dump.  | `127.0.0.1`                    |
| `DUMP_USER`     | The username of the user to connect to the database. | `test_source_collector_user`   |
| `DUMP_PASSWORD` | The password of the user to connect to the database. | `HanviliciousHamiltonHilltops` |
| `DUMP_DB_NAME`  | The name of the database to dump. | `source_collector_test_db`     |
| `DUMP_PORT`     | The port of the database to dump.  | `5432`                         |
| `RESTORE_HOST`  | The host of the database to restore into. | `127.0.0.1`                           |
| `RESTORE_USER`  | The username of the user to connect to the database. | `test_source_collector_user`   |
| `RESTORE_PORT`  | The port of the database to restore into.  | `5432`                         |
| `RESTORE_DB_NAME` | The name of the database to restore into. | `source_collector_test_db`     |
| `RESTORE_PASSWORD` | The password of the user to connect to the database. | `HanviliciousHamiltonHilltops` |
