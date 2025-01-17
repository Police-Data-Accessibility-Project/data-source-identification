#!/bin/bash
set -e

# Variables (customize these or pass them as environment variables)
DB_HOST=${DUMP_HOST:-"postgres_container"}
DB_USER=${DUMP_USER:-"your_user"}
DB_PORT=${DUMP_PORT:-"5432"}  # Default to 5432 if not provided
DB_PASSWORD=${DUMP_PASSWORD:-"your_password"}
DB_NAME=${DUMP_NAME:-"your_database"}
DUMP_FILE=${DUMP_FILE:-"/dump/db_dump.sql"}

# Export password for pg_dump
export PGPASSWORD=$DB_PASSWORD

# Dump the database
echo "Dumping database $DB_NAME from $DB_HOST:$DB_PORT..."
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME --no-owner --no-acl -F c -f $DUMP_FILE

echo "Dump completed. File saved to $DUMP_FILE."