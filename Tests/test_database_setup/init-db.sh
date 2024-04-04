#!/bin/bash
set -e

# Wait for Postgres to be ready
until pg_isready; do
  echo "Waiting for postgres to be ready"
  sleep 10
done

# Export the schema from the production database
# The `export PGPASSWORD=$DIGITAL_OCEAN_DB_PASSWORD` line sets the environment variable `PGPASSWORD`
# to the value stored in `DIGITAL_OCEAN_DB_PASSWORD`.
# This allows the `pg_dump` command to connect to the database without asking for a password.

export PGPASSWORD=$DIGITAL_OCEAN_DB_PASSWORD

# The `pg_dump` command is used to backup a PostgreSQL database.
# The `-h` option specifies the database server host.
# The `-p` option specifies the port where the database server is listening.
# The `-U` option specifies the username used to connect to the database.
# The `-d` option specifies the name of the database to connect to.
# The `-s` option means to dump only the object definitions (schema), not data.
# The `--no-owner` option prevents pg_dump from including commands to set the ownership of objects to match the original database
# The `-t` option lets you specify the tables that you want to dump. In this case, the tables are `public.agencies` and `public.agency_url_search_cache`.

if pg_dump -h "$DIGITAL_OCEAN_DB_HOST" \
   -p "$DIGITAL_OCEAN_DB_PORT" \
   -U "$DIGITAL_OCEAN_DB_USERNAME" \
   -d "$DIGITAL_OCEAN_DB_NAME" \
   --no-owner \
   -s \
   -t public.agencies \
   -t public.search_result \
   -t public.agency_url_search_cache > /tmp/prod-schema.sql; then
    echo "Schema export was successful."
else
    echo "Schema export failed." >&2
    exit 1
fi


# The database dump is written to the file /tmp/prod-schema.sql

# unset PGPASSWORD removes the `PGPASSWORD` environment variable after the `pg_dump` command is finished.
# It's good practice to not leave sensitive data like passwords lingering in the environment longer than necessary.

unset PGPASSWORD

# Import the schema into the test database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" < /tmp/prod-schema.sql
