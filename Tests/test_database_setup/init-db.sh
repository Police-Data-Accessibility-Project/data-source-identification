#!/bin/bash
set -e

# Wait for Postgres to be ready
until pg_isready -h localhost -U "$POSTGRES_USER"; do
  sleep 1
done

# Export the schema from the production database
export PGPASSWORD=$PROD_DB_PASSWORD
pg_dump -h $PROD_DB_HOST -U $PROD_DB_USER -d $PROD_DB_NAME -s -t table1 -t table2 > /tmp/prod-schema.sql
unset PGPASSWORD

# Import the schema into the test database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" < /tmp/prod-schema.sql
