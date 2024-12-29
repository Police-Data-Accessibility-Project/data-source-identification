

# Setting Up Test Database

To perform the following tests, you'll need to set up a test PostgreSQL database using Docker Compose.

To set up a test database using Docker Compose, you'll need to have Docker installed on your system. You can install docker [here](https://docs.docker.com/engine/install/).

The `docker-compose.yml` file in this directory contains instructions for setting up a test PostgreSQL database using Docker Compose. To start the test database, run the following command:
```bash
docker compose up -d
```

Once the test database is started, make sure to add the following environmental variables to your `.env` file in the root directory of the repository.:
```dotenv
POSTGRES_USER=test_source_collector_user
POSTGRES_PASSWORD=HanviliciousHamiltonHilltops
POSTGRES_DB=source_collector_test_db
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

To close the test database, run the following command:
```bash
docker compose down
```