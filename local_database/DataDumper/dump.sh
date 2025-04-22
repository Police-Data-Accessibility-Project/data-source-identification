#!/bin/bash
#set -e

# Variables (customize these or pass them as environment variables)
DB_HOST=${DUMP_HOST:-"postgres_container"}
DB_USER=${DUMP_USER:-"your_user"}
DB_PORT=${DUMP_PORT:-"5432"}
DB_PASSWORD=${DUMP_PASSWORD:-"your_password"}
DB_NAME=${DUMP_NAME:-"your_database"}
DUMP_FILE=${DUMP_FILE:-"/dump/db_dump.sql"}
DUMP_SCHEMA_ONLY=${DUMP_SCHEMA_ONLY:-false}  # Set to "true" to dump only schema

# Export password for pg_dump
export PGPASSWORD=$DB_PASSWORD

# Determine pg_dump flags
PG_DUMP_FLAGS="--no-owner --no-acl -F c"
if [[ "$DUMP_SCHEMA_ONLY" == "true" ]]; then
    PG_DUMP_FLAGS="$PG_DUMP_FLAGS --schema-only"
    echo "Dumping schema only..."
else
    echo "Dumping full database..."
fi

# Run pg_dump
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME $PG_DUMP_FLAGS -f $DUMP_FILE

echo "Dump completed. File saved to $DUMP_FILE."
